---
name: lab-prep-calculations
description: Perform pre-experiment calculations and generate step-by-step preparation protocols for dilutions, solution preparation, dissolution, and % concentrations when planning formulations and lab prep workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Preparing a working solution from a concentrated stock and needing exact pipetting and solvent volumes.
- Planning a solid-to-solution preparation (weighing + dissolution) with molecular weight and purity corrections.
- Designing a serial dilution scheme when a single-step dilution factor is impractical or exceeds pipetting limits.
- Converting and preparing percentage-based solutions (w/v, v/v, w/w), including density-based mass-volume conversions.
- Generating an executable lab protocol (steps, equipment list, and warnings) before running an experiment.

## Key Features

- Dilution calculations using **C1V1 = C2V2**, including solvent volume determination.
- Automatic suggestion/structuring of **serial dilution** steps when dilution factors are large.
- Solid preparation calculations using **m = C × V × MW**, with **purity/content correction**.
- Percentage concentration conversions (**w/v**, **v/v**, **w/w**) and density-aware conversions when applicable.
- Unit normalization (e.g., M/mM/µM; L/mL/µL) and sanity checks (e.g., **V1 ≤ V2**).
- Protocol-style outputs: calculation summary, step list, equipment/materials, and risk notes.

## Dependencies

- None (documentation-only skill; no runtime dependencies specified).

## Example Usage

**Goal:** Prepare **50 mL of 10 mM NaCl** from a **1.0 M NaCl stock**.

**Inputs**
- Target concentration (C2): 10 mM
- Target final volume (V2): 50 mL
- Stock concentration (C1): 1.0 M
- Solute/solvent: NaCl stock in water; dilute with water

**Calculation (C1V1 = C2V2)**
- Convert units: 1.0 M = 1000 mM
- \( V1 = \frac{C2 \times V2}{C1} = \frac{10\ \text{mM} \times 50\ \text{mL}}{1000\ \text{mM}} = 0.5\ \text{mL} \)
- Solvent volume to add:
  - \( V_{\text{solvent}} = V2 - V1 = 50.0\ \text{mL} - 0.5\ \text{mL} = 49.5\ \text{mL} \)

**Executable Protocol**
1. Label a clean 50 mL tube or volumetric container: "10 mM NaCl, 50 mL".
2. Pipette **0.50 mL** of **1.0 M NaCl** stock into the container.
3. Add **~45 mL** of water and mix.
4. Bring to final volume by adding water to **50.0 mL total** (or add **49.5 mL** water if using a graduated vessel and not accounting for mixing losses).
5. Mix thoroughly (invert or stir) until homogeneous.

**Equipment & Materials**
- Micropipette (range covering 0.50 mL) and compatible tips
- 50 mL tube or volumetric flask/cylinder
- 1.0 M NaCl stock solution
- Water (or specified buffer)
- Marker/label

**Checks / Warnings**
- Ensure pipette accuracy at 0.50 mL (use an appropriate pipette range).
- Confirm the stock concentration and that the solvent/buffer matches experimental requirements.

## Implementation Details

- **Requirement confirmation**
  - Target: concentration, final volume, solute, solvent/buffer.
  - Known parameters (as applicable): stock concentration, molecular weight (MW), purity/content, density.
  - Constraints: solubility limits, minimum weighable mass, pipetting range, available glassware.

- **Dilution**
  - Core equation: **C1V1 = C2V2**
  - Outputs: required stock volume **V1** and solvent addition volume **V2 − V1**
  - Validation: enforce **V1 ≤ V2**; normalize units before computation.

- **Serial dilution**
  - Trigger: dilution factor too large for a single step (e.g., impractical pipetting volume or equipment limits).
  - Method: factor the overall dilution into multiple steps; for each step output:
    - step dilution factor
    - aliquot volume to transfer
    - solvent volume to add

- **Solid preparation / dissolution**
  - Mass from molarity: **m = C × V × MW**
  - Purity/content correction: **m_adj = m / purity** (purity as a fraction, e.g., 0.98)
  - Protocol notes may include dissolution aids (heating, sonication, pH adjustment) based on solubility/constraints.

- **Percentage concentrations**
  - Support conversions among **w/v**, **v/v**, **w/w**
  - If density is provided, perform mass-volume conversions to produce weigh/measure instructions.

- **Verification and output formatting**
  - Normalize units (M/mM/µM; L/mL/µL; g/mg).
  - Sanity checks: volumes non-negative; final volume matches target; step volumes within equipment ranges.
  - Output structure guidance and verification checklist: see `references/guide.md`.
  - Reusable structured output template: `assets/lab_prep_calc_template.md`.

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
- If a file is produced, prefer a deterministic output name such as `lab_prep_calculations_result.md` unless the skill documentation defines a better convention.
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
Result file: lab_prep_calculations_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Perform pre-experiment calculations and generate step-by-step preparation protocols for dilutions, solution preparation, dissolution, and % concentrations when planning formulations and lab prep workflows.
