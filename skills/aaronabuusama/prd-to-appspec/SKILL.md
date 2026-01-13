---
name: prd-to-appspec
description: Transform PRDs (Product Requirements Documents) into structured XML app specifications optimized for AI coding agents. Converts developer-focused docs with code examples into declarative agent-consumable format. USE WHEN user says "convert PRD", "generate app spec", "transform PRD", "create specification from requirements", or wants to prepare a PRD for agent consumption.
---

# PRD to App Spec Converter

Transform Product Requirements Documents (PRDs) into structured XML application specifications optimized for AI coding agents.

## When to Activate This Skill

- Convert a PRD to app spec format
- Generate XML specification from requirements document
- Transform technical PRD for agent consumption
- Prepare documentation for AI coding agent
- Create app_spec.txt from existing PRD

## What This Skill Does

Converts developer-focused PRDs (with code snippets, TDD plans, implementation details) into declarative XML specifications that AI coding agents can consume more effectively.

**Input**: PRD with technical details, code examples, architecture decisions
**Output**: Structured `app_spec.txt` in XML format

## How to Execute

**Run the `/convert-prd` workflow**, which provides:

1. PRD file location (prompts if not provided)
2. Section-by-section extraction and transformation
3. Pydantic models → database schema conversion
4. Implementation code → feature descriptions
5. Epics/tasks → numbered implementation steps
6. Test assertions → success criteria
7. Final XML output with validation

## Core Transformations

| PRD Has | App Spec Gets |
|---------|---------------|
| Function implementations | Feature descriptions |
| Pydantic field validators | Data constraints in prose |
| Try/except patterns | Error handling requirements |
| Test assertions | Success criteria |
| CLI commands | API/command summaries |
| Directory structure | Technology stack context |

## Output Template Structure

```xml
<project_specification>
  <project_name>...</project_name>
  <overview>...</overview>
  <technology_stack>...</technology_stack>
  <core_features>...</core_features>
  <database_schema>...</database_schema>
  <api_endpoints_summary>...</api_endpoints_summary>
  <implementation_steps>...</implementation_steps>
  <success_criteria>...</success_criteria>
</project_specification>
```

## Key Principle

- **PRD**: Shows HOW (implementation details)
- **App Spec**: Describes WHAT (requirements and expectations)

The app_spec tells an agent WHAT to build without dictating exact implementation.

## Full Workflow Reference

For complete step-by-step instructions: `workflows/convert-prd.md`
