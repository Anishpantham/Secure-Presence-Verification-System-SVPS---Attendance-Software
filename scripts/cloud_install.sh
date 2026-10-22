#!/usr/bin/env bash
# Reproducible setup for this Linux cloud workspace. Does not print secret values.
set -euo pipefail
SPVS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SPVS_ROOT"
export UV_CACHE_DIR=/workspace/.uv-cache
export npm_config_cache=/workspace/.npm-cache
export BUILDX_CONFIG=/workspace/.spvs-buildx
python3 scripts/init_env.py
uv sync --project backend --frozen
python3 scripts/download_models.py
python3 scripts/download_test_samples.py
npm ci --prefix dashboard --no-fund
npm ci --prefix mobile --no-fund
mkdir -p .runtime/native/usr/lib/x86_64-linux-gnu
if ! python3 -c 'import ctypes; ctypes.CDLL("libGLESv2.so.2"); ctypes.CDLL("libEGL.so.1")' 2>/dev/null && [[ ! -f .runtime/native/usr/lib/x86_64-linux-gnu/libGLESv2.so.2 ]]; then
  SPVS_LIB_CONTAINER="$(docker create python:3.12-slim sh -c 'apt-get update && apt-get install -y --no-install-recommends libgles2 libegl1')"
  trap 'docker rm -f "$SPVS_LIB_CONTAINER" >/dev/null 2>&1 || true' EXIT
  docker start -a "$SPVS_LIB_CONTAINER" > .runtime/native-libs-install.log 2>&1
  [[ "$(docker inspect -f '{{.State.ExitCode}}' "$SPVS_LIB_CONTAINER")" == 0 ]]
  for SPVS_LIBRARY in libGLESv2.so.2 libEGL.so.1 libGLdispatch.so.0; do
    docker cp -L "$SPVS_LIB_CONTAINER:/usr/lib/x86_64-linux-gnu/$SPVS_LIBRARY" ".runtime/native/usr/lib/x86_64-linux-gnu/$SPVS_LIBRARY"
  done
  docker rm "$SPVS_LIB_CONTAINER" >/dev/null
  trap - EXIT
fi
docker compose up -d db --wait
bash scripts/backend.sh alembic upgrade head
bash scripts/backend.sh python -m app.seed
if [[ "$(docker compose exec -T db psql -U spvs -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='spvs_test'")" != 1 ]]; then
  docker compose exec -T db createdb -U spvs spvs_test
fi
# Trust the environment's existing CA bundle without weakening TLS verification.
docker build --secret id=ca_bundle,src=/etc/ssl/certs/ca-certificates.crt -t spvs-backend -f backend/Dockerfile .
docker build --secret id=ca_bundle,src=/etc/ssl/certs/ca-certificates.crt -t spvs-dashboard dashboard
echo 'Dependencies, verified models, migrations, seed data and container images prepared.'
