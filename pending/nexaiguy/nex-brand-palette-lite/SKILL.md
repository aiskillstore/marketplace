---
name: nex-brand-palette-lite
description: 'Extract brand color hex codes from a website''s CSS variables into a portable Python script. Use when: Identify primary and accent brand colors from a live URL; Generate a reusable Python script for color audits; Speed up UI development by matching existing design tokens.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-brand-palette-lite
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Brand Palette Lite

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-brand-palette-lite). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Manually digging through DevTools to find a brand's specific hex codes is tedious. Design workflows often stall when you need to match a site's primary palette but colors are hidden behind CSS variables.

## What it does

- Scrapes public URLs to identify CSS custom properties.
- Filters for specific naming conventions like --primary, --accent, and --brand.
- Generates a standalone Python script to automate color extraction.
- Operates using only standard libraries with no external dependencies required.

## Frameworks & tools

Python, CSS Custom Properties (Variables).

## Why this beats prompting it yourself

Generic prompts often fail to target the specific naming conventions used in modern design systems. This skill provides a focused extraction logic that ignores utility noise and targets meaningful brand tokens out of the box.

## Use cases

- Quickly extracting brand colors for a client proposal.
- Scaffolding a theme for a new site based on an existing design system.
- Auditing CSS variables across a landing page for brand consistency.

## Known limitations

Cannot extract colors set via JavaScript or hidden in external shadow DOMs. Limited to CSS variables only, it does not analyze images or computed styles.

## Example

**Request**

Extract the brand colors from https://example.com using CSS variables.

**Result**

I have generated assets/palette_lite.py. This script will fetch the site and extract variables like --primary and --brand-color. Run it to get the hex codes.

## Questions

### How does nex-brand-palette-lite simplify the process of gathering brand colors?

The skill identifies and extracts CSS custom properties (variables) like --primary or --brand from a website's code and compiles them into a portable Python script for easy reuse.

### What specific assets are included in this purchase?

You will receive the core logic for the extraction process, along with a standalone Python script that functions using only standard libraries, requiring no additional third-party installations.

### Which AI agents or environments are compatible with this skill?

This skill is designed to work with any AI agent that supports Python execution or code generation, making it compatible with most major LLMs and automation frameworks.

### Can this skill extract colors from images or logos found on a webpage?

No, this skill is specifically optimized to target CSS variables; it does not perform image processing or analyze computed styles from rendered pixels.

### Do I need to install any external Python libraries to use the generated output?

Setting up is simple: just provide the URL of the site you wish to analyze, and the skill will generate the necessary code to scrape and filter the brand tokens automatically.

### Are there any types of websites where the extraction might not work?

The skill works best on public URLs with standard CSS naming conventions; however, it cannot access colors protected by login screens or those stored within a shadow DOM.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
