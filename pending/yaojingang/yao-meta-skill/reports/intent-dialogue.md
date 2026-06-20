# Intent Dialogue

Skill: `yao-meta-skill`

## Opening Frame

Let's start from the real work, the result you care about, and the standards that matter here. We can make the structure clearer after that.

## Opening Tone Options

### 温柔陪伴型

- Best when: 用户想法还散、还在试探，或者需要先被接住。
- Example: 我们先不急着把它说成一个很完整的 skill。你就像跟我聊天一样，先说说你最想让它以后稳稳接住哪类重复工作；如果它做得很理想，最后应该交回你一个什么结果。

### 专业教练型

- Best when: 用户目标比较明确，希望被高效带着走。
- Example: 我们先把这件事讲清楚，再决定 skill 怎么设计。你先告诉我三件事：它要接住的重复任务是什么，别人通常会给它什么材料，最后你希望它交付什么结果。

### 共创伙伴型

- Best when: 用户已经有一些想法，希望一起打磨，不想被填表。
- Example: 我们把这次当成一次共创。你先给我一个粗糙版本就行，我先帮你看它真正的核心任务是什么，再一起决定边界、结构和接下来最值的一步。

## Conversation Path

1. Start with the user's own words, not package vocabulary.
2. Reflect the job, output, and non-goals back in one clean sentence.
3. Only then offer a tiny scaffold if it would help the user move faster.

## Why Start Here

Use this short dialogue before deep authoring. The goal is to learn the real job, output, exclusions, and constraints so the first package is small but accurate.

## Current Anchor

- Title: `Yao Meta Skill`
- Description: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.
- Focus: `portability-and-contract`
- Reference note: If you already have examples you admire, bring them in. We will learn the pattern, not copy the source.

## Questions To Ask

1. If this skill worked beautifully, what recurring job would it reliably handle for the user every time?
   Why: This reveals the real job-to-be-done and gives the package a humane center instead of a guessed prompt shape.
2. When someone reaches for this skill in the real world, what materials will they actually hand to it?
   Why: Input shape decides whether references, scripts, or templates are needed.
3. What finished output should it hand back so the user can immediately keep moving?
   Why: Outputs should drive the package structure before extra guidance is added.
4. Which nearby requests should this skill politely refuse so the boundary stays clean?
   Why: The exclusion list is the fastest route to better trigger quality.
5. What matters most here: speed, consistency, auditability, portability, governance, or tone/style fit?
   Why: Constraints decide how much structure, packaging, and review the skill actually needs.
6. Do you already have any references you want this skill to learn from, such as a repo, product, page, workflow, or prompt example?
   Why: A good reference can raise the quality bar quickly, but the skill should only borrow patterns and standards, never copy wording or confidential material.
7. Which environments or clients must be able to consume this skill?
   Why: This sets the minimum metadata and degradation strategy.

## Capture Before Drafting

- Capability sentence: Yao Meta Skill should turn a recurring request into a reliable reusable output without widening the boundary unnecessarily.
- Recommended first gate: `portability and contract`
- Tiny optional scaffold:
  - The repeated job it should reliably handle
  - The real inputs people will hand to it
  - The useful output it should hand back
  - What it should clearly refuse
- Capture: `recurring job`
- Capture: `real inputs`
- Capture: `required outputs`
- Capture: `exclusions`
- Capture: `constraints`
- Capture: `reference preferences`
- Capture: `first evaluation target`
