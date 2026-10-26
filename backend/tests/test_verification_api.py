"""API/transaction contract tests. Vision is explicitly replaced only in this test module.

Real model inference is independently exercised in test_vision_models.py. Passing these
tests does not establish real-camera liveness or face-recognition accuracy.
"""
import hashlib
import hmac
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import numpy as np
import pytest
from sqlalchemy import func, select

from app.core.security import cipher
from app.models.entities import AttendanceAttempt, AttendanceRecord, BiometricProfile, Challenge, Device, SecurityEvent, now
from app.services.vision import MODEL_VERSION, VisionError
from conftest import PASSWORD
from test_security_workflows import session_payload


@pytest.fixture
def setup_flow(client,auth,world,db,monkeypatch):
    class ContractOnlyVision:
        def verify(self,frames,challenge,template=None):
            return np.ones(128,dtype=np.float32)/np.sqrt(128),.9
    monkeypatch.setattr('app.api.verification.get_vision',lambda:ContractOnlyVision())
    student=auth('student');faculty=auth('faculty')
    registered=client.post('/api/v1/devices',headers=student,json={'label':'Test phone','platform':'android','password':PASSWORD})
    assert registered.status_code==201,registered.text
    device=registered.json()
    sid=client.post('/api/v1/sessions',headers=faculty,json=session_payload(world)).json()['id']
    db.add(BiometricProfile(student_id=world['student'].id,template_encrypted=cipher().encrypt((np.ones(128,dtype=np.float32)/np.sqrt(128)).tobytes()),model_version=MODEL_VERSION))
    db.commit()
    def issue():
        response=client.post('/api/v1/challenges',headers=student,json={'device_id':device['id'],'purpose':'attendance','session_id':sid})
        assert response.status_code==201,response.text
        return response.json()
    def body(challenge=None, presence=True, **overrides):
        c=challenge or issue()
        if presence:
            # Legacy regression fixtures supply completed factors; protocol endpoints
            # are exercised independently in test_dynamic_presence.py.
            from app.models.entities import AttendanceSession, PresenceQR, PresenceProof
            session=db.get(AttendanceSession,sid);session.presence_enabled=True
            if not db.get(PresenceProof,c['id']):
                qr=PresenceQR(session_id=sid,classroom_id=session.classroom_id,epoch=session.presence_epoch,
                    token=str(uuid4()),expires_at=now()+timedelta(seconds=10))
                db.add(qr);db.flush()
                db.add(PresenceProof(challenge_id=c['id'],student_id=world['student'].id,qr_id=qr.id,
                    audio_verified_at=now(),audio_consumed=True))
            db.commit()
        evidence={'challenge_id':c['id'],'device_id':device['id'],
          'frames':[{'jpeg':str(i)*120,'captured_at':now().isoformat()} for i in range(8)],
          'location':{'latitude':world['room'].latitude,'longitude':world['room'].longitude,'accuracy_m':5,'captured_at':now().isoformat()},
          'wifi_status':'unsupported','wifi':[],**overrides}
        return sign(evidence,device['credential'])
    return student,faculty,device,sid,issue,body


def sign(evidence,credential,key=None):
    payload=json.dumps(evidence,separators=(',',':'));key=key or str(uuid4())
    return {'payload':payload,'idempotency_key':key,'signature':hmac.new(credential.encode(),(key+'.'+payload).encode(),hashlib.sha256).hexdigest()}


def test_verification_transaction_and_idempotency(client,setup_flow,db):
    headers,_,_,_,_,body=setup_flow
    request=body();first=client.post('/api/v1/attendance/verify',headers=headers,json=request)
    assert first.status_code==200,first.text
    assert first.json()['state']=='PRESENT'
    repeated=client.post('/api/v1/attendance/verify',headers=headers,json=request)
    assert repeated.json()['id']==first.json()['id']
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==1
    assert db.scalar(select(func.count()).select_from(AttendanceAttempt))==1


def test_concurrent_retries_return_same_attempt(client,setup_flow,db):
    headers,_,_,_,_,body=setup_flow;request=body()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:client.post('/api/v1/attendance/verify',headers=headers,json=request),range(2)))
    assert [r.status_code for r in results]==[200,200]
    assert results[0].json()['id']==results[1].json()['id']
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==1


def test_replay_different_key_and_duplicate_record(client,setup_flow,db):
    headers,_,device,_,issue,body=setup_flow
    challenge=issue();request=body(challenge)
    assert client.post('/api/v1/attendance/verify',headers=headers,json=request).json()['state']=='PRESENT'
    assert client.post('/api/v1/attendance/verify',headers=headers,json=sign(json.loads(request['payload']),device['credential'])).status_code==409
    duplicate=client.post('/api/v1/attendance/verify',headers=headers,json=body()).json()
    assert duplicate['state']=='REJECTED' and 'ATTENDANCE_ALREADY_RECORDED' in duplicate['reasons']


def test_idempotency_key_cannot_change_payload(client,setup_flow):
    headers,_,device,_,_,body=setup_flow;request=body()
    assert client.post('/api/v1/attendance/verify',headers=headers,json=request).status_code==200
    changed=json.loads(request['payload']);changed['wifi_status']='unavailable'
    response=client.post('/api/v1/attendance/verify',headers=headers,json=sign(changed,device['credential'],request['idempotency_key']))
    assert response.status_code==409


def test_signature_mismatch_and_unknown_device(client,setup_flow):
    headers,_,_,_,_,body=setup_flow;request=body();request['signature']='0'*64
    assert client.post('/api/v1/attendance/verify',headers=headers,json=request).status_code==403
    assert client.post('/api/v1/attendance/verify',headers=headers,json=body(device_id=str(uuid4()))).status_code==403


def test_expired_challenge_recorded(client,setup_flow,db):
    headers,_,_,_,issue,body=setup_flow;c=issue();item=db.get(Challenge,c['id']);item.expires_at=now()-timedelta(seconds=1);db.commit()
    r=client.post('/api/v1/attendance/verify',headers=headers,json=body(c))
    assert r.json()['state']=='EXPIRED'
    db.refresh(item);assert item.used


def test_closed_session_expires_pending_challenge(client,setup_flow):
    headers,faculty,_,sid,issue,body=setup_flow;c=issue()
    assert client.post('/api/v1/sessions/'+sid+'/close',headers=faculty).status_code==200
    assert client.post('/api/v1/attendance/verify',headers=headers,json=body(c)).json()['state']=='EXPIRED'


def test_no_score_can_override_face_failure(client,setup_flow,monkeypatch,db):
    class Mismatch:
        def verify(self,*args):raise VisionError('FACE_MISMATCH')
    monkeypatch.setattr('app.api.verification.get_vision',lambda:Mismatch())
    headers,_,_,_,_,body=setup_flow
    for _ in range(3):
        r=client.post('/api/v1/attendance/verify',headers=headers,json=body())
        assert r.json()['state']=='REJECTED' and r.json()['reasons']==['FACE_MISMATCH']
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==0
    assert db.scalar(select(SecurityEvent).where(SecurityEvent.kind=='REPEATED_VERIFICATION_FAILURES'))


def test_missing_wifi_review_is_not_attendance(client,setup_flow,db):
    from app.models.entities import Policy
    headers,_,_,_,_,body=setup_flow;p=db.get(Policy,1);p.wifi_unavailable='review';db.commit()
    r=client.post('/api/v1/attendance/verify',headers=headers,json=body())
    assert r.json()['state']=='PENDING_REVIEW'
    assert db.scalar(select(func.count()).select_from(AttendanceRecord))==0


def test_device_reset_revokes_old_signature(client,setup_flow,auth):
    headers,_,_,_,_,body=setup_flow;request=body()
    reset=client.post('/api/v1/device-resets',headers=headers,json={'reason':'I replaced my old physical phone'}).json()
    approved=client.post('/api/v1/device-resets/'+reset['id']+'/approve',headers=auth('admin'),json={'reason':'Student identity checked at office'})
    assert approved.status_code==200
    assert client.post('/api/v1/attendance/verify',headers=headers,json=request).status_code==403


def test_one_active_device_and_no_credential_leak(client,setup_flow):
    headers,*_=setup_flow
    response=client.post('/api/v1/devices',headers=headers,json={'label':'Other phone','platform':'ios','password':PASSWORD})
    assert response.status_code==409
    listing=client.get('/api/v1/devices',headers=headers)
    assert 'secret_encrypted' not in listing.text and 'credential' not in listing.text


def test_malformed_evidence_cannot_supply_verdict(client,setup_flow):
    headers,_,_,_,_,body=setup_flow
    response=client.post('/api/v1/attendance/verify',headers=headers,json=body(liveness_passed=True))
    assert response.status_code==422


def test_dispute_and_resolution_scoped(client,setup_flow,auth):
    headers,faculty,_,_,_,body=setup_flow
    attempt=client.post('/api/v1/attendance/verify',headers=headers,json=body(location=None)).json()
    dispute=client.post('/api/v1/disputes',headers=headers,json={'attempt_id':attempt['id'],'reason':'Location permission was disabled accidentally'})
    assert dispute.status_code==201
    path='/api/v1/disputes/'+dispute.json()['id']+'/resolve'
    assert client.post(path,headers=auth('other_faculty'),json={'resolution':'Unauthorized resolution attempt'}).status_code==403
    assert client.post(path,headers=faculty,json={'resolution':'Student may retry with location permission enabled'}).json()['status']=='RESOLVED'


def test_biometric_enrollment_consent_and_deletion(client,setup_flow,db,world):
    headers,_,device,_,_,_=setup_flow
    profile=db.get(BiometricProfile,world['student'].id);db.delete(profile);db.commit()
    c=client.post('/api/v1/challenges',headers=headers,json={'device_id':device['id'],'purpose':'enrollment'}).json()
    evidence={'challenge_id':c['id'],'device_id':device['id'],'frames':[{'jpeg':str(i)*120,'captured_at':now().isoformat()} for i in range(8)],'consent':False}
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=sign(evidence,device['credential'])).status_code==422
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=sign({**evidence,'consent':True},device['credential'])).status_code==201
    assert client.get('/api/v1/biometrics',headers=headers).json()['enrolled'] is True
    assert client.request('DELETE','/api/v1/biometrics',headers=headers,json={'email':world['student'].email,'password':PASSWORD}).status_code==204
    assert client.get('/api/v1/biometrics',headers=headers).json()['enrolled'] is False


def test_enrollment_returns_missed_step_without_allowing_replay(client,setup_flow,db,world,monkeypatch):
    headers,_,device,_,_,_=setup_flow
    db.delete(db.get(BiometricProfile,world['student'].id));db.commit()
    c=client.post('/api/v1/challenges',headers=headers,json={'device_id':device['id'],'purpose':'enrollment'}).json()
    class FailedVision:
        def verify(self,frames,challenge):
            raise VisionError('LIVENESS_SEQUENCE_FAILED',diagnostics={
                'completed_actions':1,'expected_action':'TURN_LEFT','frame_count':8})
    monkeypatch.setattr('app.api.verification.get_vision',lambda:FailedVision())
    evidence={'challenge_id':c['id'],'device_id':device['id'],'frames':[
        {'jpeg':str(i)*120,'captured_at':now().isoformat()} for i in range(8)],'consent':True}
    request=sign(evidence,device['credential'])
    response=client.post('/api/v1/biometrics/enroll',headers=headers,json=request)
    assert response.status_code==422
    assert response.json()['error']=={'code':422,'message':'LIVENESS_SEQUENCE_FAILED',
        'details':{'completed_actions':1,'expected_action':'TURN_LEFT','frame_count':8}}
    assert client.get('/api/v1/biometrics',headers=headers).json()['enrolled'] is False
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=request).status_code==409
