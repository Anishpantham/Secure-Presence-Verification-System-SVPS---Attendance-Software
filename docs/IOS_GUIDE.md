# iOS implementation and device guide

## Prerequisites and build

Use macOS, Xcode and its selected command-line tools, Node 22.12+, a connected
iPhone with Developer Mode and a provisioning team. The user reports successful
Homebrew CocoaPods installation and native Expo/Xcode installation on iPhone 16 Pro.
For a new machine, install Homebrew CocoaPods (`brew install cocoapods`), then
`pod --version`. The repository also supplies a locked Gemfile/Bundler workflow;
use its Homebrew Ruby instructions when reproducing the historical builds.

```sh
cd mobile
npm ci
npm run prebuild
cd ios
pod install
```

Open `mobile/ios/SPVSStudent.xcworkspace` in Xcode, select SPVSStudent, choose
your Apple team under Signing & Capabilities, choose the connected iPhone and Run.
Alternatively use `npm run ios` from mobile after signing is configured.
Run `npm start` separately for the development client. Preserve local Podfile.lock
changes; do not regenerate or discard them merely to match older reports.
Simulator compilation does not establish physical microphone/camera operation.
Production distribution requires suitable signing/provisioning and HTTPS.

## Network, permissions and native boundaries

Set EXPO_PUBLIC_API_URL to the Mac's reachable LAN address plus `/api/v1`.
Simulator localhost is not a physical iPhone's localhost. Permit Local Network,
Camera, Microphone, and precise While Using location. Development-only
SPVS_DEV_HTTP=1 enables ATS allowances at prebuild; remove it for distribution.
Audio is decoded in memory by SpvsAcoustic. Native P-256 keys require Secure Enclave
on physical iPhones; simulator uses device-only Keychain. SecureStore retains tokens.

iOS provides no Android-style nearby Wi-Fi RSSI scan. A permitted current BSSID
requires a supported team/profile and opt-in SPVS_IOS_WIFI_INFO=1. Personal Team
provisioning can fail for this entitlement; leave it disabled when unsupported.
Current BSSID is not proof of multi-AP presence. The server offers review, retry,
or explicitly selected dynamic policy. Dynamic requires QR/audio plus all identity,
device and GPS gates; global attestation requirements still apply.

App Attest needs native entitlement/environment, server app ID, independently pinned
Apple root and genuine registration/assertion verification. Login or successful
signing does not establish App Attest. Do not enable capabilities just to claim success.

## Validation and troubleshooting

Follow [demo steps](EVALUATION_DEMO_GUIDE.md). The latest reported iPhone test passed
login, QR and acoustic then returned Outside geofence. Face/liveness for this trial
are not independently confirmed. [Older iOS evidence](IOS_MAC_VALIDATION.md) records
24 October enrollment and liveness with PENDING_REVIEW; it predates policy v2.
Current classroom acceptance, record creation, faculty synchronization and genuine
App Attest remain manual verification required.

Pod errors: verify active Ruby/pod paths and open the workspace rather than project.
Signing errors: check team, bundle ID, device trust and supported capabilities;
do not publish profiles or signing keys. If Metro cannot connect, recheck LAN URL,
Local Network permission and firewall. See [troubleshooting](TROUBLESHOOTING.md).
