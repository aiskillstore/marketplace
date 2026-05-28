---
name: cobrapy
description: Constraint-based reconstruction and analysis (COBRA) for metabolic models; use when you need to simulate growth/production, analyze flux ranges, or run knockout and medium studies from SBML/JSON/YAML models.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# COBRApy (COBRA: Constraint-Based Reconstruction and Analysis)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Constraint-based reconstruction and analysis (COBRA) for metabolic models; use when you need to simulate growth/production, analyze flux ranges, or run knockout and medium studies from SBML/JSON/YAML models.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Data Analytics/cobrapy
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to perform constraint-based analysis on metabolic networks, especially for:

1. **Predicting growth or production** under specific media and objectives using Flux Balance Analysis (FBA).
2. **Quantifying flux uncertainty** and alternative optima using Flux Variability Analysis (FVA) and flux sampling.
3. **Identifying essential genes/reactions** via single/double knockout (deletion) studies.
4. **Designing or optimizing media** (e.g., minimal medium) to support a target growth rate.
5. **Repairing infeasible models** by gapfilling against a universal reaction database/model.

## 2. Key Features

- **Model I/O and management**: load/save models in SBML (preferred), JSON, and YAML; access reactions/metabolites/genes.
- **FBA variants**: standard FBA, parsimonious FBA (pFBA), geometric FBA.
- **FVA**: compute min/max feasible fluxes; supports fraction-of-optimum and loopless FVA.
- **Knockout analysis**: single/double gene and reaction deletions; temporary edits via context managers.
- **Medium handling**: inspect and modify `model.medium`; compute minimal media (optionally MILP-based).
- **Flux sampling**: sample feasible flux space (OptGP/ACHR) and validate samples.
- **Production envelopes**: phenotypic phase planes / production envelopes for trade-off exploration.
- **Gapfilling**: propose reaction additions to restore feasibility.
- **Model construction**: build models from scratch (metabolites, reactions, GPR rules, boundaries, objectives).

## 3. Dependencies

- `cobra` (COBRApy) — version varies by environment (commonly `>=0.20`)
- A supported LP/MILP solver (one of):
  - `glpk` / `swiglpk` (often default)
  - `cplex` (optional)
  - `gurobi` (optional)
- Optional (for plotting/analysis in examples):
  - `pandas`
  - `matplotlib`

## 4. Example Usage

The following script is a complete, runnable example that loads a built-in model, runs FBA, performs FVA, runs a gene knockout, adjusts medium, and samples fluxes.

```python

# cobrapy_example.py
from cobra.io import load_model
from cobra.flux_analysis import flux_variability_analysis, single_gene_deletion, pfba
from cobra.sampling import sample

def main():
    # 1) Load a model (built-in test model)
    model = load_model("textbook")  # E. coli core model

    # 2) Run standard FBA
    sol = model.optimize()
    print("=== FBA ===")
    print("Status:", sol.status)
    print("Objective (growth):", sol.objective_value)

    # 3) Run pFBA (minimize total flux at optimal growth)
    pfba_sol = pfba(model)
    print("\n=== pFBA ===")
    print("Objective (growth):", pfba_sol.objective_value)

    # 4) Flux Variability Analysis at 90% of optimum
    print("\n=== FVA (90% optimum) ===")
    fva = flux_variability_analysis(model, fraction_of_optimum=0.9)
    print(fva.head())

    # 5) Single gene deletion screen (may take time on large models)
    print("\n=== Single Gene Deletion (first 5 rows) ===")
    del_res = single_gene_deletion(model)
    print(del_res.head())

    # 6) Medium modification (must re-assign the full dict)
    print("\n=== Medium ===")
    medium = model.medium
    # Example: limit glucose uptake (exchange IDs depend on the model)
    if "EX_glc__D_e" in medium:
        medium["EX_glc__D_e"] = 5.0
        model.medium = medium
        sol2 = model.optimize()
        print("Growth after limiting glucose:", sol2.objective_value)
    else:
        print("Model has no EX_glc__D_e in medium; skipping medium edit.")

    # 7) Flux sampling (small n for quick demo)
    print("\n=== Flux Sampling ===")
    samples = sample(model, n=200, method="optgp")
    print(samples.head())

if __name__ == "__main__":
    main()
```

Run:

```bash
python cobrapy_example.py
```

## 5. Implementation Details

### 5.1 Core optimization model (FBA)
- COBRApy formulates a **linear program (LP)**:
  - **Mass balance** (steady state): \( S \cdot v = 0 \)
  - **Bounds**: \( l \le v \le u \)
  - **Objective**: maximize (or minimize) a linear function \( c^\top v \) (e.g., biomass reaction flux)
- `model.optimize()` solves the LP and returns a `Solution` with:
  - `solution.status` (e.g., `optimal`)
  - `solution.objective_value`
  - `solution.fluxes` (pandas Series of reaction fluxes)

### 5.2 Reaction directionality and bounds
- Irreversible reactions typically use `lower_bound = 0`.
- Reversible reactions allow negative flux: `lower_bound < 0`.
- Use `reaction.bounds = (lb, ub)` to set both consistently.

### 5.3 Gene-Protein-Reaction (GPR) rules
- `reaction.gene_reaction_rule` encodes Boolean logic:
  - `"gene1 and gene2"` means both genes required.
  - `"gene1 or gene2"` means either gene sufficient.
- Knockouts propagate through GPR logic to constrain affected reactions.

### 5.4 FVA parameters
- `flux_variability_analysis(model, fraction_of_optimum=x)` constrains the objective to be at least `x * optimum` before computing per-reaction min/max.
- `loopless=True` attempts to remove thermodynamically infeasible loops (typically more expensive).

### 5.5 Context manager for temporary edits
- `with model:` creates a reversible sandbox:
  - changes to objectives, bounds, knockouts, and reaction sets revert automatically on exit.
- This prevents accidental state carryover across analyses.

### 5.6 Flux sampling
- Sampling explores the feasible polytope defined by constraints.
- `sample(..., method="optgp")` uses OptGP (often parallelizable); `method="achr"` uses ACHR.
- For numerical stability, validate samples when needed (e.g., via `OptGPSampler.validate`).

### 5.7 Medium handling
- `model.medium` is a dictionary mapping exchange reaction IDs to allowed uptake rates.
- You must **re-assign** the full dictionary after edits: `model.medium = medium`.

### 5.8 Gapfilling
- `gapfill(model, universal)` searches for a minimal set of reactions from `universal` that restores feasibility (commonly formulated as MILP/optimization with penalties).
- Use `with model:` when testing removals/additions to avoid permanently mutating the model.

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
- If a file is produced, prefer a deterministic output name such as `cobrapy_result.md` unless the skill documentation defines a better convention.
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
Result file: cobrapy_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Constraint-based reconstruction and analysis (COBRA) for metabolic models; use when you need to simulate growth/production, analyze flux ranges, or run knockout and medium studies from SBML/JSON/YAML models.
