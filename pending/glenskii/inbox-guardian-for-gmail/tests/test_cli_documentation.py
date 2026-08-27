"""Keep the public skill command examples aligned with guardian.py."""

from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


def test_skill_instructions_use_supported_cli_flags():
    expected = {
        "--execute",
        "--setup",
        "--review-file",
        "--trash",
        "--review-unsub",
    }
    unsupported = {
        "--sweep",
        "--action",
        "--stop-cold",
        "--confirm-permanent-delete",
        "--hard-delete",
        "--confirm-destructive",
    }

    for flag in expected:
        assert flag in SKILL_TEXT
    for flag in unsupported:
        assert flag not in SKILL_TEXT
