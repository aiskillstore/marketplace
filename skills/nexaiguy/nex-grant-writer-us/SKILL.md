---
name: nex-grant-writer-us
description: 'Guides a US nonprofit from grant prospect research to a submitted federal or foundation proposal with budget, narrative and compliance checks. Use when: Generate compliant SF-424A budget justifications with 15% MTDC rates; Draft SBIR Phase I skeletons for NSF, NIH, and DoD agencies; Create logic models to align grant activities with measurable outcomes.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-grant-writer-us
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Aider, and Cursor.
---

# Nex Grant Writer US

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-grant-writer-us). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Runs prospect research across Grants.gov, foundation 990s and state portals, then scores fit before you write anything.
- Builds the proposal skeleton required by the funder: need statement, goals and objectives, methods, evaluation plan, sustainability, organisational capacity.
- Generates a line-item budget with a matching budget narrative and an indirect cost rate note.
- Runs a submission compliance check against the funder announcement, page limits, attachments and registration prerequisites.

## Use cases

- A small nonprofit writing its first federal grant application
- Reworking a rejected proposal against reviewer criteria
- Building a reusable boilerplate library for recurring funders
- Checking a proposal for compliance before the deadline

## Known limitations

US grants only. Output is a working draft, not a submission-ready document, and it does not file anything on your behalf. Funder requirements change, so verify current guidance in the announcement before submitting.

## Example

**Request**

Help me draft a budget justification for a $250k federal grant using the new 15% de minimis indirect rate.

**Result**

I have generated a budget justification following SF-424A guidelines.
- Personnel: [User Data Needed]
- Fringe: [User Data]
- Indirect Costs: Calculated at 15% of MTDC (excludes equipment and subaward amounts >$50k).
Full skeleton ready for your figures.

## Questions

### What indirect cost rate does it use?

The skill applies the 2024 OMB revision (2 CFR 200) allowing a 15% de minimis indirect rate on Modified Total Direct Costs (MTDC).

### Does it support SBIR applications?

Yes, it handles SBIR/STTR Phase I skeletons for NSF, NIH, and DoD, including agency-specific portal requirements and registration steps.

### How does it ensure proposal consistency?

It follows a logic-model-first approach to ensure every activity in your narrative is linked to a specific outcome and budget line.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
