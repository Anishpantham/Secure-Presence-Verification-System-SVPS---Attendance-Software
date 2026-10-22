# Known limitations and release boundary

## Verification assurance

- A normal phone can be rooted, instrumented or used with injected camera/location data. The HMAC proves possession of a credential, not trustworthy physical capture.
- Temporal landmark liveness is a heuristic. It is not ISO-certified presentation-attack detection, and sophisticated replay or deepfake attacks may succeed. The action vocabulary is small even though challenge IDs and ordering are randomized.
- SFace is a real pretrained model, but the chosen threshold has not been calibrated on this institution. The public-portrait smoke tests do not estimate FAR, FRR, fairness or operational accuracy.
- Real-camera head-direction conventions, blink timing, enrollment usability and sustained phone-to-server attendance must be validated on physical devices. Automated transaction tests use an explicitly substituted vision component; they do not replace that evaluation.
- GPS and Wi-Fi support approximate physical presence, not absolute classroom proof. Rounded location history supports only coarse anomaly rules. The absence of a mock-location flag does not establish honesty.
- Wi-Fi scans are implemented only through a local Android module and depend on OS permissions, enabled location, recent scan availability and throttling. iOS reports unsupported. The default fallback is manual review.
- Play Integrity and App Attest are unconfigured provider boundaries. Their adapter always returns unverified. Requiring attestation moves otherwise eligible attempts to review.

## Application and operational limits

- Web lists generally show the latest 500 entries. Large datasets need cursor pagination and indexed query tuning; exports can be large.
- Session-row locks serialize verification and manual correction within a session. This prioritizes consistency and requires throughput evaluation before large lectures.
- Inference is CPU-based and serialized per worker. Model memory is repeated across workers; no measured capacity or latency SLA is claimed.
- Dashboard access tokens live in memory. Reload requires login. Logout revokes refresh tokens; existing access tokens have a maximum 15-minute default expiry window unless the user is disabled.
- Enrollment response recovery uses `/biometrics` status; attendance has durable idempotency, while enrollment replay returns a conflict after success.
- Audit records are protected through application authorization, not an external tamper-proof log. A database administrator can modify storage.
- No automated retention purge, key rotation/re-encryption job, institution SSO, password reset/email service or external audit export sink is included. Identity/role provisioning is institution-managed in the dashboard.
- In a real college, biometric consent, an accessible alternative attendance process, retention and dispute policies require institutional decisions. This software does not supply those policies.
- Demo Compose uses a database-owner account, local development secrets and no TLS reverse proxy. Harden deployment according to `DEPLOYMENT_GUIDE.md` before using real student data.

## Dependency audit boundary

The current backend and dashboard audit results are recorded in `TEST_RESULTS.md` and the verification report. The Expo dependency tree currently contains two upstream advisories without published fixes: `braces` nested-pattern stack exhaustion (GHSA-vfj7-8cjw-p6xm) and `node-forge` RSA signature verification (GHSA-86w9-cpqp-85rv). npm propagates these through 45 affected package entries; that is not 45 distinct root flaws. These concern Metro/build tooling and Expo certificate utilities in this project. The application's HMAC implementation uses `@noble/hashes` and the server uses Python cryptography. Do not expose the development bundler to untrusted networks or treat this explanation as a general security clearance. Re-audit before distribution and adopt upstream fixes when available.

See the verification report for exact build, native compilation and physical-device test status. An exported JavaScript bundle is not an installed/tested Android APK, and Linux validation is not macOS ARM64 validation.

## Native build blocker observed in this cloud run

Android prebuild and native module autolinking succeeded. The Gradle debug build reached Expo Kotlin compilation but could not download React Native 0.88.0’s Android AAR: Maven Central redirects to `repo.reactnative.dev`, which the current cloud proxy blocks with HTTP 403. That domain was added to the saved environment draft; the draft must be applied before another native build can validate compilation. No APK or native Kotlin compilation success is claimed. The Android JavaScript/Hermes export passed separately.
