---
name: nex-trucking-compliance
description: 'Automates FMCSA compliance, DQ files, IFTA filings, and audit readiness for small US motor carriers. Use when: Build audit-ready DQ files for new and existing drivers; Calculate per-jurisdiction taxable gallons for IFTA quarterly filings; Manage DOT drug and alcohol program documentation and random testing rates.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-trucking-compliance
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Trucking Compliance

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-trucking-compliance). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Small motor carriers often fail FMCSA audits not because of unsafe driving, but because of missing or incomplete paperwork. Maintaining Driver Qualification (DQ) files, Clearinghouse queries, and IFTA filings manually leads to expensive fines and lost operating authority.

## What it does

- Generates complete Driver Qualification (DQ) files with specific 49 CFR 391.51 retention logic.
- Orchestrates new driver onboarding workflows including Clearinghouse consents and pre-employment drug test tracking.
- Calculates IFTA quarterly fuel tax obligations across multiple jurisdictions based on mileage and fuel receipts.
- Produces new entrant safety audit readiness checklists to prevent automatic failure triggers.
- Tracks critical expiration dates for medical certificates, annual MVRs, and UCR registrations.

## Why this beats prompting it yourself

Generic LLMs often hallucinate specific DOT regulations or mix up CDL and non-CDL requirements. This skill uses verified June 2026 mandates, including exact CFR citations and the 50 percent random drug testing rate, ensuring your documentation stands up to a professional audit.

## Use cases

- Onboarding a new CDL driver while ensuring all 49 CFR 391.23 safety history requests are sent.
- Preparing for a New Entrant Safety Audit within the first 12 months of operation.
- Calculating quarterly IFTA returns to avoid the 10 percent late filing penalty.
- Managing annual Clearinghouse limited queries for a fleet of owner-operators.

## Known limitations

Does not cover Mexico- or Canada-domiciled operations. Intrastate-only rules vary by state and require local verification.

## Example

**Request**

I just hired a new CDL driver. What do I need for their DQ file and what needs to happen before their first dispatch to stay compliant?

**Result**

I have generated a 49 CFR 391.51 checklist. Before the first dispatch, you must: 1. Receive a verified negative DOT drug test. 2. Run a full Clearinghouse query. 3. Verify the Medical Examiner is on the National Registry. 4. Document the Road Test or CDL equivalent. Safety history requests to prior employers must be sent within 30 days.

## Questions

### How does nex-trucking-compliance help my fleet pass an FMCSA audit?

The skill automates the creation and maintenance of Driver Qualification (DQ) files, IFTA tax calculations, and DOT audit checklists, ensuring small carriers meet current 49 CFR mandates without manual paperwork.

### Which AI agents or platforms is this compliance skill compatible with?

This skill is designed for use with leading AI agents like ChatGPT, Claude, and AutoGPT; you simply import the skill file to enable trucking-specific compliance logic in your preferred environment.

### What specific assets are included in the nex-trucking-compliance package?

Upon purchase, you receive the production-ready skill file, a Quick Start guide for onboarding new drivers, and a checklist for New Entrant Safety Audits.

### Will I receive updates if DOT regulations or IFTA tax rates change?

Yes, your purchase includes lifetime access to regulatory updates, ensuring your workflows reflect the latest FMCSA Clearinghouse rules and current IFTA tax jurisdiction changes.

### Can I use this skill for carriers operating outside of the United States?

While it excels at federal interstate CDL requirements, this skill is currently limited to US-domiciled carriers and does not cover specific intrastate-only or international (Canada/Mexico) regulations.

### How much technical setup is required to start generating IFTA filings or DQ files?

Setup takes less than five minutes; once you load the skill into your agent, you can immediately begin uploading mileage logs for IFTA or driver data for DQ file generation.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
