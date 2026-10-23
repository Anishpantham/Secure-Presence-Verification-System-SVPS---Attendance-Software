# Final test and build results

The table below is the historical completion run. See the separate
[2026-10-23 Mac validation record](IOS_MAC_VALIDATION.md) for current local results;
the earlier browser and Android-native results were not rerun as part of that record.

| Suite | Passed | Failures/errors | Skipped |
|---|---:|---:|---:|
| Backend | 109 | 0 | 0 |
| Mobile | 28 | 0 | 0 |
| Dashboard | 8 | 0 | 0 |
| Browser | 3 | 0 | 0 |

Total: **148 passed**. See FINAL_COMPLETION_REPORT.md for test boundaries, commands and intermediate failures. Baseline evidence is retained separately.

| Capability | Observed status |
|---|---|
| Android debug APK | PASS: genuine Gradle assembleDebug, arm64-v8a; debug signed, development client; physical-device testing NOT RUN |
| Android/iOS JS export | PASS: separate platform exports; final combined export in evidence |
| iOS native project | PASS: Expo prebuild, camera/location/privacy settings, local podspec/autolinking and static configuration checks |
| iOS native compilation / simulator / IPA | NOT RUN: Linux host; no macOS/Xcode or Apple signing identity |
| PostgreSQL migrations | PASS: fresh upgrade, check, full downgrade, re-upgrade, check on isolated PostgreSQL 16 database |
| Backend and dashboard containers | PASS: both images built and used for real browser/API tests |
| Physical Android / physical iPhone | NOT TESTED |
| Apple App Attest | Synthetic verifier/counter tests passed; genuine provider/device verification UNVERIFIED |
| Google Play Integrity | NOT CONFIGURED; fail-closed boundary only |
| Biometric calibration | NOT PERFORMED; six real-model smoke cases are not accuracy metrics |

No physical Android/iPhone, iOS simulator, Xcode or genuine provider-attestation result is claimed. Synthetic API/sensor/certificate inputs and mocked React Native components are identified in their test modules.
