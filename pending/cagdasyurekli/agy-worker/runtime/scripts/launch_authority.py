"""Canonical initial-task, prompt and human launch-approval bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Sequence

MAX_TASK_BYTES = 8 * 1024 * 1024
AUTHORITY_FIELDS = {
    "kind", "content", "task_sha256", "full_prompt_sha256", "workspace_template_sha256", "base_commit", "workdir",
    "staged_instruction_template_sha256", "workflow", "mode", "max_cycles",
    "idle_seconds", "hard_seconds", "max_seconds", "notice_seconds", "model",
    "effort", "allow_scoped_repair", "self_verification_manifest_sha256",
    "provider_env_names", "allow_slash_commands", "add_dirs", "provider_schema_sha256",
}


class LaunchAuthorityError(ValueError):
    """A proposed launch cannot be represented by one reviewable authority."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":")).encode("ascii") + b"\n"


def normalize_task(raw: bytes) -> tuple[bytes, str]:
    """Match Bash's task-file command substitution: remove trailing LF only."""
    if len(raw) > MAX_TASK_BYTES or b"\0" in raw:
        raise LaunchAuthorityError("task is oversized or contains NUL")
    normalized = raw.rstrip(b"\n")
    try:
        text = normalized.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise LaunchAuthorityError("task is not UTF-8") from exc
    if not text.strip():
        raise LaunchAuthorityError("task is empty")
    return normalized, text


_PREAMBLE = """You are a bounded worker. Another agent (the driver) will independently verify
everything you claim, so inaccurate self-reporting is worse than admitting failure.

__SELF_VERIFICATION_CHECK_REQUESTS__
NON-INTERACTIVE RUN:
- Respect applicable user and repository instructions (for example GEMINI.md),
  including security, privacy, permission, and scope constraints.
- If a security, privacy, permission, or scope constraint conflicts with this task
  or output contract, or a missing answer is needed to satisfy it,
  report status=blocked and requires_human=true; explain in open_questions.
  Do not bypass the constraint or assume required authorization.
- Constraints on secrets, data destinations, destructive actions, and required
  permission to act are protected; do not treat them as routine conversation.
- Nobody can answer questions during this run. Do not ask; put assumptions,
  blockers, and questions in the result as the output contract requires.
- This run's contract governs routine conversational questions and response
  formatting. If no protected constraint needs the answer, record an unanswered
  question in open_questions and a safe assumption in summary, then continue.
- Stay within the task's scope and allowed paths. Do not add CI, hooks, linters,
  formatters, type checkers, dependencies, or refactors the task did not ask for.
- Include compatible report requirements in the schema fields; use this
  contract's format when a report template is incompatible.

OUTPUT CONTRACT — non-negotiable:
- Your FINAL response must be a single JSON object matching the enforced schema.
- Do NOT write your answer to a file, artifact, or brain document.
- Do NOT reply "see the artifact" or reference an external document.
- Follow the FILE-TOOL ROOT instruction for the files_changed reference point.
  Report net created, modified, or deleted paths; omit transient touches.
- __WORKSPACE_DIRECTIVE__ Do NOT run shell or terminal tools or tests.
  __PROVIDER_EXECUTION_NOTE__ The driver's environment is the only trusted execution
  context. Leave commands_run and tests_run as empty arrays.
- If a permission gate, missing tool, or ambiguity blocks you: set
  status="blocked", requires_human=true, and explain in open_questions.
  Do not silently work around it.

TASK FOLLOWS:
"""


STAGED_INSTRUCTION = """Read '{stage_file}' as the complete prompt, including its
output contract and task. Follow it exactly. The staged job directory is
read-only context; target files named in that prompt remain readable and editable
according to --mode and --add-dir. Return the JSON envelope inline."""

WORKSPACE_TEMPLATE = """FILE-TOOL ROOT — non-negotiable:
- The exact absolute workspace root for this attempt is the JSON string {encoded_root}.
- File tools require absolute paths. Begin by listing that exact root. For each task-relative path, use an absolute child path beneath that root; never pass the relative path alone and never guess or search for another root.
- In the final schema envelope, report each files_changed[].path relative to this workspace (for example, candidate.py), never as an absolute stage path.
{change_reference}- This is {workspace_shape}. {authority_note} Do not inspect its parent, HOME, `~/.gemini`, or any other directory. Do not call shell or terminal tools.

"""
SCOPED_REFERENCE = "- In files_changed, report net changes in this Gitless stage since this stage launched. The controller checks exactly this stage's mutations.\n"
BASE_REFERENCE = "- The immutable Git base commit {base_commit} is the files_changed reference. Report cumulative net changes relative to that base commit across all cycles, including changes already present when this attempt launched. A file created in an earlier cycle and then edited remains created.\n- {change_hint}\n"
INITIAL_REFERENCE = "- In files_changed, report net changes since this provider launch.\n"
SESSION_NOTE = "This session has normal same-user filesystem and network authority; this prompt does not confine host access. Work only beneath the stated root."
NATIVE_NOTE = "Native scoped containment limits this provider to the stated root."


def workspace_prefix(root: Path, *, scoped: bool, provider_isolation: str,
                     base_commit: str | None, change_hint: str = "") -> str:
    reference = SCOPED_REFERENCE if scoped else (
        BASE_REFERENCE.format(base_commit=base_commit, change_hint=change_hint)
        if base_commit is not None else INITIAL_REFERENCE)
    return WORKSPACE_TEMPLATE.format(
        encoded_root=json.dumps(str(root), ensure_ascii=True), change_reference=reference,
        workspace_shape="the complete approved Gitless selected-content stage" if scoped
        else "the complete explicitly approved whole worktree",
        authority_note=SESSION_NOTE if provider_isolation == "session" else NATIVE_NOTE)


def workspace_template_sha256() -> str:
    return sha256(canonical([WORKSPACE_TEMPLATE, SCOPED_REFERENCE, BASE_REFERENCE,
                             INITIAL_REFERENCE, SESSION_NOTE, NATIVE_NOTE]))


def verification_request_block(required: list[str], optional: list[str]) -> str:
    return (
        "DRIVER-OWNED SELF-VERIFICATION CHECK REQUESTS:\n"
        f"- Required check IDs, run automatically: {', '.join(required) or '(none)'}\n"
        f"- Optional check IDs, request only when useful: {', '.join(optional) or '(none)'}\n"
        "- requested_check_ids may contain each optional ID at most once. "
        "Check IDs are requests, not commands or execution authority."
    )


def full_prompt(task: bytes, *, mode: str, provider_isolation: str,
                verification_block: str = "") -> bytes:
    if mode not in {"plan", "accept-edits"}:
        raise LaunchAuthorityError("mode is invalid")
    if provider_isolation not in {"session", "native"}:
        raise LaunchAuthorityError("provider isolation is invalid")
    directive = (
        "Use file tools to inspect and edit the approved workspace."
        if mode == "accept-edits" else
        "Use file tools to inspect the approved workspace only; do not edit files."
    )
    execution_note = (
        "This job runs in a normal AGY session with same-user filesystem and network "
        "authority; the selected workspace is a task instruction, not host confinement."
        if provider_isolation == "session" else
        "Under native isolation, shell tools run in a separate scratch area; their "
        "output is not evidence about the approved workspace."
    )
    preamble = (_PREAMBLE
                .replace("__SELF_VERIFICATION_CHECK_REQUESTS__", verification_block, 1)
                .replace("__WORKSPACE_DIRECTIVE__", directive, 1)
                .replace("__PROVIDER_EXECUTION_NOTE__", execution_note, 1))
    return preamble.encode("utf-8") + b"\n" + task


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def build_authority(
    *, content: dict[str, str | None], task: bytes, prompt: bytes,
    workflow: str, mode: str, max_cycles: int,
    idle_seconds: int | float, hard_seconds: int | float, max_seconds: int | float, notice_seconds: int | float,
    model: str | None, effort: str | None,
    allow_scoped_repair: bool, self_verification_manifest_sha256: str | None,
    provider_env_names: list[str], allow_slash_commands: bool,
    add_dirs: list[str], provider_schema_sha256: str, base_commit: str | None, workdir: str,
) -> dict[str, Any]:
    """Name every caller-controlled initial provider authority in one payload."""
    if provider_env_names != sorted(set(provider_env_names)):
        raise LaunchAuthorityError("provider environment names are not canonical")
    if add_dirs != sorted(set(add_dirs)):
        raise LaunchAuthorityError("additional directories are not canonical")
    return {
        "kind": "agy-worker-launch-authority-v2",
        "content": content,
        "task_sha256": sha256(task),
        "full_prompt_sha256": sha256(prompt),
        "staged_instruction_template_sha256": sha256(STAGED_INSTRUCTION.encode("utf-8")),
        "workspace_template_sha256": workspace_template_sha256(),
        "base_commit": base_commit,
        "workdir": workdir,
        "workflow": workflow,
        "mode": mode,
        "max_cycles": max_cycles,
        "idle_seconds": idle_seconds,
        "hard_seconds": hard_seconds,
        "max_seconds": max_seconds,
        "notice_seconds": notice_seconds,
        "model": model,
        "effort": effort,
        "allow_scoped_repair": allow_scoped_repair,
        "self_verification_manifest_sha256": self_verification_manifest_sha256,
        "provider_env_names": provider_env_names,
        "allow_slash_commands": allow_slash_commands,
        "add_dirs": add_dirs,
        "provider_schema_sha256": provider_schema_sha256,
    }


def approval_sha256(authority: dict[str, Any]) -> str:
    if authority.get("kind") != "agy-worker-launch-authority-v2" or set(authority) != AUTHORITY_FIELDS:
        raise LaunchAuthorityError("launch authority kind is invalid")
    if not isinstance(authority["workdir"], str) or not authority["workdir"].startswith("/") or "\0" in authority["workdir"]:
        raise LaunchAuthorityError("launch authority destination is invalid")
    for key in ("task_sha256", "full_prompt_sha256", "workspace_template_sha256",
                "staged_instruction_template_sha256", "provider_schema_sha256"):
        if not isinstance(authority[key], str) or re.fullmatch(r"[0-9a-f]{64}", authority[key]) is None:
            raise LaunchAuthorityError("launch authority digest is invalid")
    for key in ("self_verification_manifest_sha256", "base_commit"):
        value = authority[key]
        if value is not None and (not isinstance(value, str) or
                re.fullmatch(r"[0-9a-f]{64}" if key != "base_commit" else r"[0-9a-f]{40}|[0-9a-f]{64}", value) is None):
            raise LaunchAuthorityError("launch authority optional digest is invalid")
    for key in ("allow_scoped_repair", "allow_slash_commands"):
        if type(authority[key]) is not bool:
            raise LaunchAuthorityError("launch authority permission is invalid")
    if type(authority["max_cycles"]) is not int or not 1 <= authority["max_cycles"] <= 5:
        raise LaunchAuthorityError("launch authority cycle budget is invalid")
    for key in ("idle_seconds", "hard_seconds", "max_seconds", "notice_seconds"):
        if type(authority[key]) not in (int, float) or not math.isfinite(authority[key]) or not 0 < authority[key] <= 604800:
            raise LaunchAuthorityError("launch authority budget is invalid")
    if authority["workflow"] not in {"legacy", "explore", "task", "project"} or authority["mode"] not in {"plan", "accept-edits"}:
        raise LaunchAuthorityError("launch authority workflow is invalid")
    for key in ("model", "effort"):
        value = authority[key]
        if value is not None and (not isinstance(value, str) or not value or "\0" in value):
            raise LaunchAuthorityError("launch authority selector is invalid")
    if authority["model"] is None and authority["effort"] is not None:
        raise LaunchAuthorityError("launch authority effort requires model")
    for key in ("provider_env_names", "add_dirs"):
        value = authority[key]
        if (not isinstance(value, list) or any(not isinstance(item, str) for item in value)
                or value != sorted(set(value))):
            raise LaunchAuthorityError("launch authority names are invalid")
    content = authority["content"]
    if not isinstance(content, dict) or set(content) != {
            "manifest_sha256", "policy_sha256", "selected_content_sha256",
            "content_manifest_sha256", "provider_isolation", "native_grant_profile"}:
        raise LaunchAuthorityError("launch authority content is invalid")
    for key in ("manifest_sha256", "policy_sha256", "selected_content_sha256", "content_manifest_sha256"):
        value = content[key]
        if value is not None and (not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None):
            raise LaunchAuthorityError("launch authority content digest is invalid")
    if content["provider_isolation"] not in {"session", "native"} or content["native_grant_profile"] not in {"baseline", "A", "B", "AB"}:
        raise LaunchAuthorityError("launch authority isolation is invalid")
    return sha256(canonical(authority))


def changed_field(expected: dict[str, Any], actual: dict[str, Any]) -> str | None:
    # Report the caller's changed selector before its derived prompt digest.
    order = ["task_sha256", "self_verification_manifest_sha256", "allow_scoped_repair",
             "model", "effort", "mode", "workflow", "max_cycles"]
    for field in order + sorted((expected.keys() | actual.keys()) - set(order)):
        if expected.get(field) != actual.get(field):
            if field == "content" and isinstance(expected.get(field), dict) and isinstance(actual.get(field), dict):
                nested = changed_field(expected[field], actual[field])
                return f"content.{nested}"
            return field
    return None


def approval_record(path: Path, approved_sha: str) -> dict[str, Any]:
    raw = read_bound_file(path, 32 * 1024 * 1024, private=True, label="approval record")
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise LaunchAuthorityError("approval record has duplicate keys")
            result[key] = value
        return result
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
        authority = value.get("launch_authority", value.get("preview_launch_authority"))
        if not isinstance(authority, dict) or approval_sha256(authority) != approved_sha:
            raise LaunchAuthorityError("approval record does not match approved digest")
    except (UnicodeError, json.JSONDecodeError, AttributeError, RecursionError) as exc:
        raise LaunchAuthorityError("approval record is invalid") from exc
    return authority


def read_bound_file(path: Path, limit: int, *, private: bool, label: str) -> bytes:
    if not path.is_absolute() or Path(os.path.realpath(path)) != path:
        raise LaunchAuthorityError(f"{label} path is not canonical")
    descriptor = -1
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        before = os.fstat(descriptor)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid()
                or before.st_nlink != 1 or before.st_size > limit
                or (private and stat.S_IMODE(before.st_mode) != 0o600)):
            raise LaunchAuthorityError(f"{label} file authority is invalid")
        raw = bytearray()
        while chunk := os.read(descriptor, min(65536, limit + 1 - len(raw))):
            raw.extend(chunk)
            if len(raw) > limit:
                raise LaunchAuthorityError(f"{label} is oversized")
        after = os.fstat(descriptor)
        named = path.lstat()
        identity = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_uid,
                                 info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if identity(before) != identity(after) or identity(after) != identity(named):
            raise LaunchAuthorityError(f"{label} changed while reading")
        return bytes(raw)
    except OSError as exc:
        raise LaunchAuthorityError(f"{label} is unavailable") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def duration(value: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*)(s|m|h)", value)
    if match is None:
        raise LaunchAuthorityError("timeout is invalid")
    seconds = int(match[1]) * {"s": 1, "m": 60, "h": 3600}[match[2]]
    if seconds > 7 * 24 * 3600:
        raise LaunchAuthorityError("timeout exceeds limit")
    return seconds


class PreviewParser(argparse.ArgumentParser):
    def parse_args(self, args: Sequence[str] | None = None, namespace: Any = None) -> Any:
        arguments = sys.argv[1:] if args is None else args
        seen = set()
        for argument in arguments:
            option = argument.partition("=")[0]
            action = self._option_string_actions.get(option)
            if action is not None and not isinstance(action, argparse._AppendAction):
                if action.dest in seen:
                    self.error(f"repeated {option}")
                seen.add(action.dest)
        return super().parse_args(arguments, namespace)


def preview_parser() -> argparse.ArgumentParser:
    parser = PreviewParser(prog="agy-worker.sh transmission-preview")
    parser.add_argument("--workdir", "--worktree", required=True)
    parser.add_argument("--provider-scope")
    parser.add_argument("--provider-isolation", choices=("session", "native"), default="session")
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--task")
    parser.add_argument("--workflow", choices=("legacy", "explore", "task", "project"), default="legacy")
    parser.add_argument("--mode", choices=("plan", "accept-edits"))
    parser.add_argument("--max-cycles", type=int)
    for flag in ("model", "effort", "idle-timeout", "hard-timeout", "max-runtime", "notice-interval"):
        parser.add_argument(f"--{flag}")
    parser.add_argument("--allow-scoped-repair", action="store_true")
    parser.add_argument("--self-verification-manifest")
    parser.add_argument("--provider-env", action="append", default=[])
    parser.add_argument("--add-dir", action="append", default=[])
    parser.add_argument("--allow-slash-commands", action="store_true")
    parser.add_argument("--provider-schema")
    parser.add_argument("--base-commit")
    return parser


def preview_authority(result: dict[str, Any], args: argparse.Namespace,
                      task_raw: bytes, *, use_environment: bool = True) -> tuple[dict[str, Any], str]:
    import agy_dispatch_verification as verification
    import candidate_state
    import model_selection
    environment_values = os.environ if use_environment else {}
    if environment_values.get("AGY_WORKER_TIER"):
        raise LaunchAuthorityError("AGY_WORKER_TIER is retired; use --model / AGY_WORKER_MODEL")

    task, task_text = normalize_task(task_raw)
    workflow = args.workflow
    expected_mode = "plan" if workflow in {"legacy", "explore"} else "accept-edits"
    mode = args.mode or environment_values.get("AGY_WORKER_MODE") or expected_mode
    if workflow in {"explore", "project"} and mode != expected_mode:
        raise LaunchAuthorityError("mode conflicts with workflow")
    maximum_cycles = 5 if workflow == "project" else 1 if workflow == "legacy" else 2
    cycles = args.max_cycles if args.max_cycles is not None else maximum_cycles
    if not 1 <= cycles <= maximum_cycles:
        raise LaunchAuthorityError("max_cycles is invalid")
    selectors: dict[str, str | None] = {}
    for name in ("model", "effort"):
        explicit = getattr(args, name)
        environment = environment_values.get(f"AGY_WORKER_{name.upper()}")
        if explicit is not None and environment is not None:
            raise LaunchAuthorityError(f"{name} has conflicting sources")
        selectors[name] = explicit if explicit is not None else environment
    model, effort = selectors["model"], selectors["effort"]
    if effort is not None and model is None:
        raise LaunchAuthorityError("effort requires model")
    if any(value is not None and (not value or value.strip() != value or "\0" in value)
           for value in (model, effort)):
        raise LaunchAuthorityError("model selector is invalid")
    timeouts = {}
    for field, option, environment, default in (
        ("idle_seconds", "idle_timeout", "AGY_WORKER_IDLE_TIMEOUT", "10m"),
        ("hard_seconds", "hard_timeout", "AGY_WORKER_HARD_TIMEOUT", "2h"),
        ("max_seconds", "max_runtime", "AGY_WORKER_MAX_RUNTIME", "12h"),
        ("notice_seconds", "notice_interval", "AGY_WORKER_NOTICE_INTERVAL", "30m"),
    ):
        fallback = environment_values.get(environment, default)
        if field == "hard_seconds" and "AGY_WORKER_TIMEOUT" in environment_values:
            fallback = environment_values["AGY_WORKER_TIMEOUT"]
        timeouts[field] = duration(getattr(args, option) or fallback)
    if not timeouts["idle_seconds"] <= timeouts["hard_seconds"] <= timeouts["max_seconds"]:
        raise LaunchAuthorityError("timeout ordering is invalid")
    manifest_sha = None
    block = ""
    if args.self_verification_manifest:
        path = Path(args.self_verification_manifest)
        if Path(args.workdir) in path.parents:
            raise LaunchAuthorityError("verification manifest must be outside worktree")
        raw = read_bound_file(path, verification.MAX_MANIFEST_BYTES, private=True,
                              label="verification manifest")
        manifest = verification.parse_manifest(raw)
        verification.validate_runtime(manifest, Path(args.workdir))
        manifest_sha = sha256(raw)
        block = verification_request_block(
            [check.identifier for check in manifest.checks if check.required],
            [check.identifier for check in manifest.checks if not check.required])
    if (args.allow_scoped_repair and (not args.provider_scope or workflow not in {"task", "project"}
                                     or cycles < 2)):
        raise LaunchAuthorityError("allow_scoped_repair is unavailable")
    if manifest_sha is not None and workflow not in {"task", "project"}:
        raise LaunchAuthorityError("self-verification is unavailable")
    schema = Path(args.provider_schema or environment_values.get("AGY_WORKER_SCHEMA") or
                  Path(__file__).resolve().parent.parent / "schemas/worker-result.provider.schema.json")
    schema_raw = read_bound_file(schema, 512 * 1024, private=False, label="provider schema")
    add_dirs = []
    root = Path(args.workdir).resolve()
    for directory in args.add_dir:
        path = Path(directory).resolve(strict=True)
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise LaunchAuthorityError("additional directory is outside worktree") from exc
        if not path.is_dir() or args.provider_scope:
            raise LaunchAuthorityError("additional directory is invalid")
        add_dirs.append(relative)
    names = sorted(args.provider_env)
    if len(names) > 64 or len(set(names)) != len(names) or any(
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name) is None for name in names):
        raise LaunchAuthorityError("provider environment names are invalid")
    try:
        model_selection.validate_child_environment_names(names)
    except model_selection.EvidenceUnavailable as exc:
        raise LaunchAuthorityError("provider environment names are invalid") from exc
    content = {key: result.get(key) for key in (
        "manifest_sha256", "policy_sha256", "selected_content_sha256",
        "content_manifest_sha256", "provider_isolation", "native_grant_profile")}
    base_commit = None
    if not args.provider_scope:
        try:
            base_commit = candidate_state._git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
        except (candidate_state.CandidateStateError, UnicodeError) as exc:
            if args.base_commit is not None or workflow in {"task", "project"}:
                raise LaunchAuthorityError("base commit is unavailable") from exc
        if args.base_commit is not None and args.base_commit != base_commit:
            raise LaunchAuthorityError("base commit differs from HEAD")
    elif args.base_commit is not None:
        raise LaunchAuthorityError("scoped launch cannot bind a Git base")
    prompt = full_prompt(task, mode=mode, provider_isolation=args.provider_isolation,
                         verification_block=block)
    authority = build_authority(
        content=content, task=task, prompt=prompt, workflow=workflow, mode=mode,
        max_cycles=cycles, **timeouts, model=model, effort=effort,
        allow_scoped_repair=args.allow_scoped_repair,
        self_verification_manifest_sha256=manifest_sha, provider_env_names=names,
        allow_slash_commands=args.allow_slash_commands and mode == "accept-edits", add_dirs=sorted(set(add_dirs)),
        provider_schema_sha256=sha256(schema_raw), base_commit=base_commit, workdir=str(root))
    return authority, task_text


def main(argv: list[str]) -> int:
    if len(argv) == 4 and argv[0] == "match-record":
        try:
            expected = approval_record(Path(argv[1]), argv[2])
            raw = read_bound_file(Path(argv[3]), 32 * 1024 * 1024, private=True,
                                  label="current launch preview")
            actual = json.loads(raw)["launch_authority"]
            field = changed_field(expected, actual)
            if field:
                raise LaunchAuthorityError(f"launch authority changed: {field}")
            if approval_sha256(actual) != argv[2]:
                raise LaunchAuthorityError("launch approval digest changed")
        except (LaunchAuthorityError, KeyError, json.JSONDecodeError) as exc:
            print(f"agy-worker.sh: {exc}", file=sys.stderr)
            return 64
        return 0
    if len(argv) == 3 and argv[0] == "check-record":
        try:
            approval_record(Path(argv[1]), argv[2])
        except LaunchAuthorityError as exc:
            print(f"agy-worker.sh: {exc}", file=sys.stderr)
            return 64
        return 0
    if len(argv) == 2 and argv[0] == "stage-instruction":
        if not argv[1].startswith("/") or "\0" in argv[1]:
            return 64
        sys.stdout.write(STAGED_INSTRUCTION.format(stage_file=argv[1]))
        return 0
    if len(argv) != 4 or argv[0] != "render":
        return 64
    try:
        task, _text = normalize_task(sys.stdin.buffer.read(MAX_TASK_BYTES + 1))
        prompt = full_prompt(task, mode=argv[1], provider_isolation=argv[2],
                             verification_block=argv[3])
    except LaunchAuthorityError:
        return 64
    sys.stdout.buffer.write(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
