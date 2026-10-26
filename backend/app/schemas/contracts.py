from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class CreateUser(Input):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=128)
    role: Literal["student", "faculty", "admin"] = "student"
    roll_number: str | None = Field(default=None, min_length=2, max_length=40)


class Refresh(Input):
    refresh_token: str = Field(min_length=32, max_length=200)


class UserUpdate(Input):
    active: bool | None = None
    role: Literal["student", "faculty", "admin"] | None = None
    roll_number: str | None = Field(default=None, min_length=2, max_length=40)
    reason: str | None = Field(default=None, min_length=10, max_length=1000)


class CourseInput(Input):
    code: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=160)
    faculty_id: str


class EnrollmentInput(Input):
    student_id: str


class WifiObservation(Input):
    bssid: str = Field(pattern=r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")
    rssi: int = Field(ge=-127, le=0)

    @field_validator("bssid")
    @classmethod
    def lower(cls, v):
        return v.lower()


class WifiInput(Input):
    bssid: str = Field(pattern=r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")
    min_rssi: int = Field(default=-80, ge=-100, le=-20)


class ClassroomInput(Input):
    name: str = Field(min_length=2, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(ge=5, le=300)
    wifi: list[WifiInput] = Field(default_factory=list, max_length=50)


class SessionInput(Input):
    course_id: str
    classroom_id: str
    starts_at: datetime
    ends_at: datetime

    @field_validator("starts_at", "ends_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("Timezone is required")
        return value


class PolicyInput(Input):
    max_accuracy_m: float = Field(default=35, ge=5, le=100)
    max_location_age_s: int = Field(default=20, ge=5, le=60)
    wifi_unavailable: Literal["review", "gps_only", "reject"] = "review"
    ios_presence: Literal["review", "retry", "gps_only", "dynamic"] = "dynamic"
    require_attestation: bool = False
    max_attempts: int = Field(default=5, ge=1, le=10)
    reason: str = Field(min_length=10, max_length=1000)


class Reason(Input):
    reason: str = Field(min_length=10, max_length=1000)


class CorrectionInput(Reason):
    student_id: str
    session_id: str
    status: Literal["PRESENT", "ABSENT", "EXCUSED"]


class DisputeInput(Reason):
    attempt_id: str


class Resolve(Input):
    resolution: str = Field(min_length=10, max_length=1000)


class DeviceInput(Input):
    label: str = Field(min_length=2, max_length=100)
    platform: Literal["android", "ios"]
    password: str = Field(min_length=1, max_length=128)
    public_key: str | None = Field(default=None, max_length=200)
    registration_challenge_id: str | None = None
    registration_signature: str | None = Field(default=None, max_length=200)
    key_storage: Literal["secure-enclave", "keychain", "android-keystore", "android-hardware"] = "keychain"


class AttestationChallengeInput(Input):
    device_id: str


class AttestationRegistration(AttestationChallengeInput):
    challenge_id: str
    key_id: str = Field(min_length=40, max_length=100)
    attestation: str = Field(min_length=100, max_length=30000)


class ChallengeInput(Input):
    device_id: str
    purpose: Literal["attendance", "enrollment"]
    session_id: str | None = None


class Frame(Input):
    jpeg: str = Field(min_length=100, max_length=350_000)
    captured_at: datetime

    @field_validator("captured_at")
    @classmethod
    def aware(cls, v):
        if v.tzinfo is None:
            raise ValueError("Timezone required")
        return v


class Location(Input):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float = Field(ge=0, le=10000)
    captured_at: datetime
    mocked: bool = False
    accuracy_authorization: Literal["full", "reduced", "unknown"] = "unknown"

    @field_validator("captured_at")
    @classmethod
    def aware(cls, v):
        if v.tzinfo is None:
            raise ValueError("Timezone required")
        return v


class Evidence(Input):
    challenge_id: str
    device_id: str
    frames: list[Frame] = Field(min_length=8, max_length=40)
    consent: bool = False
    location: Location | None = None
    wifi: list[WifiObservation] = Field(default_factory=list, max_length=50)
    wifi_status: Literal["available", "unsupported", "permission_denied", "unavailable"] = "unavailable"
    integrity_token: str | None = Field(default=None, max_length=10000)
    wifi_source: Literal["scan", "current_network", "none"] = "scan"
    current_bssid: str | None = Field(default=None, pattern=r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")


class SignedEvidence(Input):
    # Exact JSON string signed by HMAC-SHA256; avoids cross-language canonicalization differences.
    payload: str = Field(min_length=100, max_length=14_100_000)
    signature: str = Field(min_length=40, max_length=200, pattern=r"^[a-zA-Z0-9+/=]+$")
    idempotency_key: str = Field(pattern=r"^[a-zA-Z0-9_-]{16,64}$")
    attestation_key_id: str | None = Field(default=None, max_length=100)
    attestation_assertion: str | None = Field(default=None, max_length=10000)
