# IP as Logo

`ip-as-logo` is a compact Agent Skill for generating highly simplified personified mascot logos. It treats the result as a logo first and a character second: bold rounded silhouettes, strict complexity limits, oversized corner composition, and extremely subtle neo-skeuomorphic shading.

It follows the open Agent Skills format and is designed to work with any compatible AI agent, rather than being tied to a specific agent product.

![IP as Logo showcase](assets/ip-as-logo-wall.webp)

## What it enforces

- One dominant silhouette built from roughly 6–10 basic shapes
- Three semantic colors by default: two IP base colors plus one background color
- Three proposed directions followed by six independently generated candidates after user approval
- A quantified restrained-color default: softened chromatic backgrounds, warm neutrals, and explicit silhouette/detail contrast targets
- Thick, rounded forms without sharp or fragile details
- A 75–85% lower-corner crop with paired identifying features preserved
- Flat-first artwork with continuous low-frequency gradients capped at `0.08` OKLCH lightness span
- Opaque square output without an App-icon mask, border, or transparent margin
- Explicit rejection rules for illustration-level complexity, pure flatness, and excessive 3D volume

## Install

Install the complete skill with the Agent Skills CLI:

```bash
npx skills@latest add s1dashu/ip-as-logo-skill
```

The installer detects the repository's root `SKILL.md`, lets you choose a supported coding agent, and installs the complete `ip-as-logo` directory, including its supporting assets. Use `--global` for a personal installation available across projects:

```bash
npx skills@latest add s1dashu/ip-as-logo-skill --global
```

## Agent compatibility

Supported agents include **Codex, Coze, Doubao, YouMind, Manus, Gemini Apps, and Replit Agent**. This skill only supports agents with built-in image-generation capabilities that can return generated images as assets.

## Use

Ask your AI agent for an IP mascot logo, for example:

```text
Create a rounded ghost IP logo on a deep navy background.
```

The skill does not ask for a color-mode choice by default. Every default candidate uses three semantic colors: two IP base colors plus one background color. It no longer reserves any fraction of the candidate set for two-color logos. Closely related highlight and shade variants may be introduced around either IP base color for the ultra-light neo-skeuomorphic effect without counting as additional semantic colors. A two-color logo is generated only when the user explicitly requests it, and then uses background-colored negative space for facial marks rather than introducing a third color.

When the user already names an IP subject, the skill proposes three controlled design treatments of that subject. When the subject is open, it proposes three genuinely different IP directions tied to different product attributes or brand promises.

If the skill runs inside a product repository, it inspects relevant read-only context before asking questions. If product context is insufficient, it asks one consolidated round of background questions. Once context is sufficient, it always presents three concise directions and proposes generating six independent images. It proceeds after the user agrees, or immediately when the user has already explicitly authorized six outputs.

When the user accepts all three directions, the default batch contains two variants per direction: `A1`, `A2`, `B1`, `B2`, `C1`, and `C2`. When the user selects one direction, the skill generates six controlled variants of that direction. If the user rejects the proposed quantity or distribution, their replacement instructions take precedence.

Compatible agents may generate the six candidates in parallel with subagents up to the runtime's available concurrency, using additional waves when needed. Codex can use ImageGen when available; other agent environments may use any configured image generator. If no generator is available, the skill asks the user to provide or enable one instead of pretending that an image was generated. Every result is a separate full-resolution square asset, never a six-logo contact sheet.

When the user does not supply a palette, the skill favors clearly chromatic but restrained backgrounds rather than neon color or muddy gray. It uses OKLCH target bands when numeric control is available, prefers warm off-white with charcoal or deep navy, and keeps the normal design to exactly three semantic colors: two IP base colors plus the background. Ultra-light highlight and shade variants must remain close to their corresponding IP base color.

## Repository structure

```text
SKILL.md
assets/ip-as-logo-wall.webp
README.md
LICENSE
```

The skill itself intentionally consists of a single instruction document. The repository also includes the showcase image above, but no scripts, style references, or generation dependencies.

## Model behavior

Image-generation models may still introduce background gradients, crop paired features, replace continuous micro-gradients with layered color patches, or add too much volume. The skill treats those as failures to report or retry, rather than silently claiming compliance or repairing the image after generation.

## License

MIT
