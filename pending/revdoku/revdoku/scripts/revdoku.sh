#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
PACKAGE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
INSTALL_BASE=${REVDOKU_INSTALL_BASE:-https://raw.githubusercontent.com/revdoku/revdoku/main}
JQ_VERSION=1.8.1
JQ_BASE_URL=https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}

die() {
  echo "error: $1" >&2
  exit 1
}

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$1" | awk '{print $2}'
  else
    die "requires sha256sum, shasum, or openssl"
  fi
}

download_file() {
  case "$INSTALL_BASE" in
    file://*)
      cp "${INSTALL_BASE#file://}/$1" "$2"
      return
      ;;
  esac
  command -v curl >/dev/null 2>&1 || die "requires curl"
  curl -fsSL "${INSTALL_BASE%/}/$1" -o "$2"
}

ensure_cli() {
  if [ -x "$SKILL_DIR/bin/revdoku" ] || [ -x "$PACKAGE_ROOT/bin/revdoku" ]; then
    return
  fi
  mkdir -p "$SKILL_DIR/bin"
  download_file "skills/revdoku/bin/revdoku" "$SKILL_DIR/bin/revdoku"
  chmod 0755 "$SKILL_DIR/bin/revdoku"
}

ensure_jq() {
  if command -v jq >/dev/null 2>&1 || [ -x "$SKILL_DIR/bin/jq" ]; then
    return
  fi

  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$os/$arch" in
    darwin/arm64) asset=jq-macos-arm64; expected=a9fe3ea2f86dfc72f6728417521ec9067b343277152b114f4e98d8cb0e263603 ;;
    darwin/x86_64) asset=jq-macos-amd64; expected=e80dbe0d2a2597e3c11c404f03337b981d74b4a8504b70586c354b7697a7c27f ;;
    linux/x86_64) asset=jq-linux-amd64; expected=020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d ;;
    linux/aarch64|linux/arm64) asset=jq-linux-arm64; expected=6bc62f25981328edd3cfcfe6fe51b073f2d7e7710d7ef7fcdac28d4e384fc3d4 ;;
    *) die "unsupported platform for bundled jq: $os/$arch" ;;
  esac

  mkdir -p "$SKILL_DIR/bin"
  tmp=$(mktemp)
  command -v curl >/dev/null 2>&1 || die "requires curl"
  curl -fsSL "$JQ_BASE_URL/$asset" -o "$tmp"
  actual=$(sha256_file "$tmp")
  if [ "$actual" != "$expected" ]; then
    rm -f "$tmp"
    die "downloaded jq checksum mismatch"
  fi
  mv "$tmp" "$SKILL_DIR/bin/jq"
  chmod 0755 "$SKILL_DIR/bin/jq"
}

ensure_cli
ensure_jq

PATH="$SKILL_DIR/bin:$PATH"
export PATH

if [ -x "$SKILL_DIR/bin/revdoku" ]; then
  exec "$SKILL_DIR/bin/revdoku" "$@"
fi

if [ -x "$PACKAGE_ROOT/bin/revdoku" ]; then
  exec "$PACKAGE_ROOT/bin/revdoku" "$@"
fi

REPO_ROOT=$(CDPATH= cd -- "$PACKAGE_ROOT/../../.." && pwd)
exec "$REPO_ROOT/bin/revdoku" "$@"
