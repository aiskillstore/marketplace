---
name: nex-us-construction-payapps
description: 'Generate US construction pay applications, G702/G703 structures, lien waivers, and certified payroll drafts. Use when: Automate G702/G703 progress billing calculations to avoid rounding errors; Identify and draft the correct state-specific statutory lien waiver; Prepare WH-347 certified payroll for Davis-Bacon federal projects.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-us-construction-payapps
compatibility: Optimized for agents that support SKILL.md system prompts, including Claude Code, Cursor, and Aider.
---

# Nex US Construction Payapps

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-us-construction-payapps). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Generating construction payment applications is a manual, error-prone process. A single rounding error or a missing statutory warning on a lien waiver can lead to rejected invoices, payment delays, or voided legal protections.

## What it does

- Generates G702 and G703-style progress billing structures with automated retainage and change order math.
- Produces a schedule of values (Continuation Sheet) with column-level reconciliation checks to prevent rounding mismatches.
- Identifies the correct lien waiver type and provides mandatory statutory language for regulated states like CA, TX, and FL.
- Drafts WH-347 certified payroll structures for Davis-Bacon compliance on federal projects, including Statement of Compliance requirements.
- Calculates retainage for completed work versus stored materials based on project-specific rates.

## Frameworks & tools

Compliant with US construction standards including AIA-style field structures, Davis-Bacon Act regulations (29 CFR 5.5), and state-specific Property and Civil Codes for lien waivers.

## Why this beats prompting it yourself

General LLMs often struggle with the specific "sum of lines" logic required to pass architect review and frequently miss state-mandated legal headers for lien waivers. This skill enforces a 9-line summary reconciliation against the continuation sheet, ensuring the total earned less retainage matches the current payment due to the cent.

## Use cases

- Drafting monthly progress billings for general contractors and subcontractors.
- Determining the correct conditional or unconditional lien waiver for a specific state.
- Setting up a Davis-Bacon compliant certified payroll sequence for a new federal job.
- Reconciling stored materials and retainage releases at substantial completion.

## Known limitations

Does not provide actual AIA-copyrighted forms; users must license official documents for final submission. Does not provide legal advice.

## Example

**Request**

Create a G702 summary for Application #3. Original contract $150,000. Total completed to date $45,000. Retainage is 10%. Previous payments $25,000. Project is in Texas.

**Result**

Line 1: $150,000.00
Line 3: $150,000.00
Line 4: $45,000.00
Line 5 (10% Retainage): $4,500.00
Line 6 (Total Earned): $40,500.00
Line 7 (Prev Certificates): $25,000.00
Line 8 (Current Due): $15,500.00
Note: TX Property Code 53.284 statutory waiver language required.

## Questions

### What specific construction billing challenges does this skill address?

The skill automates the complex math for AIA-style G702/G703 structures, including retainage and change orders, and provides state-specific statutory language for lien waivers to prevent payment delays and legal errors.

### Does this skill provide actual copyrighted AIA documents?

No, this skill generates the data structures and text required for these forms; you must still use officially licensed documents from the AIA for formal submissions to comply with their copyright.

### Which AI agents and platforms is this skill compatible with?

The skill is designed to work with any AI agent that supports structured data output and text generation, making it easy to integrate into your existing project management or accounting workflows.

### Does the skill account for different lien waiver requirements across various US states?

Yes, the skill includes logic to identify and provide mandatory statutory headers and language for highly regulated states like California, Texas, and Florida.

### What is included in the purchase of the nex-us-construction-payapps skill?

You receive the full logic set for generating pay apps, schedule of values, lien waivers, and Davis-Bacon compliant payroll drafts, along with documentation for implementation.

### How does this skill ensure mathematical accuracy compared to a standard LLM prompt?

Unlike generic prompts, this skill enforces strict 9-line summary reconciliation and column-level math checks to ensure the total earned matches the payment due to the cent, satisfying strict architect reviews.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
