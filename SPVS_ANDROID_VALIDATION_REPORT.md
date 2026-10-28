# SPVS Android validation report

Checkpoint opened 28 October 2026; recorded 2026-10-28T23:56:47.529397+05:30.

## Objective

Separate native/automated validation from observed physical attendance outcomes.

## Environment and procedure

User-reported physical device: Motorola Edge 50 Neo. Historical report supplied in the audit task; exact OS/build/time for that trial was not supplied. Student logged in, completed QR/audio and identity, and submitted from the hostel. Agent separately ran mobile tests, TypeScript/export, Gradle arm64 debug build and fresh native Wi-Fi unit tests on macOS.

## Expected and actual outcomes / evidence / status

| Case / expected | Actual | Evidence | Status |
| --- | --- | --- | --- |
| API connection and student login | Succeeded | User task narrative | Physical-device passed (user-reported) |
| Rotating QR and acoustic | Succeeded | User task narrative | Physical-device passed (user-reported) |
| Face and temporal liveness | Succeeded | User task narrative | Physical-device passed (user-reported) |
| Reject hostel attendance | Not approved, outside classroom | User task narrative | Physically rejected as expected |
| Native build and 10 Wi-Fi tests | Build succeeded; 10 passed | Fresh [ledger](docs/TEST_RESULTS.md) | Automated-test passed |
| C003 legitimate v2 approval/Wi-Fi | No fresh classroom evidence | [Earlier C003 report](docs/C003_CLASSROOM_VALIDATION_2026-10-27.md) predates v2 | Not yet verified |
| Approved record and faculty sync | Pending current trial | No current-policy positive evidence | Not yet verified |

## Known limitations

No agent phone interaction occurred. Hostel GPS rejection does not independently verify classroom Wi-Fi. Prior C003 PRESENT is historical and cannot validate current QR/audio approval. No measured accuracy or rooted-device resistance is claimed.

## Follow-up actions

Manual verification required inside C003: [demo guide](docs/EVALUATION_DEMO_GUIDE.md). Collect build/policy metadata and sanitized record/dashboard evidence; preserve classroom calibration.
