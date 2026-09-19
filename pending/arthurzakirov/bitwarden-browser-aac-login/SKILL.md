---
name: bitwarden-browser-aac-login
description: Use Bitwarden Agent Access CLI (`aac`) with agent-controlled browser login flows. Use when a user wants an AI agent to log into a website through `aac listen`/`aac run`, approve credentials in Bitwarden Agent Access, fill browser login forms without printing passwords, debug Agent Access browser login pairing, or build a credential-conscious bridge between `aac run` env injection and browser automation.
---

# Bitwarden Browser AAC Login

## Contract

Use Agent Access only as an approved, domain-scoped credential handoff.

- Never ask the user to paste passwords, TOTP codes, API keys, cookies, session values, rendezvous codes, or full credential JSON.
- Never run commands that print `AAC_USERNAME`, `AAC_PASSWORD`, `AAC_TOTP`, environment dumps, shell history, cookies, or auth-capable files.
- Treat `aac run --env-all` as sensitive: credentials are available to the child process and any code path that receives them.
- Prefer a credential-blind helper that uses credentials without exposing them to the agent. If the practical path routes credentials through agent-controlled code in memory, say that clearly before use.
- Confirm the exact target domain before requesting real credentials. Approve only the domain the user expects.
- Stop before account creation, final submission, payment, permission grants, or sensitive form submission unless the user confirms at action-time.

## Workflow

1. Verify local prerequisites without reading secrets:

   ```bash
   command -v aac
   aac connections list
   ```

   Do not inspect Bitwarden vault data or environment variables.

2. Make sure the user has `aac listen` open, unlocked, and ready to approve requests. If no cached connection exists, have the user pair locally; do not ask them to paste rendezvous codes into chat.

3. Use the available browser-control tool to open the target login page and inspect only the visible form shape. Identify stable locators for the username/email field, password field, and submit button.

4. Request credentials with `aac run --domain <domain> --env-all -- <helper>`, where `<domain>` is the registrable or site-specific domain shown to the user for approval.

5. Fill and submit the login form without logging the credential values. After submission, verify success from page state such as URL, title, greeting, logout link, or the next workflow step.

6. Report only non-secret status: success, domain requested, page reached, or sanitized error type.

## Recommended Pattern

For agent-controlled browsers, the reliable pattern is to keep the browser-control execution active while `aac run` is waiting for user approval:

1. In the active browser-control execution, validate that the login locators are unique.
2. Start a temporary server bound to `127.0.0.1` on a random port.
3. Spawn `aac run --domain <domain> --env-all -- node -e '<small helper>'`.
4. The helper reads `AAC_USERNAME` and `AAC_PASSWORD`, sends them to the temporary local server, and exits.
5. The active browser-control execution receives the values in memory, fills the fields, clicks login, closes the server, and returns only sanitized status.

Read `references/browser-bridge.md` before implementing this pattern.

## Failure Modes

- `No cached connections found`: the user needs to pair the remote client with `aac listen`; do not ask for a pasted token.
- `Request denied`: the user denied approval, the domain was wrong, or no matching vault item exists.
- Login page stays unchanged: inspect visible validation errors and check whether the helper exited, but do not print credential values.
- Background bridge receives credentials but does not fill the page: keep the browser-control call alive; do not rely on browser actions from an async callback after the tool call returns.

## Sanitization

When documenting or saving workflows, replace real values with placeholders:

- Domains: `example-app.test`
- URLs: `https://example-app.test/login`
- Names and emails: `user@example.test`
- Account labels: `Example Account`
- Rendezvous codes: `[rendezvous-code]`
- Fingerprints, session ids, contract ids, or item ids: `[id]`

Do not commit local application URLs, account names, email addresses, rental/application data, secrets, or transcript snippets that contain user-specific details.
