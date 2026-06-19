# Future Outline Vs Build

## Symptom

The user is still framing or exploring a future skill, but the router prematurely triggers full skill generation.

## Anti-Pattern

Treating early planning language as execution-ready packaging intent.

## Example Prompt

`Create an outline for a possible future skill, but do not build the skill yet.`

## Why It Fails

- the prompt mentions "skill"
- the actual task is pre-build design, not packaging

## Fix

- detect "future skill", "outline", "before we decide", and similar wording as planning-only exclusions
- require either present-tense packaging intent or explicit build intent

## Regression Prompts

- `Help me shape an idea before we decide whether to build a skill.`
- `Create an outline for a possible future skill, but do not build the skill yet.`
