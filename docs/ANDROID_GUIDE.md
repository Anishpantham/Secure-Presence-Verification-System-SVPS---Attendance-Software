# Android implementation and device guide

## Prerequisites and configuration

Use Node 22.12+ (24 recommended), the locked npm dependencies, Android Studio/SDK,
JDK 17 and a USB-debugging-enabled phone. Install `npm ci` in mobile. Set the private
mobile environment EXPO_PUBLIC_API_URL to a reachable API ending `/api/v1`.
An emulator uses `10.0.2.2`; a physical phone needs the Mac's reachable LAN address.
Restart Metro after address changes. Development HTTP requires SPVS_DEV_HTTP=1
at prebuild; release JavaScript requires HTTPS regardless of native HTTP settings.

```sh
cd mobile
npm run android
npm start
```

The first command builds/installs a native development client; Metro runs separately.
Expo Go lacks SpvsSecurity, SpvsWifi and SpvsAcoustic. A debug APK is not a signed
production release. The helper `scripts/build_mobile_macos.sh android` copies an
APK into release/final; preserve an existing locally modified APK before using it.
For build-only validation use Gradle assembleDebug in the generated Android project.

## Native behavior

Camera permission supports QR and consented face capture. RECORD_AUDIO enables
bounded foreground PCM capture for the acoustic decoder; samples remain transient.
Fine/precise location and enabled location services support GPS and Wi-Fi scans.
Wi-Fi state/change permissions are declared. Android throttles scans: an unavailable
or stale scan is reported as unavailable, never replaced by synthetic readings.
Native P-256 keys remain in Android Keystore; hardware backing metadata is reported,
not server-attested. Tokens/key metadata use SecureStore. Reinstallation/key loss
requires administrator-approved reset rather than silently replacing device binding.

## Physical test procedure

Log in as an enrolled student, register only if necessary, and enroll with consent.
Faculty selects the real C003 room and starts a fresh session/challenges. Scan QR,
tap Listen, and ask faculty to play the matching attempt. Keep the app foreground,
disconnect headphones, then follow face/liveness prompts and allow fresh GPS/Wi-Fi.
Record decision/reasons, policy version, app build and whether an official record
appears. Redact identity, coordinates and raw radio identifiers from shared evidence.

The user reports that Motorola Edge 50 Neo passed login, QR, sound, face and
liveness, then rejected a hostel attempt. Current-policy C003 approval, classroom
Wi-Fi contribution, record creation and dashboard synchronization remain pending.
See [Android report](../SPVS_ANDROID_VALIDATION_REPORT.md).

## Troubleshooting

Missing module: rebuild the native client after module/permission changes.
Wi-Fi unavailable: grant precise location, enable location/Wi-Fi and wait for scan
throttling; do not change classroom fingerprints to force a pass. API unreachable:
verify shared network, local firewall, host binding and phone-reachable URL.
Use [the common troubleshooting guide](TROUBLESHOOTING.md) for capture and expiry.
