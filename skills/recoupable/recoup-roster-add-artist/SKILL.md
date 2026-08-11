---
name: recoup-roster-add-artist
description: Onboard a brand-new artist to your roster and enrich them — the 8-call chain (create → Spotify match → research → catalog → socials → knowledge base) that sets up the artist and their workspace folder. Use for "create/add/onboard an artist", "set up [artist]", "we just signed [artist]", or "new signing". To see your roster use recoup-roster-list-artists; to work inside an existing artist's files use recoup-roster-manage-artist.
---

# Recoup — Add Artist

Bring a new artist into the box: create the account, enrich it, and scaffold their
workspace. Driven by a checklist so the long chain is resumable.

## The 8-call onboarding chain (drive from the RECOUP.md checklist)

Long chains run from prose drop steps, so **drive from the `RECOUP.md` checklist**:
scaffold it first (frontmatter holds captured values; body holds the unchecked
steps), tick + persist after each step — the file IS the workflow state, resumable
from the first unchecked box. Don't run under an `agent+` account (data gets
orphaned). The 8 calls:

1. `POST /api/artists {name, organization_id}` → capture `account_id`.
2. `GET /api/spotify/search` → best match → `id`, `external_urls.spotify`, `images[0]`.
3. `PATCH /api/artists/{id}` with image + `profileUrls:{SPOTIFY}` (UPPERCASE keys).
4. Structured research (retry transient misses): `/research/lookup?spotifyId=` →
   `songstats_artist_id`, then `/research/profile|career|playlists` + `/research/web`.
5. Spotify catalog (`topTracks`, `albums`, `album`) → write `releases/{slug}/RELEASE.md`
   per album + `releases/top-tracks.md`.
6. Web search for socials (ig/tiktok/twitter/youtube).
7. `PATCH /api/artists/{id}` with discovered `profileUrls` (only platforms found).
8. Synthesize a `## Knowledge base` section into `RECOUP.md`.

Run in order; don't continue past a 4xx/5xx without recovery. Uses
recoup-platform-api-access for the call shapes.

## Guardrails

- **The file is the state** — tick + persist each step or a fresh turn redoes/skips work.
- **No placeholder data** in artist files — real content or leave the section out.
- **Never invent a roster/artist** — confirm via recoup-platform-api-access first; an
  empty filesystem is not an empty roster.
