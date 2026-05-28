# Confidence and Limitations

## Confidence Scoring
DiffDock includes a confidence model that estimates the quality of the generated poses.
- **Score Meaning**: The score correlates with the likelihood of the pose being correct (RMSD < 2Å).
- **Not Affinity**: The score is **NOT** a binding affinity prediction (e.g., Kd, Ki). It is a structural confidence score.

## Limitations
1.  **Blind Docking**: While DiffDock specializes in blind docking, providing a known pocket can improve results (if the model supports focused sampling).
2.  **Cofactors**: Standard DiffDock may not explicitly model cofactors (heme, metal ions) unless they are part of the protein graph input.
3.  **Flexibility**:
    - **Ligand**: Fully flexible.
    - **Protein**: Treated as a rigid graph during diffusion, though the embedding captures some features. Side-chain flexibility is implicitly handled but not explicitly sampled.
4.  **Complex Size**: Very large complexes may run out of GPU memory.

## Accuracy
- **State-of-the-Art**: As of 2023, DiffDock achieves top performance on the PDBBind benchmark for blind docking.
- **Failures**: It may fail for highly flexible proteins or large conformational changes upon binding.
