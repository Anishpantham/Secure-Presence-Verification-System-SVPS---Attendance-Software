# Current SPVS status

Last audited: **24 October 2026, Asia/Kolkata**. This is the entry point for the
local Mac continuation; older documents labelled "final" are historical snapshots.

Read the [complete local ecosystem and GitHub report](LOCAL_ECOSYSTEM_REPORT_2026-10-24.md)
or its [PDF](reports/LOCAL_ECOSYSTEM_REPORT_2026-10-24.pdf).

| Area | Current verified state |
| --- | --- |
| GitHub `main` | `3591220`; fetched and checked through GitHub during this audit |
| Local working branch | `spvs/ios-native-completion`, HEAD `ac97c60`; 4 commits ahead, 0 behind remote main |
| Uncommitted work | Enrollment fixes, Android scan fix, tests, new APK and documentation; see [exact inventory](evidence/local-2026-10-24/repository-state.json) |
| Remote working branch | Not published; no upstream configured; no PR for this continuation |
| Automated checks | 120 backend + 42 mobile + 8 dashboard + 10 native Wi-Fi tests passed |
| iPhone | Native build/login/device registration, face enrollment, one attendance attempt observed |
| Attendance outcome | Pending review; no official attendance record; GPS and liveness passed, Wi-Fi unavailable |
| Android | New arm64 development APK builds and verifies; no physical phone connected/tested |
| Wi-Fi | Android collection corrected; classroom references and physical validation still missing |
| Attestation | Genuine Apple App Attest and Play Integrity remain unconfigured/unverified |
| Dependency audit | Current npm: 5 high mobile entries, 0 dashboard; backend scan historical |
| Production | Not validated for institutional deployment |

Build evidence: [iOS](IOS_MAC_VALIDATION.md), [Android](ANDROID_MAC_VALIDATION.md).
Current tests: [TEST_RESULTS.md](TEST_RESULTS.md).
Delivery state: [release/final/CURRENT_STATUS.md](../release/final/CURRENT_STATUS.md).
Runtime changes in the local database are separate from source control; cloning
GitHub does not copy local accounts, device registrations, biometric templates,
attendance attempts, classroom configuration or secrets.
