---
name: nex-einvoice-pl
description: 'Technical implementation guide for Polish KSeF e-invoicing, FA(3) schemas, and API onboarding. Use when: Map ERP invoice data to the mandatory FA(3) structured XML format; Design API authentication flows for test and production KSeF environments; Implement the offline24 procedure with required QR code generation logic.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-einvoice-pl
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Einvoice PL

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-einvoice-pl). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Integrating Polish KSeF (Krajowy System e-Faktur) is more than just XML mapping. Developers must manage a clearing model where invoices only legally exist once assigned a central KSeF number, requiring specific authentication flows and offline contingency logic.

## What it does

- Generates readiness checklists based on taxpayer category, gross sales, and VAT status.
- Provides FA(3) schema field structures for standard, correction (korekta), and advance (zaliczkowa) invoices.
- Outlines onboarding workflows for KSeF 2.0 API environments across test, demo, and production.
- Defines offline24 contingency procedures, including mandatory QR code rules and submission windows.
- Flags critical 2026 deadlines for penalty grace periods and token expiration.

## Frameworks & tools

KSeF 2.0 API, FA(3) XML Schema, MCU module (Moduł Certyfikatów i Uprawnień), and ZAW-FA filing protocols.

## Why this beats prompting it yourself

Generic LLMs often confuse KSeF clearing with Peppol exchange models. This skill enforces the specific FA(3) hierarchy, legal issuance dates based on transmission, and the technical requirements for Type 2 certificates needed for offline QR codes.

## Use cases

- Map legacy ERP data fields to the mandatory FA(3) XML structure.
- Build a recovery workflow for the offline24 mode and system failures.
- Determine the exact compliance deadline for a specific Polish entity or branch.
- Configure authentication using KSeF certificates, seals, or tokens before the 2027 cutoff.

## Known limitations

Requires a KSeF certificate for offline24 modes. Commercial attachments like PDFs must be sent out-of-band as the Zalacznik node is restricted to structured tax data.

## Example

**Request**

Provide the FA(3) field mapping for a correction invoice (korekta) where the error was present from the start.

**Result**

Set RodzajFaktury to 'KOR'. Under the Naglowek node, use WariantFormularza 3. In the Fa node, set TypKorekty to 'A' (error from start) and provide the mandatory PrzyczynaKorekty. You must include the DaneFaKorygowanej section referencing the original invoice's KSeF number.

## Questions

### How does nex-einvoice-pl differ from using a standard LLM for KSeF integration?

This skill provides a structured implementation roadmap specifically for the Polish FA(3) schema, including API onboarding workflows, authentication logic, and offline24 contingency procedures that generic AI models often misinterpret.

### Which AI agents or models are compatible with this skill?

The skill is designed to work with any major LLM (such as GPT-4, Claude 3.5, or Gemini) that supports technical documentation analysis and XML structure generation.

### What specific documentation and assets are included in this purchase?

You will receive the complete technical logic package, including FA(3) field mapping guides, API environment onboarding protocols, and specific compliance checklists for the 2026/2027 deadlines.

### Does this skill cover the technical requirements for the KSeF offline contingency mode?

Yes, the skill includes the mandatory procedures for 'offline24' mode, detailing how to generate compliant QR codes and the specific submission windows required by Polish tax law during system failures.

### How are updates handled if the Polish Ministry of Finance changes the FA(3) schema?

The skill is updated to reflect the latest KSeF 2.0 API specifications and FA(3) schemas; buyers will receive notifications when updates are released to reflect changes in Polish Ministry of Finance requirements.

### Do I need an existing KSeF certificate to use this implementation guide?

This skill focuses on the technical integration and data mapping; you will still need to acquire a qualified certificate or seal from a certified provider to authenticate with the KSeF production environment.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
