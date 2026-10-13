# Setting up access to BlackForge

This skill is a thin orchestration layer. It does not talk to the API directly — it drives one of
two clients that the user installs once. Read this when the user has neither the MCP tools nor the
`blackforge` CLI available, or asks how to get set up.

## Install the skill

The skill is distributed from GitHub and installed with the
[`skills`](https://github.com/vercel-labs/skills) CLI (GitHub is the registry):

```bash
npx skills add blackforge-so/skill        # into the current project's skills dir
npx skills add blackforge-so/skill -g     # or globally (user-level)
```

`skills` auto-detects the agent and installs into whichever skills directory it uses — `.claude/skills/`
or `.agents/skills/`. It works with any skills-compatible agent (Claude Code, Cursor, and others).
`npx skills list` shows what is installed. This is only the skill itself; you still need a data client
(MCP or CLI) and an API key, below.

## Get an API key

Every keyed call needs a **BlackForge API key**. Get one at **app.blackforge.so → API** (create a
key, copy the `bf_…` string). The key's plan decides which venues, columns and granularities are
returned, and the three gates behave **differently**:

- **Columns** degrade silently — unentitled ones are dropped and an `X-BlackForge-Columns-Omitted`
  header names them. Not an error.
- **Venues and intervals** are a hard **403** before any data is read (e.g. `5m` on a pro key,
  whose floor is `1h`).
- **History depth** is clamped **silently and unheadered** — a `from` earlier than the plan's
  window is moved forward and you simply get fewer points, with nothing saying so.

See the pricing tiers at blackforge.so/pricing.

The public API base is `https://api.blackforge.so/v1`. **Note the split:** `/v1` is part of the
route, not of the configured origin — see `BLACKFORGE_BASE_URL` below.

---

## Option A — MCP server (preferred)

The MCP server exposes the five `blackforge_*` tools this skill calls directly. Once configured,
the tools appear automatically and no shelling out is needed. Add a `blackforge` server that runs
`npx -y @blackforge-so/mcp` with `BLACKFORGE_API_KEY` in its environment. The config lives wherever
your agent keeps MCP servers — for example:

**JSON config** (e.g. an MCP-enabled desktop app or a project `.mcp.json`):

```json
{
  "mcpServers": {
    "blackforge": {
      "command": "npx",
      "args": ["-y", "@blackforge-so/mcp"],
      "env": { "BLACKFORGE_API_KEY": "bf_your_key_here" }
    }
  }
}
```

**Via a CLI helper** (e.g. an agent that exposes an `mcp add` command):

```bash
<your-agent> mcp add blackforge --env BLACKFORGE_API_KEY=bf_your_key_here -- npx -y @blackforge-so/mcp
```

Restart the agent. The tools become available as:

| tool | purpose | key params |
|---|---|---|
| `blackforge_catalog` | venues + 169 metric definitions | *(keyless — call first)* |
| `blackforge_symbols` | pairs a venue trades | `exchange` |
| `blackforge_latest` | latest closed 5-min bucket | `exchange`, `symbol`, `columns?` |
| `blackforge_series` | a metric over a time range | `exchange`, `symbol`, `metric`, `from`, `to`, `interval` |
| `blackforge_usage` | recent usage + rows remaining | *(none)* |

Optional env `BLACKFORGE_BASE_URL` overrides the **origin** for a local/dev server
(e.g. `http://localhost:3001/api`). It is the origin, **not** the `/v1` base above: both clients
append `/v1/...` themselves, so setting it to `https://api.blackforge.so/v1` makes every request
hit `/v1/v1/...` and 404. The default is `https://api.blackforge.so`.

---

## Option B — `blackforge` CLI (fallback)

Use this when the MCP tools are not configured but a shell is available. No install step is
required — `npx` fetches it on demand:

```bash
npx -y @blackforge-so/cli catalog
```

Or install once for the bare `blackforge` binary:

```bash
npm install -g @blackforge-so/cli
blackforge auth set-key bf_your_key_here   # stored at ~/.blackforge/config.json (mode 0600)
```

The key is read from (in order) `--api-key`, `$BLACKFORGE_API_KEY`, then the stored config.

Commands mirror the MCP tools:

```bash
blackforge catalog                                              # keyless: venues + metrics
blackforge symbols --exchange binance
blackforge latest  --exchange binance --symbol BTCUSDT [--columns price,downDepth5,askLiqRemoved]
blackforge series  --exchange binance --symbol BTCUSDT \
                   --metric downDepth5 --interval 1h \
                   --from 2026-07-01T00:00:00Z --to 2026-07-08T00:00:00Z --output json
blackforge usage
```

Global options: `--output table|json|csv` (default table on a TTY, json when piped), `--api-key`,
`--base-url`, `--verbose`. Add `--output json` when the result will be parsed rather than read.

---

## Response headers worth surfacing

Both clients pass through BlackForge's accounting headers. When present, use them to explain results:

- `X-BlackForge-Columns-Omitted` — columns dropped because they sit above the caller's plan. Tell
  the user which tier includes them; do not report the data as missing.
- `X-BlackForge-Rows-Remaining` — rows left in the monthly quota for this key.
- `X-BlackForge-Rows-Served` / `X-BlackForge-Blocks-Billed` — what this call consumed.

A `403` on a venue/interval means the plan does not include it — point the user to blackforge.so/pricing.
