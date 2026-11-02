---
name: nex-meeting-finder
description: 'Deploy a production-ready Manifest V3 extension that detects meeting links and injects Join buttons into any webpage. Use when: Deploy a fully functional "Meeting Finder" extension to the Chrome Web Store; Bootstrap a content-rewriter extension using a proven Manifest V3 template; Add platform-specific badges and buttons to any website dynamically.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-meeting-finder
compatibility: Claude Code, Cursor, Aider, Windsurf, and Cline.
---

# Nex Meeting Finder

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-meeting-finder). Scripts, extension source, and templates from the original package are not in this folder.

## Ship a Professional Chrome Extension in Minutes

The Nex Meeting Finder is a battle-tested, production-ready Manifest V3 Chrome extension. It automatically detects meeting links from ten major platforms (Zoom, Meet, Teams, etc.) and injects interactive 'Join' buttons directly into web pages.

## What it does

- **Real-time Detection:** Scans pages for meeting links and bare-text URLs using a robust MutationObserver for dynamic apps like Slack and Gmail.
- **Smart UI Injection:** Adds platform-themed badges and quick-join buttons without breaking the host site's layout.
- **Time Parsing:** Extracts meeting times from surrounding text to provide context in the extension popup.
- **Full Management:** Includes a popup for weekly stats, a settings dashboard, and local storage persistence.

## Why use this skill?

Instead of prompting an AI for snippets and debugging manifest errors yourself, this skill delivers the **exact source code of a shipped product**. It uses a zero-build, vanilla JS/HTML/CSS architecture, meaning you can load it into Chrome immediately—no npm, no bundlers, and no setup headaches. It serves as both a functional tool and a perfect "copy-paste" template for any content-rewriter extension.

## What you get

A complete `/extension` directory containing the manifest, content scripts, background workers, and UI assets, plus a guided developer loop for customization and Web Store publishing.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Deploy a fully functional "Meeting Finder" extension to the Chrome Web Store
- Bootstrap a content-rewriter extension using a proven Manifest V3 template
- Add platform-specific badges and buttons to any website dynamically
- Implement smart time-parsing from unstructured web text for schedules

## Known limitations

- No build step: not for React/Vue frameworks.
- Client-side only: no cloud link sync.
- Regex-based: might miss links in obfuscated code.

## Example

**Request**

I need a Chrome extension that finds Zoom and Google Meet links on a page and adds a Join button next to them. Can you give me the source code?

**Result**

I have generated the full Manifest V3 source code in `assets/extension/`.

Key files included:
- `manifest.json`: Configured with required permissions.
- `content.js`: Handles link detection and button injection.
- `platforms.js`: Definitions for Zoom, Meet, Teams, etc.
- `popup.html`: The UI for your meeting list.

## Questions

### What problem does the Nex Meeting Finder extension solve?

This skill provides the full source code for a production-ready Chrome extension that automatically identifies meeting links on any webpage and adds interactive 'Join' buttons, eliminating the need to copy-paste URLs manually.

### What exactly is included in the download?

You receive a complete /extension directory including the Manifest V3 configuration, content scripts for link detection, background workers, and the full UI source code for the popup and settings dashboard.

### Do I need to install any dependencies or build tools to use this code?

The extension uses a zero-build architecture with vanilla JavaScript, HTML, and CSS, meaning you can load it directly into Chrome via 'Developer Mode' without needing to run npm, Webpack, or other complex build tools.

### Is this extension compatible with the latest Chrome standards?

Yes, the extension is built on Manifest V3, the current industry standard, making it fully compatible with the latest versions of Google Chrome, Microsoft Edge, and other Chromium-based browsers.

### Can I customize the skill to detect other types of links or data?

Absolutely; while it works out-of-the-box for meeting links, the codebase is designed as a modular template that can be easily repurposed to detect and highlight any specific type of data or text across the web.

### Which meeting platforms can the extension currently detect?

The skill supports ten major platforms, including Zoom, Google Meet, Microsoft Teams, Webex, and Skype, using a robust observer system that works even on dynamic sites like Gmail and Slack.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
