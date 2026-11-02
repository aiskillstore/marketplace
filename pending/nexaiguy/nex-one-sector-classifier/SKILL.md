---
name: nex-one-sector-classifier
description: 'Classifies a business into a sector and a matching site archetype from its website and public data, so generation can be themed automatically. Use when: Classify a business description against a specific industry keyword set; Test the Nex classification heuristic before upgrading to the full pipeline; Generate a standalone Python script for lightweight industry filtering.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-one-sector-classifier
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex One Sector Classifier

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-one-sector-classifier). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Reads a company website plus public listing data and assigns a sector with a confidence score.
- Maps the sector to a site archetype: sections, tone, imagery style and the call to action that fits.
- Falls back to a safe generic archetype instead of guessing when confidence is low.
- Returns a small JSON contract that a generator pipeline can consume directly.

## Use cases

- Auto-theming a generated demo site to the prospect sector
- Segmenting a scraped lead list by industry before outreach
- Routing a lead to the right template in a demo factory pipeline
- Enriching a CRM with a sector field that is actually consistent

## Known limitations

Tuned to Belgian and Benelux SME sectors, so exotic or multi-activity businesses land in the generic bucket. Classification quality depends on how much text the target site actually has.

## Example

**Request**

Classify this business: 'Artisanal bakery in Ghent specializing in sourdough bread and local pastries' for the Food and Beverage sector.

**Result**

Generated assets/classifier_lite.py.
Match Score: 85/100
Result: MATCH
Keywords identified: bakery, bread, pastries.
You can now run the script to integrate this logic into your pipeline.

## Questions

### How does the free classifier work?

It uses a keyword-based heuristic approach to match business descriptions against a single configured sector.

### What is the difference between this and the paid version?

The free version handles one specific sector at a time, while the full version manages 12 archetypes with AI-driven analysis.

### What file does this skill produce?

It generates a single Python file, classifier_lite.py, which you can configure and run immediately.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
