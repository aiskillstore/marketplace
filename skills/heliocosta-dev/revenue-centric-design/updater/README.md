# updater/ — maintaining the Revenue-Centric Design skill

This folder is the **pipeline** that built the skill and keeps it current as
[@richardrx](https://x.com/richardrx) posts new material. It is *not* part of the
installed skill — `npx skills add` and the agent only ever read `SKILL.md`,
`references/`, and `assets/` at the repo root. Everything here is maintainer tooling.

Secrets and bulk data are gitignored (`updater/.env`, `updater/data/`,
`updater/staging/`); the scripts and this doc are tracked so the process is
reproducible and auditable.

## The core idea: the skill is its own manifest

There is no separate list of "what's included." The set of covered posts is derived
from the `@richardrx · …` **Source** links in `references/*.md`, and each post's date
is decoded from the tweet id itself (Twitter Snowflake) — so *coverage and counts are
computed with zero API calls* and can never drift from the actual content.

## One-time setup

```bash
cd updater
cp .env.example .env          # then paste your X API v2 Bearer Token into .env
# (optional) pip install anthropic   # only if you want the auto-distiller, distill.py
```

## Updating the skill (the loop)

```
discover_new.py  →  curate → new_posts.txt  →  update.py  →  distill + REVIEW  →  paste into references/  →  refresh_meta.py  →  commit
   (optional)                                   (fetch+stage)   (LLM, human-checked)   (the curation call)      (sync numbers)
```

1. **Find new posts (optional).** `python discover_new.py` lists @richardrx **original**
   posts made since the skill's latest included post that aren't in the skill yet.
   It applies **no topical filter** — it returns *all* his original posts in that window
   (personal / off-topic ones included), because this is a *candidate list*, not a
   decision; curation (step 2) is where you choose. Add `--rank` to have Claude tag each
   candidate `[ON-topic]` / `[off-topic?]` with a one-line reason so the list is
   pre-triaged (needs `anthropic` + an API key). Or just collect URLs by hand.
2. **Curate.** Put the worthwhile URLs (one per line) in `new_posts.txt`. Not every
   post belongs — this is a curated best-of, so choose deliberately.
3. **Fetch + stage.** `python update.py`
   - Computes the delta (candidates **not** already in the skill) so re-running is safe.
   - Fetches only the new posts (original + quoted post + media; long-form and X
     Articles handled).
   - Writes `staging/posts/<id>.md`, downloads media to `staging/media/`, and writes
     `staging/prompts/<id>.md` — the distillation spec pre-filled with that post.
4. **Distill each staged post into a principle (LLM), then review.** Each
   `staging/prompts/<id>.md` already bundles everything the model needs: the distillation
   spec, the post's source text (translated), and the paths of its images. Two ways:

   - **a) Assisted — recommended for a Claude Code user, no extra deps.** In Claude Code,
     from the repo, hand it the staged prompt, e.g.:
     > *"Read `updater/staging/prompts/<id>.md` and view the image files it lists.
     > Produce the finished principle entry following the spec exactly, tell me which
     > `references/<theme>.md` it belongs in, and wait for my OK before writing anything."*

     The agent reads the prompt, **views the images** (needed to judge which are
     informational and to write the `**Visual.**` line), drafts the entry, and names the
     theme. You read it, adjust wording, and approve. For several posts at once, point it
     at the whole `updater/staging/prompts/` folder.
   - **b) Automated.** `python distill.py` sends each staged post + its images to Claude
     and writes a draft to `staging/drafts/<id>.md` with a proposed theme (needs
     `pip install anthropic` + `ANTHROPIC_API_KEY` or `ant auth login`).

   Either way, **a human reviews every draft before it enters `references/`** — the spec
   is strict, but you are the taste and accuracy check.
5. **Merge (the curation call).** Paste each approved principle into the right
   `references/<theme>.md`, **newest-first** (entries are ordered by date). If the entry
   keeps an image, copy that file from `staging/media/` into `../assets/` (the entry
   references it as `../assets/<file>`). `prompts/distill.md` lists the theme slugs.
6. **Sync the numbers.** `python refresh_meta.py` recomputes principle/theme counts,
   the per-theme table, and the coverage date range, and patches `README.md` + `SKILL.md`.
   Use `--check` first to preview, and `--updated YYYY-MM-DD` when you want to bump the
   "Last updated" date and badge. Add a line to `CHANGELOG.md` and commit.

## How updates affect existing content

**Additive by default.** A new post becomes a new principle appended to one theme
file. Existing entries are immutable — each is pinned to its own source post and date,
and nothing rewrites them. `refresh_meta.py` then bumps the counts and coverage window
to match; the 9-principle spine and the file structure stay put.

**Supersession is a human call.** Occasionally Richard revises a framework (as happened
with the Revenue-Centric Design principles: an earlier 10-item draft, then the canonical
9). Do **not** overwrite the old entry. Add the new one and cross-reference the old as
"(earlier version) … superseded by …", exactly as `references/revenue-centric-design.md`
already does. The pipeline surfaces candidate posts; it never edits curated prose on its own.

**Guardrail carries forward.** New posts are subject to the same usage boundary — do
not add principles that promote betting/casino/gambling products. `prompts/distill.md`
restates this.

## Cost

X API pay-per-use is **$0.005 per post read**, billed per resource returned, de-duped
within a 24h UTC window. A typical update (a handful of new posts + their quoted posts +
`discover_new`'s timeline scan) costs **cents**. `refresh_meta.py` and delta detection
are fully offline.

## Rebuilding from scratch

`posts.txt` holds the full list of source URLs and `fetch_posts.py` re-extracts them
into `data/` — useful for a clean rebuild or re-distillation. Keep `posts.txt` roughly
in sync by appending new URLs as you add them (the live source of truth is always
`references/`).

## Files

| File | What it does | Needs |
|---|---|---|
| `skill_lib.py` | Snowflake dates, included-ids, theme/coverage/count helpers | — |
| `fetch_posts.py` | X API v2 extractor (original + quote + media, article-aware) | Bearer token |
| `update.py` | Delta-detect + fetch new + stage with distill prompts | Bearer token |
| `refresh_meta.py` | Recompute + patch README/SKILL counts & coverage | — |
| `distill.py` | *(optional)* Claude-API auto-draft from staged prompts | `anthropic`, API key |
| `discover_new.py` | *(optional)* List not-yet-included @richardrx posts | Bearer token |
| `prompts/distill.md` | The canonical distillation spec (single source of truth) | — |
| `posts.txt` | Full rebuild manifest (all source URLs) | — |
| `new_posts.txt` | Your input: candidate URLs to add | — |
