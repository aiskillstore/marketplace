#!/usr/bin/env bash
set -euo pipefail

REPO="${DITTOBOT_REPO:-RegionallyFamous/dittobot}"
REF="${DITTOBOT_REF:-main}"

if [ -n "${DITTOBOT_ARCHIVE_URL:-}" ]; then
  ARCHIVE_URL="$DITTOBOT_ARCHIVE_URL"
elif [[ "$REF" == refs/* ]]; then
  ARCHIVE_URL="https://github.com/${REPO}/archive/${REF}.tar.gz"
elif [[ "$REF" == v[0-9]* ]]; then
  ARCHIVE_URL="https://github.com/${REPO}/archive/refs/tags/${REF}.tar.gz"
else
  ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${REF}.tar.gz"
fi

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Dittobot needs %s. Install it, then rerun this command.\n' "$1" >&2
    exit 1
  fi
}

need curl
need tar
need python3

tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/dittobot-install.XXXXXX")"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

archive="$tmpdir/dittobot.tar.gz"
printf 'Downloading Dittobot from %s\n' "$ARCHIVE_URL"
curl -fsSL "$ARCHIVE_URL" -o "$archive"
tar -xzf "$archive" -C "$tmpdir"

installer=""
while IFS= read -r candidate; do
  installer="$candidate"
  break
done < <(find "$tmpdir" -maxdepth 3 -type f -path '*/scripts/install.py')

if [ -z "$installer" ]; then
  printf 'Could not find scripts/install.py in the downloaded archive.\n' >&2
  exit 1
fi

repo_dir="$(cd "$(dirname "$installer")/.." && pwd)"
printf 'Installing Dittobot into the Codex user skills folder...\n'
python3 "$repo_dir/scripts/install.py" --copy "$@"
printf 'Dittobot is installed. Start a new Codex session if $dittobot does not appear right away.\n'
