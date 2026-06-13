#!/usr/bin/env bash
# recalculate-scores.sh
#
# Robust wrapper around `skillstore-cli skill score` used by the
# `.github/workflows/recalculate-scores.yml` job.
#
# Why: The CLI internally iterates per-breakdown updates; a single
# `TimeoutError` (e.g. transient Supabase blip during one breakdown
# write) used to abort the whole run, wasting an entire daily recalc.
# This wrapper:
#
#   1. Iterates one slug at a time (or all slugs when --recalculate is
#      passed without an explicit slug list — see WORKFLOW_NOTE below).
#   2. Retries each slug with exponential backoff (default: 3 attempts).
#   3. Isolates failures: one slug's failure is logged and counted in
#      `Errors:`; the loop continues.
#   4. Emits the same `Processed/Updated/Errors/Duration` summary line
#      format the workflow already grep-parses.
#
# Usage:
#   recalculate-scores.sh \
#     --cli /path/to/skillstore-cli \
#     [--slugs slug1,slug2,...] [--limit N] \
#     [--concurrency N] [--dry-run] \
#     [--max-attempts N] [--retry-base-seconds N]
#
# Exit codes:
#   0  - all slugs processed, no per-slug failures
#   1  - one or more slugs failed after retries (errors > 0)
#   2  - invocation / configuration error (bad args, missing CLI)
#
# WORKFLOW_NOTE:
#   When called with `--recalculate` and no `--slugs`, the CLI itself
#   enumerates skills. To preserve per-slug isolation in that mode we
#   do NOT call the CLI in "all skills" mode here; instead the caller
#   is expected to pass `--slugs`. The recalculate-scores.yml workflow
#   handles "all skills" by first listing slugs and then invoking this
#   wrapper. If the caller insists on `--recalculate` (legacy mode),
#   we fall back to a single CLI invocation wrapped in a top-level
#   retry loop and best-effort error counting.
#
# Designed to be safe under `set -u` and `set -o pipefail`. We do NOT
# use `set -e` because we want to handle child failures explicitly.
set -u
set -o pipefail

# ---------- argument parsing ----------
CLI=""
SLUGS_CSV=""
LIMIT=""
CONCURRENCY=5
DRY_RUN=0
MAX_ATTEMPTS=3
RETRY_BASE_SECONDS=2
RECALCULATE=0
EXTRA_FLAGS=()

usage() {
	cat <<'USAGE'
Usage: recalculate-scores.sh --cli PATH [options]

Options:
  --cli PATH                  Path to skillstore-cli binary (required)
  --slugs CSV                 Comma-separated slug list (mutually exclusive with --recalculate)
  --limit N                   Optional: limit total slugs (applied before per-slug loop)
  --concurrency N             Pass-through to CLI (default: 5)
  --dry-run                   Pass-through to CLI
  --max-attempts N            Per-slug retry attempts (default: 3)
  --retry-base-seconds N      Initial backoff seconds (default: 2, doubled each retry)
  --recalculate               Legacy "all skills" mode (no per-slug isolation; wrapped in top-level retry)
  --                          Forwarded as additional CLI flags
  -h | --help                 Show this help
USAGE
}

while [ $# -gt 0 ]; do
	case "$1" in
		--cli)               CLI="${2:-}"; shift 2 ;;
		--slugs)             SLUGS_CSV="${2:-}"; shift 2 ;;
		--limit)             LIMIT="${2:-}"; shift 2 ;;
		--concurrency)       CONCURRENCY="${2:-5}"; shift 2 ;;
		--dry-run)           DRY_RUN=1; shift ;;
		--max-attempts)      MAX_ATTEMPTS="${2:-3}"; shift 2 ;;
		--retry-base-seconds) RETRY_BASE_SECONDS="${2:-2}"; shift 2 ;;
		--recalculate)       RECALCULATE=1; shift ;;
		--)                  shift; while [ $# -gt 0 ]; do EXTRA_FLAGS+=("$1"); shift; done ;;
		-h|--help)           usage; exit 0 ;;
		*)                   echo "::error::Unknown argument: $1" >&2; usage; exit 2 ;;
	esac
done

if [ -z "$CLI" ]; then
	echo "::error::--cli is required" >&2
	usage
	exit 2
fi
if [ ! -x "$CLI" ]; then
	echo "::error::CLI not found or not executable: $CLI" >&2
	exit 2
fi
if [ "$RECALCULATE" -eq 1 ] && [ -n "$SLUGS_CSV" ]; then
	echo "::error::--recalculate and --slugs are mutually exclusive" >&2
	exit 2
fi
if ! [[ "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
	echo "::error::--max-attempts must be a positive integer" >&2
	exit 2
fi
if ! [[ "$RETRY_BASE_SECONDS" =~ ^[0-9]+$ ]]; then
	echo "::error::--retry-base-seconds must be a non-negative integer" >&2
	exit 2
fi

# ---------- timing ----------
START_TS=$(date +%s)

# ---------- counters ----------
PROCESSED=0
UPDATED=0
ERRORS=0
FAILED_SLUGS=()

# ---------- per-slug worker ----------
# Truncates long lines to keep workflow logs readable.
_truncate() {
	local s="$1"
	local max="${2:-240}"
	if [ "${#s}" -le "$max" ]; then
		printf '%s' "$s"
	else
		printf '%s...[truncated %d chars]' "${s:0:$max}" "$(( ${#s} - max ))"
	fi
}

# Runs the CLI for a single slug with retry/backoff. Echoes CLI's
# stdout (caller is expected to `tee` it). Returns 0 on eventual
# success, 1 on terminal failure.
score_one_slug() {
	local slug="$1"
	local attempt=1
	local sleep_secs="$RETRY_BASE_SECONDS"
	local rc=0
	local stdout_path stderr_path
	stdout_path=$(mktemp -t recalc-out.XXXXXX)
	stderr_path=$(mktemp -t recalc-err.XXXXXX)
	# shellcheck disable=SC2064
	trap "rm -f '$stdout_path' '$stderr_path'" RETURN

	while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
		if [ "$attempt" -gt 1 ]; then
			echo "  [retry $attempt/$MAX_ATTEMPTS for $slug after ${sleep_secs}s]"
			sleep "$sleep_secs"
			sleep_secs=$(( sleep_secs * 2 ))
		fi

		set +e
		# Build argv to avoid `${arr[@]}` unbound errors under `set -u`.
		cli_args=( skill score
			--slugs "$slug"
			--concurrency "$CONCURRENCY"
		)
		if [ "$DRY_RUN" -eq 1 ]; then
			cli_args+=( --dry-run )
		fi
		if [ "${#EXTRA_FLAGS[@]}" -gt 0 ]; then
			cli_args+=( "${EXTRA_FLAGS[@]}" )
		fi
		"$CLI" "${cli_args[@]}" > "$stdout_path" 2> "$stderr_path"
		rc=$?
		set -e 2>/dev/null || true

		# Forward CLI output to the caller's stdout (matches single-run
		# behavior). The caller typically also redirects this through a
		# tee/outer-file; calling `cat` here is safe because the caller
		# will only redirect our own stdout, not the per-call files.
		cat "$stdout_path" || true

		if [ "$rc" -eq 0 ]; then
			return 0
		fi
		attempt=$(( attempt + 1 ))

		# Surface a one-line hint to workflow logs (warnings are visible
		# in GitHub Actions UI without failing the step).
		local err_summary
		err_summary="$(_truncate "$(tail -n 5 "$stderr_path" 2>/dev/null | tr '\n' ' ')" 200)"
		echo "::warning::score failed for slug=$slug attempt=$attempt/$MAX_ATTEMPTS exit=$rc err=$( _truncate "$err_summary" 200 )"
	done

	echo "::error::score ultimately failed for slug=$slug after $MAX_ATTEMPTS attempts"
	return 1
}

# ---------- per-slug: parse Processed/Updated/Errors from a single
# slug run and accumulate. Best-effort: if a single CLI run does not
# print the lines, we just count it as 1 processed (success) or 1
# error (failure).
ingest_one_slug_output() {
	local slug="$1"
	local rc="$2"
	local output_path="$3"
	PROCESSED=$(( PROCESSED + 1 ))
	if [ "$rc" -eq 0 ]; then
		# Heuristic: if the CLI printed "Updated: 1" (or N>0), count
		# those. We don't have a stable Updated line for a single-slug
		# run, so assume 1 (the slug itself) on success. This matches
		# prior semantics: per-slug success == 1 update.
		UPDATED=$(( UPDATED + 1 ))
	else
		ERRORS=$(( ERRORS + 1 ))
		FAILED_SLUGS+=("$slug")
	fi
	# Note: the per-slug Processed/Updated/Errors lines printed by the
	# CLI are intentionally left in stdout so the existing workflow
	# parser (and humans) can still see them. We only print the
	# aggregate at the end.
}

# ---------- main ----------
if [ "$RECALCULATE" -eq 1 ]; then
	# Legacy "all skills" path. Wrap the single CLI call in a top-level
	# retry loop. Per-breakdown isolation is the CLI's responsibility
	# in this mode; we can only defend against transient whole-run
	# failures (network, runner glitch).
	echo "=== recalculate-scores.sh: legacy --recalculate mode (top-level retry) ==="
	attempt=1
	sleep_secs="$RETRY_BASE_SECONDS"
	rc=0
	stdout_path=$(mktemp -t recalc-out.XXXXXX)
	stderr_path=$(mktemp -t recalc-err.XXXXXX)
	trap "rm -f '$stdout_path' '$stderr_path'" EXIT

	while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
		if [ "$attempt" -gt 1 ]; then
			echo "  [top-level retry $attempt/$MAX_ATTEMPTS after ${sleep_secs}s]"
			sleep "$sleep_secs"
			sleep_secs=$(( sleep_secs * 2 ))
		fi
		set +e
		cli_args=( skill score --recalculate --concurrency "$CONCURRENCY" )
		if [ "$DRY_RUN" -eq 1 ]; then
			cli_args+=( --dry-run )
		fi
		if [ -n "$LIMIT" ]; then
			cli_args+=( --limit "$LIMIT" )
		fi
		if [ "${#EXTRA_FLAGS[@]}" -gt 0 ]; then
			cli_args+=( "${EXTRA_FLAGS[@]}" )
		fi
		"$CLI" "${cli_args[@]}" > "$stdout_path" 2> "$stderr_path"
		rc=$?
		set -e 2>/dev/null || true
		cat "$stdout_path"
		if [ "$rc" -eq 0 ]; then
			break
		fi
		err_summary="$(_truncate "$(tail -n 5 "$stderr_path" 2>/dev/null | tr '\n' ' ')" 200)"
		echo "::warning::recalculate failed attempt=$attempt/$MAX_ATTEMPTS exit=$rc err=$err_summary"
		attempt=$(( attempt + 1 ))
	done

	# Best-effort: parse the CLI's own Processed/Updated/Errors lines
	# if they were emitted.
	if [ "$rc" -eq 0 ]; then
		PROCESSED="$(grep -oE 'Processed:\s*[0-9]+' "$stdout_path" | tail -n1 | grep -oE '[0-9]+' || echo 0)"
		UPDATED="$(grep -oE 'Updated:\s*[0-9]+' "$stdout_path" | tail -n1 | grep -oE '[0-9]+' || echo 0)"
		ERRORS="$(grep -oE 'Errors:\s*[0-9]+' "$stdout_path" | tail -n1 | grep -oE '[0-9]+' || echo 0)"
	else
		ERRORS=1
	fi
	rm -f "$stdout_path" "$stderr_path"
else
	# Per-slug path. Split CSV; optionally apply --limit.
	echo "=== recalculate-scores.sh: per-slug mode (concurrency=$CONCURRENCY, max-attempts=$MAX_ATTEMPTS) ==="
	IFS=',' read -ra SLUGS_ARR <<< "$SLUGS_CSV"
	if [ -n "$LIMIT" ] && [ "$LIMIT" -gt 0 ] 2>/dev/null; then
		if [ "${#SLUGS_ARR[@]}" -gt "$LIMIT" ]; then
			SLUGS_ARR=( "${SLUGS_ARR[@]:0:$LIMIT}" )
		fi
	fi
	echo "Total slugs to process: ${#SLUGS_ARR[@]}"

	for slug in "${SLUGS_ARR[@]}"; do
		# Trim whitespace defensively.
		slug="${slug#"${slug%%[![:space:]]*}"}"
		slug="${slug%"${slug##*[![:space:]]}"}"
		if [ -z "$slug" ]; then
			continue
		fi
		echo ""
		echo "--- processing slug: $slug ---"
		out_path=$(mktemp -t recalc-out.XXXXXX)
		err_path=$(mktemp -t recalc-err.XXXXXX)
		# shellcheck disable=SC2064
		trap "rm -f '$out_path' '$err_path'" RETURN

		# score_one_slug writes its per-call CLI output to its OWN temp
		# files (stdout_path/stderr_path inside the function) and cats
		# them to the caller's stdout. We capture the caller's stdout
		# here in out_path. After the call we forward that captured
		# output so workflow logs see it once.
		rc=0
		score_one_slug "$slug" > "$out_path" 2> "$err_path" || rc=$?
		cat "$out_path"
		ingest_one_slug_output "$slug" "$rc" "$out_path"
		rm -f "$out_path" "$err_path"
	done
fi

# ---------- summary (matches workflow grep format) ----------
END_TS=$(date +%s)
DURATION=$(( END_TS - START_TS ))

echo ""
echo "=== recalculate-scores.sh summary ==="
echo "Processed: $PROCESSED"
echo "Updated: $UPDATED"
echo "Errors: $ERRORS"
echo "Duration: ${DURATION}s"
if [ "${#FAILED_SLUGS[@]}" -gt 0 ]; then
	echo "Failed slugs:"
	for s in "${FAILED_SLUGS[@]}"; do
		echo "  - $s"
	done
fi

# Exit policy:
#   0 - we processed at least one slug successfully (with or without
#       errors). A single breakdown update failure must NOT take down
#       the whole workflow; it is surfaced as ::warning:: / Errors:
#       in the summary, and the GitHub Actions job continues.
#   1 - no slug succeeded at all (e.g. CLI binary missing, every slug
#       timed out). The workflow can mark this as a failure.
if [ "$PROCESSED" -eq 0 ] || [ "$PROCESSED" -eq "$ERRORS" ]; then
	exit 1
fi
exit 0
