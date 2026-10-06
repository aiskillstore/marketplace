#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Atri10
# Shared helpers for the Executor scripts. Sourced, never executed directly.
#
# Single source of truth for ID parsing, frontmatter reading, and store
# locations, so no two scripts can drift to different conventions.

exec_die() { echo "$*" >&2; exit 2; }

# Working-tree root — the checkout you are currently on. Tracked artifacts
# belong here, because they are committed on this branch.
exec_root() {
  git rev-parse --show-toplevel 2>/dev/null || exec_die "not inside a git repository"
}

# Main repository root, identical to exec_root outside a worktree.
#
# Inside a linked worktree these differ, and the difference is load-bearing:
# removing a worktree deletes everything in it. If the execution store lived
# in the worktree, finishing a branch would destroy the very reports, verdicts,
# and rulings the Executor exists to keep. --git-common-dir points at the main
# repository's .git from any worktree, so its parent is the durable root.
exec_main_root() {
  local common
  common=$(git rev-parse --git-common-dir 2>/dev/null) || exec_die "not inside a git repository"
  case "$common" in
    /*) ;;                                   # already absolute
    *)  common="$(exec_root)/$common" ;;     # relative, e.g. plain ".git"
  esac
  cd "$(dirname "$common")" && pwd
}

# Tracked thinking store: worktree root, so specs and plans commit on the
# branch that produced them.
#
# The `local root` + `|| return` shape is load-bearing: written as
# `echo "$(exec_root)/docs/executor"` the failure of exec_root is swallowed
# by the substitution — the subshell exits, `$( )` yields empty, and `echo`
# still succeeds, so callers got a plausible-looking absolute path built on
# nothing (`/docs/executor`) instead of a failure. Outside a repository that
# is worse than wrong: `"$store"/*/INDEX.md` then globs the filesystem root.
exec_docs_store() {
  local root
  root=$(exec_root) || return 2
  echo "$root/docs/executor"
}

# Untracked execution store: main root, so it survives worktree teardown and
# every worktree of the same repository shares one execution record. Plan IDs
# are unique repo-wide, so sharing cannot collide.
exec_run_store() {
  local root
  root=$(exec_main_root) || return 2
  echo "$root/.executor"
}

# Read one frontmatter scalar from a markdown file. Frontmatter is the block
# between the first '---' line and the next '---' line. Prints nothing when
# absent, so callers can test for empty.
exec_frontmatter() {
  local file=$1 key=$2
  [ -f "$file" ] || return 0
  awk -v key="$key" '
    { sub(/\r$/, "") }                   # CRLF files: compare and match CR-stripped lines
    NR == 1 && $0 != "---" { exit }
    NR == 1 { infm = 1; next }
    infm && $0 == "---" { exit }
    infm {
      # match "key: value", tolerating surrounding whitespace
      if (match($0, "^[ \t]*" key "[ \t]*:")) {
        v = substr($0, RSTART + RLENGTH)
        sub(/\r$/, "", v)                   # CRLF files: strip carriage return
        gsub(/^[ \t]+|[ \t]+$/, "", v)
        gsub(/^["'\'']|["'\'']$/, "", v)
        print v
        exit
      }
    }
  ' "$file"
}

# INIT-0004-P01 -> INIT-0004
exec_initiative_of() {
  case "$1" in
    INIT-[0-9][0-9][0-9][0-9]*) echo "${1:0:9}" ;;
    *) return 1 ;;
  esac
}

# INIT-0004-P01 -> P01
exec_plan_segment_of() {
  case "$1" in
    INIT-[0-9][0-9][0-9][0-9]-P[0-9][0-9]) echo "${1:10}" ;;
    *) return 1 ;;
  esac
}

# Zero-pad a bare number to two digits; pass through anything already padded.
exec_pad2() { printf '%02d' "$((10#${1#0}))" 2>/dev/null || echo "$1"; }

# Resolve an initiative's folder from its ID. Folder names are
# INIT-NNNN-<slug>, so the ID prefix is the lookup key and the slug is
# cosmetic.
exec_initiative_dir() {
  local id=$1 store
  store=$(exec_docs_store)
  [ -d "$store" ] || exec_die "no initiative store at $store"
  local match
  match=$(find "$store" -maxdepth 1 -type d -name "${id}-*" -print -quit 2>/dev/null)
  [ -n "$match" ] || match=$(find "$store" -maxdepth 1 -type d -name "$id" -print -quit 2>/dev/null)
  [ -n "$match" ] || exec_die "no initiative folder for $id under $store"
  echo "$match"
}

# The same lookup, but printing nothing instead of dying when the
# initiative does not exist. Callers that merely want to ask "is this run
# in flight?" need this; exec_initiative_dir's exec_die calls `exit`, and
# an `exit` inside a command substitution tears down the whole subshell —
# a `|| true` written alongside it inside the same $( ) never runs, and
# under `set -e` the caller dies instead of seeing an empty result.
exec_initiative_dir_opt() {
  local id=$1 store match
  store=$(exec_docs_store 2>/dev/null) || return 0
  [ -d "$store" ] || return 0
  match=$(find "$store" -maxdepth 1 -type d -name "${id}-*" -print -quit 2>/dev/null) || return 0
  [ -n "$match" ] || match=$(find "$store" -maxdepth 1 -type d -name "$id" -print -quit 2>/dev/null) || return 0
  [ -n "$match" ] && echo "$match"
  return 0
}

# ------------------------------------------------------------------
# Autonomous policy: which phase gates may be cleared without a human.
#
# The file is `autonomous.md` at the initiative's root:
#
#   ---
#   kind: autonomous
#   initiative: INIT-0001
#   enabled: true
#   ---
#
#   | Phase | Mode | Why |
#   |---|---|---|
#   | intake | deny | the charter is the human's to approve |
#   | execution | allow | every stage is gated; workers are dispatched, not self-approved |
#
# Modes are `deny`, `gate`, `allow`. Anything else — a missing file, a
# missing row, an unparseable mode, or `enabled: false` — reads as `deny`.
# That default is the whole point: a policy that fails open turns a typo in
# a table cell into an unattended phase gate, which is the one failure this
# file exists to make impossible.
exec_autonomous_mode() {
  local dir=${1:-} phase=${2:-}
  local f="$dir/autonomous.md"
  [ -n "$dir" ] && [ -f "$f" ] || { echo "no policy"; return 0; }
  exec_frontmatter "$f" enabled 2>/dev/null | grep -q '^true$' || { echo "disabled"; return 0; }
  local mode
  mode=$(awk -F'|' -v ph="$phase" '
    /^\|[ \t]*Phase[ \t]*\|/ {
      for (i = 2; i <= NF; i++) {
        c = $i; gsub(/^[ \t]+|[ \t]+$/, "", c)
        if (c == "Phase") pi = i
        else if (c == "Mode") mi = i
      }
      next
    }
    pi && $0 ~ ("^\\|[ \t]*" ph "[ \t]*\\|") {
      m = $mi; gsub(/^[ \t]+|[ \t]+$/, "", m)
      print m; exit
    }
  ' "$f" 2>/dev/null)
  case "${mode:-}" in
    deny|gate|allow) echo "$mode" ;;
    # An unlisted or unrecognized phase is denied, never guessed at.
    *) echo "deny" ;;
  esac
}

# Ensure the run store exists and is self-ignoring. Writing the .gitignore
# unconditionally means no subsystem can forget it and no user has to add it
# by hand — that omission is what made the legacy store pollute git status.
exec_ensure_run_store() {
  local store
  store=$(exec_run_store)
  mkdir -p "$store"
  [ -f "$store/.gitignore" ] || printf '*\n' > "$store/.gitignore"
  echo "$store"
}

# The plan's execution workspace: .executor/<INIT>/<Pnn>/
# Resolved from the plan's `id:` frontmatter so renaming the plan file never
# orphans its artifacts. Plans predating the Executor have no id: — those fall
# back to the file's basename, which preserves legacy behaviour exactly.
exec_workspace_dir() {
  local plan=$1
  [ -f "$plan" ] || exec_die "no such plan file: $plan"
  local store plan_id init seg dir
  store=$(exec_ensure_run_store)
  plan_id=$(exec_frontmatter "$plan" id)

  if [ -n "$plan_id" ] && init=$(exec_initiative_of "$plan_id") \
     && seg=$(exec_plan_segment_of "$plan_id"); then
    dir="$store/$init/$seg"
  else
    local slug
    slug=$(basename "$plan" .md)
    [ -n "$slug" ] && [ "$slug" != "." ] && [ "$slug" != ".." ] \
      || exec_die "cannot derive a workspace name from: $plan"
    dir="$store/legacy/$slug"
  fi

  mkdir -p "$dir/briefs" "$dir/reports" "$dir/reviews/diffs" "$dir/reviews/verdicts"
  echo "$dir"
}

# Reduce a plan ledger to the latest state per task: one "tid<TAB>state"
# line per task, input order retained implicitly by last-write-wins.
#
# Two line shapes are real in the wild and both are parsed:
#   canonical:  INIT-0004-P01-T03: complete (commits a1b2c3d..d4e5f6a)
#   narrative:  - 2026-09-25T09:56Z — T03 complete (b8af4bc) — APPROVED
#               - T03 APPROVED (dd605c3f, spec 4.7)
# The narrative shape is drift — writers MUST emit the canonical form — but
# a parser that cannot read it audits nothing, which is how verdict and
# task-table checks silently no-oped in live runs. 'approved' normalizes to
# 'complete': a task whose review passed is complete for audit purposes.
# The state returned is the first word after the task marker, lowercased;
# trailing annotations stay available in the raw line, never in the state.
exec_ledger_states() {
  local progress=$1 pid=$2
  [ -f "$progress" ] || return 0
  awk -v pid="$pid" '
    {
      line = $0
      # Canonical: "^<pid>-T<nn>: <state>", optionally bullet-prefixed —
      # the only form scripts write. Anchored to line start (after an
      # optional bullet) on purpose: seed guidance text and prose that
      # merely mention an ID ("Example: X-T03: dispatched") must not parse
      # as a real event — that false positive was a live defect.
      if (match(line, "^[ \t]*(-[ \t]+)?" pid "-T[0-9][0-9]:[ \t]")) {
        seg = substr(line, RSTART, RLENGTH)
        tid = seg; sub(/^[ \t]*-[ \t]+/, "", tid); sub(/:.*/, "", tid)
        st = substr(line, RSTART + RLENGTH); sub(/[ (].*$/, "", st)
        last[tid] = tolower(st)
        next
      }
      # Narrative drift: a bullet line carrying a bare T<nn> token followed
      # by a state word. The bullet requirement is what keeps italic
      # guidance text ("…shape: X-T03: complete…") from self-matching.
      if (line ~ /^[ \t]*- / && match(line, /(^|[^A-Za-z0-9-])T[0-9][0-9][ \t]+(dispatched|in-fix|complete|parked|approved|fix|ruling|blocked|minor)/)) {
        seg = substr(line, RSTART, RLENGTH)
        t = seg; sub(/^[^A-Za-z0-9-]*/, "", t); sub(/[ \t].*/, "", t)
        st = seg; sub(/.*[ \t]/, "", st); st = tolower(st)
        if (st == "approved") st = "complete"
        last[pid "-" toupper(t)] = st
      }
    }
    END { for (t in last) print t "\t" last[t] }
  ' "$progress"
}

# Count ledger lines that record a task state but are NOT the strict
# canonical "^<pid>-T<nn>: " form — the drift the dual parser tolerates.
# check reports these as NOTEs: readable but one grammar change away from
# invisible. A bulleted full-ID line parses (the ID is unambiguous) but is
# still drift; a narrative bullet is drift too.
exec_ledger_drift_count() {
  local progress=$1 pid=$2
  [ -f "$progress" ] || { echo 0; return 0; }
  awk -v pid="$pid" '
    $0 ~ ("^" pid "-T[0-9][0-9]: ") { next }
    $0 ~ ("^[ \t]*-[ \t]+" pid "-T[0-9][0-9]:") { n++; next }
    /^[ \t]*- / && match($0, /(^|[^A-Za-z0-9-])T[0-9][0-9][ \t]+(dispatched|in-fix|complete|parked|approved|fix|ruling|blocked|minor)/) { n++ }
    END { print n + 0 }
  ' "$progress"
}

# Record the branch a task is executing on. Two surfaces, one act:
#
#   - the ledger's State changes line, canonical shape, which is what
#     exec_ledger_states parses and what a resume scan reads;
#   - the dispatches.md Branch cell, which is what a human reads.
#
# The dispatch cell is best-effort: a task with no dispatches row yet gets
# no row created here (rows carry Agent/Model the controller owns), and
# the ledger line is the authoritative record either way.
#
#   exec_record_task_branch DIR TASK_ID BRANCH BASE_SHA
exec_record_task_branch() {
  local dir=$1 tid=$2 branch=$3 base=$4
  [ -f "$dir/progress.md" ] || return 0
  printf '%s: dispatched (branch %s, base %s)\n' "$tid" "$branch" "$base" >> "$dir/progress.md"
  local dfile="$dir/dispatches.md"
  [ -f "$dfile" ] || return 0
  local tmp
  tmp=$(mktemp "$dir/.branch.XXXXXX") || return 0
  if awk -v tid="$tid" -v branch="$branch" '
    BEGIN { bcol = 0; last = 0 }
    $0 ~ /^\|[ \t]*Task[ \t]*\|/ {
      # Locate the Branch column by name — a differently-shaped table is
      # never rewritten in the wrong cell.
      n = split($0, h, "|")
      for (i = 2; i <= n; i++) {
        c = h[i]; gsub(/^[ \t]+|[ \t]+$/, "", c)
        if (c == "Branch") { bcol = i; break }
      }
      rows[NR] = $0; next
    }
    $0 ~ ("^\\|[ \t]*" tid "(-R[0-9]+)?[ \t]*\\|") { last = NR }
    { rows[NR] = $0 }
    END {
      if (bcol && last) {
        split(rows[last], f, "|")
        f[bcol] = " " branch " "
        rebuilt = f[1]
        for (i = 2; i <= length(f); i++) rebuilt = rebuilt "|" f[i]
        rows[last] = rebuilt
      }
      for (i = 1; i <= NR; i++) print rows[i]
    }
  ' "$dfile" > "$tmp"; then
    mv "$tmp" "$dfile"
  else
    rm -f "$tmp"
  fi
  return 0
}

# The branch a task is recorded on, or empty. Reads the ledger's canonical
# dispatch line ("<tid>: dispatched (branch <name>, base <sha>)") — the
# same line exec_record_task_branch writes.
exec_task_branch() {
  local dir=$1 tid=$2
  [ -f "$dir/progress.md" ] || return 0
  awk -v tid="$tid" '
    $0 ~ ("^" tid ": dispatched \\(branch ") {
      line = $0
      sub(/^.*\(branch /, "", line)
      sub(/,.*$/, "", line)
      b = line
    }
    END { if (b != "") print b }
  ' "$dir/progress.md"
}

# The fork commit recorded beside a task, or empty. Reads any canonical
# dispatched line carrying "base <sha>" — the branch form
# ("dispatched (branch <name>, base <sha>)") and the bare annotation form
# ("dispatched (agent X, base <sha>)") a sequential plan writes, which has
# no branch to name. Last match wins, same as exec_task_branch.
exec_task_branch_base() {
  local dir=$1 tid=$2
  [ -f "$dir/progress.md" ] || return 0
  awk -v tid="$tid" '
    $0 ~ ("^" tid ": dispatched \\(") && $0 ~ /( |,)base / {
      line = $0
      sub(/^.* base /, "", line)
      sub(/[ ),].*$/, "", line)
      b = line
    }
    END { if (b != "") print b }
  ' "$dir/progress.md"
}

# Append one dispatches.md row honoring the file's own header — column
# order and column SET both vary in the wild (older stores lack Branch and
# Last-Seen). Values arrive \x01-joined as alternating NAME VALUE pairs in
# $2 — awk cannot see NUL but \x01 survives; callers never emit it in cell
# text. A column the table lacks is dropped; a column the table carries
# but the caller omits is em-dash.
#   exec_dispatch_append DFILE $'Task\x01TID\x01Role\x01impl\x01…'
exec_dispatch_append() {
  local dfile=$1 pairs=$2 tmp
  [ -f "$dfile" ] || return 1
  tmp=$(mktemp "${dfile}.XXXXXX") || return 1
  awk -v args="$pairs" '
    BEGIN {
      na = split(args, a, "\x01")
      for (i = 1; i + 1 <= na; i += 2) v[a[i]] = a[i + 1]
    }
    /^\|[ \t]*Task[ \t]*\|/ && !done {
      n = split($0, h, "|")
      line = "|"
      for (i = 2; i < n; i++) {
        c = h[i]; gsub(/^[ \t]+|[ \t]+$/, "", c)
        val = (c in v) ? v[c] : "—"
        line = line " " val " |"
      }
      done = 1
    }
    # The row is built from the table header, then appended at EOF —
    # rows grow downward, newest last, per the seeded file contract.
    { print }
    END { if (done) print line }
  ' "$dfile" > "$tmp" && mv "$tmp" "$dfile"
}

# Set one named column on every OPEN row for TASK (Outcome running or
# revived-rvN). Columns are located by header name; a table without the
# column is a no-op, matching the readers' tolerance for older stores.
#   exec_dispatch_set DFILE TASK_ID COLUMN VALUE
exec_dispatch_set() {
  local dfile=$1 task=$2 col=$3 val=$4 tmp
  [ -f "$dfile" ] || return 1
  tmp=$(mktemp "${dfile}.XXXXXX") || return 1
  awk -v t="$task" -v col="$col" -v val="$val" '
    BEGIN { FS = "|"; OFS = "|" }
    /^\|[ \t]*Task[ \t]*\|/ {
      for (i = 2; i <= NF; i++) {
        c = $i; gsub(/^[ \t]+|[ \t]+$/, "", c)
        if (c == "Task") ti = i
        if (c == "Outcome" || c == "Status") oi = i
        if (c == col) ci = i   # target may BE Outcome — test it last
      }
      print; next
    }
    /^\|/ {
      if (!ti || !ci) { print; next }
      cell = $ti; gsub(/[ \t]/, "", cell)
      if (cell != t) { print; next }
      o = oi ? $oi : ""; gsub(/^[ \t]+|[ \t]+$/, "", o)
      if (o != "running" && o !~ /^revived-rv[0-9]+$/) { print; next }
      $ci = " " val " "
      print; next
    }
    { print }
  ' "$dfile" > "$tmp" && mv "$tmp" "$dfile"
}

# The task segment of a full task ID: INIT-0004-P01-T03 -> 3.
# Caller validates the ID belongs to the plan first.
exec_task_num() { echo "${1##*-T}" | sed 's/^0*//'; }

# ------------------------------------------------------------------
# The machine-readable tables every consumer shares. Skill prose used to
# carry these as markdown the pump transcribed by hand; a second copy is
# how the docs and the scripts tell two stories.

# Verb → actuator decision table. `counted` marks the verbs that promise a
# state change — the no-progress guard may count only those; WAIT/ASK/DONE
# await an external event and must never accumulate toward an
# ADJUDICATE loop on a healthy run.
#   verb | actuator | counted
exec_verbs() {
  cat <<'EOF'
REPAIR-STATE|run the named repair (usually exec-workspace PLAN)|yes
RUN-START|exec-run PLAN start|yes
DISPATCH|exec-dispatch PLAN --task N --role impl; spawn AGENT on PROMPT|yes
REVIEW|exec-dispatch PLAN --role review --task Tnn; spawn reviewer|yes
FIX|exec-dispatch PLAN --role fix --task Tnn; spawn fix implementer|yes
REVIVE|exec-ladder PLAN TID revive; spawn AGENT on PROMPT|yes
REDISPATCH|exec-ladder PLAN TID redispatch; spawn AGENT on PROMPT|yes
ADJUDICATE|exec-adjudicate PLAN TID; spawn SUPERVISOR on PROMPT|yes
REPORT|exec-report PLAN REPORT_FILE (gate-on-commit)|yes
GATE-STAGE|exec-run PLAN complete|yes
PHASE-ENTER|exec-initiative phase INIT PHASE entered, then exec-dispatch --role author|yes
PHASE-GATE|exec-present INIT PHASE to the human, or exec-gate INIT PHASE --auto|yes
CRITIQUE|exec-critique INIT COMPONENT init, then dispatch AUDIT per the phase skill|yes
ASK|relay the topic to the human; record the answer with exec-ruling|no
WAIT|idle one turn; the emit carries the wake condition|no
DONE|report the finished state and stop|no
EOF
}

# Dispatch registry — the machine-readable form of references/layout.md's
# role table. needs: brief = exec-brief+exec-context; diff = exec-review-
# package; fix = exec-fix-package; none = key=value slots only.
#   role | id_pattern | template (relative to skills/) | needs
# <TID>/<Pnn>/<Tnn>/<Vnn>/<BRN>/<L>/<C>/<nn> are substituted at mint time.
exec_roles() {
  cat <<'EOF'
impl|IMPL-<Pnn>-<Tnn>[-Rnn]|executor-execution/implementer-prompt.md|brief
review|REVIEW-<Pnn>-<Tnn>-R<nn>|executor-review/task-reviewer-prompt.md|diff
re-review|REVIEW-<Pnn>-<Tnn>-R<nn>|executor-review/re-review-prompt.md|diff
final-review|REVIEW-<Pnn>-final|executor-review/final-reviewer-prompt.md|diff
fix|IMPL-<Pnn>-<Tnn>[-Rnn]|executor-execution/implementer-prompt.md|fix
verify|VERIFY-<Pnn>-<Vnn>[-Rnn]|executor-verification/evidence-runner-prompt.md|none
supervisor|SUPERVISOR-<Pnn>-<Tnn>|executor/supervisor-prompt.md|none
decide|DECIDE-<Pnn>-<Tnn>|executor/decide-prompt.md|none
author|AUTHOR-<phase>|executor/author-prompt.md|none
EOF
}

# One exec_roles row for ROLE, or exit 2 — an unregistered role is a typo,
# and a dispatch the registry cannot name is a dispatch with no contract.
exec_role() {
  local row
  row=$(exec_roles | awk -F'|' -v r="$1" '$1 == r { print; exit }')
  [ -n "$row" ] || exec_die "unregistered dispatch role: $1 (want one of: $(exec_roles | cut -d'|' -f1 | tr '\n' ' '))"
  echo "$row"
}

# Does the named product exist? Spec forms:
#   none            never exists on disk (liveness by heartbeat alone)
#   file:PATH       -s test on an exact path
#   glob:DIR:PAT    any file matching PAT under DIR (verdicts are globbed)
exec_product_exists() {
  local spec=$1
  case "$spec" in
    ""|none)  return 1 ;;
    file:*)   [ -s "${spec#file:}" ] ;;
    glob:*)
      # bash 3.2 evaluates every word in a `local` before any assignment —
      # `local rest=… d=${rest%%:*}` reads rest unbound under set -u.
      local rest d pat
      rest=${spec#glob:}; d=${rest%%:*}; pat=${rest#*:}
      ls "$d"/$pat >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}
# Seed a plan workspace's four ledger files (idempotent — existing files
# are never rewritten). Every script that writes into a workspace calls
# this first, so no entry point can produce the bare-dir drift seen in
# live runs (a P02 workspace with no rulings/preflight/frontmatter because
# the controller resolved paths by hand instead of running exec-workspace).
#   exec_seed_workspace DIR PLAN_FILE
exec_seed_workspace() {
  local dir=$1 plan=$2
  local plan_id spec_id stamp
  plan_id=$(exec_frontmatter "$plan" id)
  spec_id=$(exec_frontmatter "$plan" spec)
  [ -n "$plan_id" ] || plan_id="(no id: — legacy plan)"
  [ -n "$spec_id" ] || spec_id="(none)"
  stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  if [ ! -f "$dir/progress.md" ]; then
    cat > "$dir/progress.md" <<EOF
---
kind: ledger
plan: $plan_id
plan_file: $plan
spec: $spec_id
created_at: $stamp
updated_at: $stamp
---

# Executor ledger

*A ledger whose plan: line names a different plan is not yours — leave it and start your own. One line per state change goes under "## State changes" at the bottom; the table below is the scan index. Bump updated_at on every append — a stale updated_at is a NOTE in exec-run check.*

## Task status

*State: pending | dispatched | in-fix | complete | parked | blocked. One row per task, filled as it moves. The resume scan reads this table first: a task with no row has never been dispatched.*

| Task | State | Commits | Review | Notes |
|---|---|---|---|---|

## State changes

*Append-only, one line per state change, newest last. Canonical shape is one ID-prefixed line per event — the task's full ID, a colon, then the state word (dispatched / in-fix / complete / parked) with optional annotations. Narrative bullet lines are tolerated by the parser but flagged as drift by exec-run check — write the canonical form. Never quote an example task ID in this file — the ledger parser will read it as a real event.*
EOF
  fi

  [ -f "$dir/rulings.md" ] || cat > "$dir/rulings.md" <<EOF
---
kind: rulings
plan: $plan_id
plan_file: $plan
created_at: $stamp
updated_at: $stamp
---

# Rulings — $plan_id

*Append-only. Every decision taken on the human's behalf, written the moment it is made and mirrored into .local/decisions/ — including questions answered by the human mid-run (logged by exec-ruling with the question attached). Entries are appended at the end of this file by exec-ruling.*
EOF

  [ -f "$dir/preflight-scan.md" ] || cat > "$dir/preflight-scan.md" <<EOF
---
kind: preflight
plan: $plan_id
plan_file: $plan
created_at: $stamp
updated_at: $stamp
---

# Preflight conflict scan — $plan_id

*One row per task pair sharing a file or interface, one row per task for self-consistency, and a ruling beside every finding. Written before Task 1 dispatches; read whenever a task surprises you.*

## Scan

*Severity: conflict | self-inconsistent | clean. Every pair sharing a file or symbol gets a row; every task gets a self-check row. A finding with no ruling is unresolved — do not dispatch until every finding is ruled.*

| Tasks | Shared surface | Produced vs consumed | Finding | Severity | Ruling |
|---|---|---|---|---|---|

## Method

*What was checked: the dependency map rows, the file map, the interface signatures, the test expectations. State the inputs you walked so a reader can see the scan's scope.*

Check every task pair sharing a file, every interface contract the plan cites, and every task against itself:

- Signature resolution — every consumed reference resolves to a produced signature: same name, same shape, same argument order.
- Interface-contract consistency — two contracts defining the same field or type declare the same shape; dict[str, list[str]] beside a record shape for one name is a conflict, not a dialect.
- Prose-vs-code consistency — implementation code embedded in a task body does not contradict that task's own Requirements/Produces line.
- Unspecified contract points — a field used across a seam whose element type or shape no cited contract defines gets a Finding row naming the field and the seam.
EOF

  [ -f "$dir/dispatches.md" ] || cat > "$dir/dispatches.md" <<EOF
---
kind: dispatches
plan: $plan_id
plan_file: $plan
created_at: $stamp
updated_at: $stamp
---

# Dispatch log — $plan_id

*Context: the brief and context file paths each agent received, so 'bad context or bad model?' has a one-line answer. Rows append BELOW the header, never above it.*
*Agent identities follow the grammar ROLE-Pnn-Tnn[-Rnn]: IMPL for implementers, REVIEW for reviewers (round-suffixed, REVIEW-P01-final for the whole-branch review), VERIFY for evidence runs. A resumed agent keeps its identity. See references/layout.md.*
*Branch is the task branch the agent worked on (task/<TASK-ID>), written by exec-branch task start; a sequential plan leaves it empty.*
*Last-Seen is the liveness witness exec-step reads: exec-dispatch and exec-ladder stamp it at write time, exec-seen refreshes it when the pump relays worker output, and the worker beats state/<TASK-ID>.heartbeat via exec-heartbeat. A pump that stamped it every fold would make the fallback permanently fresh — no per-turn refresh here. Started alone is day-granular, which cannot tell a slow worker from a dead one. Absence of the column in an older workspace is tolerated — readers locate it by name and fall back to Started.*

| Task | Role | Model | Agent | Branch | Started | Outcome | Context | Last-Seen |
|---|---|---|---|---|---|---|---|---|
EOF
}

# Seed the initiative-level rulings log — the home for decisions that
# span plans (plan-regression rulings, contract amendments, answered
# questions that affect the whole initiative). Created on first need by
# exec-workspace or exec-ruling; identical contract to the per-plan log.
exec_seed_initiative_rulings() {
  local init_id=$1
  local store rdir file stamp
  store=$(exec_ensure_run_store)
  rdir="$store/$init_id"
  file="$rdir/rulings.md"
  [ -f "$file" ] && { echo "$file"; return 0; }
  mkdir -p "$rdir"
  stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  cat > "$file" <<EOF
---
kind: rulings
initiative: $init_id
created_at: $stamp
updated_at: $stamp
---

# Rulings — $init_id (initiative-wide)

*Append-only. Decisions that span or transcend a single plan — plan-set regression rulings, contract amendments (IFCE/SPEC), questions answered by the human mid-run. Per-plan rulings stay in the plan's own rulings.md; a decision that later plans must obey belongs here. Entries are appended by exec-ruling with TASK_ID 'initiative'.*
EOF
  echo "$file"
}

# The initiative-level execution directory: .executor/<INIT>/ — home of
# artifacts that span plans (plan-regression/, rulings.md). mkdir so the
# contract location always exists when a plan workspace does.
exec_initiative_run_dir() {
  local plan_id=$1 init dir
  init=$(exec_initiative_of "$plan_id") \
    || exec_die "cannot derive initiative from plan id '$plan_id'"
  dir="$(exec_ensure_run_store)/$init"
  mkdir -p "$dir"
  echo "$dir"
}

# Extract a task's ID from its plan heading.
# Heading form: '### Task 3: Name — `INIT-0004-P01-T03`'
exec_task_id() {
  local plan=$1 n=$2
  awk -v n="$n" '
    {
      line = $0
      indent = 0
      while (substr(line, indent + 1, 1) == " ") indent++
      stripped = substr(line, indent + 1)
      if (stripped ~ /^(`{3,}|~{3,})/) {
        match(stripped, /^(`{3,}|~{3,})/)
        len = RLENGTH
        ch = substr(stripped, 1, 1)
        if (!infence) { infence = 1; flen = len; fch = ch }
        else if (ch == fch && len >= flen) { infence = 0 }
      }
    }
    !infence && $0 ~ ("^### Task[ \t]+" n "([^0-9]|$)") {
      if (match($0, /INIT-[0-9]{4}-P[0-9]{2}-T[0-9]{2}/)) {
        print substr($0, RSTART, RLENGTH)
      }
      exit
    }
  ' "$plan"
}

# Task body extraction shared by exec-brief, exec-context, and
# exec-review-package. Fence tracking follows CommonMark rules the plan
# format relies on: backtick and tilde fences, fence length (a shorter
# run does not close a longer one), and indentation up to three spaces.
# Everything else (indented code blocks) is out of scope for plans and
# rejected by plan lint, not silently parsed here.
exec_task_body() {
  local plan=$1 n=$2
  awk -v n="$n" '
    {
      line = $0
      # Measure leading whitespace for fence detection (max 3 spaces).
      indent = 0
      while (substr(line, indent + 1, 1) == " ") indent++
      stripped = substr(line, indent + 1)
      if (stripped ~ /^(`{3,}|~{3,})/) {
        match(stripped, /^(`{3,}|~{3,})/)
        len = RLENGTH
        ch = substr(stripped, 1, 1)
        if (!infence) { infence = 1; flen = len; fch = ch }
        else if (ch == fch && len >= flen) { infence = 0 }
        # A closing fence of the same char and sufficient length closes.
        # A longer opening fence requires an equal-or-longer closer.
      }
    }
    !infence && $0 ~ ("^### Task[ \t]+" n "([^0-9]|$)") { intask = 1; next }
    # A level-2 or level-3 heading ends the task body — a plan-level
    # section after the last task is not part of that task.
    !infence && intask && /^#{2,3} / { exit }
    intask { print }
  ' "$plan"
}

# Extract one numbered requirement's full text from a spec document.
# Requirement body for the grammars real specs use: heading forms
# '### R01 — t', '### R01: t', bare '### R01', '### R01. t', and
# paragraph-form 'R01. <text>' / 'R01: <text>' items (INIT-0004-SPEC-02
# writes requirements as paragraphs, not headings). A heading-form body
# runs to the next heading; a paragraph item runs to the next R<nn> item
# or heading, and its 'R01.' marker is not part of the text. rid followed
# by a non-alphanumeric or EOL only — R011 never matches R01.
exec_requirement_body() {
  local spec=$1 rid=$2
  awk -v rid="$rid" '
    /^#+[ \t]+/ {
      if (inreq) exit
      h = $0; sub(/^#+[ \t]+/, "", h); sub(/[ \t]+$/, "", h)
      if (h ~ ("^" rid "([^0-9A-Za-z]|$)")) inreq = 1
      next
    }
    !inreq && $0 ~ ("^" rid "[.:]([ \t]+|$)") {
      inreq = 1
      line = $0
      sub(("^" rid "[.:][ \t]*"), "", line)
      if (line != "") print line
      next
    }
    inreq && /^R[0-9][0-9][.:][ \t]/ { exit }
    inreq { print }
  ' "$spec"
}

# Extract a full '## Section' body from a document, to the next '## '
# heading. Used for Interfaces and Global Constraints so long sections
# are never silently truncated. Heading match is exact: '## Interfaces'
# requested must not match '## Interfaces and seams'.
exec_section_body() {
  local doc=$1 section=$2
  awk -v sec="$section" '
    /^## / {
      if (insec) exit
      h = $0; sub(/^##[ \t]+/, "", h); sub(/[ \t]+$/, "", h)
      if (h == sec) { insec = 1; next }
    }
    insec { print }
  ' "$doc"
}

# Semantic run audit shared by exec-run check/complete and exec-branch
# audit. This is the canonical gate (/017): it parses verdict
# CONTENT (the latest verdict per task and for the branch must be clean:
# spec_verdict PASS or null — re-review verdicts carry null — with
# quality APPROVED), reduces the ledger to the
# latest state per unique task, and requires the exact plan task set.
# Ledger parsing goes through exec_ledger_states, which tolerates the
# narrative drift shape real controllers write.
# Prints diagnostics to stderr; returns nonzero on any violation.
exec_run_audit() {
  local plan=$1 dir=$2
  # Callers set plan_id; die loudly rather than auditing against an empty ID.
  local plan_id=${plan_id:?exec_run_audit: caller must set plan_id}
  local violations=0

  # --- Ledger reduction: latest state per unique task ID ----------------
  #duplicate completion lines never inflate the count, and a
  # later in-fix/reopen event supersedes an earlier complete.
  local task_states
  task_states=$(exec_ledger_states "$dir/progress.md" "$plan_id")

  # --- Expected task set from the plan ----------------------------------
  # Fence-aware: a '### Task N' inside a code fence is an example, not a
  # task — the same convention exec-plan-lint enforces.
  local expected
  expected=$(awk '{
    line = $0
    indent = 0
    while (substr(line, indent + 1, 1) == " ") indent++
    stripped = substr(line, indent + 1)
    if (match(stripped, /^(`{3,}|~{3,})/)) {
      len = RLENGTH; ch = substr(stripped, 1, 1)
      if (!infence) { infence = 1; flen = len; fch = ch }
      else if (ch == fch && len >= flen) { infence = 0 }
    }
    if (!infence && $0 ~ /^### Task [0-9]+/ &&
        match($0, /INIT-[0-9]{4}-P[0-9]{2}-T[0-9]{2}/)) {
      print substr($0, RSTART, RLENGTH)
    }
  }' "$plan" 2>/dev/null | sort -u)

  # Unknown ledger task IDs (not in the plan) are a violation.
  while IFS=$'\t' read -r tid state; do
    [ -n "$tid" ] || continue
    if ! printf '%s\n' "$expected" | grep -qxF "$tid"; then
      echo "AUDIT: $tid appears in the ledger but no task heading in $plan declares it" >&2
      violations=$((violations + 1))
    fi
  done <<< "$task_states"

  # Every expected task must be complete (latest state wins).
  local completed=0
  while IFS= read -r tid; do
    [ -n "$tid" ] || continue
    state=$(printf '%s\n' "$task_states" | awk -F'\t' -v t="$tid" '$1 == t { print $2 }')
    # Ledger grammar allows an annotation after the state word:
    # "complete (commits a1b2c3d..b7c8d9e, review clean)". Compare the word.
    if [ "${state%%[ (]*}" != "complete" ]; then
      echo "AUDIT: $tid is not complete (latest ledger state: ${state:-absent})" >&2
      violations=$((violations + 1))
    else
      completed=$((completed + 1))
      # Verdict audit: file must exist AND its content must pass.
      local vfile
      vfile=$(ls "$dir/reviews/verdicts/${tid}-R"*-verdict.md 2>/dev/null | sort | tail -1)
      if [ -z "$vfile" ]; then
        echo "AUDIT: $tid is complete but no verdict file exists in reviews/verdicts/ — the task is unjudged" >&2
        violations=$((violations + 1))
      else
        if ! exec_verdict_clean "$vfile"; then
          echo "AUDIT: $tid verdict ($(basename "$vfile")) is not clean — needs spec_verdict: PASS or null with quality: APPROVED" >&2
          violations=$((violations + 1))
        fi
      fi
    fi
  done <<< "$expected"

  # Final verdict: file must exist AND content must pass. Both filename
  # cases exist in the wild (-FINAL- on case-insensitive filesystems);
  # the canonical name is lowercase -final- per references/layout.md.
  local final="$dir/reviews/verdicts/${plan_id}-final-verdict.md"
  if [ ! -f "$final" ] && [ -f "$dir/reviews/verdicts/${plan_id}-FINAL-verdict.md" ]; then
    echo "note: ${plan_id}-FINAL-verdict.md uses uppercase FINAL — canonical is -final-; rename on next touch" >&2
    final="$dir/reviews/verdicts/${plan_id}-FINAL-verdict.md"
  fi
  if [ -f "$final" ]; then
    if ! exec_verdict_clean "$final"; then
      echo "AUDIT: final verdict is not clean — needs spec_verdict: PASS or null with quality: APPROVED" >&2
      violations=$((violations + 1))
    fi
  else
    echo "AUDIT: no final verdict ($final) — whole-branch review has not run" >&2
    violations=$((violations + 1))
  fi

  # Latest final-R verdict supersedes the base final verdict:
  # if a final fix-wave re-review failed, the run is not clean.
  # Two globs, each guarded: `ls a b` exits non-zero when either path is
  # missing (invisible on case-insensitive APFS, fatal on Linux CI), and
  # under pipefail that status propagates through the pipeline.
  local latest_final_r
  latest_final_r=$( { ls "$dir/reviews/verdicts/${plan_id}-final-R"*-verdict.md 2>/dev/null || true
                      ls "$dir/reviews/verdicts/${plan_id}-FINAL-R"*-verdict.md 2>/dev/null || true; } \
                    | sort | tail -1)
  if [ -n "$latest_final_r" ] && ! exec_verdict_clean "$latest_final_r"; then
    echo "AUDIT: latest final re-review ($(basename "$latest_final_r")) is not clean — it supersedes the earlier clean verdict" >&2
    violations=$((violations + 1))
  fi

  [ "$violations" -eq 0 ]
}


# A verdict file is clean iff spec_verdict is PASS (first-pass verdicts) or
# null (re-review verdicts carry null — the spec was judged in R01) AND the
# reviewer's gate field says quality: APPROVED. Both fields are read from
# frontmatter only — a 'spec_verdict: PASS' line in the verdict body is
# prose, not a verdict.
exec_verdict_clean() {
  local sv q
  sv=$(exec_frontmatter "$1" spec_verdict)
  q=$(exec_frontmatter "$1" quality)
  { [ "$sv" = "PASS" ] || [ "$sv" = "null" ]; } && [ "$q" = "APPROVED" ]
}

# Generic store lock: one writer at a time for any shared
# store mutation. mkdir is atomic on POSIX; a failed mkdir means the
# lock is held, and the bounded wait assumes a crashed holder after
# ~10s (same policy as exec-initiative's registry lock).
store_lock() {
  local dir=$1
  local lock="$dir/.store.lock" waited=0
  mkdir -p "$dir"
  while ! mkdir "$lock" 2>/dev/null; do
    waited=$((waited + 1))
    if [ "$waited" -gt 100 ]; then
      [ -n "$lock" ] && rm -rf "$lock"
      continue
    fi
    sleep 0.1
  done
}

store_unlock() { rmdir "$1/.store.lock" 2>/dev/null || true; }

# Unique temp name for atomic writes under a lock: shared
# fixed-name temp files are how concurrent writers lost rows.
store_tmp() { mktemp "${1%/}/.store-tmp.XXXXXX"; }

# True when a `key:` line appears inside the document's frontmatter block
# (the first ---...--- region). Body code fences and prose never satisfy
# required-field checks.
exec_frontmatter_has() {
  local file=$1 key=$2
  awk -v key="$key" '
    NR == 1 && $0 !~ /^---[[:space:]]*$/ { exit 1 }
    NR > 1 && /^---[[:space:]]*$/ { exit found ? 0 : 1 }
    $0 ~ ("^" key ":") { found = 1 }
  ' "$file"
}

# ------------------------------------------------------------------
# Worker liveness. One implementation, shared by exec-step and
# exec-supervise: two copies of these thresholds would drift, and a drift
# between "who decides a worker is dead" and "who acts on it" is exactly
# the duplicate-dispatch bug the thin-controller redesign exists to kill.

# The witness file a worker touches while it works.
exec_heartbeat_file() { echo "$1/state/$2.heartbeat"; }

# Touch the witness — a worker calls this between units of work so its
# liveness is measured by the worker, not by the pump's own cadence. A
# pump-refreshed heartbeat measures the pump and cannot tell a
# 50-minute evidence run from a corpse.
exec_touch_heartbeat() {
  local dir=$1 task=$2 f
  mkdir -p "$dir/state" 2>/dev/null || return 1
  f=$(exec_heartbeat_file "$dir" "$task")
  date -u +%Y-%m-%dT%H:%M:%SZ > "$f" 2>/dev/null || return 1
}

# Seconds since the witness was last touched; empty when there is none.
# Prints the age of a missing file as empty rather than 0 so callers can
# tell "never beat" from "beat at epoch".
exec_heartbeat_age() {
  local dir=$1 task=$2 f mtime now
  f=$(exec_heartbeat_file "$dir" "$task")
  [ -f "$f" ] || return 0
  # mtime, not the file's contents: a worker that truncates and rewrites
  # the stamp must not reset the clock it is being measured against.
  mtime=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo "")
  [ -n "$mtime" ] || return 0
  now=$(date -u +%s)
  echo $((now - mtime))
}

# Liveness of one dispatched task, from the three precedence-ordered
# signals. Prints exactly one word:
#
#   zombie   output is already on disk — the work finished, the pump died
#            before recording it. NEVER revive: a revive over a completed
#            artifact is the duplicate-dispatch bug.
#   alive    beating, or started recently enough to be plausibly working
#   suspect  stale but inside the grace window — ask, do not replace
#
# Parse an ISO-ish timestamp to a UTC epoch, identically on BSD and GNU.
#
# Two things were wrong before this existed, and both were invisible on
# macOS while CI saw only the symptom:
#
#  1. `date -j -f "%Y-%m-%d" <date>` on BSD silently IGNORES the parsed date
#     and returns roughly now, so a day-old row read as seconds old. GNU's
#     `-d` parses the date correctly. The same dispatch row was therefore
#     "alive" in one run and "dead" in the other.
#  2. A day-granular value anchored at 00:00:00 makes a worker seen at 00:01
#     and checked at 23:59 look nine hours stale, past the suspect window.
#     The schema says a day-granular witness "cannot tell a slow worker from
#     a dead one" — and a false DEAD verdict is the expensive error here,
#     because it burns a revive rung and replaces an agent that still holds
#     its context. So a bare date anchors to the END of its day: today's date
#     is fresh, yesterday's is roughly a day old.
#
# Both platforms get a fully-specified UTC string, so neither has to guess a
# default time, and neither returns "now" for a date it did not read.
exec_timestamp_epoch() { # 2026-09-29 | 2026-09-29T07:33:51Z -> epoch, or empty
  local ts=$1 dp tp
  case "$ts" in
    *T*) dp=${ts%%T*}; tp=${ts#*T}; tp=${tp%Z*}; tp=${tp%%.*} ;;
    *)  dp=$ts; tp="23:59:59" ;;
  esac
  [ -n "$dp" ] && [ -n "$tp" ] || return 0
  date -u -j -f "%Y-%m-%d %H:%M:%S" "$dp $tp" +%s 2>/dev/null \
    || date -u -d "$dp $tp" +%s 2>/dev/null || true
}

# $3 = started (YYYY-MM-DD), $4 = last-seen (may be empty),
# $5 = product spec for the zombie check (exec_product_exists form).
# Default: the task's report file — implementer rows. A reviewer row's
# product is a verdict glob, a supervisor row's is a ruling section; the
# caller derives the spec from the row's Role cell. A row whose product
# spec is wrong reports zombie forever, which reads the implementer's
# report as the reviewer's output and re-commits it — the livelock the
# spec argument exists to prevent.
exec_row_liveness() {
  local dir=$1 task=$2 started=$3 lastseen=$4 product=${5:-}
  local hb_ttl=${EXEC_HEARTBEAT_TTL:-1800}
  local suspect_ttl=${EXEC_SUSPECT_TTL:-7200}
  local dead_ttl=${EXEC_DEAD_TTL:-86400}
  local age seen seen_epoch age_s

  [ -n "$product" ] || product="file:$dir/reports/${task}-report.md"
  exec_product_exists "$product" && { echo zombie; return 0; }

  age=$(exec_heartbeat_age "$dir" "$task")
  if [ -n "$age" ]; then
    [ "$age" -le "$hb_ttl" ]      && { echo alive; return 0; }
    [ "$age" -le "$suspect_ttl" ] && { echo suspect; return 0; }
  fi

  seen=${lastseen:-$started}
  if [ -n "$seen" ]; then
    seen_epoch=$(exec_timestamp_epoch "$seen")
    if [ -n "$seen_epoch" ]; then
      age_s=$(( $(date -u +%s) - seen_epoch ))
      # A day-granular witness anchors to 23:59:59, which is still ahead of
      # now on the day it is read. Clamp: the value cannot mean "seen in the
      # future", and a negative age reaching a caller that compares it
      # against a threshold is the same class of surprise as the platform
      # divergence this replaced.
      [ "$age_s" -lt 0 ] && age_s=0
      [ "$age_s" -le "$suspect_ttl" ] && { echo alive; return 0; }
      [ "$age_s" -le "$dead_ttl" ]    && { echo suspect; return 0; }
    fi
  fi
  echo dead
}

# The canonical phase order, one source for every consumer. It lives here
# because two readers that disagree about the order produce a run that
# advances and refuses in the same turn: exec-initiative validates
# transitions against it, and exec-step folds the phase table against it to
# emit the next action. A second hand-maintained copy is exactly the drift
# that makes a phase log lie.
exec_phases() {
  echo "intake discovery architecture design specification planning plan-regression execution review verification handoff"
}

# The critique component registry: one row per AUTHORING phase, mapping it
# to the artifact set a critique stage audits and where that stage's
# clearance record lives. Every consumer reads this table — the gate in
# exec-initiative, the generic checker in exec-critique, and the skill's
# check catalogs — so adding a component is a row here, not new code.
#
#   component | phase | set_spec | summary_dir | catalog
#
# set_spec    — `;`-separated `dir:glob` pairs, resolved under the thinking
#               store's initiative dir. An empty dir (`:charter.md`) is the
#               initiative root. `-` when the component has no document set.
#               The set is what each artifact is judged AGAINST, which is
#               why an empty set is never a clean set.
# summary_dir — under the initiative's execution dir. `plans` keeps the
#               pre-existing plan-regression/ home so the shipped skill,
#               its artifacts, and its readers all stay valid.
# catalog     — the check catalog key; the critique skill owns its contents.
exec_critique_components() {
  cat <<'REGISTRY'
charter|intake|:charter.md|critique/charter|charter
discovery|discovery|discovery:${init}-RSCH-[0-9][0-9]*.md;discovery:${init}-OPTS-[0-9][0-9]*.md|critique/discovery|discovery
architecture|architecture|architecture:${init}-ARCH-[0-9][0-9]*.md;architecture:${init}-ADR-[0-9][0-9]*.md;architecture:${init}-IFCE-[0-9][0-9]*.md|critique/architecture|architecture
design|design|design:${init}-DSGN-[0-9][0-9]*.md|critique/design|design
specification|specification|specs:${init}-SPEC-[0-9][0-9]*.md;risks:${init}-RISK-[0-9][0-9]*.md;verification:${init}-VRFY-[0-9][0-9]*.md|critique/specification|specification
plans|planning|plans:${init}-P[0-9][0-9]*.md|plan-regression|plans
code|execution|-|critique/code|code
verification|verification|verification:${init}-VRFY-[0-9][0-9]*.md|critique/verification|verification
handoff|handoff|-|critique/handoff|handoff
REGISTRY
}

# One registry row for COMPONENT, or exit 2. An unregistered component is
# a typo, and a typo must fail closed: a critique stage the engine cannot
# identify is a gate nobody can evaluate.
exec_critique_component() {
  local want=$1 init=${2:-} row
  row=$(exec_critique_components | awk -F'|' -v c="$want" '$1 == c { print; exit }') || true
  [ -n "$row" ] || exec_die "unknown critique component '$want' — known: $(exec_critique_components | cut -d'|' -f1 | tr '\n' ' ')"
  # ${init} is a placeholder, not a shell expansion: the row is data, and
  # expanding it here keeps every consumer from re-deriving the globs with
  # its own idea of the initiative id.
  printf '%s\n' "$row" | sed "s/\${init}/$init/g"
}

# The component that gates PHASE, or empty when the phase is not an
# authoring phase. Resolved from the registry rather than a second table so
# a phase cannot gain a critique without the two agreeing.
exec_critique_component_for_phase() {
  local phase=$1
  exec_critique_components | awk -F'|' -v p="$phase" '$2 == p { print $1; exit }'
}

# The set of artifacts COMPONENT audits, one path per line. Derived from
# disk, never from the registry: a document that was renamed or deleted
# must leave the set, and a clearance row naming it must then read stale.
exec_critique_set() {
  local id=$1 component=$2 row base pair dir glob set_spec
  # The id is what expands the registry's ${init} placeholder; without it
  # the globs stay literal and the set silently resolves to nothing.
  row=$(exec_critique_component "$component" "$id")
  set_spec=$(printf '%s' "$row" | cut -d'|' -f3)
  [ "$set_spec" != "-" ] || return 0
  base=$(exec_initiative_dir "$id")
  while IFS= read -r pair; do
    [ -n "$pair" ] || continue
    dir=${pair%%:*}
    glob=${pair#*:}
    [ "$dir" = "$pair" ] && glob=""   # no colon: not a pair, skip
    [ -n "$glob" ] || continue
    find "$base/$dir" -maxdepth 1 -name "$glob" 2>/dev/null | sort
  # The trailing newline is load-bearing: `printf '%s'` emits none, `read`
  # then returns nonzero at EOF, and a while-read loop drops the last (for a
  # single-dir component, the only) item on the floor.
  done < <(printf '%s\n' "$set_spec" | tr ';' '\n')
}
