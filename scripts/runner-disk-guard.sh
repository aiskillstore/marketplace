#!/usr/bin/env bash
set -euo pipefail

usage_threshold="${USAGE_THRESHOLD:-90}"
age_hours="${AGE_HOURS:-168}"

[[ "$usage_threshold" =~ ^[1-9][0-9]?$ ]] || {
  echo 'USAGE_THRESHOLD must be an integer from 1 through 99' >&2
  exit 2
}
[[ "$age_hours" =~ ^[1-9][0-9]*$ ]] || {
  echo 'AGE_HOURS must be a positive integer' >&2
  exit 2
}

# /run is tmpfs, so locking still works when the root filesystem is under pressure.
exec 9>/run/lock/marketplace-runner-disk-guard.lock
flock -n 9 || exit 0

usage=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
[[ "$usage" =~ ^[0-9]+$ ]] || {
  echo 'Unable to read root disk usage' >&2
  exit 1
}

if (( usage < usage_threshold )); then
  echo "Root disk usage is ${usage}%; threshold is ${usage_threshold}%. No cleanup needed."
  exit 0
fi

command -v docker >/dev/null 2>&1 || {
  echo 'Docker CLI is unavailable under disk pressure' >&2
  exit 1
}
docker info >/dev/null 2>&1 || {
  echo 'Docker daemon is unavailable under disk pressure' >&2
  exit 1
}

echo "Root disk usage is ${usage}%; pruning only unused Docker build cache older than ${age_hours}h."
docker builder prune --all --force --filter "until=${age_hours}h"
df -h /
