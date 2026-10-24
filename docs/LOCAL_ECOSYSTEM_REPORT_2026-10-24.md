# SPVS local ecosystem and GitHub synchronization report

**Audit date:** 24 October 2026, Asia/Kolkata. GitHub and local state were checked
starting at 19:54 IST; automated evidence was refreshed during this audit.
This report covers the local Mac continuation after the last published main
commit, including source changes, runtime state, builds, tests, documentation,
artifacts, omissions and the remaining synchronization work.

## 1. Main finding

**Local and GitHub are not fully synchronized.** The local working branch has
four unpublished commits plus further uncommitted changes. GitHub main contains
the prior cross-platform implementation, but none of the Mac continuation commits
or the newer enrollment/Wi-Fi fixes. The local application source includes the
new work and passes the checks recorded below. Physical Android verification,
classroom Wi-Fi configuration and production validation remain incomplete.

The local release folder also mixes a new Android APK with older source ZIP,
PDF and verification documents. This audit corrects current documentation and
the APK checksum, preserves historical evidence, and explicitly identifies the
remaining older deliverables. It does not publish, merge or deploy anything.

## 2. Exact Git position

Repository: [Secure Presence Verification System](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software).
It is public; default branch is `main`. GitHub metadata/branch/PR inspection and
a fresh Git fetch agreed with the local history comparison.

| Reference | Observed value |
| --- | --- |
| GitHub main / local origin/main | `3591220eb380b7d09a022362a4b9e44c6e684032` |
| Local main | Same `3591220` commit |
| Current local branch | `spvs/ios-native-completion` |
| Current local HEAD | `ac97c60941a13c02b9b197d52fd427adcf219e35` |
| Divergence from remote main | 4 local-only commits; 0 remote-only commits |
| Remote branch of the current name | Absent |
| Current branch upstream | Not configured |
| Staging area at audit start | Empty |
| Worktree at audit start | 21 tracked modified files + 7 untracked files = 28 file entries |
| Worktree after this documentation audit | 39 tracked modified files + 20 untracked files = 59 entries; all unstaged |
| Tracked file deletions at audit start | None |

GitHub main was committed on **23 October at 17:37:47 IST**. At the beginning
of this audit it was about **26 hours 17 minutes old**. The useful gap is the
four commits and pending file changes, not elapsed time alone. Local main matches
GitHub main but is older than the current working branch. Pulling main alone
would not upload or checkpoint the local work.

### Four local-only commits

| Commit | Time (23 October, IST) | Work recorded |
| --- | --- | --- |
| `f1b23f5` | 19:51:22 | Native iOS simulator validation on Apple Silicon, locks, configuration and build workflow |
| `8f699d9` | 23:26:27 | iOS Wi-Fi capability becomes opt-in for supported signing teams |
| `428975e` | 23:32:03 | Trusted launch on a physical iPhone |
| `ac97c60` | 23:47:29 | Physical iPhone login and native device registration |

These commits change 18 paths relative to main, with 3,201 insertions and 45
deletions of text lines, largely including the resolved native lockfiles. Those
line deletions do not mean entire features or files were removed.

### What GitHub currently has

The remote branches are `main`, `spvs/complete-implementation-20261022` at
`0ddd78a68d55c37c09704ac9d3880359e07520b2`, and
`spvs/final-completion-cross-platform` at
`c1e04f09a42c54aa71fc96e68549420c997c7386`.
[PR #1](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/1),
[PR #2](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/2),
and [PR #3](https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software/pull/3)
are merged/closed. No PR exists for this local continuation. The older checkpoint's
description of PR #2 as a draft is historical and no longer current.

No GitHub Actions workflow files are tracked in the inspected main/current trees.
Local passing tests therefore must not be described as a current GitHub CI run.
GitHub is verified here as source hosting. A separate live cloud application or
database deployment was not inspected; the old cloud build environment is not
evidence of a current production deployment.

## 3. New work in the local ecosystem

### Apple Silicon and native iOS

- Preserved the FastAPI/PostgreSQL, React dashboard and Expo/React Native architecture.
- Installed/resolved CocoaPods and Ruby dependencies and retained `Gemfile.lock`
  and `Podfile.lock`. Generated native projects remain excluded except that lock.
- Built the iOS simulator app and the signed physical-device app. The device
  launch needed the user's developer-profile trust step before succeeding.
- Confirmed physical iPhone login and signed P-256 device registration. The
  client reports Secure Enclave storage; that is not genuine Apple attestation.
- Made Wi-Fi Information an explicit opt-in because the selected Personal Team
  could not provision it. Native current-network code remains present.
- Added `--no-clean` to Expo prebuild to preserve native signing settings and locks.
- Removed unused iOS microphone, Face ID, motion and always-location descriptions
  from the generated configuration. Camera, foreground location and local-network
  access remain. These configuration changes did not remove face verification.

See [iOS Mac validation](IOS_MAC_VALIDATION.md) for the historical build commands,
signing/profile details and the new dated enrollment/attendance evidence.

### Enrollment, liveness and retry fixes

- Corrected the unmirrored camera convention: a person's left turn moves their
  nose toward image-right. The server now maps that displacement to the person's
  requested direction.
- Added photo-driven open/closed/reopen blink phases and a vibration to reopen
  the eyes. Each new prompt gets 700 ms to settle before capture.
- Moved the instruction above the camera and displays progress through the five
  requested poses. Missed-step errors identify the requested turn, center or blink.
- Allows at most two missing-landmark frames, with at least eight tracked frames
  still required. A tracking gap resets incomplete pose/blink progress. Every
  frame still undergoes image quality, single-face detection and identity checks.
- Kept the face-match threshold and challenge/signature/consent requirements.
- Added bounded stage/count diagnostics without retaining raw face frames or
  returning biometric vectors/landmark coordinates.
- Added typed API errors, parsing of `Retry-After`, a retry countdown and prevention
  of duplicate capture starts. Definitive 4xx errors discard the saved rejected
  request; network/5xx failures can retain it for idempotent recovery.
- Rate limiting now reports the remaining window rather than the full window on
  every rejection. Attempt limits were not removed or increased.

See [biometric design](BIOMETRIC_DESIGN.md) and [API documentation](API_DOCUMENTATION.md).

### Android Wi-Fi and build tooling

- Replaced the immediate-read scan flow with asynchronous completion handling.
  Readings no older than 15 seconds may be reused; otherwise the app waits up to
  eight seconds for a successful system scan broadcast.
- Shares concurrent scan requests, cleans up listeners/timeouts, and returns an
  explicit unavailable/permission-denied result when evidence cannot be obtained.
- Filters stale/future readings, malformed or placeholder BSSIDs, and invalid
  signal values. Deduplicates APs and retains up to 50 strongest valid readings.
- Requests coarse and fine location together and requires precise permission.
- Adds **Settings > Wi-Fi setup check** to display actual BSSID/RSSI evidence
  locally, without submitting attendance or automatically trusting an AP.
- Added 10 Kotlin lifecycle/filtering tests and additional mobile adapter tests.
- Installed Java 17 and official Android CLI/SDK/native build tools on this Mac.
  Gradle's timed-out download was retried through its official URL and checked
  against the official SHA-256 before use.
- Added an Android build task, automatic detection of the Homebrew JDK/local SDK,
  and optional target architecture selection. Corrected the build script's empty
  array handling for macOS Bash with `set -u`.
- Built and signature-verified a new arm64 development APK. This is not a
  standalone production build and has not been installed on an Android phone yet.

See [Android Mac validation](ANDROID_MAC_VALIDATION.md) and the
[Wi-Fi field procedure](TESTING_STRATEGY.md#android-wi-fi-setup-and-field-test).

## 4. What was removed, replaced or retained

| Item | Actual change |
| --- | --- |
| Entire tracked source files | None deleted in the local continuation inventory |
| Immediate Android scan-result read | Replaced by recent-cache reuse or awaited completion |
| Unconditional iOS Wi-Fi entitlement | Removed from the default Personal Team configuration; supported-team opt-in retained |
| Unused iOS permission descriptions | Removed as listed above; not a removal of identity/presence verification |
| Generic rejected-request retry | Replaced by status-aware recovery; rejected challenges cannot be replayed |
| Failure on any landmark miss | Replaced by bounded recovery with complete sequence and per-frame identity checks |
| Prior working-copy APK | Replaced by the new native build; the previous bytes remain in Git history |
| Historical ZIP/PDF/packaged MD files | Preserved; they remain older snapshots |
| Backend models and face threshold | Retained; no fabricated face scores or weaker matching threshold |
| Wi-Fi/GPS review policies | Retained; no automatic GPS-only approval enabled |
| Database schema | No new migration introduced by these local fixes |
| Historical test evidence | Retained; new evidence has a separate dated directory |

## 5. Real local runtime changes and observations

These are local database/device actions, not changes that a Git push transfers.

- A local PostgreSQL cluster under `.runtime/postgres` contains separate `spvs`
  and `spvs_test` databases. Application tests use the guarded test database.
- The API and Metro had stopped during testing; both were restarted, and health,
  model readiness and served mobile bundles were verified.
- Physical iPhone device registration is recorded at 23 October 23:45:13 IST.
- The user confirmed successful, easier face enrollment. The database records
  `BIOMETRIC_ENROLLED` on **24 October at 14:37:27 IST**.
- The local demo classroom's placeholder location was replaced by the user's
  supplied test pin, retaining a 50 m radius. Precise coordinates are deliberately
  excluded from this shareable report and remain local database configuration.
- Opened a one-hour CS401 test session, ending **24 October at 15:39:40 IST**.
  It has expired; the audit observed zero active sessions. A fresh session will
  be needed for the next attendance test.
- One physical iPhone attendance attempt at **14:43:49 IST** passed identity,
  liveness and GPS gates, then returned `PENDING_REVIEW` with reason
  `IOS_PRESENCE_REVIEW_REQUIRED`. Distance was 3.7 m with about 9.27 m reported
  horizontal uncertainty.
- That attempt contained `wifi_status=unavailable`, `wifi_source=none`,
  `presence_assurance=GPS_ONLY`, and no App Attest assertion. There are **zero
  official attendance records** for the demo student at this checkpoint.
- The classroom has **zero configured Wi-Fi AP references**. The signed iPhone
  app has no Wi-Fi Information or App Attest entitlement. The selected iOS
  policy requires review even if a current network matches.
- ADB reported **no connected Android device**. No Android scan readings,
  phone enrollment, classroom acceptance or outside-room rejection are claimed.

The [sanitized runtime evidence](evidence/local-2026-10-24/runtime-summary.json)
contains only the scoped status/timing/decision information. It omits names,
student/device IDs, exact coordinates, credentials, keys, templates and frames.

## 6. Local environment and persistence boundaries

| Component | Observed local state |
| --- | --- |
| Workspace | `/Users/anishpantham/Downloads/SPVS/SPVS` |
| Host | Apple Silicon arm64, macOS 27.0 (26A428); user identifies MacBook Air M4 |
| Xcode | 27.1 (27A9275) |
| Node / npm | 24.13.0 / 11.6.2 |
| Python | Backend virtual environment, Python 3.12.8 |
| PostgreSQL | Homebrew 16.15, loopback database access |
| Mobile dependencies | Expo 58.0.17, React Native 0.88.0, React 19.3.0, TypeScript 6.0.3 |
| Ruby / CocoaPods | Previously observed Ruby 3.3.13, Bundler 4.0.23, CocoaPods 1.16.2; locks retained |
| Java | Homebrew OpenJDK 17.0.21 |
| Android | SDK platform 37.0, build tools 37/36, NDK 27.1.12297006, CMake 3.22.1 |
| Gradle / Kotlin | 9.4.1 / observed build plugin 2.2.10 |
| ADB | Platform tools 37.0.1 |
| API / Metro | Both reachable during audit: API health/readiness HTTP 200, models loaded; Metro running |
| Dashboard | Production bundle freshly built; local port 5173 was not listening at audit |

`.runtime`, backend `.venv`, `node_modules`, `work`, generated native projects,
native build caches and environment files are deliberately excluded from Git.
These may exist locally even when Git reports no change. Local models are also
ignored and obtained using checksum-verified download scripts. The old source ZIP
includes model assets, but the Git repository does not rely on committing them.

Local environment files, demo passwords, signing identities/provisioning data,
private keys, database files and biometric templates must not be added to source
control or copied into the report. No such contents were included in this audit.
The public repository's absence of these files is intentional, not a sync defect.
The [service snapshot](evidence/local-2026-10-24/services.json) records the exact
probe time and results. Running services can stop when their terminals close.

## 7. Current validation evidence

| Check | Result and boundary |
| --- | --- |
| Full backend suite, fresh audit run | 120 passed, 0 failures, 0 skipped; includes real-model smoke cases and mocked-vision API contracts |
| Mobile Vitest, fresh audit run | 42 passed, 0 failures; OS/native interfaces are mocked in these tests |
| Dashboard Vitest, fresh audit run | 8 passed, 0 failures |
| Native Kotlin Wi-Fi suite | 10 passed, 0 failures, 0 skipped; callback/filtering logic, not physical radio validation |
| Total above | 180 passing automated tests across these four distinct suites |
| Mobile TypeScript | Passed during Android implementation validation |
| Dashboard production build | Passed again during this audit |
| Android native debug build | Passed in 6m 50s; arm64-v8a; APK signature verification passed |
| Metro Android/iOS bundle requests | HTTP 200 observed during the local continuation |
| iOS native builds | Prior local Mac simulator and signed-device builds passed; not rebuilt during this documentation audit |
| Browser end-to-end | Historical 3 passing cases; not rerun during this audit and not added to the total above |
| Containers / migration cycle | Historical cloud evidence retained; not rebuilt or rerun as a production deployment in this audit |
| Physical iPhone | One enrollment success and one pending-review attendance submission observed |
| Physical Android | Pending |

Current JUnit evidence: [backend](evidence/local-2026-10-24/backend-tests.xml),
[mobile](evidence/local-2026-10-24/mobile-tests.xml),
[dashboard](evidence/local-2026-10-24/dashboard-tests.xml),
[native Wi-Fi](evidence/local-2026-10-24/android-wifi-tests.xml).
Earlier focused runs (35/40 mobile or 54/83 backend tests) are superseded for
current counts; repeated runs are not additional independent tests.

Deprecation warnings remain in upstream Starlette/httpx, React test renderer,
Vite configuration and Gradle/React Native/Expo APIs. A passing build is not a
warning-free build. Unit tests and one person's phone success do not establish
biometric accuracy, spoof resistance, classroom discrimination or production scale.

## 8. Dependency security and version freshness

Fresh `npm audit` results are [mobile](evidence/local-2026-10-24/mobile-audit.json)
and [dashboard](evidence/local-2026-10-24/dashboard-audit.json).

- Mobile: **5 high-severity affected package entries**, zero critical/moderate/low.
  The entries are `@expo/cli`, `@expo/code-signing-certificates`, `expo`,
  `node-forge` and `zod`. The direct advisory records identify
  [node-forge GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv)
  and [Zod GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5).
  The count includes propagated dependencies, not five distinct root advisories.
- Dashboard: zero findings in the current npm audit.
- Backend: the historical runtime audit reported zero, but `pip-audit` is not
  installed in this local virtual environment and was not rerun here. This is
  explicitly not a current backend vulnerability clearance.
- No package upgrades or forced downgrades were performed during this audit.
  npm's proposed Expo 44 downgrade is incompatible with the current app and was
  not applied. The changed advisory count does not mean this audit patched packages.

"Up to date" here means the state is accurately recorded and checked against
GitHub; it does not mean every dependency is the latest release or all security
and production work is complete. Compatible dependency remediation needs its own
review and validation before distribution.

## 9. Artifact currency and integrity

| Artifact | Current disposition |
| --- | --- |
| Android debug APK | Rebuilt locally, 77,979,730 bytes; native scan fix included; arm64 development client |
| Final source ZIP | 39,896,439 bytes, 179 entries, CRC valid; historical source snapshot |
| Final project PDF | Historical 36-page report; not regenerated from current source |
| Final setup PDF | Historical 12-page guide; not regenerated from current source |
| Packaged final MD documents | Historical and unchanged; folder status file identifies their age |
| FILE_MANIFEST / FINAL_FILE_MANIFEST | Historical source file/hash inventories; regenerate with the next coordinated release |
| Current ecosystem report + PDF | Newly produced from this audit |
| Artifact checksum metadata | Corrected for the new APK and annotated with mixed snapshot dates |

Current APK SHA-256:
`9bd8032bc87b6f74fc86a2fe11897915fcd598081f514473c424294ec54cd3d6`.
The old APK hash was
`0c3bc2a1d938e0ce49b3e84ec56d4efd4376d8e332e9f1f10859e610cd478e9e`.
All other original final-artifact hashes matched their stored records at audit.

The old ZIP lacks the new iOS validation record, Android validation record,
Wi-Fi diagnostics, API error helper, CocoaPods lock and Ruby lock. Thus an
integrity-valid ZIP is still outdated. It has not been passed off as the source
for the newer APK. The packaging selector was corrected to include the tracked
`mobile/ios/Podfile.lock` while keeping generated native projects excluded; the
next coordinated package must be regenerated from the intended checkpoint.

See [release folder status](../release/final/CURRENT_STATUS.md) and
[artifact verification](../release/final/artifact-checks.json). There is no
claimed production-signed APK or packaged IPA. Previous published APK bytes are
recoverable from Git; the local working-copy APK was replaced, not preserved at
a second historical filename.

## 10. File-level inventory

The [machine-readable repository inventory](evidence/local-2026-10-24/repository-state.json)
lists every final modified/untracked path, remote/local SHAs, the four commits,
and paths changed in those commits. It is a point-in-time snapshot and will age
after subsequent edits. The audit added documentation/evidence beyond the 28
starting entries; those new files are also not yet committed or on GitHub.

### Source and test changes pending at audit start

| Paths | Purpose |
| --- | --- |
| `backend/app/api/verification.py` | Enrollment audit and allowlisted failure details |
| `backend/app/core/security.py` | Remaining-window Retry-After |
| `backend/app/services/vision.py` | Direction mapping, bounded landmark recovery, diagnostic frame index |
| `backend/tests/test_presence_and_liveness.py`, `test_security_workflows.py`, `test_verification_api.py`, `test_vision_models.py` | Updated server regressions and real-model boundary check |
| `backend/tests/test_capture_recovery.py` (new) | Direction, recovery and identity-check regressions |
| `mobile/App.tsx`, `src/capture.ts`, `src/protocol.ts` | Capture timing/cues, progress, retry UX and Wi-Fi settings card |
| `mobile/src/api.ts`, `src/apiErrors.ts` (new helper) | Typed HTTP failures, retry delay and diagnostic propagation |
| `mobile/src/platform/index.ts` | Android permissions and honest evidence-source status |
| `mobile/src/WifiDiagnostics.tsx` (new) | Local-only Wi-Fi setup screen |
| `mobile/modules/spvs-wifi/android/src/main/java/edu/spvs/wifi/SpvsWifiModule.kt` | Android scan bridge and lifecycle |
| `mobile/modules/spvs-wifi/android/src/main/java/edu/spvs/wifi/WifiScanSession.kt` (new) | Bounded scan coordination and reading filtering |
| `mobile/modules/spvs-wifi/android/src/test/java/edu/spvs/wifi/WifiScanSessionTest.kt` (new) | Ten native unit tests |
| `mobile/modules/spvs-wifi/android/build.gradle` | JUnit test dependency |
| `mobile/tests/api.test.ts` (new), `capture.test.ts`, `platform.test.ts` | HTTP, prompt, permission and scan-source regressions |
| `.vscode/tasks.json`, `scripts/build_mobile_macos.sh` | Repeatable Android build and local tool discovery |
| `docs/BIOMETRIC_DESIGN.md`, `docs/TESTING_STRATEGY.md`, `docs/ANDROID_MAC_VALIDATION.md` (new record) | Design, test boundaries and Android build evidence |
| `release/final/SPVS_ANDROID_DEBUG.apk` | Rebuilt native development binary |

### Documentation and local corrections made by this audit

- Added this report, its PDF, [CURRENT_STATUS.md](CURRENT_STATUS.md), dated JSON/XML
  evidence and an exact Git inventory.
- Updated README entry points, current test results and known limitations so
  historical "no iPhone/Xcode testing" statements no longer describe today's state.
- Added physical enrollment/attendance evidence to the iOS validation record.
- Updated cross-platform design, user manual, API documentation and local setup
  guidance for the new capture and Wi-Fi behavior.
- Marked old completion/delivery/checkpoint documents as historical and linked
  them to current state, retaining their original run details.
- Corrected APK checksum metadata and added an explicit mixed-age delivery notice.
- Corrected the future source-package selector for the retained CocoaPods lock.
- Fixed the PDF renderer's missing monospace font-family mapping on Macs without
  DejaVu fonts; the failure was reproduced while rendering this report, then the
  actual PDF was regenerated and checked for readable text.
- Did not commit, push, merge, alter verification policy, regenerate historical
  ZIP/PDF releases, or copy runtime secrets/database state into the repository.

## 11. What GitHub is missing

1. The four Mac/iPhone continuation commits and their 18 changed paths.
2. Current face capture, turn-direction, bounded tracking recovery and retry fixes.
3. Current backend diagnostics and the corresponding regressions.
4. Android asynchronous scan handling, native tests, permissions and diagnostics UI.
5. The local Android build task/script refinements and newly built APK.
6. Today's physical iPhone enrollment/attendance evidence and Android build evidence.
7. This audit, current status/index, updated documentation, fresh test/audit results
   and corrected artifact metadata.

GitHub should **not** receive the local database, biometric templates, secret
environment files, signing keys, generated native build trees or dependency caches.
No live cloud database synchronization is implied by bringing source branches
up to date.

## 12. Completion and publication checklist

| Work item | State / next action |
| --- | --- |
| Local source and unit/build checks | Current work is present and the recorded checks pass |
| Local documentation | Updated by this audit; use the current index rather than historical final reports |
| Git checkpoint | Pending: review and commit tracked modifications plus all intended new source/docs/evidence files |
| Remote publication | Pending: push `spvs/ios-native-completion` with upstream, then open a reviewed PR into main |
| Main synchronization | Pending: merge only after review; then refresh the local main branch |
| Coordinated release package | Pending: regenerate source ZIP/PDF reports from a named checkpoint and verify checksums together |
| Android physical test | Connect phone, install APK, sign in and run Wi-Fi setup check; no scan results yet |
| Classroom Wi-Fi references | Confirm actual institution APs and collect inside/corridor/adjacent-room RSSI before configuring thresholds |
| Next attendance session | Previous demo session expired; create a fresh bounded test session when the phone is ready |
| Android full attendance | Use a separate test student or the explicit audited device reset flow to preserve one-device binding |
| iPhone network capability | Supported provisioning and actual network references are still required; paid membership does not provide general scans |
| Automatic iPhone Wi-Fi approval | No such mode is implemented; needs a separately reviewed policy/design with real evidence |
| Genuine provider attestation | Apple App Attest and Play Integrity still need configuration and physical/provider verification |
| Production readiness | Calibration, spoof evaluation, reliable classroom discrimination, compatible security updates, TLS, operational controls and load testing remain |

A future publication can use `git push -u origin spvs/ios-native-completion`
**after** the new work is committed. Pushing now would publish only the four
existing commits, not the uncommitted fixes or this report. Do not force-push.
No publication was performed as part of this documentation request.

## 13. Evidence interpretation

GitHub SHA/branch/PR state came from live GitHub tools and a fresh fetch. Local
file and commit state came from Git. Test counts came from actual JUnit results;
build outcomes came from actual tool execution. Enrollment/attendance status came
from a sanitized read-only local database query and the user's physical-phone
confirmation. Historical build details remain explicitly attributed to their
dated validation documents. Missing tests, deployments and provider integrations
are labelled unverified rather than inferred from successful compilation.
