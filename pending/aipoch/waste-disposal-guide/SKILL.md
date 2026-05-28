---
name: waste-disposal-guide
description: Guide for disposing specific chemical wastes into the correct colored waste containers, with safety precautions and regulatory compliance notes.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Waste Disposal Guide

Guide for disposing specific chemical wastes into the correct colored waste containers.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Use this skill when identifying the correct waste container for a specific chemical.
- Use this skill when reviewing waste categories and safety precautions for laboratory chemicals.
- Do not use this skill for emergency spill response, disposal of radioactive materials, or regulated biological waste requiring special handling.

## Workflow

1. Confirm the chemical name or waste type to look up.
2. Validate that the request is for standard laboratory chemical waste disposal guidance.
3. Look up the chemical in the waste category database and return the correct container color and safety notes.
4. **Mixture handling:** If the user provides a mixture (e.g., "chloroform + ethanol"), identify the most hazardous component and assign the container for that component. Emit a note: "Mixed waste containing halogenated solvents must go into the halogenated (orange) container regardless of other components."
5. If the chemical is not found, state that clearly and suggest the closest category based on chemical class.
6. If inputs are incomplete, state which fields are missing and request only the minimum additional information.

## Usage

```text
python scripts/main.py --chemical "chloroform"
python scripts/main.py --chemical "ethanol"
python scripts/main.py --list-categories
python scripts/main.py --safety
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--chemical` | string | No | Chemical name to look up |
| `--list-categories` | flag | No | List all waste categories |
| `--safety` | flag | No | Show safety notes for all categories |

## Waste Categories

| Container | Color | Accepts |
|-----------|-------|---------|
| Halogenated | Orange | Chloroform, DCM, halogenated solvents |
| Non-halogenated | Red | Ethanol, acetone, organic solvents |
| Aqueous | Blue | Water-based solutions, buffers |
| Acid | Yellow | Acids (dilute/concentrated) |
| Base | White | Bases, alkali solutions |
| Heavy Metal | Gray | Mercury, lead, cadmium waste |
| Solid | Black | Gloves, paper, solid debris |

**Mixture rule:** When a waste stream contains both halogenated and non-halogenated solvents, use the halogenated (orange) container. When in doubt, consult your institution's EHS office.

## Output

- Correct container color and category for the queried chemical
- Disposal instructions and safety precautions
- Notes on incompatible waste streams

## Scope Boundaries

- This skill covers standard laboratory chemical waste categories; it does not cover radioactive, biological, or controlled substance waste.
- Local regulations may differ; always verify with your institution's EHS office before disposal.
- This skill does not provide emergency spill response guidance.

## Stress-Case Rules

For complex multi-constraint requests, always include these explicit blocks:

1. Assumptions
2. Chemical(s) Queried
3. Disposal Guidance
4. Safety Notes
5. Risks and Manual Checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate disposal categories or safety classifications for unknown chemicals.

## Input Validation

This skill accepts: a chemical name or waste type for container color lookup and disposal guidance.

If the request does not involve standard laboratory chemical waste disposal — for example, asking for emergency spill response, radioactive waste handling, biological waste disposal, or regulatory compliance certification — do not proceed with the workflow. Instead respond:
> "waste-disposal-guide is designed to identify the correct waste container and disposal instructions for standard laboratory chemicals. Your request appears to be outside this scope. Please provide a chemical name, or use a more appropriate tool for specialized waste streams."

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
