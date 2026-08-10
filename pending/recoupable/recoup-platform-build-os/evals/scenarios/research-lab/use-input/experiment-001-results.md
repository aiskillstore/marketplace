# Experiment 001 — sparse-attention pretraining (raw writeup)

Date run: 2026-06-21
Owner: Sidney
Research question it addresses: "Does block-sparse attention cut pretraining cost without hurting
downstream accuracy?"

## Setup
- Base model: 160M params, 12 layers.
- Variant: block-sparse attention (block size 64) vs. dense baseline.
- Data: 8B tokens, identical for both runs.
- Eval: held-out perplexity + downstream AUROC on our 3 probe tasks.

## Result
- Sparse run: 31% lower training FLOPs, perplexity within 1.5% of dense.
- Downstream AUROC: dense 0.871, sparse 0.864 — basically a wash.
- Wall-clock: 2.1 days on 4xA100 (sparse) vs 3.0 days (dense).

## Read
Promising — the cost cut is real and the accuracy hit is inside the noise band. Worth a larger-scale
confirmation run before we commit.

## Decisions made here
- We'll report **AUROC** as the primary downstream metric going forward (perplexity secondary).
- Baseline optimizer settings: cosine LR schedule, 5-epoch warmup. Lock this so runs are comparable.

## Next step
Queue experiment 002: same comparison at 410M params. Needs a GPU reservation.
