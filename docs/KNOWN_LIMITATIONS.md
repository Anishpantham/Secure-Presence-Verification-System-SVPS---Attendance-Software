# Known limitations and release boundary

## Verification assurance

- A normal phone can be rooted, instrumented or used with injected camera/location data. A native device signature (or a legacy HMAC) proves key possession, not trustworthy physical capture.
- Temporal landmark liveness is a heuristic. It is not ISO-certified presentation-attack detection, and sophisticated replay or deepfake attacks may succeed. The action vocabulary is small even though challenge IDs and ordering are randomized.
- SFace is a real pretrained model, but the chosen threshold has not been calibrated on this institution. The public-portrait smoke tests do not estimate FAR, FRR, fairness or operational accuracy.
- Real-camera head-direction conventions, blink timing, enrollment usability and sustained phone-to-server attendance must be validated on physical devices. Automated transaction tests use an explicitly substituted vision component; they do not replace that evaluation.
- GPS and Wi-Fi support approximate physical presence, not absolute classroom proof. Rounded location history supports only coarse anomaly rules. The absence of a mock-location flag does not establish honesty.
- Wi-Fi scans are implemented only through a local Android module and depend on OS permissions, enabled location, recent scan availability and throttling. iOS may provide a permitted current BSSID only; no RSSI scan is fabricated. The separate default iPhone policy requires review.
- Play Integrity remains an unconfigured provider boundary. App Attest has native and server code, but Apple configuration and genuine provider/device validation remain outstanding. Requiring unverified attestation moves otherwise eligible attempts to review.

## Application and operational limits

- Web lists generally show the latest 500 entries. Large datasets need cursor pagination and indexed query tuning; exports can be large.
- Session-row locks serialize verification and manual correction within a session. This prioritizes consistency and requires throughput evaluation before large lectures.
- Inference is CPU-based and serialized per worker. Model memory is repeated across workers; no measured capacity or latency SLA is claimed.
- Dashboard access tokens live in memory. Reload requires login. Logout revokes refresh tokens; existing access tokens have a maximum 15-minute default expiry window unless the user is disabled.
- Exact signed enrollment retries recover a successful response; different replay requests conflict. Attendance retains durable idempotency.
- Audit records are protected through application authorization, not an external tamper-proof log. A database administrator can modify storage.
- No automated retention purge, key rotation/re-encryption job, institution SSO, password reset/email service or external audit export sink is included. Identity/role provisioning is institution-managed in the dashboard.
- In a real college, biometric consent, an accessible alternative attendance process, retention and dispute policies require institutional decisions. This software does not supply those policies.
- Demo Compose uses a database-owner account, local development secrets and no TLS reverse proxy. Harden deployment according to `DEPLOYMENT_GUIDE.md` before using real student data.

## Dependency audit boundary

The current backend and dashboard audit results are recorded in `TEST_RESULTS.md` and the verification report. The Expo dependency tree currently contains two upstream advisories without published fixes: `braces` nested-pattern stack exhaustion (GHSA-vfj7-8cjw-p6xm) and `node-forge` RSA signature verification (GHSA-86w9-cpqp-85rv). npm propagates these through 15 affected package entries; that is not 15 distinct root flaws. These concern Metro/build tooling and Expo certificate utilities in this project. The application's HMAC implementation uses `@noble/hashes` and the server uses Python cryptography. Do not expose the development bundler to untrusted networks or treat this explanation as a general security clearance. Re-audit before distribution and adopt upstream fixes when available.

See the verification report for exact build, native compilation and physical-device test status. An exported JavaScript bundle is not an installed/tested Android APK, and Linux validation is not macOS ARM64 validation.

## Historical native build blocker

The baseline release failed downloading the React Native Android AAR with HTTP 403. This completion explicitly configures the managed proxy and CA trust, retaining TLS verification. The latest actual build outcome supersedes that baseline and is recorded in FINAL_COMPLETION_REPORT.md. JavaScript exports are reported separately from native compilation and physical-device testing.

## Cross-platform completion update

The current native build outcomes are in FINAL_COMPLETION_REPORT.md. No physical Android or iPhone run, Xcode compilation, simulator interaction, Apple Silicon execution, genuine Apple attestation registration, Play Integrity provider verification, institutional deployment or population biometric calibration is claimed. App Attest certificate/assertion logic is implemented and synthetic-tested; Apple receipt risk analysis is not implemented. CocoaPods resolution awaits macOS; no validated Podfile.lock is invented. `braces` <=3.0.3 and `node-forge` <=1.4.0 remain affected upstream; official registry latest versions were still 3.0.3 and 1.4.0 during this run. npm reports 15 affected mobile package entries from these two root advisories. Do not use npm force-fix downgrades to incompatible Expo 44/React Native 0.72. Keep Metro/dev tooling private, build only trusted source and do not use its vulnerable certificate utilities as an institutional trust authority. Backend and dashboard audit results are recorded separately.
