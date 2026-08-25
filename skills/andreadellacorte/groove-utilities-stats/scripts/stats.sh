#!/usr/bin/env bash
# groove-utilities-stats — bash fast-path implementation
# Read-only compound-loop dashboard: funnel (captured vs graduated),
# adherence (daily logs, streak, rollups, ratings), velocity (tasks, commits).
#
# Usage: stats.sh [week|month|all]   (default: week)
# Exit codes:
#   0  dashboard printed in full (beans/none backends, or no task backend)
#   1  no .groove/ — not a groove project
#   3  task metrics need the model (linear/github backend) — local metrics still printed;
#      SKILL.md model fallback should take over to add task counts

set -euo pipefail

period="${1:-week}"
case "$period" in
  week|month|all) ;;
  *) echo "stats: unknown period '$period' (use week|month|all)" >&2; exit 1 ;;
esac

GROOVE=".groove"
INDEX="${GROOVE}/index.md"
if [ ! -d "$GROOVE" ]; then
  echo "stats: no .groove/ here — run from a groove project root, or /groove-admin-install" >&2
  exit 1
fi

command -v python3 >/dev/null || { echo "stats: python3 not available" >&2; exit 1; }

# ---- config (frontmatter) ---------------------------------------------------
extract() { # <key> <default>  — reads a frontmatter key from .groove/index.md
  local key="$1" default="${2:-}" val=""
  [ -f "$INDEX" ] && val=$(sed -n '/^---$/,/^---$/p' "$INDEX" | grep "$key:" | head -1 | sed "s/.*${key}:[[:space:]]*//" | tr -d '[:space:]')
  echo "${val:-$default}"
}
backend=$(extract "storage" "")
[ -n "$backend" ] || backend=$(extract "backend" "none")   # legacy key fallback
review_days=$(extract "review_days" "5")
[[ "$review_days" =~ ^[0-9]+$ ]] || review_days=5

# ---- date range -------------------------------------------------------------
case "$period" in week) days=7;; month) days=30;; all) days=100000;; esac
since=$(python3 -c "import datetime,sys;print((datetime.date.today()-datetime.timedelta(days=int(sys.argv[1]))).isoformat())" "$days")

# ---- velocity: git + task backend ------------------------------------------
git_commits="NA"
if command -v git >/dev/null && git rev-parse --git-dir >/dev/null 2>&1; then
  git_commits=$(git log --oneline --since="$since" 2>/dev/null | wc -l | tr -d ' ')
fi

tasks_open="NA"; tasks_closed="NA"; mistakes_open="NA"; promises_open="NA"
needs_model=0
case "$backend" in
  beans)
    if command -v beans >/dev/null && command -v jq >/dev/null; then
      tasks_open=$(beans list --json --no-status completed --no-status scrapped 2>/dev/null | jq 'length' 2>/dev/null || echo NA)
      c=$(beans list --json --status completed 2>/dev/null | jq 'length' 2>/dev/null || echo 0)
      s=$(beans list --json --status scrapped  2>/dev/null | jq 'length' 2>/dev/null || echo 0)
      [[ "$c" =~ ^[0-9]+$ ]] || c=0; [[ "$s" =~ ^[0-9]+$ ]] || s=0
      tasks_closed=$((c + s))
      # best-effort: open items under the "Mistakes"/"Promises" epics
      epics=$(beans list --json -t epic 2>/dev/null || echo '[]')
      for kind in Mistakes Promises; do
        eid=$(echo "$epics" | jq -r --arg k "$kind" 'map(select(.title|test($k;"i")))|.[0].id // empty' 2>/dev/null || echo "")
        cnt="NA"
        [ -n "$eid" ] && cnt=$(beans list --json --parent "$eid" --no-status completed --no-status scrapped 2>/dev/null | jq 'length' 2>/dev/null || echo NA)
        [ "$kind" = "Mistakes" ] && mistakes_open="$cnt" || promises_open="$cnt"
      done
    fi
    ;;
  none|"") ;;                       # no task backend — omit task counts
  linear|github) needs_model=1 ;;   # local metrics only; model adds task counts
esac

# ---- compute + render (local metrics in python) -----------------------------
GROOVE="$GROOVE" PERIOD="$period" SINCE="$since" REVIEW_DAYS="$review_days" BACKEND="$backend" \
TASKS_OPEN="$tasks_open" TASKS_CLOSED="$tasks_closed" GIT_COMMITS="$git_commits" \
MISTAKES_OPEN="$mistakes_open" PROMISES_OPEN="$promises_open" \
python3 - <<'PY'
import os, re, glob, datetime

g          = os.environ["GROOVE"]
period     = os.environ["PERIOD"]
since      = datetime.date.fromisoformat(os.environ["SINCE"])
review     = int(os.environ["REVIEW_DAYS"])
backend    = os.environ["BACKEND"]
today      = datetime.date.today()
mem        = os.path.join(g, "memory")
learned    = os.path.join(mem, "learned")

def na(v): return v if v not in ("", None) else "NA"

DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")

# ---- funnel ----
captured_total = captured_period = 0
graduated_total = graduated_period = 0
for f in glob.glob(os.path.join(learned, "*.md")):
    if os.path.basename(f) == "signals.md":
        continue
    for line in open(f, encoding="utf-8", errors="replace"):
        m = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
        if m:
            captured_total += 1
            if datetime.date.fromisoformat(m.group(1)) >= since:
                captured_period += 1
        for gm in re.findall(r"\[graduated\s+(\d{4}-\d{2}-\d{2})\]", line):
            graduated_total += 1
            if datetime.date.fromisoformat(gm) >= since:
                graduated_period += 1
rate = f"{round(100*graduated_total/captured_total)}%" if captured_total else "n/a"

# ---- adherence: daily logs over last `review` business days + streak ----
def business_days_back(n):
    out, d = [], today
    while len(out) < n:
        if d.weekday() < 5:      # Mon-Fri
            out.append(d)
        d -= datetime.timedelta(days=1)
    return out
def has_daily(d):
    return os.path.isfile(os.path.join(mem, "daily", f"{d.isoformat()}.md"))

window = business_days_back(review)
covered = sum(1 for d in window if has_daily(d))
streak, d = 0, today
while True:
    if d.weekday() < 5:
        if has_daily(d): streak += 1
        else: break
    d -= datetime.timedelta(days=1)
    if (today - d).days > 400: break

# ---- rollup freshness: file for current or previous period exists ----
def rollup_fresh(subdir, fmts):
    prev_week = today - datetime.timedelta(days=7)
    prev_month = (today.replace(day=1) - datetime.timedelta(days=1))
    cands = set()
    for base in (today, prev_week, prev_month):
        for fmt in fmts:
            cands.add(base.strftime(fmt))
    return any(os.path.isfile(os.path.join(mem, subdir, f"{c}.md")) for c in cands)
weekly_fresh  = rollup_fresh("weekly",  ["%G-W%V"])
monthly_fresh = rollup_fresh("monthly", ["%Y-%m"])

# ---- ratings (signals.md) ----
ratings = []
sig = os.path.join(learned, "signals.md")
if os.path.isfile(sig):
    for line in open(sig, encoding="utf-8", errors="replace"):
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 3: continue
        dm = DATE.match(cells[1]) if len(cells) > 1 else None
        rm = re.match(r"(\d+)\s*/\s*5", cells[2]) if len(cells) > 2 else None
        if dm and rm and datetime.date.fromisoformat(dm.group(1)) >= since:
            ratings.append(int(rm.group(1)))
spark = "".join("▁▂▄▆█"[min(max(r,1),5)-1] for r in ratings)
avg = f"{sum(ratings)/len(ratings):.1f}" if ratings else "n/a"

def fresh(b): return "fresh" if b else "stale"
pl = "all time" if period == "all" else period
delta = "" if period == "all" else f" this {period}"

span = f"through {today.isoformat()}" if period == "all" else f"{since.isoformat()} to {today.isoformat()}"
print(f"## Groove Stats — {pl} ({span})\n")
print("### 🔁 Compound funnel")
if period == "all":
    print(f"Lessons captured: {captured_total}   Graduated: {graduated_total}")
else:
    print(f"Lessons captured: {captured_total} ({captured_period}{delta})   "
          f"Graduated: {graduated_total} ({graduated_period}{delta})")
print(f"Graduation rate: {rate}\n")
print("### 📿 Adherence")
print(f"Daily logs: {covered}/{review} business days   Streak: {streak} days")
print(f"Rollups: weekly {fresh(weekly_fresh)}, monthly {fresh(monthly_fresh)}")
print(f"Ratings: {len(ratings)} in period | avg {avg}/5" + (f"  {spark}" if spark else "") + "\n")
print("### 🚀 Velocity")
if backend in ("none", ""):
    print(f"Commits: {na(os.environ['GIT_COMMITS'])} in period")
else:
    print(f"Tasks: {na(os.environ['TASKS_OPEN'])} open / {na(os.environ['TASKS_CLOSED'])} closed   "
          f"Commits: {na(os.environ['GIT_COMMITS'])} in period")
    print(f"Open: {na(os.environ['MISTAKES_OPEN'])} mistakes, {na(os.environ['PROMISES_OPEN'])} promises")
print("\n_For qualitative patterns and learnings, run `/groove-utilities-memory-retrospective`._")
PY

if [ "$needs_model" -eq 1 ]; then
  echo
  echo "stats: task metrics for '$backend' backend need the model — re-running via the skill steps" >&2
  exit 3
fi
