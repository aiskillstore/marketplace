---
name: nex-ada-web-accessibility
description: 'Audit and document web accessibility to mitigate US ADA Title II/III litigation and meet DOJ compliance deadlines. Use when: Classify legal exposure under ADA Title II/III and state laws; Prioritize web fixes based on common US litigation patterns; Generate defensible US-flavor accessibility statements and plans.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-ada-web-accessibility
compatibility: Optimized for Claude Code, Cursor, Aider, and VS Code environments requiring precise WCAG auditing.
---

# Nex Ada Web Accessibility

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-ada-web-accessibility). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Web accessibility litigation is a serial filing industry where private businesses face Title III demand letters and government entities must meet strict new DOJ Title II deadlines. Developers often lack the legal context to prioritize fixes that actually mitigate lawsuit risk or to draft defensible compliance documentation.

## What it does

- Classifies organizational exposure under ADA Title II, Title III, Section 508, and the California Unruh Act.
- Executes a 50-point WCAG 2.1 AA audit focused on high-risk litigation targets like keyboard traps and form labels.
- Generates US-specific legal artifacts including accessibility statements and remediation plans.
- Provides response playbooks for ADA demand letters based on current US litigation patterns.
- Tracks binding DOJ deadlines for state and local government entities (2027-2028).

## Why this beats prompting it yourself

Generic prompts fail to account for the circuit split regarding "physical nexus" or the specific statutory damages under the California Unruh Act. This skill uses a verified 2026 legal fact base to prioritize remediation by what plaintiffs' firms actually target, rather than just technical specs.

## Use cases

- Assess if a pure e-commerce site without physical stores is vulnerable to Title III suits.
- Audit a municipal government portal against the April 2027/2028 DOJ Title II deadlines.
- Draft a remediation plan after receiving a formal demand letter from a serial plaintiff.
- Prepare an accessibility statement for a SaaS vendor selling to federal agencies under Section 508.

## Known limitations

Does not constitute legal advice, all outputs must be reviewed by counsel. Focuses on WCAG 2.1 AA as the US legal benchmark rather than the newer 2.2 standard.

## Example

**Request**

We just got a demand letter for our Shopify store citing ADA violations in California. What is our exposure and what should we fix first?

**Result**

You face high exposure under the California Unruh Act, which carries $4,000 minimum statutory damages per violation. Priority 1 fixes: 1. Missing alt text on product images. 2. Missing form labels in checkout. 3. Inaccessible popups. I have generated a response playbook for your counsel.

## Questions

### How does this skill help me avoid ADA-related lawsuits compared to a standard accessibility checker?

This skill identifies high-risk technical vulnerabilities that trigger litigation, generates defensible accessibility statements, and tracks specific DOJ deadlines for Title II and III compliance.

### Which AI agents or platforms can I use with the nex-ada-web-accessibility skill?

The skill is compatible with major LLM platforms like ChatGPT, Claude, and specialized legal-ops agents that support custom skill integrations.

### Why should I use this skill instead of just prompting a standard AI with WCAG guidelines?

Unlike general AI, this skill uses a specialized 2026 legal fact base that accounts for the 'physical nexus' circuit split and specific statutory damages under the California Unruh Act.

### What specific assets are included when I purchase this skill?

You receive the core audit logic, 50-point WCAG 2.1 AA check-list, demand letter response playbooks, and automated compliance documentation templates.

### Does this skill support the latest WCAG 2.2 standards?

The skill focuses on WCAG 2.1 AA because it remains the primary legal benchmark used by US courts and the DOJ for current compliance mandates.

### How are updates handled if ADA regulations or DOJ deadlines change?

Updates are released periodically to reflect new court rulings and evolving DOJ enforcement dates, ensuring your remediation plans remain legally current through 2028.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
