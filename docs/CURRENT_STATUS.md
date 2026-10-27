# Current SPVS status

Checkpoint: **27 October 2026, Asia/Kolkata**.
Publication: [PR #7](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/7),
building on the upstream QR/acoustic [PR #6](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/6).
The PR/Git refs are authoritative for current publication state.

Read [runtime integration](LOCAL_RUNTIME_UPDATE_2026-10-27.md),
[C003 observations](C003_CLASSROOM_VALIDATION_2026-10-27.md),
[current verification](FINAL_COMPLETION_REPORT.md), and
[synchronization](REPOSITORY_SYNC_2026-10-27.md).

| Area | Current state |
| --- | --- |
| Integration checkpoint | `0fc235f916fb662db71c298091255ec10f0917f6`, based on upstream main `404eed8` |
| New attendance policy | Mandatory rotating QR + acoustic proof, alongside existing identity/device/GPS/platform-presence gates |
| Local database | Backed up privately; migrated to `9bd32a88f101`; existing counts and records preserved; no schema drift |
| Services | API/dashboard restarted; health/readiness and new presence route verified |
| Local automated tests | 146 backend + 64 mobile + 11 dashboard + 10 native Wi-Fi = 231 passed |
| Separate upstream evidence | 3 browser tests passed in cloud; not rerun against the live local demo database |
| Native builds | New Android arm64 APK, iOS simulator and signed-device app built with SpvsAcoustic; signatures/configuration checked |
| Device installation / new physical tests | Not performed; wait for explicit user readiness in the classroom |
| C003 configuration | Separate classroom, 50 m radius, two provisional 5 GHz references at -70 dBm; one of two matches suffices under existing rule |
| Earlier C003 inside trial | Automatic PRESENT / VERIFICATION; Wi-Fi ratio 0.5; pre-v2 flow |
| Later distance trial | User-confirmed hostel attempt rejected OUTSIDE_GEOFENCE at reported 151.1 m; Wi-Fi was not evaluated |
| Near-door validation | Calibration scan collected with door closed; fresh Wi-Fi-specific attendance comparison not completed |
| Earlier Android demo | Registration/enrollment, pending submission, manual CORRECTION, resolved dispute and phone history observed |
| iOS policy | Local review retained; dynamic requires a separate audited choice; App Attest remains unconfigured |
| Fresh npm audit | 4 high mobile affected entries, zero dashboard; backend vulnerability scan historical |
| Production | Real QR/audio interoperability, leakage/relay, calibration and operational release gates remain open |

Earlier dated reports describe their original checkpoints. Neither the old
automatic C003 result nor native compilation proves physical QR/audio success.
The old installed apps must be updated before the next trial. No physical test,
session challenge or audible playback was started during this synchronization.

Printable records: [runtime PDF](reports/LOCAL_RUNTIME_UPDATE_2026-10-27.pdf),
[C003 PDF](reports/C003_CLASSROOM_VALIDATION_2026-10-27.pdf),
[sync PDF](reports/REPOSITORY_SYNC_2026-10-27.pdf).
See [test results](TEST_RESULTS.md), [physical plan](ACOUSTIC_DEVICE_VALIDATION.md),
and [release inventory](../release/final/CURRENT_STATUS.md).

Git publication excludes private backup/database data, credentials, signing keys,
raw network identifiers, exact coordinates, templates, frames/audio and raw UI
captures. It does not deploy a live cloud service or replicate the local database.
