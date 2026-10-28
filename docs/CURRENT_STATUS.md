# Current SPVS status

Checkpoint opened 28 October 2026 (Asia/Kolkata). This page supersedes old status
claims; dated historical reports retain their original scope.

| Area | Status and evidence |
| --- | --- |
| Implementation | Policy v2 QR/audio plus identity/device/GPS/platform rules implemented |
| Database | Fresh read-only inspection: spvs_recovery, head 9bd32a88f101, 4 users, 2 records |
| Recovery | User reports restoration from private pre-QR backup, migration and successful logins |
| Android physical | User-reported login, QR, audio, face and liveness passed; hostel attempt rejected |
| iOS physical | User-reported installation/login/QR/audio passed; Outside geofence |
| Latest iOS face/liveness | Not independently verified; older 24 October evidence cannot validate this trial |
| C003 positive policy-v2 test | Manual verification required |
| Android classroom Wi-Fi / iOS classroom policy | Manual verification required |
| Approved v2 record and faculty synchronization | Manual verification required |
| App Attest / integrity | Implemented boundary and synthetic checks; genuine provider verification not established |
| Fresh automation | See exact executed counts and exit codes in TEST_RESULTS.md |
| Release readiness | Academic demonstration partially verified; production gates remain open |

The earlier C003 automatic record predates policy v2. A hostel geofence rejection
does not isolate Wi-Fi and does not demonstrate legitimate in-classroom approval.
No physical phone interaction was performed by the agent during this audit.

Read [final verification](../SPVS_FINAL_VERIFICATION_REPORT.md),
[test evidence](TEST_RESULTS.md), [recovery](../SPVS_DATABASE_RECOVERY_REPORT.md),
[audit](REPOSITORY_AUDIT_2026-10-28.md) and [completion index](PROJECT_COMPLETION_STATUS.md).
