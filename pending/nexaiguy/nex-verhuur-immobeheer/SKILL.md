---
name: nex-verhuur-immobeheer
description: 'Automated Belgian rental contracts, legal indexation calculations, and regional compliance for landlords. Use when: Calculate indexed rent using regional correction factors and Statbel data; Draft regional-specific 9-year or short-term housing contracts; Generate notice letters for renovations or personal occupancy.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-verhuur-immobeheer
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Verhuur Immobeheer

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-verhuur-immobeheer). Scripts, extension source, and templates from the original package are not in this folder.

## Streamline Belgian Property Management

Nex Verhuur provides a comprehensive toolkit for landlords and property managers operating in the complex Belgian real estate market. Since the regionalization of housing laws, staying compliant in Flanders, Brussels, and Wallonia requires distinct legal frameworks. This skill automates the creation of jurisdiction-specific documents and precise financial calculations.

## Advanced Legal Logic

Unlike generic AI prompts, this skill integrates the latest 2026 legislative updates, including the Statbel health index (base 2025=100) and specific EPC/EPB correction factors unique to each region. It ensures that rent indexations, lease terminations, and deposits are handled according to the exact decrees governing the property's location.

## What you can generate:

- **Legally Compliant Contracts:** Customized skeletons for 9-year, short-term, or student leases.
- **Rent Indexation Letters:** Automated calculations using the correct health index formula and mandatory correction factors.
- **Official Correspondence:** Notice letters for personal use, renovation, or tenant-initiated terminations.
- **Technical Documentation:** Structured check-in/check-out inventory (plaatsbeschrijving) templates and MyRent registration workflows.

The skill outputs structured, ready-to-use Markdown documents that follow official Belgian government standards, significantly reducing the risk of legal disputes or administrative fines.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Calculate indexed rent using regional correction factors and Statbel data.
- Draft regional-specific 9-year or short-term housing contracts.
- Generate notice letters for renovations or personal occupancy.
- Create structured checklists for mandatory move-in property inspections.
- Navigate the MyRent registration workflow to avoid legal penalties.

## Known limitations

- Excludes commercial and common law leases.
- Requires manual Statbel index lookups.
- Legal output requires final human review.

## Example

**Request**

Calculate the rent indexation for an apartment in Ghent. Base rent is 850 EUR, signed Feb 2024, started March 2024, and it has an EPC label D. It is now March 2026.

**Result**

Based on the Flemish Housing Decree:
- Base Rent: €850
- Start Index (Jan 2024): 128.50
- New Index (Feb 2026): 134.12
- EPC Correction Factor: 0.95 (Label D, pre-Oct 2022 rule)
- New Rent: €885.25

I have generated the indexation formal letter for your tenant.

## Questions

### How does this skill help manage properties specifically in Belgium?

This skill automates the creation of legally-compliant rental contracts, rent indexation letters based on latest health indices, and official notice letters specifically for Flanders, Wallonia, and Brussels.

### Does the indexation tool account for regional differences and EPC/EPB ratings?

The tool includes the 2026 legislative updates, including the Statbel health index (base 2025=100) and regional energy performance (EPC/EPB) correction factors to ensure all calculations are legally valid.

### What is required to set up the nex-verhuur-immobeheer skill?

Simply import the skill into your preferred AI agent framework; it requires no external API keys or complex coding and is ready to generate documents immediately after installation.

### What specific deliverables are included with my purchase?

You receive the complete logic for generating Belgian rental documentation, including automated templates for 9-year leases, short-term contracts, student housing, and rent indexation letters.

### Which AI models or platforms are compatible with this skill?

The skill is designed to work with any major LLM (like GPT-4 or Claude 3) that supports professional Markdown output, ensuring your documents are formatted for immediate use.

### How does the skill stay updated with changing Belgian housing laws?

The logic is monitored against Belgian housing decree changes; users are notified of version updates whenever there are significant shifts in the health index base or regional rental laws.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
