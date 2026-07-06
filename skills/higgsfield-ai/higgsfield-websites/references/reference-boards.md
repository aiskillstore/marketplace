# reference-boards — design the page as IMAGES before writing code (Phase 1)

The single highest-leverage step in the pipeline. The reference boards ARE the
design: a generic board guarantees a generic site, and no amount of code craft
recovers from it. Budget real effort here.

## The output rule

Generate **ONE horizontal design-reference image PER SECTION** with
`higgsfield generate create <job_type> --prompt "…"` (strong model:
`gpt_image_2` or `nano_banana_pro`).
6 sections = 6 boards. Never one tall full-page image (detail gets mushy and
per-section composition variety dies). Aspect: 16:9 or 3:2, landscape.

Submit all boards as async jobs at once (no `--wait`; collect the printed job
ids), keep working while they render, poll `higgsfield generate wait <id>` /
`higgsfield generate get <id>`, download into the repo's `refs/` directory
(working artifact — NOT `app/public/`).

## The combinatorial pick (commit BEFORE prompting)

To avoid the AI defaults, pick ONE option per category, write the pick into
`app/design-brief.md`, and hold it across ALL boards. Do not mash categories;
pick a strong combination and execute it consistently.

- **Theme paradigm:** Pristine Light (paper/cream/off-white, dark ink) ·
  Deep Dark (charcoal/graphite — beware, most overused; needs a twist) ·
  Bold Studio Solid (oxblood, royal blue, forest, vermilion, emerald fields) ·
  Quiet Premium Neutral (bone, sand, taupe, stone, smoke).
- **Background character:** technical grid/dot field · solid with soft ambient
  depth · full-bleed cinematic imagery · tactile paper/material texture.
- **Typography character:** clean grotesk (Satoshi-like) · refined grotesk
  (Neue-Montreal-like) · expressive display (Cabinet/Clash-like) · compressed
  statement (Monument-like) · editorial serif + sans pairing · Swiss rational
  sans with hard hierarchy.
- **Hero architecture:** cinematic centered minimalist · asymmetric split ·
  floating polaroid scatter · inline typography behemoth · editorial offset ·
  massive image-first with restrained text.
- **Section system (dominant):** modular bento rhythm · alternating editorial
  blocks · poster-stacked storytelling · gallery-led cadence · Swiss grid
  discipline · asymmetric premium flow.
- **Signature components (pick 4):** diagonal staggered masonry · 3D cascading
  card deck · hover-accordion slices · gapless bento · brand marquee ·
  turning polaroid arc · vertical rhythm lines · off-grid editorial ·
  product UI panel stack · split testimonial wall · oversized metrics strip ·
  layered image crop frames.
- **Narrative spine (pick 1, thread everywhere):** artifact/collectible ·
  journey/waypoints · tool/precision instrument · living system/garden ·
  stage/spotlight · archive/dossier.
- **Second-read moment (pick exactly 1, place once):** asymmetric bleed ·
  one oversized numeral/punctuation as structure · one material switch ·
  narrow vertical side-rail note · macro crop carrying the brand color.

**Per-section variety (mandatory):** each board picks its own composition
anchor — centered statement, top-left lead, bottom-left over image,
off-grid offset, stacked center, image-as-canvas, inverted classic… At least
3 distinct anchors across the site, and the hero must NOT open on
left-text/right-image (the most overused AI pattern; use it at most once,
mid-page, if it's genuinely best). Background mode also varies per section
(solid + inline asset, duotone image, color-blocked diptych, graded
atmospheric photo, flat block + detail crop…).

**CTA variety:** boards should show different CTA garments per section
(underlined inline link + arrow, oversized headline + tiny CTA hint, framed
block, banner CTA, classic pill at most once). This feeds the bespoke-chrome
rule in the build phase.

## Palette bans (hard, also enforced by the Phase 5 gate)

Banned as default reaches — all four are documented AI tells:

1. **Graphite/near-black + orange/amber/ember accent** (`#FF4B1F`-family,
   `#F97316`, `#FF6B35`, amber-500…) — the "technical premium" default.
2. **Near-black + neon cyan/blue/green glow accent** (`#22d3ee`, `#00FFC2`,
   `#3B82F6`-on-zinc-950…) — the "AI dark SaaS" default.
3. **Beige/cream + brass/clay/oxblood** (see design-recipe.md §2 hexes) — the
   "premium craft" default.
4. **AI purple/violet glow** on anything.

Also banned: reusing the palette family of the previous build in the same
chat/session. Override any ban ONLY when the user's brand explicitly names
those colors. What to reach for instead: Bold Studio Solid fields (bottle
green, oxblood, royal blue, vermilion), chromatic lights (limestone, celadon,
warm grey + one unexpected saturated accent: chartreuse, vermilion-pink,
ultramarine), duotone photographic palettes. One accent, decisive, defended in
one line in the brief.

## Prompt recipe (per board)

"website design mockup, desktop landing page section, [SECTION ROLE], [theme
paradigm + exact palette words], [typography character] typography, [hero
architecture / composition anchor], [background mode], [narrative spine
motif], professional layout, clear hierarchy and spacing, award-winning web
design" — plus: "no watermark, no browser chrome". Boards are the design
source of truth — request the model's HIGH quality setting explicitly (don't
let it default to low). Name real content in the
prompt (the actual headline wording you plan) so type sits believably.

## The re-roll rule (mandatory — LOOK at every board)

Read every downloaded board image. For each, ask: "would this survive on a
studio's dribbble page, or does it read as a template?" If a board is generic
(centered dark hero, glowing gradient blob, default card trio, dashboard spam,
beige serif "luxury"), re-roll it with an escalated direction (push the
composition anchor harder, or swap the background mode). Budget: up to 2
re-rolls per build. A board that fails twice → change the category pick, not
just the wording.

## Hero-board minimalism rules

- Max 4 text elements visible in the hero board (eyebrow-or-nothing, headline,
  one sub-line, CTA). No feature lists, no floating UI clutter.
- Headline reads at a glance; typography IS the design.
- One focal visual (or decisive negative space) — not three competing objects.
- No fake dashboards / fake product UI unless the brief is a product with a UI.

## What each board must communicate

Layout grid, section hierarchy, spacing rhythm, typography scale
relationships, palette + accent placement, CTA priority, component styling,
image treatment. If a board can't answer "what does the build copy from
this?", it's mood art — re-roll it.
