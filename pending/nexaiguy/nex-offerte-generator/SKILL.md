---
name: nex-offerte-generator
description: 'Generate high-converting, Belgian-compliant Dutch commercial proposals for SME prospects. Use when: Convert a demo conversation into a professional Belgian Dutch proposal; Calculate 21% BTW and 30-day payment terms automatically for SME clients; Generate print-ready PDF proposals with outcome-oriented scope bullets.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nex-offerte-generator
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and Cursor.
---

# Nex Offerte Generator

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-offerte-generator). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

This skill automates the creation of high-converting, Belgian-style commercial proposals (offertes) specifically for the SME market. It converts your project brief or demo notes into a professional, Dutch-language document that follows local business customs and legal requirements.

## Why use this skill

Writing proposals is a bottleneck for many developers and agency owners. This skill doesn't just generate text; it applies a proven "closing logic" derived from real-world Belgian agency proposals that achieve 70-90% win rates. It handles the structural nuances that matter to Belgian clients—such as correct BTW (VAT) 21% calculations, KBO/BTW-nummer formatting, 30-day payment terms, and 14-day validity periods—ensuring you look like a pro without manual formatting.

## Supported output

- **offerte.md:** The canonical markdown proposal.
- **offerte.html:** A print-ready, styled HTML page (A4 format).
- **offerte.pdf:** Rendered via Pandoc/wkhtmltopdf for direct shipment.
- **Detailed Scope:** Outcome-oriented bullet points instead of technical feature lists.

## The Belgian Doctrine

The output is optimized for SME decision-makers: it focuses on "Investment" rather than "Cost," limits line items to prevent choice paralysis, and includes a clear signature block instead of an open-ended question. It turns your "proposal" into a "ready-to-sign" contract.

Built by Nex AI. More skills and info at [nex-ai.be](https://nex-ai.be) and [slopsome.com](https://slopsome.com).

## When to use

- Convert a demo conversation into a professional Belgian Dutch proposal.
- Calculate 21% BTW and 30-day payment terms automatically for SME clients.
- Generate print-ready PDF proposals with outcome-oriented scope bullets.
- Apply Belgian-specific business logic to move prospects from demo to signature.

## Known limitations

- Requires manual input of local KBO/BTW numbers.
- PDF generation depends on external tools like Pandoc.
- Optimized for Belgian law, not for Dutch (NL) or French (FR) law.

## Example

**Request**

Demo done for 'De Bistro X'. Website design €2900, hosting €45/mo. Client: Jean Dupont. Address: Markt 1, 1000 Brussel. Include the demo link https://demo.nex-ai.be/bistro-x.

**Result**

# Offerte 2024-042
De Bistro X, 21 mei 2024, geldig tot 4 juni 2024

Beste Jean Dupont,
Uw demo staat klaar op https://demo.nex-ai.be/bistro-x. De link blijft live tot ondertekening.

Investering:
Eenmalig: 2900 EUR
Maandelijks: 45 EUR
Subtotaal: 2945 EUR ex BTW
BTW 21%: 618 EUR
Totaal: 3563 EUR incl BTW

## Questions

### What specific problem does the nex-offerte-generator-be solve for agency owners?

This skill automates the creation of Dutch commercial proposals for the Belgian SME market, ensuring they meet local legal requirements (like KBO/VAT formatting) and follow a high-conversion sales structure.

### In what formats can I download the generated proposals?

The skill generates three specific file formats: a Markdown file for easy editing, a styled HTML page for web viewing, and a print-ready PDF formatted for A4 standards.

### Does the generator automatically include Belgian VAT and common payment terms?

Yes, the skill is designed to handle Belgian-specific business logic, including 21% VAT calculations, 30-day payment terms, and 14-day validity periods out of the box.

### What exactly is included in the purchase of this skill?

You receive the full skill package, including the logic for Markdown, HTML, and PDF rendering, plus a template optimized for 'The Belgian Doctrine' of high-win-rate sales.

### Which AI agents is this skill compatible with?

The skill is compatible with most modern LLM-based agents that support document generation and output manipulation; it requires your agent to have access to standard rendering tools for the PDF output.

### Is the language output limited to formal Dutch, or does it account for Belgian business culture?

The content is specifically optimized for Dutch-speaking Belgian SMEs (Vlaanderen/Brussels), focusing on regional business etiquette and 'investering' (investment) terminology favored by local decision-makers.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
