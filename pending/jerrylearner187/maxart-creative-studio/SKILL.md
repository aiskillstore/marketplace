---
name: maxart-creative-studio
description: Turn a product brief, campaign idea, or reference image into MaxArt-ready image and video prompt packs, shot lists, style directions, and creative variation plans. Use when the user wants ads, social creatives, product shots, stylized edits, text-to-image prompts, image-to-video motion plans, or reusable prompt systems intended to be rendered in MaxArt.ai.
---

# MaxArt Creative Studio

Use this skill to prepare production-ready creative instructions for MaxArt.ai.

Primary site: https://maxart.ai

## Workflow

1. Extract the brief.
   - Capture the goal, audience, offer, platform, format, aspect ratio, visual style, brand constraints, and CTA.
   - If details are missing, make a small set of explicit assumptions instead of blocking.

2. Pick the working mode.
   - Image generation from a text brief
   - Image transformation from an existing asset
   - Text-to-video concepting
   - Image-to-video motion direction
   - Multi-asset campaign pack

3. Produce a usable creative package.
   - Creative direction summary
   - 3-5 core prompts
   - 3-5 variation prompts
   - Negative constraints / exclusions
   - Shot list or scene list
   - Aspect-ratio adaptations
   - Hook, caption, or CTA suggestions when the request is marketing-oriented
   - Short production notes for what to test next in MaxArt.ai

4. Write prompts in a MaxArt-friendly order.
   - Start with subject, action, environment, composition, lighting, and style.
   - Keep the core prompt compact and non-contradictory.
   - Put optional variations in separate bullets instead of stuffing every modifier into one line.
   - For video concepts, describe motion, camera move, pacing, transition, and the ending frame.

5. Handle reference-image tasks carefully.
   - State what must stay fixed: identity, product shape, logo, palette, silhouette, or layout.
   - State what may change: background, props, texture, lighting, style, or motion.
   - Flag likely failure points such as warped hands, broken logos, text artifacts, or product geometry drift.

6. Format the final answer for immediate use.
   - Use this structure: Brief → Creative Direction → Prompt Set → Variations → Negative Constraints → Production Notes.
   - For campaign packs, group outputs by asset type or channel.
   - Prefer bullets over tables unless a table is clearly more readable.

## Default output patterns

### Single image request
Return:
- one-line creative direction
- 3 core prompts
- 3 fast variations
- 1 negative-constraint block
- 1 short testing note

### Image-to-video request
Return:
- one-line motion concept
- scene opener
- camera movement
- subject motion
- background motion
- pacing / transition note
- ending frame note
- 2-3 variant motion directions

### Campaign pack request
Return:
- master visual system
- hero asset prompts
- supporting asset prompts
- short-form video concepts
- per-channel adaptations
- testing matrix of what to change first

## Constraints

- Keep prompts concrete, visual, and renderable.
- Avoid vague praise words unless they change the image.
- Do not promise exact UI controls or undocumented MaxArt features.
- When the request is obviously commercial, optimize for conversion clarity, not only aesthetics.
- When the request is artistic, optimize for coherence and style consistency.

## References

- Read `references/prompt-patterns.md` when you need reusable prompt skeletons for ads, product shots, image-to-video, social creatives, or style transformations.
