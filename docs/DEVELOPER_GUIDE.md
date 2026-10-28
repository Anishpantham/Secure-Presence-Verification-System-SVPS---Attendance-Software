> Current checkpoint: [28 October audit](REPOSITORY_AUDIT_2026-10-28.md), [current status](CURRENT_STATUS.md), and [safe demo guide](EVALUATION_DEMO_GUIDE.md). Existing recovery installations must not run setup/seed/reset instructions intended for fresh databases. Dated counts below are historical unless explicitly rerun in [current test results](TEST_RESULTS.md).

# Developer guide

## Working directories

Use the existing repository checkout. Cloud tasks already run in an isolated workspace; do not create a Git worktree unless explicitly requested. Run backend commands in `backend`, frontend commands in `dashboard` and native commands in `mobile`. `.env` is at the repository root; backend settings read `../.env` by default. The cloud environment install/start configuration follows these same directories.

## Python workflow

`uv sync --project backend --frozen` installs the committed lockfile. Run `backend/.venv/bin` tools from the backend directory. Models and local runtime state live outside source packages in ignored `models` and `.runtime`. `alembic upgrade head` creates the schema; `alembic check` detects schema drift. Model changes require an explicit reviewed migration rather than application startup calling `create_all`.

Input contracts are in `app/schemas/contracts.py`. Auth and shared rate limits are in `core/security.py`. Route-level role dependencies are insufficient for faculty data: call `access_course` or use `session_ids` for object/query scope. Serialize access in the same lock order as verification when changing device or attendance behavior.

`services/vision.py` owns preprocessing, embeddings and temporal observations. A model replacement requires updating download provenance/checksums, dimensions, preprocessing and `MODEL_VERSION`, plus re-enrollment or a deliberate migration. Never accept a client-provided matching result. `services/presence.py` is deterministic and accepts measured evidence; add rule tests for every policy change.

## Web and mobile workflow

Use `npm ci`, not an unreviewed dependency refresh, for normal development. The web API wrapper holds tokens in memory and serializes refresh-token rotation. React Query invalidates data after mutations and polls active views. Charts read real aggregate API data. Shared form controls must preserve explicit labels and server errors.

The mobile API client rotates tokens and stores them in SecureStore. New signing uses the native P-256 module; legacy HMAC compatibility uses `@noble/hashes` with a Node interoperability test. Camera frames are resized to width 640, encoded as JPEG, submitted in memory and removed from the local camera cache. Permission denials and absent native modules return explicit unsupported/unavailable evidence. The Android module lives under `mobile/modules/spvs-wifi`; Expo autolinking must discover it in a development build. The iOS module exposes only permitted current-network BSSID and no RSSI scan.

## Tests and packaging

Run the commands in `docs/TESTING_STRATEGY.md`. Add security regression tests for authorization, challenge binding, concurrency and malformed input when changing relevant paths. The API tests' vision substitution is explicitly test-only; do not import that fixture into application code.

`scripts/package_final.py` generates final PDFs and a ZIP from actual source and documentation, excluding `.env`, dependency trees, local databases, native generated folders and live evidence. It verifies archive CRCs and PDF text/pages. Review `SPVS_FINAL_VERIFICATION_REPORT.md` before publishing a new package. No script should embed credentials or imply unrun phone tests have passed.


## Cross-platform completion update

Use Python 3.12, Node 22 or 24 compatible with the locked Expo version, JDK 17 and current Xcode on Apple Silicon. `make setup` preserves generated local secrets. `npm ci` honors each lockfile; `npx expo prebuild --no-install --no-clean` applies checked-in plugins/modules while preserving existing native projects. Expo 58 otherwise clears those directories by default. Do not edit generated iOS/Android projects as the only source of a fix. Run type checking, tests, both platform exports and native builds after changing module contracts. See [Mac validation](IOS_MAC_VALIDATION.md), CROSS_PLATFORM_IMPLEMENTATION.md and SETUP_AND_DEMO_GUIDE.md for platform-specific execution. Final packaging uses `scripts/package_final.py`; the earlier packaging script remains historical.
