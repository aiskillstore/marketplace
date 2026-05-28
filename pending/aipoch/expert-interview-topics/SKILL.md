---
name: expert-interview-topics
description: "Generates professional interview titles and questions based on expert background and topic. Provides a structured workflow for interview preparation."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generates professional interview titles and questions based on expert background and topic. Provides a structured workflow for interview preparation.".
- Packaged executable path(s): `scripts/main.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Others/expert-interview-topics"
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
- Primary implementation surface: `scripts/main.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Expert Interview Topics

This skill provides a professional workflow to generate interview titles and questions based on an expert's background and a discussion topic. It encapsulates the logic for title ideation, selection, and in-depth question formulation.

**Note**: This skill outputs the structured reasoning process and prompts, allowing users to execute the generation steps with their preferred Large Language Model (LLM).

## Usage

Run the Python script in the `scripts` directory.

### Command

```bash
python scripts/main.py --topic "<topic>" --background "<expert_background>" [--file "<path_to_transcript>"]
```

### Arguments

- `--topic`: The main topic or direction of the interview.
- `--background`: Detailed background information of the expert (Name, Unit, Research direction, Achievements, etc.).
- `--file` (Optional): Path to an existing interview transcript file (txt, md, etc.).

## Output

The script outputs three prompt templates corresponding to the workflow steps:

1.  **Title Generation Prompt**: Ready to use.
2.  **Title Selection Prompt**: Contains a placeholder `{generated_titles}` to be filled with the result from Step 1.
3.  **Question Generation Prompt**: Contains a placeholder `{selected_title}` to be filled with the result from Step 2.

## Example

```bash
python scripts/main.py --topic "AI in Healthcare" --background "Dr. Smith, Chief Scientist at HealthAI"
```

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
- If a file is produced, prefer a deterministic output name such as `expert_interview_topics_result.md` unless the skill documentation defines a better convention.
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
Result file: expert_interview_topics_result.md
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
