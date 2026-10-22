from fastapi import HTTPException
from sqlalchemy import inspect, select

from app.models.entities import AttendanceSession, Course, Enrollment, Policy


def public(row, exclude=()):
    hidden = {"password_hash", "secret_encrypted", "template_encrypted", "token_hash", "request_hash"} | set(exclude)
    return {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs if c.key not in hidden}


def required(db, model, key):
    item = db.get(model, key)
    if not item:
        raise HTTPException(404, "Resource not found")
    return item


def access_course(db, user, course_id):
    course = required(db, Course, course_id)
    if user.role == "faculty" and course.faculty_id != user.id:
        raise HTTPException(403, "Course is not assigned to you")
    if user.role == "student" and not db.get(Enrollment, (course_id, user.id)):
        raise HTTPException(403, "Student is not enrolled")
    return course


def session_ids(db, user):
    query = select(AttendanceSession.id).join(Course)
    if user.role == "faculty":
        query = query.where(Course.faculty_id == user.id)
    elif user.role == "student":
        query = query.join(Enrollment, Enrollment.course_id == Course.id).where(Enrollment.student_id == user.id)
    return query


def policy(db):
    result = db.get(Policy, 1)
    if not result:
        result = Policy(id=1)
        db.add(result)
        db.flush()
    return result
