---
name: nex-favv-food-pack
description: 'Builds FAVV registration decision trees, EU 1169/2011 label checklists, HACCP plans, allergen matrices, and recall workflows for Belgian food businesses. Use when: Determine if you need a FAVV registration, permit, or approval; Create EU 1169/2011 compliant food labels in Dutch; Build HACCP and autocontrole structures for small kitchens.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-favv-food-pack
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex FAVV Food Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-favv-food-pack). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Walks the FAVV three-level decision tree (registratie, toelating, erkenning) from your activity, product group, and scale, and tells you which status to apply for.
- Produces label checklists with the literal mandatory fields of EU Regulation 1169/2011: the 11 required mentions, the fixed nutrition table order, minimum x-height font sizes, and small-package exemptions.
- Generates HACCP and autocontrole plan structures on the 7 principles, tuned to small producers using approved sector guides like G-044.
- Builds allergen matrices covering the 14 Annex II allergens, usable as a counter or kitchen document for non-prepacked food.
- Encodes the meldingsplicht and recall workflow: block, trace via register UIT, report to the LCE, consumer recall, corrective documentation.

## Why use this

A food label that fails inspection or a missing autocontrole system costs real money in Belgium. This pack turns FAVV and EU labeling rules into working documents rather than theory, with a facts section verified against favv-afsca.be and EUR-Lex sources as of June 2026. Documents come out in Dutch, matching what Flemish inspectors and customers expect.

## Use cases

- A small food producer deciding between registratie, toelating and erkenning
- Building a compliant Dutch label for a prepacked product
- Writing a first HACCP and autocontrole plan for a small kitchen or workshop
- Preparing an allergen matrix for non-prepacked food at a counter
- Having a recall workflow ready before you need it

## Known limitations

Belgian and EU rules only, not other jurisdictions. Output is a working draft for your own review, not an FAVV-approved document, and sector guides plus the current FAVV pages should be checked at the time of use.

## Example

**Request**

I am starting a small bakery in Ghent selling sourdough bread directly to customers. Do I need a registration or a permit from FAVV, and what should my label include?

**Result**

Based on your B2C sales of fresh bread, you need a Permit (Toelating). Your label must include: 1. Benaming (Zuurdesembrood), 2. Allergenen (Gluten), 3. Nettohoeveelheid, 4. Houdbaarheid, 5. Naam/Adres exploitant. Note: Micro-bakeries are exempt from the nutrition table.

## Questions

### Is the labeling advice compliant with Belgian law?

It follows EU 1169/2011 and Belgian FAVV-AFSCA standards as of June 2026.

### Does it generate documents in Dutch?

Yes, the skill specializes in Dutch outputs, the standard for Flemish food inspections.

### What types of food businesses are supported?

It covers small producers, Horeca, B2B suppliers, and webshops.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
