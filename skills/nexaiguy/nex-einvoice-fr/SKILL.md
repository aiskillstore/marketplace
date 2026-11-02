---
name: nex-einvoice-fr
description: 'Implement the French e-invoicing mandate (2026/2027) with Factur-X specs, PDP selection, and e-reporting workflows. Use when: Determine exact mandate dates based on SIREN size and VAT regime; Map Factur-X EN16931 profiles for technical ERP integration; Design automated workflows for the four mandatory invoice statuses.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-einvoice-fr
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Windsurf.
---

# Nex Einvoice FR

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-einvoice-fr). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

French businesses and developers are struggling to implement the complex 2026/2027 e-invoicing mandate, especially after the removal of the free PPF exchange service. Misunderstanding the technical requirements for Factur-X profiles or lifecycle statuses leads to non-compliance and heavy fines.

## What it does

- Generates precise applicability calendars based on SIREN size categories (GE, ETI, PME, Micro).
- Provides technical mapping for Factur-X profiles to ensure EN 16931 compliance.
- Defines mandatory lifecycle workflows including the critical distinction between 'rejetée' and 'refusée' statuses.
- Calculates e-reporting frequencies for B2C and cross-border flows based on specific VAT regimes.
- Structures decision trees for selecting Plateformes Agréées (PA/PDP) now that the PPF fallback is gone.

## Why this beats prompting it yourself

General LLMs often reference outdated 2024 timelines or suggest using the now-defunct free PPF exchange. This skill encodes the June 2026 verified regulatory state, including the 120+ registered PA ecosystem and exact e-reporting decade frequencies.

## Use cases

- Building a readiness roadmap for a French SME or ETI finance department.
- Mapping technical fields for an ERP integration with a Plateforme Agréée.
- Designing the accounting workflow for handling rejected vs. refused electronic invoices.
- Determining e-reporting obligations for auto-entrepreneurs and B2C retailers.

## Known limitations

Does not replace EN 16931 or Peppol BIS 3.0 core semantics. Focuses strictly on the French country-specific layer and mandate mechanics.

## Example

**Request**

We are a French PME using 'réel normal' VAT. When do we need to start issuing e-invoices, and what are our e-reporting deadlines for B2C sales?

**Result**

As a PME, your issuance mandate starts September 1, 2027. However, you must be able to receive e-invoices by September 1, 2026. For B2C e-reporting under 'réel normal', you must transmit transaction data every decade (10-day period) within 10 days of the period ending.

## Questions

### How does nex einvoice fr help with the upcoming French tax regulations?

This skill automates the complex transition to the French 2026/2027 e-invoicing mandate by providing accurate Factur-X mapping, e-reporting frequencies, and PDP selection logic based on the latest regulatory updates.

### Why should I use this skill instead of a standard AI prompt?

Unlike generic AI models that may use outdated 2024 data, this skill is specifically tuned to the June 2026 verified regulatory state and the current 'PPF-free' ecosystem of registered Plateformes Agréées (PDP).

### Does this skill provide technical specifications for ERP integration?

The skill provides structured technical mapping for Factur-X profiles (EN 16931) and specific lifecycle status workflows, making it ideal for developers integrating ERP systems with French tax platforms.

### Which AI platforms are compatible with this skill?

This skill is designed to work with major LLMs and AI agent platforms; once purchased, you can instantly deploy it within your preferred workflow tool to start generating compliance roadmaps.

### What exactly is included in the purchase of this skill?

You receive the full agent logic for generating applicability calendars, e-reporting decision trees for B2C/cross-border flows, and the technical frameworks required for PDP selection.

### Are there any specific technical limitations I should be aware of?

The skill focuses on the French country-specific layer and mandate mechanics; it is intended to complement, not replace, the core EN 16931 or Peppol BIS 3.0 semantic documentation.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
