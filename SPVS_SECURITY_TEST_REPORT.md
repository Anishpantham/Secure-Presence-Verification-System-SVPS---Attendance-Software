# SPVS security test report

Checkpoint opened 28 October 2026; recorded 2026-10-28T23:56:47.529397+05:30.

## Objective

Assess implemented controls and executed security regression coverage without claiming penetration-test certification.

## Environment and procedure

Reviewed auth/JWT/roles, native keys, replay/idempotency, QR/audio deadlines, presence/vision, privacy, platform attestation and migrations. Fresh backend tests include security workflows, App Attest synthetic cases and dynamic-presence adversarial cases. Ran npm audit on both clients and staged-content secret checks (see final safety evidence).

## Expected and actual outcomes / evidence / status

| Check / expected | Actual | Evidence | Status |
| --- | --- | --- | --- |
| Security/API regression suite | Included in 146 backend passes | [Fresh JUnit](docs/evidence/final-audit-20261028/backend-tests.xml) | Automated-test passed |
| Platform/protocol/client regressions | Included in 64 mobile passes | [Fresh JUnit](docs/evidence/final-audit-20261028/mobile-tests.xml) | Automated-test passed |
| Dashboard advisory scan | Zero findings, exit 0 | [Audit](docs/evidence/final-audit-20261028/dashboard-audit.json) | Passed at scan time |
| Mobile advisory scan | 9 entries: 4 high, 5 low; exit 1 | [Audit](docs/evidence/final-audit-20261028/mobile-audit.json) | Failed clean-advisory gate |
| Backend advisory scan | Zero known vulnerabilities, exit 0 | [Frozen runtime audit](docs/evidence/final-audit-20261028/backend-audit.json) | Passed at scan time |
| Genuine platform integrity | No provider-backed device evidence | Source plus synthetic tests only | Not yet verified |
| Live relay/spoof/PAD/root/emulator testing | No fresh physical adversarial execution | No evidence | Manual verification required |

## Known limitations

Package-entry counts include transitive propagation and are not counts of independent exploits. No force-fix or incompatible Expo downgrade was applied. Signatures prove key possession, not honest sensors; dynamic iOS policy does not attest platform. QR/audio can be relayed. Liveness is heuristic and uncalibrated. Audit logs are not externally tamper-proof.

## Follow-up actions

Resolve compatible dependency fixes, repeat advisory scans before release, validate provider integrity and classroom/adversarial tests, define retention/key rotation/TLS and independent security review. See [threat model](docs/THREAT_MODEL.md).
