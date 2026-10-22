# Secure Presence Verification System · SPVS

A working college attendance project with **two verification layers**: identity and physical presence. FastAPI/PostgreSQL enforce decisions; a React dashboard manages institution workflows; an Expo development app captures real student evidence.

**Assurance boundary:** this is a production-inspired semester project, not a certified biometric or device-attestation product. Real SFace inference and server-side liveness logic are implemented. Phone capture, Android Wi-Fi behavior, and liveness usability require the real-device evaluation in `docs/TESTING_STRATEGY.md`. Play Integrity and App Attest are deliberately unconfigured and never report a successful verdict.

## Start on a MacBook Air M4

Install Docker Desktop for Apple Silicon, Python 3.12, Node 22.12+ (Node 24 LTS recommended), and `uv`. Use native ARM64 terminals, not a Rosetta Python environment. Then, from this repository:

```sh
make setup
make db
make migrate
make seed
```

In separate terminals:

```sh
make api
make dashboard
```

The API listens on port 8000 and the dashboard on 5173. API documentation is served at `/docs`, with the contract at `/openapi.json`. `GET /health` checks PostgreSQL; `GET /ready` also loads both face models and MediaPipe.

The seed creates `admin@spvs.example`, `faculty@spvs.example`, and `student@spvs.example`. Their shared **local demonstration password is randomly generated in `.env` as `DEMO_PASSWORD`**. It is not included in the distribution or printed by setup. Use individual institution accounts outside the demo. The seed is repeatable and never creates fabricated attendance, biometric profiles, device credentials, or Wi-Fi readings. Edit the explicitly marked demo classroom with real coordinates before a phone demo.

## Student app

```sh
cd mobile
cp .env.example .env
# Set EXPO_PUBLIC_API_URL to your API's reachable address, ending in /api/v1.
npm ci
npm run android
```

Android Studio, an installed Android SDK, Java compatible with the generated Gradle project, and a connected phone/emulator are required. `npm run android` creates a development build; use `npm start` to reconnect Metro. Expo Go cannot load the included Android Wi-Fi module. An Android emulator can reach the host through `10.0.2.2`; a phone needs a LAN-reachable development server or trusted HTTPS endpoint. Release builds require HTTPS. iOS development builds need Xcode and signing; Wi-Fi scans are explicitly unsupported on iOS.

## Verify the project

```sh
docker compose exec -T db createdb -U spvs spvs_test  # once
python3 scripts/download_test_samples.py
make test
make build
cd dashboard && npx playwright test
```

Browser tests require the running API/dashboard, seeded demo accounts, and Chromium (`SPVS_CHROMIUM_PATH` may override the Linux default). They create a real session, modify the demo classroom and close that session. Backend tests use only a database ending in `_test`, run Alembic, and truncate that test database between tests. Never point `SPVS_TEST_DATABASE_URL` at a live database.

See `docs/TEST_RESULTS.md` for measured results and `SPVS_VERIFICATION_REPORT.md` for the complete verification boundary. The API transaction tests explicitly replace vision **inside tests only**; real-model smoke tests separately execute YuNet, SFace and MediaPipe. Neither substitutes for real-device liveness evaluation.

## Containers

After `python3 scripts/init_env.py` and `python3 scripts/download_models.py`:

```sh
docker compose up --build -d
docker compose exec backend python -m app.seed
```

PostgreSQL persists in the `pgdata` volume. Backend runs as a non-root user; the web container proxies `/api` to FastAPI. Container setup never includes a real TLS termination service: add a trusted HTTPS reverse proxy for deployment. Production configuration and backup guidance are in `docs/DEPLOYMENT_GUIDE.md`.

## What is included

| Directory | Purpose |
|---|---|
| `backend/app/api` | Versioned, role-scoped REST endpoints |
| `backend/app/services` | Actual face pipeline, temporal liveness, geofencing and Wi-Fi rules |
| `backend/alembic` | Explicit PostgreSQL schema migration |
| `dashboard` | Accessible institutional web workflows, charts and CSV exports |
| `mobile` | Student app and native Android Wi-Fi module |
| `scripts` | Repeatable local setup, verified downloads and submission packaging |
| `docs` | Design, academic report, security analysis and measured results |

Dependencies are pinned by `backend/uv.lock` and the two `package-lock.json` files. Official model bytes are checksum-verified; their licenses are retained in `docs/LICENSE-SFACE.txt` and `docs/LICENSE-YUNET.txt`.

## Reading order

1. `docs/SETUP_AND_DEMO_GUIDE.md` — installation and evaluation walkthrough.
2. `docs/SYSTEM_ARCHITECTURE.md` and `docs/DATABASE_DESIGN.md` — implementation maps.
3. `docs/SECURITY_ARCHITECTURE.md` and `docs/KNOWN_LIMITATIONS.md` — guarantees and boundaries.
4. `docs/PROJECT_REPORT.md` — editable college submission.

There are no BLE beacons, ESP32 devices, ultrasonic tokens, surveillance cameras, blockchain storage, fabricated sensor measurements, or pretend AI predictions.
