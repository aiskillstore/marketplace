---
name: kostprijs-calculator
description: 'Berekent een concept-raming van de totale aankoopkosten van een onroerend goed in Vlaanderen (verkooprecht, ereloon, aktekosten, btw) via een Python-script met bewerkbaar tarievenbestand. Use when: Bereken registratierechten voor verschillende regimes in Vlaanderen; Genereer een transparante kostentabel voor client-communicatie; Update notariele tarieven via een centraal JSON-bestand.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: kostprijs-calculator
compatibility: Compatible with SKILL.md-compatible agents supporting local Python execution.
---

# Kostprijs Calculator

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/kostprijs-calculator). Scripts, extension source, and templates from the original package are not in this folder.

Berekent een concept-raming van de totale aankoopkosten van een onroerend goed in Vlaanderen (verkooprecht, ereloon, aktekosten, btw) via een Python-script met bewerkbaar tarievenbestand. Gebruik deze skill wanneer een notaris(medewerker) vraagt "wat kost deze aankoop", "bereken de notariskosten/registratierechten/aktekosten" of een kostenraming voor een cliënt wil. Inclusief een lokaal Python-script (argparse CLI) dat de agent zelf draait: lokale bestanden in, resultaat eruit. Onderdeel van de Nex AI kantoor-skills reeks voor Belgische professionele kantoren. Geen netwerk, geen API keys, draait volledig lokaal in je agent.

Built by Nex AI. More skills and info at https://nex-ai.be and https://slopsome.com.

## When to use

- Bereken registratierechten voor verschillende regimes in Vlaanderen.
- Genereer een transparante kostentabel voor client-communicatie.
- Update notariele tarieven via een centraal JSON-bestand.
- Schat het totale aankoopbudget inclusief btw en aktekosten.

## Known limitations

- Limited to Flemish Region by default.
- Does not calculate mortgage or credit-related costs.
- Requires local Python 3 environment to run the script.

## Example

**Request**

Bereken de totale kosten voor de aankoop van een woning van 350.000 euro in Vlaanderen onder het 2% regime (enige eigen woning).

**Result**

Raming aankoop 350.000 euro (2% regime):
- Verkooprecht (2%): 7.000,00
- Ereloon: 2.385,00
- Aktekosten: 1.200,00
- BTW (21%): 752,85
Totaal bijkomende kosten: 11.337,85 euro.
Let op: Indicatieve raming, exclusief kredietkosten.

## Questions

### Can I update the tax rates myself?

Yes, all percentages and fixed costs are stored in a local tarieven.json file that you can modify at any time.

### Does it connect to the Belgian tax authorities?

No, this skill calculates a concept estimation based on local files. It does not connect to external APIs or government portals.

### Does it support Brussels or Wallonia?

The default rates are configured for the Flemish Region (Vlaanderen). High-level changes to tarieven.json are required for other regions.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
