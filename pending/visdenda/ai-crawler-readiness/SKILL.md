---
name: ai-crawler-readiness
description: "Verify that AI crawlers and assistants can actually reach and read a site, audit one page against the current public checks, and prove what changed since the last scan: re-run a full audit of the same URL with compareTo for added, resolved and persisting findings plus the score delta. Checks cover robots.txt per bot (GPTBot, ClaudeBot, PerplexityBot), sitemap.xml, llms.txt, MCP discovery and agent readiness. Use when the question is AI visibility, bot blocking, llms.txt, sitemap, MCP discovery or agent access — or whether a fix actually worked. No API key."
license: CC-BY-4.0
compatibility: Requires an MCP client with Streamable HTTP; no credentials.
metadata:
  version: "2026-11-23.1"
---

# ai-crawler-readiness

> Anonymous checks for the AI-facing surface of a site. Endpoint: https://visdenda.com/v1/mcp/free
> (Streamable HTTP, no Authorization header). Tool names are prefixed `visdenda_`.
> Nothing here reads Search Console or account history; that needs a key — see
> https://visdenda.com/mcp.

## When to use

- "Can ChatGPT / Claude / Perplexity read this site?"
- "Why is GPTBot blocked, and what does robots.txt say per bot?"
- "Do we have llms.txt, and is it shaped right?"
- "Is our sitemap or robots.txt valid?"
- "Is our MCP server / agent card / auth.md discoverable?"
- "Score how agent-ready this site is" or "scan this one page".

## Do not use

- Do not use it to prove AI citations, AI traffic or rankings: it checks access and
  discoverability, not whether an assistant cited the page.
- Do not report a blocked bot as "invisible to AI" without naming the bot and the rule.
- Do not loop the network tools or the scan: five network checks, three scans and five
  account hand-offs per IP per day.

## Endpoint and limits

- https://visdenda.com/v1/mcp/free — anonymous, rate-limited per IP.
- Directory reads 100/day, network checks 5/day, single-page scans 3/day, account hand-offs
  5/day, 30 requests/minute.
- These are per-IP numbers. On a shared egress (for example, a hosted assistant) an aggregate
  cap can answer 429 sooner; stop and report the retry time.
- A 429 is a limit, not an error to retry; read `Retry-After`. Invalid arguments and inner
  quota denials do not use up the daily quota, so fix the call and retry once.
- The server advertises prompts `audit-agent-access` and `check-crawler-access`, plus the
  resource `visdenda://crawlers.json`.
- A 503 `MCP_DISABLED` on `tools/call` means the endpoint is switched off; report it and stop.

## Start here

1. `visdenda_audit_site` — the single audit entry. `focus=agent` (or `focus=mcp` for the
   MCP/OAuth surface) returns a 0–100 score and every failing or warning probe with a
   concrete fix; `focus=signals` covers canonical, noindex, meta, hreflang and structured
   data; `focus=robots`, `focus=sitemap` and `focus=llms` check one document each; the
   default `focus=full` runs the complete one-page scan and returns all findings, fixes,
   a seven-day report link and the `scanId` used by `compareTo` (it consumes one of the
   three daily scans).
2. `visdenda_check_crawler_access` — robots.txt per crawler, the deciding rule and
   crawl-delay, from one fetch. With exactly one crawler, `probe: true` also fetches the
   page as that agent to catch a CDN/WAF block. Pass `paths` for extra same-origin URLs
   and `probeUserAgent` to test a specific (including forged) user-agent.
3. `visdenda_search_ai_crawlers` and `visdenda_get_ai_crawler` — the directory record:
   current tokens, user agents, reverse-DNS suffixes, published IP ranges and review date.
4. `visdenda_match_user_agent` and `visdenda_verify_crawler_ip` — turn a log line or a
   source IP into evidence instead of trusting a self-declared user-agent.
5. `visdenda_connect_account` — only when the user wants monitoring, history or Search
   Console data; the free tools are one-shot.

## Public knowledge

`search` and `fetch` are the two unprefixed free tools: hosted assistants require those
exact names. Use `search` for citation-backed research over the public knowledge library,
then `fetch` with one result id. They read public material only; account data still needs
`visdenda_connect_account`.

## Verify a fix

A full audit is the only mode with a baseline. It returns a `scanId`; the report link lasts
seven days, while the comparison baseline is kept for 90 days.

1. Run `visdenda_audit_site` with `focus=full` on the exact URL and keep the `scanId`.
2. Let the user make the change.
3. Run the same call again on the same URL with `compareTo: "<scanId>"`. The field applies
   to `focus=full` only; focused modes return no comparison.
4. Report `compare.added`, `compare.resolved` and `compare.persisting` — each item has a
   `check`, a `status` and a `summary` — plus `compare.scoreDelta`, `compare.previousScore`
   and `compare.unchanged`. If `compare.truncated` is true, say the lists were capped.

A `warn` counts as an open finding, so it moves between the three lists the same way a
failure does. A check that disappeared counts as resolved only when its previous status
was `warn` or `fail`. Two full audits spend two of the three daily scans; an unknown,
expired or different-URL `compareTo` returns an error before the scan quota is charged.
Read the three lists, not only the score: a fix can resolve a real defect and still add a
warning. A focused check (for example `visdenda_check_crawler_access` for a robots change)
reports the current state but never a delta.

## Example

"We changed robots.txt — did it work?"

1. Re-run `visdenda_audit_site` with `focus=full` on the same URL and
   `compareTo: "<scanId from before the change>"`.
2. Report the robots finding under `compare.resolved`, anything still under
   `compare.persisting`, and `compare.scoreDelta`.
3. If robots still fails, `visdenda_check_crawler_access` with the crawler name and
   `probe: true` shows the deciding rule and the page as that bot sees it — one network
   check instead of another daily scan.

## Discovery loop

- Run `visdenda_audit_site` with `focus=mcp` for the server card, OAuth discovery
  documents, `auth.md` and the A2A agent card; every failing finding carries its fix.
- A missing optional document is a decision, not automatically a defect. Say what the
  absence costs before calling it a finding.

## Hand-off

- Report what is blocked (bot + rule + evidence), what is missing (document + why it
  matters), the readiness score with its failing findings, and the one fix with the
  highest expected effect. Then re-run the same audit with `compareTo` so the result is a
  delta, not a fresh impression.
- When findings remain, the result's `nextActions` points at
  `visdenda_connect_account`; use it only if the user wants monitoring or GSC data.

## References

- [Bot access: robots, user agents and log evidence](https://visdenda.com/skills/ai-crawler-readiness/references/bot-access.md) — What robots.txt decides per bot, why a 403 is not a block, and how to prove a hit.
- [Agent discovery: llms.txt, MCP cards and readiness](https://visdenda.com/skills/ai-crawler-readiness/references/agent-discovery.md) — What each discovery document proves, what it does not, and how to read a score.
- [Sitemap and robots.txt: what each verdict actually proves](https://visdenda.com/skills/ai-crawler-readiness/references/sitemap-and-robots.md) — Read sitemap and robots results as two axes — structure and policy — and know which tool answers which.
- [Page signals and changes over time](https://visdenda.com/skills/ai-crawler-readiness/references/page-signals-and-changes.md) — Choose between focused signals and a full scan, then prove whether a fix actually changed the verdict.

## Upgrade path

Owned-site history — Search Console windows, audit runs, indexing coverage, AI-crawler
fetches with paths — needs a scoped key: https://visdenda.com/mcp. The same surface, plus
`get_site_insights` and its drill-downs. Connect an account with
`visdenda_connect_account` when the user is ready to approve a six-digit code. It needs
the account owner's email and is not idempotent: call it once per attempt and do not retry
on timeout.
