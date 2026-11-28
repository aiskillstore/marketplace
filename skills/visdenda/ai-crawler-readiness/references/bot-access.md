# Bot access: robots, user agents and log evidence

> Part of the ai-crawler-readiness skill. Back to https://visdenda.com/skills/ai-crawler-readiness/SKILL.md.
> Read this when the task matches: What robots.txt decides per bot, why a 403 is not a block, and how to prove a hit.

## What robots.txt actually decides

- The matching group is the most specific user-agent token; `User-agent: *` is the fallback.
- Inside a matching group the longest matching `Allow`/`Disallow` rule wins; `*` and `$`
  are supported.
- `Crawl-delay` is not honored by Google. Treat it as advisory and check the crawler's
  own documentation.
- robots.txt is per scheme and host, at the root. A CDN/WAF block, a 401/403 or a JS
  challenge is a different gate: the bot never reaches robots.txt.
- `Sitemap:` lines help discovery. Their absence is not a block.

## Separate the agents before advising a block

The same vendor usually runs more than one agent: a training crawler, a search/index
crawler, and a user-triggered fetcher. Blocking the training token is not the same
decision as blocking the search token — one removes content from model training, the
other can remove it from answers and referrals. Confirm the current token names, user
agents and IP ranges from the directory record (`visdenda_get_ai_crawler`) instead of
memory; vendors rename and split agents.

## Prove that a bot actually hit the site

- A user-agent string is self-declared. Match it (`visdenda_match_user_agent`) to find
  candidates, then verify the source IP against the published ranges and reverse DNS.
- A 403/401 from a WAF looks identical to a robots block in aggregate analytics. Read the
  log line and the response body before naming a cause.
- A 404 is not a block: the bot fetched and the path is missing.

## Report

State the bot name and token, the deciding rule (or the non-robots gate), the path, the
status, the date and the evidence (log line or fetched file). Then give the one change
with the highest expected effect. "Blocked for training, allowed for search" is a
complete answer; "bad for AI" is not.
