"""Real-model tests use only official public test imagery; no fabricated embedding outputs."""
import base64
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from app.core.config import settings
from app.models.entities import now
from app.services.vision import VisionError, get_vision, similarity


@pytest.fixture
def vision():
    if not all((settings().model_dir/name).is_file() for name in ['face_recognition_sface_2021dec.onnx','face_detection_yunet_2023mar.onnx','face_landmarker.task']):
        pytest.skip('Official face models unavailable; run scripts/download_models.py after network access is enabled')
    return get_vision()


def test_real_detector_rejects_blank_frame(vision):
    image=np.random.default_rng(7).integers(0,255,(480,640,3),dtype=np.uint8)
    _,jpg=cv2.imencode('.jpg',image)
    with pytest.raises(VisionError,match='EXACTLY_ONE_FACE_REQUIRED'):vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpg).decode(),captured_at=now()))


def test_real_recognizer_same_face(vision):
    sample=Path('../.runtime/astronaut.png')
    if not sample.exists():pytest.skip('Public NASA/scikit-image reference image not downloaded')
    image=cv2.imread(str(sample))
    _,jpg=cv2.imencode('.jpg',image)
    first=vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpg).decode(),captured_at=now()))
    adjusted=cv2.convertScaleAbs(image,alpha=.95,beta=3)
    _,jpg2=cv2.imencode('.jpg',adjusted)
    second=vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpg2).decode(),captured_at=now()))
    assert first.embedding.shape==(128,)
    assert np.linalg.norm(first.embedding)==pytest.approx(1,abs=1e-5)
    assert similarity(first.embedding,second.embedding)>settings().face_threshold
    assert np.isfinite(first.ear) and np.isfinite(first.yaw)


def test_real_model_distinguishes_public_reference_faces(vision):
    samples=[Path('../.runtime/astronaut.png'),Path('../.runtime/grace_hopper.jpg')]
    if not all(p.exists() for p in samples):pytest.skip('Run scripts/download_test_samples.py')
    observations=[]
    for path in samples:
        image=cv2.imread(str(path));_,jpg=cv2.imencode('.jpg',image)
        observations.append(vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpg).decode(),captured_at=now())))
    score=similarity(observations[0].embedding,observations[1].embedding)
    assert score < settings().face_threshold


def test_landmark_miss_preserves_real_face_identity(vision, monkeypatch):
    sample=Path('../.runtime/astronaut.png')
    if not sample.exists():pytest.skip('Public reference image not downloaded')
    image=cv2.imread(str(sample));_,jpg=cv2.imencode('.jpg',image)
    frame=SimpleNamespace(jpeg=base64.b64encode(jpg).decode(),captured_at=now())
    tracked=vision.observe(frame)
    # Only simulate tracking loss; detection and identity still use real models.
    monkeypatch.setattr(vision,'mesh',SimpleNamespace(detect=lambda image: SimpleNamespace(face_landmarks=[])))
    untracked=vision.observe(frame)
    assert untracked.ear is None and untracked.yaw is None
    assert similarity(tracked.embedding,untracked.embedding)>settings().face_threshold


def test_real_detector_rejects_multiple_faces(vision):
    path=Path('../.runtime/astronaut.png')
    if not path.exists():pytest.skip('Run scripts/download_test_samples.py')
    image=cv2.imread(str(path));joined=np.concatenate([image,image],axis=1);_,jpg=cv2.imencode('.jpg',joined)
    with pytest.raises(VisionError,match='EXACTLY_ONE_FACE_REQUIRED'):
        vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpg).decode(),captured_at=now()))


@pytest.mark.parametrize('level',[0,255])
def test_real_pipeline_rejects_poor_lighting(vision,level):
    image=np.full((480,640,3),level,dtype=np.uint8);_,jpeg=cv2.imencode('.jpg',image)
    with pytest.raises(VisionError,match='IMAGE_QUALITY_LOW'):
        vision.observe(SimpleNamespace(jpeg=base64.b64encode(jpeg).decode(),captured_at=now()))
