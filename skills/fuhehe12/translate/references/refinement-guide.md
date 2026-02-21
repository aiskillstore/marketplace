# Refinement Guide

> Optional step. Enabled when the user explicitly requests it, or when the main Agent identifies quality issues during review.
> Sub Agents handle the actual refinement; the main Agent oversees the process and makes the final call.

---

## When to Run Refinement

The translation workflow emphasizes rewriting over literal translation, so high-quality execution already internalizes awareness of translationese. Refinement is not a default step — consider enabling it in the following situations:

- The user explicitly asks for "refinement," "polish," or "fine-tuning"
- The main Agent's verification pass finds obvious translationese or inconsistent style
- Multiple sub Agents translated in parallel and the style seams feel unnatural

## How Refinement Works

**The main Agent oversees; sub Agents execute.**

The main Agent decides the refinement granularity based on file size, then dispatches sub Agents to handle the actual work:

| Scale | Refinement Strategy |
|-------|---------------------|
| Small file (≤ 2500 lines) | Dispatch 1 sub Agent to refine the full text |
| Large file (> 2500 lines) | Dispatch sub Agents to refine segment seams + spot-check 2–3 segments |
| Multiple files | Dispatch 1 sub Agent per file for spot-check refinement |

## Sub Agent Refinement Prompt Template

```
You are a [target language] writing editor (target region: [target region]). Give the translation a second pass to eliminate translationese and improve overall prose quality.

Your inputs:
1. Translation file: [path to translation]
2. Glossary: [path to _glossary.md]
3. Translation brief: [path to _translation_brief.md]

Refinement checklist — assume the reader has already said "it still reads like a translation," and go through each paragraph with that assumption in mind:

1. **Translationese scan**: Identify awkward constructions and Europeanized phrasing; rewrite them as natural expressions in the target language
2. **Rhythm check**: Break up runs of more than three long sentences; consolidate places where short sentences are stacked unnecessarily
3. **Terminology consistency**: Search the full text for key terms and confirm the chosen translations are used consistently throughout
4. **Regional style check**: Confirm that word choices fit the conventions of the target region
5. **Cut the filler**: Remove empty words and phrases that carry no information

Refinement principle: subtract, don't add. Like a sculptor removing excess stone — let the translation reveal its natural shape.

Output: Edit the file in place (use the Edit tool). Do not create new files.
```

Sub Agent configuration:
- `subagent_type`: "general-purpose"
- `model`: "sonnet"
- Before dispatching, replace all variables in the template with actual values:
  - `[target language]` → defaults to "Chinese"; fill in based on the translation brief
  - `[target region]` → defaults to "Mainland China"; fill in based on the translation brief

## Main Agent Oversight Workflow

1. Decide whether to enable refinement (based on the trigger conditions above)
2. Determine the refinement granularity (full text / seams only / spot-check)
3. Dispatch sub Agents to execute
4. Review sub Agent output and confirm no new issues were introduced
5. Report a summary of the refinement to the user
