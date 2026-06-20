# VisionCraft — Prompt Guide

How to write prompts that get great results from the Agnes AI models. Read this when a user's request is vague and you want to suggest a richer prompt before running a script.

---

## Image prompts (agnes-image-2.1-flash)

### Recommended structure

```
[Subject] + [Scene/Environment] + [Style] + [Lighting] + [Composition] + [Quality]
```

### Examples

**Text-to-image (high information density):**
> A large fantasy harbor city built on cliffs, hundreds of small boats, layered stone bridges, glowing windows, distant mountains, cloudy sunset sky, cinematic fantasy realism, wide-angle composition, rich architectural details, high visual density

**Text-to-image (product):**
> A premium product hero shot of a luxury watch on dark marble, dramatic spotlight, water droplets, sharp reflections, cinematic commercial photography, ultra detailed

### Image-to-image: always state what to change AND what to preserve

Structure:
```
[What to change] + [New style/scene] + [Elements to add/remove] + [What to preserve]
```

Example:
> Convert the daytime street scene into a rain-soaked cyberpunk night, add neon signs and wet road reflections, preserve the original street layout, camera angle, and main building shapes

The model's headline strength is **high-information-density imagery** — complex scenes with many elements, rich compositions, dense detail. Lean into that rather than asking for minimal/sparse scenes.

---

## Video prompts (agnes-video-v2.0)

### Recommended structure

```
[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]
```

### Per-mode guidance

| Mode | What to emphasize |
|------|-------------------|
| Text-to-video | Subject action + camera movement + lighting |
| Image-to-video | What moves vs. what stays stable (face, outfit, layout) |
| Multi-image | Relationship between inputs + how the scene transitions |
| Keyframes | The transition relationship between the two frames |

### Examples

**Text-to-video:**
> A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style

**Image-to-video (state motion + stability):**
> Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent

**Keyframes (state the transition):**
> Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes

---

## General tips

- Prefer **specific over generic**. "cinematic realism, warm golden light" beats "beautiful, nice".
- Name a **camera/lens** for photos: "85mm portrait, shallow depth of field", "anamorphic lens".
- For image-to-image, **"preserve original composition"** is almost always worth including.
- Add a **negative prompt** for videos (`-NegativePrompt`) to exclude: `"blurry, distorted faces, watermark, text"`.
