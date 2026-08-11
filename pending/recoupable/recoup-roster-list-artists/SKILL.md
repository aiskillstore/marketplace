---
name: recoup-roster-list-artists
description: See who's on your roster — answers "what artists do I have" by walking the workspace and falling back to your live account when the filesystem is empty. Use for "what artists do I have", "list my roster", "who's on my roster", or "what's in this sandbox". To add a new artist use recoup-roster-add-artist; to work inside one artist's files use recoup-roster-manage-artist.
---

# Recoup — List Artists

Inventory the roster. Artist dirs live at `artists/{artist-slug}/`; `RECOUP.md`
(frontmatter `artistName`/`artistSlug`/`artistId`) is the identity file.

## Procedure

Walk the filesystem when it's a real sandbox (`ls -d artists/*/`,
`find artists -name RECOUP.md`); if `artists/` is missing/empty, fall back to
recoup-platform-api-access roster discovery (`GET /accounts/id` → `GET /organizations`
→ `GET /artists?org_id=…`).

**Never report an empty roster from a missing filesystem** — an empty `artists/`
dir is not an empty roster; confirm against the live account first.

## Guardrails

- **Never invent a roster/artist** — empty filesystem ≠ empty roster.
- Report names + identity (slug/id), not a raw JSON dump.
