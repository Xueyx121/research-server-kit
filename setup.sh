#!/usr/bin/env bash
# Install once; safe to rerun after an interrupted download or installation.
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$ROOT_DIR/.tools/node/bin:$ROOT_DIR/.tools/bin:$PATH"
trap 'printf "Setup stopped. Fix the reported error, then rerun bash setup.sh.\n" >&2' ERR

if [[ "$(uname -s)" != Linux ]]; then
  printf 'This installer supports Ubuntu/Debian Linux servers.\n' >&2
  exit 1
fi

requirements_hash="$(cat "$ROOT_DIR/requirements.txt" "$ROOT_DIR/bootstrap.sh" | sha256sum | awk '{print $1}')"
marker="$ROOT_DIR/.venv/.research-kit-packages"
if [[ ! -f "$marker" ]] || [[ "$(cat "$marker")" != "$requirements_hash" ]] || \
   ! "$ROOT_DIR/.venv/bin/python" -c 'import numpy, pandas, scipy, sklearn, matplotlib, seaborn, jupyterlab, ipykernel, requests, httpx, dotenv, openai' >/dev/null 2>&1; then
  bash "$ROOT_DIR/bootstrap.sh"
  printf '%s\n' "$requirements_hash" > "$marker"
fi

bash "$ROOT_DIR/scripts/install_node.sh"
if ! command -v codex >/dev/null 2>&1 || ! codex --version >/dev/null 2>&1; then
  installed=false
  for registry in "${CODEX_NPM_REGISTRY:-https://registry.npmmirror.com}" https://registry.npmjs.org; do
    printf 'Installing Codex CLI from %s...\n' "$registry"
    if npm install --global --prefix "$ROOT_DIR/.tools" @openai/codex \
      --registry="$registry" --fetch-retries=1 --fetch-timeout=60000 && \
      "$ROOT_DIR/.tools/bin/codex" --version; then
      installed=true
      break
    fi
  done
  if [[ "$installed" != true ]]; then
    printf 'Codex installation failed. Check npm mirror connectivity.\n' >&2
    exit 1
  fi
fi
printf 'Environment ready. Run bash start.sh to launch (Sorux by default).\n'
