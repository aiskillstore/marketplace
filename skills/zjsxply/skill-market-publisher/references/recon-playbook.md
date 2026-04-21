# Recon Playbook

Use this playbook when a market changes or when you need to add a new market adapter.

## Classification Rules

- Classify as `auto-cli` only when an official CLI documents a publish command.
- Classify as `auto-http` only when the live site or official source exposes a stable form or API endpoint.
- Classify as `manual-web` when the live workflow exists but the endpoint is hidden, undocumented, or too brittle to hardcode.
- Classify as `index-only` when discovery depends on installability, telemetry, GitHub App ingestion, or passive crawling instead of direct submission.
- Classify as `incompatible` when the market expects a different artifact type.
- Classify as `needs-recon` until the publish surface is verified from official material.

Prefer official sources in this order:

1. official docs
2. official source repository
3. official submit page HTML
4. official public API docs

Do not upgrade a market to wrapped support only because a front-end bundle contains an internal fetch call.

## Verification Workflow

1. Open the official site, docs page, or official source repository.
2. Find the actual submission surface:
   - CLI command
   - HTTP endpoint
   - HTML form action
   - front-end fetch call
3. Record the exact required fields and auth model.
4. Record repository layout and scope assumptions:
   - single skill repo
   - repo-root skill pack
   - repo with `skills/` subdirectory
   - whether a folder URL truly narrows the import scope
5. Record the strongest public verification surface:
   - status API
   - detail page
   - public search API
   - CLI search or install
6. Record auth boundaries:
   - anonymous
   - login required
   - CLI login required
   - seller onboarding required
   - GitHub App install required
7. Update the market registry in `scripts/skill_market_publish.py`.
8. Run `recon` and `plan` before claiming support.

## Safe Automation Rules

- Default to non-destructive inspection.
- Keep live submission behind an explicit `--execute` flag.
- Never test a live form with fake submissions just to probe validation.
- Preserve CSRF handling when a market uses server-side forms.
- Do not scrape hidden endpoints from unofficial mirrors when the official site does not expose a stable route.
- Keep sample-specific run logs outside the reusable skill folder.

## Listing Design Checklist

Good public listing pages do more than repeat the skill description. When a market exposes rich page design, capture the reusable parts and mirror them in your bundle or operator notes:

- one-line positioning plus category and tags
- canonical source links and install or submit links
- freshness or activity signals such as updated time, workflow status, or review state
- a sample task or test prompt
- the expected outcome or verification target
- visible file inventory or package structure
- trust signals such as audit score, security status, or known risks
- publisher identity and ownership links

These fields make manual submission packets easier to review and make post-submit verification faster.

## Useful Recon Patterns

Inspect page source quickly:

```bash
curl -L -s https://example.com/submit
```

Search for form markers:

```bash
curl -L -s https://example.com/submit | rg 'form|action=|method=|csrf|submit'
```

Search bundled JavaScript for fetch calls:

```bash
curl -L -s https://example.com/submit | rg '_next/static|assets/'
curl -L -s https://example.com/path/to/chunk.js | rg 'fetch\\(|/api/|submit'
```

## Adapter Update Checklist

- Keep the market name stable and lowercase.
- Add source URLs and marker strings for `recon`.
- Keep required fields explicit.
- Add auth and verification notes when the market exposes them.
- Record whether repo URLs, pack URLs, and folder URLs produce different import scope in practice.
- Prefer broad compatibility notes over fragile reverse-engineering.
- If the market changed in a way that makes automation unsafe, downgrade it to `manual-web`.
