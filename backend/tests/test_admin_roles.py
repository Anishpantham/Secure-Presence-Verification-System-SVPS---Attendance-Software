from sqlalchemy import select
from app.models.entities import SecurityEvent


def test_role_changes_require_admin_reason_and_apply_immediately(client,auth,world,db):
    admin=auth('admin');student=auth('student');target=world['student'].id
    assert client.patch('/api/v1/users/'+target,headers=admin,json={'role':'faculty'}).status_code==422
    result=client.patch('/api/v1/users/'+target,headers=admin,json={'role':'faculty','reason':'Appointment verified by the institution office'})
    assert result.status_code==200 and result.json()['role']=='faculty'
    assert client.get('/api/v1/devices',headers=student).status_code==403
    assert db.scalar(select(SecurityEvent).where(SecurityEvent.kind=='USER_ROLE_CHANGED'))


def test_cannot_change_own_admin_role(client,auth,world):
    result=client.patch('/api/v1/users/'+world['admin'].id,headers=auth('admin'),json={'role':'student','roll_number':'SELF','reason':'Attempted accidental loss of administrator access'})
    assert result.status_code==422
