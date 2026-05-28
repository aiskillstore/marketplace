---
name: meta-baseline-generator
description: Generates a meta-analysis baseline characteristics section (text + table) from raw data. Supports Chinese and English. Use when the user provides baseline data and wants a formatted results section.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta-Analysis Baseline Generator

This skill generates a standardized "Baseline Characteristics" section for meta-analysis papers, including a descriptive text summary and a formatted Markdown table.

## When to Use

- Use this skill when you need generates a meta-analysis baseline characteristics section (text + table) from raw data. supports chinese and english. use when the user provides baseline data and wants a formatted results section in a reproducible workflow.
- Use this skill when a academic writing task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/text_processor.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-baseline-generator` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates a meta-analysis baseline characteristics section (text + table) from raw data. Supports Chinese and English. Use when the user provides baseline data and wants a formatted results section.
- Packaged executable path(s): `scripts/text_processor.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Academic Writing/meta-baseline-generator"
python -m py_compile scripts/text_processor.py
python scripts/text_processor.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/text_processor.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/text_processor.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

1.  **Gather Inputs**: Ensure you have the following from the user:
    *   `title`: The title of the meta-analysis.
    *   `baseline_information`: The raw baseline data (JSON, text, etc.).
    *   `language`: The target output language ("Chinese" or "English").

2.  **Generate Text Description (LLM)**:
    *   Use the "Text Description Generation" prompt in [references/prompts.md](references/prompts.md).
    *   Input: `title`, `baseline_information`, `language`.
    *   Output: A paragraph describing the study characteristics.

3.  **Generate Markdown Table (LLM)**:
    *   Use the "Markdown Table Generation" prompt in [references/prompts.md](references/prompts.md).
    *   Input: `baseline_information`, `language`.
    *   Output: A Markdown table wrapped in curly braces (e.g., `{ | Table | }`).

4.  **Process and Combine (Script)**:
    *   Run `scripts/text_processor.py` to format the final output.
    *   The script performs the following deterministic operations:
        *   Inserts `(Table 1)` before the last punctuation of the text description.
        *   Cleans markdown code fences from the table output.
        *   Adds the standard table title and headers.
    *   **Execution**:
        ```python
        import sys
        sys.path.append('scripts')
        from text_processor import process_content
        
        final_result = process_content(
            text_description=step2_output, 
            raw_table=step3_output, 
            language=language
        )
        print(final_result)
        ```

5.  **Output**: Present the `final_result` to the user.

## Rules

*   **Language Consistency**: Ensure the output language strictly matches the user's request (Chinese/English).
*   **Citation Insertion**: The citation `(Table 1) MUST be inserted *before* the final punctuation of the description text.
*   **Table Format**: The table must be a standard Markdown table with a clear title.

## Testing Guidelines

When testing this skill:

1. **Verify UTF-8 encoding**: Ensure the output displays Chinese characters correctly (e.g., `【Results】` not `��Results��`).
2. **Check citation placement**: The citation tag should appear immediately before the final punctuation mark.
3. **Test edge cases**:
   - Empty or missing baseline fields (marked as "-" in table)
   - Special characters in study names (e.g., umlauts: Lübbert → Luebbert)
   - Various punctuation marks (. ! ? 。！？)
4. **Validate table structure**: Ensure markdown table has proper column alignment (`|:---|`).
