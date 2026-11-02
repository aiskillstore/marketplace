---
name: nex-einvoice-de
description: 'Expert guide for German E-Rechnung compliance, XRechnung/ZUGFeRD formats, and GoBD archiving. Use when: Determine the correct e-invoice issuance date based on turnover; Generate GoBD-compliant Verfahrensdokumentation templates; Map UStG mandatory fields to structured XML business terms.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-einvoice-de
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Einvoice DE

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-einvoice-de). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

German businesses face a staged e-invoicing mandate starting in 2025, but many SMEs are unprepared for the complex shift from PDFs to structured XML. Failing to comply with the Wachstumschancengesetz or GoBD archiving standards puts input-tax deductions and audit readiness at risk.

## What it does

- Generates dated readiness checklists based on company turnover and customer mix.
- Provides format decision logic to choose between XRechnung and ZUGFeRD profiles.
- Maps paragraph 14 UStG mandatory invoice fields to EN 16931 business terms.
- Produces templates for GoBD-compliant Verfahrensdokumentation (procedure documentation).
- Calculates specific 8-year retention periods and archiving requirements under BEG IV.

## Frameworks & tools

EN 16931, XRechnung 3.0.2, ZUGFeRD 2.4, UBL, UN/CEFACT CII, Peppol, and DATEV-compatible workflows.

## Why this beats prompting it yourself

Generic LLMs often confuse EU-wide standards with specific German tax law (UStG) and administrative letters (BMF). This skill encodes the verified June 2026 legal status, including the transition waves for 2027 and 2028, ensuring you don't miss the nuances of Leitweg-ID routing or the difference between a "sonstige Rechnung" and a compliant E-Rechnung.

## Use cases

- Assess a German SME's readiness for the 2027 versus 2028 issuance waves.
- Determine the correct ZUGFeRD profile for B2B versus B2G transactions.
- Draft a procedure documentation skeleton for a new digital invoice workflow.
- Verify if an incoming XML invoice meets the paragraph 14 UStG mandatory field requirements.

## Known limitations

Does not provide legal or tax advice. Does not cover the core Peppol network mechanics or non-German country mandates (e.g., France) without companion skills.

## Example

**Request**

Our German company had 1.2M EUR turnover last year. What are our E-Rechnung deadlines and which format should we use for B2B?

**Result**

Based on your >800k EUR turnover:
1. Since Jan 2025: You must be able to receive E-Rechnungen.
2. From Jan 2027: Mandatory issuance of E-Rechnungen for domestic B2B.
Format Recommendation: Use ZUGFeRD EN 16931 (Comfort) for B2B to provide both XML for ERPs and a PDF for humans.

## Questions

### How does nex einvoice de help my business prepare for the 2025 German e-invoicing mandate?

The skill provides a specialized logic layer for German e-invoicing compliance, helping you map mandatory UStG fields to XML structures (XRechnung/ZUGFeRD) and drafting the mandatory GoBD procedure documentation.

### Why should I use this skill instead of a standard AI prompt for XRechnung questions?

While generic AI may provide outdated information, this skill is hardcoded with the specific 2026/2027/2028 transition waves and the latest BMF administrative letters, preventing legal errors regarding input-tax deductions.

### Does the skill support both B2B and B2G (public sector) invoice format requirements?

Yes, the skill is designed to differentiate between XRechnung 3.0.2, various ZUGFeRD 2.2+ profiles, and specific Leitweg-ID requirements for B2G (Business-to-Government) transactions.

### What exactly is included in the purchase of this skill?

You receive the full logic package for your AI agent, including format decision frameworks, readiness checklists, and template generators for GoBD-compliant archiving.

### Can I use this skill for e-invoicing mandates outside of Germany?

This skill focuses strictly on German standards like XRechnung and ZUGFeRD under the Wachstumschancengesetz; it does not cover international mandates like France's Chorus Pro or Italy's SdI.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
