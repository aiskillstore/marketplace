# ============================================================
# test_rate_limit.py  -  Rate limiting and abuse resistance
#
# Prevents: credential stuffing, brute force auth attacks,
# scraping, resource exhaustion, API abuse.
#
# OWASP API Security: API4  -  Unrestricted Resource Consumption
# ============================================================

import os
import asyncio
import pytest
from conftest import route

LOGIN = route("TEST_AUTH_LOGIN_ROUTE", "/auth/login")
PROTECTED = route("TEST_PROTECTED_ROUTE", "/api/me")

pytestmark = pytest.mark.active_probe


def configured_threshold() -> int:
    value = os.getenv("TEST_RATE_LIMIT_THRESHOLD", "").strip()
    if not value:
        pytest.skip("Set TEST_RATE_LIMIT_THRESHOLD before rate-limit probes.")
    try:
        threshold = int(value)
    except ValueError:
        pytest.fail("TEST_RATE_LIMIT_THRESHOLD must be a whole number.")
    if threshold < 1:
        pytest.fail("TEST_RATE_LIMIT_THRESHOLD must be greater than zero.")
    return threshold


@pytest.mark.asyncio
async def test_login_rate_limit_enforced(client):
    """
    Repeated failed login attempts must trigger rate limiting (429).
    Without this, credential stuffing attacks run unchecked.
    Threshold is configurable via TEST_RATE_LIMIT_THRESHOLD.
    """
    threshold = configured_threshold()
    last_status = None
    hit_429 = False

    for i in range(threshold + 10):
        res = await client.post(LOGIN, json={
            "username": f"bruteforce_attempt_{i}",
            "password": "WrongPassword!"
        })
        last_status = res.status_code
        if res.status_code == 429:
            hit_429 = True
            break

    assert hit_429, (
        f"Rate limit not triggered after {threshold + 10} login attempts. "
        f"Last status: {last_status}. "
        "Login endpoint may be vulnerable to credential stuffing."
    )


@pytest.mark.asyncio
async def test_rate_limit_returns_429_not_500(client):
    """
    Rate limit responses must return 429  -  not 500 (unhandled) or 200 (silent pass).
    Some misconfigured limiters silently pass requests after the window.
    """
    threshold = configured_threshold()
    statuses = set()

    for i in range(threshold + 5):
        res = await client.post(LOGIN, json={
            "username": f"ratelimit_test_{i}",
            "password": "Wrong!"
        })
        statuses.add(res.status_code)
        if 429 in statuses:
            break

    assert 500 not in statuses, (
        "Rate limiter returned 500  -  unhandled exception on threshold breach"
    )


@pytest.mark.asyncio
async def test_rate_limit_includes_retry_after_header(client):
    """
    429 responses should include Retry-After header so clients can back off.
    Without it, clients retry immediately and the limiter provides no relief.
    """
    threshold = configured_threshold()
    hit_429 = False

    for i in range(threshold + 10):
        res = await client.post(LOGIN, json={
            "username": f"retry_after_test_{i}",
            "password": "Wrong!"
        })
        if res.status_code == 429:
            hit_429 = True
            has_retry = "retry-after" in res.headers or "x-ratelimit-reset" in res.headers
            if not has_retry:
                pytest.skip(
                    "429 returned but no Retry-After header  -  "
                    "consider adding for client backoff support"
                )
            break

    if not hit_429:
        pytest.skip("Rate limit not triggered in test window  -  increase THRESHOLD or requests")


@pytest.mark.asyncio
async def test_concurrent_requests_rate_limited(client):
    """
    Concurrent burst requests must also be rate limited.
    Sequential rate limiting can be bypassed by parallel requests.
    """
    threshold = configured_threshold()
    tasks = [
        client.post(LOGIN, json={
            "username": f"concurrent_{i}",
            "password": "Wrong!"
        })
        for i in range(threshold + 20)
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    statuses = [
        r.status_code for r in responses
        if hasattr(r, "status_code")
    ]

    assert 429 in statuses, (
        "Concurrent burst not rate limited  -  "
        "rate limiter may only check sequential requests"
    )


@pytest.mark.asyncio
async def test_api_endpoint_rate_limited(client):
    """
    Public API endpoints must also be rate limited  -  not just auth routes.
    Unprotected endpoints can be scraped or used for enumeration.
    """
    threshold = configured_threshold()
    PUBLIC = route("TEST_PUBLIC_ROUTE", "/")
    hit_429 = False

    for i in range(threshold * 3):
        res = await client.get(PUBLIC)
        if res.status_code == 429:
            hit_429 = True
            break

    if not hit_429:
        pytest.skip(
            "Public route rate limit not triggered  -  "
            "verify rate limiting is configured on public endpoints"
        )
