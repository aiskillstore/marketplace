# Document Export Vs Agent Skill

## Symptom

The request asks to package content as a document or improve a document, but the system mistakes it for agent-skill creation.

## Anti-Pattern

Reading "package" as "skill package" without checking the target artifact.

## Example Prompt

`Package this explanation as a document, not as an agent skill.`

## Why It Fails

- "package" is overloaded
- release notes, runbooks, and docs often look structurally similar to skills

## Fix

- model target artifact explicitly
- treat document-only exports as negative route evidence

## Regression Prompts

- `Improve this README but do not turn it into a skill.`
- `Package this explanation as a document, not as an agent skill.`
