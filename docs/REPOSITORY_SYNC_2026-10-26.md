# SPVS synchronization through Android demo completion

Checkpoint: **26 October 2026, Asia/Kolkata**.
Publication: [PR #5](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/5)
from `spvs/android-validation-20261026` into main.
Implementation checkpoint: `cc8f1ddba2f1aa2e8c97f39eccb5580557e15eb5`.
The PR/Git refs identify current publication status; the archive manifest records
exact contents without embedding its own future delivery-commit hash.

## Since the previous synchronization

The previous synchronized main was `6ed8e48` via PR #4. This continuation adds:

- Physical Motorola Edge 50 Neo / Android 16 testing: installation, login,
  native device registration, face enrollment, Wi-Fi collection and submission.
- A resolved demo review with exactly one official PRESENT record sourced from
  CORRECTION, attributable faculty audit events and verified Android history.
- Preserved original PENDING_REVIEW decision and explicit hostel/demo scope.
- The reproduced email-space fix: email keyboard/autofill hints, local whitespace
  rejection and specific API validation feedback; no password values logged.
- A reusable dashboard development task.
- Sanitized physical evidence and refreshed test/security-audit reports.
- Updated user/setup/demo guides, limitations, reports, source ZIP/PDF/Markdown
  delivery and artifact hashes.

No native app code changed after the verified APK build. The debug APK is
retained and serves the new JavaScript through Metro. This is not a standalone
production build. No schema migration, policy relaxation, deletion of the iPhone
registration or automatic acceptance of hostel APs was introduced.

## Validation

| Check | Result |
| --- | --- |
| Backend | 120 passed |
| Mobile | 46 passed; TypeScript passed |
| Dashboard | 8 passed; production build passed |
| Native Wi-Fi | 10 passed |
| Automated total | 184, zero failures/skips |
| Physical review | Authenticated demo faculty API correction/resolution, database audit and student API verified |
| Phone history | PRESENT/CORRECTION and original PENDING REVIEW both observed |
| Artifacts | ZIP CRC/members/source hashes, PDF extraction, relative links and checksums verified |

Fresh evidence is in [local-2026-10-26](evidence/local-2026-10-26/).
The [physical report](ANDROID_DEVICE_VALIDATION_2026-10-26.md) records failures,
recovery, measured Wi-Fi values, execution method and limitations. The faculty
browser was opened but not used to execute the correction; this distinction is
preserved. No synthetic GPS experiment is presented as physical attendance.

## Pending work

Actual classroom APs/configuration and automatic inside/outside decisions remain
unverified. The hostel AP was outside the room, unlike the intended classroom.
The scan samples establish collection, not room-level accuracy. Broader biometric/
spoof/device testing, genuine attestation, five high mobile npm entries and
production operations remain gates. Backend vulnerability scanning is historical.

The history page's generic pending-review wording/review action and lack of clear
network timeouts remain known UX follow-ups. The official-record section is the
authoritative status after a correction.

## Publication and exclusions

The update uses ordinary commits and a PR merge, with no history rewriting.
The final publication commit contains this report and regenerated delivery files.
After merging/fetching, local main and origin/main must match and Git status must
be clean. The live PR is authoritative for the merge SHA.

Secrets, signing keys, raw UI captures, router identifiers, exact coordinates,
databases, face templates and raw frames stay local/ignored. Git publication does
not deploy a cloud service or replicate local database records. Older dated
reports retain their historical claims; current entry points link here.

```sh
git status --short --branch
git rev-parse main origin/main
git rev-list --left-right --count main...origin/main
```

The final main ahead/behind comparison should be `0 0`.
