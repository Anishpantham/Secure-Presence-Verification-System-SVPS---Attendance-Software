# Delivery directory status - 24 October 2026

This directory contains files from **two different checkpoints**.

- [SPVS_ANDROID_DEBUG.apk](SPVS_ANDROID_DEBUG.apk) is the new local Mac Android
  build, 77,979,730 bytes, arm64-v8a, debug signed, requiring Metro and a reachable
  API. SHA-256: `9bd8032bc87b6f74fc86a2fe11897915fcd598081f514473c424294ec54cd3d6`.
  It includes the awaited Wi-Fi scan implementation. Physical Android testing is pending.
- The source ZIP, the two PDFs and the two `SPVS_FINAL_*.md` files are preserved
  **23 October historical deliverables**. They have not been regenerated from
  the local Mac work. Their integrity is valid, but their contents are older.
- [artifact-checks.json](artifact-checks.json) now records the current APK hash
  while retaining the original ZIP/PDF validation results. Those results do not
  establish that the old source ZIP contains the new APK's source.

Use the [current ecosystem report](../../docs/LOCAL_ECOSYSTEM_REPORT_2026-10-24.md)
and its [PDF](../../docs/reports/LOCAL_ECOSYSTEM_REPORT_2026-10-24.pdf) for the local
state. Do not distribute this folder as a single fully synchronized release.
The old APK remains recoverable from Git history; its working-copy bytes were
replaced by the successful 24 October build. A coordinated release package must
be regenerated and reviewed after the pending source changes are checkpointed.
