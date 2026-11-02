---
name: nex-gdpr-deepening
description: 'Generates GDPR Article 30 processing registers and Article 35 DPIAs for Belgian and EU SMEs, prefilled with common SME processing activities. Use when: Draft Article 30 records for controllers and processors; Run a 3-gate DPIA obligation test for new projects; Create risk-scored DPIA documents with mitigation steps.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-gdpr-deepening
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex GDPR Deepening

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-gdpr-deepening). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Generates Article 30 records of processing activities in both controller and processor variants.
- Ships five prefilled SME processing activities ready to adapt: payroll, customer management and invoicing, direct marketing, camera surveillance, and website analytics, each with legal basis, recipients, and retention periods.
- Runs the three-gate DPIA obligation check: the Belgian GBA list of eight mandatory processing types, Article 35.3, and the nine EDPB criteria.
- Drafts full DPIAs with a likelihood-times-impact risk scoring matrix, before and after measures.

## Use cases

- Building or updating an Article 30 register for an SME with staff and a customer base.
- Deciding whether a new tool requires a DPIA, with a documented negative conclusion.
- Drafting a full DPIA with risk scoring for AI profiling or sensitive data.
- Preparing an Article 36 prior consultation with the Belgian GBA.

## Known limitations

Excludes data subject requests (Articles 15 to 21), those live in the separate nex-gdpr skill. Tuned to Belgian practice, other EU member states have their own national DPIA lists. Output is a working document, not legal advice, and a DPO or privacy lawyer should review it.

## Example

**Request**

Help me create a verwerkingsregister for my Belgian SME. We do payroll, customer billing, and use camera surveillance at the office.

**Result**

I have drafted your Article 30 Register.
- Personnel/Payroll: Legal basis Art. 6.1(c), 5-year retention.
- Billing: Legal basis Art. 6.1(b), 10-year retention (BE law).
- Cameras: Legal basis Legitimate Interest, 1-month retention.
Next: Should we perform a DPIA check for the cameras?

## Questions

### Does this handle processor registers?

Yes, it contains a specific section for GDPR Article 30.2 which covers the mandatory fields for data processors.

### How is risk scoring calculated?

It uses a likelihood times impact matrix to score risks before and after technical and organizational measures.

### What criteria does it use for DPIA checks?

It uses the Belgian GBA list, Article 35.3 criteria, and the nine EDPB guidelines to determine if a DPIA is required.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
