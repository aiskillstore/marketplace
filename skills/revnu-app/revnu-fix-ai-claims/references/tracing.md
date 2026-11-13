# Tracing a claim to its source

Goal: for each wrong, outdated or missing claim, name the page most likely
feeding it, with how sure you are. Stop once a source is confirmed; don't
open twenty pages to tick boxes.

## 1. Start from the answer's citations

If the answer listed sources, open each one and search the page for the
claim's key fact (the wrong price, the old name, the missing feature).

- Found on the page → **confirmed**. That page is the fix target.
- Page cites another page for the fact → follow one hop.
- Page no longer says it → the engine may be reading an older copy. Note the
  page's visible date and whether it changed recently (the user or the repo's
  git history may know). The fix is to wait and re-check, plus making sure
  the current version is crawlable.

API answers include citation URLs: the OpenAI API web search tool returns
`url_citation` annotations, and Gemini's Grounding with Google Search returns
URL citations (see sources.md). Neither is documented as identical to the
consumer app's answer.

## 2. The business's own pages

Look for the stale or conflicting fact on pages the user controls. In the
repo and on the live site:

- `grep -ri` the old price, old plan name, old product name, retired feature
  name across the repo's content and page source.
- Fetch the sitemap (`/sitemap.xml`, or the `Sitemap:` line in robots.txt) and
  look for old launch posts, archived pricing, `/v1/` docs and duplicate
  pricing pages that still return 200.
- Compare the server HTML with the rendered page. Fetch with a plain HTTP
  client and compare to what a browser shows. Facts that appear only after
  JavaScript runs may be missed by any fetcher that doesn't render; Google
  renders, but don't assume every AI crawler does.
- Check the page's `<title>`, meta description, Open Graph tags and JSON-LD:
  an old description often survives there after the body was updated.
- Check `llms.txt` if present, only to see whether it states an old fact. Its
  presence isn't evidence that any engine reads it.

## 3. Profiles and listings

Search `"<Name>" <site>` for the profiles buyers and engines commonly read:
G2, Capterra, TrustRadius, Product Hunt, Crunchbase, LinkedIn company page,
GitHub org and repo descriptions, npm or PyPI package descriptions, app
stores, Chrome Web Store, partner marketplaces, and directories in the
category. Old pricing and old taglines persist here longest because nobody
re-opens them.

For each, record: URL, the stale text, whether the business can edit it
(claimed profile) or must request a change.

## 4. Third-party writing

- Search the claim's most distinctive words in quotes ("no free plan" "<Name>")
  and the claim's paraphrase.
- Look at review articles, "best X" roundups, comparison pages ("X vs <Name>"),
  Reddit and Hacker News threads, YouTube video descriptions.
- An answer saying "users report it's hard to set up" usually traces to forum
  threads or reviews. That's an opinion: report it, and fix it only if there's
  a factual error inside it (an old setup step that no longer exists).

## 5. Namesakes

If the claims describe a different business (wrong founders, wrong country,
wrong category), search the name alone and with the claimed details. Record
the namesake's domain. Signs it's a namesake problem:

- the business's name is a common word or matches a better-known company,
  project, person or place;
- the claims are internally consistent but about someone else;
- the business has few independent pages, so the namesake's pages dominate.

## Confidence

| Level | Use when |
|---|---|
| Confirmed | You read the claim on that page, or the answer cited it for that claim |
| Likely | The page carries the old or adjacent fact and is the kind engines cite for this question |
| Not found | Nothing found after the steps above. Say so; the source may be training data from older pages |
