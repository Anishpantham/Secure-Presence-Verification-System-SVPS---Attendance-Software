# Physical-device validation: QR + audible acoustic attendance

**Status: not performed for this feature.** Earlier SPVS hardware reports concern
the older flow. Automated PCM tests, JS exports and Android compilation do not
establish that a laptop-to-phone acoustic channel works in a real classroom.

## Setup on MacBook Air M4

Use a native ARM64 terminal, current Xcode/command-line tools, Docker Desktop,
Node 24 LTS, Python 3.12 + uv, Android Studio/SDK, JDK 17, and the repository's
Bundler/CocoaPods setup. Preserve your existing uncommitted work before switching.
From your existing repository checkout:

```sh
git fetch origin
git switch --track origin/feature/acoustic-dynamic-qr-verification
# If the local branch already exists instead:
# git switch feature/acoustic-dynamic-qr-verification
# git pull --ff-only
make setup
make db
make migrate
make seed
make build
```

Keep development services in separate terminals:

```sh
make api
make dashboard
```

Run automated checks (the test database name must end `_test`):

```sh
docker compose exec -T db createdb -U spvs spvs_test  # once; skip if it exists
make test
(cd mobile && npm run export)
(cd dashboard && npx playwright install chromium && npx playwright test)
```

For a LAN HTTP development demo only, replace the address below with your Mac's
reachable Wi-Fi address. The phone and Mac must reach each other; campus client
isolation can block this. Use trusted HTTPS for release builds.

```sh
export EXPO_PUBLIC_API_URL="http://$(ipconfig getifaddr en0):8000/api/v1"
export SPVS_DEV_HTTP=1
bash scripts/build_mobile_macos.sh ios-simulator
bash scripts/build_mobile_macos.sh ios-device
# Xcode opens: choose your Apple team and connected iPhone 16 Pro, then Run.
# Separate terminal with the same environment:
(cd mobile && npm start)
```

For Motorola Edge 50 Neo, enable USB debugging and authorize the Mac:

```sh
export EXPO_PUBLIC_API_URL="http://$(ipconfig getifaddr en0):8000/api/v1"
export SPVS_DEV_HTTP=1
export SPVS_ANDROID_ARCHITECTURES=arm64-v8a
bash scripts/build_mobile_macos.sh android
adb devices -l
adb install -r mobile/android/app/build/outputs/apk/debug/app-debug.apk
(cd mobile && npm start)
```

These commands must create **new** native builds containing `SpvsAcoustic`.
The historical release APK does not include this module. Do not commit local
`.env`, private keys, profiles, databases, recordings or biometric material.
If provisioning changes, follow the existing iOS guide. Connected-Wi-Fi entitlement
and App Attest remain separate opt-ins; nearby Wi-Fi scanning is never available on iOS.

## Baseline run

1. Use consented test accounts, one per device. Confirm enrollment and native key
   registration; configure the actual classroom geofence. Keep mandatory checks on.
   Set iOS policy to `dynamic` through the audited admin policy editor. Keep Android
   Wi-Fi requirements explicit; collect real references if Wi-Fi is required.
2. Open the faculty session page. Start challenges; verify a new QR every five
   seconds and automatic hiding at expiry or loss of connection. Confirm browser
   speakers work at comfortable volume before students start.
3. Select session on the phone, scan QR, tap Listen, and read the eight-character
   attempt label to faculty. Play that matching queue entry. Stay foreground;
   disconnect headphones/Bluetooth routing. Only then complete face/liveness/GPS.
4. Confirm server PRESENT only after every mandatory gate passes. Confirm one
   official record and one final attempt even when retrying a lost final response.
5. Deny microphone/camera, then use Finish attempt & request faculty review.
   Confirm PENDING_REVIEW, identity NOT_COMPLETED, and no automatic official record.
   Exercise dispute, reasoned faculty correction and resolution; retain original
   attempt and correction provenance. Do not call a manual correction an automatic pass.

## Measurement matrix

Run every row on **iPhone 16 Pro** and **Motorola Edge 50 Neo**. Record OS/build,
phone orientation/case, laptop/speaker model, browser, volume, distance, ambient
condition, network RTT, attempt ID, decoder outcome, server reason, and latency.
Collect at least 20 trials per ordinary seating/ambient combination; retain failures.
Use anonymous location labels instead of exact personal coordinates or identifiers.

| Condition | Procedure and expected interpretation |
|---|---|
| Front/middle/back, corners, obstructed seats | Measure decode success and latency; failed capture never auto-passes |
| Quiet and loud classroom | Speech, fans and ordinary classroom noise; vary safe volume, never discomfort |
| Doorway, corridor, adjacent room (door open/closed) | Measure sound leakage; successful decode outside is possible and is a limitation |
| Poor QR lighting, glare, distance | Exercise torch, rescan, rotation overlap and expired screenshot rejection |
| Recorded audio | Old recording must fail in a fresh attempt; current recording replay within deadline may succeed and must be reported |
| Live QR sharing | Share a current screenshot; QR alone must never suffice; sharing within ten seconds may redeem QR |
| Real-time QR + audio relay | Consenting tester relays both; record success/latency without claiming relay resistance |
| Simultaneous listeners | Queue different attempt tags; each phone ignores the other's frame; two faculty tabs cannot overlap issuance |
| Camera/mic denied or revoked | Clear guidance, no automatic pass, bounded retry/review; restore permissions in Settings |
| Call, lock screen, background, Bluetooth route | Capture stops or fails; no fabricated success, no lingering recording indicator |
| Network disabled/delayed/dropped acknowledgement | Exact retries recover accepted evidence; late answers fail; final submission is idempotent |
| Session closed or display stopped/restarted | Pending and prior verified proofs cannot produce new automatic attendance |
| GPS inaccurate/outside/mock, wrong face, failed liveness, revoked device | Valid QR/audio cannot override the failing mandatory gate |
| VoiceOver/TalkBack and audio inaccessible | Controls are identifiable; obtain faculty review without requiring inaccessible audio |
| Restart app midway / exhaust attempt budget | No automatic attendance; bounded attempts and review remain enforceable |

Do not upload recordings by default. If an approved acoustic study genuinely needs
recordings, obtain specific consent, use separate secure storage and a deletion
schedule; the application itself deliberately has no raw-audio upload route.

## Release gate and result sheet

Define institutional thresholds **before** collecting results (in-room completion
rate, latency distribution, acceptable leakage/relay risk, review burden). Do not
select thresholds just to fit observed results. Report counts, median/p95 latency,
all reason codes, failures and network conditions separately for both phones.

For each trial: `device | OS | build SHA | scenario | seat label | attempt ID |
QR result | audio result | end-to-end latency | final state | reason | review source`.
Mark native Xcode compilation, installation, permission behavior, real audio
interoperability and end-to-end hardware attendance separately. Any unperformed
item stays **NOT TESTED**. Physical leakage or real-time relay success must remain
in the final limitations report, even when every automated test passes.
