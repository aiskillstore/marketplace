---
name: cover-letter-generator
description: Generates a journal-ready cover letter from manuscript metadata, highlights, and journal-fit notes. Use when preparing an academic submission package and you need editor-facing language that clearly states novelty, relevance, declarations, and corresponding-author details.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Cover Letter Generator

Draft a submission-ready academic cover letter for a target journal. This skill is for **editor-facing academic writing**, not for inventing missing paper content.

## When to Use

- The user is preparing an initial manuscript submission.
- The user has a paper title, contribution summary, and target-journal context.
- The user wants a professional cover letter with journal fit, novelty, declarations, and closing details.
- The user needs a deterministic structure rather than ad-hoc prose.

## When Not to Use

- The user has not chosen a target journal and only wants a generic marketing blurb.
- The user is asking for peer-review responses, rebuttal letters, or grant cover pages.
- The user wants you to invent results, journal scope, reviewer identities, or declarations that were not supplied.

## Required Inputs

Minimum required:

- manuscript title
- target journal
- `2-4` core contributions or innovation points
- corresponding author name, affiliation, and email

Strongly recommended:

- one-sentence journal fit rationale
- brief methods summary
- brief key-results summary
- originality / exclusive-submission statement
- optional reviewer suggestions
- optional conflict-of-interest or ethics statement

## Missing-Input Recovery

If any required field is missing, do **not** output a fake journal-ready letter. Use this structure first:

```text
Cannot finalize the cover letter yet.
Missing required items:
- <item 1>
- <item 2>

Usable fallback:
- I can draft a partial letter shell after these items are supplied.
```

Only draft a partial shell if the user explicitly wants one after seeing the missing items.

## Output Contract

Return a complete letter using the structure below:

1. Salutation to the editor
2. Submission request with manuscript title and journal name
3. Journal-fit paragraph
4. Novelty / contribution paragraph
5. Methods + key-results paragraph
6. Relevance / readership / reproducibility paragraph
7. Required declarations paragraph
8. Optional reviewer / COI paragraph
9. Professional closing with corresponding-author identity

Formatting rules:

- professional, restrained tone
- `4-6` short paragraphs
- no hype language such as `groundbreaking`, `revolutionary`, or `game-changing`
- no claims not grounded in supplied manuscript information
- no bullet lists in the final letter unless the user explicitly requests them

## Drafting Workflow

### 1. Validate inputs

Confirm that all required items are present.

If not:

- invoke `## Missing-Input Recovery`
- stop before drafting a "journal-ready" letter

### 2. Build the journal-fit angle

Write `1-2` sentences that connect:

- manuscript topic
- target journal scope
- expected readership

Avoid generic fit claims like `This paper will interest your readers` unless followed by a concrete reason.

### 3. Write the contribution core

Summarize:

- what is new
- why it matters
- what prior gap or limitation it addresses

Keep this focused on contributions, not full manuscript retelling.

### 4. Add methods and results evidence

Use only concise, high-signal evidence:

- study approach
- model, dataset, or experimental system
- strongest result or takeaway

Do not turn this section into a mini-abstract.

### 5. Add declarations

Always include or explicitly request:

- originality / not under review elsewhere
- author approval

Add journal-specific statements if the user supplies them:

- ethics approval
- informed consent
- data availability
- code availability
- conflict of interest
- suggested reviewers

## Journal-Specific Declaration Matrix

Use the following logic:

- Basic engineering / methods journal:
  include originality, author approval, code/data availability if relevant
- Biomedical / clinical journal:
  include originality, author approval, ethics / consent if relevant, COI, data availability
- Computational journal:
  include originality, author approval, reproducibility / code availability if relevant

If the user does not provide a declaration that may be required, ask for it rather than inventing it.

## Templates and Assets

- Use `assets/cover_letter_template.md` as the paragraph skeleton.
- Use `references/guide.md` as the preflight checklist.

## Deterministic Rules

- Keep paragraph order stable.
- Mention the journal name in the opening paragraph exactly once unless there is a clear need to repeat it.
- Keep reviewer suggestions and COI in the closing section, not the middle of the letter.
- If a quantitative result is not supplied, describe the contribution qualitatively instead of guessing numbers.

## Quality Checklist

Before returning the letter, verify:

- the journal fit is concrete
- the novelty statement is specific
- the methods / results paragraph is concise
- declarations are present or explicitly requested
- the final tone sounds like editor-facing academic correspondence
