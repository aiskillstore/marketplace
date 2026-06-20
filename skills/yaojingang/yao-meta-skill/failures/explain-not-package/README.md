# Explain Not Package

## Symptom

The request is asking for explanation or interpretation, but the skill creator tries to package it as a reusable workflow.

## Anti-Pattern

Confusing topic adjacency with packaging intent.

## Example Prompt

`Review this note and tell me what it means in plain English.`

## Why It Fails

- the source material may look like a workflow
- the user still wants explanation, not systematization

## Fix

- treat explanation, summary-only, and translation-only modes as direct exclusions
- require positive evidence of reusable packaging intent before triggering

## Regression Prompts

- `Explain what a workflow is.`
- `Review this process note and explain it, no packaging needed.`
