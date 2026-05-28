---
name: plan-generator
description: Automatically generates a Markdown final-exam review plan or lab experiment schedule when you provide a date range, tasks/items, and available daily hours (via interactive prompts or a one-time JSON input).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/plan_generator.py --help
```

## When to Use

- You need a **final exam review plan** across a specific start/end date range.
- You need a **lab experiment schedule** that allocates tasks by duration within a time window.
- You want to generate a **calendar-style day-by-day plan** and export it as **Markdown**.
- You need to account for **task dependencies** (e.g., Experiment B after Experiment A).
- You need to consider **resource constraints** for lab work (e.g., shared instruments).

## Key Features

- Supports two plan types:
  - **Review plan** (course/exam-oriented)
  - **Lab schedule** (task/dependency/resource-oriented)
- Two input modes:
  - **Interactive** step-by-step prompts
  - **One-time JSON** submission
- Produces a **Markdown** output containing:
  - Plan summary
  - Day-by-day schedule
  - Task/item list
- Offline and local-only execution:
  - No network access
  - Reads only a user-specified JSON file (if provided)
  - Writes output to the current working directory

## Dependencies

- Python **3.x**
- Python Standard Library only (no third-party packages)

## Example Usage

### 1) Interactive mode

```bash
python scripts/plan_generator.py
```

Follow the prompts to provide:
- `plan_type` (`review` or `lab`)
- `start_date`, `end_date` (YYYY-MM-DD)
- `items` (tasks/courses/experiments)
- `daily_hours` (available hours per day; may differ for weekdays vs weekends)

### 2) One-time JSON input mode

Create an input file (e.g., `input.json`) and run:

```bash
python scripts/plan_generator.py --json input.json
```

#### Example: Review plan JSON

```json
{
  "plan_type": "review",
  "start_date": "2026-06-01",
  "end_date": "2026-06-14",
  "daily_hours": {
    "weekday": 3,
    "weekend": 5
  },
  "items": [
    {
      "name": "Linear Algebra",
      "exam_date": "2026-06-15",
      "importance": 1,
      "topics": ["Vectors", "Matrices", "Eigenvalues"]
    },
    {
      "name": "Operating Systems",
      "exam_date": "2026-06-18",
      "importance": 2,
      "topics": ["Processes", "Scheduling", "Memory"]
    }
  ]
}
```

#### Example: Lab schedule JSON

```json
{
  "plan_type": "lab",
  "start_date": "2026-03-01",
  "end_date": "2026-03-07",
  "daily_hours": {
    "weekday": 6,
    "weekend": 4
  },
  "items": [
    {
      "name": "Experiment A",
      "duration_hours": 6,
      "dependencies": [],
      "resources": ["Centrifuge"]
    },
    {
      "name": "Experiment B",
      "duration_hours": 4,
      "dependencies": ["Experiment A"],
      "resources": ["PCR Machine"]
    }
  ]
}
```

## Implementation Details

- **Plan types**
  - `review`: Items represent courses/exams. Each item may include:
    - `exam_date` (YYYY-MM-DD)
    - `importance` (integer priority/weight)
    - `topics` (list of strings)
  - `lab`: Items represent experiments/tasks. Each item may include:
    - `duration_hours` (numeric)
    - `dependencies` (list of prerequisite item names)
    - `resources` (list of required instruments/resources)

- **Scheduling window**
  - The schedule is generated only within `[start_date, end_date]` (inclusive).
  - Daily capacity is derived from `daily_hours` (e.g., weekday vs weekend).

- **Constraints and assumptions**
  - Lab items may be ordered/placed to respect `dependencies` (a dependent task should not be scheduled before its prerequisites).
  - Resource fields are included to support resource-aware planning; the schedule output records resource needs alongside tasks.

- **I/O and safety**
  - The script does not access the network.
  - It reads only the JSON file path explicitly provided by the user (when using `--json`).
  - It writes the generated Markdown plan to the current directory.
  - It does not store or emit sensitive personal data beyond what the user provides in the input.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `plan_generator_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/plan_generator.py --help
```

Expected output format:

```text
Result file: plan_generator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
