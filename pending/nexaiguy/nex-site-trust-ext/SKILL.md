---
name: nex-site-trust-ext
description: 'Ship a complete Manifest V3 website trust and safety checker extension with no build step required. Use when: Ship a functional website trust scorer to the Chrome Web Store; Detect high-risk domains using RDAP and on-page transparency signals; Inject custom UI warnings into malicious or low-trust websites.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-site-trust-ext
compatibility: Claude Code, Cursor, Windsurf, Aider, Cline, VS Code
---

# Nex Site Trust Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-site-trust-ext). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Building a Chrome extension from scratch involves navigating Manifest V3 manifest requirements, service worker lifecycles, and cross-script communication. Most scaffolds are either empty or require complex build pipelines just to see a "Hello World" in the browser.

## What it does

- Generates a complete, production-ready Manifest V3 extension using vanilla JS, HTML, and CSS.
- Calculates a 0 to 100 trust score based on SSL status, domain age via RDAP, and transparency signals like privacy policies and return info.
- Includes a content script that injects on-page warnings for high-risk domains.
- Provides a settings dashboard for user-supplied Google Safe Browsing and PhishTank API keys.
- Implements local storage persistence for settings and extension state without a backend.

## Frameworks & tools

Chrome Extension Manifest V3, Vanilla JavaScript, HTML5, CSS3, RDAP API, Google Safe Browsing API, PhishTank API.

## Why this beats prompting it yourself

This is the actual source code of a shipped extension. It solves the non-trivial task of coordinating background service workers, content scripts, and popup UI without a build step. You get a working security engine and asset structure that follows Chrome Web Store requirements out of the box.

## Use cases

- Deploy a website safety checker to protect users from phishing and scams.
- Fork the codebase to build any "action-on-click" style toolbar extension.
- Learn Manifest V3 architecture by studying a working, multi-part implementation.
- Create a tool that scrapes and analyzes site metadata in real-time.

## Known limitations

This skill uses the vanilla no-build pattern. It is not compatible with React, Vue, or TypeScript build pipelines without manual migration.

## Example

**Request**

Give me a working MV3 extension that scores a website's trustworthiness.

**Result**

I've generated the complete source in assets/extension/. It includes the background service worker for RDAP lookups, content scripts for transparency signals, and the popup UI. You can load this immediately in chrome://extensions using 'Load unpacked'.

## Questions

### What exactly does the nex-site-trust-ext skill provide?

This skill provides a complete, production-ready Manifest V3 Chrome extension codebase designed to evaluate website safety using SSL status, domain age, and security APIs without requiring a complex build pipeline.

### Does this extension require a build step or specific compiler to run?

The extension uses vanilla JavaScript, HTML, and CSS, meaning you can load it directly into Chrome's developer mode and see it work instantly without needing Node.js, Webpack, or TypeScript.

### Do I need my own API keys to use the security features?

Yes, while the core logic works out of the box, the extension includes dedicated settings fields for you to add your own Google Safe Browsing and PhishTank API keys for enhanced threat detection.

### What is included in the purchase?

You receive the full source code for the background service workers, content scripts, and popup UI, along with the manifest file and asset structure required by the Chrome Web Store.

### Can I use this as a template to build a different type of Chrome extension?

Absolutely; the 'no-build' architecture makes it an ideal boilerplate for any extension that requires real-time page analysis, toolbar interactions, or local storage management.

### Which browsers are compatible with this extension?

The extension is designed for any browser that supports Manifest V3, including Google Chrome, Brave, and Microsoft Edge.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
