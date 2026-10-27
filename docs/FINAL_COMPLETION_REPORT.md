# SPVS current completion and verification report

**Checkpoint: 27 October 2026, Asia/Kolkata.**
Integration source: `0fc235f916fb662db71c298091255ec10f0917f6`.
Publication: [PR #7](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/7).
It incorporates upstream main `404eed84cbb9f5f2eb0bc73e7b66910fb49476f9`
([QR/acoustic PR #6](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/6)).
Artifact metadata and FINAL_FILE_MANIFEST.txt identify the exact delivery snapshot.

## Incoming feature and local integration

The new attendance flow requires rotating classroom QR and individual acoustic
proof in addition to the existing device, face/liveness, GPS and platform-presence
requirements. Faculty starts/stops challenges, displays QR and plays the queued
student's signal. Student microphone capture is bounded/foreground; PCM remains
transient on the phone. QR rotation is five seconds, validity at most ten seconds,
and audio redemption has a server-clock five-second deadline.

The local main was clean and two commits behind, so it was fast-forwarded.
Dashboard dependencies were refreshed from the lockfile. A private local database
backup was created and checked; migration `9bd32a88f101` and model-drift check
passed. Existing accounts, devices, profiles, sessions, attempts, records,
corrections, disputes and C003 references were preserved. Local iOS and unavailable
Wi-Fi policies remain review; no physical session challenge was enabled.

API/dashboard were restarted; health, model readiness and the new presence route
were verified. Android/iOS projects were regenerated, microphone declarations
checked, and the resolved Podfile.lock now includes SpvsAcoustic.

## Current local evidence

| Check | Result |
| --- | --- |
| Backend | 146 passed |
| Mobile | 64 passed; TypeScript passed |
| Dashboard | 11 passed; production build passed |
| Native Wi-Fi | 10 passed |
| Total local | 231 passed, no failures/skips |
| Android/iOS JS exports | Passed |
| Android native APK | Built arm64; acoustic class present; signature passed |
| iOS simulator | Xcode build passed; acoustic Swift source compiled |
| iOS signed device app | Build and codesign verification passed |
| Migration/configuration | Upgrade, model drift and native declarations passed |

Evidence is in [local-2026-10-27](evidence/local-2026-10-27/).
The upstream cloud reports three additional browser tests (234 total in that
environment); they were not rerun against the local live demo database and are
not included in the local total. Cloud container checks remain separate historical
evidence. Unit tests include synthetic PCM and mocked native/UI inputs, not real
sound interoperability. Upstream deprecation warnings remain.

The new APK is 78,138,028 bytes, SHA-256
`6cd0d397cccbbc42f6033c9a98eeab5a7c0d2f3f3d312b9dfdef72c607ab35c2`.
It replaces the old APK lacking SpvsAcoustic. No rebuilt app was installed or
launched on either phone during this update. The signed iPhone app stays in ignored
local build output; no production IPA or private signing material is published.

## Physical evidence before policy v2

Earlier iPhone registration/enrollment and the Motorola hostel demo through manual
faculty API correction, dispute resolution and verified history remain valid
observations of the preceding flow. They are not physical QR/audio results.

C003 was configured separately with the user's coordinates, a 50 m radius and two
provisional 5 GHz references at -70 dBm. Three inside diagnostic samples and one
closed-door corridor sample informed this provisional fit. The existing half-match
rule accepts one of two references; no independent router mapping or statistical
calibration was claimed.

Inside C003 on 26 October at 18:34:48 IST, the old flow returned automatic PRESENT,
source VERIFICATION, with Wi-Fi ratio 0.5 and eligible face/liveness/GPS. The later
attempt at 23:57:53 IST was confirmed by the user to be from the hostel. It returned
OUTSIDE_GEOFENCE at reported distance 151.1 m and created no record. The geofence
returned before Wi-Fi matching, so this does not validate near-door Wi-Fi exclusion.

Full measurements, location correction and evidence scope:
[C003 validation](C003_CLASSROOM_VALIDATION_2026-10-27.md).

## Remaining gates and testing hold

**All further physical tests wait for explicit user readiness in the classroom.**
The rebuilt native clients must be installed, and the faculty must enable a fresh
session's QR/audio controls. Use the [physical plan](ACOUSTIC_DEVICE_VALIDATION.md).
Record the gate determining a failure; failed QR/audio/GPS does not isolate Wi-Fi.

Pending: real speaker/microphone interoperability, permissions/interruptions,
timing under network load, doorway/adjacent-room sound leakage and real-time relay,
accessible alternatives, new-flow automatic classroom decisions, broader biometric
and device calibration, genuine provider attestation and production operations.

QR/audio can be shared or relayed. The serialized five-second playback reservation
limits the channel to at most 12 individual challenges per minute. This is not
distance-bounding, cryptographic proximity or production capacity validation.

The local iOS review policy was preserved. The migration retires legacy gps_only
to dynamic where present; dynamic is a separate audited opt-in and does not override
mandatory identity/location or required attestation gates. QR/audio is not App Attest.

Fresh npm audit: 4 high mobile affected entries; dashboard zero. Backend security
auditing remains historical. No forced downgrade or general security clearance
is claimed. Historical history/review wording issues remain documented; the new
mobile API adds bounded request waits, which are not yet physical-network validated.

## Delivery

Current source ZIP, project/setup PDFs, packaged Markdown, milestone PDFs and
checksums are regenerated together. The archive includes QR/audio code, migration,
native locks, sanitized C003 evidence and local test/build records. CRC/member,
source hash, artifact hash, PDF readability and link checks are performed.

Secrets, private backups/databases, raw AP identifiers, precise locations, keys,
biometric templates, raw frames/audio and raw screen captures remain excluded.
Old dated reports and Git history preserve prior results. Source publication
does not deploy a cloud service or establish institutional production readiness.
