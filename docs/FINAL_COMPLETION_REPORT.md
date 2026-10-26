# SPVS current completion and verification report

**Checkpoint: 26 October 2026 (Asia/Kolkata).**
Application implementation: `cc8f1ddba2f1aa2e8c97f39eccb5580557e15eb5`.
Publication: [PR #5](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/5).
Artifact metadata and the source archive's FINAL_FILE_MANIFEST.txt identify the
exact snapshot without embedding the delivery commit into its own files.

## Implemented and tested

The FastAPI/PostgreSQL, React dashboard and Expo/React Native architecture remains.
Earlier Mac-native build, P-256 registration, camera-direction, photo-driven blink,
bounded tracking-recovery, retry and asynchronous Android scan fixes are retained.

The reproduced Android sign-in failure was an embedded space in the email.
The intended credentials were valid. Correcting the field produced the actual
Android home screen. The form now uses an email keyboard/autofill hints, catches
embedded whitespace before submission and translates server email/password
validation fields into clear messages without logging input.

## Current automated evidence

| Suite | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Full backend | 120 | 0 | 0 |
| Mobile | 46 | 0 | 0 |
| Dashboard | 8 | 0 | 0 |
| Native Android Wi-Fi | 10 | 0 | 0 |

**184 passed**, rerun for this checkpoint. [Dated evidence](evidence/local-2026-10-26/)
contains JUnit results and npm audits. Mobile TypeScript and dashboard production
build pass. API happy-path tests substitute vision only within tests; real-model
smoke tests are separate. JS native interfaces are mocked; native tests exercise
scan coordination/filtering, not room accuracy.

The existing Android development APK's native build/signature evidence remains
valid: this continuation changes JavaScript and documentation, not native code.
It loads the current JavaScript from Metro. It is not a standalone production
release. Historical iOS builds, browser tests and container checks retain their
original dates and are not counted as fresh phone or deployment validation.
Upstream deprecation warnings remain.

## Physical Android milestone completed

Motorola Edge 50 Neo / Android 16 / API 36 / arm64-v8a:

- Native APK installation, sign-in UI and Wi-Fi setup check observed.
- Separate Android demo account/course enrollment preserves the existing iPhone.
- P-256 device registration at 25 October 20:27:43 IST; android-hardware is a
  client storage report, not independent attestation.
- Face enrollment succeeded at 20:30:24 IST after one IMAGE_QUALITY_LOW rejection.
- Attendance at 20:33:45 IST passed face matching, liveness, device authentication
  and GPS checks. Wi-Fi was available, but no classroom AP references were configured.
  The automated decision was PENDING_REVIEW with WIFI_UNAVAILABLE.
- The student requested review. The assistant exercised the authenticated local
  demo faculty API to create an explicitly labelled hostel-test correction.
- One official PRESENT record with source CORRECTION, one resolved dispute, a
  faculty actor/reason and corresponding audit events were verified.
- The actual Android history screen showed PRESENT/CORRECTION and the original
  PENDING REVIEW attempt after the user reconnected Wi-Fi.

This was a controlled demo manual correction, not automatic classroom attendance
or a completed faculty-browser click-through. No verification policy was weakened.
The original decision is preserved. Full details and boundaries:
[Android device validation](ANDROID_DEVICE_VALIDATION_2026-10-26.md).

## Wi-Fi field scope

The user clarified the test was a hostel room with the AP outside. Two AP signals
were stronger in the corridor (-52/-67 dBm) than initially inside (-75/-89 dBm).
A repeat inside scan showed only one AP at -79 dBm. An offline rule-isolation
check with synthetic identical valid GPS accepted both initial samples at thresholds
that accepted the room. It made no attendance submission.

This establishes collection on the phone and a limitation of that setup. It does
not settle the intended classroom, whose AP is reportedly inside. Classroom AP
identities, multi-position sampling, thresholds and fresh inside/outside evaluation
are still required. No hostel references were installed as classroom references.

## iPhone and remaining boundaries

The earlier physical iPhone enrollment succeeded. Its submission passed
face/liveness/GPS and required iOS policy review; its account was not replaced.
The Personal Team build lacks Wi-Fi Information and App Attest entitlements.
Genuine Apple App Attest and Play Integrity remain unconfigured/unverified.

Remaining work includes actual-classroom automatic acceptance/rejection, broader
device/user and spoof/injection evaluation, biometric calibration, compatible
security remediation, production TLS/signing, load, backup/retention/key rotation
and institutional consent/alternative-attendance decisions.

The fresh npm audit still reports 5 high mobile package entries, zero dashboard
findings; backend vulnerability scanning remains historical. No dependency upgrade
or incompatible forced downgrade was performed.

Known UI limits: history may still show generic pending-review wording/action
after a correction, and unreachable API requests can wait without a clear timeout
indicator. WIFI_UNAVAILABLE also covers absent reference configuration. These are
documented follow-ups, not claims that scanning or manual review failed.

## Coordinated delivery

Source ZIP, project/setup PDFs, packaged Markdown, current milestone PDFs and
checksums are regenerated. The retained APK is 77,979,730 bytes, SHA-256
`9bd8032bc87b6f74fc86a2fe11897915fcd598081f514473c424294ec54cd3d6`.
Native code is unchanged; Metro serves the new sign-in JavaScript.

Packaging checks ZIP CRC, required source/evidence, each included source hash,
artifact hashes, PDF text and document links. Runtime secrets, raw BSSIDs/SSID,
precise location, private keys, databases, templates and raw screenshots/frames
are excluded. Older dated audits/records remain historical; old artifact bytes
remain in Git history. **Synchronization is not production readiness or deployment.**
