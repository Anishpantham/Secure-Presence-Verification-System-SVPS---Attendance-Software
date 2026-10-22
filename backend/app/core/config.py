from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    database_url: str = "postgresql+psycopg://spvs@localhost:5432/spvs"
    jwt_secret: str = Field(min_length=32)
    biometric_key: str  # Fernet key, separate from JWT signing key
    access_minutes: int = 15
    refresh_days: int = 7
    cors_origins: str = "http://localhost:5173"
    model_dir: Path = Path("../models")
    face_threshold: float = Field(default=0.5, ge=0.363, le=0.95)
    challenge_seconds: int = Field(default=60, ge=20, le=120)
    environment: str = "development"
    allow_registration: bool = False

    @field_validator("biometric_key")
    @classmethod
    def valid_key(cls, value: str) -> str:
        from cryptography.fernet import Fernet
        Fernet(value.encode())
        return value


@lru_cache
def settings() -> Settings:
    return Settings()
