"""Protocol and PostgreSQL tests; synthetic signatures are not hardware attestation."""
import base64
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace as Obj
from uuid import uuid4
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import select
from app.models.entities import Device, Policy, SecurityChallenge, now
from app.schemas.contracts import Location
from app.services.device_keys import registration_message, verify_signature
from app.services.presence import evaluate
from app.services.app_attest import AttestError, cbor, verify_assertion
from conftest import PASSWORD
from test_verification_api import setup_flow, sign


def key_pair():
    key=ec.generate_private_key(ec.SECP256R1())
    public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
    return key,public


def signature(key,message):
    return base64.b64encode(key.sign(message.encode(),ec.ECDSA(hashes.SHA256()))).decode()


@pytest.mark.parametrize('platform',['android','ios'])
def test_native_registration_and_challenge_authentication(client,auth,platform,db):
    headers=auth('student');key,public=key_pair()
    challenge=client.post('/api/v1/devices/registration-challenge',headers=headers).json()
    body={'label':'Native test key','platform':platform,'password':PASSWORD,'public_key':public,
          'registration_challenge_id':challenge['id'],'registration_signature':signature(key,registration_message(challenge['nonce'],platform,public))}
    result=client.post('/api/v1/devices',headers=headers,json=body)
    assert result.status_code==201,result.text
    assert 'credential' not in result.json()
    assert result.json()['key_algorithm']=='ecdsa-p256-sha256'
    assert db.get(SecurityChallenge,challenge['id']).used
    replay=client.post('/api/v1/devices',headers=headers,json=body)
    assert replay.status_code==409


@pytest.mark.parametrize('mutation',['signature','platform','expired','foreign'])
def test_registration_proof_failures(client,auth,db,mutation):
    headers=auth('student');key,public=key_pair()
    challenge=client.post('/api/v1/devices/registration-challenge',headers=headers).json()
    body={'label':'Proof failure','platform':'ios','password':PASSWORD,'public_key':public,
          'registration_challenge_id':challenge['id'],'registration_signature':signature(key,registration_message(challenge['nonce'],'ios',public))}
    if mutation=='signature':body['registration_signature']=signature(key,'wrong message')
    if mutation=='platform':body['platform']='android'
    if mutation=='foreign':headers=auth('other_student')
    if mutation=='expired':db.get(SecurityChallenge,challenge['id']).expires_at=now()-timedelta(seconds=1);db.commit()
    response=client.post('/api/v1/devices',headers=headers,json=body)
    assert response.status_code in (403,409),response.text
    assert not list(db.scalars(select(Device)))


def test_new_registration_requires_native_key_by_default(client,auth,monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings(),'allow_legacy_device_registration',False)
    result=client.post('/api/v1/devices',headers=auth('student'),json={'label':'Legacy','platform':'ios','password':PASSWORD})
    assert result.status_code==422


@pytest.mark.parametrize('platform',['android','ios'])
def test_native_signed_attendance_api(client,setup_flow,db,platform):
    headers,_,device,_,_,body=setup_flow
    private,public=key_pair();row=db.get(Device,device['id']);row.key_algorithm='ecdsa-p256-sha256';row.public_key=public;row.platform=platform;db.commit()
    request=body(wifi_source='none');message=request['idempotency_key']+'.'+request['payload'];request['signature']=signature(private,message)
    response=client.post('/api/v1/attendance/verify',headers=headers,json=request)
    assert response.status_code==200,response.text
    assert response.json()['state']==('PRESENT' if platform=='android' else 'PENDING_REVIEW')
    assert response.json()['evidence_summary']['platform']==platform
    replay=client.post('/api/v1/attendance/verify',headers=headers,json=request)
    assert replay.json()['id']==response.json()['id']
    tamper={**request,'signature':signature(private,message+'tamper')}
    assert client.post('/api/v1/attendance/verify',headers=headers,json=tamper).status_code==403


@pytest.mark.parametrize('ios_policy,state',[('review','PENDING_REVIEW'),('retry','REQUIRES_RETRY'),('gps_only','PRESENT')])
def test_ios_policy_is_distinct_and_auditable(ios_policy,state):
    location=Location(latitude=12,longitude=77,accuracy_m=5,captured_at=now(),accuracy_authorization='full')
    policy=Obj(max_accuracy_m=35,max_location_age_s=20,wifi_unavailable='gps_only',ios_presence=ios_policy,require_attestation=False)
    room=Obj(latitude=12,longitude=77,radius_m=60)
    result=evaluate(location,[],'unsupported',room,[],policy,now(),platform='ios',wifi_source='none')
    assert result.state==state
    assert result.summary['presence_assurance']=='GPS_ONLY'


def test_ios_current_network_has_no_rssi_or_scan_equivalence():
    location=Location(latitude=12,longitude=77,accuracy_m=5,captured_at=now())
    policy=Obj(max_accuracy_m=35,max_location_age_s=20,wifi_unavailable='gps_only',ios_presence='review',require_attestation=False)
    result=evaluate(location,[],'available',Obj(latitude=12,longitude=77,radius_m=60),[Obj(bssid='aa:bb:cc:dd:ee:ff',min_rssi=-80)],policy,now(),platform='ios',wifi_source='current_network',current_bssid='aa:bb:cc:dd:ee:ff')
    assert result.state=='PENDING_REVIEW' and result.summary['current_network_match']
    assert result.summary['wifi_match']=='NOT_A_SCAN'
    assert 'wifi_match_ratio' not in result.summary


def test_reduced_accuracy_cannot_pass_even_with_small_reported_radius():
    location=Location(latitude=12,longitude=77,accuracy_m=1,captured_at=now(),accuracy_authorization='reduced')
    result=evaluate(location,[],'unavailable',Obj(latitude=12,longitude=77,radius_m=60),[],Obj(max_accuracy_m=35,max_location_age_s=20),now(),platform='ios')
    assert result.state=='REQUIRES_RETRY' and result.reasons==['PRECISE_LOCATION_REQUIRED']


def test_attestation_unconfigured_is_not_success(client,auth,setup_flow):
    headers,_,device,*_=setup_flow
    response=client.post('/api/v1/attestation/challenge',headers=headers,json={'device_id':device['id']})
    assert response.status_code==503
    assert client.get('/api/v1/attestation/capabilities',headers=headers).json()['apple_app_attest']=='not_configured'


def test_device_capabilities_are_admin_only(client,auth,setup_flow):
    headers,*_=setup_flow
    assert client.get('/api/v1/admin/devices',headers=headers).status_code==403
    response=client.get('/api/v1/admin/devices',headers=auth('admin'))
    assert response.status_code==200 and 'secret_encrypted' not in response.text and 'public_key' not in response.text


# Minimal test-only CBOR encoder, independent of the production decoder.
def encode(value):
    def head(major,size):
        if size<24:return bytes([major*32+size])
        if size<256:return bytes([major*32+24,size])
        return bytes([major*32+25])+size.to_bytes(2,'big')
    if isinstance(value,bytes):return head(2,len(value))+value
    if isinstance(value,str):return head(3,len(value.encode()))+value.encode()
    if isinstance(value,int):return head(0,value) if value>=0 else head(1,-1-value)
    if isinstance(value,list):return head(4,len(value))+b''.join(map(encode,value))
    if isinstance(value,dict):return head(5,len(value))+b''.join(encode(k)+encode(v) for k,v in value.items())
    raise TypeError(value)


@pytest.mark.parametrize('raw',[b'\x9f\xff',b'\xa2\x01\x02\x01\x03',b'\x01\x01',b'\x58\xff',b'\x81'*10+b'\x01'])
def test_cbor_rejects_ambiguous_or_unbounded_values(raw):
    with pytest.raises(ValueError):cbor(raw)


@pytest.mark.parametrize('counter,previous,valid',[(1,0,True),(1,1,False),(0,1,False),(2,1,True)])
def test_assertion_signature_and_monotonic_counter(counter,previous,valid):
    import hashlib
    private,public=key_pair();data=b'signed evidence bytes'
    settings=Obj(apple_app_id='TEAM.edu.spvs.student',apple_attest_environment='development',apple_attest_root_pem='unused',apple_attest_root_sha256='configured')
    auth=hashlib.sha256(settings.apple_app_id.encode()).digest()+b'\x00'+counter.to_bytes(4,'big')
    sig=private.sign(auth+hashlib.sha256(data).digest(),ec.ECDSA(hashes.SHA256()))
    token=base64.b64encode(encode({'authenticatorData':auth,'signature':sig})).decode()
    if valid:
        assert verify_assertion(token,data,base64.b64decode(public),previous,settings)==counter
        from cryptography.exceptions import InvalidSignature
        with pytest.raises(InvalidSignature):verify_assertion(token,b'tampered',base64.b64decode(public),previous,settings)
    else:
        with pytest.raises(AttestError,match='REPLAY'):verify_assertion(token,data,base64.b64decode(public),previous,settings)


def test_enrollment_exact_retry_recovers_lost_response(client,setup_flow,db,world):
    from app.models.entities import BiometricProfile
    headers,_,device,*_=setup_flow
    db.delete(db.get(BiometricProfile,world['student'].id));db.commit()
    challenge=client.post('/api/v1/challenges',headers=headers,json={'device_id':device['id'],'purpose':'enrollment'}).json()
    evidence={'challenge_id':challenge['id'],'device_id':device['id'],'frames':[{'jpeg':str(i)*120,'captured_at':now().isoformat()} for i in range(8)],'consent':True}
    request=sign(evidence,device['credential'])
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=request).status_code==201
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=request).json()['enrolled']
    assert client.post('/api/v1/biometrics/enroll',headers=headers,json=sign(evidence,device['credential'])).status_code==409


def test_future_frame_and_duplicate_frame_rejected_before_inference():
    from app.services.vision import Vision, VisionError
    from app.schemas.contracts import Frame
    vision=Vision.__new__(Vision)
    frames=[Frame(jpeg=str(i)*120,captured_at=now()+timedelta(seconds=20+i)) for i in range(8)]
    with pytest.raises(VisionError,match='FRAME_FROM_FUTURE'):vision.verify(frames,Obj())
    frames=[Frame(jpeg='a'*120,captured_at=now()-timedelta(seconds=8-i)) for i in range(8)]
    with pytest.raises(VisionError,match='DUPLICATE_FRAMES'):vision.verify(frames,Obj())


def test_required_attestation_gate_is_independent_of_ios_gps_only():
    location=Location(latitude=12,longitude=77,accuracy_m=5,captured_at=now())
    args=(location,[],'unavailable',Obj(latitude=12,longitude=77,radius_m=60),[],Obj(max_accuracy_m=35,max_location_age_s=20,wifi_unavailable='gps_only',ios_presence='gps_only',require_attestation=True),now())
    assert evaluate(*args,platform='ios',wifi_source='none').state=='PENDING_REVIEW'
    assert evaluate(*args,platform='ios',wifi_source='none',attestation_verified=True).state=='PRESENT'
