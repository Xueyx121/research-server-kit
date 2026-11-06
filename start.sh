#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$ROOT_DIR/.tools/node/bin:$ROOT_DIR/.tools/bin:$PATH"
bash "$ROOT_DIR/setup.sh"
exec "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/start.py" "$@"
