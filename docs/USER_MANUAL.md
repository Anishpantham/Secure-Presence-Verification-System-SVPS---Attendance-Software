# User manual

## Administrator

Sign in using the dashboard. In Administration, create staff and student accounts with unique emails and student roll numbers. Assign the faculty account when creating a course, then enroll the correct students. The current role is enforced immediately by the backend; changing a role revokes refresh sessions and device binding and requires an explanation.

In Classrooms, enter surveyed coordinates and a suitable radius. A radius must be 5–300 m. Enter actual Wi-Fi BSSIDs and minimum RSSI values only after collecting a campus reference profile; each line is `aa:bb:cc:dd:ee:ff,-80`. Leave the list empty when unknown, then select a deliberate unavailable policy. The default is manual review. Do not label the demo coordinates as real campus measurements.

Device reset requests appear in Administration. Verify student identity before approving. An approval revokes the previous device; the student must then register the replacement phone. Policy changes are recorded with the old and new values. Requiring attestation while its provider is unconfigured results in review, not silent bypass.

## Faculty

Courses lists assigned courses and enrolled students. Sessions opens a bounded attendance window for one course and classroom. Choose local start/end times; the API receives timezone-aware ISO timestamps. Session details refresh approximately every 15 seconds and show attempts separately from official records. Close a session to stop further automatic attendance.

Inspect reasons and risk indicators before reviewing an attempt. In Corrections & reviews, choose the session and student, enter PRESENT/ABSENT/EXCUSED and a meaningful reason. A correction is visibly sourced as CORRECTION and retains its previous status. Resolving a dispute records an explanation; it does not itself create attendance. Make a separate correction if justified. Reports downloads actual authorized records as CSV.

## Student

Install the development app and sign in. First register the phone using account-password confirmation. Then open Face enrollment, read the retention explanation and grant consent. Follow the center, turn and slow-blink prompts in even lighting. The server rejects zero/multiple faces, weak samples or incomplete action sequences.

For an open session, tap Verify my attendance. The app checks eligibility/device status, captures a fresh sequence, obtains a current location and gathers supported Wi-Fi observations. It signs the payload and displays the server's result. Do not leave during capture. If a network submission fails, retry the same submission to avoid a new attempt. If the challenge expires or evidence fails, start a fresh challenge when permitted.

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


Automatic iPhone GPS-only approval additionally requires a verified App Attest assertion, even if the global attestation requirement is off. The registered platform is client-reported; without this gate an unverified client could select a weaker platform policy. With App Attest unavailable/unconfigured, iPhone verification remains review/retry. GPS-only evidence still has lower presence assurance after app verification.
