# Evaluation checklist

Status labels: **Implemented**, **Automated-test passed**, **Physical-device passed**,
**Physically rejected as expected**, **Not yet verified**, **Failed**. Physical passes
reported by the user must retain that attribution. A build is not a physical pass.

- [x] Inspect Git state; preserve local lock/APK/settings/environment backup.
- [x] Inspect recovered schema and aggregate counts without resetting data.
- [x] Separate current and historical evidence; update architecture/API/platform guides.
- [x] Run available automated checks and report results, failures and constraints.
- [x] Record user-reported Android QR/audio/identity and hostel rejection.
- [x] Record user-reported iOS QR/audio and outside-geofence rejection.
- [ ] Confirm current iOS face/liveness with redacted evidence.
- [ ] Complete current-policy legitimate Android attendance inside C003.
- [ ] Verify actual C003 Android Wi-Fi, including independent near-door/adjacent-room samples.
- [ ] Validate unchanged iOS classroom policy and eligible attendance decision.
- [ ] Confirm automatic official record creation and faculty dashboard synchronization.
- [ ] Verify genuine App Attest registration/assertion on the physical iPhone.
- [ ] Validate relay/leakage, rooted/emulator, spoofing, accessibility and load scenarios.
- [ ] Resolve compatible dependency security updates and production operational gates.
- [ ] Fill institution, student, supervisor and semester fields in the academic report.
- [ ] Obtain explicit merge approval; review checks and merge only afterward.

For every physical case record: objective; OS/app build; session policy version;
procedure; expected and actual decision/reasons; timestamp/operator; sanitized evidence;
status; limitations and follow-up. Keep private raw evidence outside Git.
