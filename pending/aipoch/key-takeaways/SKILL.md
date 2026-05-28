---
name: key-takeaways
description: Extracts and summarizes key takeaways from documents, meeting notes, articles, and other text content. Use when the user asks for summaries, bullet points, main points, highlights, or a TL;DR of any document or body of text. Produces structured outputs such as numbered lists, executive summaries, and action items. Supports configurable output formats including JSON export for downstream use.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Key Takeaways

Extracts and presents the most important points from any body of text — meeting notes, articles, reports, or documents — as concise, structured takeaways. Supports multiple output formats and is configurable for audience or depth.

## When to Use

- Use this skill when the task needs Extracts and summarizes key takeaways from documents, meeting notes, articles, and other text content. Use when the user asks for summaries, bullet points, main points, highlights, or a TL;DR of any document or body of text. Produces structured outputs such as numbered lists, executive summaries, and action items. Supports configurable output formats including JSON export for downstream use.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Extracts and summarizes key takeaways from documents, meeting notes, articles, and other text content. Use when the user asks for summaries, bullet points, main points, highlights, or a TL;DR of any document or body of text. Produces structured outputs such as numbered lists, executive summaries, and action items. Supports configurable output formats including JSON export for downstream use.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/key-takeaways"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.main import Key_Takeaways

# Initialize
tool = Key_Takeaways()

# Extract key takeaways from a document
result = tool.process("meeting_notes.txt")

# Export as structured JSON
tool.export(result, format="json")
```

## Core Capabilities

### 1. Extract key points from text

```python

# Read source document and extract top takeaways
result = tool.process("quarterly_report.txt")

# Returns: [{"point": "Revenue grew 12% YoY", "source_line": 4}, ...]
```

### 2. Generate structured summaries

```python

# Generate a bullet-point executive summary
result = tool.process("meeting_notes.txt", style="executive")

# Returns: {"summary": "...", "action_items": [...], "decisions": [...]}
```

### 3. Configure output depth and audience

```python

# Adjust number of takeaways and target audience
result = tool.process("article.txt", max_points=5, audience="non-technical")
```

### 4. Export results

```python

# Export takeaways to JSON or plain text
tool.export(result, format="json", output_path="takeaways.json")
tool.export(result, format="txt",  output_path="takeaways.txt")
```

## CLI Usage

```text

# Extract key takeaways from a file
python scripts/main.py --input document.txt --output takeaways.txt

# Use a config file to set depth, audience, and format
python scripts/main.py --input document.txt --config config.json --verbose

# Batch process a directory of documents
python scripts/main.py --batch input_dir/ --output output_dir/
```

**Batch processing notes:**
- Verify the output directory exists before running: `mkdir -p output_dir/`
- If processing fails on an individual file, the tool logs the error and continues with remaining files; review `output_dir/errors.log` after the run
- After batch completion, validate all JSON outputs: `for f in output_dir/*.json; do python -m json.tool "$f" > /dev/null && echo "OK: $f" || echo "FAIL: $f"; done`

## Example Input / Output

**Input** (`meeting_notes.txt`):
```
Q3 review: Sales up 15%. New product launch delayed to Q4.
Action: Alice to update roadmap by Friday. Budget approved for hiring.
```

**Output** (`takeaways.json`):
```json
{
  "key_points": [
    "Sales increased 15% in Q3",
    "Product launch rescheduled to Q4"
  ],
  "action_items": [
    "Alice to update roadmap by Friday"
  ],
  "decisions": [
    "Budget approved for hiring"
  ]
}
```

## Quality Checklist

- [ ] Source text is readable and complete before processing
- [ ] Output point count matches configured `max_points` setting
- [ ] Action items and decisions are separated from general observations
- [ ] Exported file opens and validates correctly (e.g., `python -m json.tool takeaways.json`)
  - If JSON validation fails, check source file encoding (UTF-8 expected) and re-run; inspect `--verbose` output for parsing errors
- [ ] Results reviewed against original source for accuracy

## References

- `references/guide.md` - Detailed documentation
- `references/examples/` - Sample inputs and outputs

---

**Skill ID**: 308 | **Version**: 1.0 | **License**: MIT

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `key-takeaways` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `key-takeaways` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
