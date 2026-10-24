# SPVS final delivery

**Historical delivery inventory.** The local release folder now contains a newer
Android APK alongside these older ZIP/PDF documents. See
[current artifact status](release/final/CURRENT_STATUS.md) and
[the local ecosystem audit](docs/LOCAL_ECOSYSTEM_REPORT_2026-10-24.md).

- SPVS_FINAL_COMPLETE_PROJECT.zip: existing architecture extended with cross-platform source, locks, migrations, native modules, models, documentation and actual test evidence. Extract spvs-root and follow docs/SETUP_AND_DEMO_GUIDE.md.
- SPVS_FINAL_PROJECT_REPORT.pdf: updated academic report and cross-platform/security/verification chapters.
- SPVS_FINAL_SETUP_AND_DEMO_GUIDE.pdf: Apple Silicon, Android Studio, Xcode, development builds, EAS/TestFlight and honest demonstration procedure.
- SPVS_FINAL_VERIFICATION_REPORT.md: exact automated/native outcomes, unresolved advisories and remaining hardware/provider requirements.
- SPVS_ANDROID_DEBUG.apk: included only if genuine assembleDebug succeeded. It is an arm64 development client requiring Metro/API configuration, not a production release or physical-device verification.

No IPA is supplied without a real signed Xcode/EAS build. Institutional production readiness is not established; read the verification report before using real student data. Previous release files remain unchanged. RELEASE_CHECKPOINT.md records branch/commit/PR. artifact-checks.json records CRC/readability checks and SHA-256 values.
