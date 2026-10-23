from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.auth import create_user
from app.api.common import policy, public, required
from app.core.security import audit, current_user, roles
from app.db.session import get_db
from app.models.entities import Device, DeviceReset, AppAttestKey, Faculty, RefreshToken, Student, User, now
from app.schemas.contracts import CreateUser, PolicyInput, Reason, UserUpdate

router = APIRouter(tags=["Administration"])
admin = roles("admin")


@router.get("/users")
def users(user: User = Depends(admin), db: Session = Depends(get_db)):
    return [public(u) for u in db.scalars(select(User).order_by(User.name).limit(500))]


@router.post("/users", status_code=201)
def add_user(data: CreateUser, user: User = Depends(admin), db: Session = Depends(get_db)):
    item = create_user(db, data)
    audit(db, user.id, "USER_CREATED", target_id=item.id, role=item.role)
    db.commit()
    return public(item)


@router.patch("/users/{user_id}")
def disable(user_id: str, data: UserUpdate, user: User = Depends(admin), db: Session = Depends(get_db)):
    if user.id == user_id:
        raise HTTPException(422, "Cannot change your own access or role")
    item = required(db, User, user_id)
    db.scalar(select(User).where(User.id == user_id).with_for_update())
    if data.role and data.role != item.role:
        if not data.reason:
            raise HTTPException(422, "Role changes require an audit reason")
        if data.role == "student" and not db.get(Student, user_id):
            if not data.roll_number:
                raise HTTPException(422, "Student role requires a roll number")
            db.add(Student(user_id=user_id, roll_number=data.roll_number))
        if data.role == "faculty" and not db.get(Faculty, user_id):
            db.add(Faculty(user_id=user_id))
        previous = item.role
        item.role = data.role
        # Retain subtype rows referenced by historical records; access uses the current User role.
        db.execute(update(Device).where(Device.student_id == user_id, Device.active.is_(True)).values(active=False, revoked_at=now()))
        db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True))
        audit(db, user.id, "USER_ROLE_CHANGED", severity="HIGH", target_id=user_id, previous=previous, role=data.role, reason=data.reason)
    if data.active is not None:
        item.active = data.active
    if data.active is False:
        db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True))
    audit(db, user.id, "USER_ACCESS_CHANGED", target_id=user_id, active=data.active)
    db.commit()
    return public(item)


@router.get("/policy")
def get_policy(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return public(policy(db))


@router.put("/policy")
def set_policy(data: PolicyInput, user: User = Depends(admin), db: Session = Depends(get_db)):
    item = policy(db)
    before = public(item)
    for key, value in data.model_dump(exclude={"reason"}).items():
        setattr(item, key, value)
    audit(db, user.id, "POLICY_CHANGED", severity="WARNING", before=before, after=data.model_dump())
    db.commit()
    return public(item)


@router.post("/device-resets", status_code=201)
def request_reset(data: Reason, user: User = Depends(roles("student")), db: Session = Depends(get_db)):
    if db.scalar(select(DeviceReset).where(DeviceReset.student_id == user.id, DeviceReset.status == "OPEN")):
        raise HTTPException(409, "A device reset request is already open")
    item = DeviceReset(student_id=user.id, reason=data.reason)
    db.add(item)
    audit(db, user.id, "DEVICE_RESET_REQUESTED", severity="WARNING")
    db.commit()
    return public(item)


@router.get("/device-resets")
def resets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(DeviceReset)
    if user.role != "admin":
        query = query.where(DeviceReset.student_id == user.id)
    return [public(r) for r in db.scalars(query.order_by(DeviceReset.created_at.desc()).limit(500))]


@router.post("/device-resets/{reset_id}/approve")
def approve_reset(reset_id: str, data: Reason, user: User = Depends(admin), db: Session = Depends(get_db)):
    item = required(db, DeviceReset, reset_id)
    db.scalar(select(User).where(User.id == item.student_id).with_for_update())
    if item.status != "OPEN":
        raise HTTPException(409, "Request already reviewed")
    db.execute(update(Device).where(Device.student_id == item.student_id, Device.active.is_(True)).values(active=False, revoked_at=now()))
    item.status, item.reviewed_by = "APPROVED", user.id
    audit(db, user.id, "DEVICE_RESET_APPROVED", severity="HIGH", student_id=item.student_id, reason=data.reason)
    db.commit()
    return public(item)


@router.get('/admin/devices')
def device_capabilities(user: User = Depends(admin), db: Session = Depends(get_db)):
    return [{**public(device, exclude=('public_key',)),
             'app_attest_registered': bool(db.scalar(select(AppAttestKey.key_id).where(AppAttestKey.device_id == device.id))),
             'hardware_storage_verified': False}
            for device in db.scalars(select(Device).order_by(Device.created_at.desc()).limit(500))]
