import datetime
import json

import pytest
from unittest.mock import MagicMock
import guardian
from guardian import GuardianEngine

@pytest.fixture
def mock_service():
    service = MagicMock()
    # Labels list returns existing label
    service.users().labels().list().execute.return_value = {
        "labels": [{"id": "Label_123", "name": "Guardian/Quarantine"}]
    }
    return service

def test_default_quarantine_action(mock_service):
    engine = GuardianEngine(service=mock_service)
    
    result = engine.execute_quarantine("msg_001", move_to_trash=False)
    assert result == "quarantined"
    
    # Ensure modify was called with addLabelIds and removeLabelIds
    mock_service.users().messages().modify.assert_called_with(
        userId='me',
        id='msg_001',
        body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['Label_123']}
    )

def test_move_to_trash_action(mock_service):
    engine = GuardianEngine(service=mock_service)
    
    result = engine.execute_quarantine("msg_002", move_to_trash=True)
    assert result == "trashed"
    mock_service.users().messages().trash.assert_called_with(userId='me', id='msg_002')

def test_permanent_delete_is_not_an_available_action(mock_service):
    engine = GuardianEngine(service=mock_service)

    with pytest.raises(TypeError):
        engine.execute_quarantine("msg_003", hard_delete=True)
    mock_service.users().messages().delete.assert_not_called()

def test_pagination_and_error_handling(mock_service):
    # Simulate page 1 with nextPageToken and page 2
    mock_service.users().messages().list().execute.side_effect = [
        {"messages": [{"id": "m1"}, {"id": "m2"}], "nextPageToken": "token_page_2"},
        {"messages": [{"id": "m3"}]}
    ]
    mock_service.users().messages().get().execute.side_effect = [
        {"id": "m1", "payload": {"headers": []}},
        {"id": "m2", "payload": {"headers": []}},
        {"id": "m3", "payload": {"headers": []}}
    ]

    engine = GuardianEngine(service=mock_service)
    results = engine.fetch_messages_paginated(max_results=3)
    assert len(results) == 3


def _write_signed_review(tmp_path, records, monkeypatch):
    monkeypatch.setattr(guardian, "SCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(guardian, "REVIEW_KEY_FILE", str(tmp_path / "guardian_review.key"))
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "schema_version": 1,
        "created_at": now.isoformat(),
        "expires_at": (now + datetime.timedelta(hours=1)).isoformat(),
        "records": records,
    }
    document = {
        **payload,
        "integrity": {"algorithm": "HMAC-SHA256", "signature": guardian._review_signature(payload)},
    }
    path = tmp_path / "guardian_review_test.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_signed_review_rechecks_current_message_before_action(mock_service, tmp_path, monkeypatch):
    engine = GuardianEngine(service=mock_service)
    engine.config = {"quarantine_keywords": ["blocked"], "quarantine_label_name": "Guardian/Quarantine"}
    path = _write_signed_review(tmp_path, [{"id": "msg_004", "proposed_action": "QUARANTINE"}], monkeypatch)
    mock_service.users().messages().get().execute.return_value = {
        "id": "msg_004",
        "labelIds": ["INBOX"],
        "payload": {"headers": [
            {"name": "From", "value": "hostile@example.test"},
            {"name": "Subject", "value": "blocked account"},
        ]},
    }

    engine.execute_from_review_file(str(path))

    mock_service.users().messages().modify.assert_called()


def test_tampered_review_is_rejected_before_mailbox_action(mock_service, tmp_path, monkeypatch):
    engine = GuardianEngine(service=mock_service)
    path = _write_signed_review(tmp_path, [{"id": "msg_005", "proposed_action": "QUARANTINE"}], monkeypatch)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["records"][0]["id"] = "other_message"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="integrity"):
        engine.execute_from_review_file(str(path))
    mock_service.users().messages().modify.assert_not_called()
