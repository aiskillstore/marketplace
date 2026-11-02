---
name: nex-bom-normalizer
description: 'Standardize, deduplicate, and clean messy Bill of Materials (BOM) files into procurement-ready CSVs. Use when: Deduplicate component lists by merging matching MPNs and Manufacturers; Convert messy EDA exports into a canonical column format for procurement; Automatically fix and uppercase inconsistent reference designators.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-bom-normalizer
compatibility: Claude Code, Aider, Cursor, Windsurf, Cline, VS Code
---

# Nex BOM Normalizer

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-bom-normalizer). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Engineering and procurement teams waste hours manually cleaning inconsistent BOMs exported from different EDA tools. Messy reference designators, duplicate part entries, and non-standard column headers cause ordering errors and assembly delays.

## What it does

- Standardizes inconsistent column headers into a canonical set (RefDes, Qty, MPN, Manufacturer, etc.).
- Deduplicates parts by merging rows based on Manufacturer Part Number and Manufacturer name.
- Normalizes reference designators into comma-separated, uppercase strings.
- Calculates and updates total quantities automatically during the merge process.
- Flags rows with missing required fields (MPN, Qty, Manufacturer) into a separate CSV for manual review.

## Frameworks & tools

Python-based CLI tool (scripts/normalize.py). Works with CSV and XLSX input files.

## Why this beats prompting it yourself

A generic LLM prompt often misses edge cases in part deduplication or fails to maintain strict column ordering. This skill uses a dedicated Python script to ensure 100% data integrity, providing a repeatable process with a detailed audit log of every fix applied.

## Use cases

- Cleaning messy exports from Altium, KiCad, or Eagle for procurement.
- Merging multiple partial BOMs into a single master component list.
- Preparing parts lists for pick-and-place machine programming.
- Identifying missing part data before sending a quote request to a CM.

## Known limitations

Does not perform external API lookups for pricing or stock. Data normalization is strictly local based on the provided input file.

## Example

**Request**

Clean up this messy parts list in source_bom.xlsx and give me a standardized CSV for the assembly house.

**Result**

I've normalized source_bom.xlsx.
- Merged 4 duplicate rows.
- Standardized columns to RefDes, Qty, MPN, Manufacturer.
- 2 rows flagged for missing MPNs in source_bom_flagged.csv.
Cleaned file: source_bom_normalized.csv.

## Questions

### How does this skill help with hardware procurement workflows?

This skill automates the cleaning of messy Bill of Materials (BOM) files, standardizing headers, deduplicating parts based on MPN, and formatting reference designators to ensure your data is ready for procurement or PCB assembly.

### What file formats and EDA tools are compatible with the nex-bom-normalizer?

The tool supports both CSV and XLSX file formats, and it is designed to work with exports from popular EDA tools like Altium, KiCad, and Eagle.

### What is included in the download package?

Your purchase includes the Python-based CLI tool (normalize.py), a detailed README for setup, and example input/output files to help you get started immediately.

### Does the skill notify me if there are missing part numbers or incomplete data?

Yes, the skill automatically identifies rows missing critical data like MPN or Quantity and exports them into a separate CSV file so you can quickly review and fix errors.

### Why should I use this skill instead of just prompting a standard AI model to clean my CSV?

Unlike a generic LLM prompt that may hallucinate or skip lines, this skill uses a deterministic Python script to ensure 100% data integrity and provide a clear audit log of every change made.

### Can this skill check for live stock levels or component pricing?

The nex-bom-normalizer operates strictly locally on your input files; it does not connect to external APIs for real-time pricing or component availability lookups.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
