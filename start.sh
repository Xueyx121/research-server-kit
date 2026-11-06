#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -x "$ROOT_DIR/.venv/bin/python" ]]; then
  bash "$ROOT_DIR/bootstrap.sh"
fi
exec "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/start.py" "$@"
