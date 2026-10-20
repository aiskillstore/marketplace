---
name: seo-new-keywords-research
description: Turn new AI names or unstructured AI market signals into a keyword priority table. For each name it finds the generic search terms downstream of it, screens them for relevance, and checks novelty, demand size and momentum against Google Ads volume and Google Trends, ending in prioritize, watch or skip. Use when the user has new model, product or repository names (or an AI listening report, a batch of posts, a changelog) and asks which keywords to build pages or tools for. Runs the new-term-radar command line; needs an AISA_API_KEY, and a GOANYAPI_API_KEY improves it.
---

# SEO new-keywords research

Input: names of new AI things, or raw text that mentions them. Output: one table, names and the generic terms behind them, each with a decision.

A name ("SynthID Detector") has a short life as a keyword and belongs to someone. The job it does ("ai image detector") is what people keep searching, and nobody owns it. You need both in the same table.

## Before you run anything

1. Find the radar: `$NEW_TERM_RADAR_DIR` if set, else `~/new-term-radar`; clone https://github.com/zhuyansen/new-term-radar there if missing. Run every command from that directory.
2. An AIsa key must be available, as `AISA_API_KEY` or from the AIsa CLI (`aisa login` stores it in `~/.aisa`): every lookup here is paid through it. Without it, stop and say so. A key comes from https://go.aisa.one/yansen-zhu.
3. `GOANYAPI_API_KEY` is optional (a key comes from https://goanyapi.com/r/ga-95708898fb). With it the table also holds what people really searched together with each name, and reads the bigger rows from one country's settled series. Without it, tell the user that a "flat" reading is weaker evidence (see below).
4. If there is no `config.json`, copy `config.example.json`.

## Step 1: pick the names

If the user gave names, use them. If they gave text (a listening report, posts, release notes), extract the names yourself:

- Keep names of specific models, products, tools and repositories. Drop companies alone ("Google"), common words, and features.
- Use the searchable form: lowercase, as people would type it, with its version when the version is the news ("nano banana 2.1"), without it when the family is ("photocraft").
- A repository's README is good evidence: note its `owner/repo`.
- Choose at most five, the newest and most specific first. Each name costs money and about a minute. Tell the user which you chose and which you left out.

## Step 2: say the cost, then run

About 0.05 USD a name plus 0.09 USD a call, and 40 to 90 seconds a name. State the estimate, then:

```bash
python -m radar keywords "photocraft" "synthid detector" --repo "photocraft=storytold/photocraft" --json
```

Drop `--json` for the Markdown table alone. Run one call with all the names, not one call per name: the 0.09 USD is per call.

## Step 3: read the result honestly

Each row has `phrase`, `kind` (`name` or `generic`), `names` (which name it sits behind), `new`, `per_day`, `started`, `peak_vs` and `bench_level`, `peak_day`, `momentum`, `now`, `decision`, `brand`, `source`, `trend_geo`, `evidence`, `volume`.

- **`per_day` is an estimate**, good to an order of magnitude. A generic term's comes from its own Google Ads volume moved along its Trends curve; a name's is sized against a benchmark keyword.
- **`now`**: `rising`, `holding`, `fading`, `flat`. A row with `trend_geo` was read from one country's daily data settled to yesterday. A row without it was read from a worldwide series whose last two days are discarded, and there a real move can read `flat`: say "no rise seen" for those rows, never "did not rise".
- **`brand` true** (⚠): the keyword carries someone else's brand ("photoshop alternative"). Keep it in the table and flag it; whether to use it is the user's legal and positioning call.
- **`source` "searched"** (🔎): people searched it together with the name. Stronger evidence than a phrase the model proposed.
- **A thin table is not a quiet market.** If the output's `posts_error`, `related_errors` or `country_errors` is set, a source failed: say which, and that the table holds less than it should.
- Names usually rise within days of release and may fade within a week. Generic terms move later and less, if at all. Do not present a name's spike as lasting demand.

## Step 4: deliver the priority table

One table, sorted prioritize, watch, skip:

| Keyword | Type | Behind | New? | Est. searches/day | Started rising | Momentum (7d) | Now | Page one | Decision | Why |

- Use the radar's `decision`, and add one short reason per row in your own words from the fields above (for example: "steady 2,500 a day, did not move on the release" or "rose 80% in the US for five days, still small").
- `competition` (rows that would be acted on): `verdict` open, mixed or crowded; `weak` = page-one results on sites rated under 30, the slots a new site can take; `kd`; `ads`; `weakest` (the site a new page can push past). A row with `demoted` was rising but moved to watch because page one is crowded: say so. In a name's first week page one is still forming; trust the second reading.
- Under the table: the long-tails of each name (`tails`), the other names found alongside (`cosearch`), then every caveat that applies: missing key, failed source, estimate quality.
- Then two or three lines of advice at most: which rows are worth a page or a tool now, and what to check again in a few days. Search volume data runs about two months behind; say so if the user is about to commit work to a number.

Do not invent rows, volumes or dates. If the radar returned nothing for a name, say that the posts showed no concrete use yet and offer to read it again in three days.
