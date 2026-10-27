# User manual

## Administrator

Sign in using the dashboard. In Administration, create staff and student accounts with unique emails and student roll numbers. Assign the faculty account when creating a course, then enroll the correct students. The current role is enforced immediately by the backend; changing a role revokes refresh sessions and device binding and requires an explanation.

In Classrooms, enter surveyed coordinates and a suitable radius. A radius must be 5–300 m. Enter actual Wi-Fi BSSIDs and minimum RSSI values only after collecting a campus reference profile; each line is `aa:bb:cc:dd:ee:ff,-80`. Leave the list empty when unknown, then select a deliberate unavailable policy. The default is manual review. Do not label the demo coordinates as real campus measurements.

Device reset requests appear in Administration. Verify student identity before approving. An approval revokes the previous device; the student must then register the replacement phone. Policy changes are recorded with the old and new values. Requiring attestation while its provider is unconfigured results in review, not silent bypass.

## Faculty

Student **Request a review** creates a dispute; it does not approve attendance.
After reviewing the evidence and deciding a change is justified, use
**Corrections & reviews → New correction**, select the correct session/student,
choose the justified status and enter a reason. Then use the dispute's **Resolve**
action to record its resolution. These are separate actions in the current UI.
The official record has source CORRECTION; the original automated attempt and its
reasons remain unchanged. Resolving a dispute alone does not create attendance.

Courses lists assigned courses and enrolled students. Sessions opens a bounded attendance window for one course and classroom. Choose local start/end times; the API receives timezone-aware ISO timestamps. Session details refresh approximately every 15 seconds and show attempts separately from official records. Close a session to stop further automatic attendance.

Inspect reasons and risk indicators before reviewing an attempt. In Corrections & reviews, choose the session and student, enter PRESENT/ABSENT/EXCUSED and a meaningful reason. A correction is visibly sourced as CORRECTION and retains its previous status. Resolving a dispute records an explanation; it does not itself create attendance. Make a separate correction if justified. Reports downloads actual authorized records as CSV.

## Student

Install the development app and sign in. First register the phone using account-password confirmation. Then open Face enrollment, read the retention explanation and grant consent. Follow the center, turn and slow-blink prompts in even lighting. The server rejects zero/multiple faces, weak samples or incomplete action sequences.

Enter the institution email without embedded spaces. The sign-in form uses an
email keyboard and reports malformed email/password fields explicitly. A format
error is distinct from an incorrect password. Never enter the `DEMO_PASSWORD=`
label itself when using a local demo password; enter only its value.

After faculty correction, refresh **My history**. Check **Official records** for
the current status and source. The original attempt may still show PENDING REVIEW
below it; this preserves the automated decision and does not erase the correction.

For an open session, faculty must start the classroom challenges on the session
page. Tap Verify my attendance, scan the current QR, allow foreground microphone
access, and tap Listen. Read the displayed attempt label to faculty so they play
your queued signal. Keep the app open and disconnect Bluetooth headphones.
Only server-verified sound advances to face/liveness capture, location and Wi-Fi.
PCM is processed transiently on the phone, not uploaded or saved. If QR/audio
is unavailable or inaccessible, use Finish attempt & request faculty review;
that does not automatically approve attendance. Retry an identical signed response
when offered after a network failure. See [the physical guide](ACOUSTIC_DEVICE_VALIDATION.md).

Faculty plays one queued attempt at a time. Stopping/restarting classroom
challenges invalidates earlier proofs. The new flow requires a rebuilt native
client with SpvsAcoustic; an old installed APK cannot gain microphone support
from a JavaScript reload alone.

History shows official records and attempts separately. Request review of a disputed attempt with an explanation. A PENDING_REVIEW result is not confirmed presence. Settings opens OS permission controls and signs out. Enrollment allows password-confirmed template deletion; Device allows a replacement request. No background location collection is implemented.

**Settings → Wi-Fi setup check** displays available access-point IDs and measured
signal strengths on Android, or permitted connected-network information on
iPhone. It does not upload observations, require device registration, or record
attendance. Confirm classroom AP identities with an administrator before using
them as references. Enable precise location and location services; repeated scans
may be throttled. An unavailable result is not proof that Wi-Fi is switched off.

## Result interpretation

| State | Meaning | Next action |
|---|---|---|
| PRESENT | All configured gates passed and attendance was recorded | Check history |
| REJECTED | A mandatory condition failed or a duplicate record exists | Inspect reason; request review if disputed |
| PENDING_REVIEW | Location/signals/attestation are uncertain under policy | Contact faculty; do not assume attendance approval |
| REQUIRES_RETRY | Fix a recoverable evidence issue | Enable permissions or obtain a better GPS fix, then retry |
| EXPIRED | Session/challenge is no longer valid | Ask faculty about a new session or review |


## Cross-platform completion update

On iPhone allow Camera and Precise Location. SPVS may read the current Wi-Fi BSSID when Apple permits it; it cannot scan nearby networks. Attendance can legitimately remain PENDING_REVIEW under the institution's iPhone policy. Administrators configure iPhone presence independently from Android missing-Wi-Fi policy, with an audit reason. The Device capabilities panel distinguishes legacy signing, reported native storage and verified App Attest registration. Register Apple app attestation only after institutional setup. Reinstall/key loss requires the existing reset-review workflow. To re-enroll a face, delete the existing template with password confirmation, consent again, then capture a new live sequence.


Policy v2 retires the iOS gps_only option. Current iOS choices are review, retry and dynamic; the migration maps an existing gps_only choice to dynamic while retaining stricter review/retry settings. Dynamic requires completed QR/audio proof alongside mandatory identity/device/GPS gates; a global requirement for attestation still applies. The local review policy was not changed. QR/audio does not independently attest a platform or sensor and can be relayed. See [the protocol](ACOUSTIC_DYNAMIC_QR.md).
