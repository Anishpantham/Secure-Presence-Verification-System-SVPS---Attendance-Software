# Demonstration script

Current observed hardware flow is recorded in
[Android device validation](ANDROID_DEVICE_VALIDATION_2026-10-26.md) and
[iOS validation](IOS_MAC_VALIDATION.md). Use [current status](CURRENT_STATUS.md)
for the latest evidence rather than the historical baseline reports.

## Reproduce the manual-review demonstration

1. Use a dedicated test student so an existing registered phone remains intact.
2. Complete native registration, consented enrollment and a real session submission.
3. Show the actual pending decision and evidence; missing classroom references
   can produce WIFI_UNAVAILABLE even when the scan itself is available.
4. Request review from the phone. Show that a dispute exists but no official
   attendance record is created by that request.
5. As assigned faculty, review the evidence. For an explicitly controlled demo,
   label any correction reason as a demo and state what was not verified.
6. Create the justified attendance correction, then separately resolve the dispute.
   The latest observed test exercised these authenticated faculty API operations;
   a complete faculty-browser click-through remains to be tested.
7. Refresh student history. Show PRESENT with source CORRECTION and the original
   PENDING REVIEW attempt. Do not describe this as automatic classroom verification.

The Motorola must be connected to the Mac's reachable Wi-Fi network for the local
API. The latest history check recovered after Wi-Fi reconnection; no fake data or
policy relaxation was used. The hostel scan test is not actual classroom calibration.

## Before the evaluation

Run the automated suites and retain their current result files. Configure a real classroom and a deliberate Wi-Fi fallback. Complete the real-device checklist with consenting participants before promising a successful live capture. Prepare the randomly generated demo password locally; never place it in slides or the ZIP.

## Eight-minute desktop demonstration

1. Explain the two-layer design and the reason uncertain signals produce review.
2. Sign in as administrator. Show the actual course, enrolled demo student and classroom configuration. Point out that initial metrics are real counts rather than seeded attendance.
3. Open a faculty session for the assigned course and a short future window.
4. Show the session page, separate attempts and official record tables, and automatic refresh.
5. Show the policy's manual-review Wi-Fi default and unconfigured attestation status.
6. Sign in as faculty and demonstrate that administrator navigation and API permissions are unavailable. An automated test also verifies cross-course denial.
7. Explain an authorized correction, enter a reason only for a legitimately reviewed record, and show its source/history. Do not misrepresent the correction as biometric verification.
8. Close the session and export the actual CSV. Open the security event log and identify session/correction/export events.

## Phone demonstration after hardware validation

Sign in as a student, register the phone, consent to face enrollment and follow the randomized prompts. Open the active session, capture a fresh sequence, collect real location and available Wi-Fi, and show the exact server result. A review/retry result is a valid demonstration of the decision policy; never switch to fake evidence to force PRESENT.

Demonstrate one rejected or reviewable condition: permission denial, a clearly outside location, a revoked device, or a static-photo liveness failure. Then show the corresponding attempt, reason and dispute workflow. Any successful person-to-session result must come from actual captured evidence or be visibly identified as a faculty correction.

## If hardware or network is unavailable

Demonstrate the running web/API/database workflow, real-model smoke tests and signed-request protocol tests. State that the API happy-path tests isolate vision and that physical sensor/liveness performance has not been measured. Show `SPVS_VERIFICATION_REPORT.md`, not an invented success video.


## Cross-platform completion update

For the cross-platform extension, show Android and iPhone capability differences before a phone demonstration. Open Administration and show the distinct iPhone review/retry/GPS-only choices and required audit reason. Show native device key algorithm and label storage as reported. If no Apple-configured physical device is available, show the explicit unconfigured/unsupported state and synthetic test evidence; do not claim an App Attest demo. Only mark real enrollment and attendance complete after a physical camera run succeeds. Present the final test matrix and outstanding hardware gates alongside the APK, if built.
