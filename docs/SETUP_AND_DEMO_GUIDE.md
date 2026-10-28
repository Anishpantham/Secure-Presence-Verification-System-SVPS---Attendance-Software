> Current checkpoint: [28 October audit](REPOSITORY_AUDIT_2026-10-28.md), [current status](CURRENT_STATUS.md), and [safe demo guide](EVALUATION_DEMO_GUIDE.md). Existing recovery installations must not run setup/seed/reset instructions intended for fresh databases. Dated counts below are historical unless explicitly rerun in [current test results](TEST_RESULTS.md).

# SPVS final setup and demonstration guide

## Current local QR/audio checkpoint

The [27 October runtime update](LOCAL_RUNTIME_UPDATE_2026-10-27.md) has already
backed up/migrated the local database, refreshed dependencies and built Android,
iOS simulator and signed-device clients with SpvsAcoustic. The new apps were not
installed on phones. Wait for the user's explicit classroom readiness before
installation or physical trials; old installed clients cannot complete policy v2.

For the next attendance test, use a fresh session and start the faculty QR/audio
controls. The student scans QR, requests microphone access, starts listening,
and identifies their queued attempt; faculty plays that signal before face and
location capture proceed. See [the detailed physical plan](ACOUSTIC_DEVICE_VALIDATION.md).
Do not enable iOS dynamic or required attestation policies merely to make a demo
pass; the local review choices were retained. Database records and raw/private
calibration inputs are local state, not part of Git synchronization.

See [iOS Mac validation](IOS_MAC_VALIDATION.md) for native setup and iPhone
observations, and [Android physical validation](ANDROID_DEVICE_VALIDATION_2026-10-26.md)
for the completed hostel demo through manual review and phone history.

Use the **SPVS: dashboard** task for the local faculty UI at
`http://127.0.0.1:5173`. The API and Metro tasks must also be running for phone
testing. The Motorola's Wi-Fi must actually be connected to the Mac's reachable
network; enabling Wi-Fi without joining it is insufficient. The dedicated Android
demo student was created in the local database and is not automatically created
by a fresh clone/seed; create a separate student through Administration and enroll
it in the test course when preserving an existing iPhone registration.

Use the source ZIP from this completion branch and read FINAL_COMPLETION_REPORT.md before presenting capabilities. Keep the baseline release intact. Commands below are for a MacBook Air M4 with macOS and a trusted development network. The Linux execution report does not claim these Mac commands were run on Apple Silicon.

## 1. Prerequisites

Install Homebrew from its official instructions, Docker Desktop for Apple Silicon, Android Studio for Apple Silicon, and Xcode from the App Store. Launch each application once, accept its license and complete first-run components. In Xcode Settings > Locations select the active command-line tools. Then install:

```sh
brew install python@3.12 node@22 uv openjdk@17 ruby
export PATH="$(brew --prefix node@22)/bin:$(brew --prefix ruby)/bin:$PATH"
export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
xcodebuild -version
node --version
java -version
```

Use Python 3.12, Node 22 (or the verified Node 24 environment), JDK 17 and the pinned npm/uv lockfiles. React Native's checked-in helper requires at least Xcode 16.1; install a current compatible Xcode and supported iOS simulator runtime. In Android Studio's SDK Manager install the SDK, build tools, CMake and NDK versions reported by the generated project. This run used Android API/build tools 37, Gradle 9.4.1 and NDK 27.1.12297006. Let official tools install missing exact versions. Do not substitute unofficial Maven mirrors or disable TLS.

## 2. Local services and accounts

From the unpacked `spvs-root` directory:

```sh
python3 scripts/init_env.py
uv sync --project backend --frozen
python3 scripts/download_models.py
npm ci --prefix dashboard
npm ci --prefix mobile
docker compose up -d db --wait
bash scripts/backend.sh alembic upgrade head
bash scripts/backend.sh alembic check
bash scripts/backend.sh python -m app.seed
```

The setup script creates local `.env` secrets and a random DEMO_PASSWORD. Read that password locally; never paste it into reports or commit the file. Demo accounts are admin@spvs.example, faculty@spvs.example and student@spvs.example. Seed creates no attendance or biometrics. Change the demo classroom to real coordinates and permitted real AP references before phone testing.

Run in separate terminals:

```sh
make api
make dashboard
```

The API listens on port 8000 and the dashboard on 5173. Alternatively use `docker compose up --build -d` after models are downloaded. Open http://localhost:5173. `/health` checks PostgreSQL and `/ready` also loads the real models. Use trusted TLS for any real data. Create individual accounts for institutional testing instead of shared demo credentials.

## 3. Automated verification

Create an isolated test database once, without changing the application database:

```sh
docker compose exec db createdb -U spvs spvs_test
bash scripts/backend.sh pytest
npm test --prefix dashboard -- --run
npm test --prefix mobile -- --run
npm run build --prefix dashboard
npm run typecheck --prefix mobile
cd mobile
npx expo export --platform android
npx expo export --platform ios
cd ../dashboard
npx playwright install chromium
npx playwright test
```

On macOS the configuration uses Playwright's installed Chromium. Set SPVS_CHROMIUM_PATH only when explicitly selecting another executable. The browser tests read the local demo password in memory, exercise real API endpoints and change only demo data. PostgreSQL tests require a database name ending `_test` and truncate its tables. Unit/contract tests use synthetic sensor and attestation inputs; they are not physical-device verification.

## 4. Android debug build and run

For emulator-only development set EXPO_PUBLIC_API_URL to http://10.0.2.2:8000/api/v1; for a physical phone set a LAN-reachable server URL. For real data use trusted HTTPS. Set SPVS_DEV_HTTP=1 only for a local HTTP development build.

```sh
export EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1
export SPVS_DEV_HTTP=1
bash scripts/build_mobile_macos.sh android
cd mobile
npx expo start --dev-client
```

The script runs a genuine Gradle assembleDebug and copies its output to release/final/SPVS_ANDROID_DEBUG.apk only on success. Install with `adb install -r android/app/build/outputs/apk/debug/app-debug.apk` from mobile, or use Android Studio. The debug development client needs Metro; it is not a signed production app. Use `adb reverse tcp:8081 tcp:8081` when developing over USB. Configure the API endpoint consistently in the terminal running Metro.

The [24 October Mac Android build](ANDROID_MAC_VALIDATION.md) also works with
official command-line SDK tools; Android Studio is not required for that path.
The build script discovers Homebrew Java 17 and `.runtime/android-sdk` when
available, while respecting explicit `JAVA_HOME` and `ANDROID_HOME` settings.
The saved **SPVS: Android debug build** task targets arm64-v8a. Use
`SPVS_ANDROID_ARCHITECTURES` to select another supported architecture. After
installation, sign in and use **Settings → Wi-Fi setup check** before attempting
attendance. Register actual classroom AP references using measured data.

For release distribution remove SPVS_DEV_HTTP, set an HTTPS API URL, configure institution-owned signing keys outside Git and build a reviewed release variant. Never distribute the debug signing key as an institutional credential.

## 5. iOS project, CocoaPods and simulator

```sh
cd mobile
brew install ruby@3.3
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
export BUNDLE_PATH="$PWD/../.runtime/bundle"
bundle install
cd ..
export EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
export SPVS_DEV_HTTP=1
bash scripts/build_mobile_macos.sh ios-simulator
cd mobile
npx expo run:ios
```

The script generates `ios/SPVSStudent.xcworkspace` with `--no-clean`, installs pods and invokes xcodebuild with simulator SDK and CODE_SIGNING_ALLOWED=NO. The simulator can test navigation/network/permission states; it cannot establish Secure Enclave, App Attest, live-camera liveness or real Wi-Fi behavior. The resolved Ruby and CocoaPods lockfiles are now retained from the [Mac run](IOS_MAC_VALIDATION.md); earlier Linux results did not establish iOS compilation.

## 6. Physical iPhone and App Attest

Set an HTTPS API endpoint reachable from the phone, then:

```sh
unset SPVS_DEV_HTTP
export EXPO_PUBLIC_API_URL=https://YOUR-INSTITUTION-HOST/api/v1
export SPVS_APP_ATTEST_ENV=development
bash scripts/build_mobile_macos.sh ios-device
```

In Xcode select the SPVSStudent target, set a development team, verify bundle ID/capabilities and select a connected iPhone. Enable Developer Mode on the phone and trust the developer profile if requested. Press Run. Start Metro with the same API environment. Camera and location require user consent; select Precise Location. Configure App Attest server trust settings and Apple Developer capabilities exactly as described in CROSS_PLATFORM_IMPLEMENTATION.md. Unsupported or unconfigured App Attest remains unverified. Handle a key-lost error through administrator device reset; never silently replace the registered key.

EAS is optional. The checked-in eas.json defines development, simulator, preview and production profiles. Run `eas init` in your own account, configure EXPO_PUBLIC_API_URL for the selected profile and run `eas build --platform ios --profile development`. Keep signing credentials in EAS or the Keychain. For TestFlight create an App Store Connect app, use production App Attest entitlement/server environment, increment build version, produce a genuine signed archive with Xcode Organizer or EAS production, upload and complete Apple's review/export-compliance steps. No IPA is included unless actually compiled and signed.

## 7. Demonstration sequence

1. Sign in as administrator, configure a real room, enrollment and the separate Android/iPhone presence policies. Keep iPhone review as the safe default.
2. Sign in as faculty and create a currently active session.
3. On a physical phone sign in as student and register a native device key with password confirmation. Inspect the reported capability in the admin dashboard.
4. Consent to biometric enrollment, permit the camera and follow the randomized center/head-turn/blink prompts. Show the actual result, including retry failures.
5. Select the session and complete fresh identity and location capture. Demonstrate that iPhone current-network data is not a Wi-Fi fingerprint and that review is not attendance approval.
6. Inspect faculty attempts, attendance records, audit events and CSV exports. Test invalid signature/replay using automated tests; do not fake a physical success.
7. Demonstrate face deletion/re-enrollment and an audited lost-device reset. Show pending real-device/provider/calibration work honestly.

## 8. Troubleshooting

- API unreachable on phone: localhost means the phone itself. Use the Mac LAN IP or trusted HTTPS host, bind API to 0.0.0.0, check firewall and same-network routing. Development HTTP requires a freshly generated development configuration; production remains HTTPS-only.
- Expo Go or missing native module: install a generated development client. Restarting Metro cannot add native modules to an existing binary.
- iPhone Wi-Fi unavailable: verify entitlement, provisioning and Apple's location/privacy requirements. Do not insert dummy BSSID/RSSI values; use review or retry.
- Reduced GPS/poor accuracy: enable Precise Location and retry with a fresh fix. Indoor GPS may remain insufficient.
- Liveness failures: use even light, one face, slow blink and steady capture. Inspect actual timing/orientation on each device. Do not lower mandatory identity rules to force a demo.
- Gradle 403/network/TLS failures: inspect the exact official repository URL. Allow it through the institutional network and configure the JVM proxy/CA correctly. Preserve TLS and artifact verification. Do not mirror an unverified AAR manually.
- Xcode/CocoaPods errors: verify active Xcode, compatible simulator runtime, Ruby/Bundler and generated podspecs. Source code or prebuild success does not prove native compilation.
- App Attest rejected: check TeamID.bundleID, environment, official root fingerprint, matching entitlement and physical-device support. A verified synthetic test certificate is not an Apple attestation.


Policy v2 retires the iOS gps_only option. Current iOS choices are review, retry and dynamic; the migration maps an existing gps_only choice to dynamic while retaining stricter review/retry settings. Dynamic requires completed QR/audio proof alongside mandatory identity/device/GPS gates; a global requirement for attestation still applies. The local review policy was not changed. QR/audio does not independently attest a platform or sensor and can be relayed. See [the protocol](ACOUSTIC_DYNAMIC_QR.md).
