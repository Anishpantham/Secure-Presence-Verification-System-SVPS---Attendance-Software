# Current and historical test/build results

## Current local checkpoint - 27 October 2026

| Suite | Passed | Failures/errors | Skipped | Evidence |
| --- | ---: | ---: | ---: | --- |
| Backend | 146 | 0 | 0 | [JUnit](evidence/local-2026-10-27/backend-tests.xml) |
| Mobile | 64 | 0 | 0 | [JUnit](evidence/local-2026-10-27/mobile-tests.xml) |
| Dashboard | 11 | 0 | 0 | [JUnit](evidence/local-2026-10-27/dashboard-tests.xml) |
| Native Wi-Fi | 10 | 0 | 0 | [JUnit](evidence/local-2026-10-27/android-wifi-tests.xml) |

**231 local tests passed.** TypeScript, dashboard build, both JS exports,
migration/model drift, generated native configuration, Android arm64 APK/signature,
iOS simulator and signed-device builds passed. SpvsAcoustic is present in the new
APK and the iOS native compilation. No rebuilt phone installation or physical
QR/audio test was performed. See [local results](evidence/local-2026-10-27/results.json).

The upstream cloud ran three browser tests and reports 234 total. Those browser
and container checks were not rerun against the local demo database, and are
separate from the local total. Fresh npm audits report four high mobile affected
entries and zero dashboard findings; backend vulnerability scanning is historical.

Earlier C003 automatic inside attendance and the later hostel GPS rejection
precede policy v2. See [C003 validation](C003_CLASSROOM_VALIDATION_2026-10-27.md).
All further physical testing waits for explicit user readiness in the classroom.

## Prior local checkpoint - 26 October 2026

| Suite | Passed | Failures/errors | Skipped | Evidence |
| --- | ---: | ---: | ---: | --- |
| Full backend | 120 | 0 | 0 | [JUnit](evidence/local-2026-10-26/backend-tests.xml) |
| Mobile | 46 | 0 | 0 | [JUnit](evidence/local-2026-10-26/mobile-tests.xml) |
| Dashboard | 8 | 0 | 0 | [JUnit](evidence/local-2026-10-26/dashboard-tests.xml) |
| Native Wi-Fi | 10 | 0 | 0 | [JUnit](evidence/local-2026-10-26/android-wifi-tests.xml) |

**184 passed**, all rerun for this checkpoint. Mobile TypeScript and dashboard
production build passed. The APK/native build remains the verified 24 October
development host; no native code changed, and current JavaScript is served by Metro.
The physical Android demo reached manual faculty API correction, resolved dispute,
attributable audit and verified phone history. Automatic classroom approval and
faculty-browser click-through remain unverified. See [physical evidence](ANDROID_DEVICE_VALIDATION_2026-10-26.md).

Fresh npm audits: [mobile](evidence/local-2026-10-26/mobile-audit.json) has 5 high
affected package entries, [dashboard](evidence/local-2026-10-26/dashboard-audit.json)
has zero. Backend security auditing remains historical. Prior browser/container
checks and native build runs retain their original dates; repeated tests are not
added to this total. See [current verification](FINAL_COMPLETION_REPORT.md).

## Prior local checkpoint - 24 October 2026

| Suite | Passed | Failures/errors | Skipped | Evidence |
| --- | ---: | ---: | ---: | --- |
| Backend, full suite | 120 | 0 | 0 | [JUnit](evidence/local-2026-10-24/backend-tests.xml) |
| Mobile | 42 | 0 | 0 | [JUnit](evidence/local-2026-10-24/mobile-tests.xml) |
| Dashboard | 8 | 0 | 0 | [JUnit](evidence/local-2026-10-24/dashboard-tests.xml) |
| Android native Wi-Fi | 10 | 0 | 0 | [JUnit](evidence/local-2026-10-24/android-wifi-tests.xml) |

Total: **180 passed** across these four suites. The backend/mobile/dashboard
results were rerun for the audit; the native results are from the preceding
verified local Android build. Historical browser tests are excluded from this
total. Mobile TypeScript and the dashboard production build passed. Native
Android compilation and APK signature verification passed; physical Android
testing is pending. See [Android validation](ANDROID_MAC_VALIDATION.md).

iOS simulator and signed-device builds passed in the earlier local Mac run.
Physical iPhone enrollment succeeded on 24 October; an attendance submission
passed face/liveness/GPS but required review for iOS presence policy. No official
attendance record was created. See [iOS validation](IOS_MAC_VALIDATION.md).

Fresh npm audits: [mobile](evidence/local-2026-10-24/mobile-audit.json) reports
5 high affected package entries; [dashboard](evidence/local-2026-10-24/dashboard-audit.json)
reports zero. Backend vulnerability auditing was not rerun locally. Upstream
deprecation warnings and genuine provider-attestation/calibration gaps remain.

See the [full audit](LOCAL_ECOSYSTEM_REPORT_2026-10-24.md) for scope and provenance.

## Historical cloud completion run - 23 October 2026

The tables and statements in this section describe that earlier run only.

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
