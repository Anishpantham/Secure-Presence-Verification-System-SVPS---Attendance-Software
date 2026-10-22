# SPVS setup and demonstration guide

This guide accompanies the source ZIP. The complete design and measured results are in the project report and verification report.

## 1. Unpack and inspect

Extract `SPVS_COMPLETE_PROJECT.zip`. Its `spvs-root` directory contains actual application files, migrations, tests, lockfiles and documentation. It excludes `.env`, installed dependencies, biometric data and database volumes. The included model licenses describe the official pretrained assets. Read `SPVS_DELIVERY_README.md` for the current validation boundary.

## 2. Prepare the development machine

Install Docker Desktop, Python 3.12, uv, Node 24 LTS and Git. On an M4 Mac use ARM64 installations. Run these commands from `spvs-root`:

```sh
make setup
make db
make migrate
make seed
```

Setup generates secrets only when `.env` does not exist. Keep the existing file across restarts. The demo accounts are `admin@spvs.example`, `faculty@spvs.example` and `student@spvs.example`. Read `DEMO_PASSWORD` locally from `.env` when signing in. Do not send it to an external service or include it in screenshots.

## 3. Start desktop components

Run `make api` in one terminal and `make dashboard` in another. The API uses port 8000 and web dashboard 5173. Check `/health` for database readiness and `/ready` for model initialization. The API's interactive contract is at `/docs`. In the administrator dashboard, configure real classroom coordinates and Wi-Fi references or select an explicit fallback policy.

## 4. Prepare the student phone

Install Android Studio and compatible SDK tools. In `mobile`, copy `.env.example` to `.env`, set the API URL ending in `/api/v1`, then run `npm ci` and `npm run android`. A physical phone needs the developer computer's reachable LAN address or trusted HTTPS URL. Expo Go is insufficient for the local Wi-Fi module. iOS requires Xcode/signing and reports Wi-Fi scan support as unavailable.

Grant camera and foreground location permissions. Register the phone using password confirmation, then consent to enrollment. Use a single face, good lighting and a slow blink. Do not use fake GPS, a generated portrait or preapproved attendance to make a demo appear successful.

## 5. Validate before evaluation

Create the separate test database, fetch public smoke-test samples and run `make test` and `make build`. Start the API/dashboard and run the browser tests. Read the current generated results rather than assuming a zero exit code means hardware validation. Record physical-device cases separately.

## 6. Demonstrate

Use the sequence in `docs/DEMO_SCRIPT.md`: academic configuration, session creation, real student verification when hardware is validated, understandable decision, review/correction audit, session closure and export. Explain uncertainty and operating-system limits. Show an empty chart honestly when there have been no attempts.

## 7. Recover and maintain

Restart the existing database and application processes without deleting volumes. If secrets are lost, restore them from the operator's protected backup. Do not disable TLS or checksum verification for a failed download. Use the deployment troubleshooting table and the exact failure reasons returned by the API. Refresh tokens can be revoked; access tokens expire within their configured lifetime. Administrator corrections remain attributable.

## 8. Submission

The academic PDF contains editable identity placeholders in its source Markdown. Fill in college, student, roll number, supervisor and academic year, then rerun the packaging script. Include only measured test results. Keep attestation and real-device limitations visible in both the oral demonstration and report.
