# References and provenance

The following are implementation references, not claims of deployment or experimentally measured accuracy. Consult the linked versioned source and official documentation when reproducing the project.

1. FastAPI documentation: https://fastapi.tiangolo.com/ — dependency injection, validation, security and API documentation.
2. SQLAlchemy 2.0 documentation: https://docs.sqlalchemy.org/en/20/ — ORM mappings, sessions and transactions.
3. PostgreSQL 16 documentation: https://www.postgresql.org/docs/16/ — constraints, indexes and row-level locking.
4. Alembic documentation: https://alembic.sqlalchemy.org/ — migration generation and application.
5. OpenCV Zoo, pinned commit: https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7 — official YuNet/SFace assets, Git LFS object hashes and licenses.
6. OpenCV DNN face tutorial: https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html — detection, aligned SFace features and matching metrics. Its example threshold is not a local SPVS calibration result.
7. MediaPipe Face Landmarker guide: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker — Tasks API and official model bundle.
8. MediaPipe source/license: https://github.com/google-ai-edge/mediapipe — Apache 2.0 code and model-related resources.
9. Argon2-cffi documentation: https://argon2-cffi.readthedocs.io/ — maintained password hashing interface.
10. Cryptography Fernet documentation: https://cryptography.io/en/latest/fernet/ — authenticated symmetric encryption and key handling.
11. Expo documentation: https://docs.expo.dev/ — development builds, Camera, Location, SecureStore and local modules.
12. Android Wi-Fi scanning overview: https://developer.android.com/develop/connectivity/wifi/wifi-scan — scan restrictions, permissions and throttling.
13. Android Play Integrity overview: https://developer.android.com/google/play/integrity/overview — external provider integration requirements.
14. Apple App Attest: https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity — attestation boundary not configured in this distribution.
15. React, Vite and TanStack Query: https://react.dev/ ; https://vite.dev/ ; https://tanstack.com/query/latest — client architecture.
16. Playwright and pytest: https://playwright.dev/ ; https://docs.pytest.org/ — browser and backend testing.
17. scikit-image astronaut sample, version 0.24.0: https://github.com/scikit-image/scikit-image/blob/v0.24.0/skimage/data/astronaut.png — public NASA astronaut portrait used for model smoke tests.
18. matplotlib Grace Hopper sample, version 3.9.2: https://github.com/matplotlib/matplotlib/blob/v3.9.2/lib/matplotlib/mpl-data/sample_data/grace_hopper.jpg — public reference portrait used for a different-person smoke test.
19. npm advisory GHSA-vfj7-8cjw-p6xm: https://github.com/advisories/GHSA-vfj7-8cjw-p6xm — unresolved `braces` issue recorded by audit.
20. npm advisory GHSA-86w9-cpqp-85rv: https://github.com/advisories/GHSA-86w9-cpqp-85rv — unresolved `node-forge` issue recorded by audit.

License texts for the downloaded face detector and recognizer are included in `LICENSE-YUNET.txt` and `LICENSE-SFACE.txt`. The project source inherits the repository's MIT license. Third-party dependency licenses remain their respective authors' licenses. Reference portraits are downloaded only for local tests and are excluded from submission archives.
