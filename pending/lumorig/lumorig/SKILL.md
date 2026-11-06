---
name: lumorig
description: Create, rebuild, animate, and ship brand mascots with Lumorig — generate a new rigged vector mascot from a description or rebuild an existing mascot image, add animations (instant presets or described motion), and export Lottie/SVG/GIF/MP4/stickers or a live <lumorig-player> embed. Use when the user wants a mascot, character, animated brand avatar, chatbot avatar, empty-state illustration, or loading/celebration animation for their app or site.
---

# Lumorig

Lumorig turns a description (or an existing mascot image) into a **rigged vector character** that animates cleanly and exports as true-vector Lottie/SVG, video, stickers, or a live web embed.

## Pick an interface
- **MCP tools available** (`create_mascot`, `animate_mascot`, …): use them — they wait for jobs and show previews.
- **CLI** (`lumorig`, from `npx lumorig`): good for scripts and saving files into the repo.
- **REST API**: `https://lumorig.com/api/v1`, `Authorization: Bearer $LUMORIG_API_KEY`. OpenAPI: `/api/v1/openapi.json`.

## Workflow
1. **Create.** From a prompt: be specific about who the mascot is (species/object, personality, brand, 1–2 signature details) and pick a style: `outlined`, `flat`, `kawaii`, `soft3d`, `retro`, `pixelish`. From an image: pass the file/URL; results include a `fidelity` score — if `needs_review` is true, show the user the side-by-side before building on it.
2. **Animate.** Presets are instant and free: `idle wave nod shake bounce celebrate jump talk sad surprised dance think working listen sleep` (with `intensity` 0.5–1.5). For anything else, describe the motion ("hops twice, then does a tiny bow").
3. **Ship.**
   - Web: `<script type="module" src="https://lumorig.com/player.js"></script>` + `<lumorig-player src="<bundle_url>" animation="wave" trigger="hover" follow-cursor>`; React: render the same `<lumorig-player>` element after loading player.js (React supports custom elements).
   - Files: `lottie` (smallest, vector), `animated-svg` (no JS), `webm` (alpha video), `mp4`, `gif`, `sticker`, `logo` (vector badge), `png`/`svg` stills.
   - Interactive states: create a canvas from a template (`chatbot`: listening/thinking/talking; `ai_agent`: status 0–4; `onboarding`: hello/success/error triggers), then `player.canvas = "<name>"; player.setInput("thinking", true)`.

## Tips
- Recolor by palette token is instant (`recolor_mascot` / `lumorig recolor <id> fur=#3b82f6`); prefer it over an AI edit for color changes.
- Use a **variant** (not an edit) for outfits/seasonal looks (`edit_mascot` with `variant_name`): it becomes a new look and the current one is kept; `switch_look` switches (free). All animations keep working.
- For something held or worn that should come and go (a mug, a crown), use `add_prop`; `set_props` shows or hides it for free. An embed can pick a look or hide a prop for itself: `<lumorig-player look="Winter" props="mug:off">`.
- Private mascots embed via expiring signed links; make the mascot `public` for permanent embeds.
- Generation takes 1–4 minutes and uses credits; presets and recolors are free. Downloads are free on Maker and Studio; on Free, a character's first download costs 50 credits and unlocks all its downloads (every animation, watermarked, up to 512 px).
