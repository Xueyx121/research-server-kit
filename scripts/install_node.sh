#!/usr/bin/env bash
# Use a compatible existing Node, otherwise install a verified local runtime.
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$ROOT_DIR/.tools/node/bin:$PATH"
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1 && \
   node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)' && \
   npm --version >/dev/null 2>&1; then
  exit 0
fi

case "$(uname -m)" in
  x86_64) node_arch=x64 ;;
  aarch64|arm64) node_arch=arm64 ;;
  *) printf 'Unsupported CPU architecture: %s\n' "$(uname -m)" >&2; exit 1 ;;
esac
mkdir -p "$ROOT_DIR/.tools"
temp_dir="$(mktemp -d "$ROOT_DIR/.tools/node-install.XXXXXX")"
trap 'rm -rf "$temp_dir"' EXIT
for source_url in "${NODE_DIST_MIRROR:-https://npmmirror.com/mirrors/node}" https://nodejs.org/dist; do
  source_url="${source_url%/}"
  printf 'Downloading Node.js 22 (%s) from %s...\n' "$node_arch" "$source_url"
  if ! curl -fLsS --retry 1 --connect-timeout 10 --max-time 60 \
    "$source_url/latest-v22.x/SHASUMS256.txt" -o "$temp_dir/SHASUMS256.txt"; then
    continue
  fi
  checksum_line="$(awk -v arch="$node_arch" '$2 ~ ("^node-v22\\.[0-9]+\\.[0-9]+-linux-" arch "\\.tar\\.xz$") {print; exit}' "$temp_dir/SHASUMS256.txt")"
  read -r expected_hash archive <<< "$checksum_line"
  if [[ ! "$expected_hash" =~ ^[0-9a-f]{64}$ ]] || [[ -z "$archive" ]]; then
    printf 'Mirror returned no valid Node.js archive checksum.\n' >&2
    continue
  fi
  version="${archive#node-}"
  version="${version%-linux-*}"
  if ! curl -fLsS --retry 1 --connect-timeout 10 --max-time 300 \
    "$source_url/$version/$archive" -o "$temp_dir/$archive"; then
    continue
  fi
  if ! (cd "$temp_dir"; printf '%s  %s\n' "$expected_hash" "$archive" | sha256sum -c -); then
    printf 'Node.js checksum mismatch; trying the next source.\n' >&2
    continue
  fi
  if ! tar -xJf "$temp_dir/$archive" -C "$temp_dir"; then
    continue
  fi
  extracted="${archive%.tar.xz}"
  # Validate before activating the downloaded runtime.
  if ! "$temp_dir/$extracted/bin/node" --version; then
    printf 'Node.js cannot run on this server (check glibc compatibility).\n' >&2
    continue
  fi
  destination="$ROOT_DIR/.tools/$extracted"
  if [[ -e "$ROOT_DIR/.tools/node" && ! -L "$ROOT_DIR/.tools/node" ]]; then
    printf '%s is not a managed symlink. Move it aside and retry.\n' "$ROOT_DIR/.tools/node" >&2
    exit 1
  fi
  # Replacing this versioned directory repairs a previous incomplete install.
  rm -rf "$destination"
  mv "$temp_dir/$extracted" "$destination"
  ln -sfn "$extracted" "$ROOT_DIR/.tools/node"
  "$ROOT_DIR/.tools/node/bin/npm" --version
  exit 0
done
printf 'Node.js download failed. Check network access or set NODE_DIST_MIRROR.\n' >&2
exit 1
