from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import inspect, select, text

from app.models.entities import AttendanceRecord, AttendanceSession, Correction, RefreshToken, SecurityEvent, now
from conftest import PASSWORD


def session_payload(world):
    return {"course_id": world["course"].id, "classroom_id": world["room"].id,
            "starts_at": (now()-timedelta(minutes=1)).isoformat(), "ends_at": (now()+timedelta(minutes=10)).isoformat()}


def test_migrations_create_tables_and_unique_constraint(db):
    inspector = inspect(db.bind)
    assert len(inspector.get_table_names()) >= 20
    constraints = inspector.get_unique_constraints("attendance_records")
    assert any(set(c["column_names"]) == {"student_id", "session_id"} for c in constraints)
    assert db.execute(text("select version_num from alembic_version")).scalar()


def test_health(client):
    assert client.get("/health").json() == {"status":"ok", "database":"connected"}


@pytest.mark.parametrize("path", ["/courses", "/users", "/sessions", "/records", "/events", "/policy"])
def test_requires_authentication(client, path):
    assert client.get("/api/v1"+path).status_code == 401


def test_invalid_jwt_and_password(client, world):
    assert client.get("/api/v1/courses",headers={"Authorization":"Bearer forged"}).status_code == 401
    assert client.post("/api/v1/auth/login",json={"email":world["student"].email,"password":"wrong"}).status_code == 401


def test_login_me_no_password_leak(client, auth):
    r = client.get("/api/v1/auth/me", headers=auth("student"))
    assert r.status_code == 200 and r.json()["role"] == "student"
    assert "password_hash" not in r.text


def test_refresh_rotation_and_family_revocation(client, world):
    tokens = client.post("/api/v1/auth/login",json={"email":world["student"].email,"password":PASSWORD}).json()
    rotated = client.post("/api/v1/auth/refresh",json={"refresh_token":tokens["refresh_token"]})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != tokens["refresh_token"]
    assert client.post("/api/v1/auth/refresh",json={"refresh_token":tokens["refresh_token"]}).status_code == 401
    assert client.post("/api/v1/auth/refresh",json={"refresh_token":rotated.json()["refresh_token"]}).status_code == 401


def test_logout_revokes_refresh(client, world):
    tokens=client.post("/api/v1/auth/login",json={"email":world["student"].email,"password":PASSWORD}).json()
    assert client.post("/api/v1/auth/logout",json={"refresh_token":tokens["refresh_token"]}).status_code == 204
    assert client.post("/api/v1/auth/refresh",json={"refresh_token":tokens["refresh_token"]}).status_code == 401


@pytest.mark.parametrize("path", ["/users", "/events", "/reports/attendance.csv", "/classrooms"])
def test_student_cannot_access_staff_data(client, auth, path):
    assert client.get("/api/v1"+path,headers=auth("student")).status_code == 403


def test_self_registration_disabled_and_no_role_escalation(client):
    result=client.post("/api/v1/auth/register",json={"email":"attacker@spvs.example","name":"Attacker","password":PASSWORD,"role":"admin"})
    assert result.status_code == 403


def test_admin_user_course_and_enrollment_crud(client, auth, world):
    headers=auth("admin")
    r=client.post("/api/v1/users",headers=headers,json={"name":"New Student","email":"new@spvs.example","password":PASSWORD,"role":"student","roll_number":"NEW01"})
    assert r.status_code==201
    student=r.json()["id"]
    path=f'/api/v1/courses/{world["course"].id}/enrollments'
    assert client.post(path,headers=headers,json={"student_id":student}).status_code==201
    assert len(client.get(path,headers=headers).json())==2
    assert client.delete(path+'/'+student,headers=headers).status_code==204
    assert client.patch('/api/v1/users/'+student,headers=headers,json={"active":False}).json()["active"] is False
    assert client.post('/api/v1/auth/login',json={"email":"new@spvs.example","password":PASSWORD}).status_code==401


def test_classroom_wifi_and_policy_audit(client, auth, db):
    headers=auth('admin')
    data={"name":"New lab","latitude":10,"longitude":20,"radius_m":50,"wifi":[{"bssid":"AA:BB:CC:DD:EE:FF","min_rssi":-75}]}
    room=client.post('/api/v1/classrooms',headers=headers,json=data)
    assert room.status_code==201
    assert client.put('/api/v1/classrooms/'+room.json()['id'],headers=headers,json={**data,"radius_m":80}).status_code==200
    assert any(c['wifi'] for c in client.get('/api/v1/classrooms',headers=headers).json())
    assert client.put('/api/v1/policy',headers=headers,json={"wifi_unavailable":"review","reason":"Institution requires review without Wi-Fi"}).status_code==200
    assert db.scalar(select(SecurityEvent).where(SecurityEvent.kind=='POLICY_CHANGED'))


def test_session_lifecycle_and_faculty_scope(client, auth, world):
    headers=auth('faculty')
    created=client.post('/api/v1/sessions',headers=headers,json=session_payload(world))
    assert created.status_code==201,created.text
    session_id=created.json()['id']
    assert client.get('/api/v1/sessions/'+session_id,headers=auth('other_faculty')).status_code==403
    assert client.get('/api/v1/sessions/'+session_id,headers=auth('other_student')).status_code==403
    assert client.post('/api/v1/sessions/'+session_id+'/close',headers=headers).json()['closed'] is True


def test_session_invalid_window(client, auth, world):
    data=session_payload(world);data['ends_at']=data['starts_at']
    assert client.post('/api/v1/sessions',headers=auth('faculty'),json=data).status_code==422


def test_corrections_reason_scope_and_csv(client, auth, world, db):
    headers=auth('faculty');sid=client.post('/api/v1/sessions',headers=headers,json=session_payload(world)).json()['id']
    data={"student_id":world['student'].id,"session_id":sid,"status":"PRESENT","reason":"Checked identity and classroom presence in person"}
    assert client.post('/api/v1/corrections',headers=auth('student'),json=data).status_code==403
    assert client.post('/api/v1/corrections',headers=auth('other_faculty'),json=data).status_code==403
    assert client.post('/api/v1/corrections',headers=headers,json={**data,"reason":""}).status_code==422
    assert client.post('/api/v1/corrections',headers=headers,json=data).status_code==201
    assert client.post('/api/v1/corrections',headers=headers,json={**data,"status":"EXCUSED"}).status_code==201
    assert db.scalar(select(AttendanceRecord)).status=='EXCUSED'
    assert len(list(db.scalars(select(Correction))))==2
    report=client.get('/api/v1/reports/attendance.csv',headers=headers)
    assert report.status_code==200 and 'EXCUSED,CORRECTION' in report.text
    assert client.get('/api/v1/records',headers=auth('other_faculty')).json()==[]


def test_csv_formula_escape():
    from app.api.academic import csv_safe
    assert csv_safe('=HYPERLINK("x")').startswith("'")
    assert csv_safe('Student Name')=='Student Name'


def test_rate_limit_invalid_logins(client, world):
    statuses=[client.post('/api/v1/auth/login',json={"email":world['student'].email,"password":"wrong"}).status_code for _ in range(11)]
    assert statuses[-1]==429 and statuses[0]==401


def test_validation_does_not_echo_password(client):
    r=client.post('/api/v1/auth/login',json={"email":"invalid","password":"PRIVATE-SENTINEL"})
    assert r.status_code==422 and 'PRIVATE-SENTINEL' not in r.text


def test_chunked_body_limit(client):
    r=client.post('/api/v1/auth/login',content=iter([b'x'*8_000_000,b'x'*8_000_000]))
    assert r.status_code==413
