---
name: nex-eu-accessibility-audit
description: 'Audits a website or app against the European Accessibility Act and WCAG 2.1 AA, producing a scope memo, remediation report, and accessibility statement. Use when: Determine if a business falls under European Accessibility Act scope; Perform a full WCAG 2.1 AA audit with step-by-step testing instructions; Create prioritized remediation reports with specific code fixes.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-eu-accessibility-audit
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and Aider.
---

# Nex EU Accessibility Audit

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-eu-accessibility-audit). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Walks a decision tree to determine EAA scope under Directive 2019/882: service categories, product rules, the micro-enterprise exemption and the disproportionate-burden route, then writes a scope memo you can put in a file.
- Runs the full WCAG 2.1 AA audit across all 50 A and AA success criteria, covering keyboard, screen reader, zoom, reflow and automated scanning.
- Produces a prioritised remediation report: what is blocking, what is risky, what is cosmetic, with the fix per finding.
- Generates the accessibility statement in the structure regulators expect, including the feedback mechanism and the enforcement contact.
- Ships the reusable checklist core so the same audit can be re-run after each release.

## Why use this

The European Accessibility Act applies from June 2025 and most SME sites have never been audited. This turns an intimidating directive into a scoped memo, a ranked fix list and a publishable statement.

## Known limitations

Built for GDPR compliance and EU accessibility law, not US ADA litigation. Automated scanning finds roughly a third of issues, the manual checks in the skill find the rest. The statement is a working draft, have counsel review it before publishing.

## When to use

- Determine if a business falls under European Accessibility Act scope.
- Perform a full WCAG 2.1 AA audit with step-by-step testing instructions.
- Create prioritized remediation reports with specific code fixes.
- Generate EN 301 549 compliant accessibility statements for regulators.

## Example

**Request**

Our German webshop has 15 employees and 3M turnover. Does the EAA apply to us, and can you audit our checkout flow?

**Result**

**EAA Scope: In Scope.** You exceed the micro-enterprise threshold.
**Audit Sample: Checkout Flow.**
- Result: Fail (Criterion 2.1.1). Payment button not keyboard accessible.
- Fix: Use a button element instead of a div.
- Statement: Draft generated per EN 301 549 requirements.

## Questions

### Does this skill cover all the requirements for the 2025 European Accessibility Act?

The skill audits your digital products against Directive 2019/882 (EAA) and all 50 WCAG 2.1 AA success criteria, helping you avoid compliance risks before the June 2025 deadline.

### What specific deliverables are included in the audit output?

You will receive a formal scope memo regarding exemptions, a prioritized remediation report with specific fix instructions, a draft accessibility statement for your site, and a reusable audit checklist.

### How does this skill handle accessibility issues that can't be detected by automated scanners?

While it uses automated scanning for efficiency, the skill also guides users through manual checks for keyboard navigation, screen readers, and reflow to catch the 70% of issues that automated tools typically miss.

### Do I need to be a legal expert or developer to run the accessibility audit?

The skill is designed for ease of use; you simply provide the website URL or application details, and the AI walks you through a decision tree to determine your specific legal obligations.

### Can I use this skill to re-audit my site after I've applied the suggested remediations?

Yes, the purchase includes a reusable checklist core, allowing you to re-run the audit after implementing fixes or launching new features to ensure continuous compliance.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
