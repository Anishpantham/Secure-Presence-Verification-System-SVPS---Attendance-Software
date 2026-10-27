# SPVS local and GitHub synchronization - 27 October 2026

Publication: [PR #7](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/7)
from `spvs/classroom-sync-20261027` into main. The linked PR/Git refs are
authoritative for current merge state.
Integration checkpoint: `0fc235f916fb662db71c298091255ec10f0917f6`.

## Incoming GitHub changes

Local main was clean at `3a92b73` and two commits behind.
Upstream feature `9a3640e` and merged main `404eed8` (PR #6) add dynamic QR/audio
protocol, database migration, dashboard controls and dependencies, native microphone
modules, permissions, automated coverage and physical-test documentation.
The local checkout was fast-forwarded; none of this upstream work was replaced.

## Local system update

Dashboard dependencies were refreshed, a private database backup verified, and
migration `9bd32a88f101` applied. Counts of existing accounts/devices/profiles,
sessions/attempts/records/corrections/disputes were preserved. C003 retains its
50 m radius and two provisional AP references. Review policies remain unchanged.
The API/dashboard were restarted and the new API route verified.

Android and both iOS native targets were rebuilt with SpvsAcoustic. Podfile.lock
was updated, APK and signed-app verification passed, and generated microphone
configuration was checked. The new APK replaces the old native host. No app was
installed/launched on a phone and no physical trial or classroom challenge started.

## Evidence and release refresh

- 146 backend, 64 mobile, 11 dashboard and 10 native Wi-Fi tests passed locally:
  **231 total**, zero failures/skips.
- TypeScript, dashboard build, both JS exports, migration/drift and native builds
  passed. Upstream cloud browser/container results remain separate evidence.
- The new [C003 report](C003_CLASSROOM_VALIDATION_2026-10-27.md) records three inside
  calibration points, the closed-door corridor scan, provisional -70 dBm references,
  an older-flow automatic inside PRESENT and the corrected hostel GPS rejection.
- The [runtime report](LOCAL_RUNTIME_UPDATE_2026-10-27.md) separates native compilation
  from unperformed QR/audio hardware testing and describes the compatibility change.
- Current entry points, manuals, architecture/security/API/database guides and
  delivery files are reconciled with mandatory policy v2.
- Source ZIP, PDFs, packaged Markdown and hash metadata are regenerated together.
  The manifest records actual source content without embedding its own future commit.

## What remains local or pending

Private backup/database data, credentials, signing material, raw router identifiers,
precise coordinates, raw UI captures, templates, frames and audio remain excluded.
Git synchronization does not deploy a cloud service or replicate local data.

The immediate-doorway Wi-Fi-specific attendance comparison was not completed.
The later attempted outside submission actually came from the hostel and failed
GPS before Wi-Fi evaluation. Earlier physical successes predate QR/audio.

All new physical tests wait for the user to say they are in the classroom and
ready. Newly built clients must be installed and faculty QR/audio controls enabled
for the next fresh session. Acoustic reliability/leakage/relay, actual new-flow
classroom decisions, attestation, biometric calibration and production gates remain.

Fresh npm audit: 4 high mobile affected entries and zero dashboard findings.
Backend vulnerability scanning is historical; no forced downgrade was performed.

After merge/fetch, local main and origin/main should be identical with a clean
working tree. Verify with:

```sh
git status --short --branch
git rev-parse main origin/main
git rev-list --left-right --count main...origin/main
```

Expected main divergence: `0 0`. Older dated audit/sync records preserve their
historical state and must not be read as today's pending-work inventory.
