# blackforge — agent skill

An [agent skill](https://github.com/vercel-labs/skills) that teaches any skills-compatible coding
agent (Claude Code, Cursor, and others) to answer crypto **market-data** questions by orchestrating
the [BlackForge](https://blackforge.so) MCP tools (preferred) or the `blackforge` CLI. It is a thin
orchestration + interpretation layer — it never reimplements the API.

BlackForge stores one wide row per `(exchange, symbol)` per closed 5-minute window — 169
measurement columns (order-book depth and depth walls, order-ladder rungs, resting-liquidity
add/withdraw, price-level lifetime, trade timing, outsized-trade counts, market-cap and attention
enrichment, and a per-row quality bitmask) across 9 spot exchanges and 14,000+ spot pairs. The skill knows
that vocabulary and the discover → pick → call → interpret playbook, and it frames every returned
column as a **measurement** with a definition, never as a trade call.

## Install

Install with the [`skills`](https://github.com/vercel-labs/skills) CLI — GitHub is the registry:

```bash
npx skills add blackforge-so/skill        # into this project's skills dir
npx skills add blackforge-so/skill -g     # or globally (user-level)
```

`skills` installs into whichever skills directory your agent uses (`.claude/skills/` or
`.agents/skills/`) and detects the agent automatically. Then configure access — either the
BlackForge MCP server (preferred) or the `blackforge` CLI — and get an API key at
**app.blackforge.so → API**. See [`references/setup.md`](references/setup.md).

## Contents

| Path | What |
|---|---|
| `SKILL.md` | The skill: frontmatter trigger `description` + the playbook |
| `references/metrics-glossary.md` | All 169 metrics grouped by family, each with its measurement definition and min plan |
| `references/setup.md` | How to install the skill, configure the MCP server or CLI, and get an API key |
| `scripts/latest-json.sh` | Optional CLI wrapper: dump the latest bucket for a pair as JSON |
| `scripts/check-catalog-sync.mjs` | Fails if these docs disagree with the live catalog — run it before publishing |
| `evals/trigger-eval.json` | Trigger eval set (should / should-not queries) for description tuning |

## Source of truth

This GitHub repo is the versioned source. `npx skills add blackforge-so/skill` installs a copy into
your agent's skills directory — regenerate it from here rather than editing the installed copy.

**Run this before you publish a change:**

```bash
node scripts/check-catalog-sync.mjs
```

It reads the public catalog — no key, no sibling checkout — and fails if the glossary has gained
or lost a metric, if any documented unit or min plan disagrees with the live one, if a family's
count is wrong, or if any prose here states a column count that is not real. It exits non-zero
when the catalog cannot be reached, rather than reporting success against a source it never read.

This exists because the count has drifted three separate times across the product, and because a
glossary that has silently lost one row looks exactly like a complete one. `baseAsset` went
undocumented here from the day migration 007 added it until 2026-07-28.
