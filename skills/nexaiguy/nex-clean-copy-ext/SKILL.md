---
name: nex-clean-copy-ext
description: 'A production-ready Manifest V3 extension to strip tracking parameters and hidden Unicode from copied text. Use when: Ship a functional ''Clean Copy'' extension to the Chrome Web Store in minutes; Strip invisible tracking pixels and hidden Unicode from hijacked clipboard text; Create a custom URL shortener or sanitizer using a proven MV3 archetype.'
license: MIT
metadata:
  author: Nex AI
  version: '1.3'
  agensi-slug: nex-clean-copy-ext
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Clean Copy Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-clean-copy-ext). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

This skill provides the complete, production-ready source code for the Nex Clean Copy Chrome extension. It implements a sophisticated content-rewriter pipeline that intercepts copy events to strip away hidden junk. It automatically removes zero-width characters (BOM, soft hyphens, joiners), invisible Unicode directional marks, and invasive URL tracking parameters like utm\_\*, fbclid, and gclid.

## Why use this skill

While generic AI prompts can help you write individual functions, this skill delivers a fully integrated Manifest V3 architecture that is already tested and "shipped." It follows a high-performance vanilla JS/HTML/CSS pattern with **zero build steps**, meaning no npm overhead or transpilation is required. It's the perfect technical foundation for developers who need a working content-rewriter archetype to fork, customize, and deploy immediately.

## Supported Features

- **Manifest V3 Compliant:** Uses the latest Chrome extension standards.
- **Modular Cleaning Pipeline:** Dedicated logic for Unicode stripping and URL parameter filtering.
- **UI Included:** Full popup and settings pages for user-toggled cleaning categories.
- **No-Build Workflow:** Edit and reload directly in the browser for instant feedback.
- **Store Ready:** Includes packaging instructions and manifest configurations for the Chrome Web Store.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Ship a functional 'Clean Copy' extension to the Chrome Web Store in minutes
- Strip invisible tracking pixels and hidden Unicode from hijacked clipboard text
- Create a custom URL shortener or sanitizer using a proven MV3 archetype
- Learn the 'no-build' Chrome extension development loop with vanilla JS

## Known limitations

- Cannot clean text in system dialogs or apps outside Chrome.
- Heavily obfuscated tracking URLs may require custom regex.
- No support for build-step frameworks like React/Vue.

## Example

**Request**

I need a Chrome extension that strips UTM parameters and hidden characters when I copy text.

**Result**

I've generated the 'assets/extension/' folder with the full Manifest V3 source. You can now load this as an 'unpacked extension' in Chrome. It includes cleaner.js for stripping tracking params and content.js for clipboard interception. To test, just copy a URL with ?utm_source=test attached.

## Questions

### What exactly does the nex-clean-copy-ext skill provide?

This skill provides the full source code for a Manifest V3 Chrome extension that automatically strips tracking parameters (like UTM tags) and invisible Unicode characters from your clipboard when you copy text.

### Do I need to set up a complex development environment or use build tools?

No, this is a 'no-build' project using vanilla JavaScript, HTML, and CSS, allowing you to load it directly into Chrome's developer mode and see changes instantly without npm or Webpack.

### What files and assets are included in my purchase?

You receive the complete production-ready source code, including the manifest.json file, cleaning logic modules, the user interface (popup/settings), and deployment documentation.

### Which browsers and platforms is this extension compatible with?

The extension is built on the latest Manifest V3 standard, making it compatible with Google Chrome, Brave, MS Edge, and other Chromium-based browsers that support the V3 API.

### Can I customize the cleaning logic to remove specific internal tracking tags?

Absolutely; the modular architecture is designed as a technical archetype, making it easy for developers to add custom regex filters or additional cleaning steps to the processing pipeline.

### Is the code ready for submission to the official Chrome Web Store?

Yes, the included documentation provides step-by-step instructions on how to package the source code and configure the manifest for submission to the Chrome Web Store.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
