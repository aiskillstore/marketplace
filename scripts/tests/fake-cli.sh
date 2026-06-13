#!/usr/bin/env bash
# fake-cli.sh - mock for `skillstore-cli` used in tests.
#
# Supports two modes selected by the FAKE_CLI_MODE env var:
#   success                - all slugs succeed
#   fail-slug <name>       - the named slug fails with the configured
#                            FAKE_CLI_FAIL_EXIT (default 28) the first
#                            FAKE_CLI_FAIL_TIMES (default 1) times,
#                            then succeeds on subsequent attempts.
#   timeout                - simulate an AbortError (exit 28) once for
#                            the slug in FAKE_CLI_TIMEOUT_SLUG, then
#                            succeed.
#   recalc-fail            - --recalculate mode always fails
#   help                   - print usage
#
# It records every invocation to $FAKE_CLI_LOG (one line per call:
# "ts|args...") so tests can assert "we tried N times".
set -u

MODE="${FAKE_CLI_MODE:-success}"
FAIL_EXIT="${FAKE_CLI_FAIL_EXIT:-28}"
FAIL_TIMES="${FAKE_CLI_FAIL_TIMES:-1}"
TIMEOUT_SLUG="${FAKE_CLI_TIMEOUT_SLUG:-}"
LOG="${FAKE_CLI_LOG:-/tmp/fake-cli.log}"

mkdir -p "$(dirname "$LOG")"
touch "$LOG"

ts() { date +%s%N; }
log() { printf '%s|%s\n' "$(ts)" "$*" >> "$LOG"; }

# Parse args. We only care about `skill score --slugs <csv>` and
# `skill score --recalculate`.
SCORE=0
RECALC=0
SLUGS=""
EXTRA=()
while [ $# -gt 0 ]; do
	case "$1" in
		skill) shift ;;
		score) SCORE=1; shift ;;
		--slugs) SLUGS="${2:-}"; shift 2 ;;
		--recalculate) RECALC=1; shift ;;
		--concurrency|--limit) shift 2 ;;
		--dry-run) shift ;;
		*) EXTRA+=("$1"); shift ;;
	esac
done

log "mode=$MODE recalc=$RECALC slugs=$SLUGS extra=${EXTRA[*]:-}"

if [ "$SCORE" -ne 1 ]; then
	echo "fake-cli: unsupported invocation" >&2
	exit 64
fi

if [ "$RECALC" -eq 1 ]; then
	case "$MODE" in
		recalc-fail)
			echo "::fake::recalculate: simulated failure" >&2
			exit 1
			;;
		*)
			echo "Processed: 5"
			echo "Updated: 5"
			echo "Errors: 0"
			echo "Duration: 10s"
			exit 0
			;;
	esac
fi

# Per-slug path. Emit a small "result" line and exit accordingly.
IFS=',' read -ra ARR <<< "$SLUGS"

# Count how many times this exact slug has been seen so far in the log.
slug_call_count() {
	local target="$1"
	grep -c "|slugs=$target" "$LOG" 2>/dev/null || true
}

for slug in "${ARR[@]}"; do
	slug="$(echo "$slug" | xargs)"  # trim
	case "$MODE" in
		success)
			echo "[ok] slug=$slug"
			;;
		fail-slug)
			if [ "$slug" = "${FAKE_CLI_FAIL_SLUG:-}" ]; then
				n=$(slug_call_count "$slug")
				# Fail the first FAIL_TIMES times, then succeed.
				if [ "$n" -le "$FAIL_TIMES" ]; then
					echo "::fake::simulated failure for $slug (call $n/$FAIL_TIMES)" >&2
					exit "$FAIL_EXIT"
				fi
			fi
			echo "[ok-after-retry] slug=$slug"
			;;
		fail-slug-always)
			if [ "$slug" = "${FAKE_CLI_FAIL_SLUG:-}" ]; then
				echo "::fake::permanent failure for $slug" >&2
				exit "$FAIL_EXIT"
			fi
			echo "[ok] slug=$slug"
			;;
		timeout)
			if [ "$slug" = "$TIMEOUT_SLUG" ]; then
				n=$(slug_call_count "$slug")
				if [ "$n" -le 1 ]; then
					echo "::fake::AbortError: The operation was aborted due to timeout" >&2
					exit "$FAIL_EXIT"
				fi
			fi
			echo "[ok-after-timeout] slug=$slug"
			;;
		*)
			echo "::fake::unknown mode $MODE" >&2
			exit 64
			;;
	esac
done

# Emit summary lines that the wrapper's legacy mode might parse.
echo "Processed: ${#ARR[@]}"
echo "Updated: ${#ARR[@]}"
echo "Errors: 0"
echo "Duration: 1s"
exit 0
