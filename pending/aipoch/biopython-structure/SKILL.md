---
name: biopython-structure
description: Use Bio.PDB to parse and analyze protein structures (PDB/mmCIF) for structural bioinformatics tasks; use when you need structure parsing, geometry calculations, or structural comparison/superposition.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# biopython-structure

## When to Use

- You need to parse **PDB** or **mmCIF** files and access the structure hierarchy (model → chain → residue → atom).
- You want to compute **geometric measurements** such as distances, bond angles, and dihedral angles between atoms/residues.
- You need **neighbor searches** (e.g., find residues/atoms within a cutoff) for contact analysis or local environment inspection.
- You want to perform **structural comparison**, including alignment/superposition and RMSD-style evaluation.
- You need to **extract, modify, and save** structures (e.g., subset chains/residues and write back to PDB/mmCIF).

## Key Features

- **Structure parsing** for PDB/mmCIF using `Bio.PDB` parsers.
- **Hierarchical traversal** and selection of models, chains, residues, and atoms.
- **Geometry calculations**: distance, angle, and dihedral computations using Bio.PDB utilities.
- **Neighbor search** via spatial indexing (`NeighborSearch`) for efficient cutoff queries.
- **Structural operations**: extraction, saving, and **superposition** (e.g., `Superimposer`).
- **Quality/annotation hooks**: optional integration with **DSSP** (external executable) for secondary structure and accessibility.

## Dependencies

- `biopython` (>= 1.79)
- `numpy` (>= 1.21)
- Optional: `DSSP` executable (e.g., `mkdssp`, version depends on your system installation)

## Example Usage

Create `config/task_config.json`:

```json
{
  "input_path": "data/1ubq.pdb",
  "format": "pdb",
  "chain_id": "A",
  "atom_name": "CA",
  "distance_cutoff": 8.0,
  "output_path": "outputs/chainA_ca_neighbors.json"
}
```

Create `scripts/neighbor_search.py`:

```python
import json
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser, MMCIFParser, NeighborSearch

def load_structure(input_path: str, fmt: str):
    if fmt.lower() in ("pdb", ".pdb"):
        parser = PDBParser(QUIET=True)
    elif fmt.lower() in ("cif", "mmcif", ".cif", ".mmcif"):
        parser = MMCIFParser(QUIET=True)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    return parser.get_structure("structure", input_path)

def main():
    config_path = Path("config/task_config.json")
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    structure = load_structure(cfg["input_path"], cfg["format"])

    # Use the first model by default
    model = next(structure.get_models())
    chain = model[cfg["chain_id"]]

    # Collect atoms for neighbor search
    all_atoms = list(structure.get_atoms())
    ns = NeighborSearch(all_atoms)

    # Pick a reference atom (first residue in chain that has the requested atom)
    ref_atom = None
    for residue in chain.get_residues():
        if cfg["atom_name"] in residue:
            ref_atom = residue[cfg["atom_name"]]
            break
    if ref_atom is None:
        raise RuntimeError(f"No atom '{cfg['atom_name']}' found in chain {cfg['chain_id']}")

    cutoff = float(cfg["distance_cutoff"])
    neighbors = ns.search(ref_atom.coord, cutoff, level="R")  # residues within cutoff

    results = []
    for res in neighbors:
        # Skip hetero/water if desired; here we keep everything and report identifiers
        res_id = res.get_id()  # (hetflag, resseq, icode)
        results.append(
            {
                "chain_id": res.get_parent().id,
                "resname": res.get_resname(),
                "resseq": int(res_id[1]),
                "icode": (res_id[2] or "").strip(),
            }
        )

    out_path = Path(cfg["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "input_path": cfg["input_path"],
                "reference": {
                    "chain_id": cfg["chain_id"],
                    "atom_name": cfg["atom_name"],
                    "cutoff": cutoff,
                },
                "neighbor_residues": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

if __name__ == "__main__":
    main()
```

Run the script:

```bash
python scripts/neighbor_search.py
```

## Implementation Details

- **Configuration convention**: write runtime parameters to `config/task_config.json` as an intermediate file and invoke scripts via `python scripts/<task_name>.py`. Avoid stacking many CLI `--` arguments; prefer config files.
- **Encoding and JSON output**: all file I/O must explicitly use `encoding="utf-8"`. When writing JSON, use `ensure_ascii=False` to preserve non-ASCII characters.
- **Parsing strategy**:
  - Use `PDBParser(QUIET=True)` for `.pdb`.
  - Use `MMCIFParser(QUIET=True)` for `.cif/.mmcif`.
  - Access hierarchy through iterators (`get_models()`, `get_chains()`, `get_residues()`, `get_atoms()`).
- **Geometry calculations**:
  - Distances are typically computed from atomic coordinates (NumPy arrays) using Euclidean norm, e.g. `np.linalg.norm(a.coord - b.coord)`.
  - Angles/dihedrals can be computed using Bio.PDB vector utilities (e.g., `Bio.PDB.vectors.calc_angle`, `calc_dihedral`) when needed.
- **Neighbor search**:
  - `NeighborSearch(list(structure.get_atoms()))` builds a spatial index over atoms.
  - `search(center, radius, level="A"|"R"|"C"...)` returns neighbors at the requested hierarchy level (atoms, residues, etc.).
- **Scope coverage**:
  - PDB/mmCIF parsing and hierarchical access
  - Distance/angle/dihedral computations
  - Neighbor search and structural quality/annotation (optional DSSP)
  - Structure extraction/saving and superposition (e.g., `Superimposer`)

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
- If a file is produced, prefer a deterministic output name such as `biopython_structure_result.md` unless the skill documentation defines a better convention.
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
Result file: biopython_structure_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
