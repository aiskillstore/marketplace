---
name: fiverr-gig-and-seller-sitemap-directory-scraper
description: "List live Fiverr gigs, seller profiles, categories, search tags and Logo Maker ideas straight from Fiverr's own directories, with best-effort full gig detail by URL. Output fields: title, gigUrl, priceMin, priceMax, rating and more, as JSON rows. Use it for requests like \"Fiverr gig scraper\", or a CSV/JSON export of public Fiverr data."
---

# Fiverr Gig & Seller Sitemap Directory Scraper

List live Fiverr gigs, seller profiles, categories, search tags and Logo Maker ideas straight from Fiverr's own directories, with best-effort full gig detail by URL.

- Actor: https://apify.com/vexaloom-labs/fiverr-gig-and-seller-sitemap-directory-scraper (ID `vexaloom-labs~fiverr-gig-and-seller-sitemap-directory-scraper`)
- n8n workflow for the same Actor: https://github.com/bolvein-firex/scraping-n8n-workflows/blob/main/docs/fiverr-gig-and-seller-sitemap-directory-scraper.md
- Example input: `references/example-input.json`
- Input schema: `references/input-schema.json`
- Output fields: `references/output-fields.json`

## When to use

Use this skill when the user wants:

- Fiverr gig scraper
- a repeatable export of public Fiverr data as CSV or JSON

Do not use it for private, login-protected or paywalled data.

## What it returns

One JSON row per result. Columns from the Actor's dataset schema:

- `title`: Title
- `gigUrl`: Gig Url
- `sellerUsername`: Seller Username
- `sellerLevel`: Seller Level
- `category`: Category
- `subCategory`: Sub Category
- `priceMin`: Price Min
- `priceMax`: Price Max
- `currency`: Currency
- `rating`: Rating
- `reviewsCount`: Reviews Count
- `sellerCountryCode`: Seller Country Code

All 14 declared fields: `references/output-fields.json`.

## Inputs

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `mode` | string | yes | sitemapDirectory | What to run. `search` searches Fiverr by keyword or browses search/category URLs. `gigDetails` fetches full details for gig URLs. `sellerProfiles` fetches seller profiles. |
| `searchQueries` | array | no | [] | Keywords to search on Fiverr (mode=search), e.g. `logo design` or `voice over`. One search is run per query. |
| `searchUrls` | array | no | [] | Fiverr search or category URLs to browse (mode=search), e.g. `https://www.fiverr.com/search/gigs?query=logo%20design` or a `/categories/...` URL. |
| `gigUrls` | array | no | [] | Full Fiverr gig URLs to fetch, e.g. `https://www.fiverr.com/username/gig-slug` (mode=gigDetails). |
| `sellerUrls` | array | no | [] | Fiverr seller usernames or profile URLs, e.g. `michael7878` or `https://www.fiverr.com/michael7878` (mode=sellerProfiles). |
| `sitemapType` | string | no | gigs | Which Fiverr sitemap directory to list (mode=sitemapDirectory). |
| `searchKeyword` | string | no |  | Only keep sitemap entries whose URL or slug contains this keyword (mode=sitemapDirectory). Also filters gig titles in detail and search modes when set. Case-insensitive. |
| `maxShards` | integer | no | 1 | Number of sitemap shard files to scan for gigs (up to 7), sellers (up to 6) or tags (up to 2). Values above the available shard count are capped. |
| `categoryLevel` | string | no |  | Only keep category entries at this level (mode=sitemapDirectory, sitemapType=categories). |
| `ideaType` | string | no |  | Only keep Logo Maker entries of this type (mode=sitemapDirectory, sitemapType=logomakerIdeas). |
| `category` | string | no |  | Only keep results in this Fiverr category. Applies to category directory entries, and to gig details and enriched search results when the page reports that category slug. |
| `sortBy` | string | no | relevance | Sort live search results (mode=search). |
| `sellerLevels` | array | no | [] | Keep only these seller levels (mode=search). Values: `top_rated_seller`, `level_two_seller`, `level_one_seller`, `na` (new seller). Leave empty for all levels. |
| `sellerLanguages` | array | no | [] | Keep only sellers who speak these languages (mode=search), using ISO codes such as `en`, `es`, `de`, `fr`, `hi`, `ur`. |

19 more optional fields on the Actor's Input tab.

Example (`references/example-input.json`):

```json
{
  "searchQueries": [
    "logo design"
  ],
  "searchKeyword": "logo",
  "maxPagesPerQuery": 1,
  "maxItems": 25,
  "mode": "sitemapDirectory"
}
```

The input passes the Actor's input schema (checked at every publish). First run: `maxItems` = 25, small enough for the 300-second sync wait; raise it once the rows look right.

## Run it

Set `APIFY_TOKEN`, then call the synchronous endpoint for small and medium runs (it waits up to 300 seconds):

```bash
curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~fiverr-gig-and-seller-sitemap-directory-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @references/example-input.json > output.json
```

Or with Node 18+: `node scripts/run.mjs [input.json]`.

For large runs, start an async run and read its dataset when it finishes:

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/vexaloom-labs~fiverr-gig-and-seller-sitemap-directory-scraper/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d @references/example-input.json)
RUN_ID=$(echo "$RUN" | jq -r '.data.id'); DATASET=$(echo "$RUN" | jq -r '.data.defaultDatasetId')
curl -s "https://api.apify.com/v2/actor-runs/$RUN_ID?waitForFinish=60" -H "Authorization: Bearer $APIFY_TOKEN" | jq -r '.data.status'
curl -s "https://api.apify.com/v2/datasets/$DATASET/items?format=json" -H "Authorization: Bearer $APIFY_TOKEN" > output.json
```

## Cost and limits

- Apify bills the Actor's usage on your account; the Actor's Pricing tab shows the current price.
- Keep the limit in the input small for a first run.

## Guardrails

- Public data only. Do not pass cookies, sessions or private account data.
- Do not use the output for spam, harassment or unlawful discrimination.
- Check the target site's terms and local law before running at scale.
