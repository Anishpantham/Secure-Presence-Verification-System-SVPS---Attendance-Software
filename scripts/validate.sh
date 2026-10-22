#!/usr/bin/env bash
set -euo pipefail
SPVS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SPVS_ROOT"
mkdir -p artifacts
bash scripts/backend.sh alembic check
bash scripts/backend.sh pytest --junitxml=../artifacts/backend-tests.xml
(cd dashboard && npm test -- --run --reporter=junit --outputFile=../artifacts/dashboard-tests.xml && npm run build)
(cd mobile && npm run typecheck && npm test -- --run --reporter=junit --outputFile=../artifacts/mobile-tests.xml && CI=1 EXPO_NO_TELEMETRY=1 npm run export)
curl --fail --silent http://127.0.0.1:8000/ready
(cd dashboard && npx playwright test)
