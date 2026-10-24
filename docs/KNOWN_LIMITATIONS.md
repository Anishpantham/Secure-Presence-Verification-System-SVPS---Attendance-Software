# Known limitations and release boundary

The [current local status](CURRENT_STATUS.md) supersedes historical build and
test claims. Xcode/simulator and signed-device builds have run. One physical
iPhone enrollment and one pending-review attendance attempt are recorded in
[iOS validation](IOS_MAC_VALIDATION.md). Android native compilation and unit
tests passed, but physical Android testing and genuine Apple App Attest remain
outstanding.

## Verification assurance

- A normal phone can be rooted, instrumented or used with injected camera/location data. A native device signature (or a legacy HMAC) proves key possession, not trustworthy physical capture.
- Temporal landmark liveness is a heuristic. It is not ISO-certified presentation-attack detection, and sophisticated replay or deepfake attacks may succeed. The action vocabulary is small even though challenge IDs and ordering are randomized.
- SFace is a real pretrained model, but the chosen threshold has not been calibrated on this institution. The public-portrait smoke tests do not estimate FAR, FRR, fairness or operational accuracy.
- The corrected head-direction and blink flow worked for the observed iPhone enrollment. Sustained usability, both turn directions across phones, and broader device/user evaluation remain unverified. Automated transaction tests use an explicitly substituted vision component; they do not replace that evaluation.
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

The 24 October npm audit reports **5 high-severity mobile package entries** and
zero dashboard findings. Direct advisory records identify `node-forge`
(GHSA-86w9-cpqp-85rv) and `zod` (GHSA-mrhx-c7xc-m3w5); the other affected entries
are dependency propagation. See the [saved mobile audit](evidence/local-2026-10-24/mobile-audit.json).
The earlier 15-entry/braces result remains historical; no dependency upgrade was
performed during this audit. npm still proposes an incompatible Expo 44 downgrade
for parts of the tree. Backend vulnerability scanning was not rerun; its older
zero-finding report is not a current clearance. Keep development tooling private
and review compatible fixes before distribution.

See the verification report for exact build, native compilation and physical-device test status. An exported JavaScript bundle is not an installed/tested Android APK, and Linux validation is not macOS ARM64 validation.

## Historical native build blocker

The baseline release failed downloading the React Native Android AAR with HTTP 403. This completion explicitly configures the managed proxy and CA trust, retaining TLS verification. The latest actual build outcome supersedes that baseline and is recorded in FINAL_COMPLETION_REPORT.md. JavaScript exports are reported separately from native compilation and physical-device testing.

## Historical cross-platform completion update (23 October cloud run)

The current native build outcomes are in FINAL_COMPLETION_REPORT.md. No physical Android or iPhone run, Xcode compilation, simulator interaction, Apple Silicon execution, genuine Apple attestation registration, Play Integrity provider verification, institutional deployment or population biometric calibration is claimed. App Attest certificate/assertion logic is implemented and synthetic-tested; Apple receipt risk analysis is not implemented. CocoaPods resolution awaits macOS; no validated Podfile.lock is invented. `braces` <=3.0.3 and `node-forge` <=1.4.0 remain affected upstream; official registry latest versions were still 3.0.3 and 1.4.0 during this run. npm reports 15 affected mobile package entries from these two root advisories. Do not use npm force-fix downgrades to incompatible Expo 44/React Native 0.72. Keep Metro/dev tooling private, build only trusted source and do not use its vulnerable certificate utilities as an institutional trust authority. Backend and dashboard audit results are recorded separately.


Automatic iPhone GPS-only approval additionally requires a verified App Attest assertion, even if the global attestation requirement is off. The registered platform is client-reported; without this gate an unverified client could select a weaker platform policy. With App Attest unavailable/unconfigured, iPhone verification remains review/retry. GPS-only evidence still has lower presence assurance after app verification.
