---
name: nex-iso27001-kmo-pack
description: 'Builds an ISO 27001 documentation set for a Belgian SME: scope, risk assessment, Statement of Applicability and the core Annex A policies. Use when: Generate a complete ISMS scope statement for a Belgian legal entity; Conduct a NIS2 readiness quickcheck for Belgian organizations; Create a risk register with pre-defined SME impact/likelihood defaults.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-iso27001-kmo-pack
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and Cursor.
---

# Nex Iso27001 KMO Pack

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-iso27001-kmo-pack). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Defines the ISMS scope and context, with the interested-parties and boundaries sections auditors ask for first.
- Runs the risk assessment and treatment plan with a likelihood-times-impact matrix and an owner per risk.
- Generates the Statement of Applicability across the Annex A controls, with justification for every inclusion and exclusion.
- Produces the core policy set: access control, supplier security, incident response, business continuity, secure development.

## Use cases

- An SME preparing for a first ISO 27001 certification audit
- Answering an enterprise customer security questionnaire with real documents
- Refreshing an ISMS after a scope or supplier change
- Building a risk register that a certification body will accept

## Known limitations

Documentation scaffolding, not certification. A certification body still has to audit you and an internal audit plus management review are required. Tuned to Belgian and EU SME practice.

## Example

**Request**

Start een ISO 27001 traject voor mijn Belgische IT-kmo met 15 medewerkers. We vallen waarschijnlijk onder NIS2.

**Result**

Prima. Laten we beginnen met de NIS2-quickcheck en de Scope.
1. Sector: IT/Digitale infrastructuur?
2. Omzet: >10M?
3. Medewerkers: 15 (Kmo-status bevestigd).
Op basis van 15 VTE bent u een kleine entiteit, maar mogelijk NIS2-plichtig via de keten. Zal ik het Scope Statement opstellen?

## Questions

### Does this skill provide official ISO 27001 certification?

No. It creates the documentation scaffolding. You still need an accredited auditor for certification and must perform internal audits.

### Does this cover Belgian NIS2 requirements?

Yes, it includes a NIS2 quickcheck to determine if your company is an essential or important entity under Belgian law.

### Which version of ISO 27001 does this use?

It targets the 2022 version, covering all 93 Annex A controls across the four updated themes.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
