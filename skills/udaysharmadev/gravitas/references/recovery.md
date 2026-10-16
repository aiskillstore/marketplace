# Gravitas -- Interruption Recovery Reference

## The Problem

Long engineering sessions in Antigravity can be interrupted by context compaction, model switches (Claude quota exhausted), or user ending and resuming a session. Without persistent state, the new context re-reads files, re-plans, and retries failed approaches.

## The Solution

Gravitas maintains minimal durable state that survives interruption.

## State File: .gravitas/sessions/<task-id>/state.json

{
  "task_id": "add-cursor-pagination-2026-09-11",
  "contract": "./contract.json",
  "phase": "verify",
  "completed_criteria": ["AC1", "AC2"],
  "pending_criteria": ["AC3"],
  "files_touched": ["src/routes/posts.ts", "tests/posts.test.ts"],
  "known_failures": [],
  "last_successful_action": "wrote cursor parameter handling in posts.ts",
  "next_action": "run cursor pagination test suite"
}

## Evidence Ledger: .gravitas/sessions/<task-id>/evidence.jsonl

Append-only log of completed verifications:
{"criterion": "AC1", "evidence": "vitest run: 47 passed", "timestamp": "2026-09-11T02:30:00Z"}
{"criterion": "AC2", "evidence": "diff: serializer.ts unchanged", "timestamp": "2026-09-11T02:31:00Z"}

## Recovery Protocol

When resuming after interruption:
1. Check for .gravitas/sessions/ directory
2. Find the most recent session matching the task description
3. Read state.json -- determine current phase and pending criteria
4. Read evidence.jsonl -- understand what has been verified
5. Read failures.jsonl -- do not retry listed approaches
6. Resume from next_action in state.json
7. Do NOT re-read files that state.json shows were already read and acted upon

## Failure Log: .gravitas/sessions/<task-id>/failures.jsonl

{"approach": "direct timeout change", "reason": "test expects original value", "timestamp": "..."}

Before retrying anything, check this log.

## What NOT to Do After Interruption

- Do not re-read files already documented as read in state.json
- Do not re-attempt approaches listed in failures.jsonl
- Do not re-implement work shown complete in the evidence ledger
- Do not start over from scratch if more than 50% of criteria are complete

## Circuit Breaker

If recovery leads to the same failure repeatedly:
- Same failure x2: force diagnosis mode (why is this failing?)
- Same strategy x2: replan (this approach does not work)
- Verification cycles >3: report blocked, request user input
- System failure: stop cleanly, preserve state, report

The circuit breaker prevents the Stop hook from creating infinite loops.
