# Socratic Story Cartographer

**A Socratic story-development skill for novels, screenplays, scenes, and series outlines.**  
Instead of jumping to a verdict, it runs a loop of competing diagnoses, falsification, counterfactual tests, minimal intervention, and blind re-check to find the highest-leverage problem first.

**New here? [Try the 3-minute first test →](./FIRST-TEST.md)**

## Quick start — no terminal required

If your AI agent can read GitHub and install skills, paste this directly into it:

```text
Install and enable Socratic Story Cartographer from:
https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer

Detect the Skill / Agent Skill installation method for your current harness, install it in the correct place, confirm that it can be discovered, then tell me how to run it. If you do not have filesystem or installation permission, do not pretend it worked; give me the exact manual steps for this environment.
```

Then give the agent a real story, scene, screenplay, or outline and ask it to run up to 3 loops.

## Install with CLI

Install the skill with the cross-agent Skills CLI:

```bash
npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer
```

Then give your agent the story material and ask, for example:

```text
Run Socratic Story Cartographer on this story for 3 loops. Find the highest-leverage issue first, test competing explanations, and do not rewrite until the diagnosis survives falsification and counterfactual checks.
```

## Why this skill is different

Most story-analysis skills can list strengths and weaknesses. This one is designed to **attack its own first diagnosis before recommending a fix** and to stop when another loop no longer changes the working belief.

The v2.1 diagnostic kernel was shaped by a structured 27-condition comparison across literary fiction, a 26-episode series outline, and an episode screenplay. The benchmark is published with its limitations rather than presented as an independent statistical trial.

**[Read the benchmark and methodology →](./BENCHMARK.md)**

## Why a Skill instead of one good prompt?

For one short scene, a carefully written prompt may be enough. A Skill becomes more useful when you want the same review discipline to survive across long works, repeated revisions, and producer handoffs.

Version 2.2 routes long or multi-file work through dedicated reference protocols before it makes work-wide claims. Those protocols require source coverage, distinguish unread material from true absence, preserve locked/protected elements, and compile supported findings into producer-facing decisions and revision task cards. The goal is not to make the model magically smarter; it is to make the review process **repeatable, inspectable, and harder to shortcut** than a one-off critique prompt.

That claim is testable. Compare the same model on the same unseen material with one strong prompt versus this Skill, then check whether the Skill more reliably anchors evidence, updates its diagnosis, notices regression risk, and stops when another loop adds no information.

**[Run the public Skill-vs-prompt A/B protocol →](./AB-TEST.md)**

**External tester? [Report the result in the public feedback thread →](https://github.com/OakcoderX/awesome-agent-skills/pull/1)**

The baseline in that protocol is intentionally strong. If the Skill does not show a repeatable advantage on the long-work tasks it claims to improve, treat that as a product problem rather than a marketing problem.

## What it is good at

- **Novel / short fiction:** distinguish author intent from what the text actually produces; protect ambiguity, voice, restraint, and residue while finding the smallest useful revision.
- **Screenplay / episode:** diagnose protagonist choice, scene engine, causality, information release, state change, and where the series engine actually starts.
- **Series outline / treatment:** test story-engine causality, escalation, competing explanations, and phase transitions; v2.2 adds long-work coverage controls and a producer-facing decision/task-card mode.
- **Benchmark mode:** after diagnosis, compare a work against a target level without pretending editorial or commercial acceptance can be predicted precisely.

## The loop

`Observe → Compete → Attack → Locate → Intervene → Re-test → Update`

Default: **3 loops**. A requested loop count is a maximum, not an obligation: if a new loop produces no belief update or better intervention, the skill stops early.

Every root-level diagnosis must be anchored to concrete textual evidence. Important changes are checked for regression so that solving one problem does not accidentally destroy a stronger quality already working in the story.

## Quick prompts

**Novel**
```text
Run 3 loops on this short story. Separate author intent from text reality and find the single issue most likely to limit its ceiling. Preserve ambiguity and restraint.
```

**Screenplay**
```text
Run 3 loops on this episode. Find the most causally upstream problem before suggesting edits. Test whether protagonist choices actually create the next problem.
```

**Series outline**
```text
Run 3 loops on this season outline. Identify the story engine, attack your diagnosis with falsification and counterfactual tests, then tell me whether to stop, locally revise, or structurally rebuild.
```

**Producer review**
```text
Review this full-season outline for a producer decision. Verify coverage across the complete material, trace each major problem from first appearance to visible failure, and compile an actionable revision plan without treating the review as human approval.
```

## Version

**2.2** — adds producer-outline review and long-work evidence coverage while preserving the v2.1 diagnostic kernel.

Author: **Solopup.co**

## Documentation

- [3-minute first test](./FIRST-TEST.md)
- [Skill vs prompt A/B test](./AB-TEST.md)
- [Benchmark](./BENCHMARK.md)
- [English](./README.en.md)
- [中文](./README.zh.md)
- [Runtime specification](./SKILL.md)