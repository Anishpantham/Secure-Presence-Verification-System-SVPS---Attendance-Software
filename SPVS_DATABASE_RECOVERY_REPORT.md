# SPVS local database recovery incident

Checkpoint opened 28 October 2026; recorded 2026-10-28T23:56:47.529397+05:30.

## Objective

Record the local development recovery and verify current state without repeating restoration.

## Environment and procedure

User reports restoration from private `work/backups/spvs-before-qr-acoustic-20261026T184335Z.dump` into Docker PostgreSQL `spvs_recovery`, migration from 7a2d13ce4f90 to 9bd32a88f101 and host environment connection update. Faculty/Android/iOS login subsequently succeeded. The audit only ran read-only SQL aggregate/revision queries and Alembic current/heads/check. No backup bytes or private environment values are published.

## Expected and actual outcomes / evidence / status

| Check / expected | Actual | Source | Status |
| --- | --- | --- | --- |
| Restore original development data | User reports successful restore | User task narrative | Historical user-reported recovery |
| Current schema at head | 9bd32a88f101, no drift | Fresh SQL / Alembic checks | Automated check passed |
| Accounts retained | 4 users: admin, faculty, students | Fresh aggregate SQL | Verified current aggregate |
| Prior official records retained | 2 records | Fresh aggregate SQL | Verified current aggregate |
| Classroom C003 retained | User report and existing historical evidence | Task / C003 report | Historical corroboration |
| Login after recovery | Faculty and both phone platforms succeeded | User task narrative | User-reported pass |

## Known limitations

The audit did not witness the original restore or prove every restored byte against the old dump. Aggregate counts are not a full recovery checksum. No new classroom approval is inferred from historical records. The private backup remains in place.

## Follow-up actions

Keep backups private; rehearse restore into a new disposable target and retain encryption keys securely. [Safe database guide](docs/DATABASE_DESIGN.md). Never seed/reset or overwrite spvs_recovery.
