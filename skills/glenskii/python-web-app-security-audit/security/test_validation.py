# ============================================================
# test_validation.py  -  Input boundary validation and hostile string rejection
#
# Prevents: XSS via stored/reflected input, SQL injection,
# null byte injection, type confusion attacks, oversized payload DoS,
# unexpected field acceptance (mass assignment surface).
#
# OWASP: A03 Injection, A08 Software and Data Integrity Failures
# ============================================================

import os
import pytest
from conftest import route

LOGIN = route("TEST_AUTH_LOGIN_ROUTE", "/auth/login")
REGISTER = route("TEST_AUTH_REGISTER_ROUTE", "/auth/register")

pytestmark = pytest.mark.active_probe


# ── XSS payload rejection ─────────────────────────────────────────────────────

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
    "'\"><script>alert(document.cookie)</script>",
    "<iframe src='javascript:alert(1)'>",
    "{{7*7}}",                          # Template injection probe
    "${7*7}",                           # Expression injection probe
    "<%=7*7%>",                         # Server-side template injection
]

@pytest.mark.asyncio
@pytest.mark.parametrize("payload", XSS_PAYLOADS)
async def test_xss_payload_rejected_in_login(client, payload):
    """
    XSS payloads in login fields must not return 200.
    Reflected XSS via login error messages is a common application failure.
    """
    res = await client.post(LOGIN, json={
        "username": payload,
        "password": payload
    })
    assert res.status_code != 200 or payload not in res.text, (
        f"XSS payload reflected in response: {payload}"
    )


# ── SQL injection probes ───────────────────────────────────────────────────────

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "admin'--",
    "' UNION SELECT 1,2,3--",
    "' OR EXISTS(SELECT 1)--",
    "1; SELECT * FROM users",
    "' AND SLEEP(5)--",
]

@pytest.mark.asyncio
@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
async def test_sqli_payload_rejected_in_login(client, payload):
    """
    SQL injection payloads must not authenticate the attacker.
    Classic ' OR '1'='1 bypasses apps that build queries with string concatenation.
    Generated ORM code is usually safe, but raw query fallbacks are not.
    """
    res = await client.post(LOGIN, json={
        "username": payload,
        "password": payload
    })
    # Must not return 200 with a token
    assert res.status_code != 200 or "access_token" not in res.text, (
        f"SQLi payload may have succeeded: {payload}  -  status {res.status_code}"
    )


# ── Null byte injection ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_null_byte_in_username_rejected(client):
    """
    Null bytes can truncate strings in C-backed libraries or filesystem ops.
    "admin\x00" may match "admin" in some implementations.
    """
    res = await client.post(LOGIN, json={
        "username": "admin\x00injected",
        "password": "password"
    })
    assert res.status_code in (400, 401, 422)


# ── Type coercion attacks ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_integer_username_rejected(client):
    """
    Type confusion: integer username may bypass string validation
    or match unexpected records in loosely-typed backends.
    """
    res = await client.post(LOGIN, json={"username": 12345, "password": "pass"})
    assert res.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_array_username_rejected(client):
    """
    Array injection: some parsers accept arrays where strings are expected,
    enabling NoSQL injection or parameter pollution.
    """
    res = await client.post(LOGIN, json={
        "username": ["admin", "user"],
        "password": "pass"
    })
    assert res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_object_username_rejected(client):
    """
    Object injection: MongoDB $ne operator via JSON object bypasses auth
    in apps that pass request body directly to query layer.
    """
    res = await client.post(LOGIN, json={
        "username": {"$ne": ""},
        "password": {"$ne": ""}
    })
    assert res.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_boolean_username_rejected(client):
    """
    Boolean true as username must not match any account.
    """
    res = await client.post(LOGIN, json={"username": True, "password": True})
    assert res.status_code in (400, 401, 422)


# ── Empty and missing field handling ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_empty_body_rejected(client):
    """Empty JSON body must return 400/422  -  not 500 (unhandled exception)."""
    res = await client.post(
        LOGIN,
        content="{}",
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_missing_required_fields_rejected(client):
    """Partial payload (username only, no password) must be rejected."""
    res = await client.post(LOGIN, json={"username": "test"})
    assert res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_whitespace_only_credentials_rejected(client):
    """
    Whitespace-only strings must not pass validation.
    Trimming must happen before comparison, not after storage.
    """
    res = await client.post(LOGIN, json={"username": "   ", "password": "   "})
    assert res.status_code in (400, 401, 422)


# ── Oversized payload DoS protection ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_oversized_username_rejected(client):
    """
    10,000 character username must be rejected.
    Unbounded input acceptance enables memory exhaustion and regex DoS.
    """
    res = await client.post(LOGIN, json={
        "username": "A" * 10000,
        "password": "password"
    })
    assert res.status_code in (400, 413, 422)


@pytest.mark.asyncio
async def test_oversized_body_rejected(client):
    """
    10MB body must be rejected at the framework level.
    No app should accept arbitrarily large request bodies without validation.
    """
    large_body = "X" * (10 * 1024 * 1024)  # 10 MB
    res = await client.post(
        LOGIN,
        content=large_body,
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code in (400, 413, 422)


# ── Content-Type enforcement ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_wrong_content_type_rejected(client):
    """
    JSON endpoints must reject non-JSON content types.
    Accepting text/plain or form data can bypass JSON validation.
    """
    res = await client.post(
        LOGIN,
        content="username=admin&password=admin",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res.status_code in (400, 415, 422)


@pytest.mark.asyncio
async def test_malformed_json_rejected(client):
    """
    Malformed JSON must return 400  -  not 500.
    500 on bad JSON indicates unhandled exception, which may leak stack info.
    """
    res = await client.post(
        LOGIN,
        content="{username: admin, password: }",
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code in (400, 422), (
        f"Malformed JSON returned {res.status_code}  -  may indicate unhandled exception"
    )


# ── Unexpected field handling (mass assignment surface) ───────────────────────

@pytest.mark.asyncio
async def test_extra_fields_not_stored_or_reflected(client):
    """
    Extra fields in request body must be ignored  -  not stored or reflected.
    Mass assignment vulnerability: attacker injects is_admin, role, credits, etc.
    """
    res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
        "is_admin": True,
        "role": "superuser",
        "__proto__": {"admin": True},    # Prototype pollution probe
        "constructor": {"admin": True}
    })

    # If login succeeds, verify injected fields are not in the response
    if res.status_code == 200:
        body = res.json()
        assert body.get("is_admin") is not True
        assert body.get("role") != "superuser"
