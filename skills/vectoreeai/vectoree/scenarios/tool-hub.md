# Tool Hub

Use this playbook for **S17–S19** and **C08**. Parent skill: `SKILL.md` in this folder (or https://raw.githubusercontent.com/VectoreeAI/vectoree-skills/main/skills/vectoree/SKILL.md)

Need a project API key first (`scenarios/connect.md`). The key must include scope `tools:*` (`link` adds it; older keys need a new `link`).

Tool Hub is **hosted MCP** (`search` + `extract`), billed from the org wallet. It is not Model Gateway, not ClawHub, and not `vectoree skills install`. Do not register `tavily_search` / `brave_search` aliases. Tool names are `search` and `extract`. Parameters are Tavily-shaped (`query`, `max_results`, `urls`); extra Tavily fields are ignored.

Prefer CLI ≥ 0.1.8 (`npx @vectoree/cli` so you are not stuck on an old global install).

---

## S17 / C08: add search, or switch search to Vectoree

Match what the developer said:

| They say | Do this |
|----------|---------|
| "帮我加一下搜索的能力" / add web search | Write Vectoree MCP. Keep unrelated MCP servers. |
| "搜索的能力切换到 vectoree" / replace Tavily / Brave / Exa | Write Vectoree MCP **and** drop those search servers (`--replace-search`). |

```bash
npx @vectoree/cli current
npx @vectoree/cli tools status
npx @vectoree/cli tools snippet --write --replace-search
```

`--write` defaults to Cursor: `.cursor/mcp.json`. Other clients:

```bash
npx @vectoree/cli tools snippet --write --client claude --replace-search   # .mcp.json
npx @vectoree/cli tools snippet --write --client vscode --replace-search   # .vscode/mcp.json
```

Print only (no file write):

```bash
npx @vectoree/cli tools snippet
```

Native MCP JSON (same shape Dashboard → Tool Hub shows):

```json
{
  "mcpServers": {
    "vectoree": {
      "type": "http",
      "url": "https://vectoree.ai/mcp",
      "headers": {
        "Authorization": "Bearer sk-ve-v1-..."
      }
    }
  }
}
```

stdio fallback if the client has no HTTP MCP:

```json
{
  "mcpServers": {
    "vectoree": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://vectoree.ai/mcp"],
      "env": {}
    }
  }
}
```

Put the token from `.vectoree/config.json` or `VECTOREE_API_KEY`. Never commit real keys. Add `.cursor/mcp.json` / `.mcp.json` to `.gitignore` if they contain the Bearer token (or use env substitution if the client supports it).

After writing: tell the developer to **restart** Cursor / Claude Code / VS Code so MCP reloads. Then call `search` with a short query. Do not invent a `tavily_*` tool.

Done when MCP lists `search` and `extract`, and a test `search` returns titles + URLs.

---

## Codex MCP (same C08, different file)

Do not replace the whole `~/.codex/config.toml` (C07 lives there). Backup first, then add:

```toml
[mcp_servers.vectoree]
url = "https://vectoree.ai/mcp"

[mcp_servers.vectoree.http_headers]
Authorization = "Bearer sk-ve-v1-..."
```

If this Codex build has no HTTP MCP, use `mcp-remote` instead of `url`. Remove other search MCP server tables (`tavily`, `brave`, …) when the developer asked to switch.

---

## S18: probe search / extract

These hit the REST tools API and **bill the org wallet**. Use them to verify the key, not as the agent's default search path. Runtime search should go through MCP `search`.

```bash
npx @vectoree/cli tools search "vectoree tool hub"
npx @vectoree/cli tools extract https://vectoree.ai
```

REST equivalents (same key): `POST {VECTOREE_API_URL}/api/tools/v1/search` and `/extract`.

Pricing (wallet): `search` is billed per request; `extract` per URL (max 5). If the call fails with wallet / billing 402s, **stop**. Send `{VECTOREE_API_URL}/dashboard/organization/billing` to the owner, or run `npx @vectoree/cli billing open`. Do not retry.

---

## S19: MCP connected / which tools?

```bash
npx @vectoree/cli tools status
```

Dashboard: Tool Hub (`/dashboard/tools`). Usage still lives in Organization → Billing until a tools usage CLI exists. Do not invent `tools usage`.

If `tools search` returns 401/403: the key is missing `tools:*`. Run `link` again (creates a new CLI key with that scope) or create a Dashboard API key with `tools:*`. `ik_` / `pk_` / `anon_` keys will not work.

---

## App code (optional)

Only if they want **their product** to call search, not just the coding agent:

1. Keep the key on the server. Do not put `VECTOREE_API_KEY` in a browser bundle.
2. `POST /api/tools/v1/search` with `{ "query": "..." }`.
3. Or point their agent's MCP config at `https://vectoree.ai/mcp` with the same Bearer key.

Done when either MCP tools work in the coding agent, or their server successfully probes `tools search`.
