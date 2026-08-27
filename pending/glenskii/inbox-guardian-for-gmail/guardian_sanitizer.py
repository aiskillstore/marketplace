import re
from email.utils import parseaddr

DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$'
)

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
)

def is_valid_domain(domain: str) -> bool:
    """Validates whether a domain string is syntactically valid."""
    if not domain or len(domain) > 253:
        return False
    domain = domain.strip().lower().lstrip('@.')
    return bool(DOMAIN_REGEX.match(domain))

def is_valid_email(email: str) -> bool:
    """Validates whether an email string is syntactically valid."""
    if not email or len(email) > 254:
        return False
    email = email.strip().lower()
    return bool(EMAIL_REGEX.match(email))

def sanitize_query_token(text: str) -> str:
    """
    Sanitizes user input before embedding in a Gmail search query.
    Removes quotes, control characters, and special Gmail query operators.
    """
    if not text:
        return ""
    # Strip dangerous characters that could alter query syntax
    sanitized = re.sub(r'[\r\n\t"\'\\(){}\[\]]', ' ', text)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

def extract_clean_address_and_domain(raw_header: str):
    """
    Safely parses an RFC 2822 header (e.g. From or Return-Path).
    Returns (display_name, clean_email, clean_domain).
    """
    if not raw_header:
        return "", "", ""
    name, addr = parseaddr(raw_header)
    addr = addr.strip().lower()
    domain = addr.split('@')[-1] if '@' in addr else ''
    return name.strip(), addr, domain.strip()
