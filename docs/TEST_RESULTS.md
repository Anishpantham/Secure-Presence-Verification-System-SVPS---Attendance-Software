# Test and build results

Generated from actual result files at **2026-10-23 03:02 IST**. JUnit timestamps reflect the Linux runner clock.

| Suite | Passed | Failed/errors | Skipped | Execution platform |
|---|---:|---:|---:|---|
| Backend / PostgreSQL (includes real-model tests) | 72 | 0 | 0 | Linux x86_64 |
| Dashboard interactions | 8 | 0 | 0 | Linux x86_64 |
| Mobile protocol and UI logic | 7 | 0 | 0 | Linux x86_64 |
| Chromium against running containers | 2 | 0 | 0 | Linux x86_64 |

Unique suite totals: **89 passed, 0 failed/errors, 0 skipped**.

## Commands executed

- `bash scripts/backend.sh pytest --junitxml=../artifacts/backend-tests.xml`
- `cd dashboard && npm test -- --run --reporter=junit --outputFile=../artifacts/dashboard-tests.xml`
- `cd mobile && npm test -- --run --reporter=junit --outputFile=../artifacts/mobile-tests.xml`
- `cd dashboard && npx playwright test`

## Build and runtime validation

| Capability | Observed outcome |
|---|---|
| Execution environment | Linux x86_64; Python 3.12, Node 24, PostgreSQL 16; no macOS ARM64 execution. |
| Reusable cloud setup | PASS: bash scripts/cloud_install.sh completed; npm ci, uv sync --frozen, three checksum-verified models, migrations, repeatable seed and both Docker builds. Existing local secrets preserved. |
| Database schema | PASS: alembic upgrade head and alembic check; no new upgrade operations detected; PostgreSQL integration tests passed. |
| Backend image and runtime | PASS: docker build with trusted CA secret; docker compose up -d --no-build db backend dashboard recreated services successfully. GET /health reports database connected; GET /ready reports face_models loaded and attestation not_configured. |
| Dashboard production build | PASS: npm run build (TypeScript and Vite); nginx Docker image starts and serves the actual API-connected dashboard. |
| Browser integration | PASS: npx playwright test against running Docker services; administrator room/session/export/close workflow and scoped faculty workflow. Tests use the created session ID and wait for navigation to remain repeatable. |
| Mobile type checking | PASS: npm run typecheck after the verification-result navigation correction. |
| Mobile Android bundle | PASS: CI=1 EXPO_NO_TELEMETRY=1 npm run export after the navigation correction; Metro/Hermes produced the actual Android bundle. |
| Android native preparation | PASS: Expo Android prebuild and local spvs-wifi module autolinking. Java 17, Gradle 9.4.1, Android API/build tools 37 and NDK 27.1.12297006 installed for the attempted build. |
| Android APK build | BLOCKED: ./gradlew :app:assembleDebug --no-daemon --max-workers=2 -PreactNativeArchitectures=arm64-v8a failed while resolving react-android-0.88.0-debug.aar. Maven Central redirects to repo.reactnative.dev, blocked by the cloud proxy with HTTP 403. Domain added to the saved environment draft; apply configuration before retrying. No APK produced; native compilation remains unverified. |
| Physical phone, iOS and Apple Silicon | NOT RUN: requires device/macOS hardware. Camera liveness, actual GPS/Wi-Fi behavior, accessibility and latency need the documented device matrix. |
| Platform attestation | UNCONFIGURED: adapter returns unverified; external Play Integrity/App Attest developer configuration is required. |
| Cloud configuration persistence | SAVED DRAFT: tested install/start instructions plus repo.reactnative.dev network addition. Saving is not applying/publishing; fresh-task restoration has not been independently tested. |

## Dependency audits

- Backend: 0 runtime packages with reported vulnerabilities in the locked-requirements audit.
- Dashboard: 0 affected package entries (0 critical, 0 high, 0 moderate, 0 low).
- Mobile: 45 affected package entries (0 critical, 45 high, 0 moderate, 0 low).

Audit commands: `npm audit --json` in each client; `pip-audit -r .runtime/backend-requirements.txt --format json` using requirements exported from `backend/uv.lock`. Raw reports are in `docs/evidence`.

## Interpretation and unverified behavior

The backend's four real-model smoke cases are included in its total, not counted twice. Its API transaction happy paths explicitly substitute vision inside pytest fixtures; they do not prove live human capture. Real-model smoke tests execute the current YuNet, SFace and MediaPipe Tasks pipeline. No physical phone, iOS device, macOS ARM64 run, provider-backed attestation or population biometric evaluation was performed.

The mobile audit's affected entries propagate two root advisories through the Expo/Metro tree: GHSA-vfj7-8cjw-p6xm (`braces`) and GHSA-86w9-cpqp-85rv (`node-forge`). The registry reported no fixed version. See `KNOWN_LIMITATIONS.md`; do not interpret build success as security certification.

No manual sensor or live-biometric success is claimed. Intermediate failures included a missing graphics runtime, cloud CA trust configuration, older dependency advisories and test locator/assertion errors; these were diagnosed before the recorded final successful checks. Any still-blocked native capability appears in the build table.
