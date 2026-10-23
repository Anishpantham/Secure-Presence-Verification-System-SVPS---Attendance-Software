# Native iOS validation on the local Mac

Date: 2026-10-23. Branch: `spvs/ios-native-completion`, starting at `3591220`.
This is an incremental validation record. Physical iPhone enrollment/attendance testing and genuine
Apple App Attest remain pending. Earlier Linux reports are historical.

## Observed environment

| Component | Observed version/status |
| --- | --- |
| Host | Darwin arm64, macOS 27.0 (26A428); user identifies MacBook Air M4 |
| Xcode | 27.1 (27A9275), selected at `/Applications/Xcode.app/Contents/Developer` |
| Simulator | iPhone 18 Pro, iOS 27.0 (24A434); iOS 27.1 also installed |
| Target physical device | iPhone 16 Pro, iOS 27.0.1 (24A446); USB pairing and enabled Developer Mode verified |
| Node / npm | 24.13.0 / 11.6.2 |
| Ruby / Bundler | Homebrew Ruby 3.3.13 / Bundler 4.0.23 |
| CocoaPods | 1.16.2; 115 pods installed, including SpvsSecurity and SpvsWifi |
| Expo / React Native / React | 58.0.17 / 0.88.0 / 19.3.0 |
| TypeScript | Updated mobile tooling to Expo's recommended 6.0.3 |
| Backend | Python 3.12.8; frozen uv dependencies; PostgreSQL 16.15 |
| Signing | Initial audit had no identity; user subsequently selected a Personal Team and an Apple Development identity is now available |

## Changes and reproducibility

- Preserved the existing backend, dashboard, Expo app, Android modules and
  security protocols. No private signing material is included.
- Retained the generated [Ruby lockfile](../mobile/Gemfile.lock) and
  [CocoaPods lockfile](../mobile/ios/Podfile.lock). Other generated native files
  remain ignored.
- Expo 58's installed CLI defaults to clearing native directories. The build
  script and npm prebuild command now pass `--no-clean` to preserve generated
  projects, lockfiles and local signing settings on subsequent runs.
- The [Mac build script](../scripts/build_mobile_macos.sh) uses a repository-local
  npm cache, selects Homebrew Ruby 3.3 when installed, installs/checks the pinned
  Bundler dependencies, and saves the complete simulator build log.
- Disabled unused iOS microphone, Face ID, motion and always-location permission
  descriptions in [Expo configuration](../mobile/app.json). Camera, foreground
  location and local-network descriptions remain. No authentication or
  attestation checks were relaxed.
- The first npm installation failed because the global npm cache contained
  root-owned entries. `--cache ../.runtime/npm-cache` resolved it without changing
  ownership of the global cache.

## Commands used

From the repository root, after installing and opening Xcode:

```sh
xcode-select -p
xcodebuild -version
xcodebuild -checkFirstLaunchStatus
xcrun simctl list runtimes
xcrun simctl list devices available
brew install ruby@3.3
npm ci --prefix mobile --cache .runtime/npm-cache --no-audit --no-fund
```

Initial CocoaPods installation:

```sh
cd mobile
export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
export BUNDLE_PATH="$PWD/../.runtime/bundle"
bundle install
CI=1 EXPO_NO_TELEMETRY=1 SPVS_DEV_HTTP=1 \
  EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  npx expo prebuild --platform ios --no-install --no-clean
cd ios
bundle exec pod install
```

Simulator build from the repository root:

```sh
CI=1 EXPO_NO_TELEMETRY=1 SPVS_DEV_HTTP=1 \
  EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  SPVS_IOS_DESTINATION='platform=iOS Simulator,name=iPhone 18 Pro,OS=27.0' \
  bash scripts/build_mobile_macos.sh ios-simulator
```

The underlying compiler command is:

```sh
cd mobile
xcodebuild -workspace ios/SPVSStudent.xcworkspace -scheme SPVSStudent \
  -configuration Debug -sdk iphonesimulator \
  -destination 'platform=iOS Simulator,name=iPhone 18 Pro,OS=27.0' \
  -derivedDataPath ../work/ios-derived CODE_SIGNING_ALLOWED=NO build
```

Logs are in `work/ios-build-workflow-final.log` and `work/ios-simulator-build.log`.
The final wrapper exited 0 and Xcode reported `BUILD SUCCEEDED`. For an incremental
build after a successful `npm ci` with the current lockfile, set
`SPVS_SKIP_NPM_CI=1` to reuse those installed dependencies. This option was used
for the final wrapper validation. Its prebuild output confirmed `reusing /ios`.
An earlier wrapper run completed Xcode successfully but hit a shell parsing
error because the script was edited while it ran; the finalized script was then
rerun successfully without concurrent edits.
The generated app is in
`work/ios-derived/Build/Products/Debug-iphonesimulator/SPVSStudent.app`.
Unsigned simulator builds do not establish device signing or Secure Enclave
behavior. Do not use `--clean` when preserving local signing configuration.

## Backend and phone networking

The existing initializer created a gitignored `.env` with fresh development
secrets; no values were printed. A new PostgreSQL cluster lives under
`.runtime/postgres`, listens on loopback only, uses SCRAM password authentication,
and contains separate `spvs` and `spvs_test` databases. Existing migrations and
demo seeding succeeded. No attendance or face enrollment was seeded.

`uv sync --project backend --frozen --python /usr/local/bin/python3.12` installed
the backend dependencies. Model downloads initially hit a missing Python CA
trust configuration. Setting `SSL_CERT_FILE` to the installed venv's
`lib/python3.12/site-packages/certifi/cacert.pem` fixed this while retaining TLS
verification. The existing model and public-reference-image download scripts
verified all pinned checksums.

The API task runs:

```sh
bash scripts/backend.sh uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The Mac's observed Wi-Fi IPv4 address is `10.0.11.85`. The gitignored
`mobile/.env` sets `EXPO_PUBLIC_API_URL=http://10.0.11.85:8000/api/v1` and
`SPVS_DEV_HTTP=1`. Metro loads it with `npm --prefix mobile start -- --lan`.
This is a development-only endpoint. Exports using this HTTP endpoint are
bundling checks, not release-ready builds; the application requires HTTPS in
release mode. Use trusted HTTPS for real student data.

The Mac successfully reached `/health` at that LAN address and `/ready` over
loopback. `/ready` reported models loaded and attestation not configured.
Phone-to-Mac reachability is still unverified. The iPhone must join the same
reachable network; campus/client isolation or a firewall may block it. Recheck
`ipconfig getifaddr en0` after changing networks, update `mobile/.env`, and restart
Metro. Never use the phone's `localhost` as the Mac's API address.

## Observed checks

| Check | Result |
| --- | --- |
| Mobile unit tests | 28 passed, including mocked platform/permission behavior |
| Mobile TypeScript | Passed with TypeScript 6.0.3 |
| Expo package compatibility | Dependencies up to date after TypeScript update |
| Dashboard unit tests | 8 passed |
| Dashboard production build | Passed |
| Android and iOS JavaScript exports | Both passed; not native Android compilation |
| Generated native configuration | Existing verification script passed for both platforms |
| Backend regression suite | 103 passed, six model tests initially skipped |
| Model-test follow-up | All six passed after verified model/sample downloads |
| Database migrations | Upgrade and schema check passed |
| Xcode simulator build | Passed: `BUILD SUCCEEDED`; final build wrapper exit 0 |
| Simulator app launch | Installed and launched (`edu.spvs.student`); Expo development launcher visible; Open prompt awaits user interaction |
| Signed physical-device build | Passed with Personal Team; installed and launched on iPhone 16 Pro after user trusted the developer |
| Genuine Apple App Attest | Not configured or tested |

Backend App Attest tests use synthetic certificates. These results do not
establish interoperability with Apple's service. Native Android compilation was
not repeated: Android SDK/adb and JDK 17 were absent at audit (only Java 8 was
found). Existing Android source is preserved. npm still reports 15 high-severity
affected package entries in the existing mobile dependency graph; no forced
Expo/React Native downgrade was applied.

The actual simulator screenshot is `work/ios-simulator-launch.png`. It shows
the development launcher and its Open prompt, not a completed student login.
Xcode emits upstream Swift/SDK modularization, nullability and build-phase
warnings; a successful build is not a warning-free build. Neither simulator
launch nor model tests establish real-camera or physical-iPhone behavior.

## Next manual gate and physical-device evidence

### Personal Team Wi-Fi capability configuration

The user removed Access Wi-Fi Information in Xcode because their Personal Team
could not provision it. The Expo plugin previously restored it unconditionally.
It now adds `com.apple.developer.networking.wifi-info` only when
`SPVS_IOS_WIFI_INFO=1`. Otherwise it removes that key, including a stale value
from an earlier supported-team build. No other capability logic or native
current-network code was changed. App Attest remains separately configured.

The local gitignored `mobile/.env` explicitly sets `SPVS_IOS_WIFI_INFO=0`.
For a supported Apple Developer Team with a matching provisioning profile, use:

```sh
cd mobile
SPVS_IOS_WIFI_INFO=1 npx expo prebuild --platform ios --no-install --no-clean
SPVS_IOS_WIFI_INFO=1 ../backend/.venv/bin/python ../scripts/verify_native_config.py
```

For this Personal Team development build, use:

```sh
cd mobile
SPVS_IOS_WIFI_INFO=0 npx expo prebuild --platform ios --no-install --no-clean
SPVS_IOS_WIFI_INFO=0 ../backend/.venv/bin/python ../scripts/verify_native_config.py
```

Both generated variants passed the native configuration checker. The opt-in
generated the Wi-Fi entitlement with value `true`; the final opt-out generated
an empty entitlement dictionary, matching the user's current Xcode configuration.
The selected team, automatic signing and bundle identifier survived prebuild.
Expo's actual introspection evaluator also verified unset, `0` and `1` modes,
including preservation of unrelated App Attest and keychain entitlement values.
These introspection inputs are configuration tests, not provider validation.
The mobile regression suite passed all 28 tests again, and CocoaPods completed
`pod install --deployment` against the retained lockfile.

The native `NEHotspotNetwork.fetchCurrent` implementation is retained. Without
the entitlement, useful current-network evidence is not expected; the existing
unavailable-evidence handling and server review/retry policy remain in force.
No synthetic Wi-Fi evidence or attestation is substituted.

The signed device build uses the selected local Xcode team:

```sh
xcodebuild -workspace mobile/ios/SPVSStudent.xcworkspace -scheme SPVSStudent \
  -configuration Debug -sdk iphoneos -destination 'generic/platform=iOS' \
  -derivedDataPath work/ios-device-derived \
  -allowProvisioningUpdates -allowProvisioningDeviceRegistration build
```

Device build output is retained at `work/ios-device-build.log`.
The build reported `BUILD SUCCEEDED`, and `codesign --verify --deep --strict`
passed on the completed app. Signed entitlements contain the application/team
identifiers and `get-task-allow`; Wi-Fi Information and App Attest are absent.
The embedded profile matches the signed app, includes the connected iPhone, and
expires at 2026-10-30 17:49:02 UTC.

`devicectl device install app` confirmed installation on the physical iPhone.
The initial launch was rejected with CoreDevice error 10002 / application
Security error 3, whose message includes a profile not explicitly trusted by the
user. Signature verification and profile/device matching passed locally. The
user then confirmed trusting the development profile. A subsequent
`devicectl device process launch` succeeded. The actual device screenshot at
`work/iphone-launch.png` shows the SPVS Student development launcher searching
for development servers, with a 4G status indicator. It does not show student
login. The Mac's API and Metro health checks still pass at the same LAN address.
The next manual step is to connect the iPhone to the Mac's reachable Wi-Fi
network, allow local-network access, and verify the API from phone Safari.
Phone-to-Mac connectivity and student flows remain unverified.

Follow Apple's [signing workflow](https://help.apple.com/xcode/mac/current/en.lproj/dev60b6fbbc7.html)
and [Developer Mode instructions](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device).
Add the Apple account in Xcode Settings, connect and unlock the iPhone over USB,
accept trust prompts, and enable Developer Mode when available. Sign in only
inside Apple's UI. Account credentials and private keys must not enter chat or Git.
Record the actual phone OS after pairing. Confirm team type and capability
availability before changing signing or enabling App Attest.

The following remain unverified on a physical iPhone:

- Student login, permission prompts, real front-camera capture, randomized
  liveness, enrollment response, attendance submission and history.
- Reduced-accuracy location, denied camera/location/local-network access,
  unavailable Wi-Fi information and interrupted-network retries.
- Secure Enclave key creation/signing and device registration; reinstall/key-loss
  behavior and administrator-approved recovery.
- Genuine App Attest registration/assertions with a supported Apple team and
  matching server trust configuration.

Retain the server's review/retry defaults. Simulator keys and synthetic tests
must not be represented as physical Secure Enclave or genuine Apple attestation.
