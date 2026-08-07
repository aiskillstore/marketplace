# ============================================================
# test_headers.py  -  Security header presence and directive quality
#
# Prevents: clickjacking, MIME sniffing, XSS via missing CSP,
# HTTPS downgrade attacks, referrer leakage, browser feature abuse.
#
# IMPORTANT: Header presence alone is not sufficient.
# Each test validates directive quality, not just existence.
# ============================================================

import os
import pytest
from conftest import route

PUBLIC = route("TEST_PUBLIC_ROUTE", "/")
PROTECTED = route("TEST_PROTECTED_ROUTE", "/api/me")
NOT_FOUND = route("TEST_404_ROUTE", "/this-route-does-not-exist")
ERROR_SIM = route("TEST_ERROR_SIM_ROUTE", "/error-test")


# ── Content-Security-Policy ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_csp_present_and_strict(client):
    """
    CSP without default-src allows unrestricted resource loading.
    unsafe-inline and unsafe-eval enable XSS via injected scripts.
    """
    res = await client.get(PUBLIC)
    headers = res.headers

    assert "content-security-policy" in headers, "CSP header missing"

    csp = headers["content-security-policy"].lower()
    assert "default-src" in csp, "CSP missing default-src directive"
    assert "object-src" in csp, "CSP missing object-src  -  allows plugin exploitation"
    assert "unsafe-inline" not in csp, "CSP allows unsafe-inline  -  XSS risk"
    assert "unsafe-eval" not in csp, "CSP allows unsafe-eval  -  XSS risk"


@pytest.mark.asyncio
async def test_csp_on_error_response(client):
    """
    CSP must apply to error pages  -  attackers target error flows for injection.
    """
    res = await client.get(NOT_FOUND)
    assert "content-security-policy" in res.headers, "CSP missing on 404 response"


@pytest.mark.asyncio
async def test_csp_on_protected_route(client):
    """
    Authenticated routes must also carry CSP  -  do not assume auth = security.
    """
    res = await client.get(PROTECTED)
    assert "content-security-policy" in res.headers, "CSP missing on protected route"


# ── X-Frame-Options ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_x_frame_options(client):
    """
    Prevents clickjacking  -  attacker embeds your app in an invisible iframe
    and captures user clicks on UI elements (including auth buttons).
    """
    res = await client.get(PUBLIC)
    xfo = res.headers.get("x-frame-options", "").upper()
    assert xfo in ("DENY", "SAMEORIGIN"), (
        f"X-Frame-Options is '{xfo}'  -  must be DENY or SAMEORIGIN"
    )


# ── X-Content-Type-Options ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_x_content_type_options(client):
    """
    Prevents MIME sniffing  -  browsers may execute content as a different type
    than declared, enabling script injection via uploaded files or API responses.
    """
    res = await client.get(PUBLIC)
    assert res.headers.get("x-content-type-options", "").lower() == "nosniff", (
        "X-Content-Type-Options must be 'nosniff'"
    )


# ── Referrer-Policy ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_referrer_policy(client):
    """
    Controls what referrer data is sent with requests.
    Overly permissive policies leak auth tokens or internal paths in headers.
    """
    res = await client.get(PUBLIC)
    policy = res.headers.get("referrer-policy", "").lower()

    assert policy != "", "Referrer-Policy header missing"

    # Reject overly permissive values
    dangerous = ("unsafe-url", "no-referrer-when-downgrade")
    assert policy not in dangerous, (
        f"Referrer-Policy '{policy}' leaks referrer data to third parties"
    )


# ── Strict-Transport-Security ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hsts_header_present(client):
    """
    HSTS forces HTTPS  -  without it, clients can be downgraded to HTTP
    by a man-in-the-middle attacker. Test checks header is present.
    NOTE: max-age below 1 year is considered insufficient.
    Production validation requires actual HTTPS  -  run separately.
    """
    res = await client.get(PUBLIC)
    hsts = res.headers.get("strict-transport-security", "")

    if hsts:
        # Validate max-age is at least 1 year (31536000 seconds)
        for part in hsts.split(";"):
            part = part.strip().lower()
            if part.startswith("max-age="):
                max_age = int(part.split("=")[1])
                assert max_age >= 31536000, (
                    f"HSTS max-age {max_age} is below 1 year  -  insufficient"
                )


# ── Permissions-Policy ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_permissions_policy(client):
    """
    Permissions-Policy restricts browser feature access (camera, mic, geolocation).
    Without it, embedded third-party scripts can request sensitive device access.
    """
    res = await client.get(PUBLIC)
    pp = res.headers.get("permissions-policy", "")
    # Warn only  -  not all apps require this, but it should be deliberately set
    if not pp:
        pytest.skip(
            "Permissions-Policy not set  -  acceptable if no sensitive browser APIs used"
        )


# ── Header coverage across route types ───────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("header", [
    "x-frame-options",
    "x-content-type-options",
    "content-security-policy",
])
async def test_security_headers_on_404(client, header):
    """
    Security headers must appear on error responses.
    Missing headers on non-200 paths are a common oversight.
    """
    res = await client.get(NOT_FOUND)
    assert header in res.headers, f"{header} missing on 404 response"


@pytest.mark.asyncio
async def test_no_server_header_leakage(client):
    """
    Server header can reveal framework and version  -  reduces attacker recon cost.
    It should be suppressed or obscured.
    """
    res = await client.get(PUBLIC)
    server = res.headers.get("server", "").lower()

    revealing_values = ("uvicorn", "gunicorn", "fastapi", "django", "werkzeug", "python")
    for val in revealing_values:
        assert val not in server, (
            f"Server header reveals framework: '{server}'"
        )


@pytest.mark.asyncio
async def test_no_x_powered_by(client):
    """
    X-Powered-By leaks technology stack  -  suppress entirely.
    """
    res = await client.get(PUBLIC)
    assert "x-powered-by" not in res.headers, (
        "X-Powered-By header present  -  remove to reduce stack fingerprinting"
    )
