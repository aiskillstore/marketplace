---
name: nex-landbouw-admin
description: 'Regelt de administratie van een Vlaams landbouwbedrijf: verzamelaanvraag, mestbankaangifte, perceelsregistratie en dierenregisters. Use when: Stel checklists op voor de Vlaamse verzamelaanvraag; Bereken VLIF-investeringssteun en controleer blokperiodes; Bereid de mestbankaangifte voor inclusief nieuwe PAS-data.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-landbouw-admin
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Landbouw Admin

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-landbouw-admin). Scripts, extension source, and templates from the original package are not in this folder.

## Wat het doet

- Bouwt de checklist voor de verzamelaanvraag met percelen, teelten en de ecoregelingen.
- Structureert de mestbankaangifte met dieraantallen, mestproductie en afzetdocumenten.
- Houdt de perceelsregistratie bij inclusief teeltrotatie en de randvoorwaarden.
- Genereert de dierenregisters en de bewegingen die Sanitel verwacht.

## Gebruikssituaties

- Een landbouwer die de verzamelaanvraag zelf indient
- De jaarlijkse mestbankaangifte voorbereiden
- Een controle door het departement voorbereiden
- Percelen en teeltrotatie netjes bijhouden

## Bekende beperkingen

Enkel Vlaanderen. Deadlines, ecoregelingen en normen wijzigen jaarlijks, dus verifieer op het moment van indienen bij het Departement Landbouw en Visserij en de VLM. De output is een werkdocument, geen ingediende aangifte.

## Example

**Request**

Ik ben een jonge landbouwer en wil een nieuwe stal bouwen met AER-investeringen. Welke VLIF-steun kan ik krijgen en wat zijn de blokperiodes voor 2026?

**Result**

Voor AER-investeringen krijg je 40, 65 of 80% steun, plus 25% extra als jonge landbouwer. Dit valt buiten het plafond van 300.000 euro.
Blokperiodes 2026:
- 20 jan t/m 31 maart
- 20 april t/m 30 juni
- 20 juli t/m 30 sept
- 20 okt t/m 15 dec
Zorg dat je omgevingsvergunning al rond is.

## Questions

### Dient deze skill de aangifte automatisch in?

Nee, de skill bereidt de data en checklists voor. Je moet de gegevens zelf nog definitief indienen via het e-loket van het Departement Landbouw of het Mestbankloket.

### Is de informatie up-to-date voor 2026?

De skill bevat de kernregels voor de campagne 2026, inclusief de nieuwe VLIF-blokperiodes en wijzigingen in ecoregelingen zoals het vervallen van de fotoplicht.

### Kan ik VLIF-steun voor jonge landbouwers berekenen?

Zeker. De skill ondersteunt de berekening van de 10 procent extra steun voor jonge landbouwers en de specifieke voorwaarden voor vakbekwaamheid en zeggenschap.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
