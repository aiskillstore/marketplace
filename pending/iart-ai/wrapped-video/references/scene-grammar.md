# Scene grammar: the Wrapped storyboard

A Wrapped is not a freeform film. It is a fixed sequence of short, reusable scene *types*, each a slot a data row fills. Lock the grammar once; only the data and palette change each year. This is why one template scales to millions of personalized videos.

## The crescendo

Order scenes so personal stakes rise toward a climax, then resolve on a still share card:

1. **Context first** — small, framing facts ("you listened on 287 days").
2. **Build** — top-X lists, genres, time patterns.
3. **Climax** — the single most personal/impressive stat (the percentile, the hero number), held longest and largest.
4. **Resolve** — outro share card, motion settles to a clean freeze.

Never open on the biggest number; there is nowhere to go after it. Never end on motion; the last frame must be a clean, screenshot-ready card.

## A full 7-scene storyboard (22s @ 30fps = 660 frames)

| # | Scene | Frames | Sec | Beat |
|---|---|---|---|---|
| 1 | Intro: "{name}, your {year} wrapped" | 0–90 | 0–3 | Brand + palette set |
| 2 | Big number: minutes listened | 90–210 | 3–7 | First count-up, hero scale |
| 3 | Top-5 artists, staggered | 210–330 | 7–11 | Ranked list builds 1→5 |
| 4 | Top genre / persona card | 330–420 | 11–14 | "You're an Indie Explorer" |
| 5 | Percentile: "top {x}% of listeners" | 420–540 | 14–18 | Bar fills, climax stat |
| 6 | Peak month / heatmap | 540–600 | 18–20 | "March was your month" |
| 7 | Outro share card (holds still) | 600–660 | 20–22 | Logo + handle + CTA, frozen |

Scale by stretching/trimming the montage scenes (3–6), never the intro or the count-up payoffs. For 15s, drop scenes 4 and 6. For 45s, add a second list (top tracks) and a comparison scene.

## Scene-type recipes

**Intro.** Big name + year, palette wash. One line of motion: name slides/fades up over a gradient using the per-user `accent`. Sets the visual identity for the whole film.

**Big-number reveal.** One number, oversized (180–240px), counts up with a spring, label below. Nothing else on screen. This is the most-shared scene type — give it room.

**Top-X list.** Ranks 1→5 enter staggered (rank 1 first), each `{rank, label, value}`. Rank number small and accent-colored, label bold white, value muted. The stagger *is* the animation; keep each row's motion identical.

**Superlative / persona.** Map data to a named archetype ("Indie Explorer", "Night Owl", "Top Fan"). Compute the label from thresholds so it personalizes automatically. Big label, one supporting line.

**Comparison / percentile.** "More than 92% of listeners." A horizontal bar fills to `percentile`, number counts up alongside. Strongest dopamine scene — usually the climax.

**Time / peak.** "Your busiest month was March." A simple 12-bar mini-chart with the peak bar in accent, others muted. Reads instantly even frozen.

**Outro share card.** Holds **completely still ≥2s**. Name, @handle, product logo, short CTA/URL. No competing motion. This frame is the share asset — design it as a poster.

## Copywriting patterns (data → words)

Generate headline copy from the data, not hand-written per user:

- **Superlative tiers:** `percentile <= 1 ? "Top 1% — you're a superfan" : percentile <= 10 ? "Top 10%" : "..."`.
- **Persona from dominant dimension:** pick the archetype whose threshold the row clears (genre share, late-night ratio, diversity count).
- **Comparison framing:** always "more than X% of {peers}" — concrete peer group beats abstract numbers.
- **Second person, present, short.** "You listened to 412 artists." Not "The user listened to..." Each line ≤ 7 words so it fits one bold frame.

## 9:16 safe-area map

Render **1080×1920**. Story/Reels/TikTok UI overlays the edges and the platform may crop.

| Zone | Region | Rule |
|---|---|---|
| Top 12% | 0–230px | Avoid type; platform clock/handle/close-button sit here |
| Bottom 18% | 1575–1920px | Avoid type/CTA; like/share/caption UI sits here |
| Center 80% h | ~230–1575px | All numbers, names, lists, the share CTA |
| Horizontal | center 90% w | Keep big type off the left/right 5% |

Place the single most important element at vertical center (~960px) — it survives every crop and is where the eye lands. Test by overlaying a TikTok/Reels UI mock and confirming no number is occluded.

## Motion language

Keep one motion vocabulary across all scenes so the film reads as one piece: same spring config for entrances, same fade for exits, accent color used consistently for "the number that matters." Consistency makes speed feel like confidence rather than chaos. Per-scene component code is in `remotion-recipes.md`.
