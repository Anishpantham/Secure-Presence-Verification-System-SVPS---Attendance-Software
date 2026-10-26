"""Real PostgreSQL protocol transactions; face inference remains the established test double."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from uuid import uuid4
import pytest
from sqlalchemy import select, func
from app.models.entities import (AttendanceRecord, AttendanceAttempt, AttendanceSession, Challenge,
    PresenceProof, PresenceQR, Policy, Device, SecurityEvent, now)
from app.api import classroom_presence as protocol
from test_verification_api import setup_flow, sign


@pytest.fixture
def flow(client, setup_flow):
    student, faculty, device, sid, issue, body = setup_flow
    assert client.post(f'/api/v1/sessions/{sid}/presence/control',headers=faculty,json={'enabled':True}).status_code==200
    c=issue()
    def display():
        return client.get(f'/api/v1/sessions/{sid}/presence/display',headers=faculty).json()
    def message(action, **extra):
        return sign({'challenge_id':c['id'],'device_id':device['id'],'action':action,**extra},device['credential'])
    def send(action, **extra):
        return client.post('/api/v1/presence/evidence',headers=student,json=message(action,**extra))
    def play():
        return client.post(f"/api/v1/sessions/{sid}/presence/play/{c['id']}",headers=faculty)
    def prepare():
        assert send('qr',token=display()['token']).status_code==200
        assert send('ready').status_code==200
        result=play();assert result.status_code==200,result.text
        return result.json()['payload']
    return student,faculty,device,sid,c,body,display,message,send,play,prepare


def test_rotation_and_exact_expiry(client,flow,db,monkeypatch):
    _,_,_,sid,c,_,display,_,send,*_=flow
    start=datetime.fromtimestamp(int(now().timestamp())//5*5,timezone.utc);monkeypatch.setattr(protocol,'now',lambda:start)
    first=display();token=first['token']
    monkeypatch.setattr(protocol,'now',lambda:start+timedelta(seconds=4.999))
    assert display()['token']==token
    monkeypatch.setattr(protocol,'now',lambda:start+timedelta(seconds=5))
    assert display()['token']!=token
    monkeypatch.setattr(protocol,'now',lambda:start+timedelta(seconds=10))
    assert send('qr',token=token).status_code==409
    assert db.get(PresenceProof,c['id']) is None


def test_forgery_cross_session_and_access(client,flow,auth,db):
    student,faculty,_,sid,c,_,display,_,send,*_=flow
    token=display()['token']
    assert send('qr',token=token[:-1]+('a' if token[-1]!='a' else 'b')).status_code==409
    original=db.get(AttendanceSession,sid)
    foreign=AttendanceSession(course_id=original.course_id,classroom_id=original.classroom_id,starts_at=original.starts_at,ends_at=original.ends_at)
    db.add(foreign);db.flush();db.get(Challenge,c['id']).session_id=foreign.id;db.commit()
    assert send('qr',token=token).status_code==409
    assert client.get(f'/api/v1/sessions/{sid}/presence/display',headers=student).status_code==403
    assert client.get(f'/api/v1/sessions/{sid}/presence/display',headers=auth('other_faculty')).status_code==403


def test_concurrent_qr_idempotent_but_no_second_attempt_reuse(client,flow,db):
    student,_,device,_,c,_,display,message,send,*_=flow
    token=display()['token'];request=message('qr',token=token)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:client.post('/api/v1/presence/evidence',headers=student,json=request),range(2)))
    assert [r.status_code for r in results]==[200,200]
    assert db.scalar(select(func.count()).select_from(PresenceProof))==1
    original=db.get(Challenge,c['id']);original.used=True
    other=Challenge(student_id=original.student_id,device_id=original.device_id,session_id=original.session_id,purpose='attendance',actions=original.actions,expires_at=original.expires_at)
    db.add(other);db.commit()
    request=sign({'action':'qr','device_id':device['id'],'challenge_id':other.id,'token':token},device['credential'])
    assert client.post('/api/v1/presence/evidence',headers=student,json=request).status_code==409


@pytest.mark.parametrize('platform',['android','ios'])
def test_full_flow_required_on_both_platforms(client,flow,db,platform):
    student,_,device,_,c,body,_,_,send,_,prepare=flow
    db.get(Device,device['id']).platform=platform;db.get(Policy,1).ios_presence='dynamic';db.commit()
    answer=prepare();assert send('audio',response=answer).status_code==200
    request=body(c,presence=False,wifi_source='none')
    result=client.post('/api/v1/attendance/verify',headers=student,json=request)
    assert result.json()['state']=='PRESENT',result.text
    assert client.post('/api/v1/attendance/verify',headers=student,json=request).json()['id']==result.json()['id']
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==1


@pytest.mark.parametrize('problem',['missing','wrong','expired'])
def test_audio_cannot_be_faked_or_reused(client,flow,db,monkeypatch,problem):
    student,_,_,_,c,body,_,_,send,_,prepare=flow
    answer=prepare()
    if problem=='expired':
        proof=db.get(PresenceProof,c['id']);monkeypatch.setattr(protocol,'now',lambda:proof.audio_expires_at)
    if problem!='missing':
        assert send('audio',response='0'*24 if problem=='wrong' else answer).status_code==409
        assert send('audio',response=answer).status_code==409
    result=client.post('/api/v1/attendance/verify',headers=student,json=body(c,presence=False))
    assert result.json()['state']!='PRESENT'
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==0


def test_audio_exact_retry_recovers_lost_ack_concurrently(client,flow):
    student,_,_,_,_,_,_,message,_,_,prepare=flow
    request=message('audio',response=prepare())
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:client.post('/api/v1/presence/evidence',headers=student,json=request),range(2)))
    assert [r.status_code for r in results]==[200,200]


@pytest.mark.parametrize('failure',['gps','liveness','signature','closed','stopped','restarted'])
def test_valid_factors_never_override_other_gates(client,flow,db,monkeypatch,failure):
    student,faculty,_,sid,c,body,_,_,send,_,prepare=flow
    assert send('audio',response=prepare()).status_code==200
    if failure=='liveness':
        from app.services.vision import VisionError
        class FailedVision:
            def verify(self,*args):raise VisionError('LIVENESS_SEQUENCE_FAILED')
        monkeypatch.setattr('app.api.verification.get_vision',lambda:FailedVision())
    if failure=='closed':client.post(f'/api/v1/sessions/{sid}/close',headers=faculty)
    if failure in ('stopped','restarted'):
        client.post(f'/api/v1/sessions/{sid}/presence/control',headers=faculty,json={'enabled':False})
        if failure=='restarted':client.post(f'/api/v1/sessions/{sid}/presence/control',headers=faculty,json={'enabled':True})
    request=body(c,presence=False,**({'location':None} if failure=='gps' else {}))
    if failure=='signature':request['signature']='0'*64
    result=client.post('/api/v1/attendance/verify',headers=student,json=request)
    assert result.status_code==403 if failure=='signature' else result.json()['state']!='PRESENT'
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==0


@pytest.mark.parametrize('reason',['CAMERA_PERMISSION','MICROPHONE_PERMISSION','INTERRUPTED','NETWORK_INTERRUPTED','AUDIO_DECODE_FAILED'])
def test_incomplete_factor_has_auditable_review_path(client,flow,db,reason):
    student,faculty,_,sid,c,_,_,_,send,*_=flow
    result=send('failure',reason=reason);assert result.status_code==200,result.text
    attempt=result.json();assert attempt['state']=='PENDING_REVIEW'
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==0
    dispute=client.post('/api/v1/disputes',headers=student,json={'attempt_id':attempt['id'],'reason':'Please review my incomplete presence capture'})
    assert dispute.status_code==201
    assert db.scalar(select(SecurityEvent).where(SecurityEvent.kind=='PRESENCE_INCOMPLETE'))


def test_missing_factors_old_client_fails_closed(client,flow):
    student,_,_,_,c,body,*_=flow
    result=client.post('/api/v1/attendance/verify',headers=student,json=body(c,presence=False))
    assert result.json()['state']=='PENDING_REVIEW' and 'QR_REQUIRED' in result.json()['reasons']


def test_arbitrary_audio_passed_flag_rejected(client,flow):
    student,_,_,_,_,_,_,message,*_=flow
    request=message('audio',audio_passed=True)
    assert client.post('/api/v1/presence/evidence',headers=student,json=request).status_code==422


def test_qr_accepts_just_before_ten_second_boundary(flow,db,monkeypatch):
    *_,display,message,send,play,prepare=flow
    token=display()['token'];qr=db.scalar(select(PresenceQR).where(PresenceQR.token==token))
    monkeypatch.setattr(protocol,'now',lambda:qr.expires_at-timedelta(microseconds=1))
    assert send('qr',token=token).status_code==200


def test_native_signature_on_presence_and_tampering(client,flow,db):
    from test_cross_platform import key_pair,signature
    student,_,device,_,_,_,display,message,*_=flow
    token=display()['token'];private,public=key_pair();row=db.get(Device,device['id'])
    row.key_algorithm='ecdsa-p256-sha256';row.public_key=public;db.commit()
    request=message('qr',token=token);request['signature']=signature(private,request['idempotency_key']+'.'+request['payload'])
    tampered={**request,'idempotency_key':str(uuid4())}
    assert client.post('/api/v1/presence/evidence',headers=student,json=tampered).status_code==403
    assert client.post('/api/v1/presence/evidence',headers=student,json=request).status_code==200


def test_attempt_issuance_is_idempotent_and_budget_includes_abandonment(client,flow,db):
    student,_,device,sid,c,*_=flow
    request={'device_id':device['id'],'session_id':sid,'purpose':'attendance'}
    assert client.post('/api/v1/challenges',headers=student,json=request).json()['id']==c['id']
    db.get(Policy,1).max_attempts=1;db.get(Challenge,c['id']).expires_at=now()-timedelta(seconds=1);db.commit()
    assert client.post('/api/v1/challenges',headers=student,json=request).status_code==429


def test_expiry_during_face_inference_cannot_create_record(client,flow,monkeypatch):
    import numpy as np
    student,_,_,_,c,body,_,_,send,_,prepare=flow
    assert send('audio',response=prepare()).status_code==200
    class SlowVision:
        def verify(self,*args):
            monkeypatch.setattr('app.api.verification.now',lambda:now()+timedelta(minutes=10))
            return np.ones(128,dtype=np.float32),.9
    monkeypatch.setattr('app.api.verification.get_vision',lambda:SlowVision())
    result=client.post('/api/v1/attendance/verify',headers=student,json=body(c,presence=False))
    assert result.json()['state']=='EXPIRED'
