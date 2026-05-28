---
name: medchem
description: Medicinal chemistry screening filters for compound prioritization; use when you need to apply drug-likeness rules, PAINS/structural alerts, and complexity metrics to triage or optimize libraries.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Screening large compound libraries to quickly triage for drug-like candidates (e.g., Lipinski/Veber + alerts).
- Flagging problematic chemotypes (e.g., PAINS, reactive/toxicophores, curated structural alerts) before follow-up assays.
- Prioritizing lead-optimization candidates with stricter criteria (lead-like rules, demerit systems, complexity caps).
- Enforcing property constraints (MW/logP/TPSA/rotatable bonds) for target-specific design windows (e.g., CNS).
- Identifying molecules containing specific functional groups/scaffolds (e.g., Michael acceptors, hinge binders) for SAR or risk assessment.

## Key Features

- **Drug-likeness and medchem rule sets**: Lipinski (Ro5), Veber, Oprea, CNS, lead-like (soft/strict), Rule of Three, REOS, Golden Triangle, etc.
- **PAINS and structural alert filtering**: curated alert catalogs and pattern-based screening.
- **Curated industrial filter sets**: e.g., NIBR filters; **Lilly demerit** scoring with pass/fail thresholds.
- **Functional-group detection** via SMARTS-based group matchers (hinge binders, phosphate binders, Michael acceptors, reactive groups, custom patterns).
- **Named catalogs** of curated structures (functional groups, protecting groups, reagents, fragments) for matching and annotation.
- **Molecular complexity metrics** (e.g., Bertz/Whitlock/Barone-style) and threshold-based complexity filters.
- **Constraint-based filtering** for property windows (MW/logP/TPSA/RB, etc.).
- **Query language** to combine heterogeneous criteria (rules + alerts + numeric thresholds) into a single expression.

## Dependencies

- `medchem` (latest)
- `datamol` (latest)
- `pandas` (latest, for tabular workflows)

## Example Usage

```python
# End-to-end, runnable example:
# 1) load SMILES
# 2) apply Ro5 + Veber
# 3) apply common structural alerts
# 4) compute complexity and filter
# 5) export a CSV with decisions

import pandas as pd
import datamol as dm
import medchem as mc

smiles_list = [
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # caffeine
    "c1ccccc1",  # benzene
]

df = pd.DataFrame({"smiles": smiles_list})
mols = [dm.to_mol(smi) for smi in df["smiles"]]

# 1) Drug-likeness rules
rule_filter = mc.rules.RuleFilters(rule_list=["rule_of_five", "rule_of_veber"])
rule_res = rule_filter(mols=mols, n_jobs=-1, progress=False)
df["passes_rules"] = rule_res["pass"]

# 2) Structural alerts
alerts = mc.structural.CommonAlertsFilters()
alert_res = alerts(mols=mols, n_jobs=-1, progress=False)
df["has_alerts"] = alert_res["has_alerts"]

# 3) Complexity (example threshold)
complex_filter = mc.complexity.ComplexityFilter(max_complexity=500)
complex_res = complex_filter(mols=mols, n_jobs=-1, progress=False)
df["passes_complexity"] = complex_res["pass"]

# 4) Final decision
df["keep"] = df["passes_rules"] & (~df["has_alerts"]) & df["passes_complexity"]

# 5) Save results
df.to_csv("medchem_screening_results.csv", index=False)
print(df)
```

## Implementation Details

- **Rule evaluation (`medchem.rules`)**
  - Rules are implemented as callable checks over SMILES or RDKit-like molecule objects (commonly via `datamol`).
  - `RuleFilters(rule_list=[...])` applies multiple rules and returns a structured result (typically including an overall `pass` plus per-rule details).
  - Typical use: start broad (Ro5/Veber), then tighten (CNS/lead-like) as project constraints become clearer.

- **Structural alerts (`medchem.structural`)**
  - Alert systems are primarily **SMARTS/pattern-based** matchers curated from literature/industrial practice.
  - `CommonAlertsFilters`, `NIBRFilters`, and `LillyDemeritsFilters` provide different philosophies:
    - **Common alerts**: general-purpose red flags.
    - **NIBR**: curated industrial filter set.
    - **Lilly demerits**: assigns penalties per matched rule; a common convention is **reject if total demerits > 100**.

- **Complexity (`medchem.complexity`)**
  - Complexity scores approximate synthetic difficulty / structural intricacy using established heuristics (e.g., Bertz/Whitlock/Barone-style metrics).
  - `ComplexityFilter(max_complexity=...)` converts a numeric score into a pass/fail gate for library triage.

- **Constraints (`medchem.constraints`)**
  - Property windows (MW/logP/TPSA/rotatable bonds, etc.) are applied as **hard filters**.
  - Use constraints to encode target-specific design hypotheses (e.g., CNS-like space) rather than universal “good/bad” judgments.

- **Groups and catalogs (`medchem.groups`, `medchem.catalogs`)**
  - Group detection is SMARTS-driven and returns boolean matches and/or match details (substructure hits).
  - Named catalogs provide curated sets for consistent annotation and matching across projects.

- **Parallelization**
  - Most batch APIs accept `n_jobs`; set `n_jobs=-1` to use all available CPU cores for large libraries.