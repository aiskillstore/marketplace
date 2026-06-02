# Brewpage Publish

Publish text, markdown, JSON, files, or whole multi-file sites to [brewpage.app](https://brewpage.app) — get a public URL instantly. No sign-up.

## Quick Start

1. Install:
   ```bash
   npx skills add kochetkov-ma/claude-brewcode
   ```

2. Use via slash command:
   ```
   /brewpage-publish "Hello, world!"
   /brewpage-publish report.md
   /brewpage-publish '{"status": "ok"}'
   /brewpage-publish screenshot.png --ttl 1
   /brewpage-publish ./my-site --entry index.html
   /brewpage-publish site.zip
   ```

   Or via natural language:
   ```
   Publish this to brewpage
   Upload report.md to brewpage.app
   Deploy this directory as a site
   ```

Claude detects the content type, asks for a namespace and password interactively, calls the brewpage.app API, and returns a public URL. The owner token is saved to `.claude/brewpage-history.md` for later deletion.

## What It Does

1. **Detects content type** — directory/ZIP becomes a multi-file site, single file becomes a file upload, objects/arrays become JSON, everything else becomes HTML (markdown rendered)
2. **Asks namespace** — interactive prompt for a short, human-readable namespace (URL slug)
3. **Asks password** — optional password protection (hides the page from the gallery)
4. **Calls API** — sends content to brewpage.app
5. **Returns URL** — public link ready to share
6. **Saves token** — owner token written to `.claude/brewpage-history.md`

## API Coverage

| Content | Type | Endpoint |
|---------|------|----------|
| Text / markdown | HTML | `POST /api/html?format=markdown` |
| JSON object/array | JSON | `POST /api/json` |
| Local file | File | `POST /api/files` |
| Directory | Site | `POST /api/sites` (zipped on the fly) |
| `.zip` archive | Site | `POST /api/sites` |

## Sites

`POST /api/sites` accepts **only a `.zip` archive** — there is no raw-folder upload.

- **Directory (primary):** point at a **built** static directory; the skill auto-zips it and uploads. Archive sealing keeps relative paths intact.
- **Pre-built `.zip` (alternative):** uploaded as-is.

The auto-zip **excludes** `.git/`, `.env`/`.env.*`, `node_modules/`, `.DS_Store`, `Thumbs.db`, `.idea/`, `.vscode/`, `.cache/`, `*.map` and `*.log` — only real built assets ship; secrets and VCS data never leak into the public archive.

**Built-static guard:** publish build output, not sources. No `.html` in the directory → the skill fails and tells you to build first. A source tree (`package.json` + `src/`, no top-level `.html`) → the skill asks you to point at the build output (`dist/`, `build/`, `out/`, `_site/`, `public/`).

Entry file: `--entry` override > `index.html` > first `.html` alphabetically.

**No trailing slash.** The API returns `https://brewpage.app/public/<id>` without a trailing `/`. Appending `/` routes to brewpage.app's landing page and breaks the link. Share the URL exactly as printed. Site URLs cannot be verified with plain `curl` (the no-slash URL serves an inline JS redirect that only runs in a browser) — verify with a real browser or fetch `<url>/index.html`.

## TTL

Default time-to-live is **15 days** (max 30). Override with `--ttl N` (days):

```
/brewpage-publish report.md --ttl 1
/brewpage-publish '{"data": [1,2,3]}' --ttl 30
```

## Owner Token & Privacy

The owner token is **never printed in conversation** — the skill's bash blocks curl the API, parse the token, and append it to `.claude/brewpage-history.md` directly. Only the public URL is shown.

`.claude/brewpage-history.md` is a **private file** (keep it out of version control). Use the token to delete a page:

```bash
# html / json / kv
curl -X DELETE "https://brewpage.app/api/{ns}/{id}" -H "X-Owner-Token: {token}"
# site
curl -X DELETE "https://brewpage.app/api/sites/{ns}/{id}" -H "X-Owner-Token: {token}"
```

## Part of Brewcode

This skill is part of [brewcode](https://github.com/kochetkov-ma/claude-brewcode) — a development platform for Claude Code with infinite focus tasks, agents, quorum reviews, and knowledge persistence.

```bash
claude plugin marketplace add https://github.com/kochetkov-ma/claude-brewcode
claude plugin install brewcode@claude-brewcode
```

## License

MIT
