---
name: clinic-research-design
description: Generates a structured prompt framework for clinical study protocols. Supports Diagnostic, Efficacy, Etiology, and Prognosis studies. Calculates sample size and provides logic guides for LLMs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates a structured prompt framework for clinical study protocols. Supports Diagnostic, Efficacy, Etiology, and Prognosis studies. Calculates sample size and provides logic guides for LLMs.
- Packaged executable path(s): `scripts/calculators/sample_size.py` plus 4 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Protocol Design/clinic-research-design"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/calculators/sample_size.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/main.py --help
```

# Clinic Research Design (Agentic Version)

This skill serves as a **Logic & Structure Engine** for AI Agents. Instead of outputting a finished text document, it generates a **Structured Prompt / Writing Guide**.

An Agent (like a specialized medical writer bot) should call this skill to get the "Skeleton" and "Logic", and then use its own LLM capabilities to "Flesh out" the content based on the detailed instructions provided in the output.

## Capabilities

1.  **Logic Structuring**: Automatically selects the correct protocol template (e.g., STARD for diagnostics, SPIRIT for trials) based on input.
2.  **Calculation**: Performs deterministic sample size calculations (which LLMs are bad at).
3.  **Prompt Engineering**: Generates context-aware instructions for each section (Introduction, Methods, Stats) tailored to the specific P/I/C/O.

## Usage for Agents

When an Agent receives a request like "Write a protocol for a diabetes drug trial", it should:

1.  **Call this skill**:
    ```bash
    python scripts/main.py --type efficacy --P "Type 2 Diabetes" --I "Metformin" --C "Placebo" --O "HbA1c" --study_design "RCT"
    ```
2.  **Read the Output**: The output file (e.g., `output/protocol.md`) will contain sections like:
    > **[LLM Instruction]**: Write a 3-4 paragraph introduction. Discuss gaps in understanding risk factors for...
3.  **Execute Instructions**: The Agent should then read these instructions and generate the final, polished content for the user.

## Arguments

*   `--type`: `diagnostic`, `efficacy`, `etiology`, `prognosis`
*   `--P`, `--I`, `--C`, `--O`: PICO elements.
*   `--study_design`: Specific design (e.g., `RCT`, `cohort`).
*   `--sensitivity`, `--specificity`, `--alpha`, `--power`: Statistical parameters.

## Output Format

The output is a Markdown file containing:
*   **Headers**: Standard protocol sections.
*   **Blockquotes**: `> [LLM Instruction]: ...` specific guidance for the LLM on *what* to write and *how* to write it for that specific section.
*   **Hard Data**: Pre-calculated values (Sample Size) that the LLM must strictly follow.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `clinic_research_design_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/main.py --help
```

Expected output format:

```text
Result file: clinic_research_design_result.md
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
