---
name: biomed-outline-generator
description: Generates structured biomedical outlines for review articles, discussion sections, and thesis proposals. Use when a user provides biomedical keywords, results/discussion text, or a proposal title plus background and needs a directly usable academic writing scaffold.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Biomedical Research Outline Generator

This is an **Academic Writing** skill for producing manuscript-grade biomedical outlines with deterministic headings and clear section logic.

## Optional Validation Shortcut

If you want to confirm the local helper path exists before use:

```bash
python scripts/validate_skill.py --check
```

This helper is optional. The primary workflow is still direct outline generation from user input.

## When to Use

Use this skill in biomedical contexts when the user wants one of these three outputs:

- **Type I: Review Outline**
  Input pattern: research directions, disease area, pathway keywords, or field description
- **Type II: Discussion Outline**
  Input pattern: results or discussion paragraphs containing observations, models, markers, statistics, or mechanisms
- **Type III: Thesis / Proposal Outline**
  Input pattern: `Title:` plus background, methods expectations, cohort notes, timeline, or validation requirements

## When Not to Use

- The request is clearly non-biomedical.
- The user wants fabricated results, unsupported claims, or invented citations.
- The request is for a complete manuscript draft rather than an outline.

## Required Inputs

- A biomedical topic, result paragraph, or proposal title with enough context to determine one of the three supported types.

Recommended:

- disease model or population
- key molecules, pathways, or interventions
- study aim or proposal objective
- any special formatting or institutional requirements

## Type Recognition Rules

### Type I: Review Outline

Use this type when the input is mostly:

- topic keywords
- field description
- research direction

Signals:

- no explicit `Title:`
- no detailed result paragraph
- no proposal/timeline language

### Type II: Discussion Outline

Use this type when the input contains:

- observations or findings
- effect sizes or p-values
- model systems such as cell, mouse, cohort, or patient data
- mechanistic hints and limitations

### Type III: Thesis / Proposal Outline

Use this type when the input contains:

- `Title:`
- proposal framing
- background and aims
- plan, feasibility, timeline, or expected outcomes

If the request is off-domain, stop and use the refusal contract in `## Fallback and Refusal Contract`.

## Output Contract

### Type I: Review Outline

Must include:

- title
- abstract
- keywords
- introduction
- `4-6` major chapters
- `2-3` subchapters under each major chapter where appropriate
- conclusion / outlook

### Type II: Discussion Outline

Must include:

- summary of key findings
- interpretation blocks
- literature integration
- limitations
- future directions
- conclusion

### Type III: Thesis / Proposal Outline

Must include:

- project review / background
- purpose and significance
- research plan
- feasibility / risk or ethics considerations
- innovation
- timeline
- expected outcomes

## Formatting Rules

- Markdown headings only: `#`, `##`, `###`
- Stable numeric hierarchy
- concise, field-appropriate wording
- no placeholder text like `to be added`
- no fabricated results or unsupported claims

## Workflow

### 1. Validate domain and sufficiency

Confirm that:

- the topic is biomedical
- there is enough information to classify the request
- the requested output is an outline, not a full manuscript

### 2. Detect type

Assign Type I, II, or III using the rules above.

### 3. Build the section skeleton

Use the output contract for the detected type and keep section order deterministic.

### 4. Enrich with academic logic

For each section, add actionable subpoints that reflect:

- mechanism
- evidence structure
- limitations
- validation or future work

### 5. Final safety and writing pass

Check that:

- the outline remains an outline
- the tone is biomedical and academic
- no claims exceed the source material

## Fallback and Refusal Contract

If the input is non-biomedical or too weak to classify, respond with:

```text
Cannot generate a biomedical outline yet.
Reason: <non-biomedical input / insufficient context / unsupported request>
Accepted retry formats:
- Review: biomedical keywords or topic direction
- Discussion: biomedical results/discussion paragraph
- Proposal: `Title:` plus background and objectives
```

## Validation and Safety Rules

- Do not fabricate citations, statistics, or findings.
- Do not convert associative findings into causal conclusions unless the source clearly supports that level of language.
- For clinically adjacent topics, remain at academic-writing level rather than diagnostic or treatment advice.
- Surface ethics, consent, privacy, or cohort-compliance considerations when the prompt clearly implies them.

## Deterministic Output Rules

- Keep section order fixed for each type.
- Use stable section labels across repeated runs.
- If an expected item is missing, ask for it or leave the section high-level; do not hallucinate details.

## Examples of Accepted Inputs

### Type I

```text
Research direction: tumor microenvironment, macrophage polarization, immune checkpoint resistance
Please generate a review outline.
```

### Type II

```text
In our mouse model, anti-PD-1 reduced tumor burden, but the effect was lost after CSF1 overexpression. Please draft a discussion outline.
```

### Type III

```text
Title: Exosomal miRNAs as early diagnostic biomarkers for Alzheimer's disease
Background: include plasma exosomes, qPCR versus small RNA-seq, validation cohort, and neuroinflammation markers.
```

## Completion Checklist

- Type detection is explicit.
- Output matches the correct outline contract.
- The result is directly usable for academic drafting.
- Any limitation or missing-input warning is surfaced clearly.
