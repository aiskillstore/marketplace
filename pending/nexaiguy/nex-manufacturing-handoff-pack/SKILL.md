---
name: nex-manufacturing-handoff-pack
description: 'Turns a design package into a manufacturing handoff: BOM, drawing checklist, tolerance notes, supplier RFQ and first-article inspection plan. Use when: Standardize BOMs for supplier-ready RFQ packages; Generate PCB fabrication and assembly instruction templates; Create first-article inspection plans for quality control.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-manufacturing-handoff-pack
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Manufacturing Handoff Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-manufacturing-handoff-pack). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Normalises the bill of materials into a supplier-ready format with part numbers, quantities, materials and finishes.
- Runs a drawing package checklist so nothing ships without tolerances, datums, surface finish and revision control.
- Generates the RFQ pack per supplier with quantities, lead time questions and quality requirements.
- Builds the first-article inspection plan mapping every critical dimension to a measurement method.

## Use cases

- A hardware team handing a design to a contract manufacturer for the first time
- Requesting quotes from several suppliers on the same basis
- Preparing a first-article inspection before a production run
- Cleaning up a messy BOM inherited from CAD export

## Known limitations

Generic mechanical manufacturing, not PCB assembly or regulated medical device production. Output is a working document that your engineer reviews, and it does not replace a quality management system.

## Example

**Request**

I need to prepare a manufacturing handoff for my Project X PCB. It is a 4-layer board, ENIG finish, IPC Class 2. Help me generate the documentation pack.

**Result**

Generated the following templates:
- fabrication-notes.md: 4-layer, ENIG, IPC Class 2 specs.
- assembly-notes.md: SMT instructions.
- bom-cover-sheet.md: Ready for part data.
- revision-history.md: Initial release.
Next: Let's review the handoff-checklist.md together.

## Questions

### Does this skill generate Gerber or CAD files?

No. It provides Markdown templates for fabrication and assembly notes that you must include alongside your exported design files.

### What documents are included in the pack?

The skill covers standard mechanical and PCB handoffs, including BOM normalization, inspection plans, and fabrication notes.

### Can it help with quality control planning?

Yes. It generates a first-article inspection (FAI) plan that maps critical dimensions to specific measurement methods.

### Is this suitable for medical device manufacturing?

It is optimized for generic mechanical and electronics manufacturing, not for highly regulated medical or aerospace-grade certifications.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
