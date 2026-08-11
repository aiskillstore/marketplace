# Setup and Test Boundaries

## Configuration

Set `APP_IMPORT_PATH` to the importable application and variable name, such as `my_project.main:app`. The suite loads this application in process with `httpx.ASGITransport`.

Set route variables only for routes the application actually exposes. The defaults are examples, not universal requirements. Use dedicated accounts for `TEST_USERNAME` and `TEST_ADMIN_USERNAME`. Do not place production credentials in `.env.test`.

Configure `TEST_RATE_LIMIT_THRESHOLD` to match the real limit. Set `TEST_ALLOWED_ORIGIN` to an origin the application should accept and `TEST_HOSTILE_ORIGIN` to an origin it must reject.

Set `TEST_ALLOW_ACTIVE_PROBES=true` only after the application owner authorizes an isolated test environment. Active probes include repeated login requests, malformed login payloads, and target-specific authorization checks. Set `TEST_IDOR_TARGET_IDS` and `TEST_IDOR_UNOWNED_ID` only to dedicated records known not to belong to the regular test account.

## Framework compatibility

FastAPI applications normally expose an ASGI callable directly. Django applications need an ASGI entry point, commonly `project.asgi:application`. Flask needs an ASGI adapter before it can be exercised by this suite.

## Interpret results carefully

The tests can verify the behavior of the configured application and routes. They cannot verify a reverse proxy, CDN policy, WAF, certificate configuration, production secrets, live third-party identity provider, or an unconfigured route.

A skipped check is not a pass. Record why it was skipped, whether the control applies, and the separate evidence used to cover it.

## Non-destructive test policy

The bundled suite does not create accounts, modify application records, delete records, or execute schema-changing database commands. Test registration, password reset, and other write flows only in an application-owned suite that enforces a disposable database and cleans up every test record.
