---
name: task-reminder
description: Organize scattered tasks into actionable lists and generate daily/weekly/deadline reminder plans when you need a structured schedule and exportable outputs (MD/CSV), with optional system notifications.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/task_reminder.py --help
```

## When to Use
- You have a scattered set of tasks and need them consolidated into an actionable, prioritized list.
- You want a **daily** plan that tells you what to focus on each day within a date range.
- You want a **weekly** reminder plan (e.g., every Monday) to review upcoming work.
- You need a **deadline-driven** plan that highlights tasks approaching due dates.
- You need to export reminders to **Markdown/CSV** for sharing, collaboration, or importing into other tools.

## Key Features
- Converts a raw task list into an actionable plan across a specified date range.
- Supports reminder modes: `daily`, `weekly`, `deadline`, or `all` (default).
- Exports results to:
  - `reminders.md` (human-readable actionable list + plan)
  - `reminders.csv` (tabular plan for spreadsheets/tools)
- Accepts interactive input or JSON input via CLI.
- Optional system notifications (disabled by default; requires explicit activation in the script/parameters if supported).

## Dependencies
- Python **3.x** (standard library only; no third-party packages)

## Example Usage
### 1) Run with interactive input
```bash
python scripts/task_reminder.py
```

### 2) Run with JSON input (recommended for repeatable runs)
Create `input.json`:
```json
{
  "start_date": "2026-03-01",
  "end_date": "2026-03-10",
  "reminder_mode": "all",
  "weekly_day": 0,
  "tasks": [
    {
      "title": "Write lab report",
      "deadline": "2026-03-05",
      "priority": 3,
      "estimate_hours": 2,
      "tags": ["Course", "Lab"]
    },
    {
      "title": "Prepare slides for meeting",
      "deadline": "2026-03-08",
      "priority": 2,
      "estimate_hours": 1.5,
      "tags": ["Work"]
    }
  ]
}
```

Run:
```bash
python scripts/task_reminder.py --json input.json
```

Expected outputs in the working directory:
- `reminders.md`
- `reminders.csv`

## Implementation Details
### Input Schema
**Minimum required fields**
- `tasks`: array of task objects
- `start_date`: string in `YYYY-MM-DD`
- `end_date`: string in `YYYY-MM-DD`

**Optional fields**
- `reminder_mode`: one of `daily` / `weekly` / `deadline` / `all` (default: `all`)
- `weekly_day`: integer `0..6` where `0=Monday` and `6=Sunday` (default: `0`)

**Task object fields (recommended)**
- `title` (string): task name
- `deadline` (string, `YYYY-MM-DD`): due date used for deadline-based reminders
- `priority` (number/int): higher value indicates higher priority (as provided by the user)
- `estimate_hours` (number): effort estimate used for planning context
- `tags` (array of strings): categorization for filtering/grouping in outputs

### Reminder Modes
- **daily**: generates a day-by-day plan within `[start_date, end_date]`.
- **weekly**: generates reminders on the specified `weekly_day` within the date range.
- **deadline**: emphasizes tasks by approaching deadlines within the date range.
- **all**: produces combined outputs for daily/weekly/deadline views.

### Output Files
- `reminders.md`: includes an actionable task list and the generated reminder plan in Markdown format.
- `reminders.csv`: includes a structured reminder plan table suitable for spreadsheets and imports.

### Security/Operational Constraints
- Runs as a local script with **no network access**.
- Writes only to the output files it generates (e.g., `reminders.md`, `reminders.csv`) in the specified/working directory.
- System notifications are **not enabled by default** and require explicit activation if implemented.

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
- If a file is produced, prefer a deterministic output name such as `task_reminder_result.md` unless the skill documentation defines a better convention.
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
python scripts/task_reminder.py --help
```

Expected output format:

```text
Result file: task_reminder_result.md
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
