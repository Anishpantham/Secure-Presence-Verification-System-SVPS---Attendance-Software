from datetime import timedelta
from types import SimpleNamespace as Obj

import numpy as np
import pytest
from pydantic import ValidationError

from app.models.entities import now
from app.schemas.contracts import Location, WifiObservation
from app.services.presence import evaluate, haversine
from app.services.vision import Observation, VisionError, normalize, similarity, validate_sequence


def context(**location_overrides):
    current=now()
    location=Location(latitude=12.9716,longitude=77.5946,accuracy_m=5,captured_at=current)
    location=location.model_copy(update=location_overrides)
    room=Obj(latitude=12.9716,longitude=77.5946,radius_m=60)
    policy=Obj(max_accuracy_m=35,max_location_age_s=20,wifi_unavailable='gps_only',require_attestation=False)
    return location,room,policy,current


def decide(location_changes=None,policy_changes=None,wifi=None,refs=None,status='unavailable',previous=None):
    location,room,policy,current=context(**(location_changes or {}))
    for k,v in (policy_changes or {}).items():setattr(policy,k,v)
    return evaluate(location,wifi or [],status,room,refs or [],policy,current,previous)


def test_haversine_known_distance():
    assert haversine(0,0,0,1)==pytest.approx(111194.9,rel=1e-5)
    assert haversine(12,77,12,77)==0


@pytest.mark.parametrize('changes,state,reason',[
    ({},'PRESENT','ALL_REQUIRED_CHECKS_PASSED'),
    ({'accuracy_m':100},'REQUIRES_RETRY','LOCATION_INACCURATE'),
    ({'captured_at':now()-timedelta(minutes=2)},'REQUIRES_RETRY','LOCATION_STALE'),
    ({'captured_at':now()+timedelta(minutes=2)},'REQUIRES_RETRY','LOCATION_STALE'),
    ({'mocked':True},'REJECTED','MOCK_LOCATION_REPORTED'),
    ({'latitude':13.1},'REJECTED','OUTSIDE_GEOFENCE'),
    ({'latitude':12.9721,'accuracy_m':20},'PENDING_REVIEW','GEOFENCE_BOUNDARY_UNCERTAIN'),
])
def test_gps_rules(changes,state,reason):
    result=decide(changes)
    assert result.state==state and reason in result.reasons


@pytest.mark.parametrize('fallback,state',[('review','PENDING_REVIEW'),('reject','REJECTED'),('gps_only','PRESENT')])
def test_wifi_unavailable_policy(fallback,state):
    assert decide(policy_changes={'wifi_unavailable':fallback}).state==state


@pytest.mark.parametrize('rssi,state',[(-60,'PRESENT'),(-95,'PENDING_REVIEW')])
def test_wifi_fingerprint_strength(rssi,state):
    refs=[Obj(bssid='aa:bb:cc:dd:ee:ff',min_rssi=-80)]
    observations=[WifiObservation(bssid='aa:bb:cc:dd:ee:ff',rssi=rssi)]
    assert decide(wifi=observations,refs=refs,status='available').state==state


def test_attestation_is_fail_closed():
    from app.services.attestation import verify_integrity
    assert not verify_integrity('client-says-true','nonce','android').verified
    result=decide(policy_changes={'require_attestation':True})
    assert result.state=='PENDING_REVIEW' and 'ATTESTATION_NOT_CONFIGURED' in result.reasons


def test_impossible_travel_is_explainable():
    result=decide(previous={'latitude':50,'longitude':10,'time':now()-timedelta(seconds=10)})
    assert result.state=='PENDING_REVIEW' and 'IMPLAUSIBLE_TRAVEL' in result.reasons


def test_wifi_cannot_override_failed_gps():
    result=decide({'mocked':True},wifi=[WifiObservation(bssid='aa:bb:cc:dd:ee:ff',rssi=-40)],refs=[Obj(bssid='aa:bb:cc:dd:ee:ff',min_rssi=-80)],status='available')
    assert result.state=='REJECTED'


@pytest.mark.parametrize('vector',[np.zeros(128),np.ones(64),np.full(128,np.nan),np.full(128,np.inf)])
def test_invalid_embeddings(vector):
    with pytest.raises(VisionError):normalize(vector)


def test_cosine_normalizes_actual_embedding_shape():
    assert similarity(np.ones(128),np.ones(128)*100)==pytest.approx(1,abs=1e-6)
    assert similarity(np.ones(128),-np.ones(128))==pytest.approx(-1,abs=1e-6)


def sequence():
    start=now()-timedelta(seconds=10)
    # Synthetic landmark observations are unit-test inputs, not image/model validation.
    poses=[(.3,0),(.3,0),(.3,-.3),(.3,-.3),(.3,0),(.3,0),(.3,0),(.1,0),(.3,0),(.3,0),(.3,0)]
    return start,[Observation(start+timedelta(seconds=.3*i),ear,yaw,np.ones(128)) for i,(ear,yaw) in enumerate(poses)]


def test_temporal_liveness_sequence():
    start,observations=sequence()
    validate_sequence(observations,['CENTER','TURN_LEFT','CENTER','BLINK','CENTER'],start,start+timedelta(seconds=60))


def test_wrong_liveness_action_rejected():
    start,observations=sequence()
    with pytest.raises(VisionError,match='SEQUENCE'):validate_sequence(observations,['CENTER','TURN_RIGHT','CENTER','BLINK','CENTER'],start,start+timedelta(seconds=60))


def test_liveness_requires_open_closed_open():
    start,observations=sequence()
    for o in observations:o.ear=.3
    with pytest.raises(VisionError,match='SEQUENCE'):validate_sequence(observations,['CENTER','TURN_LEFT','CENTER','BLINK','CENTER'],start,start+timedelta(seconds=60))


def test_liveness_expiry_and_order():
    start,observations=sequence()
    with pytest.raises(VisionError,match='OUTSIDE'):validate_sequence(observations,['CENTER'],start,start+timedelta(seconds=1))
    observations[2].timestamp=observations[1].timestamp
    with pytest.raises(VisionError,match='TIMING'):validate_sequence(observations,['CENTER'],start,start+timedelta(seconds=60))


def test_nan_location_rejected():
    with pytest.raises(ValidationError):Location(latitude=float('nan'),longitude=0,accuracy_m=5,captured_at=now())
