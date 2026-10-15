#!/usr/bin/env bash
# latest-json.sh — dump the latest closed 5-minute bucket for one pair as JSON.
#
# This is an OPTIONAL convenience wrapper around the `blackforge` CLI for the common
# "give me the latest row for a pair" task. It shells out to the CLI on purpose — the
# skill never talks to the API directly. Prefer the blackforge_latest MCP tool when the
# MCP server is configured; use this only on the CLI fallback path.
#
# Usage:
#   scripts/latest-json.sh <exchange> <symbol> [col1,col2,...]
# Examples:
#   scripts/latest-json.sh binance BTCUSDT
#   scripts/latest-json.sh okx BTC-USDT price,downDepth5,askLiqRemoved
#
# Auth comes from the CLI's own resolution (--api-key option > $BLACKFORGE_API_KEY >
# ~/.blackforge/config.json). Set BLACKFORGE_API_KEY or run `blackforge auth set-key` first.
set -euo pipefail

exchange="${1:?usage: latest-json.sh <exchange> <symbol> [columns]}"
symbol="${2:?usage: latest-json.sh <exchange> <symbol> [columns]}"
columns="${3:-}"

# Resolve the CLI: installed binary if present, else npx.
if command -v blackforge >/dev/null 2>&1; then
  bf=(blackforge)
else
  bf=(npx -y @blackforge-so/cli)
fi

args=(latest --exchange "$exchange" --symbol "$symbol" --output json)
[ -n "$columns" ] && args+=(--columns "$columns")

exec "${bf[@]}" "${args[@]}"
