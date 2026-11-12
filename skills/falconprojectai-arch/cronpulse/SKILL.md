---
name: cronpulse
description: Analyze imported scheduled-job and AI-agent run history to summarize failures, durations, repeated errors, and incident patterns.
---

# CronPulse

## Purpose
Turn an exported JSON array or JSONL run-history file into a concise incident and reliability review.

## Workflow
1. Request an exported run-history file or redacted sample. Do not ask for credentials or live access tokens.
2. Normalize common fields such as name/job/task, status/conclusion, started_at/start/time, duration_ms/duration, exit_code, and error/message.
3. Group runs by job/task and identify failures, non-zero exit codes, unusually long durations, repeated errors, and missing/invalid fields.
4. Calculate counts and success rate from the supplied records only; state the denominator and excluded records.
5. Summarize the most actionable incidents with timestamps and source evidence.
6. Recommend manual next checks; distinguish a confirmed failure in the input from a suspected cause.

## Limits
- This is an offline analyzer, not a live monitor. It does not connect to cron, GitHub Actions, n8n, or agent platforms; it cannot detect runs missing from the supplied export, send alerts, retry jobs, or restart tasks.
- Do not infer root cause from a status label alone.
