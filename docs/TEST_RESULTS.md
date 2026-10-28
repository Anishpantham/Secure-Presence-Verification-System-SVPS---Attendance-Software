# Fresh test and validation results

Audit opened 28 October 2026; results recorded `2026-10-28T23:56:47.529397+05:30`. Platform: macOS arm64,
project Python 3.12.8, locked client dependencies, Docker PostgreSQL 16.
These are freshly executed results, not reused historical counts.

| Suite | Passed | Failed/errors | Skipped |
| --- | ---: | ---: | ---: |
| backend | 146 | 0 | 0 |
| dashboard | 11 | 0 | 0 |
| mobile | 64 | 0 | 0 |
| browser | 3 | 0 | 0 |
| android-wifi | 10 | 0 | 0 |


Unique final suite total: **234 passed, 0 failed, 0 skipped**. The 146 backend
cases include seven real-model cases and API/integration/security cases; do not
count those categories again. Native Wi-Fi tests were explicitly rerun after the
build initially reported them UP-TO-DATE. No test expectations were changed.

## Commands, exit codes and evidence

Commands ran from the root unless noted. Private wrappers constructed DB URLs
from the existing private environment in memory; no credential-bearing command
or connection URL is published. Test target was explicitly spvs_audit_20261028_test.

| Check | Executed command / configuration | Final exit |
| --- | --- | ---: |
| Backend | `backend/.venv/bin/python work/final-audit-20261028/run_backend.py`; executes `bash scripts/backend.sh pytest --junitxml=../docs/evidence/final-audit-20261028/backend-tests.xml` with SPVS_TEST_DATABASE_URL explicitly targeting audit DB | 0 |
| Dashboard unit/UI | `npm test --prefix dashboard -- --run --reporter=junit --outputFile=../docs/evidence/final-audit-20261028/dashboard-tests.xml` | 0 |
| Mobile unit/UI | `npm test --prefix mobile -- --run --reporter=junit --outputFile=../docs/evidence/final-audit-20261028/mobile-tests.xml` | 0 |
| Dashboard build | VS Code task: `npm run build --prefix dashboard` | 0 |
| Mobile types | `npm run typecheck --prefix mobile` | 0 |
| Bundles | VS Code task: `npm run export --prefix mobile` (Android and iOS) | 0 |
| Android arm64 | In mobile/android: `./gradlew :spvs-wifi:testDebugUnitTest :app:assembleDebug -PreactNativeArchitectures=arm64-v8a --no-daemon` | 0 |
| Fresh native tests | In mobile/android: `./gradlew :spvs-wifi:cleanTestDebugUnitTest :spvs-wifi:testDebugUnitTest --no-daemon` | 0 |
| iOS simulator | `xcodebuild -workspace mobile/ios/SPVSStudent.xcworkspace -scheme SPVSStudent -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath work/audit-ios-derived CODE_SIGNING_ALLOWED=NO build` | 0 |
| Browser | Private isolated runner executes `npx playwright test --config work/final-audit-20261028/playwright.config.mjs` (absolute config path, dashboard cwd); API 8011, dashboard 5174, disposable audit DB | 0 |
| Migration status | `bash scripts/backend.sh alembic current`; `heads`; `check` | 0 each |
| Compose | `docker compose config --quiet` | 0 |
| Dependency advisories | `npm audit --prefix mobile --json`; dashboard equivalent | mobile 1; dashboard 0 |

Android environment used JDK 17, workspace .runtime/android-sdk and .runtime/gradle.
Native builds left the pre-existing modified release APK and Podfile.lock untouched.
Signed iOS device compilation/installation was not repeated; simulator build is
not physical validation. Mobile has no lint script/configured lint command; lint
is **not run**, not passed. After installing pip-audit in the project environment, the frozen runtime requirements
were audited: zero known vulnerabilities, exit 0. This is advisory coverage at scan
time, not a guarantee of absence of vulnerabilities.

## Isolation and reproduction

Create a new disposable *_test database, set SPVS_TEST_DATABASE_URL privately to
that database, then run the backend command above. The fixture validates the suffix
but truncates its target, so suffix alone is not permission to use meaningful data.
For browser checks seed only that disposable DB, run a separate API at 8011 with
DATABASE_URL pointing to it, proxy an isolated Vite server at 5174 to 8011 and set
Playwright baseURL to 5174. Keep all recovered services/coordinates untouched.
The audit's private runner terminated its isolated servers after testing.

## Failures and warnings

Initial sandbox attempts could not read Git configuration, launch Node/Docker or
load Python's framework (Python exit 134). Approved retries executed normally.
The initial browser run had three launch failures (exit 1): required Chromium was
missing. `npx playwright install chromium` installed the required version; the
unchanged suite then passed all three cases. These were environment failures,
not successful tests or application failures. Initial logs remain private locally.

Warnings: Starlette TestClient httpx deprecation; Vite future native config-loader
compatibility; deprecated Gradle features before Gradle 10; Xcode dependency/run
script warnings; Playwright NO_COLOR/FORCE_COLOR warning. They did not fail builds.

## Evidence and interpretation

Fresh sanitized [results ledger](evidence/final-audit-20261028/results.json) and JUnit:
[backend](evidence/final-audit-20261028/backend-tests.xml),
[dashboard](evidence/final-audit-20261028/dashboard-tests.xml),
[mobile](evidence/final-audit-20261028/mobile-tests.xml),
[native Wi-Fi](evidence/final-audit-20261028/android-wifi-tests.xml),
[browser](evidence/final-audit-20261028/browser-tests.xml).
Raw native/runtime logs remain in ignored local work; no signing material or raw
sensor captures are published. XML hostnames/local path prefixes are sanitized.

Objective: verify implementation without modifying recovered data. Expected:
unchanged tests/builds pass on isolated fixtures. Actual: table above. Status:
automated-test passed, with unresolved dependency findings and manual gates.
Follow-up: [evaluation checklist](EVALUATION_CHECKLIST.md). User-reported physical
observations are separately documented in the platform reports.

## Backend advisory scan follow-up

Installed pip-audit only in the local tooling environment; project dependency locks
were unchanged. Executed `uv export --project backend --frozen --no-dev
--no-emit-project --format requirements-txt --output-file
work/final-audit-20261028/backend-requirements.txt`, then
`backend/.venv/bin/python -m pip_audit -r
work/final-audit-20261028/backend-requirements.txt --no-deps --disable-pip
--format json --output docs/evidence/final-audit-20261028/backend-audit.json`.
Both exited 0; zero known vulnerabilities. pip-audit warned about using --no-deps;
input was exported from the frozen complete runtime lock. This excludes dev tools.

## Documentation, configuration and publication checks

Local Markdown file-link check: 331 resolved, zero missing at the pre-publication
checkpoint (external URLs and anchors excluded). Staged blob secret/path scan:
58 intended files, zero known-private-value or credential/key-pattern findings.
`git diff --cached --check` exited 0 after fixing trailing blank lines. Compose
JSON validation with SPVS_BACKEND_DB=spvs_recovery confirmed target database and
container host db without printing credentials or starting services. Editor
diagnostics reported no errors in the Compose file or report export script.
PDF: eight pages with extractable text and vector architecture; DOCX: valid ZIP/XML
and recognized by macOS textutil. Export hashes are in the evidence directory.
GitHub publication has no workflow/status result; local test success is not remote CI.
