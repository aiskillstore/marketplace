---
name: authorizing-api-requests
description: >-
  Use when authenticating or authorizing requests to any Mailtrap API
  (Email Send, Email Testing/Sandbox, Templates, Contacts, Sending Domains,
  Suppressions). Use when picking the auth header, choosing token scope,
  storing tokens safely, or resolving the Mailtrap account_id. Use before
  writing or generating any Mailtrap API call.
---

# Authorizing Mailtrap API requests

## Overview

Every Mailtrap API request needs **two things**:

1. An **API token** in an auth header — proves identity and carries the scope.
2. For account-scoped endpoints (most of them outside of the send hosts), an **`account_id`** in the URL path.

This skill is the single source of truth for both. Other skills (`sending-emails`, `testing-with-sandbox`, `using-email-templates`, `managing-contacts`, `setting-up-sending-domain`) reference these conventions instead of duplicating them.

## When to use

- Before writing any Mailtrap API call from code, scripts, CI, IaC, or an AI agent
- Picking which token scope and stream to provision
- Deciding where to store a token (env, secret manager, CI)
- Resolving the `account_id` for an account-scoped endpoint
- Debugging `401 Unauthorized` / `403 Forbidden` responses

## API tokens

Create tokens at **Settings** > [API Tokens](https://mailtrap.io/api-tokens) with the **smallest scope** that works:

- **Email Sending API** — for `send.api.mailtrap.io` and `bulk.api.mailtrap.io`. Scope per stream (transactional, bulk) when possible.
- **Email Testing API** — for the Sandbox (`sandbox.api.mailtrap.io`). Always separate from live sending tokens.
- **Account-level API** — for Contacts, Templates, Sending Domains, Suppressions, and other endpoints under `https://mailtrap.io/api/accounts/{account_id}/...`.

A single token can cover several scopes if the user has the right plan; prefer narrower tokens (one stream / one project / one product surface) so a leak has limited blast radius. Reference: [API tokens documentation](https://docs.mailtrap.io/email-api-smtp/setup/api-tokens.md).

## Auth headers (two equivalent forms)

Mailtrap accepts either header. Use Bearer in examples — it's the more common HTTP convention and matches most generated SDK code.

| Form                | Header                                       | When to use                                  |
| ------------------- | -------------------------------------------- | -------------------------------------------- |
| Bearer (preferred)  | `Authorization: Bearer $MAILTRAP_API_TOKEN`  | Default for new code, SDKs, curl examples    |
| Api-Token (legacy)  | `Api-Token: $MAILTRAP_API_TOKEN`             | Older clients or where Bearer is awkward     |

Do not send both at the same time. The same value goes in either header.

## Where to put tokens

- **Local dev:** environment variable, or `.env` file that is in `.gitignore`. Load with `direnv`, `dotenv`, or the framework's built-in mechanism.
- **CI / build:** the CI provider's encrypted secret store (GitHub Actions secrets, GitLab CI variables, CircleCI contexts). Inject as env vars only.
- **Production / staging:** a real secret manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault, Doppler, 1Password, etc.). Rotate on a schedule.
- **Agent / LLM workflows:** the host agent's secret store. Never paste a token into chat or a prompt.

Hard rules:

- **Never** hardcode a token in source, config, or notebooks.
- **Never** commit a token. If one lands in git, rotate it; history retention is forever.
- **Never** pass a token on the command line as a flag — it leaks into shell history, `ps`, and CI logs.
- **Never** let an LLM echo a literal token back into generated code. Use `$VAR_NAME` shell-var placeholders in all examples so generated code reaches for the env var, not the literal.
- **Never** mix sandbox and live tokens. A leaked sandbox key must not be able to send real mail.

## Recommended env var names

These names are used consistently across every other skill in this repo and across the example snippets below.

| Variable                     | Used for                                                                               |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| `MAILTRAP_API_TOKEN`         | General API: Email Send (transactional and bulk), Templates, Contacts, Sending Domains, Suppressions |
| `MAILTRAP_SANDBOX_API_TOKEN` | Sandbox / Email Testing (separate scope)                                               |
| `MAILTRAP_ACCOUNT_ID`        | Path parameter for account-scoped endpoints                                            |

If your environment uses different names, alias them once at startup so the examples in other skills work unchanged.

## Resolving `account_id` automatically

`account_id` is the integer prefix on every `https://mailtrap.io/api/accounts/{account_id}/...` endpoint. **Do not hardcode it.** It changes between environments, is different per organization, and is silently wrong when you copy a script to a teammate's account.

Resolve it once per session from the Accounts endpoint, which lists every account the token can access:

```bash
curl -s https://mailtrap.io/api/accounts \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN"
```

Response shape (array):

```json
[
  {"id": 12345, "name": "My Company", "access_levels": [1000]},
  {"id": 67890, "name": "Client Account", "access_levels": [100]}
]
```

`access_levels` values:

- `1000` — Account owner
- `100` — Admin
- `10` — Viewer (read-only on most endpoints)

One-liner to cache as an env var (pick the right account if the token can see more than one):

```bash
export MAILTRAP_ACCOUNT_ID=$(curl -s https://mailtrap.io/api/accounts \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" | jq '.[0].id')
```

Reference: [Accounts API](https://docs.mailtrap.io/developers/account-management/accounts).

## Quick reference

```bash
# Live sending (no account_id in path)
curl -X POST https://send.api.mailtrap.io/api/send \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'

# Account-scoped endpoint
curl "https://mailtrap.io/api/accounts/$MAILTRAP_ACCOUNT_ID/contacts/lists" \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN"

# Sandbox / Testing
curl -X POST "https://sandbox.api.mailtrap.io/api/send/$MAILTRAP_INBOX_ID" \
  -H "Authorization: Bearer $MAILTRAP_SANDBOX_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

## Common mistakes

| Mistake                                                       | Fix                                                                                                              |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Hardcoding the token in code, config, or a notebook           | Load from `$MAILTRAP_API_TOKEN` (env, `.env`, CI secret, secret manager); rotate the token if it ever leaked     |
| Passing the token as a CLI flag (`--token=...`)               | Use env vars; CLI flags leak to shell history, `ps`, and CI logs                                                 |
| Committing a token, then deleting it in a later commit        | History keeps the value forever — rotate the token immediately, do not just remove the file                      |
| Pasting a token into chat / prompt / issue                    | Treat chat as public; rotate if it happened                                                                      |
| Using the live `MAILTRAP_API_TOKEN` against the sandbox host  | Sandbox uses its own scope and `MAILTRAP_SANDBOX_API_TOKEN`; mixing them either fails or sends real mail by accident |
| Hardcoding `account_id`                                       | Resolve via `GET https://mailtrap.io/api/accounts` once per run and pass through `$MAILTRAP_ACCOUNT_ID`          |
| Picking the wrong account when the token can see several      | Filter the `GET /api/accounts` response by `name` or `access_levels` (1000 = owner) instead of `.[0]`            |
| Sending both `Authorization` and `Api-Token` headers          | Pick one (Bearer for new code); duplicating them is unnecessary and confuses some intermediaries                 |
| Using a viewer-scoped token for writes                        | Check `access_levels`; writes need 100 (admin) or 1000 (owner) for the relevant account                          |
