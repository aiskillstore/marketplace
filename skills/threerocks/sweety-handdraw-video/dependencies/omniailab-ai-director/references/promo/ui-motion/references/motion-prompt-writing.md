---
name: omniailab-promo-ui-motion-motion-prompt-writing
description: 「Motion prompt writing」—— UI 动效与产品演示 方向细则：Read this file before writing any motion_prompt for video generation. 
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# Motion prompt writing

Read this file before writing any `motion_prompt` for video generation. Treat the prompt as a compact director's treatment with a visible timeline, not as a mood paragraph or a list of animation keywords.

## Quality target

For a 15-second take, write **at least 1000 Chinese characters or 600 English words**, with useful information in every paragraph. This is a hard minimum and a content-density target, not permission to pad with repeated adjectives.

- 6 seconds: 2–3 timed beats, about 400–800 Chinese characters or 250–450 English words.
- 10 seconds: 3–5 timed beats, about 700–1200 Chinese characters or 400–700 English words.
- 15 seconds: 5–7 timed beats, about 1000–1800 Chinese characters or 600–1000 English words.

For an intentionally minimal 15-second concept, reduce the number of simultaneous elements, not the prompt below this minimum: use the remaining space to specify spatial continuity, camera starts and landings, easing, depth reactions, transition carriers, readable settles, and the final hold. Apply the shorter ranges above only to 6-second and 10-second takes.

## Write in this order

1. **Creative line** — UI-motion category, product/concept, interaction agent (cursor, touch point, hand gesture, gaze, or abstract driver), and whether this is the opening segment or a local continuation. Duration, aspect ratio, resolution, and frame rate belong to storyboard/storyboard metadata and must not be repeated as prompt controls.
2. **Motion thesis** — name one recurring motion cause that unifies the film: a route line pulls every state forward, a card edge unfolds into the next surface, a cursor activates all changes, or a spatial ring becomes every subsequent layout.
3. **Visual and spatial system** — define brand colors, typography direction, material, foreground/midground/background, active/inactive hierarchy, and the one or two recurring motifs that survive across beats.
4. **Interaction grammar** — define hover, press, drag, release, snap, expansion, and confirmation behavior. Make every major animation visibly caused by an input or by the previous object's physical continuation.
5. **Camera and transition grammar** — choose a controlled camera vocabulary and a small family of transition bridges before writing the timeline.
6. **Timed beat sheet** — write the whole take in chronological blocks. Each block must describe cause, response, camera, bridge, and settle.
7. **Final state and focused constraints** — specify the last composition, hold duration, stable text/brand mark, and only the failure modes that are genuinely likely for this concept.

## Build every timed beat as a causal chain

For each beat, state all of the following in natural prose:

1. **Time + purpose** — for example `0.0–1.5s | extreme-close hook`.
2. **Trigger** — what the cursor, hand, gaze, route, sound pulse, or previous shape does.
3. **Primary response** — the main UI object changes position, scale, orientation, shape, material, or state.
4. **Secondary response** — nearby layers make room, guides draw, shadows/reflections change, inactive panels recede, or the environment reacts.
5. **Camera response** — name direction and purpose, not merely “dynamic camera”.
6. **Transition bridge** — identify the exact outgoing object that becomes, covers, reveals, or leads into the next beat.
7. **Settle** — give the viewer a readable landing moment before the next acceleration.

Use no more than one primary action and two secondary reactions at the same instant. Rich motion comes from linked consequences and depth, not from making every object move at once.

## Camera grammar

Choose 3–5 camera states for a 15-second take. Reuse them as a coherent path; do not stack every technique.

- **Extreme close-up → push-through**: begin on a material edge, waveform, route, icon, or card detail; move along it and pass through an opening to reveal the full workspace.
- **Dolly / push-in**: move closer when entering a selected state or showing precision. Name the target and what parallax changes in foreground, midground, and background.
- **Pull-back / zoom-out**: reveal that previously separate panels belong to one continuous system or canvas. Reserve this for a relationship reveal or final overview.
- **Orbit / arc move**: rotate around a spatial object or layered UI to expose thickness, occlusion, and hierarchy. Keep the subject anchored.
- **Tilt into top-down**: let a spatial stage flatten into a timeline, map, editor, or board while shared elements preserve identity.
- **Path-following move**: let the camera follow a route, connector, ribbon, waveform, or light node so the viewer always understands where the next state comes from.
- **Focus pull**: shift attention between a foreground control and a background result while keeping both spatially continuous.
- **Occlusion move**: pass behind a card edge, hand, object, door frame, foreground panel, or translucent layer to hide the seam without breaking the take.

Write camera motion with a start, target, direction, and landing. Prefer “the camera tracks along the coral route, pushes through its final ring, then settles in a three-quarter view of the 规划器” over “the camera moves dynamically”.

## Transition grammar

Use at least three explicit transition bridges in a 15-second take. Choose 2–4 related families so the film has a recognizable motion language.

- **Shared-element expansion** — a selected thumbnail, card, node, or image enlarges continuously into the next full view while its content remains identifiable.
- **Shape morph** — an edge, ring, path, waveform, panel, or glyph changes geometry into the next interface structure.
- **Foreground wipe / natural occlusion** — an object passes close to camera and its surface reveals the next state.
- **Path continuation** — a line, route, ribbon, glow, or connector exits one layout and draws the next layout into existence.
- **Depth pass-through** — push into a panel, node, lens, portal, or material layer and emerge inside its detailed state.
- **Fold / unfold / reassembly** — cards fold into a track, tracks roll into a spatial scene, or modules magnetically regroup into a new hierarchy.
- **Orientation change** — a 3D workspace tilts into top-down without cutting; objects keep their relative identity while becoming timeline or map elements.
- **Material or color propagation** — a controlled light, texture, or color wave travels from the active control into the next surface and reveals it.

Never stop at “smooth transition”, “the page changes”, or “the UI transforms”. Name the carrier, its path, what remains continuous, and the state it becomes.

## Energy curve for a 15-second take

Adapt this curve to the brand rather than copying the timings mechanically:

- **0.0–1.5s | hook** — use a visually decisive close detail, path, silhouette, or first interaction. Establish the recurring carrier immediately.
- **1.5–4.0s | reveal** — expose the main workspace through a push-through, unfolding surface, or shared-element expansion.
- **4.0–7.0s | interaction** — show one clear hover/press/drag/release chain with nearby UI reacting in depth.
- **7.0–10.5s | transformation** — change layout class or spatial orientation: card to canvas, node to editor, map to board, spatial scene to timeline.
- **10.5–13.3s | wow / system reveal** — combine previous states, use an orbit or pull-back, and show why the product is more than a single screen.
- **13.3–15.0s | resolve** — let the carrier form the end composition, then hold the stable brand/product state for 0.6–1.0 seconds.

Fast brands may shorten the settles and increase path speed. Premium or calm brands may use fewer beats with longer, more precise landings. Keep the same causal chain either way.

## Richness without chaos

- Keep one persistent visual anchor across the film: cursor, route, node, active card, product object, listener point, or brand glyph.
- Define foreground, midground, and background reactions whenever the camera moves. Use occlusion, shadow, reflection, scale, blur, and parallax to prove depth.
- Write micro-interactions numerically only when they improve control: press to 98%, small 2–4% settle, 0.3–0.6s magnetic snap. Avoid filling the prompt with arbitrary measurements.
- Give inactive UI a job: recede, dim, re-stack, remain world-anchored, or preserve context. Do not make it vanish without cause.
- Preserve object identity across transitions. Content should move, fold, stretch, or re-anchor instead of disappearing and being regenerated elsewhere.
- Use exact on-screen text once, keep it short, and state that it appears as a complete stable layer. Keep numbers static unless changing values are the product feature.
- Match motion intensity to the brand. “Cool” should come from confident spatial choreography, clear motion causality, and controlled contrast—not default glitch, flashing, or particle explosions.

## Prompt skeleton

Write the final `motion_prompt` as continuous prose using this skeleton, replacing every bracketed slot with concrete content:

```text
Create a premium UI motion film for [product]. This is [the opening segment / a continuation from the supplied previous tail frame]. The interaction agent is [agent]. The recurring motion cause is [carrier]; it must initiate or physically connect every major change. The visual system uses [brand palette, typography, materials], with [foreground/midground/background] and [active/inactive hierarchy].

[Camera grammar.] Use [3–5 chosen states] as one continuous path. [Transition grammar.] Connect beats through [2–4 chosen families]; preserve [shared objects] across every change.

[0.0–x.xs | purpose] [Trigger → primary response → secondary response → camera response → exact bridge → settle.]
[x.x–x.xs | purpose] [Trigger → primary response → secondary response → camera response → exact bridge → settle.]
[Continue until the whole take is covered.]

End on [exact stable composition]. Hold for [duration]. Keep [text/logo/numbers] complete and stable. Prioritize [concept-specific success conditions].
```

Do not copy the short “single motion prompt template” in a style file as the final prompt. Treat it only as a style-specific verb and motif seed, then expand it with this structure.

## Preflight

Before calling video generation, confirm:

- The whole requested duration is covered by non-overlapping time ranges.
- Every beat has a visible trigger or physical continuation.
- Every beat names a camera response and an exact bridge into the next beat.
- The prompt contains at least one push-in/push-through or focus move and one pull-back/orbit/overview when the concept benefits from spatial depth.
- At least three transitions preserve a shared object, path, surface, or occluder.
- Foreground, midground, and background do not all compete for attention.
- The final 0.6–1.0 seconds are stable enough to read.
- Brand color names, typography, real mark, and UI text match the brand profile.
- Aspect ratio, resolution, frame rate, and technical duration are absent from the prose prompt and present in storyboard/storyboard metadata.
- For segment N>1, the prompt begins from the supplied previous tail frame and never restages the opening.
- Removing repeated adjectives would not make the prompt shorter; if it would, remove them.

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
