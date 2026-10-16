---
name: orova-seo-check
description: "Website SEO check and backlink lookup using the public Orova SEO Check API: 90+ technical, content, speed and link checks in 12 groups, PageSpeed results, referring domains from the Common Crawl domain graph, and a shareable report link on orova.vn. No API key, no signup. Triggers on: SEO check, SEO audit, technical SEO, backlinks, who links to, referring domains, site health."
user-invokable: true
argument-hint: "check <url> | backlinks <domain>"
license: MIT
metadata:
  author: Orova
  version: "1.0.0"
  category: seo
  homepage: https://orova.vn/en/seo-check
---

# Orova SEO Check

Run a full SEO check of a website, or list the domains that link to it, through the public Orova API.
The scan runs on Orova servers; only the URL or domain is sent.

## When to use

- The user asks to check, audit or score the SEO of a site or page ("check SEO of example.com").
- The user asks about technical SEO, site health, security headers, sitemap/robots, PageSpeed or Core Web Vitals of a URL.
- The user asks who links to a domain, how many referring domains it has, or its backlink profile.

## How to run

The script is `scripts/orova_seo.py`, relative to this SKILL.md file. It needs Python 3.9+ and the standard library only.

```bash
# Full SEO check (30-90 seconds; the script polls every 3 seconds)
python3 "${CLAUDE_SKILL_DIR:-skills/orova-seo-check}/scripts/orova_seo.py" check https://example.com

# Vietnamese report link instead of English
python3 "${CLAUDE_SKILL_DIR:-skills/orova-seo-check}/scripts/orova_seo.py" check https://example.com --locale vi

# Referring domains only (1..100 rows)
python3 "${CLAUDE_SKILL_DIR:-skills/orova-seo-check}/scripts/orova_seo.py" backlinks example.com --limit 50

# Raw JSON for your own analysis
python3 "${CLAUDE_SKILL_DIR:-skills/orova-seo-check}/scripts/orova_seo.py" check https://example.com --json
```

If `CLAUDE_SKILL_DIR` is not set and the repo path does not resolve, use the absolute path of
`scripts/orova_seo.py` next to this file (for a manual install: `~/.claude/skills/orova-seo-check/scripts/orova_seo.py`).

Options: `--timeout 240` (seconds to wait), `--interval 3` (poll interval), `--base-url` (or env `OROVA_BASE_URL`).
Progress lines go to stderr; the report goes to stdout.

Exit codes: `0` ok, `2` network/HTTP error (including rate limit), `3` scan failed, `4` timed out
(the scan may still finish; give the user the report link printed in the message).

Code-to-label meanings for every check are in `references/checks.md`. Read it when the user asks what a check means.

## How to present results

Keep the script's Markdown structure and add a short plain-language summary:

1. Overall score `NN/100` and the scanned URL.
2. The 12-group table (Group, Score, Max).
3. Failed checks first, then warnings. For each, say in one sentence why it matters and how to fix it.
   Group fixes by effort when there are many (quick server/header changes vs. content work).
4. Passed checks: just the count.
5. Backlinks: referring domains, domain rank and the top referring domains table.
   Always say the data is domain-level from Common Crawl and may miss small sites; 0 does not prove there are no links.
6. The shareable report link: `https://orova.vn/en/seo-check?id=<id>` (or `/vi/` with `--locale vi`).

Do not invent numbers that are not in the output. If a group shows `skip` items (for example no images on the page),
say they were not applicable rather than failed.

## Limits

- Guests get 5 scans per hour per IP. Scanning the same domain again within 24 hours returns the cached result
  and does not use a scan.
- Backlinks lookups: 30 per hour per IP.
- On a rate limit the script prints how long to wait; the user can also open https://orova.vn/en/seo-check in a browser.
- Backlinks are domain-level, from Common Crawl (cc-main-2026-jul-aug-sep, about 133 million domains), and may miss small sites.
- A scan looks at the homepage plus a few sample pages, not the whole site.

For daily monitoring, Search Console insights and AI content tools, see Orova SEO: https://orova.vn/en/seo
