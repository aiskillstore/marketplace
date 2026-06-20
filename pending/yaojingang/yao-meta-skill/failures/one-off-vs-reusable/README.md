# One-Off Vs Reusable

## Symptom

The router sees strong packaging language and triggers even though the user only wants a one-off answer or prompt.

## Anti-Pattern

Treating any "create" or "package" wording as reusable-skill intent.

## Example Prompt

`Write a custom answer for this request without creating a skill package.`

## Why It Fails

- lexical overlap is high
- true user intent is single-use output, not reusable infrastructure

## Fix

- detect one-off language explicitly
- treat "custom answer", "one-off", and similar phrases as exclusion concepts

## Regression Prompts

- `Create a one-off prompt for this task.`
- `Write a custom answer for this request without creating a skill package.`
