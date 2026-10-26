# QR + acoustic feature: completion and limitations

Completion checkpoint: 27 October 2026 (Asia/Kolkata). Branch:
`feature/acoustic-dynamic-qr-verification`, based on `main` commit
`3a92b737d7b8b13e1f01d66bcb820724f7203489`. This is a source implementation and
cloud validation report, not an assertion of production or physical-device readiness.

## Delivered

- PostgreSQL migration and models for rotating QR challenges and per-attempt proofs.
- Faculty-scoped start/stop, QR display, listening queue, one-shot audio issuance;
  student device-signed redemption and audited incomplete-capture review endpoints.
- Five-second QR rotation, at most ten-second QR validity, server-clock five-second
  acoustic deadline, atomic consumption, idempotency and distributed rate limiting.
- Mandatory QR/audio gate on both platforms, retaining face/liveness, device, GPS,
  Android Wi-Fi policy, optional iOS network evidence and required attestation policy.
- React faculty controls with QR rendering/countdown, Web Audio playback/status and
  existing outcomes, corrections, disputes and audit compatibility.
- Expo QR scanner and capture flow, foreground Kotlin/Swift microphone module,
  local audible 16-FSK encoder/decoder, CRC and noise-tolerant synchronization.
- Camera/mic permission handling, background cancellation, bounded capture/HTTP
  waits, exact signed retries after lost responses, and a review path without auto-pass.
- Updated OpenAPI, Docker integration, automated regressions and physical/Mac guides.

## Validation

| Check | Result |
|---|---|
| Backend, real PostgreSQL + separate real vision tests | 146 passed |
| Mobile codec, protocol, permissions and UI tests | 64 passed |
| Dashboard component tests | 11 passed |
| Playwright browser regressions including QR rotation | 3 passed |
| Android native Wi-Fi regression tests | 10 passed |
| Total | **234 passed; zero failures/skips in these suites** |
| Mobile TypeScript and dashboard production build | Passed |
| Android and iOS Expo JavaScript exports | Passed |
| PostgreSQL migration and Alembic model drift check | Passed |
| Backend and dashboard Docker builds | Passed |
| Android arm64 development APK assembly | Passed |
| Xcode compilation / real acoustic hardware trials | Not performed |

The final measured counts and native build outcome are recorded in
`docs/evidence/acoustic-dynamic-qr/results.json`. No iOS native build or physical
QR/audio trial was performed in this Linux cloud environment. The accompanying
[physical guide](ACOUSTIC_DEVICE_VALIDATION.md) gives exact Mac commands and the
required iPhone 16 Pro / Motorola Edge 50 Neo classroom matrix.

Tests use real PostgreSQL transactions for expiry, concurrency, signature,
policy, replay and audit checks. Existing API fixtures use test-only vision doubles;
legacy transaction regressions explicitly receive completed presence proof fixtures.
New protocol tests exercise actual issuance/redemption endpoints. Separate tests run
real face models. Codec noise tests are synthetic PCM, and native permission/UI
unit tests use mocks. None of those tests establish physical acoustic performance.

Both lockfile-based JS builds and container builds are checked. Expo iOS export is
JavaScript bundling, not Xcode compilation. Generated native configuration checks
verify permission/module declarations, not microphone behavior on hardware. The
existing historical APK and iOS build records are not represented as new validation.

## Review and deployment limits

- Rebuild native clients and apply the migration before rollout. Old clients cannot
  automatically pass policy v2. Existing iOS review/retry settings stay strict;
  an administrator must explicitly select `dynamic` to enable that automatic path.
- QR and sound are transferable. Recordings within the live window and real-time
  relay can succeed. There is no distance-bounding or cryptographic proximity claim.
- Only one individual audio challenge occupies a classroom channel per five-second
  reservation (12/minute); students must be staggered and wait for faculty readiness.
- Hardware speaker/microphone response, iOS audio interruptions, AGC, clock drift,
  classroom acoustics, accessibility and Android/iOS permissions need the physical plan.
- The registered platform remains client-reported unless independently attested;
  this feature does not solve platform spoofing or a compromised faculty/device key.
- Provider attestation, face/liveness spoof resistance, GPS uncertainty and
  institution-specific calibration retain the existing security limitations.
- No raw audio upload/storage is introduced. Protocol/audit retention remains an
  institutional operational decision; no new automatic cleanup scheduler is installed.
- Kotlin/Swift capture source is present; iOS compilation/signing requires Xcode
  and appropriate provisioning. Preserve the historical Podfile.lock, then regenerate
  pods on the Mac. Release signing and physical installation are separate tasks.

Full protocol, state transitions, timing budget, migration behavior and API contract:
[ACOUSTIC_DYNAMIC_QR.md](ACOUSTIC_DYNAMIC_QR.md).
