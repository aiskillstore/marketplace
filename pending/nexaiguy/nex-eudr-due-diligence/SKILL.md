---
name: nex-eudr-due-diligence
description: 'Builds a complete EUDR due diligence file, applicability decision, DDS structure, geolocation checklist, and risk assessment, from your product list. Use when: Determine EUDR scope, company role, and compliance deadlines; Map products to Annex I CN codes including 2025 amendments; Generate geolocation data collection checklists for suppliers.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-eudr-due-diligence
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex EUDR Due Diligence

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-eudr-due-diligence). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Runs the applicability decision tree for Regulation 2023/1115: in or out of scope, role (operator, downstream operator, trader), size class, and applicable date (30 December 2026 or 30 June 2027).
- Maps each product to Annex I by CN code, including the December 2025 amendment that removed certain printed products from scope.
- Produces the Due Diligence Statement structure mirroring Annex II, ready for the EU Information System (TRACES).
- Generates the geolocation data collection checklist with coordinate format rules and legality evidence per plot.
- Builds a country-benchmark-based risk assessment (Implementing Regulation 2025/1093 plus the Article 10 criteria) with a negligible or non-negligible conclusion per supply chain.

## Why use this

EUDR hits anyone trading cattle, cocoa, coffee, palm oil, rubber, soya, wood, or derived products on the EU market, and the December 2026 deadline is fixed. This skill takes a company from does this apply to me to a documented due diligence file, including the simplified routes for low-risk sourcing and the post-2025 reliefs for downstream companies that most summaries miss.

## Use cases

- An importer of coffee, cocoa, palm oil, soy, rubber, or timber preparing for the December 2026 deadline
- A chocolate maker or furniture producer checking whether the downstream reliefs apply
- Building the supplier geolocation data request and evidence file
- A documented risk assessment per supply chain, with the low-risk simplified route where allowed

## Known limitations

Output is a structured draft, not legal advice. The skill appends a disclaimer and the file needs professional review. Country benchmark levels and CN code mappings must be verified against the current official lists at the time of use. It structures the DDS but does not submit it to TRACES for you.

## Example

**Request**

We import coffee from Brazil for the EU market. Are we in scope for EUDR, and what due diligence do we need to prepare?

**Result**

**EUDR Applicability: In Scope**
- Role: Operator (Importer)
- Deadline: 30 Dec 2026
- Action: Full Due Diligence required.
- Files Generated: Geolocation Checklist, Risk Assessment Template (Standard Risk: Brazil), and Annex II DDS Structure.

## Questions

### How does it handle product scope?

The skill maps products to Annex I by CN code and includes the December 2025 amendment which removed specific printed goods like books and newspapers.

### Does it help with supplier data collection?

Yes. It generates a geolocation data checklist with coordinate format rules and legality evidence requirements per plot of land.

### What risk assessment criteria are used?

It uses Implementing Regulation 2025/1093 country benchmarks and Article 10 criteria to conclude if risk is negligible or non-negligible.

### Does it submit files directly to TRACES?

No. It drafts the structure and content required for the DDS, but the user must manually submit this data to the TRACES system.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
