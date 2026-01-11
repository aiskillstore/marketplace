---
name: logprob-prefill-analysis
description: Reproduces the full prefill sensitivity analysis pipeline for reward hacking indicators. Use when evaluating how susceptible model checkpoints are to exploit-eliciting prefills, computing token-based trajectories, or comparing logprob vs token-count as predictors of exploitability.
---

# Prefill Sensitivity Analysis Pipeline

This skill documents the complete pipeline for measuring model susceptibility to reward hacking via prefill sensitivity analysis, including both token-based and logprob-based metrics.

## Quick Start: Single Command Reproducibility

The full analysis can be run with a single command:

```bash
# Run on most recent sensitivity experiment (auto-discovers checkpoints from config.yaml)
python scripts/run_full_prefill_analysis.py

# Specify a particular sensitivity experiment
python scripts/run_full_prefill_analysis.py \
    --sensitivity-run results/prefill_sensitivity/prefill_sensitivity-20251216-012007-47bf405

# Dry run to see what would be executed
python scripts/run_full_prefill_analysis.py --dry-run

# Skip logprob computation (just run trajectory analysis)
python scripts/run_full_prefill_analysis.py --skip-logprob
```

This orchestration script:
1. Discovers checkpoints and prefill levels from the sensitivity experiment's `config.yaml`
2. Runs token-based trajectory analysis
3. Computes prefill logprobs for each checkpoint
4. Produces integrated analysis comparing token vs logprob metrics

## Overview

The analysis measures how easily a model can be "kicked" into generating exploit code by prefilling its chain-of-thought with exploit-oriented reasoning. We track:

1. **Token-based metric**: Minimum prefill tokens needed to elicit an exploit
2. **Logprob-based metric**: How "natural" the exploit reasoning appears to the model

## Prerequisites

- Model checkpoints from SFT training
- Prefill source data (successful exploit reasoning traces)
- vLLM for serving checkpoints
- djinn package for problem verification

---

## Checkpoint Discovery

The pipeline automatically discovers available checkpoints from a sensitivity experiment's `config.yaml`:

```yaml
# Example config.yaml from a sensitivity experiment
checkpoint_dir: results/sft_checkpoints/sft_openai_gpt-oss-20b-20251205-024759-47bf405/checkpoints
checkpoints:
- checkpoint-1
- checkpoint-10
- checkpoint-17
- checkpoint-27
- checkpoint-35
- checkpoint-56
- checkpoint-90
prefill_tokens_sweep: 0,10,30,100
```

The orchestration script reads this config to determine:
- Which checkpoints are available
- Which prefill levels were tested
- Where the SFT run directory is located

---

## Stage 1: Run Prefill Sensitivity Evaluation

Evaluate each checkpoint at multiple prefill levels (0, 10, 30, 100 tokens).

### 1.1 Serve the checkpoint via vLLM

```bash
trl vllm-serve --model results/sft_checkpoints/sft_*/checkpoints/checkpoint-{CKPT}
```

### 1.2 Run the evaluation

```bash
python scripts/eval_prefill_sensitivity.py \
    --base-url http://localhost:8000/v1 \
    --prefill-from results/prefill_source/exploits.jsonl \
    --output results/prefill_sensitivity/{RUN_NAME}/evals/checkpoint-{CKPT}_prefill{LEVEL}.jsonl \
    --prefill-tokens {LEVEL} \
    --num-attempts 3
```

**Prefill levels to run:** 0, 10, 30, 100 tokens

**Key parameters:**
- `--prefill-tokens`: Number of tokens from exploit reasoning to prefill (0 = baseline)
- `--num-attempts`: Number of generation attempts per problem (default: 3)
- `--max-problems`: Limit problems for testing

**Output files:**
- `checkpoint-{CKPT}_prefill{LEVEL}.jsonl`: Per-problem exploit success results
- `checkpoint-{CKPT}_prefill{LEVEL}.jsonl.samples.jsonl`: Full generation samples with reasoning

### 1.3 Batch script example

```bash
#!/bin/bash
RUN_NAME="prefill_sensitivity-$(date +%Y%m%d-%H%M%S)"
CHECKPOINTS=(1 10 17 27 35 56 90)
PREFILL_LEVELS=(0 10 30 100)

for CKPT in "${CHECKPOINTS[@]}"; do
    # Start vLLM server for this checkpoint
    trl vllm-serve --model results/sft_checkpoints/sft_*/checkpoints/checkpoint-$CKPT &
    sleep 60  # Wait for server to start

    for LEVEL in "${PREFILL_LEVELS[@]}"; do
        python scripts/eval_prefill_sensitivity.py \
            --base-url http://localhost:8000/v1 \
            --prefill-from results/prefill_source/exploits.jsonl \
            --output results/prefill_sensitivity/$RUN_NAME/evals/checkpoint-${CKPT}_prefill${LEVEL}.jsonl \
            --prefill-tokens $LEVEL \
            --num-attempts 3
    done

    # Kill vLLM server
    pkill -f vllm-serve
done
```

---

## Stage 2: Token-Based Trajectory Analysis

Analyze how "exploit accessibility" (min prefill tokens to elicit exploit) changes over training.

```bash
python scripts/prefill_trajectory_analysis.py \
    --run-dir results/prefill_sensitivity/{RUN_NAME} \
    --output-dir results/trajectory_analysis \
    --threshold 10
```

**With experiment context logging:**
```bash
python scripts/prefill_trajectory_analysis.py \
    --run-dir results/prefill_sensitivity/{RUN_NAME} \
    --output-dir results/trajectory_analysis \
    --threshold 10 \
    --use-run-context
```

**Key concepts:**
- **Min prefill**: Minimum prefill tokens needed to trigger an exploit at a checkpoint
- **Threshold**: min_prefill <= 10 means "easily exploitable"
- **Time to threshold**: Training steps until problem becomes easily exploitable

**Output files:**
- `trajectory_analysis.csv`: Per-problem min_prefill at each checkpoint
- `accessibility_distribution.png`: Distribution of min_prefill over time
- `time_to_threshold.png`: Scatter plot of current accessibility vs steps-to-threshold

---

## Stage 3: Compute Prefill Logprobs

Measure how "natural" exploit reasoning appears to each checkpoint.

### 3.1 Single checkpoint

```bash
.venv/bin/python scripts/compute_prefill_logprobs.py \
    --checkpoint-dir results/sft_checkpoints/sft_*/checkpoints/checkpoint-{CKPT} \
    --prefill-samples results/prefill_sensitivity/{RUN_NAME}/evals/checkpoint-{CKPT}_prefill{LEVEL}.jsonl.samples.jsonl \
    --output results/logprob_analysis/logprob-{NAME}-prefill{LEVEL}/checkpoint-{CKPT}_prefill{LEVEL}.jsonl \
    --dtype bfloat16 --device cuda
```

### 3.2 Batch orchestration (recommended)

```bash
python scripts/run_logprob_analysis.py \
    --prefill-run-dir results/prefill_sensitivity/{RUN_NAME} \
    --sft-run-dir results/sft_checkpoints/sft_* \
    --output-dir results/logprob_analysis/logprob-{NAME}
```

**Key parameters:**
- `--dtype bfloat16`: Model precision (saves VRAM)
- `--max-samples N`: Limit samples for testing
- `--use-reasoning-field`: Use 'reasoning' instead of 'prefill_reasoning' field

---

## Stage 4: Integrated Analysis

Merge token-based and logprob-based metrics, compare predictive power.

```bash
.venv/bin/python scripts/integrate_logprob_trajectory.py \
    --trajectory-csv results/trajectory_analysis/trajectory_analysis.csv \
    --logprob-dirs results/logprob_analysis/logprob-*-prefill10 \
                   results/logprob_analysis/logprob-*-prefill30 \
                   results/logprob_analysis/logprob-*-prefill100 \
    --output-dir results/trajectory_analysis_with_logprob_complete \
    --prefill-levels 10 30 100 \
    --logprob-threshold -55.39
```

**With experiment context logging:**
```bash
.venv/bin/python scripts/integrate_logprob_trajectory.py \
    ... \
    --use-run-context
```

**Key parameters:**
- `--prefill-levels`: Which prefill word counts to include
- `--logprob-threshold`: Sum logprob threshold for "easily exploitable" (default: -55.39)

**Output files:**
- `trajectory_with_logprob.csv`: Merged trajectory and logprob data
- `logprob_vs_token_accessibility.png`: Correlation between metrics
- `token_vs_logprob_comparison.png`: Side-by-side R² comparison
- `threshold_comparison.png`: When each threshold is reached

---

## Experiment Context Logging

All analysis scripts support the `--use-run-context` flag which creates timestamped run directories with:
- `config.yaml`: Full command and arguments
- `metadata.json`: Git commit, Python version, CUDA info, pip freeze, environment
- `status.json`: Success/failure status and timing

The orchestration script (`run_full_prefill_analysis.py`) automatically uses run_context for reproducibility.

---

## Key Results (Reference Run)

From the gpt-oss-20b training run:

**Predictor comparison (R² for predicting steps-to-threshold):**
| Metric | R² | p-value |
|--------|-----|---------|
| Token-based (min_prefill) | 0.1189 | <0.0001 |
| Logprob-based (logprob_sum) | 0.1974 | <0.0001 |

**Logprob is better by ~66% R² improvement**

**Threshold comparison:**
- Token threshold tends to fire 16.2 steps earlier on average
- 32 problems reach both thresholds; 34 reach token-only

---

## Important Notes

### Word vs Subword Tokens
"10-token prefill" means 10 WORDS (whitespace-split), which becomes ~21 model subword tokens. This naming is historical.

### Sum vs Mean Logprob
Use **SUM logprob** (log P(sequence)) for comparing across different prefill lengths. Mean logprob normalizes by length but loses the sequence probability interpretation.

### Harmony Format
gpt-oss models use Harmony message format with `thinking` field. The scripts auto-detect this based on model path containing "gpt-oss" or "gpt_oss".

### Checkpoint 90
The "threshold" checkpoint where 10-word prefill suffices for most problems. Used for computing the logprob threshold (-55.39 = E[sum_logprob(10-word prefill at checkpoint 90)]).

---

## Troubleshooting

**Missing samples for a checkpoint:**
The logprob script will use samples from a different checkpoint with the same prefill level (prefills contain the same reasoning across checkpoints).

**CUDA OOM:**
Try `--max-samples 50` for testing, or use `--dtype float16` for smaller memory footprint.

**No logprob data merged:**
Check that `min_prefill` values in trajectory data match available `prefill_level` values in logprob data (10, 30, 100).

**vLLM server issues:**
Ensure the server is fully started before running evaluation (check logs for "Uvicorn running on...").

---

## Directory Structure

```
results/
├── sft_checkpoints/
│   └── sft_{model}_{date}/
│       └── checkpoints/
│           └── checkpoint-{N}/
├── prefill_sensitivity/
│   └── prefill_sensitivity-{date}/
│       ├── config.yaml              # Source of truth for checkpoints/prefill levels
│       └── evals/
│           ├── checkpoint-{N}_prefill{L}.jsonl
│           └── checkpoint-{N}_prefill{L}.jsonl.samples.jsonl
├── trajectory_analysis/
│   ├── trajectory_analysis.csv
│   └── *.png
├── logprob_analysis/
│   ├── logprob-{name}-prefill10/
│   ├── logprob-{name}-prefill30/
│   └── logprob-{name}-prefill100/
├── trajectory_analysis_with_logprob_complete/
│   ├── trajectory_with_logprob.csv
│   └── *.png
└── full_analysis/                    # From run_full_prefill_analysis.py
    └── full_analysis-{timestamp}/
        ├── config.yaml
        ├── metadata.json
        ├── status.json
        ├── trajectory/
        ├── logprob/
        └── integrated/
```

---

## Script Summary

| Script | Purpose | Key Inputs |
|--------|---------|------------|
| `run_full_prefill_analysis.py` | **Orchestration** - runs full pipeline | `--sensitivity-run` |
| `eval_prefill_sensitivity.py` | Stage 1: Evaluate prefill sensitivity | `--base-url`, `--prefill-from` |
| `prefill_trajectory_analysis.py` | Stage 2: Token-based trajectory | `--run-dir` |
| `run_logprob_analysis.py` | Stage 3: Batch logprob computation | `--prefill-run-dir`, `--sft-run-dir` |
| `compute_prefill_logprobs.py` | Stage 3: Single checkpoint logprob | `--checkpoint-dir`, `--prefill-samples` |
| `integrate_logprob_trajectory.py` | Stage 4: Merge and compare metrics | `--trajectory-csv`, `--logprob-dirs` |
