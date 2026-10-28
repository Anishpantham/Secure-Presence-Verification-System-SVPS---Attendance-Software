# Threat model

## Current control-to-evidence map (28 October audit)

| Threat | Implemented mitigation | Evidence and remaining risk |
| --- | --- | --- |
| Buddy punching / device sharing | Face/liveness, bound key and enrollment/session scope | Regression tests; Android identity user-reported; collusion/compromised capture not excluded |
| QR sharing / replay | Rotation, short expiry, session/classroom/epoch binding and student redemption uniqueness | Automated protocol tests; live forwarding remains possible |
| Acoustic replay / relay | Per-attempt random answer, one guess, five-second server deadline | Automated codec/protocol tests and reported hardware exchange; live relay/leakage not independently tested |
| GPS spoofing | Freshness, accuracy, uncertainty, reported mock rejection and coarse travel check | Rule tests and expected outside rejection; compromised OS can falsify inputs |
| Wi-Fi spoofing | Actual Android scan BSSID/RSSI matching; explicit missing-signal policy | Native tests and older sampling; AP identity/RSSI is not cryptographically authenticated |
| Root / jailbreak / emulator abuse | Native key storage; configurable integrity requirement; App Attest verification boundary | Synthetic verifier tests only; Play Integrity unconfigured and genuine App Attest unverified |
| Face presentation attacks | Single-face matching and random temporal blink/turn checks | Real-model and rule tests; no certified PAD or population calibration |
| Session hijacking | Short JWT lifetime, issuer/audience/type checks, refresh rotation/reuse revocation | Backend security tests; stolen access token remains valid until expiry/disable |
| Network interception | HTTPS required by release mobile; configured CORS; signed evidence | Local HTTP is development-only; production TLS infrastructure still required |
| Privacy / biometric disclosure | Consent, encrypted templates, role scope, no raw server image/audio retention | Source/tests; institutional retention, backup access and key rotation remain operational work |

The audit is not a penetration test. See [fresh security results](../SPVS_SECURITY_TEST_REPORT.md).

## QR/audio extension

The current flow adds expiring QR tokens and a one-use per-attempt acoustic answer
available to scoped faculty playback controls. Epoch invalidation, exact signatures,
server-clock deadlines and consumption address replay/state confusion. Live relay,
current-window recordings, sound leakage, compromised clients and faculty-key
misuse remain possible. This is not a distance-bound or independently attested
proximity proof. Physical speaker/microphone, noisy-room, doorway/adjacent-room
and accessibility trials have not started; see [the matrix](ACOUSTIC_DEVICE_VALIDATION.md).

Assets include student identity, biometric templates, device credentials, location evidence, attendance integrity, refresh sessions and faculty audit accountability. Trust boundaries are the mobile device to HTTPS API, staff browser to API, API to PostgreSQL, and operator secrets to server runtime. A student client is untrusted even after login.

| Threat | Mitigation in this implementation | Residual risk / evaluation |
|---|---|---|
| Shared QR/token | No standalone shared token can create attendance; enrolled identity, challenge and device are required | Account and device credential collusion remains possible |
| Face photo | Actual embedding plus randomized temporal eye/head sequence | Advanced replay/deepfake/injection can mimic landmarks |
| Client says liveness passed | Schema rejects unknown verdict fields; server analyzes frames | Frame capture provenance is not attested |
| Hostel or remote attempt | Server GPS geofence, accuracy, age and available Wi-Fi | Compromised phones may forge all signals |
| GPS spoofing | Mock indicator, stale/accuracy checks, coarse travel anomaly | An omitted/forged mock flag is not trustworthy |
| Device ID cloning | Native P-256 proof and signed evidence; one active binding; legacy HMAC compatibility | Legacy secrets can be copied; native storage reports are not independent key attestation |
| Replay or duplicate | Purpose/user/device/session binding, expiry, single use, unique keys and records | Encoded video may be re-rendered to evade byte equality; liveness is basic |
| Concurrent submission | Student/challenge/session locks and unique constraints | Session-level serialization limits throughput |
| Faculty accesses another class | Server course-ownership checks and query scoping | Privileged administrator has institution-wide access |
| Silent attendance edit | Mandatory reasons, correction ledger, structured events | Database-superuser tampering is outside app controls |
| Refresh-token theft/reuse | Secure storage, hashing, rotation, family revocation | Access tokens have an expiry window; browser XSS can act while logged in |
| CSV formula injection | Escape dangerous leading formula characters | Downstream spreadsheet handling still needs care |
| Large payload/decoded image | Actual-byte body bound, JPEG byte and dimensions cap | Valid expensive requests still consume inference capacity |
| Dependency compromise | Lockfiles, verified model hashes, audit reports | Audits are time-bound and cannot prove absence of defects |

## Abuse evaluation protocol

Use consented volunteers on both real Android and iPhone devices. Test identical-photo presentation, screen replay, a wrong person, multiple faces, same evidence/key replay, same evidence/new key replay, a second registered device, a revoked device, a distant location, disabled location permission and unavailable Wi-Fi. Inspect both HTTP outcomes and resulting database/audit records. Record model version, threshold, device model, OS version, illumination and capture timing. Never label a human review or an unrun test as successful automatic presence verification.

The public test portraits are used only for model smoke tests. No external biometric service receives student images, and this implementation does not use facial recognition for surveillance or sensitive-trait inference.


## Cross-platform completion update

New threat cases: App Attest development/production confusion, attacker-selected trust roots, certificate nonce substitution, assertion-counter replay, app reinstall with persistent iOS Keychain entries, and presenting iOS BSSID identity as multi-AP RSSI evidence. Controls include server-configured root fingerprint/app ID/environment, challenge consumption and key uniqueness, atomic counters, installation-ID checks, and separate server iOS policy. Synthetic adversarial tests cover protocol rejection; physical sensor injection, rooted-device behavior and sophisticated presentation attacks still require evaluation. Keychain-only simulator keys are never claimed to be Secure Enclave keys.


Policy v2 retires the iOS gps_only option. Current iOS choices are review, retry and dynamic; the migration maps an existing gps_only choice to dynamic while retaining stricter review/retry settings. Dynamic requires completed QR/audio proof alongside mandatory identity/device/GPS gates; a global requirement for attestation still applies. The local review policy was not changed. QR/audio does not independently attest a platform or sensor and can be relayed. See [the protocol](ACOUSTIC_DYNAMIC_QR.md).
