import pytest
from unittest.mock import MagicMock
from guardian import GuardianEngine
from googleapiclient.errors import HttpError

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
    
    result = engine.execute_quarantine("msg_001", move_to_trash=False, hard_delete=False)
    assert result == "quarantined"
    
    # Ensure modify was called with addLabelIds and removeLabelIds
    mock_service.users().messages().modify.assert_called_with(
        userId='me',
        id='msg_001',
        body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['Label_123']}
    )

def test_move_to_trash_action(mock_service):
    engine = GuardianEngine(service=mock_service)
    
    result = engine.execute_quarantine("msg_002", move_to_trash=True, hard_delete=False)
    assert result == "trashed"
    mock_service.users().messages().trash.assert_called_with(userId='me', id='msg_002')

def test_hard_delete_action(mock_service):
    engine = GuardianEngine(service=mock_service)
    
    result = engine.execute_quarantine("msg_003", move_to_trash=False, hard_delete=True)
    assert result == "hard_deleted"
    mock_service.users().messages().delete.assert_called_with(userId='me', id='msg_003')

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
