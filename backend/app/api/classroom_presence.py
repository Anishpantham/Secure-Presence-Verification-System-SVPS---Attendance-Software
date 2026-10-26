"""Server-clock presence protocol. No endpoint exposes audio answers to students."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.common import access_course, public, required
from app.core.config import settings
from app.core.security import audit, cipher, digest, roles, throttle
from app.db.session import get_db
from app.models.entities import (AttendanceAttempt, AttendanceSession, Challenge, PresenceProof,
                                 PresenceQR, User, now)
from app.schemas.contracts import Input, SignedEvidence
from app.services.device_keys import verify_signature

router = APIRouter(tags=['Classroom presence'])
staff = roles('faculty', 'admin')
student = roles('student')


class PresenceInput(Input):
    device_id: str
    challenge_id: str
    action: str = Field(pattern=r'^(qr|ready|audio|failure)$')
    token: str | None = Field(default=None, max_length=300)
    response: str | None = Field(default=None, pattern=r'^[0-9a-f]{24}$')
    reason: str | None = Field(default=None, pattern=r'^(CAMERA_PERMISSION|MICROPHONE_PERMISSION|AUDIO_UNAVAILABLE|AUDIO_DECODE_FAILED|INTERRUPTED|NETWORK_INTERRUPTED|QR_UNAVAILABLE)$')


class Controls(Input):
    enabled: bool


def live(session, current):
    return not session.closed and session.starts_at <= current < session.ends_at


def locked_session(db, sid, user):
    session = db.scalar(select(AttendanceSession).where(AttendanceSession.id == sid).with_for_update())
    if not session:
        raise HTTPException(404, 'SESSION_NOT_FOUND')
    access_course(db, user, session.course_id)
    return session


def rotation_after(created_at):
    return datetime.fromtimestamp((int(created_at.timestamp()) // 5 + 1) * 5, timezone.utc)


def qr_mac(qr, nonce):
    message = f'SPVS-QR-v1.{qr.id}.{nonce}.{qr.session_id}.{qr.classroom_id}.{qr.epoch}'
    return hmac.new(settings().jwt_secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def valid_qr(qr, token, session, current):
    parts = token.split('.') if token else []
    return bool(qr and len(parts) == 4 and parts[0] == 'SPVS1' and parts[1] == qr.id
        and qr.session_id == session.id and qr.classroom_id == session.classroom_id
        and qr.epoch == session.presence_epoch and qr.created_at <= current < qr.expires_at
        and hmac.compare_digest(token, qr.token) and hmac.compare_digest(parts[3], qr_mac(qr, parts[2])))


@router.post('/sessions/{sid}/presence/control')
def control(sid: str, data: Controls, user: User = Depends(staff), db: Session = Depends(get_db)):
    throttle(db, 'presence-control:'+user.id, 30)
    session = locked_session(db, sid, user)
    if data.enabled and not live(session, now()):
        raise HTTPException(409, 'SESSION_NOT_ACTIVE')
    if session.presence_enabled != data.enabled:
        session.presence_enabled = data.enabled
        session.presence_epoch += 1  # Invalidates pending AND verified proofs from previous display runs.
        audit(db, user.id, 'PRESENCE_STARTED' if data.enabled else 'PRESENCE_STOPPED', sid)
    db.commit()
    return {'enabled': session.presence_enabled}


@router.get('/sessions/{sid}/presence/display')
def display(sid: str, user: User = Depends(staff), db: Session = Depends(get_db)):
    throttle(db, 'presence-display:'+user.id, 240)
    session = locked_session(db, sid, user)
    current = now()
    if not live(session, current) or not session.presence_enabled:
        return {'enabled': False, 'server_time': current, 'ends_at': session.ends_at, 'queue': []}
    qr = db.scalar(select(PresenceQR).where(PresenceQR.session_id == sid, PresenceQR.epoch == session.presence_epoch)
        .order_by(PresenceQR.created_at.desc()).limit(1))
    if not qr or current >= rotation_after(qr.created_at):
        qr = PresenceQR(id=str(uuid4()), session_id=sid, classroom_id=session.classroom_id,
            epoch=session.presence_epoch, created_at=current, expires_at=min(current+timedelta(seconds=10), session.ends_at))
        nonce = secrets.token_urlsafe(24)
        qr.token = f'SPVS1.{qr.id}.{nonce}.{qr_mac(qr, nonce)}'
        db.add(qr)
        db.flush()
    queue = list(db.scalars(select(PresenceProof).join(Challenge).join(PresenceQR, PresenceProof.qr_id == PresenceQR.id)
        .where(Challenge.session_id == sid, Challenge.used.is_(False), Challenge.expires_at > current,
               PresenceQR.epoch == session.presence_epoch, PresenceProof.ready_at.is_not(None),
               PresenceProof.audio_started_at.is_(None)).order_by(PresenceProof.ready_at).limit(100)))
    result = {'enabled': True, 'server_time': current, 'ends_at': session.ends_at, 'token': qr.token,
              'rotate_at': rotation_after(qr.created_at), 'expires_at': qr.expires_at,
              'queue': [{'attempt_id': p.challenge_id, 'label': p.challenge_id[:8]} for p in queue]}
    db.commit()
    return result


@router.post('/sessions/{sid}/presence/play/{attempt_id}')
def play(sid: str, attempt_id: str, user: User = Depends(staff), db: Session = Depends(get_db)):
    throttle(db, 'presence-play:'+user.id, 30)
    session = locked_session(db, sid, user)
    current = now()
    item = required(db, Challenge, attempt_id)
    proof = db.scalar(select(PresenceProof).where(PresenceProof.challenge_id == attempt_id).with_for_update())
    if not live(session, current) or not session.presence_enabled or item.session_id != sid or item.used or item.expires_at <= current:
        raise HTTPException(409, 'SESSION_OR_ATTEMPT_EXPIRED')
    if not proof or not proof.ready_at or proof.audio_started_at or db.get(PresenceQR, proof.qr_id).epoch != session.presence_epoch:
        raise HTTPException(409, 'AUDIO_NOT_READY_OR_ALREADY_ISSUED')
    # Serialize laptop playback across tabs/attempts. Never mix simultaneous classroom signals.
    busy = db.scalar(select(PresenceProof.challenge_id).join(Challenge).where(Challenge.session_id == sid,
        PresenceProof.audio_expires_at > current))
    if busy:
        raise HTTPException(409, 'AUDIO_CHANNEL_BUSY')
    answer = item.id.replace('-', '')[:8] + secrets.token_hex(8)  # Routing tag + 64 unpredictable bits; one guess only.
    proof.audio_hash = digest(answer)
    proof.audio_started_at = current
    proof.audio_expires_at = min(current+timedelta(seconds=5), item.expires_at, session.ends_at)
    audit(db, user.id, 'ACOUSTIC_ISSUED', sid, attempt_id=attempt_id)
    db.commit()
    return {'payload': answer, 'server_time': current, 'expires_at': proof.audio_expires_at,
            'duration_ms': 2700, 'codec': 'spvs-fsk16-v1'}


def authenticated(db, user, data):
    from app.api.verification import active_device
    try:
        evidence = PresenceInput.model_validate_json(data.payload)
    except ValidationError:
        raise HTTPException(422, 'MALFORMED_PRESENCE_MESSAGE')
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    device = active_device(db, user.id, evidence.device_id)
    message = data.idempotency_key+'.'+data.payload
    valid = verify_signature(device.public_key, data.signature, message) if device.key_algorithm == 'ecdsa-p256-sha256' else (
        device.key_algorithm == 'hmac-sha256' and hmac.compare_digest(data.signature,
            hmac.new(cipher().decrypt(device.secret_encrypted), message.encode(), hashlib.sha256).hexdigest()))
    if not valid:
        raise HTTPException(403, 'DEVICE_SIGNATURE_INVALID')
    item = db.scalar(select(Challenge).where(Challenge.id == evidence.challenge_id).with_for_update())
    if not item or item.student_id != user.id or item.device_id != device.id or item.purpose != 'attendance':
        raise HTTPException(403, 'ATTEMPT_INVALID')
    session = locked_session(db, item.session_id, user)
    return evidence, item, session


def reject(db, user, item, reason):
    audit(db, user.id, 'PRESENCE_REJECTED', item.session_id, attempt_id=item.id, reason=reason)
    db.commit()
    raise HTTPException(409, reason)


@router.post('/presence/evidence')
def redeem(data: SignedEvidence, user: User = Depends(student), db: Session = Depends(get_db)):
    throttle(db, 'presence-evidence:'+user.id, 40)
    evidence, item, session = authenticated(db, user, data)
    current = now()  # Clock sampled AFTER locks; queued HTTP requests cannot backdate receipt.
    if evidence.action == 'failure':
        prior = db.scalar(select(AttendanceAttempt).where(AttendanceAttempt.challenge_id == item.id))
        if prior:
            return public(prior)
        if not evidence.reason:
            raise HTTPException(422, 'FAILURE_REASON_REQUIRED')
        item.used = True
        attempt = AttendanceAttempt(student_id=user.id, session_id=session.id, challenge_id=item.id,
            idempotency_key=data.idempotency_key, request_hash=digest(data.payload), state='PENDING_REVIEW',
            reasons=[evidence.reason], risk_score=50, evidence_summary={'presence_policy_version': 2, 'identity': 'NOT_COMPLETED'})
        db.add(attempt)
        db.flush()
        audit(db, user.id, 'PRESENCE_INCOMPLETE', session.id, attempt_id=attempt.id, reason=evidence.reason)
        db.commit()
        return public(attempt)
    if item.used or item.expires_at <= current or not live(session, current) or not session.presence_enabled:
        reject(db, user, item, 'SESSION_OR_ATTEMPT_EXPIRED_OR_STOPPED')
    proof = db.scalar(select(PresenceProof).where(PresenceProof.challenge_id == item.id).with_for_update())
    if evidence.action == 'qr':
        qr = db.scalar(select(PresenceQR).where(PresenceQR.token == evidence.token)) if evidence.token else None
        if proof:
            if not qr or proof.qr_id != qr.id or qr.epoch != session.presence_epoch:
                reject(db, user, item, 'QR_ALREADY_BOUND')
            return {'qr': 'VERIFIED', 'attempt_id': item.id}
        if not valid_qr(qr, evidence.token, session, current):
            reject(db, user, item, 'QR_INVALID_OR_EXPIRED')
        if db.scalar(select(PresenceProof).where(PresenceProof.qr_id == qr.id, PresenceProof.student_id == user.id)):
            reject(db, user, item, 'QR_ALREADY_REDEEMED')
        proof = PresenceProof(challenge_id=item.id, student_id=user.id, qr_id=qr.id, qr_verified_at=current)
        db.add(proof)
    else:
        if not proof or db.get(PresenceQR, proof.qr_id).epoch != session.presence_epoch:
            reject(db, user, item, 'QR_REQUIRED')
        if evidence.action == 'ready':
            if proof.audio_consumed:
                reject(db, user, item, 'AUDIO_CONSUMED')
            proof.ready_at = proof.ready_at or current
        elif evidence.action == 'audio':
            request_hash = digest(data.payload)
            if proof.audio_verified_at and proof.audio_request_hash == request_hash:
                return {'audio': 'VERIFIED', 'attempt_id': item.id}
            if proof.audio_consumed:
                reject(db, user, item, 'AUDIO_CONSUMED')
            if not proof.audio_started_at:
                reject(db, user, item, 'AUDIO_NOT_ISSUED')
            proof.audio_consumed = True  # Burn wrong and late answers too; no online guessing.
            reason = 'AUDIO_EXPIRED' if current >= proof.audio_expires_at else 'AUDIO_MISMATCH'
            if current < proof.audio_expires_at and evidence.response and hmac.compare_digest(digest(evidence.response), proof.audio_hash):
                proof.audio_verified_at = current
                proof.audio_request_hash = request_hash
                reason = 'ACOUSTIC_VERIFIED'
            audit(db, user.id, reason, session.id, attempt_id=item.id)
            db.commit()
            if reason != 'ACOUSTIC_VERIFIED':
                raise HTTPException(409, reason)
    db.commit()
    return {'attempt_id': item.id, 'qr': 'VERIFIED', 'audio': 'VERIFIED' if proof.audio_verified_at else 'WAITING'}


def factor_status(db, item, session, current):
    if not session.presence_enabled:
        return 'CLASSROOM_CHALLENGES_STOPPED'
    proof = db.get(PresenceProof, item.id)
    if not proof:
        return 'QR_REQUIRED'
    qr = db.get(PresenceQR, proof.qr_id)
    if qr.epoch != session.presence_epoch:
        return 'CLASSROOM_CHALLENGES_RESTARTED'
    if not proof.audio_verified_at:
        return 'ACOUSTIC_REQUIRED'
    return None
