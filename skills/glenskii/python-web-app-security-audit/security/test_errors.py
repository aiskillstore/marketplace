# ============================================================
# test_errors.py  -  Error sanitization and stack trace leakage
#
# Prevents: information disclosure via verbose error messages,
# stack traces in production, debug pages, SQL/ORM query exposure,
# internal path and environment variable leakage.
#
# OWASP: A05 Security Misconfiguration, A09 Security Logging Failures
# ============================================================

import pytest
from conftest import route

ERROR_ROUTE = route("TEST_ERROR_ROUTE", "/debug/trigger-error")
NOT_FOUND = route("TEST_404_ROUTE", "/this-route-does-not-exist")
ERROR_SIM = route("TEST_ERROR_SIM_ROUTE", "/error-test")

# Terms that must never appear in any production error response
FORBIDDEN_LEAK_TERMS = [
    "traceback",
    "exception",
    "line ",
    "file \"",
    "/home/",
    "/usr/",
    "/var/",
    "/app/",
    "select *",
    "select ",
    " from ",
    " where ",
    "sql",
    "sqlalchemy",
    "django.db",
    "python",
    "uvicorn",
    "gunicorn",
    "fastapi",
    "starlette",
    "pydantic",
    "internal server error at",
    "debug=true",
    "secret_key",
    "database_url",
    "password=",
    "os.environ",
]


@pytest.mark.asyncio
async def test_error_route_does_not_leak_stack_trace(client):
    """
    Triggered errors must not return stack traces.
    Attackers use stack traces to map internal structure and identify
    exploitable code paths.
    """
    res = await client.get(ERROR_ROUTE)
    body = res.text.lower()

    for term in FORBIDDEN_LEAK_TERMS:
        assert term not in body, (
            f"Error response leaks sensitive term: '{term}'"
        )


@pytest.mark.asyncio
async def test_404_does_not_leak_internals(client):
    """
    404 responses must not reveal framework, routes, or internal paths.
    """
    res = await client.get(NOT_FOUND)
    body = res.text.lower()

    for term in ["traceback", "python", "fastapi", "django", "uvicorn", "/home/"]:
        assert term not in body, f"404 leaks internal info: '{term}'"


@pytest.mark.asyncio
async def test_500_error_returns_generic_message(client):
    """
    500 responses must return a generic error  -  not a debug page.
    """
    res = await client.get(ERROR_SIM)
    if res.status_code == 500:
        body = res.text.lower()
        for term in FORBIDDEN_LEAK_TERMS:
            assert term not in body, (
                f"500 response leaks: '{term}'"
            )


@pytest.mark.asyncio
async def test_error_response_is_json_not_html_debug_page(client):
    """
    API error responses must return JSON  -  not HTML debug pages.
    Django DEBUG=True returns full HTML debug pages with source code.
    """
    res = await client.get(ERROR_ROUTE)
    if res.status_code >= 400:
        content_type = res.headers.get("content-type", "")
        # API responses should not return HTML error pages
        if "text/html" in content_type:
            body = res.text.lower()
            assert "traceback" not in body, (
                "HTML error response contains traceback  -  DEBUG mode may be active"
            )
            assert "exception" not in body


@pytest.mark.asyncio
async def test_malformed_request_returns_clean_400(client):
    """
    Malformed requests must return clean 400/422  -  no internal details.
    """
    res = await client.post(
        "/api/me",
        content="NOT JSON AT ALL !!!",
        headers={"Content-Type": "application/json"}
    )
    if res.status_code in (400, 422):
        body = res.text.lower()
        for term in ["traceback", "python", "line "]:
            assert term not in body
