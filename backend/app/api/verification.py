import hashlib
import hmac
import secrets
from datetime import timedelta

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.common import access_course, policy, public, required
from app.core.config import settings
from app.core.security import audit, cipher, digest, roles, throttle, verify_password
from app.db.session import get_db
from app.models.entities import (AttendanceAttempt, AttendanceRecord, AttendanceSession, BiometricProfile,
    Challenge, Classroom, Device, User, WifiReference, SecurityChallenge, AppAttestKey, now)
from app.schemas.contracts import ChallengeInput, DeviceInput, Evidence, Login, SignedEvidence, AttestationChallengeInput, AttestationRegistration
from app.services.attestation import verify_integrity, IntegrityVerdict
from app.services.device_keys import registration_message, verify_signature
from app.services import app_attest
from cryptography.exceptions import InvalidSignature
from cryptography import x509
from app.services.presence import Decision, evaluate
from app.services.vision import MODEL_VERSION, VisionError, get_vision, normalize

router = APIRouter(tags=["Identity and presence"])
student = roles("student")


@router.get("/devices")
def devices(user: User = Depends(student), db: Session = Depends(get_db)):
    return [{**public(d), 'app_attest_registered': bool(db.scalar(select(AppAttestKey.key_id).where(AppAttestKey.device_id == d.id)))}
            for d in db.scalars(select(Device).where(Device.student_id == user.id))]


@router.post("/devices", status_code=201)
def register_device(data: DeviceInput, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "device:" + user.id, 5, 300)
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Password confirmation failed")
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    if db.scalar(select(Device).where(Device.student_id == user.id, Device.active.is_(True))):
        audit(db, user.id, "DEVICE_CHANGE_BLOCKED", severity="WARNING")
        db.commit()
        raise HTTPException(409, "An active device exists; request an administrator-approved reset")
    credential = None
    if data.public_key:
        challenge = consume_security_challenge(db, user.id, data.registration_challenge_id, 'device-registration')
        try:
            message = registration_message(challenge.nonce, data.platform, data.public_key)
        except (ValueError, TypeError):
            raise HTTPException(422, 'INVALID_P256_PUBLIC_KEY')
        if not verify_signature(data.public_key, data.registration_signature, message):
            raise HTTPException(403, 'DEVICE_REGISTRATION_SIGNATURE_INVALID')
        device = Device(student_id=user.id, label=data.label, platform=data.platform, secret_encrypted=b'',
                        key_algorithm='ecdsa-p256-sha256', public_key=data.public_key, key_storage=data.key_storage)
    else:
        if not settings().allow_legacy_device_registration:
            raise HTTPException(422, 'NATIVE_DEVICE_KEY_REQUIRED')
        credential = secrets.token_hex(32)
        device = Device(student_id=user.id, label=data.label, platform=data.platform, secret_encrypted=cipher().encrypt(credential.encode()))
    db.add(device)
    audit(db, user.id, "DEVICE_REGISTERED", platform=data.platform)
    db.commit()
    return {**public(device), **({"credential": credential} if credential else {}), "storage": "Native private key; storage type is client reported, not attested"}


@router.get("/biometrics")
def biometric_status(user: User = Depends(student), db: Session = Depends(get_db)):
    profile = db.get(BiometricProfile, user.id)
    return {"enrolled": bool(profile), "model": profile.model_version if profile else None,
            "consent_at": profile.consent_at if profile else None}


@router.delete("/biometrics", status_code=204)
def delete_biometrics(data: Login, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "biometric-delete:" + user.id, 5, 300)
    if data.email.lower() != user.email or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Password confirmation failed")
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    profile = db.get(BiometricProfile, user.id)
    if profile:
        db.delete(profile)
        audit(db, user.id, "BIOMETRIC_DELETED", severity="WARNING")
        db.commit()


def active_device(db, user_id, device_id):
    device = db.scalar(select(Device).where(Device.id == device_id).with_for_update())
    if not device or device.student_id != user_id or not device.active:
        raise HTTPException(403, "DEVICE_UNAUTHORIZED")
    return device


@router.post("/challenges", status_code=201)
def challenge(data: ChallengeInput, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "challenge:" + user.id, 8, 300)
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    active_device(db, user.id, data.device_id)
    if data.purpose == "attendance":
        session = required(db, AttendanceSession, data.session_id)
        access_course(db, user, session.course_id)
        if session.closed or not session.starts_at <= now() < session.ends_at:
            raise HTTPException(409, "SESSION_NOT_ACTIVE")
        if not db.get(BiometricProfile, user.id):
            raise HTTPException(409, "BIOMETRIC_ENROLLMENT_REQUIRED")
        ongoing = db.scalar(select(Challenge).where(Challenge.student_id == user.id, Challenge.session_id == session.id, Challenge.device_id == data.device_id,
            Challenge.used.is_(False), Challenge.expires_at > now()).order_by(Challenge.created_at.desc()))
        if ongoing:
            return {**public(ongoing), "server_time": now()}
        count = db.scalar(select(func.count()).select_from(Challenge).where(Challenge.student_id == user.id, Challenge.session_id == session.id))
        if count >= policy(db).max_attempts:
            raise HTTPException(429, "Session attempt limit reached; request faculty review")
    else:
        if data.session_id:
            raise HTTPException(422, "Enrollment challenge cannot reference a session")
        if db.get(BiometricProfile, user.id):
            raise HTTPException(409, "Delete existing biometric enrollment before re-enrolling")
    actions = [secrets.choice(["TURN_LEFT", "TURN_RIGHT"]), "BLINK"]
    secrets.SystemRandom().shuffle(actions)
    actions = ["CENTER", actions[0], "CENTER", actions[1], "CENTER"]
    current = now()
    item = Challenge(student_id=user.id, device_id=data.device_id, session_id=data.session_id,
                     purpose=data.purpose, actions=actions, created_at=current,
                     expires_at=current + timedelta(seconds=120 if data.purpose == "attendance" else settings().challenge_seconds))
    db.add(item)
    db.commit()
    return {**public(item), "server_time": current, "capture_guide": "Capture 4-6 frames/s, hold each pose for 1s; blink slowly. Unmirrored JPEG frames."}


def unpack(db, user, data):
    try:
        evidence = Evidence.model_validate_json(data.payload)
    except ValidationError:
        raise HTTPException(422, "Malformed verification evidence")
    device = active_device(db, user.id, evidence.device_id)
    message = data.idempotency_key + "." + data.payload
    if device.key_algorithm == 'ecdsa-p256-sha256':
        valid = verify_signature(device.public_key, data.signature, message)
    elif device.key_algorithm == 'hmac-sha256':
        secret = cipher().decrypt(device.secret_encrypted)
        expected = hmac.new(secret, message.encode(), hashlib.sha256).hexdigest()
        valid = hmac.compare_digest(expected, data.signature)
    else:
        valid = False
    if not valid:
        audit(db, user.id, "DEVICE_SIGNATURE_INVALID", severity="HIGH")
        db.commit()
        raise HTTPException(403, "DEVICE_SIGNATURE_INVALID")
    return evidence, device


def locked_challenge(db, user, evidence, purpose):
    item = db.scalar(select(Challenge).where(Challenge.id == evidence.challenge_id).with_for_update())
    if not item or item.student_id != user.id or item.device_id != evidence.device_id or item.purpose != purpose:
        raise HTTPException(403, "CHALLENGE_INVALID")
    return item


@router.post("/biometrics/enroll", status_code=201)
def enroll_biometrics(data: SignedEvidence, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "biometric:" + user.id, 5, 300)
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    evidence, device = unpack(db, user, data)
    item = locked_challenge(db, user, evidence, "enrollment")
    enrollment_hash = digest(data.idempotency_key + '.' + data.payload)
    if item.used and item.enrollment_request_hash == enrollment_hash and db.get(BiometricProfile, user.id):
        return {"enrolled": True, "model": MODEL_VERSION, "raw_images_retained": False}
    if item.used or item.expires_at <= now():
        audit(db, user.id, "ENROLLMENT_CHALLENGE_REPLAY", severity="HIGH")
        db.commit()
        raise HTTPException(409, "Challenge used or expired")
    if not evidence.consent:
        raise HTTPException(422, "Explicit biometric consent required")
    if db.get(BiometricProfile, user.id):
        raise HTTPException(409, "Already enrolled")
    vision = get_vision()
    item.used = True
    try:
        template, _ = vision.verify(evidence.frames, item)
    except VisionError as exc:
        audit(db, user.id, "ENROLLMENT_FAILED", severity="WARNING", reason=str(exc), **exc.diagnostics)
        db.commit()
        # Return only capture-stage diagnostics, never biometric measurements.
        details = {key: value for key, value in exc.diagnostics.items()
                   if key in {"completed_actions", "expected_action", "frame_count", "missing_landmark_frames", "frame_index"}}
        return JSONResponse({"error": {"code": 422, "message": str(exc), "details": details}}, status_code=422)
    db.add(BiometricProfile(student_id=user.id, template_encrypted=cipher().encrypt(template.astype("float32").tobytes()), model_version=MODEL_VERSION))
    item.enrollment_request_hash = enrollment_hash
    audit(db, user.id, "BIOMETRIC_ENROLLED", model=MODEL_VERSION)
    db.commit()
    return {"enrolled": True, "model": MODEL_VERSION, "raw_images_retained": False}


@router.post("/attendance/verify")
def verify_attendance(data: SignedEvidence, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "verify:" + user.id, 10, 60)
    # Serialize a student's submissions first; idempotency is checked after signature authentication.
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    evidence, device = unpack(db, user, data)
    request_hash = digest(data.payload)
    prior = db.scalar(select(AttendanceAttempt).where(AttendanceAttempt.student_id == user.id, AttendanceAttempt.idempotency_key == data.idempotency_key))
    if prior:
        if prior.request_hash != request_hash:
            raise HTTPException(409, "Idempotency key reused with different evidence")
        return public(prior)
    item = locked_challenge(db, user, evidence, "attendance")
    session = db.scalar(select(AttendanceSession).where(AttendanceSession.id == item.session_id).with_for_update())
    access_course(db, user, session.course_id)
    current = now()
    decision = None
    if item.used:
        audit(db, user.id, "CHALLENGE_REPLAY", session.id, severity="HIGH")
        db.commit()
        raise HTTPException(409, "CHALLENGE_ALREADY_USED")
    if item.expires_at <= current or session.closed or not session.starts_at <= current < session.ends_at:
        decision = Decision("EXPIRED", ["SESSION_OR_CHALLENGE_EXPIRED"], 50, {})
    count = db.scalar(select(func.count()).select_from(AttendanceAttempt).where(AttendanceAttempt.student_id == user.id, AttendanceAttempt.session_id == session.id))
    if count >= policy(db).max_attempts:
        raise HTTPException(429, "Session attempt limit reached")
    existing = db.scalar(select(AttendanceRecord).where(AttendanceRecord.student_id == user.id, AttendanceRecord.session_id == session.id))
    if existing:
        decision = Decision("REJECTED", ["ATTENDANCE_ALREADY_RECORDED"], 50, {})
    profile = db.get(BiometricProfile, user.id)
    if not profile or profile.model_version != MODEL_VERSION:
        decision = Decision("REJECTED", ["BIOMETRIC_ENROLLMENT_REQUIRED"], 80, {})
    from app.api.classroom_presence import factor_status
    dynamic_reason = factor_status(db, item, session, current)
    if decision is None:
        vision = get_vision()
        try:
            template = normalize(np.frombuffer(cipher().decrypt(profile.template_encrypted), dtype=np.float32))
            _, score = vision.verify(evidence.frames, item, template)
            room = db.get(Classroom, session.classroom_id)
            refs = list(db.scalars(select(WifiReference).where(WifiReference.classroom_id == room.id)))
            last = db.scalar(select(AttendanceAttempt).where(AttendanceAttempt.student_id == user.id).order_by(AttendanceAttempt.created_at.desc()).limit(1))
            previous = None
            if last and "latitude" in last.evidence_summary:
                previous = {**last.evidence_summary, "time": last.created_at}
            integrity = verify_platform_attestation(db, device, data, evidence)
            decision = evaluate(evidence.location, evidence.wifi, evidence.wifi_status, room, refs, policy(db), current, previous,
                                platform=device.platform, wifi_source=evidence.wifi_source, current_bssid=evidence.current_bssid,
                                attestation_verified=integrity.verified, dynamic_verified=dynamic_reason is None)
            decision.summary.update(platform=device.platform, device_key_algorithm=device.key_algorithm,
                                    key_storage_reported=device.key_storage, wifi_source=evidence.wifi_source)
            if data.attestation_assertion and not integrity.verified and decision.state == 'PRESENT':
                decision.state = 'PENDING_REVIEW'
                decision.reasons = [integrity.reason]
                decision.risk_score = max(decision.risk_score, 50)
            decision.summary.update(face_similarity=round(score, 4), liveness="PASSED", attestation=integrity.reason)
            if evidence.location:
                # Coarse coordinates for explainable travel checks; no images retained.
                decision.summary.update(latitude=round(evidence.location.latitude, 3), longitude=round(evidence.location.longitude, 3))
        except VisionError as exc:
            decision = Decision("REJECTED", [str(exc)], 100, {})
    # Inference may take seconds: never create PRESENT after the session/attempt deadline.
    if decision.state == "PRESENT" and (now() >= session.ends_at or now() >= item.expires_at):
        decision = Decision("EXPIRED", ["SESSION_OR_CHALLENGE_EXPIRED"], 50, decision.summary)
    decision.summary.update(qr_acoustic="PASSED" if dynamic_reason is None else dynamic_reason,
                            presence_policy_version=2)
    if dynamic_reason and decision.state == "PRESENT":
        decision = Decision("PENDING_REVIEW", [dynamic_reason], 50, decision.summary)
    elif dynamic_reason and dynamic_reason not in decision.reasons:
        decision.reasons.append(dynamic_reason)
    item.used = True
    attempt = AttendanceAttempt(student_id=user.id, session_id=session.id, challenge_id=item.id,
        idempotency_key=data.idempotency_key, request_hash=request_hash, state=decision.state,
        reasons=decision.reasons, risk_score=decision.risk_score, evidence_summary=decision.summary)
    db.add(attempt)
    db.flush()
    if decision.state == "PRESENT":
        db.add(AttendanceRecord(student_id=user.id, session_id=session.id, attempt_id=attempt.id))
    else:
        audit(db, user.id, "VERIFICATION_" + decision.state, session.id, severity="HIGH" if decision.risk_score >= 70 else "WARNING", reasons=decision.reasons, attempt_id=attempt.id)
        if count >= 2:
            audit(db, user.id, "REPEATED_VERIFICATION_FAILURES", session.id, severity="HIGH", attempts=count + 1)
    db.commit()
    return public(attempt)


def consume_security_challenge(db, student_id, challenge_id, purpose, device_id=None):
    item = db.scalar(select(SecurityChallenge).where(SecurityChallenge.id == challenge_id).with_for_update())
    if not item or item.student_id != student_id or item.purpose != purpose or item.device_id != device_id or item.used or item.expires_at <= now():
        raise HTTPException(409, 'SECURITY_CHALLENGE_INVALID_OR_USED')
    item.used = True
    return item


def new_security_challenge(db, user, purpose, device_id=None):
    item = SecurityChallenge(student_id=user.id, device_id=device_id, purpose=purpose,
                             nonce=secrets.token_hex(32), expires_at=now()+timedelta(seconds=120))
    db.add(item); db.commit()
    return public(item)


@router.post('/devices/registration-challenge', status_code=201)
def device_registration_challenge(user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, 'device-challenge:'+user.id, 5, 300)
    return new_security_challenge(db, user, 'device-registration')


@router.get('/attestation/capabilities')
def attestation_capabilities(user: User = Depends(student)):
    return {'apple_app_attest': 'configured' if app_attest.configured(settings()) else 'not_configured',
            'apple_environment': settings().apple_attest_environment, 'play_integrity': 'not_configured'}


@router.post('/attestation/challenge', status_code=201)
def attestation_challenge(data: AttestationChallengeInput, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, 'attest-challenge:'+user.id, 5, 300)
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    device = active_device(db, user.id, data.device_id)
    if device.platform != 'ios' or not app_attest.configured(settings()):
        raise HTTPException(503, 'APP_ATTEST_NOT_CONFIGURED_OR_UNSUPPORTED')
    return new_security_challenge(db, user, 'app-attest', device.id)


@router.post('/attestation/register', status_code=201)
def register_attestation(data: AttestationRegistration, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, 'attest-register:'+user.id, 5, 300)
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    device = active_device(db, user.id, data.device_id)
    if device.platform != 'ios' or not app_attest.configured(settings()):
        raise HTTPException(503, 'APP_ATTEST_NOT_CONFIGURED_OR_UNSUPPORTED')
    challenge = consume_security_challenge(db, user.id, data.challenge_id, 'app-attest', device.id)
    if db.scalar(select(AppAttestKey).where(AppAttestKey.device_id == device.id)):
        raise HTTPException(409, 'APP_ATTEST_KEY_ALREADY_REGISTERED')
    try:
        message = f'SPVS-ATTEST-v1.{challenge.nonce}.{device.id}.{data.key_id}'.encode()
        key = app_attest.verify_attestation(data.attestation, data.key_id, message, settings())
    except (ValueError, TypeError, KeyError, OSError, InvalidSignature, x509.ExtensionNotFound):
        audit(db, user.id, 'APP_ATTEST_REGISTRATION_FAILED', severity='HIGH')
        db.commit()  # Burn failed attestation challenges as well.
        raise HTTPException(403, 'APP_ATTEST_INVALID')
    db.add(AppAttestKey(key_id=data.key_id, device_id=device.id, public_key=key,
                       counter=0, environment=settings().apple_attest_environment))
    audit(db, user.id, 'APP_ATTEST_REGISTERED', device_id=device.id)
    db.commit()
    return {'verified': True, 'environment': settings().apple_attest_environment}


def verify_platform_attestation(db, device, data, evidence):
    if device.platform != 'ios':
        return verify_integrity(evidence.integrity_token, evidence.challenge_id, device.platform)
    if not data.attestation_assertion or not data.attestation_key_id:
        return IntegrityVerdict(False, 'APP_ATTEST_ASSERTION_MISSING')
    key = db.scalar(select(AppAttestKey).where(AppAttestKey.key_id == data.attestation_key_id,
                                             AppAttestKey.device_id == device.id).with_for_update())
    if not key or key.environment != settings().apple_attest_environment:
        return IntegrityVerdict(False, 'APP_ATTEST_KEY_UNKNOWN')
    try:
        key.counter = app_attest.verify_assertion(data.attestation_assertion,
            (data.idempotency_key+'.'+data.payload).encode(), key.public_key, key.counter, settings())
        return IntegrityVerdict(True, 'APP_ATTEST_VERIFIED')
    except (ValueError, TypeError, KeyError, InvalidSignature):
        return IntegrityVerdict(False, 'APP_ATTEST_ASSERTION_INVALID')
