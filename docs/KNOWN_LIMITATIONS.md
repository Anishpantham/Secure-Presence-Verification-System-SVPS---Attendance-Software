# Known limitations and release boundary

The [current local status](CURRENT_STATUS.md) supersedes historical build and
test claims. Xcode/simulator and signed-device builds have run. One physical
iPhone enrollment and one pending-review attendance attempt are recorded in
[iOS validation](IOS_MAC_VALIDATION.md). The [Android hostel demo](ANDROID_DEVICE_VALIDATION_2026-10-26.md)
now covers scans, registration, enrollment, submission, manual correction and
phone history. Actual classroom discrimination, broader device tests and genuine
Apple App Attest remain outstanding.

The latest user reports successful QR/audio exchanges on Android and iOS, followed
by expected outside-geofence rejection. Current-policy C003 approval, Android
classroom Wi-Fi contribution and iOS policy behavior remain unverified. Earlier
C003 approval predates policy v2. See [current status](CURRENT_STATUS.md).

- Live QR/audio can be relayed; five-second freshness is not distance bounding.
- Audio reservations permit at most 12 individual challenges/minute in ideal
  conditions; no measured classroom throughput is claimed.
- Noise, speaker/microphone diversity, leakage, interruption and accessibility
  require independent classroom testing.

## Verification assurance

- A normal phone can be rooted, instrumented or used with injected camera/location data. A native device signature (or a legacy HMAC) proves key possession, not trustworthy physical capture.
- Temporal landmark liveness is a heuristic. It is not ISO-certified presentation-attack detection, and sophisticated replay or deepfake attacks may succeed. The action vocabulary is small even though challenge IDs and ordering are randomized.
- SFace is a real pretrained model, but the chosen threshold has not been calibrated on this institution. The public-portrait smoke tests do not estimate FAR, FRR, fairness or operational accuracy.
- The corrected capture flow worked for the observed iPhone and Motorola enrollments; the Motorola had one IMAGE_QUALITY_LOW rejection before success. Sustained usability, both turn directions across phones, and broader device/user evaluation remain unverified. Automated API tests substitute vision and do not replace hardware evaluation.
- GPS and Wi-Fi support approximate physical presence, not absolute classroom proof. Rounded location history supports only coarse anomaly rules. The absence of a mock-location flag does not establish honesty.
- Wi-Fi scans are implemented only through a local Android module and depend on OS permissions, enabled location, recent scan availability and throttling. iOS may provide a permitted current BSSID only; no RSSI scan is fabricated. The separate default iPhone policy requires review.
- Play Integrity remains an unconfigured provider boundary. App Attest has native and server code, but Apple configuration and genuine provider/device validation remain outstanding. Requiring unverified attestation moves otherwise eligible attempts to review.

## Application and operational limits

- The hostel minimum-RSSI experiment accepted both inside and corridor samples
  under identical synthetic valid GPS, with stronger signals outside near the AP.
  This is not actual classroom calibration; no hostel thresholds were installed.
- Later C003 sampling produced a provisional fit for two 5 GHz references at
  -70 dBm and one older-flow automatic inside pass. The attempted outside
  attendance was actually from the hostel and stopped at GPS. Fresh near-door
  Wi-Fi-specific validation was not completed; see [C003 evidence](C003_CLASSROOM_VALIDATION_2026-10-27.md).
- WIFI_UNAVAILABLE can mean missing AP references even when the phone supplied a
  scan. More specific configuration-versus-sensor reason codes remain a UX item.
- After manual correction, original attempts remain PENDING_REVIEW for audit.
  The history UI can retain generic pending wording/review actions; official
  records are authoritative. The incoming mobile API now adds bounded request
  waits, but its physical network-interruption behavior remains to be tested.
- The latest faculty review test exercised the authenticated demo API and phone
  history, not a complete faculty-browser click-through or institutional approval.

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

Fresh audit results and unresolved findings are in [security report](../SPVS_SECURITY_TEST_REPORT.md).
Do not reuse old advisory counts as current clearance. No forced Expo downgrade
or broad dependency migration is applied by this documentation audit.

## Current platform policy

iOS policy-v2 choices are review, retry and dynamic; GPS-only is retired by the
migration. Dynamic QR/audio does not independently attest device platform or sensors.
Genuine App Attest and Play Integrity are not established. Native compilation,
historical enrollment and latest QR/audio operation do not prove those controls.
