---
name: nex-medical-billing-priorauth
description: 'Handles US prior authorisation and claim denials: payer requirement lookup, request packets, appeal letters and a denial tracking log. Use when: Generate formatted prior auth request packets for US payers; Classify denial codes into administrative or medical necessity routes; Draft structured first-level insurance appeal letters.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-medical-billing-priorauth
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and Aider.
---

# Nex Medical Billing Priorauth

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-medical-billing-priorauth). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Builds the prior authorisation request packet per payer with clinical justification, codes and the documents that payer actually asks for.
- Classifies denial reason codes and routes each to the right response: corrected claim, reconsideration, formal appeal or peer-to-peer.
- Drafts the appeal letter with the medical necessity argument and the policy citation.
- Keeps a denial tracking log so patterns per payer become visible instead of anecdotal.

## Use cases

- A small practice handling its own prior authorisations
- Turning a denial into a structured appeal instead of a rewrite from scratch
- Preparing a peer-to-peer review with the clinical argument ready
- Spotting which payer and which code drive most of your denials

## Known limitations

US payers only. Payer policies change constantly, so verify the current medical policy before submitting. Output is a working draft for a billing specialist or clinician to review, not clinical or legal advice.

## Example

**Request**

Draft a first-level appeal for patient John Doe, Member ID 12345, for a denied CPT 64493. The payer says it lacks medical necessity, but the notes show he failed PT for 6 weeks.

**Result**

**Appeal Letter: Level 1**
Patient: John Doe (ID: 12345)
Denied Service: CPT 64493
Basis: Medical Necessity

Summary: The provider documents the patient failed 6 weeks of conservative physical therapy (see notes dated 10/01-11/15) prior to this request. We request a reversal of this denial.

## Questions

### Does this skill suggest CPT or ICD-10 codes?

No. This skill only uses codes and clinical findings provided by the practice to ensure accuracy and compliance.

### How does it handle insurance denials?

It helps classify if a denial is administrative or based on medical necessity and routes the workflow accordingly.

### Can it track multiple authorizations at once?

The skill creates a structured tracking log to monitor pending authorizations and deadlines for every case.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
