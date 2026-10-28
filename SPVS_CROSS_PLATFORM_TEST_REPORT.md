# SPVS cross-platform test report

Checkpoint opened 28 October 2026; recorded 2026-10-28T23:56:47.529397+05:30.

## Objective

Compare shared protocol validation with platform-specific assurance boundaries.

## Environment and procedure

Fresh macOS automated tests/builds plus separately attributed user reports from Motorola Edge 50 Neo and iPhone 16 Pro. Procedures are in the platform reports and test ledger.

## Expected and actual outcomes / evidence / status

| Suite | Passed | Failed/errors | Skipped |
| --- | ---: | ---: | ---: |
| backend | 146 | 0 | 0 |
| dashboard | 11 | 0 | 0 |
| mobile | 64 | 0 | 0 |
| browser | 3 | 0 | 0 |
| android-wifi | 10 | 0 | 0 |

Fresh total: 234 passed; zero final failures/skips. [JUnit/commands](docs/TEST_RESULTS.md).

| Factor | Android | iOS |
| --- | --- | --- |
| Login/QR/audio physical | User-reported pass | User-reported pass |
| Latest identity/liveness | User-reported pass | Not independently verified |
| Outside classroom | Expected rejection | Expected rejection |
| Nearby Wi-Fi | Native real scan implemented | Unsupported; optional current BSSID only |
| Classroom v2 approval | Manual verification required | Manual verification required |
| Integrity provider | Play Integrity unconfigured | Genuine App Attest unverified |

## Known limitations

Shared JS tests do not establish native sensor equivalence. Simulator compilation is not iPhone operation. Older records are not proof of the new policy.

## Follow-up actions

Run paired in-classroom trials, interruptions, permissions, acoustic accessibility/relay and record synchronization with unchanged calibration.
