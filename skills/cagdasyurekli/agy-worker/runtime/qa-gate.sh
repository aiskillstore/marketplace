#!/usr/bin/env bash
# qa-gate.sh — independently verify an agy worker envelope against reality.
#
# The envelope is a CLAIM. Only driver-owned --verify commands execute here.
# Worker-supplied commands are untrusted data and are never evaluated.
#
# usage: qa-gate.sh --envelope FILE --repo DIR --base FULL_COMMIT_ID
#                   [--allow PATHGLOB]... [--only PATHGLOB]...
#                   [--expect-edits] --verify COMMAND [--verify COMMAND]...
#                   (internal verify-job handoff: --evidence-fd FD
#                    --evidence-token TOKEN)
# exit: 0 accepted · 10 scope violation · 11 untrusted command/test claim
#       12 malformed envelope · 13 expected edits missing
#       14 driver verification failed/mutated repo · 15 worker escalation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA="${AGY_WORKER_SCHEMA:-$SCRIPT_DIR/schemas/worker-result.schema.json}"

envelope=""; repo="$PWD"; base=""; expect_edits=0
evidence_fd=""; evidence_fd_seen=0; evidence_token=""; evidence_token_seen=0
evidence_python=""
allow=(); only=(); verify=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --envelope) [[ $# -ge 2 ]] || exit 64; envelope="$2"; shift 2 ;;
        --repo) [[ $# -ge 2 ]] || exit 64; repo="$2"; shift 2 ;;
        --base) [[ $# -ge 2 ]] || exit 64; base="$2"; shift 2 ;;
        --allow) [[ $# -ge 2 ]] || exit 64; allow+=("$2"); shift 2 ;;
        --only) [[ $# -ge 2 ]] || exit 64; only+=("$2"); shift 2 ;;
        --verify)
            [[ $# -ge 2 && "$2" == *[![:space:]]* ]] || {
                echo "qa-gate.sh: --verify requires a non-empty command" >&2; exit 64;
            }
            verify+=("$2"); shift 2 ;;
        --expect-edits) expect_edits=1; shift ;;
        --evidence-fd)
            [[ $# -ge 2 && $evidence_fd_seen -eq 0 ]] || exit 64
            case "$2" in ''|*[!0-9]*|0|1|2) exit 64 ;; esac
            evidence_fd="$2"
            evidence_fd_seen=1
            shift 2 ;;
        --evidence-token)
            [[ $# -ge 2 && $evidence_token_seen -eq 0 ]] || exit 64
            evidence_token="$2"
            evidence_token_seen=1
            shift 2 ;;
        *) echo "qa-gate.sh: unknown arg: $1" >&2; exit 64 ;;
    esac
done

[[ -n "$envelope" && -f "$envelope" ]] || {
    echo "qa-gate.sh: --envelope FILE required" >&2; exit 64;
}
envelope="$(cd "$(dirname "$envelope")" && pwd)/$(basename "$envelope")"
[[ -d "$repo" ]] || { echo "qa-gate.sh: --repo DIR required" >&2; exit 64; }
repo="$(cd "$repo" && pwd -P)"
[[ -f "$SCHEMA" ]] || { echo "qa-gate.sh: schema not found: $SCHEMA" >&2; exit 64; }
SCHEMA="$(cd "$(dirname "$SCHEMA")" && pwd)/$(basename "$SCHEMA")"

git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "qa-gate.sh: not a git worktree: $repo" >&2; exit 64;
}
case "$base" in
    ''|*[!0-9a-f]*)
        echo "qa-gate.sh: --base must be the full immutable commit ID captured before dispatch" >&2
        exit 64 ;;
esac
if [[ ${#base} -ne 40 && ${#base} -ne 64 ]]; then
    echo "qa-gate.sh: --base must be a full 40- or 64-character commit ID" >&2
    exit 64
fi
resolved_base="$(git -C "$repo" rev-parse --verify "$base^{commit}" 2>/dev/null)" || {
    echo "qa-gate.sh: invalid base commit: $base" >&2; exit 64;
}
[[ "$resolved_base" == "$base" ]] || {
    echo "qa-gate.sh: base did not resolve to the exact supplied commit" >&2; exit 64;
}

if [[ -n "$evidence_fd" ]]; then
    case "$evidence_token" in
        *[!0-9a-f]*|'') exit 64 ;;
    esac
    [[ ${#evidence_token} -eq 64 \
        && "${AGY_WORKER_INTERNAL_EVIDENCE_TOKEN:-}" == "$evidence_token" ]] \
        || exit 64
    evidence_python="${AGY_WORKER_INTERNAL_PYTHON:-}"
    [[ "$evidence_python" == /* && -f "$evidence_python" \
        && ! -L "$evidence_python" && -x "$evidence_python" ]] || exit 64
    "$evidence_python" -I -S -B - "$evidence_fd" <<'PY' || exit 64
import fcntl
import os
import sys

descriptor = int(sys.argv[1])
try:
    os.fstat(descriptor)
    flags = fcntl.fcntl(descriptor, fcntl.F_GETFL)
except (OSError, OverflowError, ValueError):
    raise SystemExit(1)
raise SystemExit(0 if flags & os.O_ACCMODE != os.O_RDONLY else 1)
PY
elif [[ -n "$evidence_token" ]]; then
    exit 64
fi

gate_python() {
    if [[ -n "$evidence_fd" ]]; then
        "$evidence_python" -I -S -B "$@"
    else
        python3 "$@"
    fi
}

evidence_workspace=""
evidence_envelope_sha256=""
evidence_initial_state_sha256=""

gate_cleanup_evidence() {
    local workspace="${evidence_workspace:-}"
    [[ -n "$workspace" ]] || return 0
    case "$workspace" in
        /*/agy-worker-gate.*) ;;
        *) return 1 ;;
    esac
    [[ -d "$workspace" && ! -L "$workspace" && -O "$workspace" ]] || return 1
    /bin/rm -f -- "$workspace/envelope.snapshot" 2>/dev/null || return 1
    /bin/rmdir "$workspace" 2>/dev/null || return 1
    evidence_workspace=""
}

gate_signal() {
    local signal_name="$1"
    gate_cleanup_evidence >/dev/null 2>&1 || true
    trap - "$signal_name"
    kill -s "$signal_name" "$$"
}

gate_prepare_workspace() {
    local base_dir canonical workspace old_umask rc
    for base_dir in /private/tmp /private/var/tmp /tmp /var/tmp; do
        [[ -d "$base_dir" && -w "$base_dir" ]] || continue
        canonical="$(CDPATH= cd -- "$base_dir" 2>/dev/null && pwd -P)" || continue
        case "$canonical" in
            "$repo"|"$repo"/*) continue ;;
        esac
        old_umask="$(umask)"
        umask 077
        workspace="$(/usr/bin/mktemp -d \
            "$canonical/agy-worker-gate.XXXXXX" 2>/dev/null)"
        rc=$?
        umask "$old_umask"
        [[ "$rc" == 0 && -d "$workspace" && ! -L "$workspace" \
            && -O "$workspace" ]] || continue
        /bin/chmod 700 "$workspace" 2>/dev/null || {
            /bin/rmdir "$workspace" 2>/dev/null || true
            continue
        }
        evidence_workspace="$(CDPATH= cd -- "$workspace" && pwd -P)" || {
            /bin/rmdir "$workspace" 2>/dev/null || true
            continue
        }
        return 0
    done
    return 1
}

gate_snapshot_envelope() {
    local source="$1" destination="$2"
    gate_python - "$source" "$destination" 2>/dev/null <<'PY'
import hashlib
import os
import stat
import sys

source, destination = sys.argv[1:3]
maximum = 1024 * 1024
digest = hashlib.sha256()
total = 0
source_fd = os.open(
    source,
    os.O_RDONLY
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_NONBLOCK", 0),
)
destination_fd = -1
try:
    source_metadata = os.fstat(source_fd)
    if not stat.S_ISREG(source_metadata.st_mode):
        raise OSError("envelope snapshot source is not regular")
    if source_metadata.st_size > maximum:
        raise OSError("envelope snapshot source is oversized")
    destination_fd = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    os.fchmod(destination_fd, 0o600)
    while True:
        chunk = os.read(source_fd, 1024 * 1024)
        if not chunk:
            break
        if len(chunk) > maximum - total:
            raise OSError("envelope snapshot source grew oversized")
        total += len(chunk)
        digest.update(chunk)
        view = memoryview(chunk)
        while view:
            written = os.write(destination_fd, view)
            if written <= 0:
                raise OSError("short snapshot write")
            view = view[written:]
    os.fsync(destination_fd)
finally:
    os.close(source_fd)
    if destination_fd >= 0:
        os.close(destination_fd)
print(digest.hexdigest())
PY
}

gate_emit_evidence() {
    local gate_exit="$1" gate_outcome="$2" final_state="$3" payload
    payload="$(gate_python - \
        "$resolved_base" "$evidence_envelope_sha256" \
        "$evidence_initial_state_sha256" "$final_state" \
        "$gate_exit" "$gate_outcome" <<'PY'
import json
import sys

base, envelope, initial, final, gate_exit, outcome = sys.argv[1:]
value = {
    "schema_version": 1,
    "kind": "agy-worker-gate-evidence",
    "resolved_base": base,
    "envelope_sha256": envelope,
    "initial_candidate_state_sha256": initial,
    "final_candidate_state_sha256": final,
    "gate_exit": int(gate_exit),
    "gate_outcome": outcome,
}
print(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
PY
)" || return 1
    [[ ${#payload} -le 4095 && "$payload" != *$'\n'* ]] || return 1
    printf '%s\n' "$payload" >&"$evidence_fd" || return 1
}

gate_finish() {
    local gate_exit="$1" gate_outcome="$2" final_state
    if [[ -z "$evidence_fd" ]]; then
        exit "$gate_exit"
    fi
    final_state="$(snapshot_repo)" || {
        gate_cleanup_evidence >/dev/null 2>&1 || true
        exit 70
    }
    gate_emit_evidence "$gate_exit" "$gate_outcome" "$final_state" || {
        gate_cleanup_evidence >/dev/null 2>&1 || true
        exit 70
    }
    gate_cleanup_evidence >/dev/null 2>&1 || exit 70
    exit "$gate_exit"
}

scope_check() {
    gate_python - "$envelope" "$repo" "$base" "${#allow[@]}" "${#only[@]}" \
        ${allow[@]+"${allow[@]}"} ${only[@]+"${only[@]}"} <<'PY'
import fnmatch
import json
import os
import posixpath
import subprocess
import sys

envelope_path, repo, base = sys.argv[1:4]
allow_count, only_count = map(int, sys.argv[4:6])
allow = sys.argv[6:6 + allow_count]
only = sys.argv[6 + allow_count:6 + allow_count + only_count]

def git_output(*args):
    return subprocess.run(
        ["git", "-C", repo, *args], check=True,
        stdout=subprocess.PIPE).stdout

def git_paths(*args):
    return {
        part.decode("utf-8", "surrogateescape")
        for part in git_output(*args).split(b"\0") if part
    }

def normalize_claim(path):
    if not isinstance(path, str):
        raise ValueError("file path is not a string")
    path = path.strip()
    if not path:
        raise ValueError("file path is empty")
    if os.path.isabs(path):
        # Resolve directory aliases such as macOS /var -> /private/var, but do not
        # resolve the final path component: a worker must not smuggle a symlink
        # target outside the repository into the comparison.
        parent = os.path.realpath(os.path.dirname(path))
        path = os.path.relpath(os.path.join(parent, os.path.basename(path)), repo)
    elif path.startswith("./"):
        path = path[2:]
    path = posixpath.normpath(path)
    if path in ("", ".", "..") or path.startswith("../") or posixpath.isabs(path):
        raise ValueError(f"file path escapes repository: {path!r}")
    return path

try:
    with open(envelope_path, encoding="utf-8") as handle:
        envelope = json.load(handle)
    claimed_changes = {}
    for item in envelope["files_changed"]:
        path = normalize_claim(item["path"])
        if path in claimed_changes:
            raise ValueError(f"duplicate claimed path: {path!r}")
        claimed_changes[path] = item["change"]

    parts = [part for part in git_output(
        "diff", "--name-status", "--no-renames", "-z", base, "--"
    ).split(b"\0") if part]
    if len(parts) % 2:
        raise ValueError("unexpected git name-status output")
    actual_changes = {}
    for index in range(0, len(parts), 2):
        status = parts[index].decode("ascii", "strict")
        path = parts[index + 1].decode("utf-8", "surrogateescape")
        actual_changes[path] = (
            "created" if status == "A" else
            "deleted" if status == "D" else
            "modified"
        )
    untracked = git_paths("ls-files", "--others", "--exclude-standard", "-z", "--")
    ignored = git_paths(
        "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--")
    for path in untracked | ignored:
        actual_changes.setdefault(path, "created")
except (OSError, ValueError, subprocess.CalledProcessError) as exc:
    print(f"qa-gate: cannot establish scope: {exc}", file=sys.stderr)
    sys.exit(1)

claimed = set(claimed_changes)
actual = set(actual_changes)
undeclared = {
    path for path in actual - claimed
    if not any(fnmatch.fnmatchcase(path, pattern) for pattern in allow)
}
phantom = claimed - actual
outside_policy = {
    path for path in actual
    if only and not any(fnmatch.fnmatchcase(path, pattern) for pattern in only)
}
kind_mismatches = {
    path: (claimed_changes[path], actual_changes[path])
    for path in claimed & actual
    if claimed_changes[path] != actual_changes[path]
}

if undeclared:
    print("qa-gate: SCOPE VIOLATION - changed but undeclared:", file=sys.stderr)
    for path in sorted(undeclared):
        print(f"    {path}", file=sys.stderr)
if phantom:
    print("qa-gate: SCOPE VIOLATION - declared but unchanged:", file=sys.stderr)
    for path in sorted(phantom):
        print(f"    {path}", file=sys.stderr)
if outside_policy:
    print("qa-gate: ONLY POLICY VIOLATION:", file=sys.stderr)
    for path in sorted(outside_policy):
        print(f"    {path}", file=sys.stderr)
if kind_mismatches:
    print("qa-gate: CHANGE KIND MISMATCH:", file=sys.stderr)
    for path, (claimed_kind, actual_kind) in sorted(kind_mismatches.items()):
        print(f"    {path}: claimed {claimed_kind}, actual {actual_kind}",
              file=sys.stderr)
if undeclared or phantom or outside_policy or kind_mismatches:
    sys.exit(1)
print(f"qa-gate: scope OK ({len(actual)} file(s) changed)", file=sys.stderr)
print(len(claimed))
PY
}

snapshot_repo() {
    gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
        --repo "$repo" --base "$base"
}

if [[ -n "$evidence_fd" ]]; then
    gate_prepare_workspace || exit 70
    trap 'gate_cleanup_evidence >/dev/null 2>&1 || true' EXIT
    trap 'gate_signal HUP' HUP
    trap 'gate_signal INT' INT
    trap 'gate_signal TERM' TERM
    evidence_envelope_sha256="$(gate_snapshot_envelope \
        "$envelope" "$evidence_workspace/envelope.snapshot")" || exit 70
    envelope="$evidence_workspace/envelope.snapshot"
    evidence_initial_state_sha256="$(snapshot_repo)" || exit 70
fi

if [[ -n "$evidence_fd" ]]; then
    gate_python "$SCRIPT_DIR/scripts/validate-envelope.py" "$SCHEMA" "$envelope" \
        || gate_finish 12 invalid-envelope
else
    "$SCRIPT_DIR/scripts/validate-envelope.py" "$SCHEMA" "$envelope" \
        || gate_finish 12 invalid-envelope
fi

claimed_count="$(scope_check)" || gate_finish 10 scope-violation

status="$(gate_python -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$envelope")"
requires_human="$(gate_python -c 'import json,sys; print("true" if json.load(open(sys.argv[1]))["requires_human"] else "false")' "$envelope")"

# Escalation is a valid worker outcome, but never accepted work. Scope has already
# been checked so status cannot hide edits.
if [[ "$status" != "completed" || "$requires_human" == "true" ]]; then
    echo "qa-gate: WORKER ESCALATION (status=$status requires_human=$requires_human)" >&2
    gate_finish 15 worker-escalation
fi

if (( expect_edits )) && [[ "$claimed_count" == "0" ]]; then
    echo "qa-gate: expected edits, but the completed worker changed nothing" >&2
    gate_finish 13 expected-edits-missing
fi

# Never execute commands supplied by the untrusted envelope. Workers are instructed
# to leave this list empty; a non-empty list is a contract violation, not evidence.
command_count="$(gate_python -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["commands_run"]))' "$envelope")"
test_count="$(gate_python -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["tests_run"]))' "$envelope")"
if [[ "$command_count" != "0" || "$test_count" != "0" ]]; then
    echo "qa-gate: UNTRUSTED COMMAND CLAIM - commands_run and tests_run must be empty; nothing from the envelope was executed" >&2
    gate_finish 11 untrusted-worker-claim
fi

if (( ${#verify[@]} == 0 )); then
    echo "qa-gate: at least one driver-owned --verify command is required" >&2
    exit 64
fi

before_snapshot="$(snapshot_repo)" || gate_finish 14 driver-verification-failed
for (( i=0; i<${#verify[@]}; i++ )); do
    vcmd="${verify[$i]}"
    echo "qa-gate: driver verification: $vcmd" >&2
    if [[ -n "$evidence_fd" ]]; then
        if (
            builtin eval "exec ${evidence_fd}>&-" || exit 126
            unset AGY_WORKER_INTERNAL_EVIDENCE_TOKEN AGY_WORKER_INTERNAL_PYTHON
            exec /bin/bash -c "$vcmd"
        ); then
            verifier_rc=0
        else
            verifier_rc=$?
        fi
    else
        if bash -c "$vcmd"; then
            verifier_rc=0
        else
            verifier_rc=$?
        fi
    fi
    if [[ "$verifier_rc" != 0 ]]; then
        echo "qa-gate: DRIVER VERIFICATION FAILED - '$vcmd'" >&2
        gate_finish 14 driver-verification-failed
    fi
done
after_snapshot="$(snapshot_repo)" || gate_finish 14 driver-verification-failed
if [[ "$before_snapshot" != "$after_snapshot" ]]; then
    echo "qa-gate: DRIVER VERIFICATION MUTATED THE WORKTREE" >&2
    gate_finish 14 driver-verification-failed
fi

# Re-check path policy after verification as defense in depth.
scope_check >/dev/null || gate_finish 10 scope-violation

echo "qa-gate: ACCEPTED" >&2
gate_finish 0 gate-passed
