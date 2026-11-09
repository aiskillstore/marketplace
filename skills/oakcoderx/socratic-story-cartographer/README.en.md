# Socratic Story Cartographer

## Overview

A creator-oriented narrative diagnostic skill that uses Socratic questioning to support first-pass reading of fiction.
It is designed for novels, screenplays, scenes, and multi-episode outlines.

Version: 2.2
Author: Solopup.co

The goal is not to give a final verdict, but to identify the highest-leverage story issues and the next correction that can be tried first.

## Discoverability

### Search keywords

**Primary tags:** Socratic questioning, narrative diagnosis, screenplay evaluation, outline triage, novel diagnosis, script readiness, root-cause intervention, 3-loop review, blind re-check.

### Retrieval phrases for AI or search

- `Socratic Story Loop`
- `story triage for novel`
- `screenplay production review`
- `how to diagnose a TV series outline`
- `3-loop socratic analysis`

## Origin

The concept was inspired by Li Feifei’s point that Socratic questioning, when used early, can reduce uncertainty faster than immediate assertions.

I also used this approach in my own writing workflow and applied it to first-pass reviews of novels and scripts.

## What this version improves

- Automatic input type classification: Novel / Screenplay / Outline / Scene / Mixed / Unclear.
- Story-facing output language: goals, obstacles, choices, stakes, causality, and consequences.
- Fixed loop for fast diagnosis and re-checking.
- Long-work source manifests and coverage ledgers that prevent partial reading from becoming a work-wide claim.
- Producer decision pages, issue routes, hard-error lists, and executable revision task cards for full-season or multi-episode outlines.
- Explicit authority boundaries: an AI review, score, or validation pass is not human approval or canon promotion.

## Loop structure (default 3 loops)

Each loop follows:

1. Observe
2. Generate 2–3 competing interpretations
3. Test the strongest interpretation with:
   - one falsification test
   - one counterfactual test
4. Choose the leverage point (root-cause first)
5. Suggest interventions
   - minimal option
   - optional alternative
6. Predict consequences
7. Ask at most 1–2 key questions when needed
8. Blind re-check and update belief

## Output shape

Each loop outputs:

- Current belief
- Competing diagnosis
- Test design
- Leverage point
- Intervention suggestion(s)
- Expected consequence
- Regression check
- Open uncertainty
- Optional author questions (if needed)

Final pass includes:

- What the story is currently centered on
- What was changed and why
- Remaining risks
- Top 3 follow-up fixes (priority order)
- Continue / stop recommendation

## What to include in one request

For best results, include three things:

1) The text to evaluate (one novel chapter, one scene, one episode, or one outline block)
2) Your goal (`first-pass`, `benchmark`, `minimum intervention`, `series triage`)
3) Boundaries (`no rewrite`, `minimal edits only`, or `structure can change`)

If objective and boundaries are not given, the skill infers them, but explicit constraints improve stability.

## Example prompts

- `Run 3 loops on this series outline and give me the highest-leverage production risk first.`
- `Review this full-season outline for a producer decision. Verify complete coverage, trace each major issue to its onset, and compile revision task cards.`
- `Diagnose this screenplay scene only. Do not rewrite yet. Just locate what a minimal next edit should target.`
- `Use benchmark mode and tell me whether this novel chapter reaches serious submission-level quality for [target].`

Typical output always stays practical:

- current belief
- evidence anchors
- competing diagnosis
- leverage point
- minimal intervention + alternatives
- expected gain / possible loss
- open uncertainty and next question (if needed)

## Scope and constraints

- No guarantee of acceptance labels (no “greenlight/reject” verdicts).
- No replacement for human legal, rights, or production decisions.
- No full rewrite mode.
- No invention of missing facts, motivations, or plot events.

## Suggested skill name

**Socratic Story Cartographer**  
Repository name: `socratic-story-cartographer`

Use this skill when you want:

- fast first-pass reading
- precise producer triage
- smallest useful intervention suggestions
