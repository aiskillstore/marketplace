---
name: nex-kinderopvang-admin
description: 'Regelt de administratie van een Vlaamse kinderopvang: inschrijvingen, aanwezigheidsregistratie, facturatie en het fiscaal attest. Use when: Genereer een huishoudelijk reglement volgens de Opgroeien-vereisten; Stel een volledig vergunningsdossier op voor een nieuwe opvanglocatie; Maak schriftelijke ouderovereenkomsten voor IKT of vrije prijs.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-kinderopvang-admin
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Kinderopvang Admin

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-kinderopvang-admin). Scripts, extension source, and templates from the original package are not in this folder.

## Wat het doet

- Bouwt het inschrijvingsdossier met opvangplan, schriftelijke overeenkomst en huishoudelijk reglement volgens de Opgroeien-vereisten.
- Structureert de aanwezigheidsregistratie en de omzetting naar gefactureerde dagen, inclusief afwijkingen en gerechtvaardigde afwezigheden.
- Genereert de maandfactuur per kind met de juiste tarieflijnen en de opvangtoeslag.
- Maakt het fiscaal attest kinderopvang klaar met de gegevens die de fiscus verwacht.

## Gebruikssituaties

- Een zelfstandige onthaalouder of kleine opvang die de papierwinkel zelf doet
- Maandelijkse facturatie zonder fouten in aanwezigheden
- Fiscale attesten klaarmaken in januari
- Een nieuw kind inschrijven met een volledig dossier

## Bekende beperkingen

Gericht op Vlaanderen en de Opgroeien-regelgeving, niet op Brussel of Wallonie. De output is een werkdocument, geen officieel goedgekeurd formulier, en tarieven en attestregels moeten je op het moment van gebruik nakijken.

## Example

**Request**

Maak een huishoudelijk reglement voor een nieuwe groepsopvang met inkomenstarief (IKT) en zelfstandige begeleiders. Gebruik de 2026 klachtenregels.

**Result**

# Huishoudelijk Reglement [NAAM]
1. Identificatie: [ONDERNEMINGSNUMMER]
2. Beleid: Open van 07:30 tot 18:30.
3. Prijs: Inkomenstarief (IKT) via Mijn Kind en Gezin.
4. Klachten: U kunt zich rechtstreeks wenden tot het Opgroeipunt zonder verplichte interne melding.
[VOLLEDIG DOCUMENT GEGENEREERD]

## Questions

### Zijn de documenten up-to-date met de nieuwste wetgeving?

De skill volgt de meest recente Opgroeien-besluiten, inclusief de wijzigingen uit het Plan kinderopvang 2025-2029 en het nieuwe handhavingskader.

### Werkt dit ook voor zelfstandige onthaalouders?

Zeker. De skill kent de specifieke eisen voor gezinsopvang, groepsopvang en samenwerkende onthaalouders (groepSOO).

### Helpt dit bij de voorbereiding op een inspectie?

De skill genereert een volledig dossier conform de Zorginspectie-vereisten, inclusief kwaliteitsonderdelen zoals de crisisprocedure.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
