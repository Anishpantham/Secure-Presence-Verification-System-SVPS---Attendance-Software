# SPVS engineering verification report

**Historical baseline report.** Current validation and publication status are in
[current status](docs/CURRENT_STATUS.md); the 24 October audit is pre-publication history.

Generated **2026-10-23 03:02 IST** from the actual workspace and test outputs.

## Delivery status

Actual application source, PostgreSQL migration, clients, tests, model-download configuration, documentation and packaging tools exist. This is a production-inspired college project. Hardware validation and configured platform attestation remain outstanding; the mobile dependency advisories below remain unresolved. Read those limits before treating this as a deployable institutional system.

## Tests

| Suite | Passed | Failed/errors | Skipped | Execution platform |
|---|---:|---:|---:|---|
| Backend / PostgreSQL (includes real-model tests) | 72 | 0 | 0 | Linux x86_64 |
| Dashboard interactions | 8 | 0 | 0 | Linux x86_64 |
| Mobile protocol and UI logic | 7 | 0 | 0 | Linux x86_64 |
| Chromium against running containers | 2 | 0 | 0 | Linux x86_64 |

Total: **89 passed, 0 failed/errors, 0 skipped**.

- `bash scripts/backend.sh pytest --junitxml=../artifacts/backend-tests.xml`
- `cd dashboard && npm test -- --run --reporter=junit --outputFile=../artifacts/dashboard-tests.xml`
- `cd mobile && npm test -- --run --reporter=junit --outputFile=../artifacts/mobile-tests.xml`
- `cd dashboard && npx playwright test`

## Builds and startup

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

## What was verified

- Real PostgreSQL migration and schema constraints, authentication and backend role scope.
- Course/enrollment/classroom workflows, session creation/closure and actual dashboard-to-API integration.
- Refresh-token rotation/reuse, evidence HMAC verification, device reset/revocation, replay, idempotency and concurrent duplicate protection.
- Server-side geofence, accuracy/freshness, Wi-Fi fallback, explainable anomalies, disputes and correction auditing.
- Real model-generated 128-dimensional embeddings, same-person variation, different-person rejection and no/multiple-face rejection on public test portraits.
- Server temporal-liveness sequence/timing rules on unit inputs; no client-supplied successful liveness verdict is trusted.
- Dashboard forms and role navigation, actual browser session lifecycle/CSV export, mobile TypeScript/signing logic and Android JavaScript bundle.

## Verification boundaries

The backend's four real-model smoke cases are included in its total, not counted twice. Its API transaction happy paths explicitly substitute vision inside pytest fixtures; they do not prove live human capture. Real-model smoke tests execute the current YuNet, SFace and MediaPipe Tasks pipeline. No physical phone, iOS device, macOS ARM64 run, provider-backed attestation or population biometric evaluation was performed.

The mobile audit's affected entries propagate two root advisories through the Expo/Metro tree: GHSA-vfj7-8cjw-p6xm (`braces`) and GHSA-86w9-cpqp-85rv (`node-forge`). The registry reported no fixed version. See `KNOWN_LIMITATIONS.md`; do not interpret build success as security certification.

## Dependency audits

- Backend: 0 runtime packages with reported vulnerabilities in the locked-requirements audit.
- Dashboard: 0 affected package entries (0 critical, 0 high, 0 moderate, 0 low).
- Mobile: 45 affected package entries (0 critical, 45 high, 0 moderate, 0 low).

## Files and artifacts

The source ZIP is `SPVS_COMPLETE_PROJECT.zip`. PDF outputs are `SPVS_PROJECT_REPORT.pdf` and `SPVS_SETUP_AND_DEMO_GUIDE.pdf`. The archive contains source, locks, migrations, documentation, audit/test evidence and the verified pretrained model assets. It excludes secrets, node_modules, Python virtual environments, camera samples, native generated folders and database contents. `docs/FILE_MANIFEST.txt` lists packaged source files with SHA-256 values (excluding the manifest itself). PDF readability, ZIP CRCs and required members are checked by `scripts/package_submission.py`; `artifacts/artifact-checks.json` records those checks.

## Remaining work

1. Run and document the real-device matrix in `docs/TESTING_STRATEGY.md`, including live enrollment/attendance, spoof attempts, direction/blink timing and actual Android Wi-Fi measurements.
2. Configure Google/Apple provider verification only with real developer-account settings; current verdicts remain unverified.
3. Calibrate face/liveness thresholds on consented local evaluation data and establish accessible review alternatives.
4. Resolve upstream Expo tooling advisories when patches become available; complete production TLS, secrets, backups, retention and operational hardening before real institutional use.
5. Fill the academic title-page placeholders and add only measurements actually collected.
