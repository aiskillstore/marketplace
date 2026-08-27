from unittest.mock import MagicMock

import guardian
from guardian import GuardianEngine


def _learning_config():
    return {
        "whitelist_domains": [],
        "blocklist_domains": [],
        "learned_domain_candidates": {},
    }


def test_learning_does_not_promote_a_shared_relay(monkeypatch):
    config = _learning_config()
    monkeypatch.setattr(guardian, "load_config", lambda: config)
    monkeypatch.setattr(guardian, "save_config", lambda value: None)

    learned = guardian.learn_confirmed_sender_domain(
        "Newsletter <news@publisher.example>",
        "<bounce@shared-relay.example>",
    )

    assert learned is None
    assert config["blocklist_domains"] == []
    assert config["learned_domain_candidates"] == {}


def test_learning_promotes_an_aligned_sender_after_repeated_review(monkeypatch):
    config = _learning_config()
    monkeypatch.setattr(guardian, "load_config", lambda: config)
    monkeypatch.setattr(guardian, "save_config", lambda value: None)

    first = guardian.learn_confirmed_sender_domain(
        "Spam <alerts@rogue.example>",
        "<alerts@rogue.example>",
    )
    second = guardian.learn_confirmed_sender_domain(
        "Spam <alerts@rogue.example>",
        "<alerts@rogue.example>",
    )

    assert first is None
    assert second == "rogue.example"
    assert config["blocklist_domains"] == ["rogue.example"]
    assert config["learned_domain_candidates"] == {}


def test_audit_review_record_omits_mail_previews(monkeypatch):
    engine = GuardianEngine(service=MagicMock())
    engine.fetch_messages_paginated = lambda **kwargs: [{
        "id": "msg_01",
        "labelIds": ["INBOX"],
        "payload": {"headers": [
            {"name": "From", "value": "Spam <offers@rogue.example>"},
            {"name": "Return-Path", "value": "<offers@rogue.example>"},
            {"name": "Subject", "value": "Very private subject"},
        ]},
    }]
    engine.classify_message = lambda headers, labels: ("QUARANTINE_KEYWORD", "keyword")

    records = engine.run_audit(output_review_file=False)

    assert records == [{
        "id": "msg_01",
        "classification": "QUARANTINE_KEYWORD",
        "reason": "keyword",
        "proposed_action": "QUARANTINE",
    }]


def test_review_execution_requires_exact_owner_confirmation(monkeypatch, tmp_path):
    review_file = tmp_path / "guardian_review_20260827_000000.json"
    monkeypatch.setattr("builtins.input", lambda prompt: "QUARANTINE guardian_review_20260827_000000.json")
    assert guardian.confirm_review_execution(review_file) is True

    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    assert guardian.confirm_review_execution(review_file) is False
