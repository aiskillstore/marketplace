---
name: nex-receipt-vault
description: 'Deploy a complete Manifest V3 extension to capture and dashboard online receipts locally without bank access. Use when: Deploy a private, local-only spending tracker for online shoppers; Build a robust web scraper extension using pre-configured platform detectors; Create a data-extraction tool that works without a backend or server.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-receipt-vault
compatibility: Compatible with Claude Code, Cursor, and Cline.
---

# Nex Receipt Vault

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-receipt-vault). Scripts, extension source, and templates from the original package are not in this folder.

## Secure Receipt Scraper & Dashboard

Nex Receipt Vault is a production-ready, Manifest V3 Chrome extension designed for privacy-first purchase tracking. It eliminates the need for intrusive bank connections by capturing order data directly from browser confirmation pages. This skill provides the complete, working source code—originally a shipped product—built on a vanilla JS, HTML, and CSS architecture.

## What it does

The extension monitors active tabs for order-confirmation patterns. Once detected, its specialized extraction engine parses merchant details, itemized lists, totals, and dates. All data is stored locally on the user's device. The included popup provides a comprehensive spending dashboard and history view. Key features include:

- **Multi-Platform Detectors:** Pre-built support for Amazon, Shopify, WooCommerce, and more.
- **Intelligent Classification:** Distinguishes between standard pages and valid receipts.
- **Zero-Build Workflow:** Edit and reload instantly without npm or bundlers.
- **Privacy-Centric:** No accounts, no servers, and no third-party data access.

## Why use this skill?

Building reliable web scrapers that survive DOM changes is difficult. This skill saves days of development by providing a field-tested architecture for DOM-based data extraction. It serves as both a functional tool and a masterclass in professional extension development, covering everything from background service workers to local storage persistence.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Deploy a private, local-only spending tracker for online shoppers.
- Build a robust web scraper extension using pre-configured platform detectors.
- Create a data-extraction tool that works without a backend or server.
- Learn professional Manifest V3 architecture with a zero-build-step workflow.

## Known limitations

- No automated testing suite included.
- Scraper logic requires manual updates if merchant DOM changes.
- Requires manual reload in developer mode: no HMR.

## Example

**Request**

I want to build an extension that saves my Amazon and Shopify orders locally so I can track my spending without linking my bank account. Do you have a template for this?

**Result**

I've initialized the Nex Receipt Vault extension. It includes specialized detectors for Amazon and Shopify, a local storage service worker, and a spending dashboard. You can load it via 'Load unpacked' in chrome://extensions. Files are in assets/extension/.

## Questions

### What exactly am I buying with the Nex Receipt Vault skill?

This skill provides the full source code for a Manifest V3 Chrome extension that captures and stores purchase data locally from browser confirmation pages, bypassing the need for sensitive bank API connections.

### How difficult is it to install and customize this extension?

The skill includes a 'Zero-Build' workflow using vanilla JS, HTML, and CSS, allowing you to load it into Chrome's Developer Mode and see changes instantly without needing npm or complex build tools.

### Which websites are supported for receipt scraping out of the box?

It features pre-built detectors for major platforms like Amazon, Shopify, and WooCommerce, but its modular architecture allows you to easily add custom extraction logic for other merchants.

### Does this tool send my purchase data to an external database?

Absolutely. The extension is designed with a privacy-first approach, storing all scraped data and itemized lists directly on the user's local device rather than a third-party server.

### Is this extension compatible with the latest Google Chrome requirements?

The code follows the latest Manifest V3 standards, ensuring long-term compatibility with the Chrome Web Store and modern browser security requirements.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
