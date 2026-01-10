---
name: skill-template
description: Template for production-grade DocEngineering skills
allowed-tools:
  - Read
  - Grep
  - Write
  - "Bash(python:*)"
---

# Skill Template

## Overview

Use this folder as the starting point for a new skill.

## Prerequisites

- Confirm required input paths exist.
- Prefer relative paths via `{baseDir}` for portability.

## Instructions

1. **Scout**: Use `Grep`/`find` to locate only the relevant files.
2. **Analyze**: Read the minimum set of files needed.
3. **Execute**: Prefer deterministic scripts under `{baseDir}/scripts/`.
4. **Verify**: Run validation scripts and/or tests before returning results.

## Output Format

- Define a strict output format (Markdown template in `{baseDir}/assets/` and/or JSON schema).

## Error Handling

- If required inputs are missing, ask for them explicitly and stop.
- If any hard gate fails, return `EXIT_BLOCKED` and list blockers.
