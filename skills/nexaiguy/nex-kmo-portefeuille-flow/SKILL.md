---
name: nex-kmo-portefeuille-flow
description: 'Loodst een Vlaamse kmo door de kmo-portefeuille: subsidiabiliteit, aanvraag, betaling via het portaal en de bewijsstukken. Use when: Bereken het juiste subsidiepercentage en plafond voor je onderneming; Genereer een stappenplan voor een foutloze subsidieaanvraag; Stel een bewijsstukkenlijst op voor een VLAIO controle.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-kmo-portefeuille-flow
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex KMO Portefeuille Flow

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-kmo-portefeuille-flow). Scripts, extension source, and templates from the original package are not in this folder.

## Wat het doet

- Checkt of je onderneming en je dienstverlener in aanmerking komen, met de actuele steunpercentages en plafonds per grootte.
- Bouwt de aanvraag op met projectomschrijving, prestatieperiode en de juiste pijler advies of opleiding.
- Zet de betaalflow uit: eigen aandeel storten, subsidie toegevoegd, facturatie via het portaal.
- Maakt de bewijsstukkenlijst klaar voor een eventuele controle achteraf.

## Gebruikssituaties

- Een kmo die voor het eerst kmo-portefeuille aanvraagt
- Een dienstverlener die klanten correct wil begeleiden
- Nakijken of een opleiding of advies subsidiabel is
- Een dossier bewijsklaar maken voor controle

## Bekende beperkingen

Enkel Vlaanderen. Steunpercentages, plafonds en de lijst van erkende dienstverleners wijzigen, dus verifieer altijd op vlaio.be op het moment van aanvraag. De output is een werkdocument, geen goedgekeurde aanvraag.

## Example

**Request**

Ik heb gisteren een opleiding cybersecurity gevolgd van 1000 euro. Ben ik nog op tijd voor de kmo-portefeuille en hoeveel steun krijg ik als kleine onderneming?

**Result**

Ja, je bent op tijd (deadline: binnen 13 dagen). Als kleine onderneming krijg je 45% subsidie voor cybersecurity. Je betaalt zelf 550 euro en ontvangt 450 euro steun. Let op: stort je eigen aandeel binnen 30 dagen na aanvraag.

## Questions

### Kan ik nog subsidie krijgen voor algemeen bedrijfsadvies?

Alleen cybersecurity advies is nog subsidiabel. Andere adviezen zoals marketing of HR vallen sinds februari 2026 buiten de boot.

### Wat is de deadline voor mijn aanvraag?

De aanvraag moet uiterlijk 14 kalenderdagen na de start van de dienst ingediend zijn. Na 15 dagen vervalt je recht onherroepelijk.

### Helpt deze skill ook bij registratie als dienstverlener?

Ja, de skill helpt dienstverleners bij het voorbereiden van de kwaliteitskamer audit voor een 2- of 5-jarige registratie.

### Hoe snel moet ik de eigen bijdrage storten?

De eigen bijdrage moet binnen 30 kalenderdagen na de aanvraag op de rekening van de kmo-portefeuille staan.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
