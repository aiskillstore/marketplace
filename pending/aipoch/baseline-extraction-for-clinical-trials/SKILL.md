---
name: baseline-extraction-for-clinical-trials
description: Extracts clinical trial baseline data (study, region, participants, etc.) from article text or PMID. Checks PubMed for metadata; always falls back to LLM extraction for full details.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Baseline Extraction (RCT)

This skill extracts 10 key baseline characteristics from clinical trial articles. It implements a hybrid workflow:
1.  **PubMed Lookup**: Checks PubMed API using the PMID to verify existence and get basic metadata.
2.  **LLM Extraction**: Analyzes the article text to extract detailed baseline data (since PubMed metadata is limited).

## When to Use

- Use this skill when you need extracts clinical trial baseline data (study, region, participants, etc.) from article text or pmid. checks pubmed for metadata; always falls back to llm extraction for full details in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `baseline-extraction for clinical trials` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Extracts clinical trial baseline data (study, region, participants, etc.) from article text or PMID. Checks PubMed for metadata; always falls back to LLM extraction for full details.
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/baseline-extraction-for-clinical-trials"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

### Step 1: Check PubMed (Deterministic)

If the user provides a PMID, use the `baseline_extractor.py` script to check PubMed.

```python
import subprocess
import json

# Replace <PMID> with actual PMID
result = subprocess.run(["python", "scripts/baseline_extractor.py", "<PMID>"], capture_output=True, text=True)
print(result.stdout)
```

**Analyze the Script Output:**
*   If `status` is `"success"`: **Stop here.** Return the `data` JSON to the user.
*   If `status` is `"not_found"`, `"incomplete"`, or `"error"` (or if no PMID was provided): Proceed to Step 2.

### Step 2: LLM Extraction (Fallback)

If Step 1 did not yield a complete result, use the LLM to extract the information from the **full article text**.

**Input:**
*   Full article text provided by the user.

**Instructions:**
1.  Read the [Extraction Schema](references/extraction_schema.md) carefully.
2.  Analyze the text to identify all 10 required fields.
3.  Ensure the output is strictly in the JSON format defined in the schema.
4.  **Constraint**: Do not hallucinate. If a field is not mentioned in the text, set it to `null` or an empty string.

## Output

Return the final result as a Markdown code block containing the JSON object.

```json
{
  "study": "...",
  "region": "...",
  ...
}
```

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:
