# SPVS synchronized delivery - 26 October 2026

This delivery contains the Mac continuation and refreshed documentation.
Read [current status](../../docs/CURRENT_STATUS.md) and
[verification](../../docs/FINAL_COMPLETION_REPORT.md). Publication:
[PR #5](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/5).

- `SPVS_FINAL_COMPLETE_PROJECT.zip`: current source, locks, models, docs and test
  evidence under `spvs-root`. Follow its README and setup guide.
- `SPVS_FINAL_PROJECT_REPORT.pdf`: regenerated project/design/verification report.
- `SPVS_FINAL_SETUP_AND_DEMO_GUIDE.pdf`: regenerated setup/demo guide.
- `SPVS_FINAL_VERIFICATION_REPORT.md`: current validation and remaining gates.
- `SPVS_ANDROID_DEBUG.apk`: genuine arm64 development build with corrected Wi-Fi
  scanning, requiring Metro and a reachable API. Native code is unchanged; the
  current sign-in JavaScript is served by Metro.
- `artifact-checks.json`: generation metadata, CRC/member/PDF checks, source-base
  commit and SHA-256 hashes. The ZIP includes its exact source file manifest.

Physical iPhone enrollment and pending-review submission were observed. The Android
hostel demo now completes registration, enrollment, submission, manual faculty API
correction, dispute resolution and phone history. Actual classroom automatic
acceptance/rejection remains pending.
Attestation, calibration and production readiness remain unverified. Secrets,
signing keys, databases and biometric data are excluded. Prior artifacts remain
recoverable from Git history.
