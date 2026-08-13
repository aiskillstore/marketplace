# Prompt guide — flux-2 (flux-2-pro, flux-2-klein-4b)

Order the elements subject, action, style, context — position carries weight, most important first.
Lighting and camera close the chain; leave them unstated and they get chosen for you. For fine
multi-element control, prompt in JSON (`scene`, `subjects`, `camera`). Write the detail in yourself
rather than relying on the model to expand a sparse prompt.

- **Exclusions** — negative prompts are unsupported; describe what belongs, not what to omit.
- **Length** — 10–30 words explores, 30–80 typical, 80+ for complex scenes.
- **Photographic look** — name era, camera, lens, film stock, grain and light, not a quality label.
- **On-image text** — quote the literal string; give placement, type style, size, colour. Text rendering can be imperfect, so keep it short and essential.
- **Colour** — precede a hex code with `color` or `hex`, bound to a named object; gradients by start and end colours.
- **Multi-reference editing** — character consistency and composites; state each reference's job.
