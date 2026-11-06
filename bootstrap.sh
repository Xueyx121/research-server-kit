#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

if [[ "$(uname -s)" != "Linux" ]]; then
  printf 'This bootstrap script supports Linux servers only.\n' >&2
  exit 1
fi

if [[ -r /etc/os-release ]]; then
  # shellcheck disable=SC1091
  source /etc/os-release
else
  printf 'Cannot identify Linux distribution (/etc/os-release is missing).\n' >&2
  exit 1
fi

if [[ "${ID:-}" != "ubuntu" && "${ID:-}" != "debian" && "${ID_LIKE:-}" != *debian* ]]; then
  printf 'Detected %s. This script currently supports Ubuntu/Debian; install equivalents manually.\n' "${PRETTY_NAME:-unknown Linux}" >&2
  exit 1
fi

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=()
elif command -v sudo >/dev/null 2>&1; then
  SUDO=(sudo)
else
  printf 'Root access or sudo is required to install system packages.\n' >&2
  exit 1
fi

printf 'Installing system packages on %s...\n' "${PRETTY_NAME:-Linux}"
"${SUDO[@]}" apt-get update
"${SUDO[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential ca-certificates curl git pkg-config tar xz-utils \
  python3 python3-dev python3-pip python3-venv

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  printf 'Python interpreter not found: %s\n' "${PYTHON_BIN}" >&2
  exit 1
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -c 'import sys; assert sys.version_info >= (3, 9), "Python 3.9+ required"'
"${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel \
  --index-url "${PIP_INDEX_URL}"
"${VENV_DIR}/bin/python" -m pip install -r "${ROOT_DIR}/requirements.txt" \
  --index-url "${PIP_INDEX_URL}"

if [[ ! -e "${ROOT_DIR}/.env" ]]; then
  (umask 077; set -o noclobber; cat "${ROOT_DIR}/.env.example" > "${ROOT_DIR}/.env")
fi

printf '\nPython research packages installed.\n'
