# ============================================================
# conftest.py  -  Shared fixtures for the Python web app security audit suite
# All tests import from here. Do not duplicate fixtures elsewhere.
# ============================================================

import os
import pytest
from importlib import import_module
from httpx import ASGITransport, AsyncClient
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))


def active_probes_enabled() -> bool:
    """Return whether the application owner authorized active probes."""
    return os.getenv("TEST_ALLOW_ACTIVE_PROBES", "false").strip().lower() == "true"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "active_probe: sends repeated, malformed, or target-specific requests",
    )


@pytest.fixture(autouse=True)
def require_active_probe_authorization(request):
    """Skip active probes unless an isolated target was explicitly authorized."""
    if request.node.get_closest_marker("active_probe") and not active_probes_enabled():
        pytest.skip(
            "Active probe disabled. Set TEST_ALLOW_ACTIVE_PROBES=true only for an "
            "authorized isolated test environment."
        )


def load_app():
    """
    Dynamically import the ASGI app from APP_IMPORT_PATH.
    Format: module.path:app_variable
    Fails loudly if env var is missing  -  no silent misconfiguration.
    """
    import_path = os.getenv("APP_IMPORT_PATH")
    if not import_path or ":" not in import_path:
        raise EnvironmentError(
            "APP_IMPORT_PATH must be set in .env.test as 'module.path:app_variable'"
        )
    module_path, app_name = import_path.split(":", 1)
    module = import_module(module_path)
    return getattr(module, app_name)


@pytest.fixture
async def client():
    """
    Unauthenticated ASGI test client.
    Use for public routes and auth rejection tests.
    """
    app = load_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client():
    """
    Authenticated ASGI test client.
    Logs in with TEST_USERNAME / TEST_PASSWORD and injects token.
    Use for protected route tests.
    """
    app = load_app()
    login_route = os.getenv("TEST_AUTH_LOGIN_ROUTE", "/auth/login")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Obtain auth token  -  adjust payload keys to match your app
        response = await ac.post(login_route, json={
            "username": os.getenv("TEST_USERNAME"),
            "password": os.getenv("TEST_PASSWORD"),
        })
        assert response.status_code == 200, (
            f"Auth fixture login failed: {response.status_code}  -  "
            "check TEST_USERNAME / TEST_PASSWORD in .env.test"
        )

        token = response.json().get("access_token")
        assert token, "Auth fixture: no access_token in login response"

        ac.headers.update({"Authorization": f"Bearer {token}"})
        yield ac


@pytest.fixture
async def admin_client():
    """
    Admin-authenticated ASGI test client.
    Use for admin boundary and privilege escalation tests.
    """
    app = load_app()
    login_route = os.getenv("TEST_AUTH_LOGIN_ROUTE", "/auth/login")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post(login_route, json={
            "username": os.getenv("TEST_ADMIN_USERNAME"),
            "password": os.getenv("TEST_ADMIN_PASSWORD"),
        })
        assert response.status_code == 200, (
            f"Admin auth fixture login failed: {response.status_code}"
        )

        token = response.json().get("access_token")
        assert token, "Admin auth fixture: no access_token in login response"

        ac.headers.update({"Authorization": f"Bearer {token}"})
        yield ac


# ── Route helpers ─────────────────────────────────────────────────────────────

def route(env_key: str, default: str = "/") -> str:
    """Return route from env or fall back to default."""
    return os.getenv(env_key, default)
