"""OpenCV YuNet detection + SFace embeddings and MediaPipe temporal landmarks."""
import base64
import binascii
import threading
from dataclasses import dataclass
from functools import lru_cache

import cv2
import numpy as np

from app.core.config import settings

MODEL_VERSION = "opencv-sface-2021dec-128-yunet-2023mar"


class VisionError(ValueError):
    def __init__(self, message, *, diagnostics=None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


def normalize(vector):
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    if vector.shape != (128,) or not np.isfinite(vector).all() or np.linalg.norm(vector) < 1e-6:
        raise VisionError("INVALID_EMBEDDING")
    return vector / np.linalg.norm(vector)


def similarity(a, b):
    return float(np.clip(np.dot(normalize(a), normalize(b)), -1, 1))


@dataclass
class Observation:
    timestamp: object
    ear: float | None
    yaw: float | None
    embedding: np.ndarray


def landmark_metrics(points):
    def ear(ids):
        p = points[ids]
        return (np.linalg.norm(p[1]-p[5]) + np.linalg.norm(p[2]-p[4])) / (2 * np.linalg.norm(p[0]-p[3]))
    eye_ratio = (ear([33,160,158,133,153,144]) + ear([362,385,387,263,373,380])) / 2
    left, right = points[33], points[263]
    # Commands name the person's own left/right. In an unmirrored image their
    # left turn moves the nose toward image-right, so negate image displacement.
    yaw = ((left[0] + right[0]) / 2 - points[1][0]) / max(1, abs(right[0]-left[0]))
    if not np.isfinite(eye_ratio) or not np.isfinite(yaw):
        raise VisionError("LANDMARKS_INVALID")
    return float(eye_ratio), float(yaw)


def validate_sequence(observations, actions, issued_at, expires_at):
    if not 8 <= len(observations) <= 40:
        raise VisionError("LIVENESS_FRAME_COUNT")
    times = [o.timestamp for o in observations]
    if times[0] < issued_at or times[-1] > expires_at:
        raise VisionError("FRAME_OUTSIDE_CHALLENGE")
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
    if any(g < 0.08 or g > 2.5 for g in gaps) or (times[-1] - times[0]).total_seconds() < 2:
        raise VisionError("FRAME_TIMING_INVALID")
    missing = sum(o.ear is None or o.yaw is None for o in observations)
    if missing > 2 or len(observations) - missing < 8:
        raise VisionError("LANDMARKS_UNAVAILABLE", diagnostics={
            "missing_landmark_frames": missing, "frame_count": len(observations),
        })
    index, stable, blink_open, blink_closed = 0, 0, False, False
    for obs in observations:
        if obs.ear is None or obs.yaw is None:
            # A tracking gap cannot prove a pose or connect an incomplete blink.
            # All frames still undergo face detection and identity comparison.
            stable, blink_open, blink_closed = 0, False, False
            continue
        action = actions[index]
        if action == "BLINK":
            if obs.ear > 0.23:
                if blink_closed:
                    index += 1
                    stable = 0
                else:
                    blink_open = True
            elif obs.ear < 0.19 and blink_open:
                blink_closed = True
        else:
            matches = (abs(obs.yaw) < 0.12 if action == "CENTER" else
                       obs.yaw < -0.18 if action == "TURN_LEFT" else obs.yaw > 0.18)
            stable = stable + 1 if matches else 0
            if stable >= 2:
                index += 1
                stable = 0
        if index == len(actions):
            return
    # Retain only stage progress for troubleshooting, never frames or landmarks.
    raise VisionError("LIVENESS_SEQUENCE_FAILED", diagnostics={
        "completed_actions": index, "expected_action": actions[index],
        "frame_count": len(observations),
    })


class Vision:
    def __init__(self):
        import mediapipe as mp
        root = settings().model_dir
        detector_path = root / "face_detection_yunet_2023mar.onnx"
        recognizer_path = root / "face_recognition_sface_2021dec.onnx"
        landmark_path = root / "face_landmarker.task"
        if not detector_path.is_file() or not recognizer_path.is_file() or not landmark_path.is_file():
            raise RuntimeError("Face models missing; run scripts/download_models.py")
        self.detector = cv2.FaceDetectorYN.create(str(detector_path), "", (640, 480), 0.85)
        self.recognizer = cv2.FaceRecognizerSF.create(str(recognizer_path), "")
        self.mp = mp
        self.mesh = mp.tasks.vision.FaceLandmarker.create_from_options(
            mp.tasks.vision.FaceLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(landmark_path)),
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_faces=2, min_face_detection_confidence=0.6,
                min_face_presence_confidence=0.6))
        self.lock = threading.Lock()

    def observe(self, frame):
        try:
            encoded = base64.b64decode(frame.jpeg, validate=True)
        except (ValueError, binascii.Error):
            raise VisionError("INVALID_IMAGE_ENCODING")
        # Check dimensions before decoding to bound decompression memory.
        from PIL import Image
        import io
        try:
            with Image.open(io.BytesIO(encoded)) as header:
                if header.format != "JPEG" or min(header.size) < 160 or max(header.size) > 1280:
                    raise VisionError("IMAGE_SIZE_OR_FORMAT")
        except (OSError, Image.DecompressionBombError):
            raise VisionError("INVALID_IMAGE")
        image = cv2.imdecode(np.frombuffer(encoded, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise VisionError("INVALID_IMAGE")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if gray.mean() < 30 or gray.mean() > 235 or cv2.Laplacian(gray, cv2.CV_64F).var() < 30:
            raise VisionError("IMAGE_QUALITY_LOW")
        with self.lock:
            self.detector.setInputSize((image.shape[1], image.shape[0]))
            _, faces = self.detector.detect(image)
            if faces is None or len(faces) != 1:
                raise VisionError("EXACTLY_ONE_FACE_REQUIRED")
            if min(faces[0][2:4]) < 70:
                raise VisionError("FACE_TOO_SMALL")
            aligned = self.recognizer.alignCrop(image, faces[0])
            embedding = normalize(self.recognizer.feature(aligned))
            result = self.mesh.detect(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,
                                                    data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        if not result.face_landmarks:
            return Observation(frame.captured_at, None, None, embedding)
        if len(result.face_landmarks) != 1:
            raise VisionError("EXACTLY_ONE_FACE_REQUIRED")
        points = np.array([(p.x * image.shape[1], p.y * image.shape[0]) for p in result.face_landmarks[0]])
        eye_ratio, yaw = landmark_metrics(points)
        return Observation(frame.captured_at, eye_ratio, yaw, embedding)

    def verify(self, frames, challenge, template=None):
        from app.models.entities import now
        if (frames[-1].captured_at - now()).total_seconds() > 2:
            raise VisionError("FRAME_FROM_FUTURE")
        if len({__import__("hashlib").sha256(f.jpeg.encode()).hexdigest() for f in frames}) != len(frames):
            raise VisionError("DUPLICATE_FRAMES")
        observations = []
        for index, frame in enumerate(frames):
            try:
                observations.append(self.observe(frame))
            except VisionError as exc:
                exc.diagnostics.update(frame_index=index, frame_count=len(frames))
                raise
        validate_sequence(observations, challenge.actions, challenge.created_at, challenge.expires_at)
        reference = template if template is not None else observations[0].embedding
        scores = [similarity(reference, o.embedding) for o in observations]
        if min(scores) < settings().face_threshold:
            raise VisionError("FACE_MISMATCH")
        return normalize(np.mean([o.embedding for o in observations], axis=0)), min(scores)


@lru_cache
def get_vision():
    return Vision()
