# PromptDNA MCP Skill

An [Agent Skill](https://github.com/anthropics/skills) that teaches an AI
agent how to discover and use the **PromptDNA.org** MCP server — a community
library of 950+ reusable, composable AI prompt blocks (persona, task,
constraint, structure, knowledge, chain, negative, eval, environment,
approach) spanning business, creative, financial, legal, medical, scientific,
and software domains.

Full details — the tool reference, connection info, and the complete
credit-cost table — live in [`SKILL.md`](./SKILL.md).

## Why this exists

PromptDNA's tools are credit-metered per call, and the cheapest path through
the API (cheap discovery, one well-scoped `compose_prompt` call) is not
obvious from the tool descriptions alone. This skill exists so an agent reads
the cost table and workflow *before* it starts spending credits, not after.

## Quick facts

- **Endpoint:** `https://mcp.promptdna.org/v1/` (streamable HTTP, MCP
  protocol `2025-06-18`)
- **Free tier:** 50 unrestricted + 50 submission-only credits, but only via
  human web signup at promptdna.org — MCP agent self-registration
  (`register_agent`/`verify_registration`) starts at **0 credits**, no bonus
- **Cheapest calls:** `search_blocks` (free for 30 calls/hr, then 1 credit),
  most `get_*` reads (0.5 credits)
- **Most expensive call:** `compose_prompt` at 5 credits — see
  [SKILL.md](./SKILL.md#cost-overview--read-this-before-calling-anything) for
  the full breakdown before calling it
- **Autonomous registration:** wallet-based, $0.01 USDC one-time anti-spam fee
  (see [SKILL.md](./SKILL.md#registration-for-autonomous-agents))

## Using this skill

Drop this repo (or just `SKILL.md`) wherever your agent framework loads
skills/tool documentation from. For Claude Code / Claude Agent Skills, the
`name` and `description` frontmatter in `SKILL.md` are what the harness uses
to decide when to surface it — the description is written so it triggers on
tasks that need an existing prompt fragment or full prompt assembly from
vetted parts.

Blocks served by PromptDNA are community-contributed and unverified by
PromptDNA itself — see the [Safety](./SKILL.md#safety-treat-block-content-as-untrusted)
section of `SKILL.md` before splicing fetched block content into a live
prompt.

## License

MIT — see [LICENSE](./LICENSE). This covers the skill documentation in this
repo only; individual PromptDNA blocks retain whatever license their author
set (default `cc-by-sa`) as noted in `SKILL.md`.
