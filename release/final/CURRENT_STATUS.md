> Historical artifact snapshot. Current audit: [verification](../../SPVS_FINAL_VERIFICATION_REPORT.md), [index](../../docs/PROJECT_COMPLETION_STATUS.md). Existing binary/archive contents are retained and do not contain the current documentation refresh.

# Delivery status - 27 October 2026

Current source ZIP, project/setup PDFs, packaged Markdown and checksums include
the QR/acoustic update, local migration/native build evidence, and corrected C003
trial interpretation. Publication:
[PR #7](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/7).
Integration source: `0fc235f916fb662db71c298091255ec10f0917f6`.
The live PR identifies publication; the source manifest identifies exact content.

[SPVS_ANDROID_DEBUG.apk](SPVS_ANDROID_DEBUG.apk): 78,138,028 bytes, arm64-v8a,
debug signed, includes SpvsAcoustic, requires Metro/API and microphone permission.
SHA-256: `6cd0d397cccbbc42f6033c9a98eeab5a7c0d2f3f3d312b9dfdef72c607ab35c2`.

The former APK lacked the native microphone module and is superseded.
Xcode simulator and signed-device builds passed locally, without installing or
launching the rebuilt apps on phones. Physical QR/audio validation waits for the user.

See [checksums](artifact-checks.json), [verification](SPVS_FINAL_VERIFICATION_REPORT.md),
[runtime update](../../docs/LOCAL_RUNTIME_UPDATE_2026-10-27.md) and
[C003 observations](../../docs/C003_CLASSROOM_VALIDATION_2026-10-27.md).
Prior artifacts remain in Git history. This is not a production release or a
live cloud deployment.
