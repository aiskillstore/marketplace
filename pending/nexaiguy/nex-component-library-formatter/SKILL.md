---
name: nex-component-library-formatter
description: 'Normalize and validate electronics component library metadata against a strict canonical schema. Use when: Standardize manufacturer and lifecycle strings across large component CSVs; Identify missing required fields like footprints or MPNs in part libraries; Enforce character limits on component descriptions for EDA compatibility.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-component-library-formatter
compatibility: Claude Code, Cursor, Aider, Windsurf, Cline, VS Code
---

# Nex Component Library Formatter

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-component-library-formatter). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Component libraries often suffer from inconsistent naming, missing manufacturer part numbers, and non-standard lifecycle statuses. Manually auditing CSVs for PCB design software is tedious and prone to human error, leading to fabrication delays or procurement issues.

## What it does

- Normalizes component metadata into a canonical schema including footprints, MPNs, and manufacturers.
- Automatically trims whitespace, title-cases manufacturer names, and standardizes lifecycle strings.
- Validates required fields like symbol name and description length to ensure library integrity.
- Generates detailed gap reports identifying exactly which rows and fields are missing data.
- Exports cleaned and formatted CSV files ready for import into EDA tools.

## Frameworks & tools

Python, pytest, and CLI-based CSV processing scripts.

## Why this beats prompting it yourself

General-purpose LLMs struggle with strict schema enforcement across large datasets and often hallucinate "fixes" for part numbers. This skill uses a deterministic validation script paired with an agent to ensure 100% compliance with your specific library standards without manual data entry.

## Use cases

- Cleaning up legacy component libraries before migrating to new EDA software.
- Validating a new batch of parts from a distributor or contractor.
- Standardizing footprint and symbol naming conventions across a hardware team.
- Auditing BOM components for lifecycle status and datasheet links.

## Known limitations

Requires the scripts/validate_library.py file to exist in the environment. Only supports CSV format.

## Example

**Request**

Format my component library at data/parts.csv and fix any lifecycle naming issues.

**Result**

I've processed data/parts.csv.
- Validated 142 rows.
- Normalized 12 manufacturer names to title-case.
- Fixed 5 lifecycle strings (e.g., 'active' to 'Active').
- Reported 3 rows missing required MPNs (Rows: 42, 87, 101).
Cleaned file saved to data/parts_fixed.csv.

## Questions

### What specific data issues does the nex-component-library-formatter resolve?

This skill acts as a rigorous quality gate for electronics metadata, fixing inconsistent naming, standardizing manufacturer names, and validating part numbers to ensure your PCB component libraries are ready for production and procurement.

### Which PCB design tools is this skill compatible with?

The skill exports cleaned CSV files that are pre-formatted for seamless import into industry-standard EDA tools like Altium Designer, KiCad, and Eagle, following your team's specific naming conventions.

### How does this perform better than just asking an AI to clean my CSV?

Unlike standard AI prompts, this skill uses a deterministic Python-based validation engine to ensure 100% schema compliance, preventing the "hallucinated" part numbers or formatting errors common with general-purpose LLMs.

### What exactly is included in the purchase of this skill?

You will receive the core Python processing scripts, the canonical schema definitions, a suite of pytest validation tests, and the agent configuration required to run the formatter in your environment.

### Can I customize the validation rules to fit my company's specific internal standards?

Yes, while it comes with a strict canonical schema, you can adjust the validation rules to match your organization’s specific requirements for symbol naming, footprint libraries, and mandatory metadata fields.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
