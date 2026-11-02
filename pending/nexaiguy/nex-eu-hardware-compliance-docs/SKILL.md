---
name: nex-eu-hardware-compliance-docs
description: 'Generates CE Declaration of Conformity, RoHS statement, and REACH SVHC declaration templates from your hardware product details. Use when: Create a draft CE Declaration of Conformity for new electronics; Generate RoHS 3 compliance statements for supplier files; Draft REACH SVHC declarations for Article 33 requirements.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-eu-hardware-compliance-docs
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex EU Hardware Compliance Docs

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-eu-hardware-compliance-docs). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Produces a fill-in CE Declaration of Conformity with manufacturer, product, directive, and standards fields
- Produces a RoHS compliance statement under Directive 2011/65/EU as amended by 2015/863/EU
- Produces a REACH SVHC declaration covering the Article 33 supplier communication duty under Regulation 1907/2006
- Runs a structured intake: product and model, manufacturer legal name, EU authorized representative, applicable directives, standards, restricted substances
- Marks anything you cannot provide as an explicit [PLACEHOLDER] instead of guessing, and ships a date-stamped directive reference

## Why use this

Writing your first CE, RoHS, and REACH paperwork from scratch means reverse-engineering directive language. This gives you the correct document structures with every required field named, so your compliance engineer reviews a draft instead of starting blank. The skill never assumes which directives apply and never fills in what it does not know, which keeps the output honest and reviewable.

## Use cases

- A hardware startup preparing its first CE marking documentation package
- An importer needing RoHS and REACH declarations for a supplier file
- A manufacturer outside the EU documenting its authorized representative
- Refreshing compliance documents after a product or standards change

## Known limitations

This is document scaffolding, not legal advice. Confirm the applicable directives and engage a qualified compliance engineer or notified body where required. Templates cover CE, RoHS and REACH only, not machinery, medical device or radio equipment specifics.

## Example

**Request**

Generate EU compliance templates for my hardware product: 'SmartHub X1' by 'NexGen Tech'. We use LVD 2014/35/EU and EMC 2014/30/EU. No RoHS restricted substances.

**Result**

I have generated three templates:
1. CE Declaration of Conformity: Includes SmartHub X1, NexGen Tech, LVD 2014/35/EU, and EMC 2014/30/EU.
2. RoHS Statement: Confirms compliance with 2011/65/EU.
3. REACH SVHC: Placeholder for supplier communication.
Review and sign these before use.

## Questions

### Does this replace a certification lab?

No. This skill provides document scaffolding based on your input. It does not perform testing or provide legal verification of your compliance status.

### What specific documents are included?

The skill generates a CE Declaration of Conformity, a RoHS Statement, and a REACH SVHC Declaration template.

### How current are the regulatory references?

The skill uses a reference file with date-stamped directive information. You should verify all directives against the latest Official Journal of the EU.

### Can it handle manufacturers outside the EU?

Yes, the skill includes placeholders for an EU Authorized Representative, which is required for non-EU manufacturers.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
