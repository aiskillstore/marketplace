---
name: nex-riziv-zorgpraktijk
description: 'Regelt de RIZIV-administratie van een Belgische zorgpraktijk: conventiestatus, nomenclatuur, getuigschriften en derdebetaler. Use when: Generate convention vs. de-convention financial impact briefings; Draft legally mandatory tariff posters for waiting rooms; Set up eAttest and eFact administrative workflows.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-riziv-zorgpraktijk
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Windsurf.
---

# Nex RIZIV Zorgpraktijk

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-riziv-zorgpraktijk). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Managing RIZIV compliance in a Belgian healthcare practice is an administrative burden prone to costly errors. Practitioners struggle to calculate the financial impact of convention status, maintain legal patient communications, and follow shifting eAttest requirements.

## What it does

- Generates discipline-specific financial briefings for convention versus de-convention decisions.
- Produces legally compliant patient communications, including de-convention letters and mandatory tariff posters.
- Builds administrative intake structures for new patients covering eHealth consent and insurance status.
- Provides workflow checklists for eAttest, eFact, and third-party payer (derdebetalersregeling) rules.
- Calculates the financial impact of the 2026 minus 25 percent reimbursement rule for logopedists.

## Frameworks & tools

Supports Belgian healthcare standards including RIZIV/INAMI regulations, ProGezondheid workflows, and eAttest/eFact protocols for dentists, physiotherapists, and speech therapists.

## Why this beats prompting it yourself

This skill integrates specific 2026 indexation rates, legislative deadlines, and discipline-specific mandates that generic models often hallucinate. It enforces the strict legal distinction between administrative compliance and medical advice, ensuring documentation remains professional and safe.

## Use cases

- Drafting the mandatory tariff poster (tariefaffiche) required by the law of October 2021.
- Evaluating the ROI of de-conventioning based on current patient mix and social status loss.
- Automating the administrative checklist for a dental practice's mandatory eAttest workflow.
- Preparing patient notification letters regarding supplement changes and reimbursement impacts.

## Known limitations

Strictly limited to administrative and organizational tasks. Does not provide medical advice, diagnosis, or clinical nomenclature selection.

## Example

**Request**

Generate a briefing for a speech therapist considering de-conventioning in April 2026. My practice has 30% patients with increased reimbursement (verhoogde tegemoetkoming).

**Result**

Your de-convention briefing for April 2026:
- The -25% rule applies: Patients lose 25% reimbursement unless they have 'verhoogde tegemoetkoming' (30% of your base is safe).
- Financials: You lose the social status premium.
- Task: Update your 'tariefaffiche' to show the lower reimbursement.

## Questions

### How does it help with the convention decision?

It generates specific financial briefings for Kine, Dentist, and Speech Therapy disciplines, including the 2026 reimbursement rules and indexation rates.

### Can this skill give medical advice?

No. The skill is strictly for administrative and organizational tasks. It does not provide medical advice or select clinical nomenclature.

### Does it help with legal display obligations?

Yes, it includes structures for the mandatory tariff posters (tariefaffiche) required by the law of October 2021.

### How does it handle digital attestation?

It provides workflow checklists for eAttest and eFact, specifically addressing the 2025-2026 mandates for dentists and other paramedics.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
