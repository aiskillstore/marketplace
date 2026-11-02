---
name: nex-einvoice-es
description: 'Navigate Spanish VeriFactu and Crea y Crece compliance with updated 2027 deadlines and technical field requirements. Use when: Map the transition timeline for IS taxpayers and autónomos through 2028; Define technical requirements for SHA-256 hash chaining in invoice records; Evaluate the impact of TicketBAI vs VeriFactu for multi-regional businesses.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-einvoice-es
compatibility: Compatible with Claude Code, Cursor, Windsurf, and other SKILL.md-compatible agents.
---

# Nex Einvoice ES

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-einvoice-es). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Spanish businesses face two overlapping but distinct invoicing mandates that are frequently confused. Implementing the wrong technical requirements for VeriFactu or missing the Crea y Crece B2B deadlines leads to heavy non-compliance penalties, reaching up to EUR 50,000 for users and EUR 150,000 for developers.

## What it does

- Identifies whether a business falls under VeriFactu, TicketBAI, SII, or the Basque/Navarra foral regimes.
- Validates software compliance against Real Decreto 1007/2023 requirements including SHA-256 hash chaining and QR code generation.
- Outlines the specific technical field structures for high-level and cancellation invoice records (registros de facturación).
- Maps the multi-phase Crea y Crece B2B e-invoicing rollout starting in late 2027.
- Generates vendor-specific questionnaires to verify the mandatory "declaración responsable" for invoicing software.

## Frameworks & tools

Spanish AEAT specifications, Real Decreto 1007/2023 (RRSIF), Orden HAC/1177/2024, EN 16931 semantic model, and UBL syntax for the SPFE platform.

## Why this beats prompting it yourself

Standard LLMs often reference outdated 2026 deadlines. This skill uses the corrected 2027/2028 timeline established by Real Decreto-ley 15/2025. It enforces the critical distinction between software certification (VeriFactu) and structured exchange (Crea y Crece) which generic prompts often blur.

## Use cases

- Determine if an existing ERP or SaaS needs a "declaración responsable" to stay legal in Spain.
- Design the database schema for Spanish-compliant hash-chained invoice logs.
- Advise a Spanish "autónomo" on when they must switch to structured B2B e-invoices.
- Assess whether to adopt the real-time VERI\*FACTU mode to reduce local data retention burdens.

## Known limitations

Does not replace a professional tax advisor or legal counsel. Ministerial orders for Crea y Crece are based on the latest June 2026 drafts and require final BOE publication confirmation.

## Example

**Request**

Our software uses Excel to generate invoices for B2B clients in Madrid. What are our obligations under the new Spanish mandates and what is the deadline for an IS taxpayer?

**Result**

Under Real Decreto 1007/2023, even simple invoicing software must comply. As an IS taxpayer, your deadline is 1 January 2027. You must implement SHA-256 hash chaining, event logs, and mandatory QR codes. For B2B exchange, Crea y Crece obligations start 1 October 2027 for companies over 8M turnover.

## Questions

### How does this skill help me distinguish between VeriFactu and the Crea y Crece law?

The skill clarifies the distinct requirements between VeriFactu (software certification and hash chaining) and Crea y Crece (B2B structured e-invoicing), ensuring you don't apply the wrong technical standards to your ERP or SaaS.

### Does the skill include the latest 2027 deadline updates from recent Spanish legislation?

Yes, this skill is specifically updated with the Real Decreto-ley 15/2025 timelines, providing the correct 2027 and 2028 deadlines that generic AI models often miss.

### What technical specifications does it cover for developers building invoicing software?

It provides detailed guidance on implementing SHA-256 hash chaining, QR code formatting, and the mandatory 'declaración responsable' required for software developers under AEAT regulations.

### Is this skill compatible with my existing AI development agent?

The skill is compatible with major AI agents that support regulatory analysis and can be integrated into your workflow to audit existing database schemas or compliance roadmaps.

### Can I use this for businesses operating in the Basque Country or Navarra?

While it covers the national AEAT/VeriFactu framework, it also helps identify when a business falls under the specific Basque (TicketBAI) or Navarra foral regimes instead.

### What is included in the purchase of the nex einvoice es skill?

You receive the full logic and knowledge base for Spanish e-invoicing compliance, including schema design advice and vendor-specific questionnaires to verify software legality.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
