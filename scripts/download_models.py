"""Download official OpenCV Zoo assets and verify Git LFS SHA-256 object IDs."""
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / "models"
COMMIT = "48b10fa505aeb51fbd127fc60a5c660040e823b7"
MODELS = {
    "face_detection_yunet_2023mar.onnx": ("face_detection_yunet", "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"),
    "face_recognition_sface_2021dec.onnx": ("face_recognition_sface", "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"),
}
LANDMARK_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
LANDMARK_SHA256 = "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"


def main():
    ROOT.mkdir(exist_ok=True)
    assets = [(name, f"https://media.githubusercontent.com/media/opencv/opencv_zoo/{COMMIT}/models/{directory}/{name}", expected)
              for name, (directory, expected) in MODELS.items()]
    assets.append(("face_landmarker.task", LANDMARK_URL, LANDMARK_SHA256))
    for name, url, expected in assets:
        path = ROOT / name
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == expected:
            print(f"Verified {name}")
            continue
        temporary = path.with_suffix(".download")
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
            temporary.unlink()
            raise RuntimeError(f"Checksum mismatch: {name}")
        temporary.replace(path)
        print(f"Downloaded and verified {name}")


if __name__ == "__main__":
    main()
