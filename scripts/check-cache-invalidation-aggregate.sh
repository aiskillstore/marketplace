#!/usr/bin/env bash

set -euo pipefail

CACHE_PLAN_RESULT="${CACHE_PLAN_RESULT:-}"
CACHE_SHARD_RESULT="${CACHE_SHARD_RESULT:-}"
SCORE_RESULT="${SCORE_RESULT:-}"

if [ "$CACHE_PLAN_RESULT" = "success" ] &&
  [ "$CACHE_SHARD_RESULT" = "success" ] &&
  [ "$SCORE_RESULT" = "success" ]; then
  echo "Cache invalidation aggregate succeeded"
  exit 0
fi

echo "::error::Cache invalidation did not complete successfully (plan=$CACHE_PLAN_RESULT, shards=$CACHE_SHARD_RESULT, scores=$SCORE_RESULT)" >&2
exit 1
