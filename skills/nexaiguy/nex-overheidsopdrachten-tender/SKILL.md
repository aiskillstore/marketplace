---
name: nex-overheidsopdrachten-tender
description: 'Analyseert een Belgisch bestek en levert een go of no-go met knock-outs, gunningscriteria, weging en drempelbedragen. Use when: Voer een snelle go of no-go analyse uit per bestek; Genereer een technisch offerteskelet op maat van criteria; Vul het UEA of ESPD formulier correct in voor kmo''s.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-overheidsopdrachten-tender
compatibility: Compatible with SKILL.md-compatible agents
---

# Nex Overheidsopdrachten Tender

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-overheidsopdrachten-tender). Scripts, extension source, and templates from the original package are not in this folder.

## Wat het doet

- Haalt de knock-outcriteria uit het bestek en zegt meteen of je uberhaupt mag meedoen.
- Zet de gunningscriteria met hun weging op een rij en berekent waar je punten kan winnen.
- Toetst de raming aan de Europese en nationale drempelbedragen en de bijhorende procedure.
- Levert een gestructureerde go of no-go-analyse die je in het dossier kan steken.

## Toepassingen

- Snel beslissen of een overheidsopdracht de moeite is
- De offerte richten op de criteria die het zwaarst wegen
- Uitsluitingsgronden en selectiecriteria nakijken voor je begint te schrijven
- Een dossier voorbereiden voor je jurist of aankoper

## Beperkingen

Belgische en Europese aanbestedingsregels, niet die van andere landen. De output is een werkdocument en geen juridisch advies, en de finale beoordeling blijft bij de aanbestedende overheid.

## Known limitations

- Enkel voor Belgische wetgeving (2016/2017).
- Geen juridisch advies maar een werkdocument.
- Geen ondersteuning voor speciale sectoren (water, energie).

## Example

**Request**

Analyseer dit bestek voor een nieuwe kantoorinrichting in Brussel en geef een go/no-go advies op basis van de knock-outs en gunningscriteria.

**Result**

**Analyse Resultaat**
- **Go/No-Go:** GO (beperkte concurrentie, match met expertise).
- **Knock-outs:** Erkenning klasse 3 vereist (u voldoet), 3 referenties nodig.
- **Gunningscriteria:** Prijs (50%), Plan van Aanpak (30%), Duurzaamheid (20%).
- **Advies:** Focus op het Plan van Aanpak voor maximale score.

## Questions

### Welke wetgeving wordt gehanteerd?

De skill volgt de wet van 17 juni 2016 en het KB plaatsing van 18 april 2017 voor de klassieke sectoren.

### Zijn de drempelbedragen up-to-date?

Ja, de skill bevat de geactualiseerde Europese drempels voor de periode 2026-2027.

### Werkt dit ook voor buitenlandse tenders?

Nee, de skill ondersteunt enkel de Belgische federale en regionale wetgeving via e-Procurement.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
