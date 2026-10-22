import hashlib
import hmac
import secrets
from datetime import timedelta

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.common import access_course, policy, public, required
from app.core.config import settings
from app.core.security import audit, cipher, digest, roles, throttle, verify_password
from app.db.session import get_db
from app.models.entities import (AttendanceAttempt, AttendanceRecord, AttendanceSession, BiometricProfile,
    Challenge, Classroom, Device, User, WifiReference, now)
from app.schemas.contracts import ChallengeInput, DeviceInput, Evidence, Login, SignedEvidence
from app.services.attestation import verify_integrity
from app.services.presence import Decision, evaluate
from app.services.vision import MODEL_VERSION, VisionError, get_vision, normalize

router = APIRouter(tags=["Identity and presence"])
student = roles("student")


@router.get("/devices")
def devices(user: User = Depends(student), db: Session = Depends(get_db)):
    return [public(d) for d in db.scalars(select(Device).where(Device.student_id == user.id))]


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
    credential = secrets.token_hex(32)
    device = Device(student_id=user.id, label=data.label, platform=data.platform, secret_encrypted=cipher().encrypt(credential.encode()))
    db.add(device)
    audit(db, user.id, "DEVICE_REGISTERED", platform=data.platform)
    db.commit()
    return {**public(device), "credential": credential, "storage": "Store once in OS secure credential storage"}


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
    device = db.get(Device, device_id)
    if not device or device.student_id != user_id or not device.active:
        raise HTTPException(403, "DEVICE_UNAUTHORIZED")
    return device


@router.post("/challenges", status_code=201)
def challenge(data: ChallengeInput, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, "challenge:" + user.id, 8, 300)
    active_device(db, user.id, data.device_id)
    if data.purpose == "attendance":
        session = required(db, AttendanceSession, data.session_id)
        access_course(db, user, session.course_id)
        if session.closed or not session.starts_at <= now() < session.ends_at:
            raise HTTPException(409, "SESSION_NOT_ACTIVE")
        if not db.get(BiometricProfile, user.id):
            raise HTTPException(409, "BIOMETRIC_ENROLLMENT_REQUIRED")
        count = db.scalar(select(func.count()).select_from(AttendanceAttempt).where(AttendanceAttempt.student_id == user.id, AttendanceAttempt.session_id == session.id))
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
                     expires_at=current + timedelta(seconds=settings().challenge_seconds))
    db.add(item)
    db.commit()
    return {**public(item), "server_time": current, "capture_guide": "Capture 4-6 frames/s, hold each pose for 1s; blink slowly. Unmirrored JPEG frames."}


def unpack(db, user, data):
    try:
        evidence = Evidence.model_validate_json(data.payload)
    except ValidationError:
        raise HTTPException(422, "Malformed verification evidence")
    device = active_device(db, user.id, evidence.device_id)
    secret = cipher().decrypt(device.secret_encrypted)
    expected = hmac.new(secret, (data.idempotency_key + "." + data.payload).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, data.signature):
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
        audit(db, user.id, "ENROLLMENT_FAILED", severity="WARNING", reason=str(exc))
        db.commit()
        raise HTTPException(422, str(exc))
    db.add(BiometricProfile(student_id=user.id, template_encrypted=cipher().encrypt(template.astype("float32").tobytes()), model_version=MODEL_VERSION))
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
            decision = evaluate(evidence.location, evidence.wifi, evidence.wifi_status, room, refs, policy(db), current, previous)
            integrity = verify_integrity(evidence.integrity_token, item.id, device.platform)
            decision.summary.update(face_similarity=round(score, 4), liveness="PASSED", attestation=integrity.reason)
            if evidence.location:
                # Coarse coordinates for explainable travel checks; no images retained.
                decision.summary.update(latitude=round(evidence.location.latitude, 3), longitude=round(evidence.location.longitude, 3))
        except VisionError as exc:
            decision = Decision("REJECTED", [str(exc)], 100, {})
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
