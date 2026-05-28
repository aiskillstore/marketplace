---
name: article-format-adjustment
description: Adjust academic paper formatting and convert between DOCX/LaTeX/Markdown when you need to meet a journal or school template requirement.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/format_adjuster.py --help
```

## When to Use

- You have a draft in **Word/LaTeX/Markdown** and must submit it in a **different format** (e.g., DOCX → LaTeX).
- A journal or school requires strict **typography rules** (fonts, sizes, margins, spacing) and you want them applied automatically.
- You need to enforce consistent **figure/table captions** and table border styles across the whole manuscript.
- You must switch or standardize **citation/reference styles** (e.g., IEEE, APA, GB/T 7714) before submission.
- You want to apply a **known journal template** (e.g., Nature/Science/Elsevier) or a **custom JSON/YAML template** to multiple papers.

## Key Features

- **Format conversion**
  - Word (`.docx`) ↔ Markdown (`.md`)
  - Word (`.docx`) ↔ LaTeX (`.tex`) (via Pandoc)
  - Markdown (`.md`) ↔ LaTeX (`.tex`)
  - Preserves document structure and basic formatting as much as possible

- **Full formatting adjustment**
  - Typography: fonts, font sizes (body/headings/footnotes), line spacing, margins, paragraph indentation and spacing
  - Figures/Tables: caption font size, caption position, table font, table border/line styles
  - References: citation styles (APA/MLA/Chicago/IEEE/GB/T 7714), reference list formatting, in-text citation formatting
  - Terminology: first-occurrence abbreviation annotation, terminology consistency checks, unit formatting standardization

- **Journal template management**
  - Built-in templates (e.g., Nature, Science, IEEE, Elsevier)
  - Template download by journal name (best-effort from official sources/Overleaf)
  - Custom templates via **JSON/YAML** configuration

- **Validation**
  - Checks whether the output meets the configured formatting requirements.

## Dependencies

### Runtime
- Python `>= 3.8`

### Python packages (typical)
- `python-docx` (Word read/write)
- `markdown` (Markdown processing)
- `PyYAML` (YAML parsing)
- `requests` (template download)
- `beautifulsoup4` (HTML parsing)

### System tools
- `pandoc` (required for DOCX ↔ LaTeX conversions)
  - Windows: `choco install pandoc`
  - macOS: `brew install pandoc`
  - Linux (Debian/Ubuntu): `apt install pandoc`

> Note: Exact package versions depend on `requirements.txt` in your repository.

## Example Usage

### 1) Apply a built-in journal template (DOCX → formatted DOCX)
```bash
python scripts/init_run.py \
  --input paper.docx \
  --journal "Nature" \
  --output paper_formatted.docx
```

### 2) Apply a custom configuration (MD → formatted MD)
```bash
python scripts/init_run.py \
  --input paper.md \
  --config formats/my_journal.json \
  --output paper_adjusted.md
```

### 3) Download a journal template configuration
```bash
python scripts/init_run.py \
  --download-template "Science" \
  --output templates/science_format.json
```

### 4) Minimal end-to-end runnable Python example (module usage)
```python
from scripts.format_converter import FormatConverter
from scripts.format_adjuster import FormatAdjuster

def run(input_file: str, config: dict, output_file: str):
    converter = FormatConverter()
    adjuster = FormatAdjuster(config)

    # 1) Normalize to Markdown as an intermediate representation
    md = converter.to_markdown(input_file)

    # 2) Apply formatting rules
    formatted_md = adjuster.apply_format(md, config)

    # 3) Validate against the same rules
    ok = adjuster.validate_format(formatted_md, config)
    if not ok:
        raise RuntimeError("Validation failed: output does not meet the configured requirements.")

    # 4) Convert back to the desired output format inferred from output_file
    converter.from_markdown(formatted_md, output_file)

if __name__ == "__main__":
    config = {
        "font": {"body": "Times New Roman", "body_size": 10},
        "spacing": {"line_space": "single", "paragraph_space": 6, "indent": 0.5},
        "margins": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54},
        "references": {"style": "Nature", "format": "numbered"},
        "figures": {"caption_position": "below", "font_size": 9},
        "tables": {"caption_position": "above", "font_size": 9, "borders": True},
    }
    run("paper.docx", config, "paper_formatted.docx")
```

## Implementation Details

### Processing pipeline
1. **Detect input format** (`.docx` / `.md` / `.tex`)
2. **Convert to Markdown** as a unified intermediate representation
3. **Apply formatting rules** from a selected journal template or custom config
4. **Validate** the formatted result against the config
5. **Convert to target format** (DOCX/MD/TEX)

### Core modules (typical responsibilities)
- `format_converter.py`
  - Conversion engine between Word/Markdown/LaTeX
  - Uses Pandoc for conversions involving LaTeX and/or DOCX where needed
- `format_adjuster.py`
  - Applies typography, figure/table, and reference formatting rules
  - Provides validation routines to check compliance
- `template_downloader.py`
  - Downloads template/config by journal name (best-effort)
  - Parses web sources (often via `requests` + `beautifulsoup4`)
- `format_validator.py`
  - Performs rule-based checks (margins, font sizes, caption placement, citation style selection, etc.)

### Configuration schema (key parameters)
A configuration file (JSON/YAML) typically includes:

- `font`
  - `body`, `body_size`, `title`, `title_size`, `caption`, `caption_size`
- `spacing`
  - `line_space` (`single` / `1.5` / `double`)
  - `paragraph_space` (e.g., points)
  - `indent` (e.g., first-line indent)
- `margins`
  - `top`, `bottom`, `left`, `right` (commonly in cm)
- `references`
  - `style` (e.g., `IEEE`, `APA`, `GB/T 7714-2015`)
  - `format` (e.g., `numbered`, `author-year`)
- `figures` / `tables`
  - `caption_position` (`above` / `below`)
  - `font_size`
  - `borders` (tables)

### CLI parameters (behavior)
- `--input`: input file path (**required**)
- `--output`: output file path (auto-generated if omitted)
- `--config`: path to JSON/YAML config (uses built-in default if omitted)
- `--journal`: journal name (selects a built-in or downloaded template)
- `--download-template`: journal name to download a template config
- `--format`: output format (`docx` / `md` / `tex`), defaults to the input format

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
- If a file is produced, prefer a deterministic output name such as `article_format_adjustment_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/format_adjuster.py --help
```

Expected output format:

```text
Result file: article_format_adjustment_result.md
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
