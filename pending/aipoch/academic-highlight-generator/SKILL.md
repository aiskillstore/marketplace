---
name: academic-highlight-generator
description: Generates submission-ready Elsevier/SCI Highlights from manuscript text or extracted PDF/DOCX/TXT content. Use when a user needs 3-5 concise, evidence-grounded highlight bullets for a research paper, review, meta-analysis, case report, or bioinformatics manuscript.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Academic Highlight Generator

Generate journal-ready `Highlights` that can be pasted directly into a submission system. This skill is for **academic writing output**, not for inventing missing results.

## When to Use

- The user wants a `Highlights` section for a manuscript submission.
- The source is an English manuscript, abstract, results summary, or extracted full text.
- The paper falls into one of these types: Original Research, Meta-analysis, Review, Case Report, Bioinformatics, Bibliometrics, or Technical Note.
- The user needs a deterministic, concise output with strict bullet-count and length limits.

## When Not to Use

- The user asks you to fabricate results, novelty claims, study counts, effect sizes, or conclusions that are not in the source.
- The source text is too short to identify study type or key findings reliably.
- The document is a perspective, commentary, editorial, or otherwise unsuitable for formal submission highlights.
- The user provides a binary `.doc` file. This package supports `.txt`, `.pdf`, and `.docx`; convert `.doc` before continuing.

## Required Inputs

Provide one of the following:

- Plain manuscript text, abstract, or structured study summary.
- A supported source file path for `scripts/extract_text.py`: `.txt`, `.pdf`, or `.docx`.

Recommended metadata if available:

- Manuscript type or target journal.
- Core method, main findings, and significance sentence.
- Any wording constraints such as British/American spelling.

## Output Contract

Always return:

```text
Highlights
- <bullet 1>
- <bullet 2>
- <bullet 3>
[- <bullet 4>]
[- <bullet 5>]
```

Hard requirements:

- Exactly `3-5` bullets.
- English bullets only unless the user explicitly requests Chinese.
- Maximum `85` characters per English bullet.
- Objective third-person tone.
- No first person (`we`, `our`).
- No undefined abbreviations, citation markers, or figure/table references.
- Every bullet must be grounded in source material.

## Supported Execution Paths

### Path A: Source text already provided

Use the provided text directly. This is the preferred path for speed and determinism.

### Path B: Source file needs extraction

Use:

```bash
python scripts/extract_text.py <file_path>
```

Supported formats:

- `.txt`
- `.pdf`
- `.docx`

Unsupported format:

- `.doc` -> ask the user to convert to `.docx` or `.pdf` first.

## Workflow

### 1. Validate source sufficiency

Before writing anything, confirm the source contains enough signal to identify:

- study type
- method or evidence base
- main finding or conclusion

If not, stop and use the refusal template in `## Fallback and Refusal Contract`.

### 2. Extract text if needed

If the user provided a file instead of text, run:

```bash
python scripts/extract_text.py <file_path>
```

If extraction fails:

- report the exact failure,
- preserve the original file path in the message,
- do not invent content from the missing file.

### 3. Detect article type

Use `references/prompts.md` to classify the manuscript into one of:

- Original Research
- Meta-analysis
- Review
- Case Report / Case Series
- Bioinformatics Study
- Perspective / Commentary
- Education / Policy Research
- Bibliometric Analysis
- Short Communication / Technical Note
- Other / Unclear

### 4. Generate draft highlights

Select the matching generation prompt from `references/prompts.md`.

Coverage priorities by type:

- Original Research: method, main result, mechanism/utility, significance
- Meta-analysis / Review: evidence base, synthesis method, conclusion, gap/future direction
- Case Report: case feature, diagnostic or treatment learning point, follow-up significance
- Bioinformatics: data source, analytic method, marker/pathway/model, biological relevance
- Bibliometrics: database, time span, tools, hotspots/trends, collaboration pattern
- Technical Note: method/device/process optimization, efficiency or usability gain

### 5. Self-critique and refine

Use the critique and refinement prompts in `references/prompts.md`.

The final output must satisfy all of these checks:

- `3-5` bullets
- no bullet exceeds the limit
- the bullets are not copied verbatim from the abstract
- the set covers method + finding + value at least once
- no fabricated numbers or study claims

## Fallback and Refusal Contract

If the source is unsuitable or insufficient, respond with this structure:

```text
Cannot generate submission-ready Highlights yet.
Reason: <insufficient source / unsupported article type / unsupported file format>
Detected type: <type or Unknown>
Minimum additional input needed:
- <item 1>
- <item 2>
```

Use this refusal contract when:

- the article type is `Other / Unclear`,
- the text is too short to ground claims,
- the user asks for invention rather than extraction,
- the file format is unsupported.

## Deterministic Rules

- Keep the same output header every time: `Highlights`.
- Do not switch between sentence fragments and full sentences in one output.
- Prefer one factual claim per bullet.
- If a key value is unavailable, omit that value instead of guessing it.
- If the source supports only three safe bullets, output three rather than padding to five.

## Quality Checklist

Before returning the final answer, verify:

- Study type and bullet focus are aligned.
- No unsupported causal overstatement appears.
- No clinical recommendation is implied unless the source itself states one cautiously.
- Each bullet is independently readable.
- The final output can be pasted into a journal submission form without reformatting.
