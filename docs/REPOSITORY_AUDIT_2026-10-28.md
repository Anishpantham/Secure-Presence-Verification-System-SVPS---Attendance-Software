# Repository audit — 28 October 2026

## Discovery before edits

Local root: SPVS workspace. Starting branch `main`, HEAD
`80a2d4d358f5dd61f09c2e0709771808ea4f759d`. A successful `git fetch origin`
confirmed this matched `origin/main`; default branch is `main`. GitHub search
returned no open pull requests. Existing remote feature/release branches were
inspected and retained. No repository AGENTS.md or tracked GitHub workflow was found.
Work proceeds on `spvs/final-audit-20261028`; merging is not authorized.

Existing modifications: `mobile/ios/Podfile.lock`, `release/final/SPVS_ANDROID_DEBUG.apk`.
Existing untracked files: `.env.before-recovery-switch`, `.vscode/settings.json`.
These are preserved and excluded from the audit commit. Environment contents are private.
Historical reports, archives and backups are retained.

## Findings and actions

| Finding | Action / boundary |
| --- | --- |
| Current pages say physical QR/audio testing has not started | Replace with dated user-reported results; keep historical checkpoints |
| README encourages seeding without distinguishing recovery | Separate existing/recovered startup from fresh disposable setup |
| Compose backend overrides host DATABASE_URL with hardcoded original DB | Add SPVS_BACKEND_DB selection; do not change running services or local secrets |
| Compose healthcheck hardcodes DB/user | Use container POSTGRES_DB/POSTGRES_USER |
| Environment backup is unignored | Ignore environment variants, preserving example templates |
| Academic report has old table count and iOS GPS-only policy | Update from current models, migrations and policy-v2 implementation |
| OpenAPI response models are mostly unspecified | Publish actual endpoint/request inventory and explicitly document schema gaps |
| Browser suite edits classroom coordinates | Isolate before execution; never target recovered runtime |
| Native build helper overwrites the locally modified APK | Use direct native builds without copying over that artifact |
| No genuine App Attest/Play Integrity validation | Keep as release gate; login is not integrity evidence |

Reviewed backend routes, contracts, auth, device binding, verification, QR/audio,
presence, vision, migration/test harness, mobile native/configuration and client
flows, dashboard challenge controls, scripts and reports. This is a source and
test audit, not an independent penetration test or security certification.

## Recovery check

Read-only SQL on Docker PostgreSQL `spvs_recovery` confirmed revision
`9bd32a88f101`, 4 users (1 admin, 1 faculty, 2 students), and 2 records.
No account names, credentials, coordinates, BSSIDs or biometric data are published.
The recovery operation itself is user-reported; this audit did not restore anything.

## Validation safety

Backend fixtures migrate/truncate only a newly created `spvs_audit_20261028_test`
database via an explicit SPVS_TEST_DATABASE_URL. The recovered database is never
used for tests, seeds, resets or migration application. Current/heads/check are
inspection operations. Detailed fresh results are in [test results](TEST_RESULTS.md).
