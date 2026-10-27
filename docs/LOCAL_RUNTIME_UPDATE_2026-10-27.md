# Local integration of GitHub QR/acoustic update

Date: **27 October 2026, Asia/Kolkata**.
Incoming GitHub main: `404eed84cbb9f5f2eb0bc73e7b66910fb49476f9`, merged through
[PR #6](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/6).
Feature implementation: `9a3640e2bc25f07da9dd450711c933f7d18624e7`.
The prior local main (`3a92b73`) was clean and two commits behind, so it was
fast-forwarded without conflicts or history rewriting. The incoming change
covered 49 files, including the migration, protocol, UI, native modules and docs.

## Updated runtime

- Installed the dashboard's locked dependencies, including QR rendering support.
- Created and checked a private PostgreSQL backup in the ignored work directory
  before migrating. The backup contains private application data and is not an artifact.
- Upgraded the local database from `7a2d13ce4f90` to `9bd32a88f101`; Alembic model
  drift check passed. Existing counts remained 4 users, 2 devices, 2 biometric
  profiles, 4 sessions, 4 attempts, 2 official records, 1 correction and 2 disputes.
- C003 coordinates/references and existing attendance outcomes were preserved.
  iOS and unavailable-Wi-Fi policies remain review. No classroom challenge was
  automatically enabled and no new physical submission was made.
- Restarted the API and dashboard. API health/readiness passed, models loaded,
  and the new `/api/v1/presence/evidence` route appeared in the running schema.
- Regenerated native projects with microphone permission/module declarations,
  preserving local native settings. CocoaPods now includes SpvsAcoustic; the
  resolved Podfile.lock is retained in Git.

## Local validation

| Check | Local result |
| --- | --- |
| Backend | 146 passed |
| Mobile | 64 passed; TypeScript passed |
| Dashboard | 11 passed; production build passed |
| Native Wi-Fi | 10 passed |
| Total local tests | 231 passed; no failures/skips in these suites |
| Android/iOS JS export | Passed; bundling is not hardware validation |
| Android arm64 APK | Native build passed; acoustic class present in DEX; signature verified |
| iOS simulator | Xcode BUILD SUCCEEDED; SpvsAcoustic Swift source compiled |
| iOS device app | Signed generic-device build passed; codesign verification passed |
| Native configuration | Microphone/module declarations verified |
| Browser E2E | Upstream cloud's 3 passing cases retained; not rerun against the local live demo database |
| Containers | Upstream build evidence retained; not rebuilt/deployed locally in this update |

The cloud report's total is 234 because it includes three browser tests. The
fresh local total is 231; do not add repeated runs as new independent cases.
Upstream deprecation/SDK warnings remain. Actual local results and hashes are in
[results.json](evidence/local-2026-10-27/results.json).

The rebuilt local Android APK is 78,138,028 bytes; SHA-256
`6cd0d397cccbbc42f6033c9a98eeab5a7c0d2f3f3d312b9dfdef72c607ab35c2`.
The cloud-only APK had a different build hash and was not distributed in Git.
The local replacement includes the required native microphone module.

## Compatibility and policy transition

New attendance requires a rotating QR proof and a server-verified acoustic
response before face/liveness, device, GPS and platform-presence checks can pass.
Faculty must start challenges, display QR and play the queued student's signal.
The capture is foreground/bounded and PCM stays transient on the phone.

QR rotates every five seconds with at most ten-second validity; audio redemption
has a server-clock five-second deadline. Individual audio playback reservations
serialize the channel to at most 12 per minute. Recordings/live relay and sound
leakage remain possible; this is not distance-bounding or certified proximity.

The migration retires old iOS gps_only policy into dynamic if present, but the
local review policy was unchanged. Dynamic iOS approval is a separate audited
administrator choice and was not enabled here. Provider attestation remains
unconfigured; QR/audio proof is not independent platform/sensor attestation.

Previously installed phone builds lack SpvsAcoustic and must be replaced before
testing the new flow. **No rebuilt client was installed or launched on a phone
during this update.** The signed iPhone app remains in ignored local build output;
no signing keys/profile or production IPA is published. Native compilation is
not microphone permission, speaker/microphone or acoustic-channel validation.

## Security, privacy and remaining work

Fresh npm audit: 4 high affected mobile entries and zero dashboard findings.
No forced dependency downgrade was applied. Backend vulnerability scanning is
historical, not a current clearance. Genuine provider attestation, calibrated
biometrics, load/throughput, retention/backups, production TLS/signing and
institutional policy remain release gates.

The [C003 report](C003_CLASSROOM_VALIDATION_2026-10-27.md) records the earlier
inside automatic pass and the corrected hostel GPS rejection. They predate policy
v2 and do not demonstrate physical QR/audio success. The old immediate-doorway
Wi-Fi-specific attendance test was not completed.

All physical testing waits for explicit user readiness in the classroom.
Secrets, database backup/data, raw AP identifiers, exact locations, private keys,
biometric templates, raw frames/audio and raw UI snapshots stay excluded from Git.
