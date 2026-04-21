---
name: semantic-scholar-library-feed
description: Work with a user's Semantic Scholar account to read Research Feeds, inspect private Library folders, add papers to folders, and resolve Semantic Scholar paper records from identifiers such as arXiv IDs.
---

# Semantic Scholar Library & Feed

## Overview

Use this skill to work against Semantic Scholar's authenticated Library and Research Feed surfaces without browser-driven login flows. Prefer the bundled CLI for Cookie Store inspection, browser-curl import, SSR probing, feed pagination, folder inspection, folder writes, and Graph `paper/batch` lookups.

## Quick Start

1. Check whether the fixed Cookie Store already exists:

```bash
python3 scripts/semantic_scholar_cli.py cookie-summary
```

2. If the Cookie Store is missing or stale, ask the user to copy an authenticated Semantic Scholar request as curl from browser DevTools, then import it:

```bash
python3 scripts/semantic_scholar_cli.py import-curl \
  --curl-file /tmp/semantic-scholar-request.sh
```

`import-header` is still available when the user already extracted only the raw Cookie header.

3. Check cookie health:

```bash
python3 scripts/semantic_scholar_cli.py cookie-summary
```

4. Choose the task module below.

## Cookie Store

Save Semantic Scholar auth state under:

- `~/.auth/semantic-scholar.cookies.json`
- `~/.auth/semantic-scholar.cookie-header.txt`

Treat `sid` and `s2` as the minimum required cookies for private Library and Feed access. If either is missing, ask the user for a fresh browser-copied curl and re-import it before touching private endpoints.

Read [references/auth-and-cookies.md](references/auth-and-cookies.md) when you need the Cookie Store workflow or the curl import format.

## Task Modules

### Research Feed

Use this path when the user wants feed export, history crawl, or local coarse filtering.

1. Probe SSR if you need to inspect `var DATA`:

```bash
python3 scripts/semantic_scholar_cli.py ssr-dump --list-names
```

2. Crawl the feed through `/api/1/library/folders/recommendations`:

```bash
python3 scripts/semantic_scholar_cli.py feed-crawl \
  --output /tmp/research-feed.json
```

3. Persist output after every window. Do not wait for the entire crawl to finish.

Read [references/research-feed.md](references/research-feed.md) when you need the SSR decode order, the real API path, or the pagination stop rules.

### Library Folder

Use this path when the user wants folder contents, folder diffs, or bulk add operations.

1. Export a folder:

```bash
python3 scripts/semantic_scholar_cli.py folder-entries \
  --folder-id 13895811 \
  --all-pages \
  --output /tmp/folder.json
```

2. Add a paper to a folder:

```bash
python3 scripts/semantic_scholar_cli.py folder-add \
  --paper-id 25f612200a3821c71b99819cd671f2e60df5b470 \
  --paper-title 'AgentArk: Distilling Multi-Agent Intelligence into a Single LLM Agent' \
  --folder-ids 13895811
```

Read [references/library.md](references/library.md) when you need endpoint behavior, `pageSize` limits, or the verified `entries/bulk` request shape.

### Paper ID Resolution

Use Graph `paper/batch` when BibTeX already contains stable identifiers such as arXiv IDs.

```bash
python3 scripts/semantic_scholar_cli.py graph-batch \
  --ids ARXIV:2602.08234,ARXIV:2602.12670
```

Prefer this over search-page scraping when possible.

## Operating Rules

- Prefer direct HTTP after cookies exist.
- Do not use Playwright for login. If the Cookie Store is missing, ask the user to copy an authenticated browser request as curl and import it.
- Use Playwright only when rendered-page behavior or network inspection is needed to discover hidden interfaces.
- Treat browser clicking as a reconnaissance step, not the main extraction path.
- For feed history, stop on `empty days`, missing `nextWindowUTC`, or repeated windows.
- For folder sync, resolve `paperId` first, diff against existing folder entries, then call `folder-add`.
- If the task depends on a private page and returns `401`, ask for a fresh browser-copied curl and refresh the Cookie Store before debugging the endpoint.
