---
name: page
description: "Draft one page as one URL, one offer, and one action. Use when a landing page should hold a single address and a single next step, and when a sitemap must be refused."
models: ""
---

# The page

A page is one address. It states one offer. It asks for one action. A sitemap is a list of addresses. This pack refuses that list.

No portal course owns this job. The skill still ships the page.

The build guide teaches a human. This pack teaches an agent.

## The three parts

1. URL. One https address for this page. Not a list of paths.
2. Offer. The thing the page puts in the reader's hands, in one sentence.
3. Action. The one thing the reader does on that page.

## What the scorer refuses

The scorer refuses a sitemap. A sitemap is a `kind` of sitemap, a `urls` list, or a URL whose path says sitemap.

A page can name one address, one offer, and one action. It does not inventory the site.

## Checklist

Copy this list and tick it in order.

- [ ] 1. Name the one URL.
- [ ] 2. Fill the page shell: url, offer, action.
- [ ] 3. Run `python3 scripts/score.py --file draft.json`.

Check again until the script exits 0.

Go back to step 2 if step 3 fails.

## Run

```bash
python3 scripts/score.py --file examples/page-good.json
python3 scripts/score.py --file examples/page-sitemap.json
```

The good file exits 0 and prints the URL, the offer, and the action. The sitemap file exits 1.

The JSON object has three strings: `url`, `offer`, and `action`. A broken JSON exits non-zero and does not echo the raw input.

Python 3 standard library only. No network. No publish.

## Shell

```json
{
  "url": "https://example.com/desk",
  "offer": "A one-page desk that names the week's leak.",
  "action": "Read the page and reply with the one number you want next."
}
```
