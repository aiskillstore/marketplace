#!/usr/bin/env bash
# Generate an overview of GitHub Actions triggers (push, pull_request, schedule, ...)
# and cron schedules across repository checkouts, and write a Markdown report.
# Scheduled workflows are sorted by weekday/time and shown with a human-readable
# run time plus the original cron expression.
#
# Usage: list-workflow-triggers.sh [--root <dir>] [--glob <pattern>] [--out <file>] [--no-report]
#
#   --root <dir>      directory containing repo checkouts
#                     (default: $REFERENZEN_DIR or ~/projects/referenzen)
#   --glob <pattern>  workflow filename filter under .github/workflows
#                     (default: all *.yml and *.yaml)
#   --out <file>      Markdown report path (default: target/workflow-triggers.md)
#   --no-report       only print to stdout, do not write the report file
#
# Examples:
#   bash list-workflow-triggers.sh
#   bash list-workflow-triggers.sh --root ~/projects/referenzen --glob 'maven-build.yml'
#   bash list-workflow-triggers.sh --root /c/development/projects --out target/triggers.md

set -euo pipefail

REFERENZEN_DIR="${REFERENZEN_DIR:-$HOME/projects/referenzen}"
ROOT="$REFERENZEN_DIR"
GLOB=""
OUT="target/workflow-triggers.md"
WRITE_REPORT=1

while [[ $# -gt 0 ]]; do
	case "$1" in
	--root)
		ROOT="$2"
		shift 2
		;;
	--glob)
		GLOB="$2"
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
	-h | --help)
		sed -n '2,22p' "$0"
		exit 0
		;;
	*)
		echo "Unknown option: $1" >&2
		exit 1
		;;
	esac
done

if [[ ! -d "$ROOT" ]]; then
	echo "Directory not found: $ROOT" >&2
	exit 1
fi

shopt -s nullglob

# Extract trigger names from the top-level `on:` block, including inline forms.
extract_triggers() {
	awk '
		function emit(list) {
			gsub(/[][ ]/, "", list)
			n = split(list, parts, ",")
			for (i = 1; i <= n; i++) if (parts[i] != "") print parts[i]
		}
		/^on:/ {
			rest = $0
			sub(/^on:[[:space:]]*/, "", rest)
			if (rest ~ /^\[/) { gsub(/[\[\]]/, "", rest); emit(rest); in_on = 0; next }
			if (rest != "") { print rest; in_on = 0; next }
			in_on = 1
			next
		}
		in_on {
			if ($0 ~ /^[^[:space:]]/) { in_on = 0; next }
			if ($0 ~ /^  [A-Za-z_][A-Za-z0-9_-]*:/) {
				key = $0
				sub(/^  /, "", key)
				sub(/:.*/, "", key)
				print key
			}
		}
	' "$1"
}

# Extract cron expressions, stripping quotes, inline comments and whitespace.
extract_crons() {
	grep -E '^[[:space:]]*-?[[:space:]]*cron:' "$1" 2>/dev/null |
		sed -E "s/^[^:]*cron:[[:space:]]*//; s/[[:space:]]*#.*\$//; s/^['\"]//; s/['\"][[:space:]]*\$//" |
		grep -v '^[[:space:]]*$' || true
}

SCHED_TSV="$(mktemp)"
EVENT_TSV="$(mktemp)"
trap 'rm -f "$SCHED_TSV" "$EVENT_TSV"' EXIT

declare -A SEEN_REPOS=()
WF_COUNT=0
SCHED_COUNT=0

for repo in "$ROOT"/*/; do
	WF_DIR="${repo%/}/.github/workflows"
	[[ -d "$WF_DIR" ]] || continue

	REPO_NAME="$(basename "${repo%/}")"
	if [[ -n "$GLOB" ]]; then
		workflows=("$WF_DIR"/$GLOB)
	else
		workflows=("$WF_DIR"/*.yml "$WF_DIR"/*.yaml)
	fi

	for wf in "${workflows[@]}"; do
		[[ -f "$wf" ]] || continue

		SEEN_REPOS["$REPO_NAME"]=1
		WF_COUNT=$((WF_COUNT + 1))

		mapfile -t TRIGGERS < <(extract_triggers "$wf")
		mapfile -t CRONS < <(extract_crons "$wf")

		triggers="—"
		if [[ ${#TRIGGERS[@]} -gt 0 ]]; then
			triggers="$(printf '%s, ' "${TRIGGERS[@]}")"
			triggers="${triggers%, }"
		fi

		if [[ ${#CRONS[@]} -eq 0 ]]; then
			printf '%s\t%s\t%s\n' "$REPO_NAME" "$(basename "$wf")" "$triggers" >>"$EVENT_TSV"
		else
			crons="$(printf '%s;' "${CRONS[@]}")"
			crons="${crons%;}"
			printf '%s\t%s\t%s\t%s\n' "$REPO_NAME" "$(basename "$wf")" "$triggers" "$crons" >>"$SCHED_TSV"
			SCHED_COUNT=$((SCHED_COUNT + ${#CRONS[@]}))
		fi
	done
done

# Build sorted scheduled rows: key \t readable \t repo \t workflow \t cron \t triggers
SORTED="$(
	awk -F'\t' '
		function iso(d) { return (d == 0 ? 7 : d) }
		function dowName(d) {
			if (d == 0) return "Sunday"
			if (d == 1) return "Monday"
			if (d == 2) return "Tuesday"
			if (d == 3) return "Wednesday"
			if (d == 4) return "Thursday"
			if (d == 5) return "Friday"
			return "Saturday"
		}
		{
			repo = $1; wf = $2; trig = $3
			nc = split($4, crons, ";")
			for (i = 1; i <= nc; i++) {
				cron = crons[i]
				gsub(/^[ \t]+|[ \t]+$/, "", cron)
				if (cron == "") continue
				n = split(cron, f, /[ \t]+/)
				if (n != 5) { printf "z\t%s\t%s\t%s\t%s\t%s\n", "custom", repo, wf, cron, trig; continue }
				mn = f[1]; hr = f[2]; dom = f[3]; mon = f[4]; dow = f[5]
				if (mn !~ /^[0-9]+$/ || hr !~ /^[0-9]+$/) {
					printf "z\t%s\t%s\t%s\t%s\t%s\n", "custom", repo, wf, cron, trig; continue
				}
				if (dow == "*" && dom == "*") { dk = 0; label = "daily" }
				else if (dow ~ /^[0-7]$/ && dom == "*") { dk = iso(dow + 0); label = dowName(dow + 0) }
				else if (dow == "1-5" && dom == "*") { dk = 1; label = "weekdays" }
				else if (dom ~ /^[0-9]+$/ && dow == "*") { dk = 0; label = "monthly day " dom }
				else { printf "z\t%s\t%s\t%s\t%s\t%s\n", "custom", repo, wf, cron, trig; continue }
				key = sprintf("%02d %02d:%02d", dk, hr + 0, mn + 0)
				readable = sprintf("%s %02d:%02d", label, hr + 0, mn + 0)
				printf "%s\t%s\t%s\t%s\t%s\t%s\n", key, readable, repo, wf, cron, trig
			}
		}
	' "$SCHED_TSV" | sort
)"

REPO_COUNT=${#SEEN_REPOS[@]}

# --- Console output ---
echo "Scheduled workflows (sorted by weekday/time):"
echo
if [[ -z "$SORTED" ]]; then
	echo "  (none)"
else
	while IFS=$'\t' read -r _key readable repo wf cron triggers; do
		printf '  %-16s %-30s %-24s %s\n' "$readable" "$repo" "$wf" "[$cron]"
	done <<<"$SORTED"
fi

echo
echo "Event-only workflows (no schedule):"
echo
if [[ ! -s "$EVENT_TSV" ]]; then
	echo "  (none)"
else
	while IFS=$'\t' read -r repo wf triggers; do
		printf '  %-30s %-24s %s\n' "$repo" "$wf" "$triggers"
	done <"$EVENT_TSV"
fi

echo
echo "Repositories: $REPO_COUNT  Workflows: $WF_COUNT  Scheduled entries: $SCHED_COUNT"

# --- Markdown report ---
if [[ $WRITE_REPORT -eq 1 ]]; then
	mkdir -p "$(dirname "$OUT")"
	{
		echo "# GitHub Actions Trigger Overview"
		echo
		echo "- Root: \`$ROOT\`"
		echo "- Generated: $(date '+%Y-%m-%d %H:%M:%S %z')"
		echo "- Repositories: $REPO_COUNT"
		echo "- Workflows: $WF_COUNT"
		echo "- Scheduled entries: $SCHED_COUNT"
		echo
		echo "## Scheduled workflows (sorted by weekday/time)"
		echo
		if [[ -z "$SORTED" ]]; then
			echo "_No scheduled workflows found._"
		else
			echo "| Run | Repository | Workflow | Cron | Triggers |"
			echo "| --- | ---------- | -------- | ---- | -------- |"
			while IFS=$'\t' read -r _key readable repo wf cron triggers; do
				echo "| $readable | $repo | $wf | \`$cron\` | $triggers |"
			done <<<"$SORTED"
		fi
		echo
		echo "## Event-only workflows (no schedule)"
		echo
		if [[ ! -s "$EVENT_TSV" ]]; then
			echo "_None._"
		else
			echo "| Repository | Workflow | Triggers |"
			echo "| ---------- | -------- | -------- |"
			while IFS=$'\t' read -r repo wf triggers; do
				echo "| $repo | $wf | $triggers |"
			done <"$EVENT_TSV"
		fi
	} >"$OUT"
	echo
	echo "Report written to $OUT"
fi
