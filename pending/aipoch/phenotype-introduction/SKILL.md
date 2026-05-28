---
name: phenotype-introduction
description: "Expert system for generating comprehensive biomedical phenotype introductions with structured academic content. Use when users request detailed explanations of cellular phenotypes including concept, mechanism, regulation, and detection methods in Chinese academic writing."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Phenotype Introduction

## When to Use

- Use this skill when you need "expert system for generating comprehensive biomedical phenotype introductions with structured academic content. use when users request detailed explanations of cellular phenotypes including concept, mechanism, regulation, and detection methods in chinese academic writing." in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/example.py` is the most direct path to complete the request.
- Use this skill when you need the `phenotype-introduction` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: "Expert system for generating comprehensive biomedical phenotype introductions with structured academic content. Use when users request detailed explanations of cellular phenotypes including concept, mechanism, regulation, and detection methods in Chinese academic writing.".
- Packaged executable path(s): `scripts/example.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/example_asset.txt`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/phenotype-introduction"
python -m py_compile scripts/example.py
python scripts/example.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/example.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Overview` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/example.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Packaged assets: reusable files are available under `assets/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Overview

This skill generates detailed academic introductions for biomedical phenotypes with strict content requirements and word count constraints.
It produces structured academic content with four mandatory sections:

1. Concept
2. Mechanism and occurrence process
3. Regulation
4. Marker detection methods

---

## Quick Start

When a user requests a phenotype introduction:

1. Parse the phenotype name from the user query.
2. Generate **Concept section** (≥800 words) including definition, biological characteristics, cellular functions, and historical background.
3. Generate **Mechanism section** (≥800 words) describing occurrence process, cellular impacts, and key molecular components.
4. Generate **Regulation section** (≥800 words) covering regulatory principles, molecular pathways, and phenotype crosstalk.
5. Generate **Marker Detection section** (≥500 words) listing ≥5 key markers with detection principles and methods.
6. Format output using strict academic structure.

---

## Content Requirements

### 1. Concept Section (≥800 words)

Include:

* Detailed phenotype definition
* Biological characteristics
* Cellular-level functions and roles
* Historical development and background

---

### 2. Mechanism Section (≥800 words)

Include:

* How the phenotype occurs
* Cellular impacts and downstream effects
* Key molecular components
* Step-by-step occurrence description

---

### 3. Regulation Section (≥800 words)

Include:

* Regulatory principles
* Participating molecules and signaling pathways
* Crosstalk with other phenotypes
* Nested or hierarchical relationships

---

### 4. Marker Detection Section (≥500 words, ≥5 markers)

Include:

* List of key marker molecules
* Detection rationale for each marker
* Common detection methods

---

## Output Format

Strict academic structure:

```
1. Concept

[Content ≥800 words]

2. Mechanism and Occurrence Process

[Content ≥800 words]

3. Regulation

Regulation: [Regulatory content]

Phenotype Crosstalk: [Crosstalk content]

4. Markers and Detection Methods

Molecule: [Marker name]; Principle: [Detection principle]; Methods: [Detection method]

Molecule: [Marker name]; Principle: [Detection principle]; Methods: [Detection method]

[Repeat for ≥5 markers]
```

---

## Quality Control

All outputs must pass validation for:

* Word count per section
* Minimum 5 marker molecules
* Proper academic terminology
* Complete section coverage
* Logical scientific consistency
