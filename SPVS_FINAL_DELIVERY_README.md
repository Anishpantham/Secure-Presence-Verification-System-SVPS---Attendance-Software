# SPVS synchronized delivery - 27 October 2026

This package incorporates upstream dynamic QR/acoustic verification and its local
Mac integration. Read [current status](docs/CURRENT_STATUS.md),
[verification](docs/FINAL_COMPLETION_REPORT.md), and
[the physical test plan](docs/ACOUSTIC_DEVICE_VALIDATION.md).
Publication: [PR #7](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/7).

- `SPVS_FINAL_COMPLETE_PROJECT.zip`: current source, migration, native locks,
  models, docs and sanitized evidence under `spvs-root`.
- `SPVS_FINAL_PROJECT_REPORT.pdf`: regenerated design/verification report,
  including QR/audio protocol, runtime integration and C003 scope.
- `SPVS_FINAL_SETUP_AND_DEMO_GUIDE.pdf`: current setup and physical-test guide.
- `SPVS_FINAL_VERIFICATION_REPORT.md`: current results and boundaries.
- `SPVS_ANDROID_DEBUG.apk`: newly rebuilt arm64 development client containing
  SpvsAcoustic; Metro/API connectivity and runtime microphone permission required.
- `artifact-checks.json`: generation/source-base metadata, CRC/member/PDF checks
  and SHA-256 values. Exact included hashes are in the ZIP's source manifest.

Old phone installs need replacement before new attendance can pass QR/audio.
The new signed iPhone app is local build output, not a distributed production IPA.
No physical QR/audio test was started. Earlier classroom/hostel trials predate
policy v2 and retain their original meanings. Secrets, backups/database data,
private keys, exact coordinates, router identifiers and biometrics are excluded.
