# Dataset Comparison — A/B Testing Across Dataset Versions

Run structured experiments that compare how an agent performs across different dataset versions, and present results as leaderboards with per-evaluator breakdowns. Use this to answer: "Did scores drop because of harder tests or agent regression?"

## Experiment Structure

An experiment consists of:
1. **Pinned agent version** — the same agent evaluated on each dataset
2. **Varied dataset versions** — the versions being compared
3. **Same evaluators** — applied consistently across all runs
4. **Comparison results** — which dataset version the agent performs better on

## Step 1 — Define the Experiment

| Parameter | Value | Example |
|-----------|-------|---------|
| Agent | Pinned agent version | `v3` |
| Baseline dataset | Previous dataset version | `support-bot-prod-traces-v2` |
| Treatment dataset(s) | New dataset version(s) | `support-bot-prod-traces-v3` |
| Evaluators | Same set for all runs | coherence, fluency, relevance, intent_resolution, task_adherence |

## Step 2 — Run Evaluations

For each dataset version, run **`evaluation_agent_batch_eval_create`** with:
- Same `evaluationId` (groups all runs for comparison)
- Same `agentVersion`
- Same `evaluatorNames`
- Different `inputData` (from each dataset version)

> **Important:** Use `evaluationId` on `evaluation_agent_batch_eval_create` to group runs. After the runs exist, switch to `evalId` for `evaluation_get` and `evaluation_comparison_create`.

> ⚠️ **Eval-group immutability:** Keep the evaluator set and thresholds fixed within one evaluation group. If you need to change evaluators or thresholds, create a new evaluation group instead of reusing the previous `evaluationId`.

> ⚠️ **Score drops are expected.** When comparing v1→v2 datasets, lower scores on the new dataset likely mean the new test cases are harder (better coverage), not that the agent regressed. **Do NOT remove dataset rows or weaken evaluators to recover scores.** Instead, optimize the agent for the new failure patterns, then re-evaluate.

## Step 3 — Compare Results

Use **`evaluation_comparison_create`** with the baseline and treatment runs:

```json
{
  "insightRequest": {
    "displayName": "Dataset comparison: traces-v2 vs traces-v3 on agent-v3",
    "state": "NotStarted",
    "request": {
      "type": "EvaluationComparison",
      "evalId": "<eval-group-id>",
      "baselineRunId": "<traces-v2-run-id>",
      "treatmentRunIds": ["<traces-v3-run-id>"]
    }
  }
}
```

> ⚠️ **Common mistake:** `evaluation_comparison_create` uses `insightRequest.request.evalId`, not `evaluationId`, even when the runs were originally grouped with `evaluationId`.

## Step 4 — Leaderboard

Present results as a leaderboard table:

| Evaluator | traces-v2 (baseline) | traces-v3 | Effect |
|-----------|:---:|:---:|:---:|
| Coherence | 4.0 | 3.6 | ⚠️ Lower |
| Fluency | 4.5 | 4.3 | ⚠️ Lower |
| Relevance | 3.6 | 3.2 | ⚠️ Lower |
| Intent Resolution | 4.1 | 3.7 | ⚠️ Lower |
| Task Adherence | 3.9 | 3.4 | ⚠️ Lower |

### Recommendation

If scores drop uniformly across all evaluators, the new dataset is likely harder:

*"Agent v3 scores dropped on traces-v3 across all evaluators. traces-v3 added 15 edge-case queries from production failures. This is expected — optimize the agent for the new failure patterns rather than reverting the dataset."*

## Pairwise A/B Comparison

For detailed pairwise analysis between exactly two dataset versions:

| Evaluator | Baseline (traces-v2) | Treatment (traces-v3) | Delta | p-value | Effect |
|-----------|:---:|:---:|:---:|:---:|:---:|
| Coherence | 4.0 ± 0.6 | 3.6 ± 0.9 | −0.4 | 0.03 | Degraded |
| Fluency | 4.5 ± 0.4 | 4.3 ± 0.5 | −0.2 | 0.12 | Inconclusive |
| Relevance | 3.6 ± 0.9 | 3.2 ± 1.1 | −0.4 | 0.04 | Degraded |

> 💡 **Tip:** The `evaluation_comparison_create` result includes `pValue` and `treatmentEffect` fields. Use `pValue < 0.05` as the threshold for statistical significance.

## Multi-Dataset Comparison

Compare how the same agent version performs across different datasets:

| Dataset | Coherence | Fluency | Relevance | Notes |
|---------|:---------:|:-------:|:---------:|-------|
| traces-v3 (prod) | 4.0 | 4.5 | 3.6 | Production-derived |
| synthetic-v2 | 4.3 | 4.6 | 4.1 | May overestimate quality |
| manual-v1 (curated) | 3.8 | 4.4 | 3.2 | Hardest test cases |

> ⚠️ **Warning:** Be cautious comparing scores across datasets with different structures (e.g., production traces vs synthetic). Differences may reflect dataset difficulty, not agent quality.

## Next Steps

- **Track trends over time** → [Eval Trending](eval-trending.md)
- **Check for regressions** → [Eval Regression](eval-regression.md)
- **Audit full lineage** → [Eval Lineage](eval-lineage.md)
