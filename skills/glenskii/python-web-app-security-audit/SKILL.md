---
name: python-web-app-security-audit
description: "Run defensive pre-release security tests for Python web applications. Use for FastAPI, Django, Flask, and ASGI services: the common interface between Python web apps and servers. Tests authentication, authorization, hostile input, headers, CORS, cookies, rate limits, errors, and configuration to return evidence-backed findings and clear test boundaries."
license: CC-BY-4.0
metadata:
  version: 1.0.0
---

# Python Web App Security Audit

Run a configurable pytest suite against a local Python web application before release. It uses ASGI, the interface between a Python web app and its server, so the checks can exercise FastAPI, Django, Flask through an adapter, and comparable services without opening a public server.

## Scope

The bundled checks cover authentication, authorization, input validation, response headers, CORS, cookies, rate limits, error handling, HTTP method handling, and unsafe configuration. Read [setup and boundaries](references/setup-and-boundaries.md) before adapting the suite to an application.

Do not represent a passing run as a penetration test or proof of production security. The suite does not verify deployment TLS, a WAF, dependency vulnerabilities, external infrastructure, or controls it cannot reach through the configured test application.

## Prepare the suite

1. Install the dependencies in the target project's isolated environment.

   ```bash
   pip install "pytest>=8" "pytest-asyncio>=0.24" "httpx>=0.27" python-dotenv
   ```

2. Copy the bundled suite into the target project without overwriting an existing security directory.

   ```bash
   python scripts/prepare_security_suite.py C:\path\to\your-project
   ```

   The helper copies `security/`, `pytest.ini` when absent, and the `.env.test.template` file. It never creates a credentials file.

3. In the copied `security/` directory, copy `.env.test.template` to `.env.test`. Supply an app import path, routes, rate limit, permitted origin, and dedicated test credentials. Keep `.env.test` out of version control.

4. From the target project root, run the suite.

   ```bash
   pytest security/ -v
   ```

## Operating rules

1. Test actual application behavior, not framework defaults.
2. Use dedicated test accounts and non-production data.
3. Configure route variables before treating a failing default route as a defect.
4. Inspect every failure before assigning a release gate.
5. Keep application-layer findings separate from infrastructure findings.
6. Report both verified results and test boundaries.

## Report the result

Use [the report template](assets/security-audit-report-template.md). For every finding, state the affected route or control, evidence, severity, recommended fix, and what was not tested. End with one of these release decisions:

- **BLOCKED:** A confirmed issue must be fixed before release.
- **REVIEW REQUIRED:** A material risk remains and needs an owner decision.
- **PASS:** The configured checks found no blocking or review-level issue. This does not prove complete security.

## Suite contents

| File | Purpose |
|---|---|
| `security/conftest.py` | Application import, test client, authentication fixtures, and route helpers |
| `security/test_headers.py` | Header presence and directive quality |
| `security/test_validation.py` | Hostile input, malformed payloads, and type coercion |
| `security/test_auth.py` | Authentication enforcement and enumeration resistance |
| `security/test_authorization.py` | Object ownership, role boundaries, and mass assignment |
| `security/test_rate_limit.py` | Threshold and 429 response checks |
| `security/test_errors.py` | Error sanitization and internal detail leakage |
| `security/test_cors.py` | Origin restrictions and preflight handling |
| `security/test_cookies.py` | Cookie flag enforcement |
| `security/test_config.py` | Debug exposure, method handling, and configuration checks |

## Boundaries

This skill does not replace manual security assessment, dependency scanning, production HTTPS verification, WAF validation, or dynamic scanning. Add an application-specific CSRF test when state-changing requests use cookie authentication.
