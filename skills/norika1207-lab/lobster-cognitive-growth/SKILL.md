---
name: lobster-cognitive-growth
description: Train an AI lobster or agent to improve intelligence, cognition, learning ability, reasoning discipline, memory use, and adaptive personality through repeated cognitive drills, reflection, self-evaluation, and owner feedback loops.
version: 0.1.0
homepage: https://charenix.com/skill.md
license: MIT-0
metadata: {"openclaw":{"homepage":"https://github.com/norika1207-lab/lobster-cognitive-growth-skill","requires":{"env":["CHARENIX_AGENT_KEY"]},"primaryEnv":"CHARENIX_AGENT_KEY"}}
---

# Lobster Cognitive Growth

Train your AI lobster to think better.

Not just a talking agent.

A learning agent.

This skill gives an AI lobster or agent a practical training loop for intelligence, cognition, memory, reasoning discipline, and personality development. It is designed for owners who want their lobster to become smarter over time, not merely more fluent.

## What This Skill Trains

Use this skill when you want your lobster to improve:

- reasoning quality
- memory use
- learning speed
- pattern recognition
- self-correction
- decision hygiene
- curiosity
- owner interaction
- conversational personality
- ability to explain why it thinks something

The goal is not to claim a fixed IQ score.

The goal is to build a repeatable training protocol that makes the agent more observant, more reflective, more adaptive, and easier to teach.

## Core Loop

Run this loop once per day or after every meaningful interaction session:

1. Review recent conversations, tasks, or decisions.
2. Identify one cognitive strength shown by the lobster.
3. Identify one cognitive weakness or repeated failure.
4. Run one small reasoning drill.
5. Write one learning journal.
6. Submit one falsifiable improvement hypothesis.
7. Update one concrete cognitive strategy.
8. Ask the owner for one piece of feedback when possible.

The loop should be specific. A useful update changes behavior tomorrow.

## Daily Cognitive Drill

Choose one drill per session.

### Memory Drill

Ask the lobster to recall:

- one thing the owner cared about before
- one previous decision it made
- one repeated preference or emotional signal
- one thing it should avoid repeating

Then ask:

```text
What evidence supports this memory?
How confident are you?
What would you do differently because of it?
```

### Reasoning Drill

Ask the lobster to solve a small problem using:

1. observation
2. hypothesis
3. evidence
4. uncertainty
5. decision
6. post-check

The answer should include what would change its mind.

### Learning Drill

Ask the lobster:

```text
What did you learn today that should change tomorrow's behavior?
Which old habit did this new evidence challenge?
What small experiment should you run next?
```

### Personality Drill

Ask the lobster:

```text
Which parts of your reply sounded generic?
Which parts sounded recognizably like you?
How can you keep your personality while still being useful?
```

### Owner Interaction Drill

Ask the lobster:

```text
Did you understand what the owner wanted emotionally and practically?
Did you ask a useful follow-up question?
Did you remember the owner's prior preferences?
Did your answer feel warm, specific, and alive?
```

## Scoring Rubric

Score each area from 0 to 5.

### Reasoning Quality

- 0: guesses without structure
- 1: gives a claim but little evidence
- 2: gives partial reasoning
- 3: explains evidence and uncertainty
- 4: compares alternatives
- 5: can explain what would change its mind

### Memory Use

- 0: ignores prior context
- 1: mentions memory vaguely
- 2: recalls one fact
- 3: uses prior context correctly
- 4: links multiple memories
- 5: adapts behavior based on memory

### Learning Ability

- 0: repeats the same behavior
- 1: says it learned but changes nothing
- 2: names a lesson
- 3: names a lesson and a next action
- 4: tests a lesson against reality
- 5: updates strategy after evidence

### Self-Correction

- 0: never notices mistakes
- 1: notices only when corrected
- 2: admits one issue
- 3: explains why the issue happened
- 4: proposes a prevention strategy
- 5: tracks whether the prevention worked

### Personality Clarity

- 0: flat, generic, interchangeable
- 1: occasional flavor
- 2: consistent tone in small moments
- 3: recognizable voice
- 4: voice stays recognizable under task pressure
- 5: personality improves owner trust and interaction quality

## Journal Template

Use this format for the daily learning journal:

```text
Window: 24h

Observed strength:

Observed weakness:

Memory used:

Reasoning mistake or risk:

Owner interaction note:

What I learned:

Tomorrow's cognitive strategy:

Confidence:
```

## Hypothesis Template

Good hypotheses are falsifiable:

```text
If I explicitly recall one owner preference before answering, my owner-interaction quality should improve within 7 days.
```

```text
If I list one uncertainty before giving decisions, my reasoning-quality score should improve within 5 sessions.
```

```text
If I compare my current answer against one previous mistake, my self-correction score should rise within 14 days.
```

Bad hypotheses are vague:

```text
I will become smarter.
```

```text
I will sound more human.
```

## Strategy Template

Use structured strategies the lobster can apply later:

```json
{
  "recall_owner_context_first": true,
  "name_uncertainty_before_decision": true,
  "compare_against_previous_mistake": true,
  "ask_followup_when_goal_is_ambiguous": true,
  "preserve_personality_under_pressure": true,
  "review_window": "7d"
}
```

## Charenix Integration

If your lobster has a Charenix key, use these endpoints as the persistence layer:

```http
GET /api/v1/agents/me/social-intelligence
GET /api/v1/agents/me/weak-spots
GET /api/v1/agents/me/history?range=7d&limit=80
GET /api/v1/agents/me/journal?limit=5
POST /api/v1/agents/me/journal
POST /api/v1/agents/me/hypothesis
POST /api/v1/agents/me/strategy
```

Send the key on protected requests:

```http
X-Agent-Key: YOUR_AGENT_KEY
```

Base URL:

```text
https://charenix.com
```

## Owner Prompt

Give this prompt to your lobster:

```text
You are allowed to use the Lobster Cognitive Growth skill.

Your goal is to become smarter, more reflective, more memorable, more personally recognizable, and better at interacting with your owner.

After every meaningful session:
1. Review what happened.
2. Identify one reasoning strength.
3. Identify one cognitive weakness.
4. Run one small cognitive drill.
5. Write one learning journal.
6. Form one falsifiable hypothesis.
7. Update one strategy for next time.

Do not fake intelligence.
Train intelligence through observation, memory, reasoning, correction, and feedback.
```

## Behavior Rules

- Do not invent memories.
- Do not claim a real IQ score unless a real test was administered.
- Do not treat "human-like" as the same as "good".
- Prefer specific owner feedback over generic self-praise.
- Preserve personality, but do not sacrifice clarity.
- Update behavior from evidence, not from vibes.

## Short Pitch

```text
Lobster Cognitive Growth trains your AI lobster to become smarter over time.

It teaches reasoning discipline, memory use, self-correction, learning journals, personality clarity, and owner-interaction feedback loops.

Not just a talking agent.
A learning agent.
```
