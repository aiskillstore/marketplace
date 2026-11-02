---
name: nex-font-grab-ext
description: 'Ship a professional Chrome extension that identifies fonts, extracts CSS, and finds Google Font matches. Use when: Extract CSS and Tailwind font styles from any website instantly; Identify paid fonts and find their closest free Google Font alternatives; Fork a production-ready Manifest V3 overlay extension archetype.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-font-grab-ext
compatibility: Claude Code, Cursor, Windsurf, Aider, and Cline
---

# Nex Font Grab Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-font-grab-ext). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Nex Font Grab is a professional-grade Manifest V3 Chrome extension that allows users to identify fonts on any webpage with a single click. It provides an inspector-style overlay to extract CSS properties (font-family, size, weight, line-height, etc.) and instantly suggests the closest free Google Font alternative using a built-in mapping database.

## Why use this skill

Instead of prompting an AI to write a complex Chrome extension from scratch—which often results in broken background scripts or permission errors—this skill delivers a battle-tested, shipped codebase. It follows the "no-build" pattern, using vanilla JS, HTML, and CSS, making it perfect for developers who want a high-performance extension without the overhead of Webpack or React.

## What you get

- **Complete Source:** Ready-to-load Manifest V3 directory including content scripts, background workers, and UI panels.
- **Google Font Mapping:** A JSON database of 70+ paid-to-free font mappings.
- **Multiple Exports:** Instant copy-paste support for standard CSS, shorthand CSS, and Tailwind classes.
- **Deployment Guide:** Step-by-step instructions for loading unpacked extensions and packaging for the Chrome Web Store.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Extract CSS and Tailwind font styles from any website instantly
- Identify paid fonts and find their closest free Google Font alternatives
- Fork a production-ready Manifest V3 overlay extension archetype
- Learn the no-build Chrome extension development and deployment lifecycle

## Known limitations

- Vanilla JS only: no support for React/Vue frameworks.
- Local mapping: Google Font matches are limited to the included 70+ font JSON database.

## Example

**Request**

I need a Chrome extension that identifies fonts and finds free Google Font alternatives. Give me the code and show me how to load it.

**Result**

I've generated the Nex Font Grab source in `assets/extension/`.

To load it:
1. Go to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the folder.

The font matching logic is in `fontmatch.js` and the CSS extraction in `content.js`.

## Questions

### What exactly is included in the nex-font-grab-ext package?

You will receive a complete, ready-to-use Manifest V3 source directory containing the content scripts, background workers, a JSON font-mapping database, and a deployment guide for the Chrome Web Store.

### How does this skill differ from simply asking an AI to write a font-picker extension?

Unlike AI-generated scripts that often struggle with background permissions, this skill provides a battle-tested codebase that correctly handles Manifest V3 architecture and includes a curated database for matching paid fonts to Google Font alternatives.

### What technical stack is used, and will I need to install any frameworks?

The extension is built with a 'no-build' philosophy using vanilla JavaScript, HTML, and CSS, ensuring high performance and easy modifications without needing Webpack, React, or complex dependencies.

### Can I export the identified font styles directly into my code?

Yes, the skill includes a 'Multiple Exports' feature that allows you to instantly copy font data as standard CSS, shorthand CSS, or Tailwind utility classes for your projects.

### Is this extension ready for immediate use, or do I need to configure it?

Installation is straightforward; the included guide walks you through loading the files as an 'unpacked extension' in Chrome Developer Mode, making it functional in seconds.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
