---
name: new-term-radar
description: One run from signal to decision. Finds the names of new AI models, products and repositories seen in the last 24 hours (X, Hugging Face, GitHub, sitemaps), then builds a keyword priority table for them, each new name and the generic search terms behind it, sized against Google Ads volume and Google Trends, with prioritize, watch or skip. Use when the user wants today's new AI keywords, an AI trend radar, or asks what new AI terms are worth building a page or tool for. Also takes names the user already has. Runs the new-term-radar command line; needs an AISA_API_KEY.
---

# New-term radar

The whole job in one run: collect what is new, then work out which keywords are worth acting on. If the user wants only the collection, or only the keyword research on names they already have, the split skills `ai-listening` and `seo-new-keywords-research` do each half.

## Before you run anything

1. Find the radar: `$NEW_TERM_RADAR_DIR` if set, else `~/new-term-radar`; clone https://github.com/zhuyansen/new-term-radar there if missing. Run every command from that directory. Python 3.10 or newer; nothing to install.
2. An AIsa key must be available, as `AISA_API_KEY` or from the AIsa CLI (`aisa login` stores it in `~/.aisa`): the X posts, the search volumes, Google Trends and the models all go through it. Without it, stop and say so. A key comes from https://go.aisa.one/yansen-zhu.
3. `TRUSTMRR_API_KEY` is optional: with it the weekly ⑥ revenue signal reads the products people pay for that grow fastest (TrustMRR). Its leads are for the user's own research: TrustMRR's terms forbid republishing the data, so never paste the product list into anything public.
4. `GOANYAPI_API_KEY` is optional (a key comes from https://goanyapi.com/r/ga-95708898fb). With it the table also holds what people really searched together with each name, and reads the bigger rows from one country's settled series. Without it, tell the user a "flat" reading is weaker evidence.
5. If there is no `config.json`, copy `config.example.json` and tell the user they are on the example list of X accounts and sitemaps.

## Choose the path

**The user has names already** ("research PhotoCraft and SynthID Detector"): skip collection.

```bash
python -m radar keywords "photocraft" "synthid detector" --repo "photocraft=storytold/photocraft" --json
```

About 0.05 USD a name plus 0.09 USD a call, 40 to 90 seconds a name, eight names at most. One call for all the names.

**The user wants today's new terms**: run everything.

```bash
python -m radar daily --out report.md
```

With the example config this is about 0.30 USD and 10 to 15 minutes: it reads every X account in `config.json` (0.003 USD and 10 seconds each), finds breakout repositories and new sitemap pages, scores which terms are names, then builds the keyword table for up to five of the day's names. It writes `report.md` and `report.json`.

Say the cost and the time before either command, and do not run `daily` twice in a row: the second run reports only what changed since the first.

The first `daily` run on a machine only builds snapshots, so it reports GitHub breakouts and little else. Say so; do not present it as a quiet day.

On Mondays (or with `--asks`) `daily` also reads what people asked for on Reddit that week (⑦, about 0.12 USD): jobs an AI tool could do, sized and checked for room on page one. It also lists the sites that just put up a payment link (⑧, Stripe, Polar, Lemon Squeezy, Gumroad, Creem; about 0.25 USD): new products people already pay for, AI and software first. A payment link means the site sells, not that it sells well. With `--revenue` and a `TRUSTMRR_API_KEY` it reads the products people pay for (⑥).

**The user wants to know what people complain about for a kind of tool** ("what's wrong with AI headshot tools?"):

```bash
python -m radar pains "ai headshot" --json
```

About 0.05 USD and a minute or two. It reads low-star Chrome Web Store reviews (needs `GOANYAPI_API_KEY`), Reddit complaints and comments under tutorial videos, and returns `gaps`: each with `gap`, `kind` (missing, too hard, quality, price, wants a tool), `count`, `phrase` (what someone with the problem would search) and `quotes` with links. Counts are of what was read, not of the market. App Store, Google Play and Trustpilot reviews are not reachable, and the radar does not read There's An AI For That or Facebook groups; say so if the user expects them.

## Read the result honestly

From `report.json`: `leads` are the day's names (with `kinds`, `signals`, `named`, `examples`, `posts`), `keywords` is the keyword table (`rows`, `tails`, `cosearch`, and the error fields). From `keywords --json` the table is the whole output.

Each table row: `phrase`, `kind` (`name` or `generic`), `names` (the name it sits behind), `new`, `per_day`, `started`, `peak_day`, `momentum`, `now`, `decision`, `brand`, `source`, `trend_geo`, `evidence`.

- `per_day` is an estimate, good to an order of magnitude.
- `now` is `rising`, `holding`, `fading` or `flat`. A row with `trend_geo` was read from one country's daily data settled to yesterday. A row without it was read from a worldwide series whose last two days are discarded, where a real move can read `flat`: for those rows say "no rise seen", never "did not rise".
- `brand` true (⚠): the keyword carries someone else's brand. Keep it, flag it; using it is the user's call.
- `source` "searched" (🔎): people searched it together with the name. Stronger than a phrase the model proposed.
- If `posts_error`, `related_errors` or `country_errors` is set, or a signal's block in `report.json` holds `error`, a source failed. Say which, and that the result holds less than it should. A thin table is not a quiet market.
- If `keywords.names` is empty, no lead today was a thing with a name score of 0.8 or more. Say that; offer to run `keywords` on a name the user picks from the leads.
- Names usually rise within days of release and may fade within a week. Generic terms move later and less, if at all.

## Deliver

1. **Today's new names** (skip this part on the names-given path): strongest first, each with what it is in a few words from the examples, where it was seen with the number that shows its strength, and one link.
2. **The priority table**, sorted prioritize, watch, skip:

   | Keyword | Type | Behind | New? | Est. searches/day | Started rising | Momentum (7d) | Now | Page one | Decision | Why |

   Use the radar's `decision` and add one short reason per row from the fields above.
   `competition` (rows that would be acted on): `verdict` open, mixed or crowded; `weak` = page-one results on sites rated under 30, the slots a new site can take; `kd`; `ads`; `weakest` (the site a new page can push past). A row with `demoted` was rising but moved to watch because page one is crowded: say so. In a name's first week page one is still forming; trust the second reading.
3. **Under the table**: each name's long-tails (`tails`), other names found alongside (`cosearch`), then every caveat that applies: missing key, failed source, first run, estimate quality.
4. **Two or three lines of advice**: which rows are worth a page or a tool now, and what to look at again in a few days. Search volume data runs about two months behind; say so if the user is about to commit work to a number.

Do not add names, rows, volumes or dates from your own knowledge. The output is what the radar saw.
