#!/usr/bin/env python3
"""Render a compact human report from one validated Evidence Receipt v1.

The stdout-only ``main(argv)`` path returns normally. File-output ``main(argv)``
is process-owning: it keeps signal rollback authority through ``os._exit(0)``.
Invoke file-output mode as a command/subprocess; do not embed it in a host process.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import signal
import stat
import sys
from typing import Any, NoReturn

sys.dont_write_bytecode = True
SCRIPTS_ROOT = str(Path(__file__).resolve(strict=True).parent)
if SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, SCRIPTS_ROOT)

from evidence_receipt import (  # noqa: E402
    ValidationFailure,
    load_schema,
    parse_json_bytes,
    published_bytes,
    read_real_file,
    require_sha,
    sha256_bytes,
    validate_receipt,
)
from recommendation_record import (  # noqa: E402
    RecommendationRecordError,
    validate_recommendation_record,
)


MAX_REPORT_BYTES = 64 * 1024
SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
REPORT_FORMATS = ("text", "json", "markdown", "github-step-summary")


class UsageFailure(ValueError):
    pass


class PublicationFailure(ValueError):
    pass


class Interrupted(BaseException):
    def __init__(self, signal_number: int) -> None:
        self.signal_number = signal_number


class PublishedReport:
    def __init__(
        self,
        parent_fd: int,
        final_name: str,
        identity: tuple[int, int],
        prior_mask: set[signal.Signals],
    ) -> None:
        self.parent_fd = parent_fd
        self.final_name = final_name
        self.identity = identity
        self.prior_mask = prior_mask

    def rollback(self) -> None:
        _owned_unlink(self.parent_fd, self.final_name, self.identity)
        os.fsync(self.parent_fd)

    def close(self) -> None:
        if self.parent_fd >= 0:
            os.close(self.parent_fd)
            self.parent_fd = -1


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(64, "evidence-report: invalid arguments\n")


def one(parser: Parser, values: list[str] | None, flag: str, required: bool) -> str | None:
    if not values:
        if required:
            parser.error(f"{flag} is required")
        return None
    if len(values) != 1:
        parser.error(f"{flag} must be provided exactly once")
    return values[0]


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def build_report(receipt: dict[str, Any]) -> dict[str, Any]:
    """Return the bounded report representation, never the raw receipt."""
    return {
        "caller_selection_bound": "caller_selection" in receipt,
        "envelope_sha256": receipt["envelope_sha256"],
        "final_candidate_state_sha256": receipt["final_candidate_state_sha256"],
        "gate_authority": receipt["gate_authority"],
        "gate_exit": receipt["gate_exit"],
        "gate_outcome": receipt["gate_outcome"],
        "human_review_required_before_acceptance": True,
        "initial_candidate_state_sha256": receipt["initial_candidate_state_sha256"],
        "integrity": {
            "signed": False,
            "tamper_evident": False,
        },
        "kind": "agy-worker-evidence-report",
        "path_policy_sha256": receipt["path_policy_sha256"],
        "pre_dispatch_recommendation_bound": "pre_dispatch_recommendation" in receipt,
        "recommendations_participated_in_acceptance": False,
        "resolved_base": receipt["resolved_base"],
        "schema_version": 1,
        "verdict": receipt["verdict"],
        "verification_labels": [entry["label"] for entry in receipt["verifiers"]],
    }


def _safe_markdown_atom(value: str) -> str:
    if not value or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        for character in value
    ):
        raise ValidationFailure("report value is not safe for Markdown")
    return value


def _validate_rendered_payload(payload: bytes, output_format: str) -> bytes:
    if not payload or len(payload) > MAX_REPORT_BYTES:
        raise ValidationFailure("rendered report is empty or oversized")
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValidationFailure("rendered report is not ASCII") from exc
    if "\r" in text or "\x00" in text or text.startswith("::") or "\n::" in text:
        raise ValidationFailure("rendered report contains workflow-command syntax")
    if output_format in ("markdown", "github-step-summary") and any(
        marker in text for marker in ("](", "<")
    ):
        raise ValidationFailure("rendered report contains unsafe Markdown syntax")
    return payload


def render_json(receipt: dict[str, Any]) -> bytes:
    return published_bytes(build_report(receipt))


def render_text(receipt: dict[str, Any]) -> bytes:
    labels = [entry["label"] for entry in receipt["verifiers"]]
    lines = [
        "Evidence Report v1",
        f"Verdict: {receipt['verdict']}",
        f"Gate outcome: {receipt['gate_outcome']} (exit {receipt['gate_exit']})",
        f"Gate authority: {receipt['gate_authority']}",
        f"Resolved base: {receipt['resolved_base']}",
        f"Envelope SHA-256: {receipt['envelope_sha256']}",
        f"Path policy SHA-256: {receipt['path_policy_sha256']}",
        f"Initial candidate state SHA-256: {receipt['initial_candidate_state_sha256']}",
        f"Final candidate state SHA-256: {receipt['final_candidate_state_sha256']}",
        f"Verification labels ({len(labels)}): {', '.join(labels)}",
        f"Caller selection bound: {_yes('caller_selection' in receipt)}",
        f"Pre-dispatch recommendation bound: {_yes('pre_dispatch_recommendation' in receipt)}",
        "Recommendations participated in acceptance: no",
        "Integrity: unsigned and not tamper-evident",
        "Human review: required before calling a gate-passed candidate accepted.",
    ]
    return ("\n".join(lines) + "\n").encode("ascii")


def render_markdown(receipt: dict[str, Any], *, step_summary: bool = False) -> bytes:
    labels = [_safe_markdown_atom(entry["label"]) for entry in receipt["verifiers"]]
    label_text = ", ".join(f"`{label}`" for label in labels)
    heading = "# Evidence Report v1 (GitHub Step Summary)" if step_summary else "# Evidence Report v1"
    lines = [
        heading,
        "",
        f"- Verdict: `{_safe_markdown_atom(receipt['verdict'])}`",
        f"- Gate outcome: `{_safe_markdown_atom(receipt['gate_outcome'])}` (exit `{receipt['gate_exit']}`)",
        f"- Gate authority: `{_safe_markdown_atom(receipt['gate_authority'])}`",
        f"- Resolved base: `{_safe_markdown_atom(receipt['resolved_base'])}`",
        f"- Envelope SHA-256: `{_safe_markdown_atom(receipt['envelope_sha256'])}`",
        f"- Path policy SHA-256: `{_safe_markdown_atom(receipt['path_policy_sha256'])}`",
        f"- Initial candidate state SHA-256: `{_safe_markdown_atom(receipt['initial_candidate_state_sha256'])}`",
        f"- Final candidate state SHA-256: `{_safe_markdown_atom(receipt['final_candidate_state_sha256'])}`",
        f"- Verification labels ({len(labels)}): {label_text}",
        f"- Caller selection bound: **{_yes('caller_selection' in receipt)}**",
        f"- Pre-dispatch recommendation bound: **{_yes('pre_dispatch_recommendation' in receipt)}**",
        "- Recommendations participated in acceptance: **no**",
        "- Integrity: **unsigned and not tamper-evident**",
        "",
        "> Human review is required before calling a gate-passed candidate accepted.",
    ]
    return ("\n".join(lines) + "\n").encode("ascii")


def _read_bound_json(path: Path, label: str) -> Any:
    return parse_json_bytes(read_real_file(path, label), label)


def validate_bindings(
    receipt: dict[str, Any],
    *,
    envelope: str | None,
    selection: str | None,
    recommendation: str | None,
    initial_digest: str | None,
    final_digest: str | None,
) -> None:
    if envelope is not None:
        if sha256_bytes(read_real_file(Path(envelope), "bound envelope")) != receipt["envelope_sha256"]:
            raise ValidationFailure("bound envelope digest does not match receipt")
    if selection is not None:
        if _read_bound_json(Path(selection), "bound selection") != receipt.get("caller_selection"):
            raise ValidationFailure("bound selection does not match receipt")
    if recommendation is not None:
        value = _read_bound_json(Path(recommendation), "bound recommendation")
        try:
            validate_recommendation_record(value, required_stage="pre-dispatch")
        except RecommendationRecordError as exc:
            raise ValidationFailure("bound recommendation is invalid") from exc
        if value != receipt.get("pre_dispatch_recommendation"):
            raise ValidationFailure("bound recommendation does not match receipt")
    if initial_digest is not None:
        require_sha(initial_digest, "bound initial state digest")
        if initial_digest != receipt["initial_candidate_state_sha256"]:
            raise ValidationFailure("bound initial state digest does not match receipt")
    if final_digest is not None:
        require_sha(final_digest, "bound final state digest")
        if final_digest != receipt["final_candidate_state_sha256"]:
            raise ValidationFailure("bound final state digest does not match receipt")


def _canonical_parent(target: Path) -> tuple[Path, str]:
    if not target.is_absolute() or "\n" in str(target) or "\r" in str(target):
        raise UsageFailure("--output must be one canonical absolute path")
    if target.exists() or target.is_symlink():
        raise UsageFailure("--output must name a new path and never overwrites")
    parent = target.parent
    if not parent.is_dir() or parent.is_symlink():
        raise UsageFailure("--output parent must be one real directory")
    canonical = Path(os.path.realpath(parent))
    if Path(os.path.realpath(target)) != canonical / target.name or target.name in ("", ".", ".."):
        raise UsageFailure("--output path must be canonical")
    return canonical, target.name


def _owned_unlink(parent_fd: int, name: str, identity: tuple[int, int]) -> None:
    try:
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == identity:
        os.unlink(name, dir_fd=parent_fd)


def _pending_signal() -> int | None:
    if not hasattr(signal, "sigpending"):
        return None
    pending = sorted(set(signal.sigpending()).intersection(SIGNALS))
    return pending[0] if pending else None


def _restore_mask_preserving(
    prior_mask: set[signal.Signals], first_signal: int | None, *, raise_after: bool = True
) -> None:
    pending = _pending_signal()
    if first_signal is None:
        first_signal = pending
    handlers = {number: signal.getsignal(number) for number in SIGNALS}
    for number in SIGNALS:
        signal.signal(number, signal.SIG_IGN)
    signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)
    for number, handler in handlers.items():
        signal.signal(number, handler)
    if first_signal is not None and raise_after:
        raise Interrupted(first_signal)


def _completion_checkpoint() -> None:
    """Test-only callable seam; production has no environment or CLI override."""


def _before_atomic_exit_checkpoint() -> None:
    """Test-only callable seam after unmasking and before process exit."""


def _atomic_success_exit() -> NoReturn:
    os._exit(0)


def _complete_published_success(publication: PublishedReport) -> NoReturn:
    # Keep the rollback handlers and the inode-pinned parent descriptor alive until
    # the process is gone. A signal pending before this transition is delivered by
    # the unmask; a signal after it either runs the handler or loses the race to
    # process termination. There is no ignored-signal or normal-return window.
    signal.pthread_sigmask(signal.SIG_SETMASK, publication.prior_mask)
    _before_atomic_exit_checkpoint()
    _atomic_success_exit()


def publish_new(target: Path, payload: bytes) -> PublishedReport:
    prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    parent_fd = -1
    final_name = ""
    temporary = ""
    descriptor = -1
    identity: tuple[int, int] | None = None
    final_identity: tuple[int, int] | None = None
    try:
        parent, final_name = _canonical_parent(target)
        parent_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        temporary = f".{final_name}.evidence-report.{secrets.token_hex(12)}.tmp"
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        os.fchmod(descriptor, 0o600)
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise PublicationFailure("report write failed")
            view = view[written:]
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        identity = (metadata.st_dev, metadata.st_ino)
        os.close(descriptor)
        descriptor = -1
        os.link(
            temporary,
            final_name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
        final_identity = identity
        linked = os.stat(final_name, dir_fd=parent_fd, follow_symlinks=False)
        if (linked.st_dev, linked.st_ino) != identity or stat.S_IMODE(linked.st_mode) != 0o600:
            raise PublicationFailure("published report identity changed")
        os.fsync(parent_fd)
        os.unlink(temporary, dir_fd=parent_fd)
        identity = None
        os.fsync(parent_fd)
        assert final_identity is not None
        return PublishedReport(parent_fd, final_name, final_identity, prior_mask)
    except BaseException as error:
        first_signal = error.signal_number if isinstance(error, Interrupted) else None
        cleanup_failed = False
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                cleanup_failed = True
        for name, owned_identity in ((final_name, final_identity), (temporary, identity)):
            if parent_fd >= 0 and name and owned_identity is not None:
                try:
                    _owned_unlink(parent_fd, name, owned_identity)
                except OSError:
                    cleanup_failed = True
        if parent_fd >= 0:
            try:
                os.fsync(parent_fd)
            except OSError:
                cleanup_failed = True
        if parent_fd >= 0:
            os.close(parent_fd)
            parent_fd = -1
        _restore_mask_preserving(prior_mask, first_signal)
        if cleanup_failed:
            raise PublicationFailure("report cleanup failed") from error
        raise


def run(arguments: list[str]) -> PublishedReport | None:
    parser = Parser(prog="evidence-report.sh")
    parser.add_argument("--receipt", action="append")
    parser.add_argument("--format", action="append", choices=REPORT_FORMATS)
    parser.add_argument("--output", action="append")
    parser.add_argument("--envelope", action="append")
    parser.add_argument("--selection", action="append")
    parser.add_argument("--pre-recommendation", action="append")
    parser.add_argument("--initial-state-digest", action="append")
    parser.add_argument("--final-state-digest", action="append")
    parsed = parser.parse_args(arguments)
    receipt_path = one(parser, parsed.receipt, "--receipt", True)
    output_format = one(parser, parsed.format, "--format", True)
    output_path = one(parser, parsed.output, "--output", False)
    envelope = one(parser, parsed.envelope, "--envelope", False)
    selection = one(parser, parsed.selection, "--selection", False)
    recommendation = one(parser, parsed.pre_recommendation, "--pre-recommendation", False)
    initial_digest = one(parser, parsed.initial_state_digest, "--initial-state-digest", False)
    final_digest = one(parser, parsed.final_state_digest, "--final-state-digest", False)
    assert receipt_path is not None and output_format is not None
    runtime_root = Path(__file__).resolve(strict=True).parent.parent
    schema = load_schema(runtime_root / "schemas/evidence-receipt.schema.json")
    receipt = validate_receipt(
        _read_bound_json(Path(receipt_path), "receipt"),
        schema,
    )
    validate_bindings(
        receipt,
        envelope=envelope,
        selection=selection,
        recommendation=recommendation,
        initial_digest=initial_digest,
        final_digest=final_digest,
    )
    if output_format == "text":
        payload = render_text(receipt)
    elif output_format == "json":
        payload = render_json(receipt)
    else:
        payload = render_markdown(
            receipt, step_summary=output_format == "github-step-summary"
        )
    payload = _validate_rendered_payload(payload, output_format)
    if output_path is None:
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
    else:
        return publish_new(Path(output_path), payload)
    return None


def main(argv: list[str] | None = None) -> int:
    entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    previous = {number: signal.getsignal(number) for number in SIGNALS}
    disarmed = False
    publication: PublishedReport | None = None

    def interrupt(number: int, _frame: Any) -> None:
        raise Interrupted(number)

    try:
        for number in SIGNALS:
            signal.signal(number, interrupt)
        signal.pthread_sigmask(signal.SIG_SETMASK, entry_mask)
        publication = run(list(sys.argv[1:] if argv is None else argv))
        if publication is not None:
            _completion_checkpoint()
            _complete_published_success(publication)
        return 0
    except Interrupted as exc:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        restore_mask = blocked
        if publication is not None and publication.parent_fd >= 0:
            restore_mask = publication.prior_mask
            try:
                publication.rollback()
            finally:
                publication.close()
        _restore_mask_preserving(
            restore_mask, exc.signal_number, raise_after=False
        )
        print("evidence-report: interrupted", file=sys.stderr)
        return 128 + exc.signal_number
    except UsageFailure as exc:
        print(f"evidence-report: {exc}", file=sys.stderr)
        return 64
    except ValidationFailure:
        print("evidence-report: receipt or trusted binding is invalid", file=sys.stderr)
        return 1
    except (OSError, PublicationFailure):
        print("evidence-report: output publication failed", file=sys.stderr)
        return 74
    finally:
        if not disarmed:
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
            for number, handler in previous.items():
                signal.signal(number, handler)
            signal.pthread_sigmask(signal.SIG_SETMASK, entry_mask)


if __name__ == "__main__":
    raise SystemExit(main())
