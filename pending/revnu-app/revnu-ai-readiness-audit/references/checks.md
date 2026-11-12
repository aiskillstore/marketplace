# How to run each check

Commands assume a POSIX shell with `curl` and Python 3. Replace `$URL`.
Keep requests to the pages being audited; this is not a site crawl.

## Gate: status, redirects, indexability

```bash
# Status, redirect chain and robots headers, as a browser and as a search crawler
curl -sIL -o /dev/null -w '%{http_code} %{url_effective}\n' "$URL"
curl -sIL "$URL" | grep -iE '^(HTTP/|location:|x-robots-tag:|content-type:)'
curl -sIL -A 'Mozilla/5.0 (compatible; OAI-SearchBot/1.4; +https://openai.com/searchbot)' "$URL" | grep -iE '^HTTP/'
```

Read from the HTML (see the extractor below): `<meta name="robots">`,
`<link rel="canonical">`, `<title>`, meta description.

Findings worth raising:

- A non-200 final status, or a chain of more than one redirect.
- `noindex`, `none` or `nosnippet` on a page meant to be found. Google says a
  page must be indexed and snippet-eligible to appear in AI Overviews or AI
  Mode, so `nosnippet` keeps it out.
- A canonical pointing at another URL (or at the homepage from every page),
  or `http://` canonicals on an `https://` site.
- A soft 404: a missing path that returns 200 with a "not found" page.
  Test with `curl -s -o /dev/null -w '%{http_code}' "$ORIGIN/this-should-not-exist-$RANDOM"`.

For per-crawler robots.txt and firewall checks, run
`revnu-ai-crawler-access`'s `scripts/check_ai_crawlers.py` if that skill is
installed next to this one (`../revnu-ai-crawler-access/scripts/`).

## Raw HTML extractor

Python standard library only; reads one saved page. Save first with
`curl -sL "$URL" -o page.html`, then:

```bash
python3 - page.html <<'PY'
import sys, re, json, html
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
def first(rx):
    m = re.search(rx, t, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else None
print("title:", first(r"<title[^>]*>(.*?)</title>"))
print("description:", first(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'))
print("robots:", first(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']*)'))
print("canonical:", first(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)'))
for level, text in re.findall(r"<h([1-3])[^>]*>(.*?)</h\1>", t, re.I | re.S):
    print(f"h{level}:", html.unescape(re.sub(r"<[^>]+>|\s+", " ", text)).strip()[:120])
blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', t, re.I | re.S)
print("json-ld blocks in raw HTML:", len(blocks))
for b in blocks:
    try:
        d = json.loads(b)
        items = d if isinstance(d, list) else d.get("@graph", [d])
        print("  types:", [i.get("@type") for i in items if isinstance(i, dict)])
    except Exception as e:
        print("  INVALID JSON-LD:", str(e)[:80])
body = re.sub(r"(?is)<(script|style|noscript|template)\b.*?</\1>", " ", t)
words = re.findall(r"\w{2,}", re.sub(r"<[^>]+>", " ", body))
print("visible words in raw HTML:", len(words))
print("first 60 words:", " ".join(words[:60]))
PY
```

## Raw vs rendered

- **Raw:** the extractor's word count and first 60 words.
- **Rendered:** with a browser tool, load the page and read
  `document.body.innerText.split(/\s+/).length` and the first screen of text.
  Without one, ask the user to confirm what the first screen shows, or note
  "rendered DOM not checked".

If the raw HTML has a fraction of the rendered words, or the key facts
(price, what it is) appear only after rendering, raise it. Fix options, in
order of effort: server-render or statically generate that section; move
the fact into the initial HTML (even a short summary paragraph); prerender
the route.

## Rendered JSON-LD

In a browser tool's console or evaluate step:

```js
[...document.querySelectorAll('script[type="application/ld+json"]')]
  .map(s => { try { const d = JSON.parse(s.textContent); return [].concat(d['@graph'] || d).map(i => i['@type']); }
              catch (e) { return 'INVALID'; } })
```

If rendered finds blocks that raw doesn't, the markup is injected by
JavaScript (common with tag managers and some CMS plugins). Report it as
"present after rendering only": Google can process it; whether other
engines' fetchers see it is undocumented. Prefer emitting it server-side.

Without a browser tool, Google's Rich Results Test
(https://search.google.com/test/rich-results) renders the page; ask the user
to run it, or say "rendered schema not checked".

## Answer-first read

For each page, write down, from the first screen of raw text only:

1. What is this? (category in plain words)
2. Who is it for?
3. What is this page's answer? (price; the comparison verdict; the how-to's
   first step)

Any blank is a candidate fix. Quote the current opening line as evidence and
propose a replacement that states the missing answer in one or two plain
sentences, using only facts from the site or the user.

## Entity facts table

Collect each fact from: homepage, about, pricing, footer, `<title>`, meta
description, Organization/Product JSON-LD, and the social or directory
profiles linked from the site (`sameAs` or footer links). One row per fact,
one column per place. Contradictions and outdated values are findings.

For namesake risk, run one web search for the bare business name. If the
first results are a different company or product, recommend stating the
disambiguating facts plainly on the homepage and about page (what it is,
domain, founding year, location) and keeping them identical in
`Organization` markup.

## Freshness

```bash
curl -s "$ORIGIN/sitemap.xml" | grep -o '<lastmod>[^<]*' | sort | tail -5
```

Compare the visible "updated" date on the page, `dateModified` in its
JSON-LD and its sitemap `lastmod`. Flag a page whose year in the title or
H1 has passed, or whose prices differ from the pricing page.

## llms.txt

```bash
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' "$ORIGIN/llms.txt"
curl -s "$ORIGIN/llms.txt" | head -30
```

Report: present or not; status and content type; whether it starts with an
H1 (the proposal's only required section); whether its links resolve
(spot-check three). Then stop. It is not a top-10 fix.
