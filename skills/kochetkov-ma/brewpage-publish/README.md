# Brewpage Publish

Publish text, markdown, JSON, files, or whole multi-file sites to [brewpage.app](https://brewpage.app) — get a public URL instantly. No sign-up.

BrewPage needs no account and keeps pages for 1 to 30 days. To compare it with GitHub Pages, Netlify Drop, Tiiny Host and others, see [brewpage.app/compare](https://brewpage.app/compare).

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
   /brewpage-publish report.md --delivery-mode subdomain
   /brewpage-publish ./my-site --entry index.html
   /brewpage-publish site.zip
   ```

   Or via natural language:
   ```
   Publish this to brewpage
   Upload report.md to brewpage.app
   Deploy this directory as a site
   ```

Claude detects the content type and requires explicit namespace and password choices before calling the brewpage.app API. Explicit **Skip** selects the suggested private namespace or no password; an unanswered or ambiguous choice stops the upload, including headless runs without prior explicit choices. After publishing, Claude returns a shareable URL. The owner token is saved to `.claude/brewpage-history.md` at the project root for later deletion.

The skill is model-invocable: Claude can run it on its own when you ask to publish or share a link. Every step is one `brewpage-run.sh` command covered by a single scoped Bash rule, so Bash never prompts. Claude Code asks once for the `Skill` call in default permission mode.

`scripts/` ships with the skill (`brewpage-run.sh` with `probe`, `stage`, `publish` and `cleanup`, plus a helper library and `publish.mjs` for site bundles). `npx skills add` copies the whole folder.

## Requirements

Use a POSIX runtime (macOS, Linux or WSL) with `bash`, `curl`, `jq` and Python 3 (`python3`) with `fcntl` for secure local owner-token history. Git is also required inside a Git checkout. Native Windows Python is unsupported. Directory and ZIP sites also require `node` and `unzip`; directory packaging also requires `zip`.

## What It Does

1. **Detects content type** — directory/ZIP becomes a multi-file site, single file becomes a file upload, objects/arrays become JSON, everything else becomes HTML (markdown rendered)
2. **Asks namespace** — `public` or a short, human-readable private slug (default). In `public`, pages, sites and files are listed in the public gallery and the sitemap, so Google, Bing and AI search can find and index them and people can discover them. Use it for anything meant to be found or shared. Anyone can find and read a public publication, so never put secrets, tokens or personal data there. A private slug (default) is unlisted and not indexed; anyone with the link can still open it.
3. **Asks password** — optional protection (hides the page from the gallery): an existing local file, given by absolute path, holds the password (min 4 characters); nothing is typed or generated
4. **Calls API** — sends content to brewpage.app
5. **Returns URL** — shareable link
6. **Saves token** — the script writes the owner token to `.claude/brewpage-history.md` at the project root (mode 600, git-ignored)

## API Coverage

| Content | Type | Endpoint |
|---------|------|----------|
| Text / markdown | HTML | `POST /api/html?format=markdown` |
| JSON object/array | JSON | `POST /api/json` |
| Local file | File | `POST /api/files` |
| Directory | Site | `POST /api/sites` (zipped on the fly) |
| `.zip` archive | Site | `POST /api/sites` |

## Sites

`POST /api/sites` accepts a **ZIP archive** or **repeated `files` with matching `paths` fields**. This skill uses ZIP transport for directory uploads.

- **Directory (primary):** point at a **built** static directory; the skill builds a ZIP from it, verifies the archive (`unzip -t`, name set) and uploads. Relative paths stay intact.
- **Pre-built `.zip` (alternative):** copied to a private temporary file, then inspected, hashed and uploaded from that same copy. The original archive bytes are never rewritten.

The directory bundle is **allowlisted**: it drops system files (`.DS_Store`, `__MACOSX/`, `Thumbs.db`, `desktop.ini`), which are listed under `SKIPPED` in the manifest, never flagged and never counted toward the server's file limit. It also drops hidden files and folders (`.env`, `.git/`), `node_modules/`, symlinks and unknown file types (`*.map`, `*.log`). The root `.well-known/` is the one hidden folder that ships, with all its files, extension-less ones included (for example `apple-app-site-association`). Kept names that look sensitive (`secret`, `token`, `password`, `credential`) are flagged, and the script stops with `CONFIRM:` before uploading anything. A supplied ZIP gets the same inspection: anything unexpected or sensitive inside it needs confirmation. File contents are not scanned, so still check the built bundle for embedded secrets.

For a flagged archive, review the manifest and its `REVIEW_SHA256` digest, then approve that exact content. Re-run the command with `--confirmed --review-sha256 <displayed-digest>`. If the source bytes change, the script prints a fresh manifest and digest and exits with code 2 without uploading; review it and approve again. Temporary files are removed on every exit; no confirmation cache is retained.

**Built-static guard:** publish build output, not sources. No `.html` in the directory → the skill fails and tells you to build first. A source tree (`package.json` + `src/`, no top-level `.html`) → the skill asks you to point at the build output (`dist/`, `build/`, `out/`, `_site/`, `public/`).

Entry file (server rule): `--entry` override > root `index.html` > shallowest `.html` (ties: name order). To start on another page, pass `--entry`.

Site limits: 200 files, 5 MB per file, 20 MB total, 25 MB per request. To see the current values, ask the skill to check the limits or run `curl -s https://brewpage.app/api/limits`; the skill runs its own `limits` command before a big site. A successful upload prints `OK <url>`, followed by any server `NOTICE:` lines. A rejected upload prints `FAILED: publish rejected (HTTP <status>: <message>)` with the server's reason and no notices.

Local ZIP inspection has separate size and metadata budgets, rejects ZIP64 and split archives, and limits each `unzip` check to 10 seconds; see [the skill's archive inspection notes](SKILL.md#notes).

Share the server's `link` exactly, including any trailing `/`. New subdomain roots include `/`; existing links keep their historical form. Verify a new site at its returned URL and asset paths, with a browser for rendering. Existing sites may still use a browser redirect; verify those in a browser or fetch their explicit entry asset.

## Delivery Mode

`--delivery-mode path|subdomain` optionally sends the `X-Delivery-Mode` creation header. With no flag, the skill sends no header and uses the server default. Other values are rejected; the option never changes the uploaded content.

| New publication (`routingCohort: new-v1`) | Delivery |
|-----------------------------------------|----------|
| Site or non-`public` HTML page (format `html`) | Dedicated subdomain (`subdomain`); explicit `path` is coerced to `subdomain`, with a mismatch notice |
| All other uploads, including password-protected uploads | Promotion (`path`) by default; `subdomain` is optional |

An upload may return an existing publication. Keep that winner's identity, metadata and exact server link even if its delivery differs from the request. Existing publications without routing metadata keep their historical links; do not infer their mode from the URL. Never construct or parse a publication hostname to recover its namespace or resource ID.

See the [hosting API reference](https://brewpage.app/api#hosting) for mode changes and delivery limits.

## TTL

Default requested time-to-live is **15 days** (normally 1..30, subject to owner limits). Override with `--ttl N` (days). Site PUT keeps the original expiry; use returned `expiresAt` for actual retention, including any eligible automatic extension.

```
/brewpage-publish report.md --ttl 1
/brewpage-publish '{"data": [1,2,3]}' --ttl 30
```

## Owner Token & Privacy

The owner token is **never printed in conversation** — `brewpage-run.sh` parses the response and writes it directly to `.claude/brewpage-history.md` at the project root (`CLAUDE_PROJECT_DIR`, else the git toplevel). The script creates the file with mode 600 and adds it to the project `.gitignore`. It also records the exact public URL, apex `ownerLink`, and identity fields such as `id`, `namespace`, `type`, `routingCohort`, `deliveryMode` and `hostingVersion` for later owner operations.

Optional: sign in free (Google or any email) at [account.brewpage.app](https://account.brewpage.app) to manage publications and tokens, with retention up to 90 days. Publications still expire; a token without an expiry does not extend content retention. Local owner-token history stays in your project. Sign-in is not needed to publish.

New password-protected links stay clean: do not append `?p=`. Readers unlock through the trusted `unlock.brewpage.app` page; programmatic reads use `X-Password` on the apex API. Existing password behavior remains unchanged.

Use the saved `ownerLink` and identity for updates and deletion on `https://brewpage.app`, never the publication host. Existing history without metadata keeps its saved API identifiers. Delete:

```bash
curl -X DELETE "{ownerLink}" -H "X-Owner-Token: {token}"
# no ownerLink: {type} = html|json|files|kv|sites
curl -X DELETE "https://brewpage.app/api/{type}/{ns}/{id}" -H "X-Owner-Token: {token}"
```

New publications without a required subdomain support owner-only `PATCH /api/{type}/{ns}/{id}/hosting` with `deliveryMode` and the current `expectedVersion`. Read the version first; use the returned link and version afterward. Switching modes retains the same reserved host. Legacy publications, sites and non-public HTML pages (format `html`) keep their required or historical delivery; incompatible PATCH requests return unchanged with a notice. Ordinary content updates omit `X-Delivery-Mode`. See the [hosting API reference](https://brewpage.app/api#hosting).

## Part of Brewcode

This skill is part of [brewcode](https://github.com/kochetkov-ma/claude-brewcode) — a Claude Code plugin suite for skill and agent authoring, semantic code search, project-tailored review, and documentation tools.

```bash
claude plugin marketplace add https://github.com/kochetkov-ma/claude-brewcode
claude plugin install brewdoc@claude-brewcode
```

## License

MIT
