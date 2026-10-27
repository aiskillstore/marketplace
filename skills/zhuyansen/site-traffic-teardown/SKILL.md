---
name: site-traffic-teardown
description: Competitor traffic and SEO teardown for any website, using AIsa data (Similarweb traffic and channel mix, Semrush keywords/backlinks/organic competitors, Ahrefs DR) for a few dollars instead of Ahrefs + Semrush subscriptions. Finds competitors, screens them by traffic, pulls a side-by-side table, then reads it into growth-engine types and 3 concrete opportunities. Use when the user asks to tear down / 拆解 competitors of a site, compare traffic of several sites, find out how a competitor gets traffic, "竞品流量", "竞品 SEO", "谁在抢我的流量", "这个站流量从哪来", or wants a cheap Ahrefs/Semrush-style competitor report. Needs the `aisa` CLI signed in (AISA_API_KEY).
---

# Site Traffic Teardown

Turn "who are my competitors and how do they get traffic" into one table plus three actions, for under $1 per domain.

## Preconditions

- `which aisa && aisa --version` and `aisa whoami`. If missing, tell the user to run `npm i -g @aisa-one/cli` then `aisa login`; do not install it unasked.
- Never print, log or write the API key. Never send the user's email anywhere.
- Every stage is **quote first** (free). Report the quote, then run. The script refuses a single call over `--max-call` (default $2) or a batch over `--max-total` (default $5); raise them only after the user OKs that quote. Report real charges (`customer_cost_micros_usd`) at the end of each stage.

## Workflow

Script: `scripts/teardown.py <stage> --target <domain> [--competitors a.com,b.com] [--month YYYY-MM] [--lang en|zh] [--run] [--out DIR]`. Without `--run` it only quotes. Pass `--lang zh` when the user writes Chinese. Each run writes `<stage>-<time>.calls.json`, `.results.json` and a `.md` summary into `--out`. Calls that fail to quote are dropped, not run.

1. **discover** (~$0.31): Semrush organic competitors + overview + 3-month visits of the target.
   Semrush competitors are noisy (sites that only share a few words). Keep the same-shape sites; also add obvious rivals from a quick web search or the user's own list — official/big players often don't show up.
2. **screen** (~$0.075 per domain): one month of visits per candidate. Keep 3–5: the biggest direct rival, the fastest grower, the closest keyword overlap, and anything the user names.
3. **full** (~$0.84 per domain, of which $0.225 is the 3-month trend): channel mix, 3-month trend, Semrush overview, backlinks, Ahrefs DR.
4. **keywords** (~$0.02 per domain): Semrush top organic keywords with landing URLs. Returns only the top ~20 rows — enough to see which page type earns traffic, not a full keyword list. Say so.
5. **Read and write up** — load `references/interpretation.md` and produce:
   - the comparison table (visits, trend, search/direct/social/referral %, DR, referring domains, Semrush keywords),
   - each site's growth-engine type,
   - 3 opportunities for the target, each tied to a number in the table,
   - data caveats that apply,
   - a cost line: quoted vs charged, per stage and total.

## Hard-won rules

- Similarweb: always `main_domain_only=false`. With the default `true`, subdomain traffic is dropped (seen: 29,580 vs 99,450 for the same site, 3.4x).
- Similarweb channel sources is the expensive call ($0.525). Geographies is $2.25 per call — only with explicit OK.
- Similarweb only queries whole domains. Sub-sections like `lobehub.com/skills` can't be isolated; use `get_semrush_url_organic_keywords` on the section URL and say it only covers that page.
- Semrush overview `us` is US-only and Similarweb is worldwide; expect big gaps on small or non-US sites. Report both, never average them.
- Monthly data lands after the month closes; use the last full month.
- Products without a public web market (installed inside an app/CLI) can't be measured by traffic; use GitHub stars or install counts instead and label it.
