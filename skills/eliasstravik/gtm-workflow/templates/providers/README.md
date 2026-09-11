# Provider adapters

Put adapters in `providers/<name>.ts`, with one plain exported function per endpoint. Call each adapter through `provider()` inside an operator-named step and set that step's `maxRetries = 0`. Use the `Provider`, `Endpoints`, `Environment`, `Cost per request`, `Cache TTL`, and `Mode` header labels documented in the skill's provider reference. Mirror environment names empty in `.env.example`. Tests use fixtures under `providers/__fixtures__/` and make no paid calls. With `GTM_SANDBOX=1`, an adapter may omit its authorization header when the host brokers that header at the firewall.

Declare a documented free preflight check with `Auth check: GET https://api.example.com/account free` and `Auth header: Authorization | COMPANY_DATA_API_KEY | Bearer`, or `Auth check: none` when unavailable. Every named credential belongs in `Environment`.

Fixture mode reads `__fixtures__/<encoded-provider>/<encoded-endpoint>.json` arrays of `{ "input": {}, "value": {} }` cases. Export row functions and add `__fixtures__/rows/<workflow-path>.json` arrays of `{ "step": "enrichAccount", "row": { "key": "example" }, "expected": {} }` for `gtm check`. Exact canonical input must match; missing fixtures warn and never call a live endpoint.
