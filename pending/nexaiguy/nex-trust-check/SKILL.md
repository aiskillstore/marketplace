---
name: nex-trust-check
description: 'Deploy or fork a production-ready Chrome extension for AI text detection and fake review analysis. Use when: Ship a complete AI-text detection extension to the Chrome Web Store; Create a custom content-rewriter extension using a proven MV3 scaffold; Add fake-review detection features to an existing browser tool.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-trust-check
compatibility: Claude Code, Cursor, Windsurf, Aider, Cline, VS Code
---

# Nex Trust Check

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-trust-check). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Nex Trust Check is a production-ready Chrome Extension (Manifest V3) that detects AI-generated text and fraudulent reviews in real-time. It analyzes text patterns locally via a side panel, providing users with a "trust score." This skill provides the complete high-fidelity source code—the exact same code shipped by Nex—and guides you through the process of loading, customizing, and publishing the extension.

## Why use this skill

Building a Chrome Extension from scratch involves navigating complex Manifest V3 requirements and cross-script communication. This skill bypasses the "blank page" problem by delivering a fully functional, already-shipped product. It follows a "no-build" philosophy (vanilla JS, HTML, and CSS), meaning there are no complex build steps, transpilers, or npm dependencies to manage.

## Supported Tools

- Manifest V3 Architecture
- Chrome Extension APIs (activeTab, scripting, storage, contextMenus)
- Vanilla JavaScript (No-build pattern)
- Heuristic Content Analysis Engine

## What you get

You receive the full source code (manifest, content scripts, background workers, and UI components) along with a developer loop for rapid iteration and a checklist for Chrome Web Store submission.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Ship a complete AI-text detection extension to the Chrome Web Store
- Create a custom content-rewriter extension using a proven MV3 scaffold
- Add fake-review detection features to an existing browser tool
- Learn MV3 development with a "no-build" vanilla JS implementation

## Known limitations

- Local heuristic analysis only, no server-side LLM verification.
- No support for build-step frameworks like React or Tailwind.
- Requires manual site selector updates in sites.js.

## Example

**Request**

I need a Chrome extension that can identify if a product review was written by an AI. Give me the source for a trust-check tool.

**Result**

I've generated the complete Manifest V3 source in `assets/extension/`. You can load this into Chrome immediately via "Load unpacked". The system uses `analyzer.js` for local scoring and `sites.js` for platform-specific DOM selectors. No build step required—just edit and reload.

## Questions

### What exactly do I get with the nex-trust-check-ext skill?

This skill provides the full source code for a production-ready Manifest V3 Chrome Extension that analyzes text locally to identify AI-generated patterns and fake reviews. It solves the complexity of extension development by providing a functional, 'no-build' boilerplate that you can deploy or customize immediately.

### Do I need specific software or build tools to use this code?

The extension uses a vanilla JavaScript, HTML, and CSS 'no-build' philosophy, meaning you can edit the files and reload them in Chrome without needing npm, Webpack, or complex transpilers. It is built strictly for Google Chrome and Chromium-based browsers like Edge or Brave.

### Can I connect this extension to my own AI models or third-party APIs?

Yes, while the extension comes with a built-in heuristic analysis engine, the architecture is designed for easy integration with external LLMs or detection APIs through the background script. This allows you to scale the detection logic based on your specific accuracy requirements.

### Is this extension compatible with the latest Chrome Manifest V3 requirements?

This skill is currently built on the Manifest V3 standard, the latest requirement for the Chrome Web Store. Buyers receive the current stable version of the source code, featuring the side-panel UI and context menu integration.

### How do I install and start testing the extension after purchase?

Simply download the source files, navigate to chrome://extensions in your browser, enable 'Developer mode,' and click 'Load unpacked.' Detailed documentation is included to guide you from this local setup to a full Chrome Web Store submission.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
