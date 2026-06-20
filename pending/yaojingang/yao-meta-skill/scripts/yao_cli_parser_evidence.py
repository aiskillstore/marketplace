#!/usr/bin/env python3
"""Evidence command declarations for the Yao CLI parser."""

import argparse
from collections.abc import Callable


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by yao_cli_parser.py to keep evidence command declarations out of the main parser module."


def _handler(command_handlers: dict[str, Callable[[argparse.Namespace], int]], name: str) -> Callable[[argparse.Namespace], int]:
    if name not in command_handlers:
        raise KeyError(f"Missing CLI command handler: {name}")
    return command_handlers[name]


def add_evidence_commands(
    subparsers: argparse._SubParsersAction,
    command_handlers: dict[str, Callable[[argparse.Namespace], int]],
) -> None:
    world_class_evidence_cmd = subparsers.add_parser(
        "world-class-evidence",
        help="Render the evidence collection plan for remaining world-class readiness gaps.",
    )
    world_class_evidence_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_evidence_cmd.add_argument("--output-json")
    world_class_evidence_cmd.add_argument("--output-md")
    world_class_evidence_cmd.add_argument("--generated-at")
    world_class_evidence_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_evidence"))

    world_class_ledger_cmd = subparsers.add_parser(
        "world-class-ledger",
        help="Render the machine-checkable ledger for world-class evidence gaps.",
    )
    world_class_ledger_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_ledger_cmd.add_argument("--output-json")
    world_class_ledger_cmd.add_argument("--output-md")
    world_class_ledger_cmd.add_argument("--submissions-dir")
    world_class_ledger_cmd.add_argument("--generated-at")
    world_class_ledger_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_ledger"))

    world_class_intake_cmd = subparsers.add_parser(
        "world-class-intake",
        help="Validate world-class human and external evidence intake packets.",
    )
    world_class_intake_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_intake_cmd.add_argument("--submissions-dir")
    world_class_intake_cmd.add_argument("--output-json")
    world_class_intake_cmd.add_argument("--output-md")
    world_class_intake_cmd.add_argument("--generated-at")
    world_class_intake_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_intake"))

    world_class_preflight_cmd = subparsers.add_parser(
        "world-class-preflight",
        help="Render operator preflight checks for collecting pending world-class evidence.",
    )
    world_class_preflight_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_preflight_cmd.add_argument("--submissions-dir")
    world_class_preflight_cmd.add_argument("--output-json")
    world_class_preflight_cmd.add_argument("--output-md")
    world_class_preflight_cmd.add_argument("--output-html")
    world_class_preflight_cmd.add_argument("--generated-at")
    world_class_preflight_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_preflight"))

    world_class_submission_kit_cmd = subparsers.add_parser(
        "world-class-submission-kit",
        help="Prepare editable world-class evidence submission drafts.",
    )
    world_class_submission_kit_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_submission_kit_cmd.add_argument("--output-dir")
    world_class_submission_kit_cmd.add_argument("--evidence-key", action="append", default=[])
    world_class_submission_kit_cmd.add_argument("--overwrite", action="store_true")
    world_class_submission_kit_cmd.add_argument(
        "--prefill-artifacts",
        action="store_true",
        help="Insert SHA-256 digests for currently available aggregate artifacts while keeping drafts template-only.",
    )
    world_class_submission_kit_cmd.add_argument("--generated-at")
    world_class_submission_kit_cmd.add_argument("--output-html")
    world_class_submission_kit_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_submission_kit"))

    world_class_submission_review_cmd = subparsers.add_parser(
        "world-class-submission-review",
        help="Render a read-only review queue for world-class evidence submissions.",
    )
    world_class_submission_review_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_submission_review_cmd.add_argument("--submissions-dir")
    world_class_submission_review_cmd.add_argument("--output-json")
    world_class_submission_review_cmd.add_argument("--output-md")
    world_class_submission_review_cmd.add_argument("--generated-at")
    world_class_submission_review_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_submission_review"))

    world_class_runbook_cmd = subparsers.add_parser(
        "world-class-runbook",
        help="Render an operator runbook for pending world-class evidence.",
    )
    world_class_runbook_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_runbook_cmd.add_argument("--submissions-dir")
    world_class_runbook_cmd.add_argument("--output-json")
    world_class_runbook_cmd.add_argument("--output-md")
    world_class_runbook_cmd.add_argument("--output-html")
    world_class_runbook_cmd.add_argument("--generated-at")
    world_class_runbook_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_runbook"))

    world_class_claim_guard_cmd = subparsers.add_parser(
        "world-class-claim-guard",
        help="Scan public claim surfaces for premature world-class completion claims.",
    )
    world_class_claim_guard_cmd.add_argument("skill_dir", nargs="?", default=".")
    world_class_claim_guard_cmd.add_argument("--claim-surface", action="append", default=[])
    world_class_claim_guard_cmd.add_argument("--output-json")
    world_class_claim_guard_cmd.add_argument("--output-md")
    world_class_claim_guard_cmd.add_argument("--generated-at")
    world_class_claim_guard_cmd.set_defaults(func=_handler(command_handlers, "command_world_class_claim_guard"))

    benchmark_reproducibility_cmd = subparsers.add_parser(
        "benchmark-reproducibility",
        help="Render benchmark methodology, artifact, failure-disclosure, and reproduction-command evidence.",
    )
    benchmark_reproducibility_cmd.add_argument("skill_dir", nargs="?", default=".")
    benchmark_reproducibility_cmd.add_argument("--output-json")
    benchmark_reproducibility_cmd.add_argument("--output-md")
    benchmark_reproducibility_cmd.add_argument("--generated-at")
    benchmark_reproducibility_cmd.set_defaults(func=_handler(command_handlers, "command_benchmark_reproducibility"))

    evidence_consistency_cmd = subparsers.add_parser(
        "evidence-consistency",
        help="Render cross-report evidence consistency checks.",
    )
    evidence_consistency_cmd.add_argument("skill_dir", nargs="?", default=".")
    evidence_consistency_cmd.add_argument("--output-json")
    evidence_consistency_cmd.add_argument("--output-md")
    evidence_consistency_cmd.add_argument("--generated-at")
    evidence_consistency_cmd.set_defaults(func=_handler(command_handlers, "command_evidence_consistency"))
