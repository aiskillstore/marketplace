# Python Web App Security Audit

Version 1.1.0

Python Web App Security Audit runs defensive pre-release checks against a configured local application. It supports FastAPI, Django, Flask through an ASGI adapter, and other importable ASGI services.

The suite checks authentication, authorization, hostile input, security headers, CORS, cookies, rate limits, error handling, HTTP methods, and runtime configuration. It returns evidence-backed findings with stated test boundaries.

## Why use it

Application teams often need repeatable security checks before release, but a generic scan cannot know which routes, accounts, limits, and ownership rules apply to a specific service. This skill provides configurable tests without treating defaults or skipped routes as a pass.

## Included material

- A pytest suite for common application-layer controls.
- A safe copy helper that does not overwrite an existing security directory.
- Framework, route, fixture-safety, and assertion references.
- A report template and release decision guidance.
- Explicit rules that prohibit account creation, record changes, and destructive database commands.

## Start safely

1. Read [setup and boundaries](references/setup-and-boundaries.md).
2. Install `requirements-security-audit.txt` after using the copy helper, or install this folder's [requirements](requirements.txt).
3. Configure only routes, users, thresholds, and origins that exist in the target application.
4. Use dedicated non-production accounts and an isolated environment.
5. Keep `TEST_ALLOW_ACTIVE_PROBES=false` until the application owner authorizes active checks.
6. Configure an explicit rate threshold and dedicated unowned target IDs before enabling active checks.
7. Run `python -m pytest security/ -v` from the target project root.
8. Read every failure before setting a release decision.

## What a result means

`PASS` means the configured checks found no blocking or review-level issue. It does not prove full production security. `REVIEW REQUIRED` means an owner decision is needed. `BLOCKED` means a confirmed weakness must be corrected before release.

## Documentation

- [Skill instructions](SKILL.md)
- [Setup and boundaries](references/setup-and-boundaries.md)
- [Framework adapters](references/framework-adapters.md)
- [Route configuration](references/route-configuration.md)
- [Fixture safety](references/fixture-safety.md)
- [Assertion catalog](references/assertion-catalog.md)
- [Release decision guide](docs/release-decision-guide.md)
- [Continuous integration guide](docs/continuous-integration-guide.md)

## License

MIT. See [LICENSE](LICENSE).
