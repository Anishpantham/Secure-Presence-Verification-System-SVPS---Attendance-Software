# Testing strategy

## Automated suites

Backend tests use a dedicated PostgreSQL database, not SQLite. Migrations run before fixtures and tables are truncated between cases. `SPVS_TEST_DATABASE_URL`, if set, must identify a database ending in `_test`. The default derives `spvs_test` using the development database credentials. This guard prevents accidental truncation of a non-test database.

```sh
docker compose exec -T db createdb -U spvs spvs_test
python3 scripts/download_test_samples.py
cd backend
.venv/bin/alembic upgrade head
.venv/bin/alembic check
.venv/bin/pytest --junitxml=../artifacts/backend-tests.xml
```

The service suite exercises geofence boundaries, mocked/stale/inaccurate GPS, missing/matching/weak Wi-Fi, impossible travel, fail-closed attestation, embedding normalization and temporal sequences. Database-backed API tests cover roles, account management, refresh rotation/replay, sessions, correction history, CSV, device reset, consent, signed evidence, idempotency and simultaneous retries. Model smoke tests execute actual YuNet, SFace and MediaPipe on public reference portraits.

The API happy-path transaction tests replace vision through pytest monkeypatching **only within tests**. They establish the API-to-database decision wiring but do not establish a person's live capture. The separately labeled real-model tests do not estimate population biometric accuracy. Report both categories accurately.

```sh
cd dashboard
npm test -- --run --reporter=junit --outputFile=../artifacts/dashboard-tests.xml
npm run build
npx playwright test
cd ../mobile
npm run typecheck
npm test -- --run --reporter=junit --outputFile=../artifacts/mobile-tests.xml
npm run export
```

Dashboard unit tests exercise login, errors, role navigation, record filtering, form submission and token refresh. Playwright uses Chromium against the running FastAPI/PostgreSQL/Vite stack; no browser API interception is used. It modifies only named demo data. Mobile tests validate HMAC interoperability, payload binding, session-time boundaries and accurate result wording. Type checking and Metro/Hermes export validate JavaScript composition, not Kotlin compilation or sensor behavior.

## Physical-device matrix — must be recorded separately

| Case | Procedure | Expected result |
|---|---|---|
| Real enrollment | Registered phone, consent, one face, even lighting | Actual server liveness passes and encrypted template is created |
| Wrong person | A second consenting person performs the same session challenge | Face mismatch; no attendance record |
| Static photograph | Present a printed portrait without live motion | Sequence failure; no attendance record |
| Screen replay | Try prerecorded and challenge-specific video | Measure outcomes; do not assume all attacks fail |
| Head direction | Test both directions on front camera, Android/iOS | Unmirrored pose signs agree with prompts |
| Blink timing | Normal and slow blink across phone camera frame rates | Identify retry/false-reject behavior and calibrate |
| GPS boundary | Inside, overlapping accuracy circle, clearly outside | PRESENT only if other checks pass; review/reject as specified |
| Permission denial | Deny camera and location separately | Actionable error; no fake submission success |
| Android Wi-Fi | Known campus APs with permissions and location enabled | Real BSSID/RSSI readings or explicit unavailable status |
| iOS Wi-Fi | Run iOS development build | Explicit unsupported status; configured fallback |
| Revoked phone | Approve a reset then submit from old phone | Device authorization denied |
| Network loss | Interrupt after submit, retry identical signed payload | One attendance attempt/record, same response ID |
| Native integrity | Configure provider separately and submit invalid/replayed token | Provider verification must fail closed |

Record phone model, OS, app build, permissions, model hashes, face threshold, lighting, measured positions, timings and observed database outcome. Use volunteers who consent. Do not upload their samples into the public repository. A semester report should include only measurements actually collected.

## Dependency and deployment validation

Run `npm audit --json` in each client and `pip-audit` against the locked backend runtime requirements. Keep unresolved upstream advisories visible; do not use `--force` to silently downgrade the SDK. Verify container builds on the intended architecture, health/readiness and migration restart. Mac ARM64 instructions are provided but an x86_64 cloud test is not an Apple Silicon execution result.
