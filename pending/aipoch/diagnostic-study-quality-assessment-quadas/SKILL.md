---
name: diagnostic-study-quality-assessment-quadas
description: "Analyzes clinical diagnostic accuracy studies for bias using the QUADAS-2 tool. Use when Claude needs to assess the quality, risk of bias, or applicability of diagnostic accuracy studies (e.g., \"Assess this paper using QUADAS-2\")."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Clinical Study Bias Assessment (QUADAS-2)

This skill evaluates clinical diagnostic accuracy studies for bias and applicability concerns using the Quality Assessment of Diagnostic Accuracy Studies-2 (QUADAS-2) tool.

## When to Use

- Use this skill when you need analyzes clinical diagnostic accuracy studies for bias using the quadas-2 tool. use when claude needs to assess the quality, risk of bias, or applicability of diagnostic accuracy studies (e.g., "assess this paper using quadas-2") in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/pdf_extractor.py` is the most direct path to complete the request.
- Use this skill when you need the `diagnostic-study-quality-assessment-quadas-2` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Analyzes clinical diagnostic accuracy studies for bias using the QUADAS-2 tool. Use when Claude needs to assess the quality, risk of bias, or applicability of diagnostic accuracy studies (e.g., "Assess this paper using QUADAS-2").
- Packaged executable path(s): `scripts/pdf_extractor.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/example_asset.txt`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/diagnostic-study-quality-assessment-quadas-2"
python -m py_compile scripts/pdf_extractor.py
python scripts/pdf_extractor.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/pdf_extractor.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/pdf_extractor.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Packaged assets: reusable files are available under `assets/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

To assess a study, follow these steps:

1.  **Analyze Patient Selection**:
    *   Assess if the sample was consecutive or random.
    *   Check for case-control design (should be avoided).
    *   Check for inappropriate exclusions.
    *   See `references/quadas_2_criteria.md` for detailed signaling questions.

2.  **Analyze Index Test**:
    *   Assess if the index test results were interpreted without knowledge of the reference standard.
    *   Check if the threshold was pre-specified.

3.  **Analyze Reference Standard**:
    *   Assess if the reference standard correctly classifies the target condition.
    *   Check if reference standard results were interpreted without knowledge of the index test.

4.  **Analyze Flow and Timing**:
    *   Assess the interval between index test and reference standard.
    *   Check if all patients received the reference standard (and the same one).
    *   Check if all patients were included in the analysis.

## Output Format

For each domain (Patient Selection, Index Test, Reference Standard, Flow and Timing), you MUST output the findings in the following structure:

```markdown

### [Domain Name]

**[Signaling Question 1]?**
- Comments: [Explanation in Chinese]
- Quote: [Original text quote]
- Answer: [Yes/No/Unclear]

... (Repeat for all signaling questions)
```

## Quality Rules

1.  **Language**: Explanations (Comments) must be in Chinese.
2.  **Evidence**: Every judgment must be supported by a direct quote from the paper.
3.  **Strictness**: If information is missing, select "Unclear". Do not guess.

## PDF Parsing Tool

For processing PDF literature, you can use the provided Python script:

```bash

# Install dependencies
pip install PyPDF2

# Extract full text
python scripts/pdf_extractor.py "paper.pdf"

# Extract specific page range
python scripts/pdf_extractor.py "paper.pdf" 5 15
```

The script will automatically extract the text, which you can then copy and send to me for QUADAS-2 assessment.

## References

-   [QUADAS-2 Criteria](references/quadas_2_criteria.md): Detailed signaling questions and judgment guidelines.

