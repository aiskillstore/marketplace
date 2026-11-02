---
name: nex-coppa-2026-pack
description: 'Audit and generate compliance documentation for the 2026 FTC COPPA Rule amendments. Use when: Classify services as child-directed or mixed audience using FTC criteria; Generate unbundled parental consent flows for third-party ad sharing; Draft mandatory written data retention and information security programs.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-coppa-2026-pack
compatibility: Compatible with Claude Code, Cursor, Aider, and Cline.
---

# Nex COPPA 2026 Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-coppa-2026-pack). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

The 2026 FTC COPPA amendments introduced heavy requirements, including unbundled consent for targeted ads and mandatory written security programs. Missing these details or failing the "totality of circumstances" test puts you at risk of $53,000+ fines per violation.

## What it does

- Triages services into child-directed, mixed, or general audience buckets using the FTC's multi-factor test.
- Generates dual-layer consent flows that separate baseline collection from third-party disclosure and targeted advertising.
- Drafts mandatory written documents including data retention policies, information security programs, and direct notices to parents.
- Inventories data against the 2026 expanded definitions of personal information, including biometric and government identifiers.
- Maps state-specific overlays for Arkansas, Connecticut, and California to ensure compliance beyond the federal floor.

## Why this beats prompting it yourself

General LLMs often reference outdated COPPA rules from 2013. This skill is hardcoded with the April 2026 mandates, ensuring you don't miss the specific "unbundled consent" requirement or the new public transparency duties for Safe Harbor members.

## Use cases

- Auditing a mobile game to see if its visual style triggers "child-directed" status.
- Building a neutral age-gate for a mixed-audience social platform.
- Drafting the mandatory written data retention policy for an EdTech tool.
- Configuring consent logic for ad SDKs to meet the 2026 disclosure rules.

## Known limitations

Applies to US COPPA and related state laws only. Does not cover GDPR-K or other international children's privacy frameworks.

## Example

**Request**

My app is a math game. Most users are 10-14. I use Unity Ads. Help me check if I'm compliant with the new 2026 COPPA rules.

**Result**

Based on your audience, you are likely a "Mixed Audience" service. You must implement a neutral age screen. Since you use Unity Ads, you need the new 2026 separate consent layer: parents must opt-in to third-party disclosures specifically. Here is your direct notice draft and retention policy.

## Questions

### How does the nex coppa 2026 pack differ from standard privacy policy generators?

This skill specifically automates the auditing of services against the 2026 'totality of circumstances' test and generates the required dual-layer consent flows and written security programs mandated by the latest FTC amendments.

### Which AI agents or platforms are compatible with this compliance pack?

The pack is compatible with most major LLM-based agents; once purchased, you can import the compliance logic and template structures directly into your preferred workspace.

### What specific documentation and tools are included in the purchase?

The purchase includes the full logic set for service triaging, automated templates for 2026-compliant data retention and security policies, and a mapping guide for state-specific overlays like those in California and Connecticut.

### Will this skill be updated if the FTC further amends COPPA requirements after 2026?

While this pack is optimized for the April 2026 FTC mandates, buyers receive lifetime access to all version updates if the FTC issues further clarifications or enforcement guidelines.

### Does this pack cover international children's privacy regulations like GDPR-K?

No, this skill is specifically engineered for US Federal COPPA compliance and relevant US state laws; it does not generate documentation for international frameworks like GDPR-K or the UK Age Appropriate Design Code.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
