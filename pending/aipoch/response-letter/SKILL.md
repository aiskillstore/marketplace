---
name: response-letter
description: Helps organize reviewer comments and generate a standardized Word (.docx) response letter that maps each change to its exact location (page/paragraph/line). Use when revising a manuscript, replying to peer-review feedback, or preparing internal review responses.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You received peer-review comments and need a point-by-point response letter for journal resubmission.
- You must clearly map every manuscript change to a specific location (page/paragraph/line) for reviewers or editors.
- You need a consistent, professional response structure across multiple reviewers and revision rounds.
- You are coordinating an internal review and want a standardized change log and execution checklist.
- You need a Word (.docx) deliverable rather than a table-based response format.

## Key Features

- Consolidates, merges, and numbers reviewer comments across reviewers.
- Separates major vs. minor comments to prioritize revision work.
- Produces a fixed, repeatable response layout per comment:
  - **Reviewer’s Comment**
  - **Response**
  - **Changes in Text**
- Requires explicit change-location marking (page/paragraph/line) and version labeling.
- Supports quoting revised manuscript text (e.g., blockquotes) to make changes auditable.
- Generates a Word (.docx) response letter plus a modification/execution checklist.
- Adds an **Overview for the Editor** section summarizing major revisions at the beginning.
- Enforces a professional, polite tone throughout.

## Dependencies

- Microsoft Word `.docx` output (Word-compatible document generation)
- Reference format guide: `references/guide.md`

## Example Usage

```text
Input:
- Manuscript (tracked version or clean version + change notes)
- Reviewer comments (all reviewers, all rounds)
- Current manuscript pagination/line numbering scheme (if available)

Steps:
1) Organize comments
   - Merge all reviewer comments into a single list.
   - Number them sequentially (e.g., R1-1, R1-2…; R2-1…).
   - Tag each as Major or Minor.

2) Draft "Overview for the Editor"
   - Write one concise paragraph summarizing the major revisions and their rationale.

3) Write point-by-point responses
   For each numbered comment, output:
   - Reviewer’s Comment: (verbatim or lightly cleaned for clarity)
   - Response: (polite, direct, addresses the request)
   - Changes in Text: (what changed + where)

4) Mark locations and quote revised text
   - Provide page/paragraph/line for each change.
   - Specify additions/deletions.
   - Quote the revised paragraph when the main text is modified.

5) Generate deliverables
   - Export the full response letter as a Word document (.docx).
   - Produce a modification/execution checklist to verify all changes are applied.

Output (Word .docx structure):
- Title / Manuscript info (optional)
- Overview for the Editor
- Responses to Reviewer 1
  - R1-1
  - R1-2
  ...
- Responses to Reviewer 2
  ...
- Modification / Execution Checklist
```

## Implementation Details

- **Comment normalization and numbering**
  - Merge comments from all sources; assign stable IDs (e.g., `R{reviewer}-{index}`) to preserve traceability across revision rounds.
- **Major vs. minor classification**
  - Major: requests affecting study design, analyses, interpretation, or core claims.
  - Minor: wording, formatting, clarifications, citations, typos.
- **Per-comment fixed layout**
  - Each response must include three labeled blocks: *Reviewer’s Comment*, *Response*, *Changes in Text*.
- **Location marking**
  - Use page/paragraph/line when available; otherwise use section/subsection headings plus paragraph index.
  - Always indicate whether text was **added**, **deleted**, or **rewritten**.
- **Revised-text excerpting**
  - When the manuscript body changes, include the updated paragraph as an indented blockquote under *Changes in Text* for auditability.
- **Output constraints**
  - Final deliverable is a Word document (`.docx`).
  - Do not use table format for the response letter.
- **Formatting and checklists**
  - Follow `references/guide.md` for required output formats, checklist items, and key writing points.