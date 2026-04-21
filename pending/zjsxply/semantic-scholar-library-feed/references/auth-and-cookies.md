# Authentication And Cookie Store

## Fixed paths

Store Semantic Scholar cookies under:

- `~/.auth/semantic-scholar.cookies.json`
- `~/.auth/semantic-scholar.cookie-header.txt`

Keep these paths stable. Other scripts in this skill assume them unless the caller overrides `--cookie-path`.

If `--cookie-path` is overridden, write the matching header file beside it with a derived sibling name such as:

- `/tmp/custom.cookies.json`
- `/tmp/custom.cookie-header.txt`

## Preferred workflow

1. Try the fixed Cookie Store first:

```bash
python3 scripts/semantic_scholar_cli.py cookie-summary
```

2. If the file is missing, stale, or lacks `sid`/`s2`, ask the user to open an authenticated Semantic Scholar request in browser DevTools and copy it as curl.

3. Import that curl directly:

```bash
python3 scripts/semantic_scholar_cli.py import-curl \
  --curl-file /tmp/semantic-scholar-request.sh
```

You can also pass the curl inline:

```bash
python3 scripts/semantic_scholar_cli.py import-curl \
  --curl "$(pbpaste)"
```

4. Verify the saved cookie bundle contains at least `sid` and `s2`.

If the user already extracted only the Cookie header, fall back to:

- `scripts/semantic_scholar_cli.py import-header --header 'sid=...; s2=...'`

## Minimum working cookies

Current verified minimum for private Library and Research Feed access:

- `sid`
- `s2`

Only `sid` is not enough for the tested account state. It returns `401` for private pages.

## Why save both JSON and a raw header

The JSON file preserves structured cookie metadata for repeatable CLI usage. The raw header file is faster for HTTP debugging and lets the skill reuse the session outside the browser.

## Curl import notes

- Browser DevTools usually exposes "Copy as cURL (bash)" for any request in the Network tab.
- Prefer copying a request that already succeeded inside the authenticated Semantic Scholar UI.
- `import-curl` reads `-b/--cookie`, `Cookie:`, `User-Agent:`, and `Referer:` fields from the copied command.
- Treat the copied curl as sensitive account material.

## Playwright scope

- Do not use Playwright as the login path for this skill.
- Use Playwright only to inspect rendered pages, confirm which hidden API a button triggers, or observe network requests when direct HTTP behavior is unclear.

## Verification checklist

After refreshing cookies, verify one of these before continuing:

- `scripts/semantic_scholar_cli.py cookie-summary`
- `scripts/semantic_scholar_cli.py ssr-dump --page-url https://www.semanticscholar.org/me/recommendations --list-names`

If the request returns `401`, refresh cookies again.
