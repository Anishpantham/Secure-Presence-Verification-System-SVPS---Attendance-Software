# Android physical-device validation through manual review

Checkpoint: **26 October 2026, Asia/Kolkata**. Device: Motorola Edge 50 Neo,
Android 16 / API 36, arm64-v8a. This records a controlled hostel demo, not a
classroom accuracy study or production approval.

## Completed sequence and evidence

| Step | Observed outcome |
| --- | --- |
| Install and launch | Verified native development APK installed through ADB; SPVS sign-in UI observed |
| Network | Metro initially reached through USB, then LAN; API reachable over the campus Wi-Fi connection |
| Wi-Fi collection | In-app setup check displayed actual AP identifiers and RSSI on the phone |
| Separate test account | Dedicated Android demo student enrolled in CS401; original iPhone account retained |
| Sign-in issue | Email contained an embedded space after a dot; server schema rejected it; correction produced the Android home screen |
| Device registration | 25 October 20:27:43 IST; native P-256 registration, client reports android-hardware storage |
| Face enrollment | IMAGE_QUALITY_LOW at 20:29:31 IST, followed by successful enrollment at 20:30:24 IST |
| Attendance submission | 25 October 20:33:45 IST; identity/liveness/GPS passed; scan available; result PENDING_REVIEW |
| Review request | Student opened a dispute for the attempt |
| Faculty correction | 26 October about 03:28 IST; one manual PRESENT record with source CORRECTION |
| Dispute resolution | One dispute resolved; faculty audit events recorded |
| Student API history | Exactly one PRESENT/CORRECTION record; original attempt remains PENDING_REVIEW |
| Android history UI | Verified after Wi-Fi reconnection: official PRESENT/CORRECTION above original PENDING REVIEW attempt |

The authenticated local faculty API was exercised by the assistant at the user's
request. The correction reason explicitly identifies a controlled Android hostel
workflow test with classroom Wi-Fi validation still outstanding. This was not a
real institutional attendance approval, automatic acceptance, or a completed
faculty-browser click-through test. The faculty dashboard was started and opened,
but remained at sign-in while the API review was performed.

The database confirms one correction from UNRECORDED to PRESENT, a faculty actor,
a non-empty reason, ATTENDANCE_CORRECTED and DISPUTE_RESOLVED audit events, and a
resolved dispute. The original automated decision was not rewritten.

## Wi-Fi collection versus classroom discrimination

The user clarified that the test location was a **hostel room**, with its AP
outside. The intended classroom reportedly has an AP inside; that classroom has
not yet been tested. SSIDs, raw BSSIDs and exact coordinates are omitted here.

| Same observed AP | Initial hostel-room sample | Corridor sample | Repeat room sample |
| --- | ---: | ---: | ---: |
| AP A, 2.4 GHz | -75 dBm | -52 dBm | Not observed in this scan |
| AP B, 5 GHz | -89 dBm | -67 dBm | -79 dBm |
| Total displayed APs | 2 | 6 | 1 |

Corridor signals were 23 dB and 22 dB stronger for these APs. The user scanned
outside and returned without rescanning; the retained UI was inspected before
the repeat inside check. Location labels follow the user's procedure, not
independent position tracking. UI inspection times are not radio timestamps.

An offline rule check used these measured RSSI values, minima equal to the first
inside readings, and identical **synthetic valid GPS** inputs to isolate Wi-Fi.
Both samples returned PRESENT with match ratio 1.0. That experiment made no
attendance submissions or database changes. It shows that this minimum-RSSI
rule cannot separate these samples; it neither proves nor disproves performance
with different AP placement in the actual classroom. One scan is not calibration.

No hostel APs or thresholds were configured as classroom references. The actual
classroom needs confirmed AP identities, repeated samples across seats, doorway,
corridor and adjacent room, then evaluation on fresh samples.

## Actual Android attendance evidence

The submitted attempt reported Wi-Fi available with source scan, GPS distance
17.4 m, horizontal uncertainty about 28.1 m, location age 0.5 s, and liveness
PASSED. Mandatory face matching and device-signature checks completed before
the presence decision. Provider attestation was not configured.

The result was PENDING_REVIEW with WIFI_UNAVAILABLE because the classroom has
zero configured AP references. In this case the reason means comparison was
unavailable, not radio collection failure. This ambiguous reason code is retained
in the historical attempt; no weaker policy was enabled to force approval.

After the labelled demo correction, the official status is PRESENT with source
CORRECTION. Original attempt reasons remain visible. The history UI still uses
generic pending-review explanatory text and may offer a review action for the
original attempt; the official-record section is authoritative. Improving that
resolved-state wording/action is a remaining UX item.

## Sign-in fix and network recovery

The invalid email was confirmed from the non-password input and validated against
the actual server schema. The intended credentials independently returned HTTP
200. Removing only the embedded space allowed phone login; no password was logged.

The mobile form now requests an email keyboard and email autofill hints. Sign-in
rejects embedded whitespace locally and translates server email/password field
validation into clear messages. Authentication errors remain distinct. Four new
regressions bring the mobile suite to 46 passing tests; TypeScript passes.

The history screen initially waited for responses while the phone had Wi-Fi
enabled but was not connected. API/student-history checks succeeded on the Mac.
After the user reconnected Wi-Fi, the actual phone UI displayed the saved record
and original attempt. This confirms recovery for this case, not a comprehensive
network interruption/timeout test. Requests can still wait without a clear
timeout/loading indication; that remains a UX/reliability item.

## What remains

Actual classroom automatic acceptance/rejection, broader Android/iPhone device
coverage, false-match/spoof evaluation, provider attestation and production
operations remain unverified. Hardware storage is client-reported, not independently
attested. No new claim of classroom-level accuracy follows from the demo.

Sanitized database/UI-derived evidence is in
[android-physical-validation.json](evidence/local-2026-10-26/android-physical-validation.json).
Raw UI snapshots, router identifiers, local credentials, templates and private
keys are excluded from publication. The earlier [Mac build record](ANDROID_MAC_VALIDATION.md)
remains the dated native compilation record; this document supersedes its
then-pending installation and initial physical-flow items.
