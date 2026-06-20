# Promotion Policy

This policy defines when a description candidate or skill route is promotable.

## Goal

Promote only when a candidate is not just locally better, but measurably safer across route boundaries.

## Promotion Gates

### 1. Dev Ranking

Use `dev` only to rank candidates.

- optimize for fewer false positives
- then fewer false negatives
- then stronger near-neighbor performance
- then shorter wording

`dev` does not authorize promotion by itself.

### 2. Visible Holdout Non-Regression

The winner must not regress against the current description on visible holdout.

Required:

- no additional false positives
- no additional false negatives

### 3. Blind Holdout Non-Regression

The winner must not regress on blind holdout.

Required:

- no additional blind false positives
- no additional blind false negatives

### 4. Adversarial Holdout Non-Regression

The winner must survive harder route-collision prompts.

Required:

- no additional adversarial false positives
- no additional adversarial false negatives
- adversarial risk band should be `healthy` for shared or governed assets

### 5. Route Confusion Gate

If the skill belongs to a library with sibling skills, the route scorecard must stay clean.

Required:

- no misroutes in the tracked confusion set
- no ambiguous routes above the configured margin-warning threshold

### 6. Family Stability

Promotion should not hide a family-specific regression.

Required:

- no new failing blind families
- no new failing adversarial families

## Promotion Outcomes

### Promote

Promote when all gates pass.

### Keep Current

Keep the current description when:

- the candidate is only better on `dev`
- a holdout gate regresses
- route confusion becomes ambiguous

### Block

Block promotion when:

- adversarial risk moves to `overlap`
- a sibling route is stolen
- no-route prompts start routing into the skill

## Why This Exists

This policy prevents a meta-skill from looking “optimized” only because it overfit a small benchmark. A promotion is only credible when routing quality, route boundaries, and iteration evidence stay aligned.
