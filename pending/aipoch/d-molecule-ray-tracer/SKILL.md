---
name: d-molecule-ray-tracer
description: "Generate photorealistic rendering scripts for PyMOL and UCSF ChimeraX."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# 3D Molecule Ray Tracer

Advanced molecular visualization tool that generates professional-grade rendering scripts with cinematic effects for creating publication-quality and cover-worthy molecular images.

## When to Use

- Use this skill when the task is to Generate photorealistic rendering scripts for PyMOL and UCSF ChimeraX.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Generate photorealistic rendering scripts for PyMOL and UCSF ChimeraX.
- Packaged executable path(s): `scripts/main.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/3d-molecule-ray-tracer"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features

- **Multi-Software Support**: Generate scripts for PyMOL and UCSF ChimeraX
- **Photorealistic Rendering**: Ray-tracing, depth of field, ambient occlusion
- **Cinematic Lighting**: Studio, outdoor, and dramatic lighting presets
- **Publication Presets**: Pre-configured settings for journals, covers, and presentations
- **Customizable Scenes**: Fine control over camera, materials, and atmosphere

## Usage

### Basic Usage

```text

# Generate PyMOL script with default settings
python scripts/main.py --pdb 1mbn

# Generate cover-quality render script
python scripts/main.py --pdb 1mbn --preset cover

# Generate ChimeraX script
python scripts/main.py --software chimerax --pdb 1abc --preset publication
```

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--software` | str | pymol | No | Target rendering software (pymol/chimerax) |
| `--pdb` | str | None | Yes | PDB file path or 4-letter PDB ID |
| `--preset` | str | standard | No | Rendering preset (standard/cover/publication/cinematic) |
| `--style` | str | cartoon | No | Molecular representation style |
| `--resolution` | int | from preset | No | Output resolution in pixels |
| `--bg-color` | str | white | No | Background color |
| `--ao-on` | flag | False | No | Enable ambient occlusion |
| `--shadows` | flag | False | No | Enable shadow casting |
| `--fog` | float | from preset | No | Fog density (0-1) |
| `--dof-on` | flag | False | No | Enable depth of field |
| `--dof-focus` | str | center | No | DOF focus point |
| `--dof-aperture` | float | from preset | No | Aperture size (higher = more blur) |
| `--lighting` | str | from preset | No | Lighting preset |
| `--output` | str | auto | No | Output script filename |

### Advanced Usage

```text

# Cover-quality render with depth of field
python scripts/main.py \
  --software pymol \
  --pdb 1mbn \
  --preset cover \
  --dof-on \
  --dof-focus "A:64" \
  --dof-aperture 2.0 \
  --style surface \
  --output cover_render.pml

# Cinematic 4K render
python scripts/main.py \
  --software pymol \
  --pdb complex.pdb \
  --preset cinematic \
  --resolution 3840 \
  --ao-on \
  --shadows \
  --lighting cinematic
```

## Rendering Presets

| Preset | Resolution | Ray Trace | DOF | AO | Shadows | Use Case |
|--------|------------|-----------|-----|-----|---------|----------|
| **Standard** | 2400px | ✓ | ✗ | ✗ | ✗ | Quick high-quality |
| **Cover** | 3000px | ✓ | ✓ | ✓ | ✓ | Journal covers |
| **Publication** | 2400px | ✓ | ✗ | ✓ | ✗ | Manuscript figures |
| **Cinematic** | 3840px | ✓ | ✓ | ✓ | ✓ | Presentations |

## Supported Software

| Software | Best For | Features |
|----------|----------|----------|
| **PyMOL** | Traditional rendering, ease of use | Ray tracing, shadows, AO |
| **ChimeraX** | Modern effects, large structures | PBR lighting, ambient occlusion, VR |

## Technical Difficulty: **MEDIUM**

⚠️ **AI independent acceptance status**: manual inspection required
This skill requires:
- Python 3.8+ environment
- PyMOL 2.5+ or ChimeraX 1.5+ installed separately
- Understanding of molecular visualization concepts

### Required Python Packages

```text
pip install -r requirements.txt
```

### External Software

- **PyMOL**: https://pymol.org/
- **UCSF ChimeraX**: https://www.cgl.ucsf.edu/chimerax/

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts executed locally | Medium |
| Network Access | Fetches PDB structures from RCSB (optional) | Low |
| File System Access | Writes rendering scripts | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | No sensitive data exposure | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access (../)
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Input file paths validated
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment
- [x] Error messages sanitized
- [x] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt

# Install PyMOL or ChimeraX separately
```

## Output Example

```
✓ Rendering script generated: /path/to/cover_render.pml

Configuration:
  Software: pymol
  Preset: cover
  Style: cartoon
  Resolution: 3000px
  Depth of Field: ON
  Ambient Occlusion: ON
  Shadows: ON
  Lighting: cinematic

To render:
  pymol cover_render.pml
  # Or within PyMOL:
  @ cover_render.pml
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully generates valid PyMOL/ChimeraX scripts
- [ ] Scripts execute without errors in target software
- [ ] Output images meet quality standards
- [ ] Handles edge cases gracefully

### Test Cases
1. **Basic Functionality**: Generate script for PDB ID → Valid script created
2. **File Input**: Generate script from PDB file → Valid script created
3. **Preset Override**: Custom parameters override preset → Correct settings applied
4. **Both Software**: Generate for PyMOL and ChimeraX → Both scripts valid

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-15
- **Known Issues**: None
- **Planned Improvements**:
  - Blender integration
  - AI-assisted composition suggestions
  - Real-time preview mode

## References

See `references/` for:
- PyMOL-specific rendering techniques
- ChimeraX lighting documentation
- Colorblind-friendly palettes
- Journal submission guidelines

## Limitations

- **Static Images Only**: Generates scripts for still images, not animations
- **Software Dependency**: Requires separately installed PyMOL or ChimeraX
- **Rendering Time**: High-quality renders can take 10-30 minutes per image
- **Learning Curve**: Advanced effects require understanding of photography concepts
- **File Sizes**: High-res images can be 10-50 MB each
- **No Automatic Layout**: Creates single images; figure assembly requires separate tools

---

**💡 Tip: For creating multiple related figures, save your complete scene setup (lighting, camera, colors) as a PyMOL session file (.pse) or ChimeraX session (.cxs), then modify only the specific elements needed for each figure. This ensures consistency across figure panels.**

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `3d-molecule-ray-tracer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `3d-molecule-ray-tracer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.

