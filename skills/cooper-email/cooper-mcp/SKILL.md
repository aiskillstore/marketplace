---
name: cooper-mcp
description: Connect or troubleshoot the hosted Cooper Email MCP server (https://cooperemail.com/mcp) in Cursor, Claude Code, Claude.ai, ChatGPT, VS Code, Windsurf, Codex, or any Streamable HTTP MCP client. Use for installation, OAuth sign-in, Bearer API-key headers, 401 errors, or missing tools. Do not use when the connection already works and the user just wants to send, read, or manage mail; use the sibling Cooper skills for that.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com/docs/mcp
---

# Cooper Email MCP

Hosted Streamable HTTP server (no local process):

```text
https://cooperemail.com/mcp
```

`/api/mcp` is an alias. The server publishes 61 tools today; clients read the
live catalog, so do not depend on a copied count.

## Cursor (this plugin)

The plugin registers the server with the bare URL. Cursor signs in with
OAuth 2.1 + PKCE the first time a tool needs auth: on Cooper's consent screen
you can create a new inbox or paste an existing key. No key goes in the config.

To use an API key instead (scripts, or a client without OAuth), add the server
to `.cursor/mcp.json` or `~/.cursor/mcp.json` with a header:

```json
{
  "mcpServers": {
    "cooper-email": {
      "url": "https://cooperemail.com/mcp",
      "headers": { "Authorization": "Bearer ${env:COOPER_API_KEY}" }
    }
  }
}
```

Keys start with `coop_live_`. Keep them in an environment variable or secret
store, never in a committed file or in chat.

## Other clients

- Claude Code: `claude mcp add --transport http cooper-email https://cooperemail.com/mcp`
  (add `--header "Authorization: Bearer $COOPER_API_KEY"` to use a key), or the
  plugin: `/plugin marketplace add cooper-email/cooper-email`, then
  `/plugin install cooper-email@cooper-email`.
- Claude.ai and Claude Desktop: Settings, Connectors, Add custom connector.
  Name `Cooper Email`, URL `https://cooperemail.com/mcp`, then connect (OAuth).
- ChatGPT: connect through the public Cooper Email listing, or add the MCP URL
  with OAuth.
- VS Code, Windsurf, Codex, Goose: copy-paste configs at
  https://cooperemail.com/integrations

## No account yet

`cooper_onboard` needs no auth. It creates an account, one
`username@cooperemail.com` inbox, and an API key shown once. With OAuth, the
consent screen does the same thing.

## Verify

1. Reload Cursor (Developer: Reload Window) or start a new session.
2. Check the MCP status in Cursor settings and finish sign-in.
3. Call `cooper_whoami` (shows `auth_type` oauth or api_key) and
   `cooper_list_inboxes` as read-only smoke tests.

## Troubleshoot

- 404: the URL is missing `/mcp`.
- 401 with "needs an OAuth access token or Authorization: Bearer": the
  connection is not signed in. Finish OAuth, set the header, or call
  `cooper_onboard`.
- "API key or OAuth access token is not recognized": the key is wrong,
  revoked, or expired, or `COOPER_API_KEY` was not visible to the client
  process. Reconnect with OAuth, or mint a new key from a working session over
  HTTP (`POST /api/v1/keys`) so the secret stays out of the chat.
- 403 `permission_denied`: the key is limited to one inbox or a permission
  list; `cooper_whoami` shows the scope.
- Discovery: `/.well-known/oauth-protected-resource`,
  `/.well-known/oauth-authorization-server`, `/.well-known/mcp.json`, and the
  catalog at `/api/v1/mcp/tools`.

Docs: https://cooperemail.com/docs/mcp · https://cooperemail.com/llms.txt
