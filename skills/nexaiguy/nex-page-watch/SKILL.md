---
name: nex-page-watch
description: 'Deploy a production-ready Manifest V3 Chrome extension for visual webpage monitoring and change alerts. Use when: Deploy a fully functional Manifest V3 extension with no build steps required; Implement visual diffing logic using offscreen documents for performance; Fork a proven ''action-on-click'' extension architecture for custom tools.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-page-watch
compatibility: Claude Code, Cursor, Windsurf, Aider, Cline
---

# Nex Page Watch

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-page-watch). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Nex Page Watch is a production-ready Chrome Extension (Manifest V3) that monitors web pages for content changes. It provides a complete, "no-build" codebase using vanilla JS, HTML, and CSS. When a monitored page changes, users receive a browser notification and a detailed visual diff highlighting additions, removals, and word-level modifications.

## Why use this skill

Unlike basic scaffolding prompts, this skill delivers a fully functional, shipped product. It bypasses the complexity of modern build chains, offering a "Load Unpacked" workflow that is perfect for rapid prototyping or immediate deployment. It solves the architectural challenge of performing heavy diffing operations in an extension by utilizing offscreen documents, ensuring the browser remain responsive.

## Supported architecture & features

- **Manifest V3:** Built on the latest Chrome extension standards.
- **Offscreen API:** Off-thread processing for performance-intensive diffing.
- **Alarms & Storage:** Reliable background scheduling and local data persistence.
- **Vanilla Stack:** Zero dependencies—no npm, no Webpack, no Vite.

## The Output

You receive the complete `assets/extension/` source directory containing the manifest, background scripts, content scripts, and UI files. The agent also provides a comprehensive guide on the developer loop, customization, and Web Store packaging steps.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Deploy a fully functional Manifest V3 extension with no build steps required.
- Implement visual diffing logic using offscreen documents for performance.
- Fork a proven 'action-on-click' extension architecture for custom tools.
- Schedule background webpage checks using the Chrome Alarms API.

## Known limitations

- Local storage only: no cloud sync.
- Browser based: requires Chrome to be active for background checks.
- Static diffing: may struggle with highly dynamic SPA content.

## Example

**Request**

I need a Chrome extension that alerts me when the price changes on a specific website. Can you provide the source for a page monitor?

**Result**

I've generated the Nex Page Watch extension in `/assets/extension/`.

Key components:
- `manifest.json`: Manifest V3 config
- `background.js`: Alarm-based scheduler
- `diff.js`: Visual diffing engine

To install: Open chrome://extensions, enable Developer Mode, and 'Load unpacked' the folder.

## Questions

### What exactly does the 'nex-page-watch-ext' skill generate?

This skill provides a complete, production-ready codebase for a Chrome Extension that tracks web content changes and sends desktop notifications when updates are detected, saving you from building complex monitoring logic from scratch.

### Do I need to install any development dependencies or build tools to use the code?

No external build tools like npm, Webpack, or Vite are required; the output uses a 'vanilla' stack (HTML/JS/CSS) designed to be loaded directly into Chrome via 'Load Unpacked' for immediate testing and deployment.

### What is included in the final output from the agent?

You receive the full source directory including the Manifest V3 file, background and content scripts, offscreen document logic for performance, and UI files, along with a guide for customization and Web Store packaging.

### Is the generated extension compatible with browsers other than Chrome?

Yes, because it uses standard Manifest V3 and vanilla JavaScript, the resulting extension is fully compatible with Google Chrome and other Chromium-based browsers like Microsoft Edge and Brave.

### How does the extension handle performance during complex page comparisons?

The skill utilizes Chrome's Offscreen API to handle data-heavy difference calculations (diffing) in a separate thread, ensuring that your browser remains fast and responsive even during intensive monitoring tasks.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
