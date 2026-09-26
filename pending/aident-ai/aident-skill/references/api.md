# OpenAPI Reference

Use the OpenAPI surface when an agent host needs raw HTTPS instead of the CLI or MCP. The CLI and MCP servers are wrappers around the same package operations.

## Base URLs

```text
https://loadout.aident.ai/api/openapi/loadout.json
https://loadout.aident.ai/api/openapi/loadout/operations
https://loadout.aident.ai/api/openapi/loadout/{operationId}
```

Use `AIDENT_BASE_URL` to target another Aident deployment:

```bash
export AIDENT_BASE_URL=https://your-server.example.com
```

## Getting A Token

Tokens are persisted to `~/.aident/credentials.json` after `aident login`. For direct HTTPS scripts, export the access token as `AIDENT_TOKEN`.

OAuth endpoints remain under the MCP OAuth namespace because MCP and OpenAPI use the same Aident OAuth server:

```text
POST /api/mcp/oauth/register
GET  /api/mcp/oauth/authorize
POST /api/mcp/oauth/token
POST /api/mcp/oauth/revoke
```

## Discover Operations

Fetch the Loadout OpenAPI document:

```bash
curl -H "Authorization: Bearer $AIDENT_TOKEN" \
  "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout.json"
```

Fetch compact operation metadata:

```bash
curl -H "Authorization: Bearer $AIDENT_TOKEN" \
  "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout/operations"
```

Operation IDs are stable and package-prefixed. Common Loadout operations:

| Operation ID                   | CLI equivalent                               |
| ------------------------------ | -------------------------------------------- |
| `loadout_capabilities_search`  | `aident capabilities search`                 |
| `loadout_capabilities_get`     | `aident capabilities get`                    |
| `loadout_capabilities_execute` | `aident capabilities execute`                |
| `loadout_vault`                | `aident vault status / connect / disconnect` |
| `loadout_audit`                | `aident audit recent / summary`              |

Use `loadout_capabilities_search` with `types: ["integration"]` to discover integrations; Loadout does not expose a
separate public integrations-list operation.

## Execute Operations

POST the command arguments directly to the operation URL.

```bash
curl -X POST "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout/loadout_capabilities_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AIDENT_TOKEN" \
  -d '{ "query": "send email", "limit": 5 }'
```

Execute a capability:

```bash
curl -X POST "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout/loadout_capabilities_execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AIDENT_TOKEN" \
  -d '{
    "name": "composio:gmail_tools:gmail_send_email",
    "input": { "to": "team@example.com", "subject": "Notes", "body": "..." }
  }'
```

Check Vault connection status:

```bash
curl -X POST "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout/loadout_vault" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AIDENT_TOKEN" \
  -d '{ "action": "status" }'
```

Audit recent Loadout action calls:

```bash
curl -X POST "${AIDENT_BASE_URL:-https://loadout.aident.ai}/api/openapi/loadout/loadout_audit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AIDENT_TOKEN" \
  -d '{ "action": "summary", "limit": 50 }'
```

Successful audit entries can include `resultFiles` with `type`, `downloadUrl`, and nullable `expiresAt`. Use those
download URLs to recover persisted files when an action response was interrupted. Asset IDs and raw provider output are
not part of the public audit response.

## Multi-Account Fields

Multi-account connections are a Pro feature. Pay-as-you-go users are limited to one connected account per integration and use that integration's default account. Only offer account selection when Vault or capability output confirms that multi-account fields are available.

For eligible Pro users:

- `loadout_capabilities_execute` accepts an optional top-level `accountAlias` field beside `name` and `input` to pin an Action to one connected account. When a side-effecting Action's integration has more than one active account, omitting it returns `account-selection-required` with the default-first account list.
- Successful Action execution results include `usedUserAccount`, the summary of the account that performed the Action.
- `loadout_vault` connect accepts `addAccount` or `accountAlias` with `replaceAccountConfirmed`; disconnect requires `accountAlias` when multiple accounts exist.

## Error Handling

| HTTP Status | Meaning                                                              |
| ----------- | -------------------------------------------------------------------- |
| 200         | Success. Check the returned `success` field.                         |
| 400         | Invalid request body or unsupported operation.                       |
| 401         | Invalid or expired token. Reauthenticate or refresh.                 |
| 403         | Authenticated account lacks the required package or operation scope. |
| 426         | CLI/client version is too old for this server.                       |
| 500         | Operation execution error. Check the returned `error` field.         |

## Advanced Overrides

| Variable          | Purpose                                                    |
| ----------------- | ---------------------------------------------------------- |
| `AIDENT_TOKEN`    | Skip credential file and use this Bearer token directly.   |
| `AIDENT_BASE_URL` | Override the default server (`https://loadout.aident.ai`). |

## Rate Limits

Standard rate limits apply. If rate limited, wait and retry with exponential backoff.
