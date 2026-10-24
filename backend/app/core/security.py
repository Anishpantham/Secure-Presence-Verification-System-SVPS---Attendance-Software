import hashlib
import secrets
from datetime import timedelta
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import RateBucket, RefreshToken, SecurityEvent, User, now

passwords = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
bearer = HTTPBearer(auto_error=False)


def cipher():
    return Fernet(settings().biometric_key.encode())


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_password(value, hashed):
    try:
        return passwords.verify(hashed, value)
    except VerificationError:
        return False


def issue_tokens(db: Session, user: User, family=None):
    current = now()
    access = jwt.encode({"sub": user.id, "iat": current, "exp": current + timedelta(minutes=settings().access_minutes),
                         "jti": str(uuid4()), "iss": "spvs", "aud": "spvs-clients", "type": "access"},
                        settings().jwt_secret, algorithm="HS256")
    refresh = secrets.token_urlsafe(48)
    db.add(RefreshToken(user_id=user.id, token_hash=digest(refresh), family=family or str(uuid4()),
                        expires_at=current + timedelta(days=settings().refresh_days)))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "expires_in": settings().access_minutes * 60}


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    try:
        if credentials is None:
            raise ValueError("missing")
        data = jwt.decode(credentials.credentials, settings().jwt_secret, algorithms=["HS256"],
                          audience="spvs-clients", issuer="spvs", options={"require": ["exp", "iat", "sub", "jti"]})
        if data.get("type") != "access":
            raise ValueError("type")
        user = db.get(User, data["sub"])
        if not user or not user.active:
            raise ValueError("user")
        return user
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(401, "Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"})


def roles(*allowed):
    def check(user: User = Depends(current_user)):
        if user.role not in allowed:
            raise HTTPException(403, "Role not permitted")
        return user
    return check


def audit(db, actor_id, kind, session_id=None, severity="INFO", **details):
    db.add(SecurityEvent(actor_id=actor_id, kind=kind, session_id=session_id, severity=severity, details=details))


def throttle(db: Session, key: str, limit: int, seconds=60):
    """Postgres upsert + row lock: shared across API workers, no process-local bypass."""
    from sqlalchemy.dialects.postgresql import insert
    current = now()
    db.execute(insert(RateBucket).values(key=key, window_at=current, count=0).on_conflict_do_nothing())
    bucket = db.scalar(select(RateBucket).where(RateBucket.key == key).with_for_update())
    if (current - bucket.window_at).total_seconds() >= seconds:
        bucket.window_at, bucket.count = current, 0
    bucket.count += 1
    blocked = bucket.count > limit
    db.commit()
    if blocked:
        from math import ceil
        remaining = max(1, ceil(seconds - (current - bucket.window_at).total_seconds()))
        raise HTTPException(429, "Too many requests; try again shortly", headers={"Retry-After": str(remaining)})
