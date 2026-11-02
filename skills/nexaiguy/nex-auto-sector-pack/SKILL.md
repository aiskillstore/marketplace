---
name: nex-auto-sector-pack
description: 'Automates Belgian automotive sales docs, Car-Pass workflows, and 2022 warranty compliance for garages. Use when: Generate binding vehicle sales contracts with mandatory Belgian clauses; Automate Car-Pass mileage registration workflows for workshop interventions; Create used-car intake checklists for private trade-ins.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-auto-sector-pack
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Auto Sector Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-auto-sector-pack). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Belgian car dealers and garages often use outdated sales contracts that fail to meet the 2022 consumer warranty requirements. Missing a Car-Pass or failing to register mileage during repairs can lead to voided sales and heavy fines.

## What it does

- Generates legally compliant Belgian vehicle order forms (bestelbon) for B2C and B2B sales.
- Automates workshop workflows for mandatory Car-Pass mileage and repair descriptions.
- Produces intake checklists for used-car purchases and trade-ins with damage history tracking.
- Drafts warranty communication templates including acceptance and rejection letters under the 2022 rules.
- Calculates validity periods for inspection certificates and registration forms based on current Flemish regulations.

## Why this beats prompting it yourself

Generic LLMs often hallucinate Belgian warranty terms or miss specific 2024 Car-Pass reporting requirements. This skill enforces the exact structure required for legal validity, including the 2026 inspection reforms, ensuring no mandatory clauses are omitted.

## Use cases

- Drafting a binding sales agreement for a used car with the correct 1-year warranty limitation.
- Standardizing mileage registration procedures for workshop technicians to ensure Car-Pass compliance.
- Creating a professional rejection letter for a warranty claim based on wear and tear.
- Preparing a trade-in document for a private seller with open financing checks.

## Known limitations

Does not provide financial advice for specific credit or leasing contracts. Users must verify the final rollout of September 2026 inspection reforms via official channels like GOCA.

## Example

**Request**

Ik heb een tweedehandswagen verkocht aan een particulier. Maak een bestelbon voor een Volkswagen Golf, chassis WVWZZZ123, 85.000km, eerste inschrijving 2021. De garantie is 1 jaar.

**Result**

BESTELBON / VERKOOPOVEREENKOMST
Verkoper: [Naam Garage] KBO: [Nummer]
Koper: [Naam]
Voertuig: Volkswagen Golf (2021)
VIN: WVWZZZ123
KM-stand: 85.000
Garantie: 12 maanden (overeenkomstig wet 1 juni 2022)
OPMERKING: Verkoper overhandigt Car-Pass bij levering. Zonder Car-Pass is verkoop nietig.

## Questions

### How does this skill help my garage stay compliant with Belgian law?

This skill generates legally compliant sales contracts (bestelbon), automates Car-Pass mileage reporting workflows, and manages 2022 warranty documentation specifically tailored for the Belgian automotive market.

### What exactly is included in the nex-auto-sector-pack?

You receive a comprehensive set of automation workflows for B2C/B2B sales, intake checklists for trade-ins, and standardized warranty communication templates that reflect the latest 2024 reporting requirements.

### Does the skill cover the specific warranty rules for second-hand vehicle sales?

Yes, the skill is designed to handle the specific warranty limitation clauses for used vehicles and includes upcoming 2026 inspection reform logic to keep your documentation future-proof.

### What AI platforms is this skill compatible with?

The pack is a set of specialized agent instructions and document structures compatible with most major LLMs and AI agent platforms; setup involves importing these configurations into your preferred workspace.

### How are updates handled if Belgian automotive regulations change?

We provide regular updates to the templates whenever Belgian automotive legislation changes, such as new Car-Pass reporting mandates or GOCA inspection updates.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
