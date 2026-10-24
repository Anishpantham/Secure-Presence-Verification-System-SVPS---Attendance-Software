# SPVS current completion and verification report

**Checkpoint: 25 October 2026 (Asia/Kolkata).** Application implementation:
`26b2895a83fdf8014e5a4a3cb5aa20d8af23deb7`. Delivery documentation and regenerated
artifacts extend that implementation checkpoint through
[PR #4](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/4).
Exact packaged source hashes are in FINAL_FILE_MANIFEST.txt inside the archive;
artifact metadata records the source base and generation time.

## Delivered behavior

The FastAPI/PostgreSQL, React dashboard and Expo/React Native architecture is
retained. This continuation adds validated Mac/iOS build workflows, native locks,
Personal Team compatible configuration, enrollment fixes and Android Wi-Fi recovery.

- Enrollment maps turns to the student's own left/right for unmirrored images,
  gives 700 ms to settle into prompts, and drives blink cues by completed photos
  with a vibration to reopen the eyes.
- At most two missing-landmark frames can recover, with eight tracked frames and
  the complete action sequence still required. Every frame must pass quality,
  single-face and identity checks. Thresholds, signatures, consent and replay
  protections remain.
- Typed API failures show specific missed-step guidance and the remaining retry
  window. Definitive 4xx errors discard rejected saved submissions; network/5xx
  errors can recover using the same signed request.
- Android reuses actual readings at most 15 seconds old or waits up to eight
  seconds for a successful scan broadcast. Timeout, permission loss, cancellation
  and concurrent callers are handled explicitly.
- Settings includes a local Wi-Fi setup check displaying measured AP IDs/RSSI
  without submitting attendance or automatically trusting classroom references.

## Actual validation

| Suite | Passed | Failed / skipped | Evidence date |
| --- | ---: | --- | --- |
| Full backend | 120 | 0 / 0 | 24 October |
| Mobile | 42 | 0 / 0 | 24 October |
| Dashboard | 8 | 0 / 0 | 24 October |
| Native Android Wi-Fi | 10 | 0 / 0 | 24 October |

**180 passing tests**. Reports are in [dated evidence](evidence/local-2026-10-24/).
Backend API happy paths substitute vision only in tests; real-model smoke tests
separately execute YuNet, SFace and MediaPipe. Mobile OS/native interfaces are
mocked in JS tests. Native tests cover scan coordination/filtering, not radio quality.

Mobile TypeScript, dashboard production build, Android debug compilation and APK
signature verification passed. The APK is an arm64-v8a development client requiring
Metro/API connectivity. Simulator and signed-device iOS builds passed locally.
Earlier browser/container tests remain historical and are not fresh validation
of this checkpoint. Upstream deprecation warnings remain.

## Physical-device evidence

The iPhone logged in, registered a native P-256 key and enrolled a face. The user
confirmed improved enrollment usability; the database records enrollment on
24 October at 14:37:27 IST. Attendance at 14:43:49 IST passed face/liveness/GPS,
then returned `PENDING_REVIEW` for `IOS_PRESENCE_REVIEW_REQUIRED`.
No official attendance record was created.

Reported Secure Enclave storage is not independent hardware attestation. The
Personal Team build lacks Wi-Fi Information and App Attest entitlements and
supplied no Wi-Fi evidence. No classroom AP references are configured. The iOS
review policy requires review even if the connected BSSID matches.

**Android physical testing is pending until the user connects the phone.**
No Android enrollment, scan readings, classroom acceptance/corridor rejection or
hardware-attestation outcome is claimed.

## Artifact currency

Current source ZIP, project/setup PDFs, delivery/verification Markdown and
checksums in `release/final` are regenerated for this checkpoint. The actual
local Mac Android APK is 77,979,730 bytes, SHA-256:
`9bd8032bc87b6f74fc86a2fe11897915fcd598081f514473c424294ec54cd3d6`.

The archive includes new code/tests, dated evidence, status reports and both
Ruby/CocoaPods locks. Environment secrets, native private signing material,
databases, caches and generated projects (except the tracked CocoaPods lock) are
excluded. Packaging verifies ZIP CRC/members/source hashes and PDF text extraction.

The [pre-publication audit](LOCAL_ECOSYSTEM_REPORT_2026-10-24.md) and
[historical cloud report](HISTORICAL_CLOUD_COMPLETION_2026-10-23.md) remain dated
records. Their earlier Git gaps and test counts do not describe this delivery.
Old artifact bytes remain in Git history.

## Remaining release gates

- Physical Android tests and confirmed AP references; compare classroom, corridor
  and adjacent-room readings while keeping GPS eligibility constant.
- Broader camera usability, false-match/non-match, spoof/injection, accessibility
  and population calibration evaluations with measured uncertainty.
- Supported iOS network provisioning, genuine App Attest interoperability and
  the unfinished Google Play Integrity provider integration.
- The 24 October npm audit has 5 high mobile affected entries associated with
  node-forge/Zod and propagation, and zero dashboard findings. Backend scanning
  is historical. No incompatible forced downgrade was applied.
- Production TLS/signing, least-privilege operations, retention/backups/key
  rotation, load testing and institution-approved biometric/alternative policies.

**Source synchronization and passing tests do not establish production readiness.**
See [CURRENT_STATUS.md](CURRENT_STATUS.md) for the current entry point.
