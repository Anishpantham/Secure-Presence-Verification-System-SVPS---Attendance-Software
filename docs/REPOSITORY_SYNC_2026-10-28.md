# Audit synchronization checkpoint — 28 October 2026

Starting local/default branch: main at 80a2d4d358f5dd61f09c2e0709771808ea4f759d,
matching origin/main after fetch. No open PR was found at discovery.
Audit branch: `spvs/final-audit-20261028`; target: `main`.

Publication commit/PR and CI are recorded after pushing; until then this document
does not claim remote publication. No merge is authorized or performed. The default
branch is intentionally unchanged while the review branch carries the audit.

Fresh validation: 234 tests passed, zero final failures/skips; dashboard/mobile
and native build checks passed. See [exact evidence](TEST_RESULTS.md).
Mobile advisories remain 4 high/5 low; backend frozen runtime advisory scan found zero known vulnerabilities.

Existing modified mobile/ios/Podfile.lock and release/final/SPVS_ANDROID_DEBUG.apk,
untracked editor settings and private environment backup are preserved and excluded
from the audit commit. The environment backup is now ignored. Native build outputs
stay private/ignored. Old archives and reports are retained with historical labels.

The recovered database received no seed/reset/restore/migration application during
this audit. Only the newly created disposable audit test database was migrated,
truncated and seeded. Current recovered aggregate counts are 4 users and 2 records.

## Current report exports

- [Academic report PDF](reports/SPVS_PROJECT_REPORT_2026-10-28.pdf).
- [Academic report DOCX](reports/SPVS_PROJECT_REPORT_2026-10-28.docx).
- [Export verification](evidence/final-audit-20261028/report-exports.json).

The Markdown source remains authoritative for interactive links and Mermaid
diagrams. Exports are dated; previous PDFs are retained. Institutional title-page
fields require student completion.

Reproduce current report exports with `backend/.venv/bin/python scripts/export_academic_report.py`. DOCX provides editable headings/text and a textual architecture description; the PDF contains a vector architecture diagram, and Markdown retains the full Mermaid source.
