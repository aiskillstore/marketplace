---
name: fit-scorer
slug: fit-scorer
displayName: "Fit Scorer · 红人适配评分"
summary: "用 typed C3 ACE 评估创作者，并将活动商业适配度作为独立矩阵排序"
description: 'Use when the user asks to "score this influencer", "rank these creators for our campaign", or "tell me which influencer is the best fit"; produces typed C3 ACE creator results plus a separately labeled campaign-fit ranking without mixing brand fit into ACE. Not for finding new influencers — use influencer-discovery; not for sending outreach — use outreach-manager.'
version: "17.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a user has a shortlist of influencers and needs an objective, weighted score to prioritize outreach, choose between candidates, justify a selection to stakeholders, set consistent evaluation standards, compare creators across niches or platforms, or build long-term partner tiers. Activates on requests like score @handle for our brand, compare and rank these creators, or which of these is the best fit."
argument-hint: "<brand or campaign> <influencer handle(s)> [campaign goal: awareness|engagement|conversion]"
metadata: {"author": "aaron-he-zhu", "version": "17.0.0", "discipline": "influencer", "phase": "discover", "family": "influencer-marketing", "hermes": {"tags": ["marketing", "influencer", "discover"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Fit Scorer

Score each shortlisted creator on the typed C3 ACE creator rubric, then keep campaign-specific commercial fit in a separate prioritization matrix. The ACE result is portable and brand-independent; the commercial matrix is not an ACE score and never enters CVI.

## Quick Start

Score one influencer:

```
Score @[handle] for [brand/campaign] and tell me if they're a good fit
```

Compare and rank a shortlist:

```
Compare and rank these influencers for [campaign]: @influencer1, @influencer2, @influencer3
```

## Skill Contract

- **Reads**: brand/campaign context, target audience definition, campaign goal, and a shortlist of influencer handles (supplied by the user or carried over from `influencer-discovery`). Optional prior audience profiles from `memory/influencer/audience-mapper/` and competitor partner benchmarks from `memory/influencer/competitor-tracker/`. For rostered creators, read partnership history and audience-stat provenance from `memory/creators/<handle-slug>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) roster record — as Partnership Potential inputs.
- **Writes**: only with explicit authorization, a report containing typed ACE results plus a separately labeled commercial-fit comparison at `memory/influencer/fit-scorer/YYYY-MM-DD-<topic>.md`.
- **Promotes**: only with separate authorization, evidence-backed top picks and their exact ACE profile/version; never promote an unscored or provisional result.
- **Done when**:
  - Every creator has all 12 ACE items explicitly Pass/Partial/Fail/Unknown/N/A with dated evidence or a gap reason.
  - The exact `ace-<goal>` profile/context and deterministic scorer result are preserved; Unknown prevents an ACE total.
  - Any commercial-fit ranking is visibly separate from ACE and cannot override a veto or missing evidence.
- **Primary next skill**: [competitor-tracker](../../plan/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already partner with.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). Fit Scorer works end to end by asking the user for the inputs it scores — handles, audience targets, brand values, and any metrics they have. A connector sharpens the numbers but none is required.

- `~~influencer database` — follower counts, audience demographics, and partnership history.
- `~~social platform analytics` — engagement rate, comment quality samples, posting cadence, growth trend.
- `~~audience intelligence` — real-vs-bot follower estimates and audience overlap with your target.
- **Roster record (keyless Tier 1)** — prior contact, response reputation, and delivery history come from `memory/creators/<handle-slug>.md` when the creator is rostered ([creator-registry](../../../protocol/creator-registry/SKILL.md) curates it); `~~CRM` is an optional Tier-2 sharpener for the same history when no roster record exists.

**Measured YouTube inputs (free key)**: for YouTube candidates, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" videos @handle --limit 10` supplies the engagement-authenticity inputs directly — per-video views/likes/comments against the displayed subscriber base (views-to-subs consistency, comment rate, cadence) — so those sub-scores come from **Measured** numbers instead of screenshots. Free `YOUTUBE_API_KEY`; shortlist vetting only (ToS refuses bulk-harvesting quota). See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

With zero integrations, ask the user to supply each value the scoring tables request; the framework and weighting still produce a defensible ranking. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

The commercial comparison layouts live in [references/scoring-templates.md](references/scoring-templates.md). They are optional decision support, not the C3 rubric.

1. **Lock typed context.** Declare creator target/version, goal (`awareness|engagement|conversion|brand-building`), profile `ace-<goal>`, `scope: ace`, `assessment_time: forecast|actual`, shared campaign `rollup_id`, observation date, platform/tier/niche cohort, and evidence window. Profile scope/goal must match context.
2. **Freeze evidence.** Use creator analytics, public observations, roster history, and cohort benchmarks with source/date/type/confidence. Missing or refused private access is Unknown, never Fail or Partial.
3. **Score ACE only.** Evaluate A1-A4 Audience, C1-C4 Credibility, and E1-E4 Engagement from [ace-creator-benchmark.md](../../../references/c3/ace-creator-benchmark.md). Creator-brand fit, exclusivity conflict, cost, and campaign conversion belong to ROI.O/I, not ACE.
4. **Verify critical failures.** `C3-ACE.A2` fails only on verified real-follower rate below 70%; `C3-ACE.C1` on verified disqualifying conduct; `C3-ACE.E2` on verified bought/pod engagement. One verified veto yields `DONE_WITH_CONCERNS/FIX` and `final=min(raw,59)`; two or more yield `DONE/BLOCK` with no final score. Operationally hold outreach while a critical issue remains, but do not relabel the typed verdict.
5. **Run the deterministic scorer.** Follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, verify the scorer and typed catalog, then execute `python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score <run.json>`. If the standalone install lacks them, return `score_state: NOT_SCORED` / `score_confidence: not_scored`; do not hand-calculate a total, verdict, or persistent artifact.
6. **Build the separate commercial matrix when requested.** Use audience-to-campaign fit, content style, campaign-specific brand/category fit, commercial terms, availability, and partnership potential. Label its 1-5 total `commercial_fit_score`; it is not ACE, cannot clear an ACE veto, and never enters CVI.
7. **Rank transparently.** Show ACE profile/result (or coverage/interval), critical controls, commercial fit separately, evidence confidence, and an outreach recommendation with owner/rerun condition. Do not rank an Unknown-heavy candidate as definitively superior.
8. **Persist only with permission.** Save the report only after authorization; request separate authorization before any hot-cache promotion or creator-registry proposal.

## Compact Example

**User**: "Compare @ecofashionista, @greenwardrobe, @sustainablesarah for our sustainable fashion brand (goal: conversion)."

**Output**: Each creator receives a typed `ace-conversion` result using the same campaign `rollup_id`; the separate commercial matrix explains brand/category fit and terms. A verified 55% real-follower result fails A2 and caps one-veto ACE at 59, while refused access stays Unknown and prevents a total. Persistence is offered, not assumed.

## Reference Materials

- [references/scoring-templates.md](references/scoring-templates.md) — all per-dimension tables, final-score rollup, comparison report, custom-weighting matrix, worked example, and tips.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Scoring rubric: [c3-benchmark.md](../../../references/c3-benchmark.md) (CVI rollup), [c3/ace-creator-benchmark.md](../../../references/c3/ace-creator-benchmark.md) (the ACE Creator rubric this skill emits, incl. A2/C1/E2 veto items), [c3/scoring-architecture.md](../../../references/c3/scoring-architecture.md) (weighting and cap methodology).
- Sibling skills: [influencer-discovery](../influencer-discovery/SKILL.md), [competitor-tracker](../../plan/competitor-tracker/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md), [outreach-manager](../../activate/outreach-manager/SKILL.md).

## Next Best Skill

**Primary**: [competitor-tracker](../../plan/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already work with before you commit budget.

**Alternates** (same discover phase):
- [influencer-discovery](../influencer-discovery/SKILL.md) — if the shortlist is too thin to rank, source more candidates.
- [audience-mapper](../audience-mapper/SKILL.md) — if audience-match scores are uncertain, tighten the target-audience definition first.

**Termination note**: Track a visited-set of skills invoked this session. If the recommended next skill has already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops (max-depth 3) and hand back to the user with the saved report path.

## Related Skills

- [influencer-discovery](../influencer-discovery/SKILL.md) - Find influencers to score
- [competitor-tracker](../../plan/competitor-tracker/SKILL.md) - Benchmark against competitor partners
- [audience-mapper](../audience-mapper/SKILL.md) - Define target audience
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact top-scored influencers
