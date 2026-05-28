---
name: latex-posters
description: Creates academic-poster writing packages for LaTeX using beamerposter, tikzposter, or baposter. Use when a user needs poster-ready section copy, figure plans, captions, and package-specific layout decisions for conference or thesis posters.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# LaTeX Academic Posters

This is an **Academic Writing** skill for turning research content into a poster-ready LaTeX brief. The core deliverable is not just layout advice, but a writing package that can be assembled directly in `beamerposter`, `tikzposter`, or `baposter`.

## When to Use

- The user needs a conference, thesis-defense, or departmental research poster.
- The user wants help choosing between `beamerposter`, `tikzposter`, and `baposter`.
- The user needs poster-ready section copy, figure plan, captions, and block ordering.
- The user wants to compress a paper, abstract, or slide deck into a readable poster narrative.

## When Not to Use

- The user wants a PowerPoint-native workflow with no LaTeX output at all.
- The user wants to cram full manuscript detail onto one poster.
- The user asks for fake results, invented metrics, or nonexistent figures.

## Core Deliverables

This skill should produce one or more of these outputs:

- **Poster Brief**
  poster size, audience, package choice, and section map
- **Poster Copy Plan**
  title, introduction, methods, results, conclusion, and acknowledgments text limits
- **Figure Plan**
  one-message-per-figure architecture, captions, and panel priorities
- **LaTeX Assembly Guidance**
  package-specific layout choices using bundled assets in `assets/`

## Package Decision Matrix

- Use `tikzposter` when the user wants modern flexible block design and portrait conference style.
- Use `beamerposter` when the user wants a classic academic appearance or already knows Beamer.
- Use `baposter` when the user needs a box-based multi-column layout and explicit panel control.

If the user does not specify a package:

- default to `tikzposter` for most modern research posters
- switch to `beamerposter` for formal thesis-defense aesthetics
- switch to `baposter` when the content is block-heavy and highly modular

## Writing Output Contract

Always provide:

1. recommended package
2. poster size / orientation
3. section list in display order
4. section-level word budget
5. figure plan with one message per figure
6. caption guidance
7. final quality-control checklist

If the user asks for direct copy, provide concise poster-ready wording for:

- title
- one-sentence problem statement
- methods block
- `2-4` results bullets
- conclusion block
- optional QR / data / contact block

## Hard Constraints

- A0 poster: usually `300-800` words total
- no more than `5-6` major content blocks on one poster
- one figure = one message
- avoid dense paragraphs
- body text must remain poster-readable

If the request violates these constraints, refuse the density request and propose a reduced architecture.

## Workflow

### 1. Collect poster context

Confirm:

- poster size and orientation
- audience
- source material type
- required figures or logos
- whether the user needs only a brief, or also section copy

### 2. Choose the package

Use `## Package Decision Matrix`.

### 3. Compress the narrative

Convert the source into:

- one central message
- one methods summary
- `2-3` strongest results
- one clear conclusion

Do not preserve every subsection from the manuscript.

### 4. Plan the figures

For each figure:

- define one message only
- keep labels minimal
- assign where it belongs in the poster flow
- define whether it needs a caption or only a headline

### 5. Assemble the writing package

Return:

- poster brief
- section order
- section copy limits
- figure plan
- LaTeX asset recommendation from `assets/`

## Refusal and Recovery Contract

If the user asks for an unreadable or off-scope poster, respond with:

```text
Cannot produce a readable poster plan as requested.
Reason: <too much content / unsupported non-LaTeX workflow / missing source information>
Suggested recovery:
- <step 1>
- <step 2>
```

Use this when:

- the user wants tiny-font dense content
- the user wants a non-LaTeX-native deliverable
- the source is too incomplete to plan poster copy

## Asset Usage

Bundled assets:

- `assets/beamerposter_template.tex`
- `assets/tikzposter_template.tex`
- `assets/baposter_template.tex`
- `assets/poster_quality_checklist.md`

Use these assets as the implementation anchor. Do **not** reference nonexistent local scripts.

## Academic Writing Rules

- keep the tone neutral and conference-appropriate
- prefer short declarative statements over abstract-like paragraphs
- results language must stay grounded in source evidence
- captions should interpret the figure's role, not repeat every numeric detail

## Final Quality Checklist

Before returning:

- package choice is explicit
- section order is clear
- word budget is realistic
- figure plan is readable
- no fake script requirement appears
- no impossible density request is accepted
