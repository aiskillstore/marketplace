# Tutorial outline template

Fill this skeleton in order. Anything that doesn't serve the learning objective gets deleted rather than shortened.

## Table of Contents

- [Size limits](#size-limits)
- [Skeleton](#skeleton)
- [What you'll build](#what-youll-build)
- [Background](#background)
- [Before you begin](#before-you-begin)
- [Step 1: <imperative verb phrase>](#step-1-imperative-verb-phrase)
- [Step 2: <imperative verb phrase>](#step-2-imperative-verb-phrase)
- [Checkpoint: <what is now true>](#checkpoint-what-is-now-true)
- [Step 5: <imperative verb phrase>](#step-5-imperative-verb-phrase)
- [What you built](#what-you-built)
- [Troubleshooting](#troubleshooting)
- [Where to go next](#where-to-go-next)
- [Section rules](#section-rules)

## Size limits

The first three come from the Good Docs Project's tutorial template guide and can be quoted as such; the readings after each dash are this skill's.

- 15-60 minutes end to end (sourced). Under 15, it's a quickstart; over 60, split it at a checkpoint into an ordered pair.
- At most seven primary steps (sourced: "avoid writing procedures that are more than seven primary steps long"). A ladder that needs more rungs is two tutorials.
- At most four substeps inside one primary step (sourced).
- One environment: one language, one package manager, one OS family, pinned versions - this skill's rule, following Diátaxis' ban on presenting choices.

## Skeleton

```markdown
# Build <artefact> with <technology>

<One sentence: what the learner will be able to do afterwards.>

|                       |                                      |
| --------------------- | ------------------------------------ |
| **Time**              | 30 minutes (measured, not estimated) |
| **Level**             | <declared audience level>            |
| **You'll need**       | <language/runtime + versions>        |
| **Assumed knowledge** | <concept> (link), <concept> (link)   |

## What you'll build

<Screenshot, sample output, or short description of the finished artefact.>

By the end of this tutorial, you'll be able to:

- <verb the learner performs>
- <verb the learner performs>

## Background

<At most a short paragraph: the feature being learned, or the layout of the starter project. The only place explanation is allowed. Delete it if the tutorial needs none.>

## Before you begin

| Requirement | Version | Check       |
| ----------- | ------- | ----------- |
| <tool>      | <min>   | `<command>` |

Assumed knowledge, with a link each:

- <concept> - <link>

## Step 1: <imperative verb phrase>

<One or two sentences of what and why. No theory.>

<One code block, in the shape the ladder calls for at this stage.>

Expected output:

<Separate block containing real output from a real run.>

## Step 2: <imperative verb phrase>

…

## Checkpoint: <what is now true>

<Command the learner runs.>

<Exact expected output.>

You've now <capability>. If the output differs, see <troubleshooting link> or reset to `<branch/tag/seed command>`.

<Optional> Try it yourself: <variation>. Answer: <link or collapsed block>.

## Step 5: <imperative verb phrase>

…

## What you built

<Complete final artefact, in one block or one linked file, so the learner can diff their work.>

You can now:

- <capability, worded differently from the objectives above>

## Troubleshooting

### <verbatim error message>

**Cause:** <one line.>
**Fix:** <command or edit.>

## Where to go next

- <How-to guide for the most common real-world variant>
- <Reference page for the machinery just used>
- <Explanation page for the why>
```

## Section rules

**Header table.** The time figure comes from a measured cold run, not from the author's estimate. The level line is a contract: it tells an expert to skip and a novice what to read first.

**What you'll build.** Show the end result before the first command. A learner who can picture the destination tolerates a longer path.

**Background.** The Good Docs Project template puts one context section between the overview and the prerequisites, and it is the single place a tutorial tolerates explanation. Use it for the feature under study or the shape of a provided starter project, and keep it to a paragraph - everything past that is the explanation Diátaxis says blocks learning.

**Before you begin.** Two lists, never one: software with a check command, and knowledge with a link. Knowledge prerequisites are what distinguishes a tutorial's preamble from a quickstart's - and omitting them is what makes learners feel stupid instead of unprepared.

**Steps.**

- Verb heading.
- One action.
- One block.
- Real output.
- A fail pointer where the step can realistically fail.

When the learner edits more than two files, show the file tree with the current file marked.

**Checkpoints.** Every 3-5 steps. Never a bare "it should work now" - a command, its exact output, and a way back.

**What you built.** Restate as capabilities the learner has, not topics the page covered. Give the complete artefact so they can find their own typo by diffing.

**Troubleshooting.** Headed by the verbatim error string, so search and Ctrl-F both find it. Two lines each: cause, fix. Anything longer belongs on a dedicated error page.

**Where to go next.** At most three links, one per Diátaxis quadrant. A wall of links at the end is an abandonment surface.
