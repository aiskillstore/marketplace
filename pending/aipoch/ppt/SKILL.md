---
name: ppt
description: Create and export PPTX decks using the local HTML/JS PPT framework in `D:\SKILL\project\ppt`. Use this when you need to generate slides from a topic/outline, edit slide content via `projects/*.js`, preview as HTML, or export a `.pptx` without relying on an existing template.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## When to Use

- You need to generate a new slide deck from a topic, brief, or outline (6-10 sections) and want a consistent visual style.
- You want to iteratively edit slide content and structure in code (`projects/*.js`) rather than in PowerPoint.
- You need a fast HTML preview loop before exporting a final `.pptx`.
- You must export a `.pptx` without starting from an existing PowerPoint template.
- You want to standardize slide layouts using predefined component types (e.g., comparison, timeline, stats).

## Key Features

- Code-driven deck authoring via `const SLIDES = [...]` in `projects/*.js`.
- Built-in slide element/component types (e.g., `comparison`, `timeline`, `stats`, `valueCards`, `quote`, `ending`).
- HTML preview generation for quick review and iteration.
- PPTX export pipeline producing a PowerPoint-compatible `.pptx`.
- Consistent layout rules (spacing, margins) and guidance for palette selection.

## Dependencies

- Python (3.10+ recommended)
- Python packages listed in: `D:\SKILL\project\ppt\requirements.txt`

## Example Usage

### 1) Create a project file

Create: `D:\SKILL\project\ppt\projects\demo-20260227.js`

```javascript
const SLIDES = [
  {
    badge: { icon: "*", text: "DEMO" },
    title: { text: "PPT Framework Demo" },
    subtitle: "Build in JS, preview in HTML, export to PPTX",
    clickHint: "2026-02-27 / v1",
    elements: [
      {
        step: 1,
        type: "quote",
        text: "A code-first workflow makes decks reproducible and easy to iterate.",
        author: { icon: "-", text: "Key takeaway" }
      }
    ]
  },
  {
    badge: { icon: "*", text: "AGENDA" },
    title: { text: "What We Will Cover" },
    subtitle: "A simple outline slide",
    clickHint: "Section 1/3",
    elements: [
      { step: 1, type: "valueCards", title: "Authoring", items: ["Edit `projects/*.js`", "Use `const SLIDES`"] },
      { step: 2, type: "valueCards", title: "Preview", items: ["Generate HTML", "Review layout quickly"] },
      { step: 3, type: "valueCards", title: "Export", items: ["Convert to PPTX", "Share the deck"] }
    ]
  },
  {
    badge: { icon: "*", text: "END" },
    title: { text: "Next Steps" },
    subtitle: "Export and refine",
    clickHint: "Section 3/3",
    elements: [
      { step: 1, type: "ending", title: "Export the deck", bullets: ["Run HTML build", "Run PPTX conversion"] }
    ]
  }
];

module.exports = { SLIDES };
```

### 2) Preview as HTML

From `D:\SKILL\project\ppt`:

```bash
python build_html.py demo-20260227
```

### 3) Export to PPTX

```bash
python convert_to_pptx.py demo-20260227
```

### 4) Output location

Generated files are written to:

- `D:\SKILL\project\ppt\output\`

## Implementation Details

### Authoring model

- Each deck is defined in a single project file under `projects/`.
- The deck is an ordered array: `const SLIDES = [ ... ]`.
- Each slide typically includes:
  - `badge`: small label (icon + text)
  - `title`: primary headline (keep short and specific)
  - `subtitle`: one-sentence context
  - `clickHint`: date/version or navigation hint
  - `elements`: ordered visual components with `step` sequencing

### Component usage

- Use component `type` values such as `comparison`, `timeline`, `stats`, `valueCards`, `quote`, `ending` to ensure each slide has a visual structure.
- Prefer minimal body text; express content as concise bullets or structured blocks.

### Workflow guidance (content + design)

- Outline first: draft 6-10 sections, each with a single intent; expand each into 3-5 concise bullets.
- Palette rule: choose one dominant color, two supporting colors, and one accent color.
- Avoid text-only slides: every slide should include at least one visual component.
- Layout rule: keep spacing consistent and maintain margins ≥ 0.5".

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

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `ppt_result.md` unless the skill documentation defines a better convention.
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

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: ppt_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
