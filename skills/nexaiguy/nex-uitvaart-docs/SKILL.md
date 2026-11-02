---
name: nex-uitvaart-docs
description: 'Generate Belgian death administration docs, roadmaps, and notification letters for funeral directors and families. Use when: Generate a first-week administrative roadmap for a Belgian death; Create notification letters for Belgian banks and insurance companies; Calculate regional inheritance tax deadlines and filing locations.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-uitvaart-docs
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Uitvaart Docs

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-uitvaart-docs). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Families and funeral directors in Belgium face a fragmented administrative burden after a death. Missing a deadline for the inheritance declaration or failing to notify a bank correctly can lead to financial penalties and blocked accounts.

## What it does

- Generates a day-by-day roadmap for the first week after a death in Belgium, including medical certificates and eLys digital declarations.
- Produces ready-to-use notification letters for banks, insurers, and utility providers with legally required identifiers.
- Calculates specific deadlines for inheritance declarations across Flanders, Brussels, and Wallonia based on the place of death.
- Runs a decision logic to determine if a free Certificate of Heredity (via MyMinfin) is sufficient or if a Notary Act is legally mandatory.
- Drafts comprehensive checklists for over 10 different Belgian authorities and utility sectors.

## Why this beats prompting it yourself

This skill integrates specific Belgian legislation updated for June 2026, including the eLys digital platform requirements and the 5,000 euro leefgeld regulations. It prevents generic AI hallucinations regarding regional tax deadlines and specific documentation routes that vary by marital status.

## Use cases

- A funeral director creating a structured administrative dossier to hand over to a grieving family.
- A family member drafting formal notifications to unblock bank accounts using the leefgeld rule.
- An executor determining whether to apply for a free certificate via MyMinfin or visit a notary.
- Planning the tax timeline for a death occurring abroad to avoid late-filing surcharges.

## Known limitations

The skill stops where the formal notary trajectory for complex estate liquidation begins. It does not provide specific legal advice for estates involving debts or minor heirs beyond the requirement for a Peace Judge authorization.

## Example

**Request**

Mijn vader is gisteren overleden in Gent. Wat moet ik regelen met de bank en wanneer moet de aangifte van nalatenschap gebeuren?

**Result**

Ik heb een draaiboek voor de eerste week opgesteld. Voor de bank: u heeft recht op maximaal 5.000 euro leefgeld als langstlevende partner zonder attest. De aangifte van nalatenschap in Vlaanderen moet uiterlijk binnen 4 maanden worden ingediend bij de Vlaamse Belastingdienst in Aalst.

## Questions

### How does this skill handle the different inheritance regulations across Belgian regions?

This skill automates the creation of Belgian-specific notification letters, calculated tax timelines, and administrative roadmaps, specifically accounting for regional variations in Flanders, Wallonia, and Brussels.

### What exactly is included in the output when I run this skill?

The skill provides a full administrative toolkit including custom letter templates, a day-by-day roadmap for the first week, and a decision logic tool to determine if a notary is legally required.

### Is the administrative logic up to date with the latest Belgian digital platform requirements?

The skill is updated with June 2026 legislation, including specific eLys digital platform requirements and the current €5,000 'leefgeld' rules for unblocking bank accounts.

### Can this skill help if the death occurred outside of Belgium but the deceased lived there?

Yes, the skill includes a specific module for deaths occurring abroad, helping you calculate adjusted filing deadlines for the Belgian inheritance declaration to avoid surcharges.

### Does this skill replace the need for a notary during the estate settlement process?

No, this skill is designed for administrative assistance; it identifies when a notary is legally mandatory and prepares the necessary paperwork, but does not replace formal legal counsel for complex estate liquidations.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
