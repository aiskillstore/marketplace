# Agent discovery: llms.txt, MCP cards and readiness

> Part of the ai-crawler-readiness skill. Back to https://visdenda.com/skills/ai-crawler-readiness/SKILL.md.
> Read this when the task matches: What each discovery document proves, what it does not, and how to read a score.

## What the documents are for

- `llms.txt` — an optional map for agents: H1, one-line summary, link lists. Serve it as
  `text/plain` or `text/markdown`; an HTML page answering 200 is a soft 404.
- MCP server card plus OAuth discovery documents — tell a client how to reach the server
  and how to authorize. A card that points at a dead endpoint is worse than no card.
- `auth.md` — how a human or an agent obtains a credential.
- A2A agent card — what the agent does, its skills and its endpoint.
- None of these are ranking factors. They remove guesswork for clients that look for them.

## Checks in order

1. `visdenda_audit_site` with `focus=agent` — up to eight probes in one call, a 0–100
   score, and every failing or warning probe with a concrete fix.
2. The same tool with `focus=mcp` — server card, protected-resource and
   authorization-server metadata, `auth.md` and the A2A card.
3. `focus=llms` — one document: missing file, soft 404, missing H1 and broken links.
4. `focus=full` — meta, canonical, robots, sitemap, llms.txt, schema, hreflang and
   redirects; returns all findings with fixes and a seven-day report link.

## Interpret, do not worship the score

- A missing optional document is a decision. Say what the absence costs — an extra
  round-trip, or a client that cannot discover the server — before calling it a defect.
- A high score does not mean assistants cite the site; discovery is not usage.
- A low score with one broken critical document (a server card pointing at 404) matters
  more than several missing nice-to-haves.
