# ============================================================
# test_cookies.py  -  Cookie security flag enforcement
#
# Prevents: session hijacking via XSS (HttpOnly),
# session theft over HTTP (Secure), CSRF via cross-site requests (SameSite).
#
# OWASP: A02 Cryptographic Failures, A07 Identification and Auth Failures
# ============================================================

import os
import pytest
from conftest import route

LOGIN = route("TEST_AUTH_LOGIN_ROUTE", "/auth/login")


def parse_set_cookie(header_value: str) -> dict:
    """Parse Set-Cookie header into a dict of directives."""
    parts = [p.strip().lower() for p in header_value.split(";")]
    directives = {}
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            directives[k.strip()] = v.strip()
        else:
            directives[part] = True
    return directives


@pytest.mark.asyncio
async def test_session_cookie_httponly(client):
    """
    HttpOnly prevents JavaScript from reading session cookies.
    Without it, XSS can steal session tokens directly via document.cookie.
    """
    res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    })

    set_cookie = res.headers.get("set-cookie", "")
    if not set_cookie:
        pytest.skip("No Set-Cookie header  -  app may use token auth instead of cookies")

    cookie = parse_set_cookie(set_cookie)
    assert "httponly" in cookie, (
        "Session cookie missing HttpOnly flag  -  XSS can steal session token"
    )


@pytest.mark.asyncio
async def test_session_cookie_secure(client):
    """
    Secure flag prevents cookie transmission over HTTP.
    Without it, session tokens are transmitted in plaintext on non-HTTPS connections.
    NOTE: In-memory ASGI tests run over HTTP  -  Secure flag must still be SET
    even if not enforced by the test transport.
    """
    res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    })

    set_cookie = res.headers.get("set-cookie", "")
    if not set_cookie:
        pytest.skip("No Set-Cookie header")

    cookie = parse_set_cookie(set_cookie)
    assert "secure" in cookie, (
        "Session cookie missing Secure flag  -  cookie transmitted over HTTP"
    )


@pytest.mark.asyncio
async def test_session_cookie_samesite(client):
    """
    SameSite=Strict or Lax prevents CSRF via cross-site form submissions.
    SameSite=None requires Secure and enables cross-site sends  -  use deliberately.
    """
    res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    })

    set_cookie = res.headers.get("set-cookie", "")
    if not set_cookie:
        pytest.skip("No Set-Cookie header")

    cookie = parse_set_cookie(set_cookie)
    samesite = cookie.get("samesite", "")

    assert samesite in ("strict", "lax"), (
        f"SameSite='{samesite}'  -  must be Strict or Lax to prevent CSRF. "
        "SameSite=None allows cross-site requests."
    )


@pytest.mark.asyncio
async def test_no_sensitive_data_in_cookie_value(client):
    """
    Cookie values must not contain plaintext sensitive data.
    Session identifiers should be opaque tokens  -  not JWTs with user data,
    not serialized user objects, not role flags.
    """
    res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    })

    set_cookie = res.headers.get("set-cookie", "")
    if not set_cookie:
        pytest.skip("No Set-Cookie header")

    cookie_lower = set_cookie.lower()
    sensitive_patterns = ["password", "secret", "admin", "role=", "is_admin"]
    for pattern in sensitive_patterns:
        assert pattern not in cookie_lower, (
            f"Cookie value may contain sensitive data: '{pattern}'"
        )
