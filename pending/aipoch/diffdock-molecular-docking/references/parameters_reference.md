# Parameters Reference

## Inference Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--config` | Path to YAML config file containing default args | `default_inference_args.yaml` |
| `--protein_path` | Path to the protein structure file (.pdb) | Required (or sequence) |
| `--protein_sequence` | Amino acid sequence string (if PDB not available) | None |
| `--ligand` | Ligand SMILES string or path to .sdf/.mol2 file | Required |
| `--out_dir` | Directory to save output poses and scores | `results/` |
| `--complex_name` | Name of the complex (for naming outputs) | `complex` |
| `--inference_steps` | Number of denoising steps (diffusion) | 20 |
| `--samples_per_complex` | Number of poses to generate | 10 |
| `--batch_size` | Batch size for inference | 1 |
| `--no_final_step_noise` | Whether to remove noise in the final step | False |

## Model Configuration
* Refer to `model_parameters.yaml` (if present) for deep learning architecture settings (e.g., hidden dimensions, layers).
