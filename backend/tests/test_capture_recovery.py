"""Synthetic geometry/protocol regressions; physical-camera usability is separate."""
from datetime import timedelta
from types import SimpleNamespace

import numpy as np
import pytest

from app.models.entities import now
from app.services import vision


def observations(poses):
    start = now() - timedelta(seconds=30)
    return start, [vision.Observation(start + timedelta(seconds=.3 * i), ear, yaw,
                                    np.ones(128)) for i, (ear, yaw) in enumerate(poses)]


@pytest.mark.parametrize("nose_x,action", [(65, "TURN_LEFT"), (35, "TURN_RIGHT")])
def test_unmirrored_camera_turn_is_named_from_the_persons_perspective(nose_x, action):
    # A person's left points to the viewer's right in an unmirrored image.
    points = np.zeros((468, 2))
    for ids, center in [([33, 160, 158, 133, 153, 144], 25),
                        ([362, 385, 387, 263, 373, 380], 75)]:
        points[ids] = [(center-5, 0), (center-3, -1.5), (center+3, -1.5),
                       (center+5, 0), (center+3, 1.5), (center-3, 1.5)]
    points[1] = (nose_x, 20)
    ear, yaw = vision.landmark_metrics(points)
    start, samples = observations([(.3, 0)] * 6 + [(ear, yaw)] * 2)
    vision.validate_sequence(samples, ["CENTER", action], start, start+timedelta(seconds=60))
    opposite = "TURN_RIGHT" if action == "TURN_LEFT" else "TURN_LEFT"
    with pytest.raises(vision.VisionError, match="SEQUENCE"):
        vision.validate_sequence(samples, ["CENTER", opposite], start, start+timedelta(seconds=60))


def sequence():
    return observations([(.3, 0)] * 5 + [(.3, -.3)] * 5 + [(.3, 0)] * 5
                        + [(.3, 0)] * 2 + [(.1, 0)] * 3 + [(.3, 0)] * 8)


ACTIONS = ["CENTER", "TURN_LEFT", "CENTER", "BLINK", "CENTER"]


def test_brief_landmark_loss_can_recover_without_losing_the_full_sequence():
    start, samples = sequence()
    for index in [4, 9]:
        samples[index].ear = samples[index].yaw = None
    vision.validate_sequence(samples, ACTIONS, start, start+timedelta(seconds=60))


def test_persistent_landmark_loss_still_rejects():
    start, samples = sequence()
    for index in [4, 9, 14]:
        samples[index].ear = samples[index].yaw = None
    with pytest.raises(vision.VisionError, match="LANDMARKS_UNAVAILABLE"):
        vision.validate_sequence(samples, ACTIONS, start, start+timedelta(seconds=60))


@pytest.mark.parametrize("poses", [
    [(.3, 0)] * 6 + [(.3, -.3), (None, None), (.3, -.3)],
    [(.3, 0)] * 6 + [(.1, 0), (None, None), (.3, 0)],
])
def test_tracking_gap_cannot_complete_a_pose_or_blink(poses):
    start, samples = observations(poses)
    action = "TURN_LEFT" if poses[6][1] else "BLINK"
    with pytest.raises(vision.VisionError, match="SEQUENCE"):
        vision.validate_sequence(samples, ["CENTER", action], start, start+timedelta(seconds=60))


def test_landmark_loss_does_not_skip_identity_comparison(monkeypatch):
    start, samples = sequence()
    samples[4].ear = samples[4].yaw = None
    samples[4].embedding = -np.ones(128)
    engine = vision.Vision.__new__(vision.Vision)
    iterator = iter(samples)
    monkeypatch.setattr(engine, "observe", lambda frame: next(iterator))
    frames = [SimpleNamespace(jpeg=f"frame-{i}", captured_at=o.timestamp)
              for i, o in enumerate(samples)]
    challenge = SimpleNamespace(actions=ACTIONS, created_at=start, expires_at=start+timedelta(seconds=60))
    with pytest.raises(vision.VisionError, match="FACE_MISMATCH"):
        engine.verify(frames, challenge)
