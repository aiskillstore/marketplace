---
name: diffdock-molecular-docking
description: Diffusion-based molecular docking to predict 3D ligand–protein binding poses (blind docking) with confidence scoring; use when you need pose prediction for drug discovery or virtual screening.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# DiffDock Molecular Docking

## When to Use

- **Blind docking** when you have a protein structure (PDB) and a ligand (SMILES) but no known binding site.
- **Pose prediction** to generate multiple plausible 3D binding conformations and rank them.
- **Virtual screening support** to quickly evaluate candidate ligands by predicted binding poses and confidence.
- **Drug discovery workflows** where you need automated docking outputs (SDF poses + scores) for downstream analysis.
- **Batch/advanced docking** when running many ligand–protein pairs or using alternative inputs (e.g., sequence-based workflows; see `references/workflows_examples.md`).

## Key Features

- **Diffusion generative sampling** to produce diverse ligand binding poses.
- **Confidence model scoring** to rank predicted poses.
- **Simple CLI inference** for single protein–ligand docking.
- **Batch/advanced workflows** documented in `references/workflows_examples.md`.
- **Structured outputs** including ranked SDF pose files and a confidence score report.

## Dependencies

- Python (version not specified)
- PyTorch (version not specified)
- PyTorch Geometric / PyG (version not specified)
- RDKit (version not specified)
- ESM (version not specified)

## Example Usage

### 1) Verify the Environment

```bash
python scripts/setup_check.py
```

### 2) Run Standard Inference (Single Docking)

Dock a single ligand (SMILES) to a protein structure (PDB) and write results to an output directory:

```bash
python scripts/inference_runner.py \
  --protein ./data/protein.pdb \
  --ligand "CC(=O)Oc1ccccc1C(=O)O" \
  --out_dir ./results
```

**Arguments**
- `--protein`: Path to the protein PDB file.
- `--ligand`: Ligand SMILES string.
- `--out_dir`: Output directory (default: `results/`).

### 3) Outputs

After inference, the tool produces:

- **Ranked SDF pose files** (e.g., `rank1.sdf`, `rank2.sdf`, ...), each containing a predicted 3D binding pose.
- **Confidence score report**: `confidence_scores.txt`, listing the score for each ranked pose.

## Implementation Details

- **Pose generation**: Uses a diffusion-based generative model to sample multiple candidate ligand poses relative to the protein target.
- **Ranking**: A separate confidence model assigns a score to each sampled pose; poses are sorted by this score and saved as `rank*.sdf`.
- **Parameterization**:
  - For the complete CLI argument list and defaults, see `references/parameters_reference.md`.
  - For confidence interpretation, known limitations, and expected accuracy/scope, see `references/confidence_and_limitations.md`.
- **Advanced workflows**: Batch processing and alternative input configurations are documented in `references/workflows_examples.md`.