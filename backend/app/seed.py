"""Idempotent development fixtures; no attendance or biometric samples are seeded."""
import os
from dotenv import load_dotenv
from sqlalchemy import select
from app.api.auth import create_user
from app.db.session import SessionLocal
from app.models.entities import Classroom, Course, Enrollment, Policy, User
from app.schemas.contracts import CreateUser


def main():
    load_dotenv("../.env")
    password = os.environ.get("DEMO_PASSWORD", "")
    if len(password) < 12:
        raise SystemExit("Set DEMO_PASSWORD with at least 12 characters in .env")
    with SessionLocal() as db:
        users = {}
        for role, name in [("admin", "Institution Administrator"), ("faculty", "Demo Faculty"), ("student", "Demo Student")]:
            email = f"{role}@spvs.example"
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                user = create_user(db, CreateUser(email=email, name=name, role=role, password=password,
                                                  roll_number="DEMO-001" if role == "student" else None))
                db.flush()
            users[role] = user
        course = db.scalar(select(Course).where(Course.code == "CS401"))
        if not course:
            course = Course(code="CS401", name="Applied Security Engineering", faculty_id=users["faculty"].id)
            db.add(course)
            db.flush()
        if not db.get(Enrollment, (course.id, users["student"].id)):
            db.add(Enrollment(course_id=course.id, student_id=users["student"].id))
        if not db.scalar(select(Classroom).where(Classroom.name == "Demo lab — configure coordinates")):
            # Explicit setup placeholder; no attendance is generated and no location evidence is fabricated.
            db.add(Classroom(name="Demo lab — configure coordinates", latitude=0, longitude=0, radius_m=50))
        if not db.get(Policy, 1):
            db.add(Policy(id=1))
        db.commit()
    print("Seeded three demo accounts, one course and a classroom requiring real coordinates. No attendance seeded.")


if __name__ == "__main__":
    main()
