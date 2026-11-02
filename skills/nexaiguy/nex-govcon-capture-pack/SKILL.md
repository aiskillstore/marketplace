---
name: nex-govcon-capture-pack
description: 'Takes a small business from SAM.gov registration to compliant federal RFP responses with capability statements and compliance matrices. Use when: Register a small business on SAM.gov for free; Map ownership to 8(a), WOSB, SDVOSB, or HUBZone certifications; Generate a one-page government capability statement.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-govcon-capture-pack
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Govcon Capture Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-govcon-capture-pack). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Walks the SAM.gov registration checklist (Login.gov, entity validation, UEI, CAGE, NAICS and PSC codes, EFT banking, free 365-day renewal), leading with the warning that registration is free.
- Maps ownership and location to the right SBA certification: 8(a), WOSB or EDWOSB, SDVOSB, or HUBZone, all via the SBA certification portal.
- Generates a one-page capability statement with core competencies, past performance, differentiators and a codes block.
- Builds RFP response skeletons driven by Sections L and M of the Uniform Contract Format, with the standard four-volume structure.

## Use cases

- Registering a small business on SAM.gov without paying a middleman
- Choosing and applying for the right set-aside certification
- Writing a one-page capability statement for agency outreach
- Responding to a federal RFP or RFI with a compliant volume structure and matrix

## Known limitations

US federal contracting only, state and local procurement differ. Output is a draft that needs professional review, and the skill appends that disclaimer on every deliverable. Certification eligibility rules and thresholds change, so verify current figures at certifications.sba.gov before applying.

## Example

**Request**

I need a compliance matrix for a new federal RFP. Here are Sections L and M. Also, remind me what I need for my SAM renewal.

**Result**

I have generated a compliance matrix mapping Section L instructions to Section M factors. For your SAM.gov renewal: it is free, requires a Login.gov account, and you must verify your UEI and CAGE data. Start 60 days before expiration.

## Questions

### Does this skill handle the full SAM.gov process?

It covers the UEI, CAGE code, NAICS selection, and EFT banking steps, while warning against common paid registration scams.

### How does it help with SBA certifications?

The skill provides a mapping for 8(a), WOSB/EDWOSB, SDVOSB, and HUBZone programs based on your business profile.

### Can it help me structure a complex RFP response?

It builds a skeleton based on Section L instructions and Section M evaluation factors to ensure all requirements are met.

### Can I create a capability statement with this?

Yes, it generates a professional one-page capability statement including core competencies and past performance.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
