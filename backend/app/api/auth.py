from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.common import public
from app.core.config import settings
from app.core.security import audit, current_user, digest, issue_tokens, passwords, throttle, verify_password
from app.db.session import get_db
from app.models.entities import Faculty, RefreshToken, Student, User, now
from app.schemas.contracts import CreateUser, Login, Refresh

router = APIRouter(prefix="/auth", tags=["Authentication"])
DUMMY_HASH = passwords.hash("spvs-constant-time-placeholder")


def create_user(db, data):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(409, "Email already exists")
    if data.role == "student" and not data.roll_number:
        raise HTTPException(422, "Student roll number is required")
    user = User(email=data.email.lower(), name=data.name, password_hash=passwords.hash(data.password), role=data.role)
    db.add(user)
    db.flush()
    if user.role == "student":
        db.add(Student(user_id=user.id, roll_number=data.roll_number))
    elif user.role == "faculty":
        db.add(Faculty(user_id=user.id))
    return user


@router.post("/register", status_code=201)
def register(data: CreateUser, request: Request, db: Session = Depends(get_db)):
    if not settings().allow_registration:
        raise HTTPException(403, "Accounts are institution-managed")
    throttle(db, "register:" + request.client.host, 5, 3600)
    if data.role != "student":
        raise HTTPException(403, "Only student self-registration is permitted")
    user = create_user(db, data)
    audit(db, user.id, "ACCOUNT_REGISTERED")
    db.commit()
    return public(user)


@router.post("/login")
def login(data: Login, request: Request, db: Session = Depends(get_db)):
    throttle(db, "login-ip:" + request.client.host, 40, 300)
    throttle(db, "login-account:" + digest(data.email.lower()), 10, 300)
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    valid = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid or not user.active:
        audit(db, user.id if user else None, "LOGIN_FAILED", severity="WARNING")
        db.commit()
        raise HTTPException(401, "Invalid email or password")
    tokens = issue_tokens(db, user)
    audit(db, user.id, "LOGIN_SUCCEEDED")
    db.commit()
    return {**tokens, "user": public(user)}


@router.post("/refresh")
def refresh(data: Refresh, db: Session = Depends(get_db)):
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest(data.refresh_token)).with_for_update())
    if not record:
        raise HTTPException(401, "Invalid refresh token")
    if record.used or record.revoked:
        db.execute(update(RefreshToken).where(RefreshToken.family == record.family).values(revoked=True))
        audit(db, record.user_id, "REFRESH_TOKEN_REUSE", severity="HIGH")
        db.commit()
        raise HTTPException(401, "Refresh token replay; token family revoked")
    user = db.get(User, record.user_id)
    if record.expires_at <= now() or not user or not user.active:
        raise HTTPException(401, "Refresh session expired")
    record.used = True
    tokens = issue_tokens(db, user, record.family)
    db.commit()
    return tokens


@router.post("/logout", status_code=204)
def logout(data: Refresh, db: Session = Depends(get_db)):
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest(data.refresh_token)))
    if record:
        db.execute(update(RefreshToken).where(RefreshToken.family == record.family).values(revoked=True))
        db.commit()


@router.get("/me")
def me(user: User = Depends(current_user)):
    return public(user)
