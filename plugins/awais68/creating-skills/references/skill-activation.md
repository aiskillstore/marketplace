# Skill Activation Patterns

Research shows skills activate only 20-50% of the time with simple description-based triggers. This document covers patterns that achieve 84% activation.

## The Problem

Claude sees skill descriptions but often ignores them, proceeding directly to implementation without loading skill knowledge.

| Approach | Activation Rate |
|----------|----------------|
| Description only | 20% |
| Simple instruction hook | 50% |
| **Forced eval hook** | **84%** |

## The Solution: Commitment Mechanism

Force Claude to explicitly evaluate each skill before proceeding:

```
Step 1 - EVALUATE: For each skill, state YES or NO with brief reason
Step 2 - ACTIVATE: Use Skill(skill-name) to activate it NOW
Step 3 - IMPLEMENT: Only after activation
```

## Why It Works

The difference is **commitment**:

**Simple instruction (50%):**
```
If prompt matches skill keywords, use Skill(skill-name)
```
This is passive - Claude acknowledges it mentally, then ignores it.

**Forced eval (84%):**
```
MANDATORY: Evaluate each skill YES/NO before proceeding
CRITICAL: Skipping activation wastes the skill's knowledge
```
This creates accountability:
1. Claude must show its work (write YES/NO for each)
2. Once written, it's committed to activate
3. Can't skip to implementation without the evaluation step

## Hook Implementation

See `.claude/hooks/skill-activation.sh`:
- Runs synchronously on UserPromptSubmit
- Extracts skill names and descriptions
- Outputs evaluation prompt with skill list
- Skips short prompts (<20 chars)

## Aggressive Language Helps

Words like "MANDATORY", "CRITICAL", "WORTHLESS" make instructions harder to ignore:

```
CRITICAL: The evaluation is WORTHLESS unless you ACTIVATE the skills.
```

## Trade-offs

| Pro | Con |
|-----|-----|
| 84% vs 20% activation | More verbose output |
| No external dependencies | Lists all skills every prompt |
| Works offline | Slightly more tokens |

## Source

Based on testing 200+ prompts across multiple hook configurations.
Original research: https://chriscoyier.net/2024/11/16/how-to-make-claude-code-skills-activate-reliably/
