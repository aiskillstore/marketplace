---
name: soft-article-writer
description: Generates high-quality promotional soft articles with structured outlines, tailored introductions, and optimized titles based on product info and hot topics. Use when you need to write promotional content, "soft articles" (), or marketing copy that integrates product highlights with current trends, news, or industry insights.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates high-quality promotional soft articles with structured outlines, tailored introductions, and optimized titles based on product info and hot topics. Use when you need to write promotional content, "soft articles" (), or marketing copy that integrates product highlights with current trends, news, or industry insights.
- Packaged executable path(s): `scripts/outline_utils.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/soft-article-writer"
python -m py_compile scripts/outline_utils.py
python scripts/outline_utils.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/outline_utils.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/outline_utils.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/outline_utils.py --help
```

# Soft Article Writer

This skill orchestrates the creation of a promotional "soft article" (). It takes product details and marketing materials (hotspots, news, insights) as input, generates a structured outline, writes tailored sections (Introduction, Body, Conclusion), and optimizes titles.

## Inputs

The user should provide the following information (or the skill should prompt for it):

1.  **Product (`product`)**: Description of the product to be promoted. (Required)
2.  **Highlights (`highlights`)**: Key selling points or highlights of the product. (Required)
3.  **Material Type (`type`)**: The combination of materials provided.
    *   `1`: Hotspot + Insights
    *   `2`: News + Insights
    *   `3`: Single Material (Hotspot / News / Insights)
4.  **Materials**:
    *   `topics`: Hotspot content (if applicable).
    *   `news`: News content (if applicable).
    *   `insights`: Industry insights/Dry goods (if applicable).
5.  **Optional**:
    *   `theme`: Specific theme for the article.
    *   `style`: Writing style (e.g., professional, humorous).
    *   `structure`: Specific structure requirements.

## Workflow

### 1. Generate Outline
Generate a structured outline based on the inputs. The outline must explicitly contain "Introduction" (), "Body" (), and "Conclusion" () sections marked with bold headers (e.g., ****).

### 2. Extract Outline Sections
Use the `scripts/outline_utils.py` script to parse the generated outline text and extract the specific guidance for Introduction, Body, and Conclusion.

```bash
python scripts/outline_utils.py --text "<generated_outline_text>"
```

The script returns a JSON object with `introduction`, `body`, and `conclusion` fields.

### 3. Generate Introduction
Generate the Introduction section. The content must be tailored based on the `type` input:
*   **Type 1 (Hotspot + Insights)**: Integrate `topics` and `insights`.
*   **Type 2 (News + Insights)**: Integrate `news` and `insights`.
*   **Type 3 (Single)**: Integrate the available material (`topics`, `news`, or `insights`).

**Constraints**:
*   Must align with `theme` and `style`.
*   Must naturally lead into the product without being too salesy.
*   Length: 300-500 words.

### 4. Generate Body
Generate the Body section using:
*   `product` and `highlights`.
*   The `body` outline extracted in Step 2.
*   The generated Introduction (for context).

**Constraints**:
*   Word count: 800-1500 words.
*   Must cover product highlights.

### 5. Generate Conclusion
Generate the Conclusion section using:
*   The `conclusion` outline extracted in Step 2.
*   All previous context.

**Constraints**:
*   Length: 150-250 words.
*   Must include a Call to Action (CTA).

### 6. Generate and Select Titles
1.  Generate 6-10 candidate titles (under 40 words, avoiding hard ad-speak).
2.  Select the top 3 best titles based on attractiveness and relevance.

### 7. Final Output
Present the final article in Markdown format:

```markdown

# [Selected Title]

## Introduction
[Introduction Content]

## Body
[Body Content]

## Conclusion
[Conclusion Content]
```

## Quality Rules

*   **No Hard Selling**: Avoid aggressive sales language. Use third-party endorsements or "planting grass" () style.
*   **Consistency**: Ensure the tone matches the requested `style`.
*   **Factuality**: Do not invent fake data or citations.

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
- If a file is produced, prefer a deterministic output name such as `soft_article_writer_result.md` unless the skill documentation defines a better convention.
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
python scripts/outline_utils.py --help
```

Expected output format:

```text
Result file: soft_article_writer_result.md
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
