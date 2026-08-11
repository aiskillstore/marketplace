# ============================================================
# test_cors.py  -  CORS origin restrictions and preflight handling
#
# Prevents: cross-origin data theft, CSRF via CORS misconfiguration,
# credential leakage to hostile origins.
#
# OWASP: A05 Security Misconfiguration
# ============================================================

import os
import pytest
from conftest import route

PUBLIC = route("TEST_PUBLIC_ROUTE", "/")
PROTECTED = route("TEST_PROTECTED_ROUTE", "/api/me")
HOSTILE_ORIGIN = os.getenv("TEST_HOSTILE_ORIGIN", "https://evil.example.com")
ALLOWED_ORIGIN = os.getenv("TEST_ALLOWED_ORIGIN", "https://yourdomain.com")


@pytest.mark.asyncio
async def test_hostile_origin_not_reflected(client):
    """
    Wildcard CORS or origin reflection allows any site to make credentialed
    requests to your API on behalf of a logged-in user.
    The hostile origin must not appear in Access-Control-Allow-Origin.
    """
    res = await client.get(PUBLIC, headers={"Origin": HOSTILE_ORIGIN})
    acao = res.headers.get("access-control-allow-origin", "")

    assert acao != "*", (
        "Access-Control-Allow-Origin: * allows any origin  -  "
        "credentialed cross-origin requests possible"
    )
    assert HOSTILE_ORIGIN not in acao, (
        f"Hostile origin '{HOSTILE_ORIGIN}' reflected in CORS header"
    )


@pytest.mark.asyncio
async def test_cors_does_not_allow_null_origin(client):
    """
    'null' origin is sent by sandboxed iframes and local file: requests.
    Allowing null enables CSRF from attacker-controlled local content.
    """
    res = await client.get(PUBLIC, headers={"Origin": "null"})
    acao = res.headers.get("access-control-allow-origin", "")
    assert acao != "null", (
        "CORS allows 'null' origin  -  sandboxed iframe CSRF possible"
    )


@pytest.mark.asyncio
async def test_preflight_hostile_origin_rejected(client):
    """
    OPTIONS preflight from hostile origin must not be approved.
    Approved preflights enable the hostile site to make cross-origin requests.
    """
    res = await client.options(
        PUBLIC,
        headers={
            "Origin": HOSTILE_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization",
        }
    )

    acao = res.headers.get("access-control-allow-origin", "")
    assert HOSTILE_ORIGIN not in acao, (
        f"Preflight approved hostile origin '{HOSTILE_ORIGIN}'"
    )


@pytest.mark.asyncio
async def test_credentials_not_allowed_with_wildcard(client):
    """
    Access-Control-Allow-Credentials: true with * is invalid per spec
    but some misconfigured servers attempt it. Browsers reject it
    but the config itself indicates a misunderstanding of CORS security.
    """
    res = await client.get(PUBLIC, headers={"Origin": ALLOWED_ORIGIN})
    acao = res.headers.get("access-control-allow-origin", "")
    acac = res.headers.get("access-control-allow-credentials", "").lower()

    if acao == "*" and acac == "true":
        pytest.fail(
            "CORS misconfiguration: Allow-Credentials: true with wildcard origin  -  "
            "invalid and insecure"
        )


@pytest.mark.asyncio
async def test_cors_on_protected_route(client):
    """
    Protected API routes must enforce CORS as strictly as public routes.
    Authenticated endpoints are higher value targets for cross-origin attacks.
    """
    res = await client.options(
        PROTECTED,
        headers={
            "Origin": HOSTILE_ORIGIN,
            "Access-Control-Request-Method": "GET",
        }
    )
    acao = res.headers.get("access-control-allow-origin", "")
    assert HOSTILE_ORIGIN not in acao and acao != "*", (
        f"Protected route CORS approves hostile origin: '{acao}'"
    )
