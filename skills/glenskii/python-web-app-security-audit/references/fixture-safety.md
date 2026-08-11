# Fixture safety

Use fixtures that can authenticate against a local or isolated test application without changing application state beyond the configured login flow.

## Account rules

- Provide dedicated existing test accounts through `.env.test`.
- Do not create users, roles, tenants, records, or database fixtures from this package.
- Do not use production accounts, production data, or shared session material.
- Keep `TEST_ALLOW_ACTIVE_PROBES=false` until the application owner authorizes an isolated test environment.
- Stop when the configured account cannot authenticate. Do not guess alternate credentials or create a replacement account.

## Route rules

Configure only routes that exist in the target application. A missing default route is a configuration problem until the target route is confirmed. Keep write routes out of the bundled suite unless the application owner has built a separate disposable test fixture and authorized the scope.

## Response rules

Record status codes, relevant headers, and sanitized response excerpts. Exclude tokens, cookies, credentials, personal data, and stack traces from reports. A rejected request is evidence only when the configured route and expected policy are known.

## Cleanup

The bundled suite must leave no created accounts, changed records, or schema changes. If an application-owned extension performs a write, that extension must use a disposable database and explicit cleanup outside this package.
