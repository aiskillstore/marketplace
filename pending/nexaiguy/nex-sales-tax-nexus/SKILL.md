---
name: nex-sales-tax-nexus
description: 'US sales tax economic nexus evaluation, registration checklists, and exemption certificate workflows for e-commerce. Use when: Determine which states require sales tax registration based on revenue; Manage and validate MTC and SST exemption certificates for wholesale; Brief marketplace-only sellers on their specific registration requirements.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-sales-tax-nexus
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Windsurf.
---

# Nex Sales Tax Nexus

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-sales-tax-nexus). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Managing US sales tax compliance across multiple jurisdictions is a logistical nightmare for e-commerce sellers. Keeping track of shifting economic nexus thresholds, marketplace facilitator rules, and physical footprint triggers leads to expensive penalties and audit exposure.

## What it does

- Evaluates economic and physical nexus across all US states, including marketplace warehouse footprints like FBA.
- Generates state-specific threshold reference tables updated with the latest June 2026 transaction and revenue rules.
- Produces registration checklists and handles voluntary disclosure agreement (VDA) prioritization for historical exposure.
- Standardizes exemption certificate management for wholesale and B2B sales using MTC and SST forms.
- Determines specific registration duties for marketplace-only sellers versus mixed-channel operators.

## Frameworks & tools

Supports **Shopify**, **Amazon FBA**, **eBay**, **Walmart**, and **Etsy** sellers. Incorporates data from **Streamlined Sales Tax (SST)** and state Department of Revenue sources.

## Why this beats prompting it yourself

General LLMs often hallucinate tax thresholds or use outdated pre-Wayfair logic. This skill enforces a rigorous physical-then-economic evaluation layer and bakes mandatory verification steps into every workflow to ensure audit-proof documentation.

## Use cases

- Assess whether a Shopify store has crossed the $100,000 threshold in a specific state.
- Create a registration roadmap for a seller expanding into states with $500,000 thresholds like CA or TX.
- Validate resale certificates for a wholesale distributor selling to tax-exempt entities.
- Review tax obligations for non-US sellers shipping inventory to US-based warehouses.

## Known limitations

Does not provide legal or tax advice. Does not calculate income or franchise tax nexus. Requires manual verification against state DOR sites for the most current rule changes.

## Example

**Request**

Evaluate my nexus. I sell $120k annually to Illinois customers via Shopify and have $50k in California. I also use FBA and have inventory in a Texas warehouse.

**Result**

Nexus Evaluation:
1. Physical Nexus: Texas (Confirmed via FBA inventory).
2. Economic Nexus: Illinois (Threshold $100k gross receipts crossed; 200-transaction test removed Jan 2026).
3. Risk: California (Below $500k threshold).
Next step: Register in TX and IL using the attached checklist.

## Questions

### How does this skill help manage US sales tax compliance across different states?

This skill automates the tracking of economic nexus thresholds across all 50 states, manages exemption certificate workflows, and provides specific registration checklists based on your sales volume and physical footprint.

### Which e-commerce platforms and tax frameworks are compatible with this skill?

The skill is designed for e-commerce operators using Shopify, Amazon FBA, eBay, Walmart, and Etsy, and it integrates with data frameworks from Streamlined Sales Tax (SST) and state Department of Revenue sources.

### How does this skill ensure tax threshold information is more accurate than a standard LLM prompt?

Unlike general AI which may use outdated data, this skill uses a specialized logic layer updated with June 2026 rules to prevent hallucinations regarding state-specific transaction and revenue thresholds.

### What specific assets are included in my purchase of the nex sales tax nexus skill?

You will receive the full AI agent skill package, including the nexus evaluation workflows, state-specific registration roadmaps, and standardized templates for MTC and SST exemption certificates.

### Are there any specific tax types or legal obligations that this skill does not cover?

While the skill provides rigorous evaluation and audit-proof documentation workflows, it does not calculate income/franchise tax or provide formal legal advice, and users should manually verify final filings with state DOR sites.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
