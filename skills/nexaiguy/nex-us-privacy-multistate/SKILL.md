---
name: nex-us-privacy-multistate
description: 'Automated US multi-state privacy compliance engine for threshold mapping, policy generation, and DSR workflows. Use when: Map business data to 20+ state-specific legal thresholds automatically; Generate state-keyed privacy policies with California-specific disclosure blocks; Create DSR workflows that handle GPC signals and 45-day response windows.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-us-privacy-multistate
compatibility: Compatible with Claude Code, Cursor, Windsurf, and other SKILL.md-compatible agents.
---

# Nex US Privacy Multistate

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-us-privacy-multistate). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

SMBs selling across the US face a fragmented landscape of 20+ state privacy laws with no federal standard. Missing a volume threshold or failing to register as a data broker leads to daily fines of $200 per request or statutory penalties up to $7,500 per violation.

## What it does

- Determines legal applicability across all 20 active US state privacy laws using verified 2026 thresholds.
- Generates multi-state privacy policies with state-specific disclosure blocks for California, Texas, and strict outliers like Maryland.
- Builds Data Subject Request (DSR) workflows including intake, verification logic, and Global Privacy Control (GPC) technical requirements.
- Provides specialized checklists for California Delete Act compliance and DROP platform registration.
- Produces a compliance calendar for upcoming legislative changes through 2028.

## Why this beats prompting it yourself

General LLMs often hallucinate thresholds or rely on outdated 2023 data. This skill uses a verified June 2026 logic engine that accounts for recent amendments in Montana and Connecticut, plus specific SBA small business exemptions in Texas and Nebraska that generic prompts miss.

## Use cases

- Determine if a growing e-commerce brand has hit the 35,000-resident threshold for Maryland or Delaware.
- Draft a privacy policy that satisfies California's CCPA/CPRA while handling Texas consent requirements for sensitive data.
- Set up a standardized 45-day DSR response pipeline that covers access, deletion, and the right to appeal.
- Audit a company's data broker status to avoid $6,000+ registration penalties.

## Known limitations

Does not cover federal HIPAA or GLBA specific filings. Only covers California for employee/B2B data contexts as other states remain consumer-focused.

## Example

**Request**

We have 40,000 customers in Connecticut and 10,000 in Virginia. We use Meta pixels for retargeting. Which laws apply to us in 2026 and what do we need to change?

**Result**

You trigger CTDPA (CT) as you exceed the 35,000 resident threshold effective July 2026. Because you use Meta pixels, you are 'selling/sharing' data and must implement GPC signal support and a clear 'Opt-Out of Targeted Advertising' link. Virginia does not apply yet (100k threshold).

## Questions

### How does this skill help manage the fragmented US privacy law landscape?

This skill identifies which of the 20+ state privacy laws apply to your business based on 2026 thresholds, generates localized privacy policies, and creates technical workflows for handling Data Subject Requests (DSRs).

### How is this engine more accurate than simply prompting a standard LLM for legal advice?

Unlike general AI, this skill uses a verified June 2026 logic engine that accounts for specific nuances like Montana's recent amendments and unique small business exemptions in Texas and Nebraska that generic models often overlook.

### What exactly is included in the purchase of the nex-us-privacy-multistate skill?

You receive the full multi-state logic engine, a suite of policy generation templates, automated DSR intake workflows, a California Delete Act checklist, and a compliance calendar tracking legislative changes through 2028.

### Is this skill compatible with my existing AI agent or automated workflow?

Yes, the skill is designed for seamless integration with most major AI agent frameworks and can be deployed as a backend compliance layer for your existing customer support or legal operations tools.

### Are there any specific industries or data types that this skill does not cover?

While it provides comprehensive coverage for consumer data across all 20 active states, it does not handle federal HIPAA or GLBA filings, nor does it cover non-consumer data (like B2B or employee data) outside of California.

### How does the skill stay updated as new state privacy laws are enacted?

The skill includes access to a live compliance calendar; as state laws are amended or new ones are passed, the underlying logic is updated to ensure your policy generation remains current through 2028.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
