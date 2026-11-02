---
name: nex-color-spy-ext
description: 'Fully-functional, zero-build Chrome extension for inspecting CSS colors, fonts, and dimensions with Shadow-DOM. Use when: Deploy a professional CSS inspector to the Chrome Web Store in minutes; Create a font-matching tool that sits on top of any website; Build a pixel-perfect design overlay that avoids host-page CSS leaks.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-color-spy-ext
compatibility: Claude Code, Cursor, Windsurf, Aider, Cline, VS Code
---

# Nex Color Spy Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-color-spy-ext). Scripts, extension source, and templates from the original package are not in this folder.

## Overview

Nex Color Spy is a production-ready, Manifest V3 Chrome extension designed for designers and front-end developers who need instant access to computed styles. Unlike generic AI scripts, this skill provides the complete source code for a field-tested "overlay" extension that inspects colors, fonts, and box model data in real-time without interfering with page styles.

## What it does

- **Shadow-DOM Overlay:** Features a floating inspector panel isolated from host page CSS to ensure consistent UI rendering.
- **Real-time Inspection:** Tracks the cursor to report computed hex codes, font families, font sizes, margins, and padding.
- **Zero-Build Architecture:** Written in vanilla JS, HTML, and CSS. No Webpack, Vite, or NPM required—just edit and reload.
- **Clipboard Integration:** Quick-click functionality to copy any hex code or CSS value directly to the clipboard.

## Why use this skill?

Prompting an AI to "write an extension" often results in broken background scripts or styling conflicts. This skill delivers a battle-hardened codebase optimized for the MV3 lifecycle. It includes keyboard shortcuts (Alt+Shift+I), storage persistence for settings, and a professional-grade content script that handles complex page layouts effortlessly. Use it to ship a finished tool immediately or as a robust template for your own overlay-based extensions.

## Supported Features

- Manifest V3 compliant (Service Workers).
- Isolation via Shadow-DOM.
- Keyboard-driven toggles and toolbar actions.
- Ready-to-zip packaging for the Chrome Web Store.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Deploy a professional CSS inspector to the Chrome Web Store in minutes.
- Create a font-matching tool that sits on top of any website.
- Build a pixel-perfect design overlay that avoids host-page CSS leaks.
- Learn the no-build developer loop for rapid Chrome extension prototyping.

## Known limitations

- No support for canvas or SVG internals.
- Limited inspection on browser-protected URLs (e.g. Chrome Web Store).
- Vanilla JS only: no support for React/Vue build steps.

## Example

**Request**

Build me a Chrome extension that lets me hover over any element to see its hex color and font size in a floating window.

**Result**

I've generated the 'Nex Color Spy' extension in assets/extension/. Key features:
- Manifest V3 architecture
- Shadow-DOM isolation for the inspector panel
- Hotkey toggle (Alt+Shift+I)
- Hex/Font-size extraction logic
To install: Load the folder as an 'Unpacked Extension' in Chrome.

## Questions

### What exactly is included in the nex-color-spy-ext package?

You receive the full source code for a Manifest V3 Chrome extension, including the background service worker, the Shadow-DOM content script, and the manifest file, all organized for immediate deployment.

### How do I install and run the extension after purchasing?

Installation is simple: download the source files, navigate to chrome://extensions in your browser, enable 'Developer mode', and click 'Load unpacked' to select the folder.

### How does this extension handle websites with complex styling or existing CSS conflicts?

The extension uses a Shadow-DOM overlay to isolate the inspector UI from the host page's CSS, ensuring the inspection panel looks perfect and doesn't break the layout of the site you are visiting.

### Can I customize the code or use it as a template for my own extension projects?

Absolutely. Since it is built with zero-build vanilla JS and HTML, you can easily open the files in any text editor to modify the UI, add new inspection metrics, or change keyboard shortcuts without needing NPM or complex compilers.

### Is this skill compatible with my existing AI coding agent?

This skill is designed as a standalone codebase that can be managed by any AI agent capable of file manipulation or code analysis, acting as a "Pro-level" starting point that avoids common AI-generated bugs in Manifest V3 scripts.

### Which specific CSS properties can the Color Spy inspect?

The extension provides real-time data on HEX color codes, font families, font sizes, margins, padding, and element dimensions directly as you hover over page elements.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
