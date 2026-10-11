#!/usr/bin/env bash
# qa-gate.sh — independently verify an agy worker envelope against reality.
#
# The envelope is a CLAIM. Only driver-owned verifier specs execute here.
# Worker-supplied commands are untrusted data and are never evaluated.
#
# usage: qa-gate.sh --envelope FILE --repo DIR --base FULL_COMMIT_ID
#                   [--allow PATHGLOB]... [--only PATHGLOB]...
#                   [--expect-edits] [--verify-env NAME]...
#                   [--verify-credential-env NAME]...
#                   --verify-argv CANONICAL_JSON_ARRAY [...]
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
verify_env_fd=""; verify_env_fd_seen=0
evidence_python=""
allow=(); only=(); verify_modes=(); verify_specs=(); verify_env=(); verify_credential_env=()
legacy_shell_verification=0
acknowledge_verifier_network=0
acknowledge_verifier_credential_access=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --envelope) [[ $# -ge 2 ]] || exit 64; envelope="$2"; shift 2 ;;
        --repo) [[ $# -ge 2 ]] || exit 64; repo="$2"; shift 2 ;;
        --base) [[ $# -ge 2 ]] || exit 64; base="$2"; shift 2 ;;
        --allow) [[ $# -ge 2 ]] || exit 64; allow+=("$2"); shift 2 ;;
        --only) [[ $# -ge 2 ]] || exit 64; only+=("$2"); shift 2 ;;
        --verify-argv)
            [[ $# -ge 2 ]] || exit 64
            verify_modes+=("argv"); verify_specs+=("$2"); shift 2 ;;
        --verify-shell)
            [[ $# -ge 2 && "$2" == *[![:space:]]* ]] || {
                echo "qa-gate.sh: shell verifier must be non-empty" >&2; exit 64;
            }
            verify_modes+=("shell"); verify_specs+=("$2"); shift 2 ;;
        --verify)
            [[ $# -ge 2 && "$2" == *[![:space:]]* ]] || {
                echo "qa-gate.sh: legacy shell verifier must be non-empty" >&2; exit 64;
            }
            verify_modes+=("legacy"); verify_specs+=("$2"); shift 2 ;;
        --legacy-shell-verification)
            (( legacy_shell_verification == 0 )) || exit 64
            legacy_shell_verification=1; shift ;;
        --acknowledge-verifier-network)
            (( acknowledge_verifier_network == 0 )) || exit 64
            acknowledge_verifier_network=1; shift ;;
        --acknowledge-verifier-credential-access)
            (( acknowledge_verifier_credential_access == 0 )) || exit 64
            acknowledge_verifier_credential_access=1; shift ;;
        --verify-env)
            [[ $# -ge 2 ]] || exit 64
            verify_env+=("$2"); shift 2 ;;
        --verify-credential-env)
            [[ $# -ge 2 ]] || exit 64
            verify_credential_env+=("$2"); shift 2 ;;
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
        --verify-env-fd)
            [[ $# -ge 2 && $verify_env_fd_seen -eq 0 ]] || exit 64
            case "$2" in ''|*[!0-9]*|0|1|2) exit 64 ;; esac
            verify_env_fd="$2"
            verify_env_fd_seen=1
            shift 2 ;;
        *) echo "qa-gate.sh: unknown arg: $1" >&2; exit 64 ;;
    esac
done

(( ${#verify_specs[@]} <= 999 )) || {
    echo "qa-gate.sh: at most 999 verifier commands are supported" >&2; exit 64;
}
legacy_seen=0; shell_seen=0
for (( verify_index=0; verify_index<${#verify_specs[@]}; verify_index++ )); do
    verify_mode="${verify_modes[$verify_index]}"
    if [[ "$verify_mode" == legacy ]]; then legacy_seen=1; shell_seen=1; fi
    if [[ "$verify_mode" == shell ]]; then shell_seen=1; fi
done
if (( legacy_seen && ! legacy_shell_verification )); then
    echo "qa-gate.sh: --verify is legacy shell verification; migrate to --verify-argv or add --legacy-shell-verification" >&2
    exit 64
fi
if (( legacy_shell_verification && ! legacy_seen )); then
    echo "qa-gate.sh: --legacy-shell-verification requires --verify" >&2
    exit 64
fi
if (( shell_seen && (! acknowledge_verifier_network || ! acknowledge_verifier_credential_access) )); then
    echo "qa-gate.sh: shell verification requires both verifier acknowledgements" >&2
    exit 64
fi

if (( verify_env_fd_seen )) && [[ "$verify_env_fd" == "$evidence_fd" ]]; then
    exit 64
fi

(( ${#verify_env[@]} + ${#verify_credential_env[@]} <= 64 )) || {
    echo "qa-gate.sh: at most 64 verifier environment names are supported" >&2; exit 64;
}
is_credential_env_name() {
    local restore_nocasematch=0 result
    shopt -q nocasematch || { restore_nocasematch=1; shopt -s nocasematch; }
    [[ "$1" == HOME || "$1" == PGPASSWORD || "$1" == MYSQL_PWD \
        || "$1" == GH_PAT || "$1" == DATABASE_URL \
        || "$1" =~ (^|_)(AUTH|COOKIE|CREDENTIALS?|HOME|KEY|PASS(WORD|WD)?|SESSION|SECRET|TOKEN)(_|$) ]]
    result=$?
    (( restore_nocasematch == 0 )) || shopt -u nocasematch
    return "$result"
}
all_verify_env=()
for verify_env_name in ${verify_env+"${verify_env[@]}"}; do
    all_verify_env+=("$verify_env_name")
done
for verify_env_name in ${verify_credential_env+"${verify_credential_env[@]}"}; do
    all_verify_env+=("$verify_env_name")
done
for verify_env_name in ${all_verify_env+"${all_verify_env[@]}"}; do
    case "$verify_env_name" in
        ''|*[!A-Za-z0-9_]*|[0-9]*|BASH_ENV|ENV|SHELLOPTS|BASHOPTS|PS4|CDPATH|GLOBIGNORE|BASH_LOADABLES_PATH|BASH_XTRACEFD|BASH_COMPAT|NODE_OPTIONS|RUBYOPT|RUBYLIB|PERL5OPT|PERL5LIB|JAVA_TOOL_OPTIONS|JDK_JAVA_OPTIONS|CLASSPATH|AGY_WORKER_SCHEMA|BASH_FUNC_*|PYTHON*|LD_*|DYLD_*|GIT_*|AGY_WORKER_INTERNAL_*)
            echo "qa-gate.sh: unsafe --verify-env name" >&2; exit 64 ;;
    esac
    [[ ${#verify_env_name} -le 128 ]] || {
        echo "qa-gate.sh: invalid --verify-env name" >&2; exit 64;
    }
    verify_env_occurrences=0
    for compared_verify_env_name in "${all_verify_env[@]}"; do
        [[ "$verify_env_name" != "$compared_verify_env_name" ]] || \
            verify_env_occurrences=$((verify_env_occurrences + 1))
    done
    (( verify_env_occurrences == 1 )) || {
        echo "qa-gate.sh: repeated --verify-env name" >&2; exit 64;
    }
done
for verify_env_name in ${verify_env+"${verify_env[@]}"}; do
    if is_credential_env_name "$verify_env_name"; then
        echo "qa-gate.sh: credential-like names require --verify-credential-env" >&2
        exit 64
    fi
done
for verify_env_name in ${verify_credential_env+"${verify_credential_env[@]}"}; do
    if ! is_credential_env_name "$verify_env_name"; then
        echo "qa-gate.sh: --verify-credential-env requires a credential-like name" >&2
        exit 64
    fi
done
if (( ${#verify_credential_env[@]} && ! acknowledge_verifier_credential_access )); then
    echo "qa-gate.sh: credential environment requires credential acknowledgement" >&2
    exit 64
fi

verifier_environment=()
append_verifier_environment() {
    local name="$1" present=""
    builtin eval "present=\${$name+x}"
    [[ -z "$present" ]] || verifier_environment+=("$name=${!name}")
}
for baseline_name in PATH TMPDIR LANG LANGUAGE LC_ALL LC_CTYPE LC_NUMERIC \
        LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS \
        LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION; do
    append_verifier_environment "$baseline_name"
done
if (( verify_env_fd_seen )); then
    (( evidence_fd_seen && evidence_token_seen )) || exit 64
    received_verify_env=()
    received_name=""
    while IFS= read -r -d '' received_name <&"$verify_env_fd"; do
        IFS= read -r -d '' received_value <&"$verify_env_fd" || exit 64
        received_allowed=0
        for verify_env_name in ${all_verify_env+"${all_verify_env[@]}"}; do
            [[ "$received_name" != "$verify_env_name" ]] || received_allowed=1
        done
        (( received_allowed )) || exit 64
        for previous_name in ${received_verify_env+"${received_verify_env[@]}"}; do
            [[ "$received_name" != "$previous_name" ]] || exit 64
        done
        received_verify_env+=("$received_name")
        verifier_environment+=("$received_name=$received_value")
    done
    [[ -z "$received_name" ]] || exit 64
    builtin eval "exec ${verify_env_fd}<&-"
elif (( ${#all_verify_env[@]} )); then
    echo "qa-gate.sh: verifier environment opt-in requires verify-job.sh private handoff" >&2
    exit 64
fi
verifier_has_bytecode_setting=0
verifier_has_pytest_setting=0
for verifier_name in ${received_verify_env+"${received_verify_env[@]}"}; do
    [[ "$verifier_name" != PYTHONDONTWRITEBYTECODE ]] || verifier_has_bytecode_setting=1
    [[ "$verifier_name" != PYTEST_ADDOPTS ]] || verifier_has_pytest_setting=1
done
(( verifier_has_bytecode_setting )) || verifier_environment+=("PYTHONDONTWRITEBYTECODE=1")
(( verifier_has_pytest_setting )) || verifier_environment+=("PYTEST_ADDOPTS=-p no:cacheprovider")

verifier_python="$(command -v python3)" || {
    echo "qa-gate.sh: verifier runtime unavailable" >&2; exit 64;
}
for (( verify_index=0; verify_index<${#verify_specs[@]}; verify_index++ )); do
    [[ "${verify_modes[$verify_index]}" != argv ]] || {
        if ! printf '%s' "${verify_specs[$verify_index]}" | \
                "$verifier_python" -I -S -B \
                "$SCRIPT_DIR/scripts/evidence_receipt.py" validate-verifier argv \
                >/dev/null 2>&1; then
            echo "qa-gate.sh: invalid --verify-argv specification" >&2
            exit 64
        fi
    }
done

[[ -n "$envelope" && -f "$envelope" ]] || {
    echo "qa-gate.sh: --envelope FILE required" >&2; exit 64;
}
envelope="$(cd "$(dirname "$envelope")" && pwd)/$(basename "$envelope")"
[[ -d "$repo" ]] || { echo "qa-gate.sh: --repo DIR required" >&2; exit 64; }
repo="$(cd "$repo" && pwd -P)"
[[ -f "$SCHEMA" ]] || { echo "qa-gate.sh: schema not found: $SCHEMA" >&2; exit 64; }
SCHEMA="$(cd "$(dirname "$SCHEMA")" && pwd)/$(basename "$SCHEMA")"

case "$base" in
    ''|*[!0-9a-f]*)
        echo "qa-gate.sh: --base must be the full immutable commit ID captured before dispatch" >&2
        exit 64 ;;
esac
if [[ ${#base} -ne 40 && ${#base} -ne 64 ]]; then
    echo "qa-gate.sh: --base must be a full 40- or 64-character commit ID" >&2
    exit 64
fi
resolved_base="$("$verifier_python" -I -S -B \
    "$SCRIPT_DIR/scripts/candidate_state.py" --repo "$repo" \
    --base "$base" --verify-base)" || {
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
        python3 -B "$@"
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
    gate_python - "$SCRIPT_DIR/scripts" "$envelope" "$repo" "$base" "${#allow[@]}" "${#only[@]}" \
        ${allow[@]+"${allow[@]}"} ${only[@]+"${only[@]}"} <<'PY'
import fnmatch
from functools import lru_cache
from pathlib import Path
import json
import os
import posixpath
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv.pop(1))
from candidate_state import _checked_git_reader

envelope_path, repo, base = sys.argv[1:4]
allow_count, only_count = map(int, sys.argv[4:6])
allow = sys.argv[6:6 + allow_count]
only = sys.argv[6 + allow_count:6 + allow_count + only_count]

git_reader = _checked_git_reader(Path(repo))

def git_output(*args):
    return git_reader(Path(repo), *args)

def git_paths(*args):
    return {
        part.decode("utf-8", "surrogateescape")
        for part in git_output(*args).split(b"\0") if part
    }

def path_matches(path, pattern):
    parts, patterns = path.split("/"), pattern.split("/")

    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(patterns):
            return i == len(parts)
        if patterns[j] == "**":
            return match(i, j + 1) or (i < len(parts) and match(i + 1, j))
        return (i < len(parts) and fnmatch.fnmatchcase(parts[i], patterns[j])
                and match(i + 1, j + 1))

    return match(0, 0)


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
    envelope_status = envelope["status"]
    requires_human = envelope["requires_human"]
    commands_run = envelope["commands_run"]
    tests_run = envelope["tests_run"]
    if (envelope_status not in ("completed", "partial", "blocked", "failed")
            or type(requires_human) is not bool
            or type(commands_run) is not list or type(tests_run) is not list
            or len(commands_run) > 9999 or len(tests_run) > 9999):
        raise ValueError("envelope control fields changed after validation")
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
except (OSError, ValueError, KeyError, TypeError) as exc:
    print(f"qa-gate: cannot establish scope: {exc}", file=sys.stderr)
    sys.exit(1)

claimed = set(claimed_changes)
actual = set(actual_changes)
undeclared = {
    path for path in actual - claimed
    if not any(path_matches(path, pattern) for pattern in allow)
}
phantom = claimed - actual
outside_policy = {
    path for path in actual
    if only and not any(path_matches(path, pattern) for pattern in only)
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
if len(claimed) > 9999:
    sys.exit(1)
print(f"{len(claimed)} {envelope_status} {'true' if requires_human else 'false'} "
      f"{len(commands_run)} {len(tests_run)}")
PY
}

snapshot_repo() {
    gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
        --repo "$repo" --base "$base"
}

snapshot_repo_with_facts() {
    gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
        --repo "$repo" --base "$base" --digest-facts
}

snapshot_repo_with_git_state() {
    gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
        --repo "$repo" --base "$base" --digest-git-state
}

snapshot_diagnostic_facts() {
    gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
        --repo "$repo" --facts
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

parse_scope_record() {
    local pattern='^([0-9]{1,4}) (completed|partial|blocked|failed) (true|false) ([0-9]{1,4}) ([0-9]{1,4})$'
    [[ "$1" =~ $pattern ]] || return 1
    scope_claimed_count="${BASH_REMATCH[1]}"
    scope_status="${BASH_REMATCH[2]}"
    scope_requires_human="${BASH_REMATCH[3]}"
    scope_command_count="${BASH_REMATCH[4]}"
    scope_test_count="${BASH_REMATCH[5]}"
}

first_scope_record="$(scope_check)" || gate_finish 10 scope-violation
parse_scope_record "$first_scope_record" || gate_finish 10 scope-violation
claimed_count="$scope_claimed_count"
status="$scope_status"
requires_human="$scope_requires_human"
command_count="$scope_command_count"
test_count="$scope_test_count"

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
if [[ "$command_count" != "0" || "$test_count" != "0" ]]; then
    echo "qa-gate: UNTRUSTED COMMAND CLAIM - commands_run and tests_run must be empty; nothing from the envelope was executed" >&2
    gate_finish 11 untrusted-worker-claim
fi

if (( ${#verify_specs[@]} == 0 )); then
    echo "qa-gate: at least one driver-owned verifier is required" >&2
    exit 64
fi

before_bundle="$(snapshot_repo_with_facts)" || gate_finish 14 driver-verification-failed
before_snapshot="${before_bundle%%$'\n'*}"
before_remainder="${before_bundle#*$'\n'}"
before_diagnostic_facts="${before_remainder%%$'\n'*}"
before_git_state="${before_remainder#*$'\n'}"
failed_verifier=""
for (( i=0; i<${#verify_specs[@]}; i++ )); do
    verifier_mode="${verify_modes[$i]}"
    [[ "$verifier_mode" != legacy ]] || verifier_mode=shell
    verifier_label="$(printf 'verify-%03d' "$((i + 1))")"
    echo "qa-gate: driver verification: $verifier_label ($verifier_mode)" >&2
    if [[ -n "$evidence_fd" ]]; then
        if (
            builtin eval "exec ${evidence_fd}>&-" || exit 126
            unset AGY_WORKER_INTERNAL_EVIDENCE_TOKEN AGY_WORKER_INTERNAL_PYTHON
            cd "$repo" || exit 126
            if [[ "$verifier_mode" == argv ]]; then
                printf '%s' "${verify_specs[$i]}" | exec /usr/bin/env -i \
                    "${verifier_environment[@]}" "$verifier_python" -I -S -B \
                    "$SCRIPT_DIR/scripts/evidence_receipt.py" execute-verifier argv
            else
                exec /usr/bin/env -i "${verifier_environment[@]}" \
                    /bin/bash -c "${verify_specs[$i]}"
            fi
        ); then
            verifier_rc=0
        else
            verifier_rc=$?
        fi
    else
        if (
            cd "$repo" || exit 126
            if [[ "$verifier_mode" == argv ]]; then
                printf '%s' "${verify_specs[$i]}" | exec /usr/bin/env -i \
                    "${verifier_environment[@]}" "$verifier_python" -I -S -B \
                    "$SCRIPT_DIR/scripts/evidence_receipt.py" execute-verifier argv
            else
                exec /usr/bin/env -i "${verifier_environment[@]}" \
                    /bin/bash -c "${verify_specs[$i]}"
            fi
        ); then
            verifier_rc=0
        else
            verifier_rc=$?
        fi
    fi
    if [[ "$verifier_rc" != 0 ]]; then
        failed_verifier="$verifier_label ($verifier_mode)"
        break
    fi
done
after_bundle="$(snapshot_repo_with_git_state)" || gate_finish 14 driver-verification-failed
after_snapshot="${after_bundle%%$'\n'*}"
after_git_state="${after_bundle#*$'\n'}"
if [[ "$before_snapshot" != "$after_snapshot" || "$before_git_state" != "$after_git_state" ]]; then
    git_state_details=""
    if [[ "$before_git_state" != "$after_git_state" ]]; then
        git_state_details="$(printf '%s\n%s\n' "$before_git_state" "$after_git_state" | \
            gate_python "$SCRIPT_DIR/scripts/candidate_state.py" --compare-git-states)" || git_state_details=""
    fi
    after_diagnostic_facts="$(snapshot_diagnostic_facts)" || after_diagnostic_facts=""
    diagnostic_details=""
    if [[ -n "$before_diagnostic_facts" && -n "$after_diagnostic_facts" ]]; then
        diagnostic_details="$(gate_python "$SCRIPT_DIR/scripts/candidate_state.py" \
            --compare-diagnostics "$before_diagnostic_facts" "$after_diagnostic_facts")" || diagnostic_details=""
    fi
    echo "qa-gate: DRIVER VERIFICATION MUTATED THE CANDIDATE${git_state_details:+: $git_state_details}${diagnostic_details:+: $diagnostic_details}; inspect paths and request same-worker repair" >&2
    [[ -z "$failed_verifier" ]] || echo "qa-gate: DRIVER VERIFICATION FAILED - $failed_verifier" >&2
    gate_finish 14 driver-verification-failed
fi
if [[ -n "$failed_verifier" ]]; then
    echo "qa-gate: DRIVER VERIFICATION FAILED - $failed_verifier" >&2
    gate_finish 14 driver-verification-failed
fi

# Re-check path policy after verification as defense in depth.
final_scope_record="$(scope_check)" || gate_finish 10 scope-violation
parse_scope_record "$final_scope_record" || gate_finish 10 scope-violation
[[ "$final_scope_record" == "$first_scope_record" ]] || gate_finish 10 scope-violation

echo "qa-gate: ACCEPTED" >&2
gate_finish 0 gate-passed
