# Kickoff — independent record label (RICH input)

Tests the **Recoup specialization**: turning a label's real input packet into the music-company OS
without re-inferring the domain (it is fixed — a music label). The builder's domain input is the
packet in `./kickoff/` next to this file:

- `kickoff/roster.csv` — the signed roster (artist, slug, genre, status, next release).
- `kickoff/artist-brief.md` — a loose brief on one priority artist (voice, audience, upcoming work).
- `kickoff/notes.md` — recurring questions, a standing decision, a reusable template, a one-off idea.

The builder reads all three fully, then builds the OS for this label.

**What a strong build looks like:** the domain stays **music label** (the skill does NOT re-run
domain inference); a top-level `artists/` entity folder with a record + `RECOUP.md` identity file per
roster row (frontmatter `artistName` / `artistSlug` / `artistId`), each with a `releases/` subfolder;
**no top-level pipeline folder** — release stage lives per-release in `RELEASE.md`; unsigned / A&R
candidates parked in `prospects/`; `knowledge/faqs/` + `knowledge/decisions/` populated from
`notes.md` (the standard rollout, the DSP-pitch-window rule, the short-form-first decision); the
reusable DSP one-sheet structure mined into `library/`; the one-off "sound-alike finder" idea parked
in `work/` (NOT a top-level folder); `.env.example` + a `.gitignore` that ignores `.env` (secrets
never committed to the shared repo); and the build wired to pull the real roster from the Recoup API
— or hand off to `recoup-roster-onboard` if the account is empty — rather than inventing a roster.
Inferred facts marked "draft — confirm".
