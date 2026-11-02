---
name: nex-tab-cost-ext
description: 'A production-ready Manifest V3 Chrome extension to monitor tab memory, manage resources, and gamify browser hygiene. Use when: Deploy a complete ''Nex Tab Cost'' extension to the Chrome Web Store; Build memory-aware browser tools without an NPM/build step; Identify and auto-close resource-heavy idle browser tabs.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-tab-cost-ext
compatibility: Compatible with Claude Code, Cursor, and VS Code.
---

# Nex Tab Cost Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-tab-cost-ext). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Nex Tab Cost is a production-ready Chrome Extension (Manifest V3) that calculates and displays the real-time resource cost of open browser tabs. It uses a sophisticated heuristic engine to estimate memory usage based on domain weight, activity status, and media playback. The extension provides a toolbar badge with color-coded severity levels, a dashboard for managing heavy tabs, and gamified achievements to encourage lean browsing habits.

## Why use this skill

Unlike basic scaffolding tools, this skill delivers a fully functional, previously shipped product. It follows a "no-build" philosophy—using vanilla JavaScript, HTML, and CSS—eliminating the need for complex toolchains, Webpack, or NPM dependencies. It's the perfect solution for developers who need a hardened MV3 starting point or an immediate utility for tab management.

## Output & Features

- Complete source code including Manifest V3 service workers and popup dashboards.
- Heuristic weighting database (heavysites.json) for accurate memory estimation.
- Gamification engine with five unlockable achievement badges.
- CSV export functionality for historical resource usage tracking.
- Step-by-step guidance for Chrome Web Store packaging and deployment.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Deploy a complete 'Nex Tab Cost' extension to the Chrome Web Store.
- Build memory-aware browser tools without an NPM/build step.
- Identify and auto-close resource-heavy idle browser tabs.
- Implement a domain-weighting heuristic engine for resource tracking.

## Known limitations

- Memory usage is heuristic-based: not a 1:1 match with Chrome Task Manager.
- No build step: not suitable for React or TypeScript workflows.

## Example

**Request**

I need a browser extension that shows me how much RAM my tabs are using and lets me close the heavy ones. Use a vanilla JS approach.

**Result**

I've generated the Nex Tab Cost extension in `assets/extension/`.

Key features:
- Badge shows total RAM (Green <2GB, Red >4GB)
- Popup dashboard sorts tabs by memory impact
- One-click 'Close Idle' for tabs older than 60 mins

Load it via Chrome > Extensions > Load Unpacked.

## Questions

### What specific problems does the nex-tab-cost-ext skill solve?

This skill provides a fully functional Manifest V3 Chrome extension that monitors tab memory usage in real-time, helping users identify resource-heavy sites and improve browser performance through a built-in dashboard and gamified achievements.

### Do I need to install any external developer tools or dependencies to use this code?

No, this skill is designed with a 'no-build' philosophy using vanilla JavaScript, HTML, and CSS, allowing you to modify and deploy the code immediately without setting up Webpack, NPM, or complex build pipelines.

### What exactly is included in the purchase of this skill?

You receive the complete production-ready source code, the 'heavysites.json' heuristic database, a gamification engine with achievement badges, CSV export functionality, and a step-by-step deployment guide for the Chrome Web Store.

### Is this extension compatible with the latest Google Chrome security standards?

The extension is built strictly on the latest Manifest V3 (MV3) standards, ensuring full compatibility with the current Chrome Web Store requirements and modern Chromium-based browsers like Edge and Brave.

### How do I install this extension in my browser after purchasing the skill?

Setting it up is simple: download the source files, navigate to 'chrome://extensions' in your browser, enable Developer Mode, and use the 'Load unpacked' feature to select the skill folder.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
