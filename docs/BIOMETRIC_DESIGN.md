# Biometric design

## Model provenance and separation of responsibilities

YuNet detects a face and five alignment landmarks. It does not establish identity. SFace generates a 128-dimensional learned face representation, using OpenCV's `FaceRecognizerSF.alignCrop` and `feature` APIs. MediaPipe Face Mesh separately supplies dense facial landmarks for temporal liveness. ONNX models are executed by OpenCV DNN on CPU; ONNX Runtime is unnecessary for this pipeline.

| Asset | Provenance | License |
|---|---|---|
| `face_detection_yunet_2023mar.onnx` | OpenCV Zoo, commit `48b10fa505aeb51fbd127fc60a5c660040e823b7` | MIT; Shiqi Yu notice retained |
| `face_recognition_sface_2021dec.onnx` | Same official repository/commit | Apache 2.0; full license retained |
| `face_landmarker.task` float16 v1 | Official Google MediaPipe model storage; consumed by MediaPipe 1.1.1 Tasks | MediaPipe code is Apache 2.0; consult the linked official model card/provider terms for the pretrained asset |

Expected SHA-256 values are in `scripts/download_models.py`, copied from the official Git LFS pointer objects. A mismatch stops installation. The SFace asset is 38,696,353 bytes and YuNet is 232,589 bytes. No model is trained in this project.

The landmark task is downloaded over verified HTTPS from the versioned official Google URL. Its SHA-256 is pinned as `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`; it is loaded in IMAGE mode with at most two faces. The current MediaPipe Tasks API avoids the legacy package's protobuf dependency.

## Enrollment and comparison

Enrollment requires an authenticated student, an authorized device, explicit consent, a fresh enrollment-purpose challenge and a server-validated sequence. JSON cannot carry a trusted embedding or similarity score. JPEG input is base64-decoded, limited to dimensions 160–1280, checked for brightness and Laplacian sharpness, and must contain exactly one usable YuNet face of at least 70 pixels. The aligned BGR crop passes through OpenCV's SFace preprocessing. Returned vectors must contain exactly 128 finite values and have nonzero norm. They are L2-normalized.

Every verification frame is embedded and compared against the encrypted enrolled template. Enrollment frames must match the first frame so that a sequence cannot trivially switch people. The minimum similarity across frames must meet `FACE_THRESHOLD`, default **0.5**. OpenCV's tutorial gives a cosine baseline of approximately 0.363 for its example evaluation; 0.5 here is a stricter initial operating point, not a locally calibrated false-acceptance guarantee. A realistic institution must collect consented evaluation data and measure FAR/FRR across lighting, pose and user groups before choosing a threshold.

The enrollment template is the normalized mean of sequence embeddings and is encrypted with Fernet under a separate `BIOMETRIC_KEY`. Templates carry an explicit model version. Raw frame bytes and unencrypted embeddings are not persisted. Student deletion requires password confirmation. Backup retention can still retain deleted ciphertext; operators must apply their retention policy to backups as well.

## Liveness protocol

The server issues an unpredictable UUID challenge bound to a student, device, purpose and attendance session (when applicable). It selects a left/right turn and randomizes the turn/blink ordering, inserting center poses. A challenge normally expires after 60 seconds and is consumed once. Session attempts and challenge issuance are rate limited.

Face Mesh computes eye aspect ratio (EAR) from six landmarks per eye, averaged across both eyes. A blink must transition open (`EAR > 0.23`) → closed (`EAR < 0.19`) → open. Head direction is a signed nose displacement relative to eye centers, normalized by interocular distance. Center is absolute displacement below 0.12; turns exceed 0.18 in the requested direction. Two consecutive observations must support each non-blink pose. This is a heuristic displacement proxy rather than a calibrated three-dimensional head-pose estimator.

A sequence contains 8–40 frames, has increasing timestamps separated by 0.08–2.5 seconds, spans at least two seconds, remains inside the challenge time window, and may not claim a final capture more than two seconds in the future. Identical encoded frames are rejected. Mobile captures unmirrored camera images and synchronizes capture timestamps to the challenge's server clock. Direction conventions, timing and EAR thresholds require physical-camera validation; basic frame rates can miss a fast blink, so the UI asks for a slow close/open action.

## Limits and measured evidence

Landmark liveness rejects a static frame and some naive replay attempts. It does not prove camera provenance and can be defeated by sophisticated replay, virtual-camera injection, deepfakes or a compromised client. Randomized action order and signatures increase the effort but are not certified presentation-attack detection. Client timestamps are assertions checked for consistency, not trusted hardware timestamps.

Real model tests use the public NASA astronaut image from scikit-image and Grace Hopper image from matplotlib: same-face photometric variation, different-person comparison, zero faces and multiple faces. These smoke tests validate model operation; four tests on two portraits are not a biometric accuracy study. No live student was enrolled during automated evaluation.
