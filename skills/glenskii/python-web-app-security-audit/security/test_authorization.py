# ============================================================
# test_authorization.py  -  IDOR, admin boundary, privilege escalation
#
# Prevents: horizontal privilege escalation (user A reads user B's data),
# vertical privilege escalation (regular user accesses admin functions),
# insecure direct object reference exploitation.
#
# OWASP API Security: API1 (BOLA/IDOR), API5 (Broken Function Level Auth)
# ============================================================

import os
import pytest
from conftest import route

IDOR_TEMPLATE = os.getenv("TEST_IDOR_ROUTE_TEMPLATE", "/api/user/{target_id}")
ADMIN = route("TEST_ADMIN_ROUTE", "/api/admin")
PROTECTED = route("TEST_PROTECTED_ROUTE", "/api/me")


# ── IDOR  -  Broken Object Level Authorization ──────────────────────────────────

@pytest.mark.asyncio
async def test_idor_cannot_access_other_user_resource(auth_client):
    """
    IDOR (Insecure Direct Object Reference): user can access another user's
    resource by guessing or incrementing an ID in the URL.

    This is the #1 API vulnerability class. Vibe-coded apps almost universally
    miss this because code generators can create CRUD without ownership checks.

    Test accesses IDs 1–5. If your test user owns any of these, adjust
    TEST_IDOR_ROUTE_TEMPLATE or test against IDs outside the test account range.
    """
    forbidden_ids = [1, 2, 3, 4, 5]

    for target_id in forbidden_ids:
        url = IDOR_TEMPLATE.replace("{target_id}", str(target_id))
        res = await auth_client.get(url)

        # 200 from a different user's resource = IDOR vulnerability
        # 403, 404 are acceptable (ownership check or obscured IDs)
        assert res.status_code in (403, 404), (
            f"IDOR: auth_client accessed resource ID {target_id} "
            f"and received {res.status_code}  -  ownership check may be missing"
        )


@pytest.mark.asyncio
async def test_idor_uuid_cannot_be_guessed(auth_client):
    """
    Tests that sequential or predictable non-UUID identifiers are not accepted.
    If your app uses UUIDs, this validates the format is enforced.
    """
    fake_uuid = "00000000-0000-0000-0000-000000000001"
    url = IDOR_TEMPLATE.replace("{target_id}", fake_uuid)
    res = await auth_client.get(url)
    assert res.status_code in (403, 404, 422)


@pytest.mark.asyncio
async def test_idor_unauthenticated_cannot_access_any_user(client):
    """
    Unauthenticated requests must be rejected before ownership checks run.
    """
    for target_id in [1, 2, 3]:
        url = IDOR_TEMPLATE.replace("{target_id}", str(target_id))
        res = await client.get(url)
        assert res.status_code in (401, 403), (
            f"Unauthenticated request to user resource {target_id} "
            f"returned {res.status_code}"
        )


# ── Admin boundary enforcement ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_regular_user_cannot_access_admin_route(auth_client):
    """
    Regular authenticated users must be blocked from admin endpoints.
    Vibe-coded apps often protect routes from anonymous access but forget
    to enforce role checks between user tiers.
    """
    res = await auth_client.get(ADMIN)
    assert res.status_code in (401, 403), (
        f"Regular user accessed admin route  -  returned {res.status_code}"
    )


@pytest.mark.asyncio
async def test_admin_user_can_access_admin_route(admin_client):
    """
    Admin credentials must grant access to admin routes.
    Confirms admin fixture is working and admin role is correctly applied.
    """
    res = await admin_client.get(ADMIN)
    assert res.status_code == 200, (
        f"Admin user denied admin route  -  returned {res.status_code}"
    )


@pytest.mark.asyncio
async def test_unauthenticated_cannot_access_admin_route(client):
    """
    Admin routes must reject unauthenticated access  -  not just non-admin users.
    """
    res = await client.get(ADMIN)
    assert res.status_code in (401, 403)


# ── Privilege escalation via parameter manipulation ───────────────────────────

@pytest.mark.asyncio
async def test_cannot_escalate_via_role_parameter(auth_client):
    """
    Attacker attempts to inject role claim in request body or query string.
    App must not accept client-supplied role/permission claims.
    """
    res = await auth_client.get(ADMIN, params={"role": "admin"})
    assert res.status_code in (401, 403), (
        "Role escalation via query param succeeded  -  server accepted client role claim"
    )


@pytest.mark.asyncio
async def test_cannot_escalate_via_body_role(auth_client):
    """
    POST to admin route with forged role in body must be rejected.
    """
    res = await auth_client.post(ADMIN, json={"role": "admin", "is_admin": True})
    assert res.status_code in (401, 403, 405)


# ── Mass assignment protection ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cannot_assign_admin_flag_on_registration(client):
    """
    Mass assignment: attacker includes is_admin or role fields in registration payload.
    Server must ignore or reject undeclared fields  -  not bind them to the user model.
    OWASP API Security: API6  -  Mass Assignment
    """
    register_route = route("TEST_AUTH_REGISTER_ROUTE", "/auth/register")
    res = await client.post(register_route, json={
        "username": "hacker_test_user",
        "password": "Hacker1234!",
        "email": "hacker@example.com",
        "is_admin": True,
        "role": "admin",
        "permissions": ["read", "write", "admin"]
    })

    # Registration may succeed (201) or reject unknown fields (400/422)
    # What must NOT happen: 201 with admin flag applied
    if res.status_code == 201:
        body = res.json()
        assert body.get("is_admin") is not True, (
            "Mass assignment: is_admin=True was accepted from registration payload"
        )
        assert body.get("role") != "admin", (
            "Mass assignment: role=admin was accepted from registration payload"
        )
