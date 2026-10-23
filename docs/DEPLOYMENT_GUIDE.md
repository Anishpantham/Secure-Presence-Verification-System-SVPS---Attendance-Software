# Deployment guide

## Local prerequisites and compatibility

Use Python 3.12, `uv`, Node 24 LTS (or a compatible Node 22 version meeting the locked tool engines), Docker with Compose, and Git. On Apple Silicon, install native ARM64 Python/Node and Docker Desktop for Apple Silicon. PostgreSQL 16 has ARM64 images. OpenCV and MediaPipe wheels must match the interpreter and architecture; avoid mixing x86 Homebrew libraries with ARM64 wheels. This environment's measured platform is Linux x86_64, so macOS native validation remains a manual task.

The normal setup is `make setup`, `make db`, `make migrate`, `make seed`, followed by `make api` and `make dashboard`. The generated `.env` contains unique local secrets. Protect it with restrictive permissions and never include it in an academic submission. For phones, configure `mobile/.env` with a reachable API URL; it contains no credentials.

Linux hosts also need `libgl1`, `libgles2`, `libegl1` and `libglib2.0-0`. The Dockerfile installs these through the distribution package manager. In the restricted cloud workspace, `scripts/cloud_install.sh` extracts verified distribution libraries from a temporary container into ignored local runtime storage; `scripts/backend.sh` activates that location. It does not replace system libraries or disable package/TLS verification. On a normal Debian/Ubuntu machine, installing the packages with the system package manager is simpler.

## Docker workflow

1. Generate `.env` and checksum-verified face models.
2. Run `docker compose up --build -d`.
3. Run `docker compose exec backend python -m app.seed` for local demonstration accounts only.
4. Check API `/health` and `/ready`; readiness must load all model assets.
5. Sign into the dashboard and configure real classroom data.

The backend image uses a pinned uv executable and a frozen Python lockfile. The web image uses `npm ci` and nginx. PostgreSQL has a health check and a persistent named volume. API migrations run before uvicorn at container startup. Persistent database files and model files survive process restarts; HTTP processes and authentication sessions in browser memory do not.

Corporate/cloud TLS interception may require the existing trusted CA bundle inside build steps. Both Dockerfiles support an optional BuildKit secret named `ca_bundle`. The cloud installer supplies the host's trusted public CA bundle using `--secret`; it is not baked into the image or included in artifacts. Normal direct-Internet Compose builds need no extra secret. Never use insecure TLS flags as a workaround.

## Production-inspired deployment changes

The Compose configuration is a development baseline. Add trusted HTTPS termination, a non-demo administrator provisioning process, institution-specific CORS origins, encrypted backups, key rotation and a retention policy. Remove demo accounts or replace their passwords before real use. Keep the database port private. Use a separate least-privilege application database role and reviewed migration credentials; the development `spvs` role is also the database owner.

Verify `JWT_SECRET` and `BIOMETRIC_KEY` are independent, generated secrets delivered through a secret manager. Rotating the biometric key without re-encryption makes stored templates/device keys unreadable. Do not invent credentials for provider attestation. Add a provider-backed verifier only with real Google/Apple project credentials and package/signing configuration.

## Android development build

Install Android Studio and its supported SDK/NDK tools, enable USB debugging on a test phone and run `npm run android` in `mobile`. The generated project declares the exact SDK/Gradle versions selected by the locked Expo release. `expo prebuild --platform android --no-install` regenerates native code and discovers the local Wi-Fi module. Do not use Expo Go for that module. Gradle compilation, a Metro/Hermes export and physical device tests are distinct checks.

Use a trusted HTTPS URL for distribution. Development HTTP on a local network is only for controlled local testing. Do not put a raw API secret or biometric key in `EXPO_PUBLIC_*`: those values are embedded in the client bundle. iOS builds require Xcode/signing on macOS, and the application reports Wi-Fi scanning as unsupported.

## Troubleshooting

| Symptom | Diagnosis / action |
|---|---|
| Database connection failure | Start Compose database, confirm port availability and `.env` URL |
| Backend config validation fails | Generate real JWT/Fernet secrets; placeholders are intentionally invalid |
| Readiness returns 503 | Run verified model downloader; inspect missing assets and writable caches |
| Official downloads denied | Allow `media.githubusercontent.com` and `storage.googleapis.com` in environment settings |
| Model checksum mismatch | Stop using the file; retry official source and investigate upstream provenance |
| Phone cannot reach API | Use LAN address/HTTPS; `localhost` on a phone points to the phone |
| Wi-Fi unavailable | Confirm native build, location permission/services and Android scan throttling; follow policy |
| Frequent liveness retries | Evaluate frame timing, slow blink, pose direction and lighting on the actual device |
| Browser session disappears on reload | Intended in-memory token storage; sign in again |
| Duplicate request conflicts | Preserve exact signed payload/key for a retry; use new challenge for new evidence |

Do not delete the PostgreSQL volume to resolve ordinary setup issues. `docker compose down -v` is destructive and is not part of normal setup or restart instructions.

## Android dependency download in this cloud

The observed Gradle build used Java 17, Gradle 9.4.1, Android API/build tools 37 and NDK 27.1.12297006. React Native 0.88.0’s AAR redirects from Maven Central to `repo.reactnative.dev`; allow that specific domain if the proxy returns HTTP 403. The saved cloud configuration includes this addition, but saving a draft does not apply it. Review/save the environment settings and publish before retrying. Keep TLS verification enabled, using the environment’s trusted Java CA store where necessary. Full native compilation and device execution remain unverified in the delivered results.

## Cross-platform release configuration

Apply migrations through `7a2d13ce4f90` before deploying updated clients. Leave ALLOW_LEGACY_DEVICE_REGISTRATION=false; migrate existing HMAC devices through approved resets. Configure ios_presence explicitly, retaining review by default. Set APPLE_APP_ID, APPLE_ATTEST_ENVIRONMENT, APPLE_ATTEST_ROOT_PEM and APPLE_ATTEST_ROOT_SHA256 only after verifying Apple Developer configuration and the official trust anchor; mount the PEM read-only into the backend container. A successful /ready response proves model/database availability, not platform attestation deployment.

Use HTTPS, institution-owned signing credentials and tested backups. Raw frames are transient; encrypted biometric templates persist until explicit deletion. Define and implement institution-approved retention for templates, coarse location summaries, security events and expired challenges before real deployment. Automated retention/cryptographic key rotation and load testing remain operational work; the academic package does not invent a compliance guarantee. Run the physical Android/iPhone matrix and genuine App Attest interoperability checks before enabling production policy. EAS/TestFlight instructions are in SETUP_AND_DEMO_GUIDE.md.
