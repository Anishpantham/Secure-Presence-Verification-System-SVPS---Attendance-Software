import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

# Legacy compatibility fixtures only; new client registration uses native P-256 keys.
os.environ["ALLOW_LEGACY_DEVICE_REGISTRATION"] = "true"

root = Path(__file__).resolve().parents[2]
local = dotenv_values(root / ".env")
for key in ["JWT_SECRET", "BIOMETRIC_KEY"]:
    if key not in os.environ and local.get(key):
        os.environ[key] = local[key]
url = make_url(os.environ.get("SPVS_TEST_DATABASE_URL") or local.get("DATABASE_URL", "postgresql+psycopg://spvs@localhost/spvs"))
if not os.environ.get("SPVS_TEST_DATABASE_URL"):
    url = url.set(database="spvs_test")
if not url.database.endswith("_test"):
    raise RuntimeError("Destructive tests require a database name ending in _test")
os.environ["DATABASE_URL"] = url.render_as_string(hide_password=False)

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models.entities import User, Student, Faculty, Course, Classroom, Enrollment, Policy
from app.core.security import passwords

PASSWORD = "test-only-correct-password"


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    config = Config(str(root / "backend/alembic.ini"))
    config.set_main_option("script_location", str(root / "backend/alembic"))
    command.upgrade(config, "head")
    yield


@pytest.fixture(autouse=True)
def clean_database(migrated_database):
    with engine.begin() as connection:
        names = ",".join('"' + t.name + '"' for t in Base.metadata.sorted_tables)
        connection.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def world(db):
    hashed = passwords.hash(PASSWORD)
    users = {}
    for role in ["admin", "faculty", "student", "other_faculty", "other_student"]:
        actual = role.replace("other_", "")
        user = User(name=role, email=f"{role}@spvs.example", role=actual, password_hash=hashed)
        db.add(user)
        db.flush()
        if actual == "student":
            db.add(Student(user_id=user.id, roll_number=role))
        elif actual == "faculty":
            db.add(Faculty(user_id=user.id))
        users[role] = user
    db.flush()
    course = Course(code="TEST101", name="Test Course", faculty_id=users["faculty"].id)
    room = Classroom(name="Test lab", latitude=12.9716, longitude=77.5946, radius_m=60)
    db.add_all([course, room, Policy(id=1, wifi_unavailable="gps_only")])
    db.flush()
    db.add(Enrollment(course_id=course.id, student_id=users["student"].id))
    db.commit()
    return {**users, "course": course, "room": room}


@pytest.fixture
def auth(client, world):
    def login(role):
        response = client.post("/api/v1/auth/login", json={"email": world[role].email, "password": PASSWORD})
        assert response.status_code == 200, response.text
        return {"Authorization": "Bearer " + response.json()["access_token"]}
    return login
