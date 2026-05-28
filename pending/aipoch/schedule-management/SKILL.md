---
name: schedule-management
description: Local schedule management for adding events, tracking deadlines, generating reminders, and detecting time conflicts when users need offline scheduling with optional popup notifications.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use
- You need lightweight, **offline/local-only** schedule management without any cloud sync.
- You want to **add meetings/events** and store them in a simple local data directory.
- You need to **track deadlines** (modeled as events with `type=deadline`) and list them by time range.
- You want to **detect scheduling conflicts** (overlapping time windows on the same date).
- You need **local reminders** exported to a file and optionally shown as **desktop popup notifications**.

## Key Features
- Add and store events locally in `events.jsonl`.
- List and filter events by time range.
- Import events (operation-driven workflow).
- Detect conflicts by checking overlapping time intervals.
- Generate upcoming reminders into `reminders.csv`.
- Optional popup notifications via a local script with deduplication using `notified.log`.
- Strict validation for required fields and time format.

## Dependencies
- Python `>= 3.9`
- (Optional, for popup reminders) Windows PowerShell `>= 5.1` to run `scripts/notify.ps1`

## Example Usage
> Time format must be `YYYY-MM-DD HH:MM` (24-hour).

### 1) Add an event with a reminder
```bash
python scripts/schedule_tool.py \
  --operation add \
  --data-dir "./data" \
  --title "Project Sync" \
  --start "2026-02-10 09:00" \
  --end "2026-02-10 10:00" \
  --type "meeting" \
  --location "Room 3A" \
  --notes "Bring status updates" \
  --tags "work,weekly" \
  --remind 30
```

### 2) List events
```bash
python scripts/schedule_tool.py \
  --operation list \
  --data-dir "./data"
```

### 3) Detect conflicts
```bash
python scripts/schedule_tool.py \
  --operation conflicts \
  --data-dir "./data"
```

### 4) Generate reminders export
```bash
python scripts/schedule_tool.py \
  --operation reminders \
  --data-dir "./data"
```

This generates:
- `./data/events.jsonl`
- `./data/reminders.csv`

### 5) (Optional) Show popup reminders with deduplication
1. Generate reminders first:
   ```bash
   python scripts/schedule_tool.py --operation reminders --data-dir "./data"
   ```
2. Run the notifier periodically (e.g., via Task Scheduler):
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/notify.ps1 -DataDir "./data"
   ```
Notifications are deduplicated using `./data/notified.log` so each reminder time is shown only once.

> Additional examples may be available in `references/examples.md`.

## Implementation Details
- **Storage**
  - Events are appended to `events.jsonl` in the specified `--data-dir`.
  - Reminder exports are written to `reminders.csv` in the same directory.
  - Popup notification deduplication uses `notified.log` in the data directory.

- **Operations**
  - `add`: validates required fields and writes a new event record.
  - `import`: imports event records (format depends on the script’s supported import mode).
  - `list`: prints a summary of stored events (optionally filtered by time range).
  - `conflicts`: checks for overlapping events and reports conflicts.
  - `reminders`: computes upcoming reminder times and exports them.

- **Time Parsing Rules**
  - Accepted format: `YYYY-MM-DD HH:MM` (24-hour).
  - Invalid time formats are explicitly rejected.

- **Conflict Detection**
  - Two events conflict if they occur on the same date and their time intervals overlap:
    - Overlap condition: `startA < endB` and `startB < endA`
  - Conflicts are reported to standard output.

- **Deadlines**
  - A deadline is represented as an event with `type=deadline`.
  - Deadline tracking uses the same storage and listing mechanisms as other events.

- **Failure Handling**
  - Missing required fields terminates only the current operation (does not corrupt existing data).
  - Validation errors are surfaced clearly (e.g., invalid time format).

- **Security & Compliance**
  - No network access and no external APIs.
  - Reads/writes are restricted to the user-specified local `--data-dir`.