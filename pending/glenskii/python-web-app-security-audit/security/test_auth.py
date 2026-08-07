# ============================================================
# test_auth.py  -  Authentication enforcement and enumeration resistance
#
# Prevents: unauthenticated access, token bypass, account enumeration,
# credential stuffing enablement, session fixation.
# ============================================================

import os
import pytest
from conftest import route

LOGIN = route("TEST_AUTH_LOGIN_ROUTE", "/auth/login")
REGISTER = route("TEST_AUTH_REGISTER_ROUTE", "/auth/register")
PROTECTED = route("TEST_PROTECTED_ROUTE", "/api/me")
ADMIN = route("TEST_ADMIN_ROUTE", "/api/admin")


# ── Unauthenticated access rejection ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_protected_route_rejects_unauthenticated(client):
    """
    Protected resources must return 401 or 403 with no token.
    200 here means auth middleware is missing or misconfigured.
    """
    res = await client.get(PROTECTED)
    assert res.status_code in (401, 403), (
        f"Protected route returned {res.status_code} without auth  -  "
        "auth middleware may not be applied"
    )


@pytest.mark.asyncio
async def test_admin_route_rejects_unauthenticated(client):
    """
    Admin routes must be inaccessible without credentials.
    """
    res = await client.get(ADMIN)
    assert res.status_code in (401, 403), (
        f"Admin route returned {res.status_code} without auth"
    )


@pytest.mark.asyncio
async def test_protected_route_rejects_invalid_token(client):
    """
    Malformed or expired tokens must be rejected.
    Some frameworks silently accept garbage tokens  -  this catches that.
    """
    res = await client.get(
        PROTECTED,
        headers={"Authorization": "Bearer this.is.not.a.valid.token"}
    )
    assert res.status_code in (401, 403), (
        f"Invalid token accepted  -  returned {res.status_code}"
    )


@pytest.mark.asyncio
async def test_protected_route_rejects_empty_bearer(client):
    """
    Empty Bearer token must be rejected  -  not treated as anonymous.
    """
    res = await client.get(
        PROTECTED,
        headers={"Authorization": "Bearer "}
    )
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_protected_route_rejects_wrong_scheme(client):
    """
    Basic auth scheme on a Bearer endpoint must be rejected.
    Scheme confusion can bypass some auth middleware.
    """
    res = await client.get(
        PROTECTED,
        headers={"Authorization": "Basic dGVzdDp0ZXN0"}
    )
    assert res.status_code in (401, 403)


# ── Authenticated access confirmation ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_protected_route_accepts_valid_token(auth_client):
    """
    Valid authenticated users must be able to access protected resources.
    Confirms the test fixture is working correctly.
    """
    res = await auth_client.get(PROTECTED)
    assert res.status_code == 200, (
        f"Valid auth rejected on protected route  -  returned {res.status_code}"
    )


# ── Login enumeration resistance ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_unknown_user_does_not_reveal_existence(client):
    """
    Login failure for unknown user must return the same response as wrong password.
    Different responses enable account enumeration  -  attackers map valid accounts
    before credential stuffing attacks.
    """
    unknown_res = await client.post(LOGIN, json={
        "username": "definitely_does_not_exist_xyz987",
        "password": "SomePassword123!"
    })
    wrong_pass_res = await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": "WrongPasswordXYZ!"
    })

    # Status codes must match
    assert unknown_res.status_code == wrong_pass_res.status_code, (
        "Login returns different status codes for unknown user vs wrong password  -  "
        "account enumeration possible"
    )

    # Response bodies must not reveal account existence
    for phrase in ("user not found", "no account", "does not exist", "invalid user"):
        assert phrase not in unknown_res.text.lower(), (
            f"Login response reveals account existence: '{phrase}'"
        )


@pytest.mark.asyncio
async def test_login_timing_consistency(client):
    """
    Response timing for unknown user vs wrong password should not differ
    significantly. Timing oracles enable enumeration even when bodies match.
    This test is a heuristic  -  production timing analysis requires load testing.
    """
    import time

    start = time.monotonic()
    await client.post(LOGIN, json={
        "username": "nonexistent_user_abc123",
        "password": "SomePassword!"
    })
    unknown_time = time.monotonic() - start

    start = time.monotonic()
    await client.post(LOGIN, json={
        "username": os.getenv("TEST_USERNAME"),
        "password": "WrongPassword!"
    })
    known_time = time.monotonic() - start

    # Heuristic: timing difference should not exceed 500ms
    diff = abs(unknown_time - known_time)
    assert diff < 0.5, (
        f"Login timing difference {diff:.3f}s may enable timing-based enumeration"
    )


# ── Invalid login credentials ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_rejects_missing_password(client):
    """
    Login with no password must be rejected  -  not treated as anonymous session.
    """
    res = await client.post(LOGIN, json={"username": os.getenv("TEST_USERNAME")})
    assert res.status_code in (400, 422), (
        f"Login accepted missing password  -  returned {res.status_code}"
    )


@pytest.mark.asyncio
async def test_login_rejects_missing_username(client):
    """
    Login with no username must be rejected cleanly.
    """
    res = await client.post(LOGIN, json={"password": "SomePassword!"})
    assert res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_login_rejects_empty_credentials(client):
    """
    Empty string credentials must be rejected  -  not matched against empty DB values.
    """
    res = await client.post(LOGIN, json={"username": "", "password": ""})
    assert res.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_login_rejects_null_credentials(client):
    """
    Null credential values must be rejected  -  null handling bugs can bypass auth.
    """
    res = await client.post(LOGIN, json={"username": None, "password": None})
    assert res.status_code in (400, 422)
