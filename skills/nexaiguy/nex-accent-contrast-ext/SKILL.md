---
name: nex-accent-contrast-ext
description: 'Ship a Manifest V3 Chrome extension that applies a custom accent color theme across any website. Use when: Generate a production-ready Manifest V3 extension without manual scaffolding; Apply dynamic color themes to third-party websites via CSS injection; Learn HSL color math for generating UI states (hover/active) from a single hex.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-accent-contrast-ext
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Windsurf.
---

# Nex Accent Contrast Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-accent-contrast-ext). Scripts, extension source, and templates from the original package are not in this folder.

## Build a Global Site Recolor Extension

Nex Accent is a professional-grade Chrome Extension (Manifest V3) that acts like Dark Reader, but for custom accent colors. It provides a complete, production-ready codebase for dynamically recoloring every website a user visits using a single hex code. Instead of starting from scratch, this skill delivers the full source code for a "content-rewriter" extension that handles the complex math and CSS overrides required to theme the web.

## Advanced Color Engineering

The skill features a sophisticated HSL math engine that generates a unified palette—including hover states, active states, borders, and muted tones—from one input color. It solves the "style specificity" problem by injecting high-priority stylesheets at `document_start`, ensuring your custom theme overrides heavy frameworks like Tailwind, Bootstrap, and Material UI without flickering.

## No-Build Workflow

This is a vanilla JS/HTML/CSS implementation. There are no heavy dependencies, no `npm install`, and no bundler required. You get a raw, performant dev loop: edit the code, click refresh in Chrome, and see the results instantly.

- Manifest V3 compliant (Service Workers, Scripting API).
- Per-domain settings with local storage persistence.
- Custom CSS escape hatch for power users.
- High-specificity selector engine for global compatibility.
- Complete assets: icons, popups, and settings pages.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Generate a production-ready Manifest V3 extension without manual scaffolding.
- Apply dynamic color themes to third-party websites via CSS injection.
- Learn HSL color math for generating UI states (hover/active) from a single hex.
- Build a domain-specific site styler with per-page toggle settings.

## Known limitations

- Not for extensions requiring React/Vue build steps.
- Global CSS injection may conflict with some shadow DOM elements.
- Restricted on protected Chrome store pages.

## Example

**Request**

Build me a Chrome extension that changes every website's primary color to #ff5733 with a toggle for each site.

**Result**

I've deployed the Nex Accent extension source to /assets/extension/.

Key features:
- Core: Manifest V3 with HSL palette generation.
- Logic: content.js handles high-specificity CSS injection.
- UI: Popup toggle and per-domain intensity settings.
- Build: No-build vanilla JS pattern.

## Questions

### What is the primary benefit of the nex-accent-contrast-ext skill?

This skill delivers a production-ready Manifest V3 source code package for a 'Global Recolor' extension, handling complex CSS overrides and HSL color math that are usually difficult to build from scratch.

### How does it handle the styling of different websites?

The extension identifies key UI elements across any website and applies a unified theme—including hover and active states—using high-priority CSS injection to ensure it works even on sites using Tailwind or Bootstrap.

### Do I need to install heavy dependencies or use a bundler to use this code?

No, this is a vanilla JS/HTML/CSS implementation that requires no 'npm install' or complex build tools, allowing for a fast development loop and easy customization.

### Is the provided code compatible with the latest Chrome Manifest V3 requirements?

Yes, the codebase is fully compliant with Manifest V3 standards, utilizing Service Workers and the modern Scripting API for maximum security and browser performance.

### What exactly is included in the purchase?

You receive the complete source code, including the manifest file, the HSL color engine, popup UI components, settings page UI, and a suite of icons.

### Which AI agents or IDEs can I use with this skill?

Since it is written in standard JavaScript, this skill is compatible with any AI coding agent that can process directory structures, such as Cursor, Replit Agent, or GitHub Copilot.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
