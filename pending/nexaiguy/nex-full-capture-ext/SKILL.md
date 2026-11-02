---
name: nex-full-capture-ext
description: 'Ship a complete, production-ready Manifest V3 Chrome extension for scrolling screenshots and PDF exports. Use when: Generate a complete Manifest V3 scrolling capture extension in seconds; Learn the offscreen document pattern for complex image processing in Chrome; Implement local, client-side PDF generation without external APIs.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-full-capture-ext
compatibility: Claude Code, Cursor, Windsurf, Aider, Cline, VS Code
---

# Nex Full Capture Ext

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-full-capture-ext). Scripts, extension source, and templates from the original package are not in this folder.

## Professional Full-Page Capture Chrome Extension

This skill delivers the production-ready source code for the Nex Full Capture extension, a robust Manifest V3 tool that enables one-click scrolling screenshots. Unlike basic AI-generated boilerplates, this is a fully realized, shipped product that handles complex tasks like viewport stitching via offscreen documents and local PDF generation.

## What it does

- **Full-Page Scrolling:** Orchestrates background scripts to scroll, capture, and stitch page segments.
- **Multiple Export Formats:** Offers PNG downloads, PDF generation via local scripts, and clipboard support.
- **Zero-Build Architecture:** Built with vanilla JS, HTML, and CSS for a lightning-fast developer loop—just load and go.
- **MV3 Compliant:** Uses the latest Chrome Manifest V3 standards, including offscreen documents and background workers.

## Why use this skill?

Building a reliable scrolling capture tool is notoriously difficult due to lazy-loading elements and coordinate math. This skill provides a proven, tested implementation that handles these edge cases out of the box. It serves as both a powerful utility and a high-quality "action-on-click" template for developers looking to build their own browser-based tools without the overhead of heavy frameworks or build steps.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Generate a complete Manifest V3 scrolling capture extension in seconds
- Learn the offscreen document pattern for complex image processing in Chrome
- Implement local, client-side PDF generation without external APIs
- Bootstrap a vanilla JS extension project with zero build configuration

## Known limitations

- Not compatible with build-step frameworks (React/Vue).
- Limited by browser memory on extremely long pages.
- May struggle with complex sticky/fixed headers.

## Example

**Request**

I need to build a Chrome extension that takes a scrolling screenshot of a whole webpage and lets me save it as a PDF.

**Result**

I have generated the full source for your extension in /assets/extension/. This includes the Manifest V3 configuration, scrolling logic in background.js, and local PDF export via pdf-gen.js. You can load this immediately in Chrome via 'Load unpacked' under chrome://extensions.

## Questions

### What exactly is included in the nex-full-capture-ext package?

You will receive the complete, production-ready source code (JavaScript, HTML, CSS) and the Manifest V3 configuration files required to run the extension. It includes the specialized logic for viewport stitching and PDF generation without any hidden dependencies.

### How does this differ from a basic AI-generated screenshot script?

This skill solves the common "lazy-loading" and "coordinate math" issues that cause standard screenshot tools to fail. It provides a reliable architectural blueprint for scrolling captures and PDF exports that is much more robust than basic AI-generated boilerplates.

### How do I install and test the extension after purchasing the skill?

Since this is a zero-build vanilla JS project, setup is instant: simply enable "Developer mode" in Chrome, click "Load unpacked," and select the folder. There are no npm installs or complex build pipelines required to get it running.

### Is the extension compatible with the latest Chrome Manifest V3 requirements?

Yes, the code is fully compliant with modern Chrome Manifest V3 standards. It specifically utilizes offscreen documents and background workers to handle heavy processing, ensuring long-term compatibility with the Chrome Web Store.

### Can I use this skill with AI coding assistants to customize the extension?

While the code is provided as a standalone professional tool, it is designed for ease of use by AI agents. You can supply the source files to an agent like Claude or ChatGPT to quickly add custom features or integrate it into larger automation workflows.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
