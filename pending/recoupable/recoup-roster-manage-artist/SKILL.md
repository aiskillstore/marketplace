---
name: recoup-roster-manage-artist
description: Work inside one artist's folder — read and update their context, brand, songs, and releases. Use for "organize [artist]'s files", "update [artist]'s brand/context", "what's in [artist]'s workspace", or any task about a named artist's files. To list your whole roster use recoup-roster-list-artists; for research/metrics on an artist use recoup-research-artist-overview.
---

# Recoup — Manage Artist

Operate inside an existing artist's workspace at `artists/{artist-slug}/`.
`RECOUP.md` (frontmatter `artistName`/`artistSlug`/`artistId`) is the identity file.

## Layout

`context/artist.md` (who they are — static), `context/audience.md` (static),
`context/images/face-guide.png`, `releases/{slug}/RELEASE.md` (the release master
doc), `songs/{slug}/{slug}.mp3`. Nothing is pre-created — add files when real
content arrives; never write placeholder tokens.

## Static vs dynamic context

Update `artist.md`/`audience.md` deliberately (they're the source of truth other
skills read); treat research/release docs as time-bound — archive when stale.
Commit `{what}: {why}`; the git log is the per-artist progress log.

## Guardrails

- **No placeholder data** in artist files — real content or leave the section out.
- **Don't overwrite static context** casually — `artist.md` changes are deliberate
  evolutions; note the why in the commit.
- **Never invent a roster/artist** — empty filesystem ≠ empty roster; confirm via
  recoup-platform-api-access first.
