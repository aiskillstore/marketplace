"""Validate public-package claims that can otherwise drift from the code."""

from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


def test_private_mailbox_artifacts_are_ignored():
    ignored = (SKILL_DIR / ".gitignore").read_text(encoding="utf-8")
    for filename in (
        "credentials.json",
        "token.json",
        "config.json",
        "guardian.log",
        "guardian_stats.json",
        "sender_reputation.db",
        "guardian_review_*.json",
        "guardian_unsubscribe_review_*.json",
        "dashboard.html",
    ):
        assert filename in ignored


def test_docs_do_not_advertise_unsupported_scheduler_commands():
    readme = (SKILL_DIR / "README.md").read_text(encoding="utf-8")
    assert "--install-scheduler" not in readme
    assert "--uninstall-scheduler" not in readme
