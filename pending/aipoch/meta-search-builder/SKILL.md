---
name: meta-search-builder
description: Medical literature search strategy generator. Given a user's natural-language description (e.g., meta-analysis topic, PICOS elements, research question), automatically extract medical entities (disease, intervention, population, outcomes) and generate professional search queries for seven major databases (PubMed, Cochrane, Embase, Web of Science, CNKI, Wanfang, VIP). Useful for developing search strategies for systematic reviews and meta-analyses.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Medical Literature Search Strategy Generator

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Medical literature search strategy generator. Given a user's natural-language description (e.g., meta-analysis topic, PICOS elements, research question), automatically extract medical entities (disease, intervention, population, outcomes) and generate professional search queries for seven major databases (PubMed, Cochrane, Embase, Web of Science, CNKI, Wanfang, VIP). Useful for developing search strategies for systematic reviews and meta-analyses.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Others/meta-search-builder
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

### Step 1: Entity extraction

Extract PICOS elements from the user's input:

1. **P (Population)**: target population / disease
2. **I (Intervention)**: intervention
3. **C (Comparator)**: comparator (optional)
4. **O (Outcome)**: outcome measures (optional)
5. **S (Study)**: study type (default: RCT)

Extraction rules:
- Limit the number of keywords to at most 5
- Simplify descriptive phrases (e.g., "patients with ovarian cancer" -> "ovarian cancer")
- Map non-standard terms to common medical terminology 
- Use standardized outcome terms where appropriate

### Step 2: Generate search strategies for seven databases

See [references/databases.md](references/databases.md) for database-specific syntax and examples.

#### Output format

```

## Extracted medical entities

- P (Population/Disease): xxx
- I (Intervention): xxx
- C (Comparator): xxx
- O (Outcome): xxx
- S (Study type): xxx

## Search strategies

### 1. PubMed
[search query]

### 2. Cochrane Library
[search query]

### 3. Embase
[search query]

### 4. Web of Science
[search query]

### 5. CNKI (China National Knowledge Infrastructure)
[search query]

### 6. Wanfang
[search query]

### 7. VIP
[search query]
```

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
- If a file is produced, prefer a deterministic output name such as `meta_search_builder_result.md` unless the skill documentation defines a better convention.
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
Result file: meta_search_builder_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
