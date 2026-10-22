#!/usr/bin/env bash
# Run backend tooling with optional workspace-local Linux graphics libraries.
set -euo pipefail
SPVS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -d "$SPVS_ROOT/.runtime/native/usr/lib/x86_64-linux-gnu" ]]; then
  export LD_LIBRARY_PATH="$SPVS_ROOT/.runtime/native/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
export MPLCONFIGDIR="$SPVS_ROOT/.runtime/matplotlib"
mkdir -p "$MPLCONFIGDIR"
cd "$SPVS_ROOT/backend"
SPVS_COMMAND="$1"
shift
exec ".venv/bin/$SPVS_COMMAND" "$@"
