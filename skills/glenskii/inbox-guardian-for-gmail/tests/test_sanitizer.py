import pytest
from guardian_sanitizer import (
    is_valid_domain,
    is_valid_email,
    sanitize_query_token,
    extract_clean_address_and_domain
)

def test_valid_domains():
    assert is_valid_domain("google.com") is True
    assert is_valid_domain("sub.example.co.uk") is True
    assert is_valid_domain("@glenegrant.com") is True
    assert is_valid_domain("mailmindz.app") is True
    assert is_valid_domain("invalid_domain") is False
    assert is_valid_domain("http://google.com") is False
    assert is_valid_domain("") is False
    assert is_valid_domain("a"*260 + ".com") is False

def test_valid_emails():
    assert is_valid_email("user@example.com") is True
    assert is_valid_email("first.last+tag@sub.domain.org") is True
    assert is_valid_email("invalid-email") is False
    assert is_valid_email("@domain.com") is False
    assert is_valid_email("") is False

def test_sanitize_query_token():
    assert sanitize_query_token('from:"spammer.com"') == 'from: spammer.com'
    assert sanitize_query_token('malicious\r\nquery;--') == 'malicious query;--'
    assert sanitize_query_token('valid_domain.com') == 'valid_domain.com'

def test_extract_clean_address_and_domain():
    name, addr, dom = extract_clean_address_and_domain('"John Doe" <john.doe@company.com>')
    assert name == "John Doe"
    assert addr == "john.doe@company.com"
    assert dom == "company.com"

    name, addr, dom = extract_clean_address_and_domain('spammer@bad.biz')
    assert addr == "spammer@bad.biz"
    assert dom == "bad.biz"

    name, addr, dom = extract_clean_address_and_domain('')
    assert name == ""
    assert addr == ""
    assert dom == ""
