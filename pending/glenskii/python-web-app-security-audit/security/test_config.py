# ============================================================
# test_config.py  -  Config hardening, debug mode, secret exposure
#
# Prevents: debug pages in production, test route exposure,
# secret leakage via API responses, verbose server identification.
#
# OWASP: A05 Security Misconfiguration
# ============================================================

import pytest
from conftest import route

PUBLIC = route("TEST_PUBLIC_ROUTE", "/")
NOT_FOUND = route("TEST_404_ROUTE", "/this-route-does-not-exist")
ERROR_ROUTE = route("TEST_ERROR_ROUTE", "/debug/trigger-error")


# ── Debug mode detection ──────────────────────────────────────────────────────

DEBUG_INDICATORS = [
    "debug=true",
    "debug mode",
    "development server",
    "werkzeug debugger",
    "django debug toolbar",
    "traceback (most recent call last)",
    "exception value:",
    "exception location:",
    "python executable:",
    "python version:",
    "django settings module",
    "installed apps",
    "reload this page",         # Django debug page footer
    "switch to copy-and-paste", # Django debug page
]


@pytest.mark.asyncio
async def test_debug_mode_not_active_on_public_route(client):
    """
    Django DEBUG=True and Flask DEBUG=True expose full stack traces,
    environment variables, installed apps, and source code in the browser.
    This must never be active in a deployed environment.
    """
    res = await client.get(PUBLIC)
    body = res.text.lower()

    for indicator in DEBUG_INDICATORS:
        assert indicator not in body, (
            f"Debug mode indicator found in public response: '{indicator}'"
        )


@pytest.mark.asyncio
async def test_debug_mode_not_exposed_on_error(client):
    """
    Error pages are where debug mode is most dangerous.
    A triggered exception in debug mode returns full source code context.
    """
    res = await client.get(ERROR_ROUTE)
    body = res.text.lower()

    for indicator in DEBUG_INDICATORS:
        assert indicator not in body, (
            f"Debug mode indicator in error response: '{indicator}'"
        )


@pytest.mark.asyncio
async def test_debug_route_not_accessible_in_production(client):
    """
    Debug trigger routes must not be mounted in production.
    These routes exist for development and must be removed or guarded
    before deployment.
    """
    res = await client.get(ERROR_ROUTE)
    # Should return 404 (not mounted) or 401/403 (guarded)
    # 200 or 500 indicates a debug route is live in production
    assert res.status_code in (401, 403, 404), (
        f"Debug route returned {res.status_code}  -  "
        "test/debug routes must not be accessible in production"
    )


# ── Environment variable and secret leakage ───────────────────────────────────

SECRET_PATTERNS = [
    "secret_key",
    "database_url",
    "db_password",
    "api_key",
    "aws_access_key",
    "aws_secret",
    "stripe_secret",
    "sendgrid_api",
    "jwt_secret",
    "private_key",
    "-----begin",            # PEM key header
    "eyj",                   # Raw JWT prefix (base64 encoded {)
    "postgres://",
    "mysql://",
    "mongodb://",
    "redis://",
    "amqp://",
]


@pytest.mark.asyncio
async def test_no_secrets_in_public_response(client):
    """
    API responses must not contain secrets, connection strings,
    or environment variable values. Default application scaffolds sometimes
    return full config objects in debug responses.
    """
    res = await client.get(PUBLIC)
    body = res.text.lower()

    for pattern in SECRET_PATTERNS:
        assert pattern not in body, (
            f"Possible secret pattern in public response: '{pattern}'"
        )


@pytest.mark.asyncio
async def test_no_secrets_in_error_response(client):
    """
    Error responses must not leak connection strings or keys.
    ORM errors often include the full DATABASE_URL in exception messages.
    """
    res = await client.get(NOT_FOUND)
    body = res.text.lower()

    for pattern in SECRET_PATTERNS:
        assert pattern not in body, (
            f"Possible secret pattern in 404 response: '{pattern}'"
        )


# ── Method abuse ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["TRACE", "CONNECT", "PATCH"])
async def test_unsupported_methods_rejected(client, method):
    """
    TRACE enables XST (Cross-Site Tracing) attacks  -  must be disabled.
    CONNECT is a proxy method  -  must not be accepted by app servers.
    PATCH on non-PATCH routes must return 405.
    """
    res = await client.request(method, PUBLIC)
    assert res.status_code in (404, 405), (
        f"Method {method} returned {res.status_code}  -  expected 404 or 405"
    )


@pytest.mark.asyncio
async def test_trace_method_rejected(client):
    """
    TRACE method enables XST attacks  -  must return 405 explicitly.
    XST allows cookie theft even with HttpOnly via reflected TRACE response.
    """
    res = await client.request("TRACE", PUBLIC)
    assert res.status_code in (404, 405), (
        f"TRACE method accepted  -  XST vulnerability possible. Status: {res.status_code}"
    )


# ── Server fingerprinting ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_version_not_exposed_in_headers(client):
    """
    Framework version numbers in headers reduce attacker recon cost.
    Known version = known CVEs = known exploits.
    """
    res = await client.get(PUBLIC)

    version_headers = ["x-fastapi-version", "x-django-version", "x-powered-by"]
    for header in version_headers:
        assert header not in res.headers, (
            f"Version header present: {header}={res.headers.get(header)}"
        )

    server = res.headers.get("server", "").lower()
    version_indicators = ["0.", "1.", "2.", "3.", "4.", "/"]
    for indicator in version_indicators:
        if indicator in server:
            pytest.fail(
                f"Server header may contain version: '{server}'  -  suppress or obscure"
            )
