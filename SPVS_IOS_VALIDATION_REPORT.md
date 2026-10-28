# SPVS iOS validation report

Checkpoint opened 28 October 2026; recorded 2026-10-28T23:56:47.529397+05:30.

## Objective

Document the iPhone trial without inferring identity or platform integrity from login.

## Environment and procedure

User-reported device: iPhone 16 Pro; Homebrew CocoaPods setup and Expo/Xcode installation succeeded. User performed login, QR/acoustic exchange and an outside-classroom attempt. Agent compiled the existing iOS workspace for simulator without signing/installation.

## Expected and actual outcomes / evidence / status

| Case / expected | Actual | Evidence | Status |
| --- | --- | --- | --- |
| CocoaPods/native install | Succeeded | User task narrative | Physical-device setup passed (user-reported) |
| Login, QR and acoustic | Succeeded | User task narrative | Physical-device passed (user-reported) |
| Reject outside geofence | Outside geofence | User task narrative | Physically rejected as expected |
| Latest-trial face/liveness | Not independently confirmed | Latest task contains no confirming evidence | Not yet verified |
| Earlier identity/liveness | 24 October enrollment and PENDING_REVIEW recorded | [Historical iOS report](docs/IOS_MAC_VALIDATION.md) | Historical physical evidence; predates v2 |
| Fresh simulator compile/export | Passed | [Fresh ledger](docs/TEST_RESULTS.md) | Automated build passed |
| Genuine App Attest/integrity | No provider/device verification established | Native/server code and synthetic tests only | Not yet verified |
| C003 iOS policy/approval/record/sync | Pending | No current-policy positive evidence | Not yet verified |

## Known limitations

iOS current-network identity is not Android Wi-Fi scanning. Default review policy may prevent automatic approval inside the room. A geofence rejection is not an approved attendance. The audit did not repeat signed device provisioning or use the phone.

## Follow-up actions

Manual verification required: latest face/liveness, unchanged classroom policy, legitimate decision/record/dashboard sync and genuine App Attest. Follow [iOS guide](docs/IOS_GUIDE.md).
