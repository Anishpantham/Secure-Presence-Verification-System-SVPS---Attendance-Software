"""Relational records. Verification evidence images are never persisted."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def now():
    return datetime.now(timezone.utc)


class IdentityMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class User(IdentityMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Student(Base):
    __tablename__ = "students"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    roll_number: Mapped[str] = mapped_column(String(40), unique=True)


class Faculty(Base):
    __tablename__ = "faculty"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    department: Mapped[str] = mapped_column(String(100), default="Computer Science")


class Course(IdentityMixin, Base):
    __tablename__ = "courses"
    code: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    faculty_id: Mapped[str] = mapped_column(ForeignKey("faculty.user_id"), index=True)


class Enrollment(Base):
    __tablename__ = "enrollments"
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), primary_key=True)


class Classroom(IdentityMixin, Base):
    __tablename__ = "classrooms"
    name: Mapped[str] = mapped_column(String(100), unique=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    radius_m: Mapped[float] = mapped_column(Float)


class WifiReference(IdentityMixin, Base):
    __tablename__ = "wifi_references"
    __table_args__ = (UniqueConstraint("classroom_id", "bssid"),)
    classroom_id: Mapped[str] = mapped_column(ForeignKey("classrooms.id"), index=True)
    bssid: Mapped[str] = mapped_column(String(17))
    min_rssi: Mapped[int] = mapped_column(Integer, default=-80)


class Policy(Base):
    __tablename__ = "policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    max_accuracy_m: Mapped[float] = mapped_column(Float, default=35)
    max_location_age_s: Mapped[int] = mapped_column(Integer, default=20)
    wifi_unavailable: Mapped[str] = mapped_column(String(16), default="review")
    require_attestation: Mapped[bool] = mapped_column(Boolean, default=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)


class Device(IdentityMixin, Base):
    __tablename__ = "devices"
    __table_args__ = (Index("uq_active_student_device", "student_id", unique=True,
                           postgresql_where=__import__("sqlalchemy").text("active = true"),
                           sqlite_where=__import__("sqlalchemy").text("active = 1")),)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    platform: Mapped[str] = mapped_column(String(16))
    secret_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DeviceReset(IdentityMixin, Base):
    __tablename__ = "device_resets"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="OPEN")
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))


class BiometricProfile(Base):
    __tablename__ = "biometric_profiles"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), primary_key=True)
    template_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    model_version: Mapped[str] = mapped_column(String(100))
    consent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AttendanceSession(IdentityMixin, Base):
    __tablename__ = "attendance_sessions"
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), index=True)
    classroom_id: Mapped[str] = mapped_column(ForeignKey("classrooms.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)


class Challenge(IdentityMixin, Base):
    __tablename__ = "challenges"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))
    session_id: Mapped[str | None] = mapped_column(ForeignKey("attendance_sessions.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(16))
    actions: Mapped[list] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class AttendanceAttempt(IdentityMixin, Base):
    __tablename__ = "attendance_attempts"
    __table_args__ = (UniqueConstraint("student_id", "idempotency_key"),)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id"), index=True)
    challenge_id: Mapped[str] = mapped_column(ForeignKey("challenges.id"))
    idempotency_key: Mapped[str] = mapped_column(String(64))
    request_hash: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(24))
    reasons: Mapped[list] = mapped_column(JSON)
    risk_score: Mapped[int] = mapped_column(Integer)
    evidence_summary: Mapped[dict] = mapped_column(JSON)


class AttendanceRecord(IdentityMixin, Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("student_id", "session_id"),)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"), index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id"), index=True)
    attempt_id: Mapped[str | None] = mapped_column(ForeignKey("attendance_attempts.id"))
    status: Mapped[str] = mapped_column(String(24), default="PRESENT")
    source: Mapped[str] = mapped_column(String(16), default="VERIFICATION")


class SecurityEvent(IdentityMixin, Base):
    __tablename__ = "security_events"
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("attendance_sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), default="INFO")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)


class Correction(IdentityMixin, Base):
    __tablename__ = "corrections"
    record_id: Mapped[str] = mapped_column(ForeignKey("attendance_records.id"), index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(Text)
    previous_status: Mapped[str] = mapped_column(String(24))
    new_status: Mapped[str] = mapped_column(String(24))


class Dispute(IdentityMixin, Base):
    __tablename__ = "disputes"
    student_id: Mapped[str] = mapped_column(ForeignKey("students.user_id"))
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attendance_attempts.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="OPEN")
    resolution: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))


class RefreshToken(IdentityMixin, Base):
    __tablename__ = "refresh_tokens"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    family: Mapped[str] = mapped_column(String(36), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class RateBucket(Base):
    __tablename__ = "rate_buckets"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    window_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    count: Mapped[int] = mapped_column(Integer, default=0)
