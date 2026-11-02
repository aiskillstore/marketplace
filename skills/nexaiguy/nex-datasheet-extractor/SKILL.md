---
name: nex-datasheet-extractor
description: 'Extracts structured electrical specs, package data, and compliance status from component datasheet PDFs. Use when: Convert PDF datasheets into structured JSON or CSV rows; Identify electrical constraints like voltage and temperature ranges; Extract package and pin count data for footprint assignment.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-datasheet-extractor
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Datasheet Extractor

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-datasheet-extractor). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Manually transcribing electrical specifications from PDF datasheets into component libraries is slow and prone to human error. Developers and hardware engineers often waste hours hunting for supply voltages, temperature ranges, and package types across multi-page documents.

## What it does

- Parses PDF text layers to extract primary part numbers and manufacturer names.
- Identifies key electrical parameters including min/max supply voltages and operating temperatures.
- Extracts mechanical data like package strings and pin counts for footprint mapping.
- Checks for RoHS and REACH compliance status within the document text.
- Outputs structured data in JSON or CSV format for direct library ingestion.

## Frameworks & tools

Python, pdfminer.six, pytest.

## Why this beats prompting it yourself

General LLM prompting for PDF extraction often suffers from hallucination of numerical values or inconsistent formatting. This skill uses a specialized script to target specific datasheet patterns, providing a structured output with an extraction confidence score to flag entries needing manual review.

## Use cases

- Populating an ECAD component library (Altium, KiCad) from a batch of PDFs.
- Automating compliance checks for large BOMs by extracting RoHS/REACH status.
- Building a searchable internal database of component electrical characteristics.

## Known limitations

Only works on PDFs with a text layer. Scanned images or tables formatted as images will not be captured. Requires manual verification of electrical parameters before library commitment.

## Example

**Request**

Extract the specs from components/stm32f4.pdf and save it as a CSV row for my library.

**Result**

Extraction complete. Created stm32f4.csv:
part_number: STM32F405RG
manufacturer: STMicroelectronics
package: LQFP64
supply_voltage_min: 1.8
supply_voltage_max: 3.6
operating_temp_min: -40
operating_temp_max: 85
rohs_status: Compliant
confidence: high

## Questions

### How does the nex-datasheet-extractor improve my hardware engineering workflow?

This skill automates the tedious task of transcribing electrical specs, package data, and compliance status from PDF datasheets into structured formats like JSON or CSV, significantly reducing human error and manual labor.

### Can this skill extract data from scanned datasheets or images?

It is designed to work with PDFs that have a text layer; however, it cannot extract data from scanned images or tables rendered as images.

### How does the tool handle potential inaccuracies in the extracted data?

The skill provides a structured output accompanied by a confidence score, allowing you to quickly identify and manually verify entries that may require a second look before final library ingestion.

### What exactly is included in the purchase of this skill?

You will receive the specialized Python-based extraction scripts, a suite of pytest files for validation, and documentation on how to integrate the output into ECAD tools like Altium or KiCad.

### Which AI agents or environments are compatible with this extractor?

The skill is highly compatible with any Python-based environment and can be integrated as a custom tool for AI agents that support script execution and file processing.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
