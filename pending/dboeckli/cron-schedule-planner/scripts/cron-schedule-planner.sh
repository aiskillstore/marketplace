#!/usr/bin/env bash
# cron-schedule-planner.sh — overview and distribution of GitHub Actions cron schedules.
#
# Collects scheduled workflows across repositories (via `gh`, or local checkouts),
# classifies resource intensity, converts cron times between UTC and a local
# timezone, builds an hourly histogram with collisions, and suggests less
# contended slots for CPU-intensive jobs.
#
# Usage: cron-schedule-planner.sh [options]
#
#   --owner <owner>      GitHub owner to scan (default: authenticated user)
#   --repo <owner/repo>  explicit repository (repeatable); disables owner scan
#   --local <dir>        scan local checkouts under <dir> instead of GitHub
#   --tz <zone>          local timezone (default: Europe/Zurich)
#   --limit <n>          max repositories for the owner scan (default: 200)
#   --out <file>         Markdown report (default: target/cron-schedule-overview.md)
#   --no-report          print to stdout only, do not write the report
#   --top <n>            max redistribution suggestions (default: 5)
#   --queue-stats        add observed queue time per UTC hour (via gh run list)
#   --runs <n>           max runs per repo for queue stats (default: 50)
#   -h, --help           show this help
#
# Examples:
#   bash cron-schedule-planner.sh
#   bash cron-schedule-planner.sh --owner dboeckli --tz Europe/Zurich
#   bash cron-schedule-planner.sh --local ~/projects/referenzen
#   bash cron-schedule-planner.sh --repo dboeckli/ai-agent-skills --repo dboeckli/camel-first

set -euo pipefail

OWNER=""
LOCAL_DIR=""
TZ_LOCAL="Europe/Zurich"
LIMIT=200
OUT="target/cron-schedule-overview.md"
WRITE_REPORT=1
TOP=5
QUEUE_STATS=0
RUNS=50
declare -a EXPLICIT_REPOS=()
declare -a QUEUE_REPOS=()

while [[ $# -gt 0 ]]; do
	case "$1" in
	--owner)
		OWNER="$2"
		shift 2
		;;
	--repo)
		EXPLICIT_REPOS+=("$2")
		shift 2
		;;
	--local)
		LOCAL_DIR="$2"
		shift 2
		;;
	--tz)
		TZ_LOCAL="$2"
		shift 2
		;;
	--limit)
		LIMIT="$2"
		shift 2
		;;
	--out)
		OUT="$2"
		shift 2
		;;
	--no-report)
		WRITE_REPORT=0
		shift
		;;
	--top)
		TOP="$2"
		shift 2
		;;
	--queue-stats)
		QUEUE_STATS=1
		shift
		;;
	--runs)
		RUNS="$2"
		shift 2
		;;
	-h | --help)
		sed -n '2,26p' "$0"
		exit 0
		;;
	*)
		echo "Unknown option: $1" >&2
		exit 1
		;;
	esac
done

command -v gh >/dev/null 2>&1 || {
	echo "ERROR: gh CLI not found" >&2
	exit 1
}
command -v jq >/dev/null 2>&1 || {
	echo "ERROR: jq not found" >&2
	exit 1
}

REFDATE="$(date -u +%Y-%m-%d)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
RECORDS="$TMP_DIR/records.tsv"
QUEUE_TSV="$TMP_DIR/queue.tsv"
: >"$RECORDS"
: >"$QUEUE_TSV"

# Derive an owner/repo slug from a local checkout's origin remote.
slug_from_dir() {
	git -C "$1" remote get-url origin 2>/dev/null |
		sed -nE 's#.*github\.com[:/]([^/]+)/([^/]+?)(\.git)?$#\1/\2#p' | head -1
}

# ── Parsing helpers ────────────────────────────────────────────────────────

# Extract cron expressions from a workflow's `on.schedule` block.
extract_crons() {
	grep -E '^[[:space:]]*-?[[:space:]]*cron:' 2>/dev/null |
		sed -E "s/^[^:]*cron:[[:space:]]*//; s/[[:space:]]*#.*\$//; s/^['\"]//; s/['\"][[:space:]]*\$//" |
		grep -v '^[[:space:]]*$' || true
}

# Extract an optional schedule timezone (GitHub `on.schedule[].timezone`).
extract_timezone() {
	sed -nE 's/^[[:space:]]*timezone:[[:space:]]*//p' 2>/dev/null |
		tr -d "\"'" | awk '{ print $1; exit }' || true
}

# Describe a cron expression: "HH MM daykey daylabel frequency".
describe_cron() {
	awk -v c="$1" '
		function dowName(d) {
			if (d == 0) return "Sunday"
			if (d == 1) return "Monday"
			if (d == 2) return "Tuesday"
			if (d == 3) return "Wednesday"
			if (d == 4) return "Thursday"
			if (d == 5) return "Friday"
			return "Saturday"
		}
		BEGIN {
			n = split(c, f, /[ \t]+/)
			if (n != 5) { print "?\t?\t9\tcustom\tcustom"; exit }
			mn = f[1]; hr = f[2]; dom = f[3]; mon = f[4]; dow = f[5]
			if (mn !~ /^[0-9]+$/ || hr !~ /^[0-9]+$/) { print "?\t?\t9\tcustom\tcustom"; exit }
			if (dow == "*" && dom == "*") { dk = 0; lbl = "daily"; fr = "daily" }
			else if (dow ~ /^[0-7]$/ && dom == "*") { dk = (dow == 0 ? 7 : dow); lbl = dowName(dow + 0); fr = "weekly" }
			else if (dow == "1-5" && dom == "*") { dk = 1; lbl = "weekdays"; fr = "weekdays" }
			else if (dom ~ /^[0-9]+$/ && dow == "*") { dk = 0; lbl = "monthly day " dom; fr = "monthly" }
			else { print "?\t?\t9\tcustom\tcustom"; exit }
			printf "%02d\t%02d\t%d\t%s\t%s\n", hr + 0, mn + 0, dk, lbl, fr
		}
	' </dev/null
}

# Classify resource intensity from workflow content: "high|medium|low<TAB>evidence".
# High-intensity patterns are checked in priority order so the evidence names
# the most meaningful resource (containers/cluster before matrix).
classify() {
	local content="$1" evidence
	local -a high_patterns=(
		'docker[ -]?compose|compose\.ya?ml'
		'testcontainers|withtestcontainers'
		'^[[:space:]]*services:'
		'kind-action|k3s'
		'matrix:'
	)
	local p
	for p in "${high_patterns[@]}"; do
		if evidence=$(printf '%s\n' "$content" | grep -oiE "$p" | head -1) && [[ -n "$evidence" ]]; then
			printf 'high\t%s\n' "$evidence"
			return
		fi
	done
	if evidence=$(printf '%s\n' "$content" | grep -oiE 'maven|mvn |gradle|docker build|buildx' | head -1) && [[ -n "$evidence" ]]; then
		printf 'medium\t%s\n' "$evidence"
		return
	fi
	printf 'low\t-\n'
}

# ── Analyze a single workflow ──────────────────────────────────────────────

analyze() {
	local repo="$1" wf="$2" content="$3"
	local crons
	crons="$(printf '%s\n' "$content" | extract_crons)"
	[[ -n "$crons" ]] || return 0

	local intensity evidence
	IFS=$'\t' read -r intensity evidence < <(classify "$content")

	local src_tz
	src_tz="$(printf '%s\n' "$content" | extract_timezone)"
	[[ -n "$src_tz" ]] || src_tz="UTC"

	local cron
	while IFS= read -r cron; do
		[[ -n "$cron" ]] || continue
		local hh mm daykey daylabel freq
		IFS=$'\t' read -r hh mm daykey daylabel freq < <(describe_cron "$cron")
		local utc_hhmm="?" local_hhmm="?" hour_utc=""
		if [[ "$hh" != "?" ]]; then
			local epoch
			epoch="$(TZ="$src_tz" date -d "$REFDATE $hh:$mm:00" +%s 2>/dev/null || true)"
			if [[ -n "$epoch" ]]; then
				utc_hhmm="$(TZ=UTC date -d "@$epoch" +%H:%M)"
				local_hhmm="$(TZ="$TZ_LOCAL" date -d "@$epoch" +%H:%M)"
				hour_utc="$(TZ=UTC date -d "@$epoch" +%H)"
			fi
		fi
		printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
			"$repo" "$wf" "$cron" "$intensity" "$evidence" "$src_tz" \
			"$utc_hhmm" "$local_hhmm" "$hour_utc" "$daylabel" "$freq" >>"$RECORDS"
	done <<<"$crons"
}

# ── Collect repositories ───────────────────────────────────────────────────

collect_gh() {
	local slug="$1" names name content
	names="$(gh api "repos/$slug/contents/.github/workflows" --jq '.[] | select(.type=="file") | .name' 2>/dev/null || true)"
	[[ -n "$names" ]] || return 0
	while IFS= read -r name; do
		[[ "$name" == *.yml || "$name" == *.yaml ]] || continue
		content="$(gh api "repos/$slug/contents/.github/workflows/$name" -H "Accept: application/vnd.github.raw" 2>/dev/null || true)"
		[[ -n "$content" ]] || continue
		analyze "$slug" "$name" "$content"
	done <<<"$names"
}

collect_local() {
	local repo_dir="$1" name content
	while IFS= read -r name; do
		[[ -n "$name" ]] || continue
		content="$(cat "$name")"
		analyze "$(basename "$repo_dir")" "$(basename "$name")" "$content"
	done < <(find "$repo_dir/.github/workflows" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null | sort)
}

if [[ -n "$LOCAL_DIR" ]]; then
	[[ -d "$LOCAL_DIR" ]] || {
		echo "Directory not found: $LOCAL_DIR" >&2
		exit 1
	}
	echo "Scanning local checkouts under $LOCAL_DIR ..."
	for d in "$LOCAL_DIR"/*/; do
		[[ -d "$d/.github/workflows" ]] || continue
		collect_local "${d%/}"
		slug="$(slug_from_dir "${d%/}")"
		[[ -n "$slug" ]] && QUEUE_REPOS+=("$slug")
	done
elif [[ ${#EXPLICIT_REPOS[@]} -gt 0 ]]; then
	echo "Scanning ${#EXPLICIT_REPOS[@]} explicit repositories ..."
	for slug in "${EXPLICIT_REPOS[@]}"; do
		collect_gh "$slug"
		QUEUE_REPOS+=("$slug")
	done
else
	OWNER="${OWNER:-$(gh api user --jq .login)}"
	echo "Scanning repositories of owner $OWNER (limit $LIMIT) ..."
	mapfile -t repos < <(gh repo list "$OWNER" --limit "$LIMIT" --json nameWithOwner --jq '.[].nameWithOwner')
	for slug in "${repos[@]}"; do
		collect_gh "$slug"
		QUEUE_REPOS+=("$slug")
	done
fi

RECORD_COUNT="$(wc -l <"$RECORDS" | tr -d ' ')"
if [[ "$RECORD_COUNT" -eq 0 ]]; then
	echo "No scheduled workflows found."
	exit 0
fi

REPO_COUNT="$(cut -f1 "$RECORDS" | sort -u | wc -l | tr -d ' ')"

# ── Optional: observed queue times ─────────────────────────────────────────

QUEUE_HIST=""
if [[ "$QUEUE_STATS" -eq 1 && ${#QUEUE_REPOS[@]} -gt 0 ]]; then
	echo "Collecting queue times (last $RUNS runs per repo) ..."
	for slug in "${QUEUE_REPOS[@]}"; do
		gh run list -R "$slug" --limit "$RUNS" --json createdAt,startedAt 2>/dev/null |
			jq -r '.[] | select(.createdAt != null and .startedAt != null) | [.createdAt, .startedAt] | @tsv' 2>/dev/null |
			while IFS=$'\t' read -r created started; do
				c="$(date -u -d "$created" +%s 2>/dev/null)" || continue
				s="$(date -u -d "$started" +%s 2>/dev/null)" || continue
				q=$((s - c))
				[[ "$q" -gt 0 ]] || continue
				h="$(date -u -d "$created" +%H)"
				printf '%s\t%s\n' "$h" "$q" >>"$QUEUE_TSV"
			done
	done
	QUEUE_HIST="$(awk -F'\t' '{ n[$1]++; sum[$1] += $2; if ($2 > mx[$1]) mx[$1] = $2 } END { for (h = 0; h < 24; h++) { k = sprintf("%02d", h); if (n[k] > 0) printf "%02d\t%d\t%.0f\t%d\n", h, n[k], sum[k] / n[k], mx[k] } }' "$QUEUE_TSV")"
fi

# ── Histogram / collisions / recommendations ───────────────────────────────

HIST="$(awk -F'\t' '$9 != "" { count[$9]++ } END { for (h = 0; h < 24; h++) { k = sprintf("%02d", h); printf "%02d\t%d\n", h, count[k] + 0 } }' "$RECORDS")"

WEEKDAY_HIST="$(awk -F'\t' '{ count[$10]++ } END { split("daily Monday Tuesday Wednesday Thursday Friday Saturday Sunday weekdays monthly", o, " "); for (i = 1; i <= 10; i++) printf "%s\t%d\n", o[i], count[o[i]] + 0 }' "$RECORDS")"

COLLISIONS="$(awk -F'\t' '$9 != "" { c[$9]++ } END { for (h in c) if (c[h] >= 2) printf "%02d\t%d\n", h, c[h] }' "$RECORDS" | sort)"

# Quiet UTC hours (no scheduled runs) — candidate slots for CPU-intensive jobs.
mapfile -t QUIET_HOURS < <(awk -F'\t' '$9 != "" { c[$9]++ } END { for (h = 0; h < 24; h++) { k = sprintf("%02d", h); if ((c[k] + 0) == 0) printf "%02d\n", h } }' "$RECORDS")

# When queue data is available, prefer candidate hours with the lowest queue.
if [[ -n "$QUEUE_HIST" && ${#QUIET_HOURS[@]} -gt 0 ]]; then
	mapfile -t QUIET_HOURS < <(
		for h in "${QUIET_HOURS[@]}"; do
			avg="$(awk -F'\t' -v k="$h" '$1 == k { print $3; exit }' <<<"$QUEUE_HIST")"
			printf '%s\t%s\n' "${avg:-0}" "$h"
		done | sort -n -k1,1 | cut -f2
	)
fi

# Suggest moving high-intensity entries out of crowded hours.
SUGGESTIONS="$(awk -F'\t' -v top="$TOP" -v quiet="${QUIET_HOURS[*]}" '
	function newCron(cron, newHour,   f) {
		split(cron, f, /[ \t]+/)
		f[2] = newHour
		return f[1] " " f[2] " " f[3] " " f[4] " " f[5]
	}
	BEGIN { nq = split(quiet, q, " ") }
	$9 != "" { c[$9]++ }
	$4 == "high" && $9 != "" { hi[++n] = $0 }
	END {
		qi = 1
		shown = 0
		for (i = 1; i <= n && shown < top; i++) {
			split(hi[i], r, "\t")
			if ((c[r[9]] + 0) < 2) continue
			nh = ""
			while (qi <= nq) {
				cand = q[qi]; qi++
				if (cand + 0 != r[9] + 0) { nh = cand; break }
			}
			if (nh == "") break
			printf "%s\t%s\t%s\t%s\t%s\t%s\n", r[1], r[2], r[3], r[9], nh, newCron(r[3], nh)
			shown++
		}
	}
' "$RECORDS")"

# ── Console output ─────────────────────────────────────────────────────────

echo
echo "Scheduled workflows by UTC hour:"
while IFS=$'\t' read -r hour count; do
	bar=""
	for ((i = 0; i < count; i++)); do bar+="▇"; done
	printf '  %s:00  %-20s %d\n' "$hour" "$bar" "$count"
done <<<"$HIST"

echo
echo "Repositories: $REPO_COUNT  Scheduled entries: $RECORD_COUNT"

if [[ -n "$COLLISIONS" ]]; then
	echo
	echo "Collisions (UTC hours with 2+ scheduled runs):"
	while IFS=$'\t' read -r hour count; do
		printf '  %s:00  %d\n' "$hour" "$count"
	done <<<"$COLLISIONS"
fi

if [[ -n "$QUEUE_HIST" ]]; then
	echo
	echo "Observed queue time per UTC hour (avg / max seconds):"
	while IFS=$'\t' read -r hour samples avg max; do
		printf '  %s:00  avg %4ss  max %5ss  (%s runs)\n' "$hour" "$avg" "$max" "$samples"
	done <<<"$QUEUE_HIST"
fi

if [[ -n "$SUGGESTIONS" ]]; then
	echo
	echo "Redistribution suggestions (high-intensity jobs in crowded hours):"
	while IFS=$'\t' read -r repo wf cron from_hour to_hour new_cron; do
		printf '  %s/%s: %s -> %s (%s:00 -> %s:00 UTC)\n' "$repo" "$wf" "$cron" "$new_cron" "$from_hour" "$to_hour"
	done <<<"$SUGGESTIONS"
fi

# ── Markdown report ────────────────────────────────────────────────────────

if [[ "$WRITE_REPORT" -eq 1 ]]; then
	mkdir -p "$(dirname "$OUT")"
	{
		echo "# GitHub Actions Cron Schedule Overview"
		echo
		echo "- Generated: $(date '+%Y-%m-%d %H:%M:%S %z')"
		if [[ -n "$LOCAL_DIR" ]]; then
			echo "- Source: local checkouts under \`$LOCAL_DIR\`"
		elif [[ ${#EXPLICIT_REPOS[@]} -gt 0 ]]; then
			echo "- Source: explicit repositories"
		else
			echo "- Source: GitHub API (owner \`$OWNER\`)"
		fi
		echo "- Local timezone: \`$TZ_LOCAL\` (cron is UTC)"
		echo "- Repositories: $REPO_COUNT"
		echo "- Scheduled entries: $RECORD_COUNT"
		if [[ "$QUEUE_STATS" -eq 1 ]]; then
			echo "- Queue stats: last $RUNS runs per repo"
		fi
		echo
		echo "> Cron expressions are UTC. Local times use \`$TZ_LOCAL\` for the current date;"
		echo "> daylight-saving transitions can shift them by one hour."
		echo
		echo "## Scheduled workflows"
		echo
		echo "| Repo | Workflow | Cron (UTC) | UTC | Local ($TZ_LOCAL) | Frequenz | Intensität | Nutzt |"
		echo "| ---- | -------- | ---------- | --- | ----------------- | -------- | ---------- | ----- |"
		sort -t$'\t' -k9,9 -k1,1 -k2,2 "$RECORDS" | while IFS=$'\t' read -r repo wf cron intensity evidence src_tz utc_hhmm local_hhmm hour_utc daylabel freq; do
			echo "| $repo | $wf | \`$cron\` | $utc_hhmm | $local_hhmm | $daylabel | $intensity | $evidence |"
		done
		echo
		echo "## Runs per UTC hour"
		echo
		echo "| UTC hour | Runs | |"
		echo "| -------- | ---- | - |"
		while IFS=$'\t' read -r hour count; do
			bar=""
			for ((i = 0; i < count; i++)); do bar+="▇"; done
			echo "| ${hour}:00 | $count | $bar |"
		done <<<"$HIST"
		echo
		echo "## Runs per frequency / weekday"
		echo
		echo "| Slot | Runs |"
		echo "| ---- | ---- |"
		while IFS=$'\t' read -r slot count; do
			echo "| $slot | $count |"
		done <<<"$WEEKDAY_HIST"
		echo
		if [[ -n "$QUEUE_HIST" ]]; then
			echo "## Observed queue time per UTC hour"
			echo
			echo "| UTC hour | Samples | Avg queue | Max queue |"
			echo "| -------- | ------- | --------- | --------- |"
			while IFS=$'\t' read -r hour samples avg max; do
				echo "| ${hour}:00 | $samples | ${avg}s | ${max}s |"
			done <<<"$QUEUE_HIST"
			echo
		fi
		echo "## Collisions (UTC hours with 2+ scheduled runs)"
		echo
		if [[ -z "$COLLISIONS" ]]; then
			echo "_None._"
		else
			echo "| UTC hour | Runs |"
			echo "| -------- | ---- |"
			while IFS=$'\t' read -r hour count; do
				echo "| ${hour}:00 | $count |"
			done <<<"$COLLISIONS"
		fi
		echo
		echo "## Redistribution suggestions"
		echo
		if [[ -z "$SUGGESTIONS" ]]; then
			echo "_No crowded hours with high-intensity jobs._"
		else
			echo "| Repo | Workflow | Current (UTC) | Suggested (UTC) | Move |"
			echo "| ---- | -------- | ------------- | --------------- | ---- |"
			while IFS=$'\t' read -r repo wf cron from_hour to_hour new_cron; do
				echo "| $repo | $wf | \`$cron\` | \`$new_cron\` | ${from_hour}:00 → ${to_hour}:00 |"
			done <<<"$SUGGESTIONS"
			echo
			echo "Suggestions only move high-intensity jobs out of crowded hours into empty"
			echo "ones; review before applying and adjust for DST."
		fi
	} >"$OUT"
	echo
	echo "Report written to $OUT"
fi
