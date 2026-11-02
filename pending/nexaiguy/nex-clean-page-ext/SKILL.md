---
name: nex-clean-page-ext
description: 'Deploy or fork a production-ready, no-build Manifest V3 Chrome extension that declutters websites in one click. Use when: Ship a ready-to-use website decluttering tool for the Chrome Web Store; Bootstrap a content-rewriter extension without setting up a build pipeline; Learn the Manifest V3 ''Load Unpacked'' dev loop with a real-world example.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-clean-page-ext
compatibility: Compatible with Claude Code, Cursor, and VS Code.
---

# Nex Clean Page Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-clean-page-ext). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Nex Clean Page is a production-ready Chrome Extension (Manifest V3) designed to declutter websites with a single click. It targets and hides common visual "noise" like cookie banners, chat widgets, sticky headers, and newsletter popups. Unlike simple scripts, it uses a sophisticated detection engine that classifies elements into categories, allowing for granular control and 100% reversibility without breaking the page DOM.

## Why use this skill

As a developer, building a robust Chrome Extension that handles dynamic DOM changes across various sites is time-consuming. This skill provides the complete, shipped source code of a real-world extension. It bypasses the complexity of modern build tools by using a vanilla JS/HTML/CSS pattern, making it extremely easy to debug, modify, and reload directly in the browser. It's the perfect foundation for anyone building a content-rewriter or a site-utility tool.

## Supported Features

- **Manifest V3 Compliant:** Uses the latest Chrome Extension standards for long-term support.
- **No-Build Architecture:** No npm, Webpack, or Vite required—edit and reload instantly.
- **Categorized Detection:** Includes dedicated logic for popups, chat widgets, and social sidebars.
- **State Management:** Uses chrome.storage to persist user preferences and restoration states.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Ship a ready-to-use website decluttering tool for the Chrome Web Store.
- Bootstrap a content-rewriter extension without setting up a build pipeline.
- Learn the Manifest V3 'Load Unpacked' dev loop with a real-world example.
- Implement non-destructive DOM hiding for better reading experiences.

## Known limitations

- Cannot remove elements within iFrames or Shadow DOM.
- Requires manual reload in chrome://extensions after edits.
- Visual noise detection is heuristic based.

## Example

**Request**

I need to build a Chrome extension that removes annoying popups and sticky headers from websites. Give me the source code for a tool like that.

**Result**

I've generated the full source code for the Nex Clean Page extension in assets/extension/. This includes the Manifest V3 configuration, the content.js declutter engine, and the detectors category system. You can load it immediately via 'Load unpacked' in chrome://extensions.

## Questions

### What specifically does the nex-clean-page-ext skill provide to a developer?

This skill provides the full source code for a production-ready Chrome Extension that removes web clutter like cookie banners and popups without needing complex build tools. Use it to launch your own utility tool or as a clean foundation for advanced content-rewriting projects.

### Do I need to install Node.js or other build tools to use this extension source?

No, this is a no-build Manifest V3 project using vanilla JavaScript, HTML, and CSS. You can modify the code and see changes immediately by refreshing the extension in Chrome, skipping the need for npm, Webpack, or Vite.

### How does the extension handle website elements without breaking the page layout?

The skill uses a categorized detection engine that identifies and hides elements like chat widgets and sticky headers without deleting them from the DOM. This ensures 100% reversibility and prevents website functionality from breaking.

### What exactly is included in the purchase?

You will receive the complete, documented source code including the manifest file, background scripts, content scripts, and UI assets. It is fully ready to be loaded into Chrome's developer mode or forked for your own custom features.

### Is this extension compatible with the latest Google Chrome requirements?

Yes, the extension is built on the Manifest V3 standard, ensuring long-term compatibility with the Google Chrome Web Store. It also utilizes chrome.storage to maintain user preferences across different browsing sessions.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
