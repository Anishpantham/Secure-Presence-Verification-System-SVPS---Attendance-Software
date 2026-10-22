import csv
import io
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.common import access_course, policy, public, required, session_ids
from app.core.security import audit, current_user, roles
from app.db.session import get_db
from app.models.entities import (AttendanceAttempt, AttendanceRecord, AttendanceSession, Classroom, Correction,
    Course, Dispute, Enrollment, Faculty, SecurityEvent, Student, User, WifiReference, now)
from app.schemas.contracts import (ClassroomInput, CorrectionInput, CourseInput, DisputeInput, EnrollmentInput,
    Resolve, SessionInput)

router = APIRouter(tags=["Academic workflows"])
staff = roles("faculty", "admin")
admin = roles("admin")


@router.get("/courses")
def courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Course)
    if user.role == "faculty":
        query = query.where(Course.faculty_id == user.id)
    elif user.role == "student":
        query = query.join(Enrollment).where(Enrollment.student_id == user.id)
    return [public(c) for c in db.scalars(query.order_by(Course.code))]


@router.post("/courses", status_code=201)
def add_course(data: CourseInput, user: User = Depends(admin), db: Session = Depends(get_db)):
    required(db, Faculty, data.faculty_id)
    course = Course(**data.model_dump())
    db.add(course)
    audit(db, user.id, "COURSE_CREATED", code=data.code)
    db.commit()
    return public(course)


@router.get("/courses/{course_id}/enrollments")
def enrollments(course_id: str, user: User = Depends(staff), db: Session = Depends(get_db)):
    access_course(db, user, course_id)
    return [public(u) for u in db.scalars(select(User).join(Enrollment, Enrollment.student_id == User.id).where(Enrollment.course_id == course_id))]


@router.post("/courses/{course_id}/enrollments", status_code=201)
def enroll(course_id: str, data: EnrollmentInput, user: User = Depends(admin), db: Session = Depends(get_db)):
    required(db, Course, course_id)
    required(db, Student, data.student_id)
    if not db.get(Enrollment, (course_id, data.student_id)):
        db.add(Enrollment(course_id=course_id, student_id=data.student_id))
        audit(db, user.id, "STUDENT_ENROLLED", course_id=course_id, student_id=data.student_id)
        db.commit()
    return {"enrolled": True}


@router.delete("/courses/{course_id}/enrollments/{student_id}", status_code=204)
def unenroll(course_id: str, student_id: str, user: User = Depends(admin), db: Session = Depends(get_db)):
    db.delete(required(db, Enrollment, (course_id, student_id)))
    audit(db, user.id, "STUDENT_UNENROLLED", course_id=course_id, student_id=student_id)
    db.commit()


@router.get("/classrooms")
def classrooms(user: User = Depends(staff), db: Session = Depends(get_db)):
    return [{**public(c), "wifi": [public(w) for w in db.scalars(select(WifiReference).where(WifiReference.classroom_id == c.id))]}
            for c in db.scalars(select(Classroom).order_by(Classroom.name))]


def write_room(db, data, room=None):
    if room is None:
        room = Classroom()
        db.add(room)
    for key, value in data.model_dump(exclude={"wifi"}).items():
        setattr(room, key, value)
    db.flush()
    for old in db.scalars(select(WifiReference).where(WifiReference.classroom_id == room.id)):
        db.delete(old)
    db.flush()
    for w in data.wifi:
        db.add(WifiReference(classroom_id=room.id, bssid=w.bssid.lower(), min_rssi=w.min_rssi))
    return room


@router.post("/classrooms", status_code=201)
def add_classroom(data: ClassroomInput, user: User = Depends(admin), db: Session = Depends(get_db)):
    room = write_room(db, data)
    audit(db, user.id, "CLASSROOM_CREATED", classroom_id=room.id)
    db.commit()
    return public(room)


@router.put("/classrooms/{room_id}")
def update_classroom(room_id: str, data: ClassroomInput, user: User = Depends(admin), db: Session = Depends(get_db)):
    room = write_room(db, data, required(db, Classroom, room_id))
    audit(db, user.id, "CLASSROOM_UPDATED", classroom_id=room.id)
    db.commit()
    return public(room)


@router.get("/sessions")
def sessions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AttendanceSession).where(AttendanceSession.id.in_(session_ids(db, user))).order_by(AttendanceSession.starts_at.desc()).limit(500))
    return [{**public(s), "course_name": db.get(Course, s.course_id).name, "classroom_name": db.get(Classroom, s.classroom_id).name,
             "present_count": db.scalar(select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.session_id == s.id, AttendanceRecord.status == "PRESENT"))} for s in rows]


@router.post("/sessions", status_code=201)
def add_session(data: SessionInput, user: User = Depends(staff), db: Session = Depends(get_db)):
    access_course(db, user, data.course_id)
    required(db, Classroom, data.classroom_id)
    if not timedelta(minutes=1) <= data.ends_at - data.starts_at <= timedelta(hours=8) or data.ends_at <= now():
        raise HTTPException(422, "Session must end in the future and last 1 minute to 8 hours")
    session = AttendanceSession(**data.model_dump())
    db.add(session)
    db.flush()
    audit(db, user.id, "SESSION_CREATED", session.id)
    db.commit()
    return public(session)


@router.get("/sessions/{session_id}")
def session_detail(session_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = required(db, AttendanceSession, session_id)
    course = access_course(db, user, session.course_id)
    return {**public(session), "course": public(course), "classroom": public(db.get(Classroom, session.classroom_id)),
            "policy": public(policy(db))}


@router.post("/sessions/{session_id}/close")
def close_session(session_id: str, user: User = Depends(staff), db: Session = Depends(get_db)):
    session = db.scalar(select(AttendanceSession).where(AttendanceSession.id == session_id).with_for_update())
    if not session:
        raise HTTPException(404, "Session not found")
    access_course(db, user, session.course_id)
    session.closed = True
    audit(db, user.id, "SESSION_CLOSED", session.id)
    db.commit()
    return public(session)


def records_query(db, user, model, session_id=None):
    query = select(model).where(model.session_id.in_(session_ids(db, user)))
    if user.role == "student":
        query = query.where(model.student_id == user.id)
    if session_id:
        query = query.where(model.session_id == session_id)
    return query.order_by(model.created_at.desc())


@router.get("/records")
def records(session_id: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{**public(r), "student_name": db.get(User, r.student_id).name, "student_email": db.get(User, r.student_id).email}
            for r in db.scalars(records_query(db, user, AttendanceRecord, session_id).limit(500))]


@router.get("/attempts")
def attempts(session_id: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{**public(r), "student_name": db.get(User, r.student_id).name}
            for r in db.scalars(records_query(db, user, AttendanceAttempt, session_id).limit(500))]


@router.get("/events")
def events(user: User = Depends(staff), db: Session = Depends(get_db)):
    query = select(SecurityEvent)
    if user.role == "faculty":
        query = query.where(SecurityEvent.session_id.in_(session_ids(db, user)))
    return [public(r) for r in db.scalars(query.order_by(SecurityEvent.created_at.desc()).limit(500))]


@router.post("/events/{event_id}/review")
def review_event(event_id: str, user: User = Depends(staff), db: Session = Depends(get_db)):
    event = required(db, SecurityEvent, event_id)
    if user.role == "faculty":
        if not event.session_id:
            raise HTTPException(403, "Institution-level event")
        access_course(db, user, required(db, AttendanceSession, event.session_id).course_id)
    event.reviewed = True
    audit(db, user.id, "EVENT_REVIEWED", event.session_id, event_id=event.id)
    db.commit()
    return public(event)


@router.post("/corrections", status_code=201)
def correct(data: CorrectionInput, user: User = Depends(staff), db: Session = Depends(get_db)):
    # Same session lock used by verification prevents a correction/verification race.
    session = db.scalar(select(AttendanceSession).where(AttendanceSession.id == data.session_id).with_for_update())
    if not session:
        raise HTTPException(404, "Session not found")
    access_course(db, user, session.course_id)
    if not db.get(Enrollment, (session.course_id, data.student_id)):
        raise HTTPException(422, "Student is not enrolled in this course")
    record = db.scalar(select(AttendanceRecord).where(AttendanceRecord.session_id == session.id, AttendanceRecord.student_id == data.student_id).with_for_update())
    old = record.status if record else "UNRECORDED"
    if not record:
        record = AttendanceRecord(student_id=data.student_id, session_id=session.id, status=data.status, source="CORRECTION")
        db.add(record)
        db.flush()
    record.status, record.source = data.status, "CORRECTION"
    correction = Correction(record_id=record.id, actor_id=user.id, reason=data.reason, previous_status=old, new_status=data.status)
    db.add(correction)
    audit(db, user.id, "ATTENDANCE_CORRECTED", session.id, severity="WARNING", student_id=data.student_id, reason=data.reason, previous=old, status=data.status)
    db.commit()
    return public(correction)


@router.get("/corrections")
def corrections(user: User = Depends(staff), db: Session = Depends(get_db)):
    query = select(Correction).join(AttendanceRecord).where(AttendanceRecord.session_id.in_(session_ids(db, user)))
    return [public(c) for c in db.scalars(query.order_by(Correction.created_at.desc()).limit(500))]


@router.post("/disputes", status_code=201)
def dispute(data: DisputeInput, user: User = Depends(roles("student")), db: Session = Depends(get_db)):
    attempt = required(db, AttendanceAttempt, data.attempt_id)
    if attempt.student_id != user.id:
        raise HTTPException(403, "Attempt belongs to another student")
    item = Dispute(student_id=user.id, attempt_id=attempt.id, reason=data.reason)
    db.add(item)
    audit(db, user.id, "DISPUTE_OPENED", attempt.session_id)
    db.commit()
    return public(item)


@router.get("/disputes")
def disputes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Dispute).join(AttendanceAttempt).where(AttendanceAttempt.session_id.in_(session_ids(db, user)))
    if user.role == "student":
        query = query.where(Dispute.student_id == user.id)
    return [public(d) for d in db.scalars(query.order_by(Dispute.created_at.desc()).limit(500))]


@router.post("/disputes/{dispute_id}/resolve")
def resolve_dispute(dispute_id: str, data: Resolve, user: User = Depends(staff), db: Session = Depends(get_db)):
    item = required(db, Dispute, dispute_id)
    attempt = required(db, AttendanceAttempt, item.attempt_id)
    access_course(db, user, required(db, AttendanceSession, attempt.session_id).course_id)
    item.status, item.resolution, item.reviewed_by = "RESOLVED", data.resolution, user.id
    audit(db, user.id, "DISPUTE_RESOLVED", attempt.session_id, dispute_id=item.id, resolution=data.resolution)
    db.commit()
    return public(item)


def csv_safe(value):
    value = str(value)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value


@router.get("/reports/attendance.csv")
def export(session_id: str | None = None, user: User = Depends(staff), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "student", "email", "status", "source", "recorded_at"])
    for record in db.scalars(records_query(db, user, AttendanceRecord, session_id)):
        student = db.get(User, record.student_id)
        writer.writerow([record.session_id, csv_safe(student.name), csv_safe(student.email), record.status, record.source, record.created_at.isoformat()])
    audit(db, user.id, "REPORT_EXPORTED", session_id)
    db.commit()
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="spvs-attendance.csv"'})


@router.get("/overview")
def overview(user: User = Depends(staff), db: Session = Depends(get_db)):
    scope = session_ids(db, user)
    sessions_count = db.scalar(select(func.count()).select_from(AttendanceSession).where(AttendanceSession.id.in_(scope)))
    states = dict(db.execute(select(AttendanceAttempt.state, func.count()).where(AttendanceAttempt.session_id.in_(scope)).group_by(AttendanceAttempt.state)).all())
    records_count = db.scalar(select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.session_id.in_(scope), AttendanceRecord.status == "PRESENT"))
    active = db.scalar(select(func.count()).select_from(AttendanceSession).where(AttendanceSession.id.in_(scope), AttendanceSession.closed.is_(False), AttendanceSession.starts_at <= now(), AttendanceSession.ends_at > now()))
    return {"sessions": sessions_count, "active_sessions": active, "present_records": records_count,
            "attempts_by_state": states, "pending_review": states.get("PENDING_REVIEW", 0)}
