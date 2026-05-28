---
name: pathway-introduction-expert
description: Generates comprehensive academic introductions for biological pathways, including signaling processes, markers, and inhibitors. Use when the user asks to introduce a pathway, molecule, or gene.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates comprehensive academic introductions for biological pathways, including signaling processes, markers, and inhibitors. Use when the user asks to introduce a pathway, molecule, or gene.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/pathway-introduction-expert"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Pathway Introduction Expert

## Workflow

1.  **Analyze the Request**: Identify if the user is asking about a specific **Pathway**, **Molecule**, or **Gene**.
2.  **Generate Report**:
    *   Follow the **Content Requirements** and **Output Format** below strictly.
    *   If the input is a **Molecule/Gene**, list 5 related pathways first, then choose the most relevant one to introduce.
    *   If the input is a **Pathway**, introduce it directly.

## Content Requirements

### 1. General Introduction
*   **Focus**: Protein interactions and signaling processes.
*   **Length**: **No less than 500 words**.
*   **Logic**:
    *   **Pathway Input**: Introduce directly.
    *   **Molecule/Gene Input**: List 5 related pathways, then CHOOSE 1 most relevant pathway to introduce.

### 2. Markers and Key Genes
*   List all markers and key genes.
*   Provide brief introductions for each.
*   **Crucial**: Describe their **detection forms**.

### 3. Agonists and Inhibitors
*   List all known agonists.
*   List all known inhibitors.

## Output Format (Strict)

You MUST answer in **Chinese**. Translate the following structure and headers into Chinese for the final output:

```text
I. Pathway Introduction
(Content...)

II. Markers and Key Genes
1. Molecule Name; Introduction; Detection Form
2. Molecule Name; Introduction; Detection Form
...
n. Molecule Name; Introduction; Detection Form

III. Agonists and Inhibitors
1. Agonists:
   a.
   b.
   ...
2. Inhibitors:
   a.
   b.
   ...
```

## Example (Structure Reference)

**I. Pathway Introduction:**
The MAPK (Mitogen-Activated Protein Kinase) pathway is a signaling pathway widely present in cells... (Content continues)...

**II. Markers:**
a) ERK1/2 pathway: Ras, Raf...
Name    Detection Form
ERK1/2  Phosphorylation
...

**III. Agonists and Inhibitors**
1. Agonists:
   a) Growth factors...
2. Inhibitors:
   a) ERK1/2 pathway inhibitors: U0126...

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `pathway_introduction_expert_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: pathway_introduction_expert_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
