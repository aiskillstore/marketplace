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

pytestmark = pytest.mark.active_probe


def configured_unowned_ids() -> list[str]:
    """Return dedicated records confirmed not to belong to the test account."""
    raw = os.getenv("TEST_IDOR_TARGET_IDS", "").strip()
    if not raw:
        pytest.skip(
            "Set TEST_IDOR_TARGET_IDS to dedicated unowned test records before "
            "target-specific authorization probes."
        )
    return [item.strip() for item in raw.split(",") if item.strip()]


# ── IDOR  -  Broken Object Level Authorization ──────────────────────────────────

@pytest.mark.asyncio
async def test_idor_cannot_access_other_user_resource(auth_client):
    """
    IDOR (Insecure Direct Object Reference): user can access another user's
    resource by guessing or incrementing an ID in the URL.

    Generated CRUD implementations can omit ownership checks. Configure only
    dedicated records known not to belong to the authenticated test account.
    """
    forbidden_ids = configured_unowned_ids()

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
    target_id = os.getenv("TEST_IDOR_UNOWNED_ID", "").strip()
    if not target_id:
        pytest.skip("Set TEST_IDOR_UNOWNED_ID before UUID authorization probes.")
    url = IDOR_TEMPLATE.replace("{target_id}", target_id)
    res = await auth_client.get(url)
    assert res.status_code in (403, 404, 422)


@pytest.mark.asyncio
async def test_idor_unauthenticated_cannot_access_any_user(client):
    """
    Unauthenticated requests must be rejected before ownership checks run.
    """
    for target_id in configured_unowned_ids():
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
    Generated applications often protect routes from anonymous access but forget
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
