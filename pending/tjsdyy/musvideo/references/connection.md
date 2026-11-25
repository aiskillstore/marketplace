# Connecting MusVideo

Service: `https://musvideo.ai/api/mcp`, Streamable HTTP, OAuth with PKCE S256.
The client opens MusVideo sign-in and consent in the user's browser. Each person uses their own account. `mv.read` permits account, balance, project and video reads; `mv.create` permits imports and approved creation/render actions. Read-only setups cannot create videos.

- **Codex:** `codex mcp add musvideo --url https://musvideo.ai/api/mcp`, then `codex mcp login musvideo`. For a client that fails published-identity discovery, retry login with `--oauth-client-registration dcr` if that version supports it. Use `--no-browser` only for a headless terminal. Do not paste the authorization callback into the conversation.
- **Claude Code:** `claude mcp add --transport http musvideo https://musvideo.ai/api/mcp`, then `claude mcp login musvideo` (or `/mcp` in the interactive client). A plugin installation already supplies the server; choose that server in `/mcp` instead of adding a duplicate.
- **Claude web/Desktop/Cowork:** Settings → Connectors → Add custom connector, enter the service URL. Use **Register automatically** for the verified DCR path. Approve the MusVideo connection in the browser. A Code plugin or standalone Skill does not automatically create this account connector.
- **Cursor:** merge `{"mcpServers":{"musvideo":{"url":"https://musvideo.ai/api/mcp"}}}` into `.cursor/mcp.json` or the client's global MCP settings. Use its OAuth connect control.
- **VS Code/Copilot:** add the HTTP endpoint through Chat: Open Customizations → MCP Servers. The Copilot native configuration is `~/.copilot/mcp-config.json` or workspace-root `.mcp.json` with an `mcpServers` object. This is a configuration example; OAuth in VS Code has not been certified by this release.

After login, call `get_credit_balance` and `list_my_videos` before attempting creation. Never replace browser OAuth with a shared token. HTTP 401 means sign in/reconnect; HTTP 403 with `insufficient_scope` means reconnect with the required permission. Do not loop on login failures. Disconnect from the MusVideo account page to revoke the server-side connection; removing a local config alone may not revoke it.

MCP Apps cards depend on host support. Text results and watch URLs remain available. Local-file attachment support has only been verified in ChatGPT; other clients should supply a public audio URL.
