import pytest
from unittest.mock import MagicMock
from guardian import GuardianEngine, normalize_text

@pytest.fixture
def mock_engine():
    mock_service = MagicMock()
    mock_service.users().labels().list().execute.return_value = {"labels": []}
    engine = GuardianEngine(service=mock_service)
    engine.config = {
        "whitelist_domains": ["trusted.com", "mybusiness.org"],
        "whitelist_emails": ["partner@special.com"],
        "blocklist_domains": ["evil-spammer.com"],
        "blocklist_senders": ["blocked-person@generic.com"],
        "suspicious_sender_tlds": [".biz", ".web.id", ".my.id"],
        "quarantine_keywords": ["last reminder", "account is locked", "crypto", "viruses found"]
    }
    return engine

def test_unicode_normalization():
    styled_math_bold = "𝐥𝐚𝐬𝐭 𝐫𝐞𝐦𝐢𝐧𝐝𝐞𝐫"
    assert normalize_text(styled_math_bold) == "last reminder"
    
    italic_text = "𝘊𝘭𝘰𝘶𝘥 𝘈𝘤𝘤𝘰𝘶𝘯𝘵 𝘓𝘰𝘤𝘬𝘦𝘥"
    assert normalize_text(italic_text) == "cloud account locked"

def test_starred_and_sent_precedence(mock_engine):
    headers = {"from": "spammer@evil-spammer.com", "subject": "crypto viruses found"}
    
    verdict, reason = mock_engine.classify_message(headers, labels=["STARRED"])
    assert verdict == "SAFE"
    assert "Starred" in reason

    verdict, reason = mock_engine.classify_message(headers, labels=["SENT"])
    assert verdict == "SAFE"
    assert "Sent" in reason

def test_whitelist_beats_spam_keywords(mock_engine):
    # Legitimate partner talking about crypto / security warnings
    headers = {
        "from": "CEO <partner@special.com>",
        "return-path": "<partner@special.com>",
        "authentication-results": "mx.google.com; dmarc=pass header.from=special.com",
        "subject": "Urgent: Account is locked and crypto review"
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "SAFE"
    assert "Whitelisted" in reason

def test_whitelist_domain_beats_suspicious_tlds(mock_engine):
    headers = {
        "from": "Support <support@mybusiness.org>",
        "return-path": "<bounces@mybusiness.org>",
        "authentication-results": "mx.google.com; dmarc=pass header.from=mybusiness.org",
        "subject": "System Status Update"
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "SAFE"

def test_spoofed_allowlisted_header_is_not_trusted(mock_engine):
    headers = {
        "from": "CEO <partner@special.com>",
        "return-path": "<relay@hostile.example>",
        "authentication-results": "mx.google.com; dmarc=fail header.from=special.com",
        "subject": "Account is locked",
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "QUARANTINE_KEYWORD"
    assert "Whitelisted" not in reason

def test_blocklist_triggers_quarantine(mock_engine):
    headers = {
        "from": "Marketing <sales@evil-spammer.com>",
        "return-path": "<sales@evil-spammer.com>",
        "subject": "Friendly follow up"
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "QUARANTINE_BLOCKLIST"

def test_keyword_triggers_quarantine(mock_engine):
    headers = {
        "from": "Unknown <random@untrusted.net>",
        "return-path": "<random@untrusted.net>",
        "subject": "⚠️ Final warning: Your account is locked today!"
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "QUARANTINE_KEYWORD"

def test_tld_triggers_quarantine(mock_engine):
    headers = {
        "from": "Spoofed User <relay@dynamic-server.my.id>",
        "return-path": "<relay@dynamic-server.my.id>",
        "subject": "Hello there"
    }
    verdict, reason = mock_engine.classify_message(headers, labels=["INBOX"])
    assert verdict == "QUARANTINE_TLD"
