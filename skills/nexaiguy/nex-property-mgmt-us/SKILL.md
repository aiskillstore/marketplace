---
name: nex-property-mgmt-us
description: 'Runs a small US rental portfolio: tenant screening, lease packets, notices, maintenance workflow and move-out accounting. Use when: Generate state-specific residential lease agreements; Calculate security deposit return deadlines and itemizations; Draft compliant pay-or-quit and entry notices.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-property-mgmt-us
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Property Mgmt US

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-property-mgmt-us). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Builds the tenant screening workflow with the fair-housing safe application criteria and the adverse action notice.
- Assembles the lease packet with required disclosures such as lead-based paint and the state-specific addenda checklist.
- Generates the notice ladder: late rent, cure or quit, entry notice, non-renewal.
- Runs move-out accounting with the security deposit itemisation and the statutory return deadline.

## Use cases

- A landlord with a handful of units doing their own paperwork
- Screening applicants consistently and defensibly
- Documenting a maintenance request trail before a dispute
- Returning a deposit correctly with an itemised statement

## Known limitations

US only, and landlord-tenant law is state and city specific. Output is a working draft, not legal advice, and eviction or deposit disputes should go to counsel. Verify state deadlines and notice periods before sending anything.

## Example

**Request**

I need to draft a 3-day pay or quit notice for a tenant in Florida who is late on rent.

**Result**

NOTICE TO PAY RENT OR DELIVER POSSESSION
Date: 10/24/2024
To: [Tenant Name]
You are hereby notified that you are indebted to me in the sum of $[Amount] for the rent and use of the premises. I demand payment of the rent or possession of the premises within 3 days.

## Questions

### How does it handle different state laws?

The skill asks for your state and city to identify local rules and requires you to verify specific numbers against current statutes before finalizing documents.

### What is included in the lease package?

It generates a universal core lease and a separate state-specific addendum covering deposits, late fees, and required disclosures.

### Does it help with security deposits?

It provides a structured workflow for move-out accounting, including itemized deduction letters and state-specific return deadlines.

### Can this file an eviction for me?

No. This skill provides working drafts for administrative use. Any legal action like an eviction filing should be reviewed by licensed counsel.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
