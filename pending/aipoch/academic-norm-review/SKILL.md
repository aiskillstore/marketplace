---
name: academic-norm-review
description: Detects content similarity, verifies standardized citations and abbreviations, and flags potential academic integrity risks; use it before submission, during academic writing QA, or for compliance reviews.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Pre-submission screening**: Run a final compliance check on a manuscript before journal/conference submission.
- **Academic writing quality control**: Ensure citations, references, and abbreviations follow consistent standards across a draft.
- **Institutional compliance review**: Identify potential academic integrity risks (e.g., high similarity passages) for internal audits.
- **Collaborative editing**: Validate consistency when multiple authors contribute sections with different citation/abbreviation habits.
- **Revision triage**: Generate a prioritized issue list with locations to guide efficient corrections.

## Key Features

- **Citation verification**
  - Checks citation formatting and completeness.
  - Validates consistency between in-text citations and the reference list.
- **Abbreviation standardization**
  - Ensures abbreviations are defined at first occurrence.
  - Detects inconsistent abbreviation usage across the document.
- **Similarity and repetition detection**
  - Flags high-similarity passages and repetitive expressions.
  - Suggests paraphrasing and/or adding citations where appropriate.
- **Actionable reporting**
  - Produces an issue list with locations, priorities, and revision suggestions.
  - Supports structured outputs using provided templates.

## Dependencies

- None (documentation-driven skill).
- Optional reference materials:
  - `references/guide.md` (output formats, checklists, key inspection points)
  - `assets/academic_compliance_checklist.md` (reusable structured checklist template)

## Example Usage

### Input

**Manuscript (excerpt)**

```text
In recent years, large language models (LLM) have been widely used in education.
LLM can improve feedback quality. LLM can improve feedback quality.

As shown in [1], the method outperforms baselines. According to Smith et al., 2020, the results are significant.

References
[1] Smith, J. 2020. A Study on Models. Journal of AI.
[2] Doe, A. 2019. Another Paper. Journal of ML.
```

### Run (Checklist-Driven Review)

Use `assets/academic_compliance_checklist.md` as the preferred structured output format when needed, and follow `references/guide.md` for inspection points.

### Output (Sample Findings)

```markdown
# Academic Norm Review Report

## Summary
- Total issues: 6
- High priority: 2
- Medium priority: 3
- Low priority: 1

## Issues

1) [High] Abbreviation not defined at first use
- Location: Paragraph 1, sentence 1
- Evidence: "large language models (LLM)" (LLM is defined, but ensure the long form is correct and consistent)
- Suggestion: Confirm the first occurrence includes the full term + abbreviation, and keep the same form throughout.

2) [High] Repetitive expression / potential high similarity
- Location: Paragraph 1, sentences 2-3
- Evidence: "LLM can improve feedback quality." repeated verbatim
- Suggestion: Remove duplication or paraphrase; add citation if the claim is sourced.

3) [Medium] In-text citation format inconsistent
- Location: Paragraph 2, sentence 2
- Evidence: "According to Smith et al., 2020" vs. "[1]" style elsewhere
- Suggestion: Use a single citation style consistently (e.g., numeric [1] or author-year).

4) [Medium] Reference list and in-text citation mismatch risk
- Location: Paragraph 2
- Evidence: Author-year citation "Smith et al., 2020" should map clearly to a reference entry
- Suggestion: Ensure the reference list supports the chosen in-text style and that all in-text citations resolve to exactly one reference entry.

5) [Medium] Citation completeness check
- Location: References section
- Evidence: Potential missing fields (e.g., volume/issue/pages/DOI) depending on target style
- Suggestion: Complete bibliographic fields per the required style guide.

6) [Low] Abbreviation consistency check
- Location: Entire document
- Evidence: "LLM" appears; verify no variants like "L.L.M." or "LLMs" without definition rules
- Suggestion: Standardize pluralization and punctuation per style guide.
```

## Implementation Details

### 1) Citation Verification

- **Goal**: Ensure citations are correctly formatted, complete, and consistent.
- **Checks**
  - In-text citation style consistency (e.g., numeric vs. author-year).
  - One-to-one resolvability: each in-text citation maps to a reference entry; each reference entry is cited (if required).
  - Completeness of reference fields based on the target style (journal/conference/institutional rules).
- **Outputs**
  - Missing references, uncited references, inconsistent formats, incomplete bibliographic fields.

### 2) Abbreviation Standards

- **Goal**: Ensure abbreviations are introduced and used consistently.
- **Checks**
  - First occurrence definition: `Full Term (ABBR)` or style-required variant.
  - Consistency: same abbreviation for the same term; avoid multiple abbreviations for one concept.
  - Variant detection: punctuation, plural forms, capitalization differences.
- **Outputs**
  - Undefined abbreviations, inconsistent usage, conflicting definitions.

### 3) Similarity Rate and Paraphrasing

- **Goal**: Identify passages that may indicate excessive similarity or repetitive phrasing.
- **Checks**
  - Repeated sentences/phrases within the document.
  - High-overlap segments (when similarity metrics are available in your environment).
- **Recommendations**
  - Paraphrase repetitive content while preserving meaning.
  - Add citations when statements rely on external sources.
  - Prefer removing redundancy when repetition adds no value.
- **Outputs**
  - Flagged segments with locations, severity, and suggested remediation.

### 4) Output and Rectification

- **Goal**: Provide a prioritized, location-aware issue list for efficient revision.
- **Report structure**
  - Summary counts by severity.
  - Issue list with: location, evidence, rationale, and suggested fix.
- **Templates**
  - Use `assets/academic_compliance_checklist.md` for structured reporting.
  - Follow `references/guide.md` for recommended output formats and inspection points.

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

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `academic_norm_review_result.md` unless the skill documentation defines a better convention.
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

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: academic_norm_review_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Detects content similarity, verifies standardized citations and abbreviations, and flags potential academic integrity risks; use it before submission, during academic writing QA, or for compliance reviews.
