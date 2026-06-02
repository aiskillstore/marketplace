---
name: low-frequency-thread-monitor
description: 低频巡检 Skill for ordinary non-Goal Codex controller windows that need active, ETA-aware monitoring of background worker/review/planning threads. Use to keep the monitor alive until a terminal state, reduce context pollution and token spend, avoid over-polling, minimize expected wasted waiting time, and decide the next allowed action only after a final report, failure, or blocker appears.
---

# 低频巡检 Skill

## Purpose

Monitor a background Codex thread with minimal reads, no interruption, and low wasted waiting time.

This skill is monitoring only. It does not authorize writes, approvals, closure, gate unblocks, active promotion, or PROJECT_B consume/display changes.

Use it for ordinary non-Goal controller windows that still need to keep background work moving. It complements Goal mode; it does not replace durable Goal workflows.

## State Model

Keep these states separate:

- Foreground monitor state: the controller is active, waiting, checking, absorbing, blocked, or done.
- Background worker state: the worker is running, finalizing, completed, failed, blocked, or asking Owner.
- Governance state: self-report, review, absorption, approval, and routing are separate steps.

Pending next check means the monitor is still active, even if no foreground text is being generated.

## Hard Rules

1. If the target thread is still running and a next check is scheduled, the monitor is still active. Do not send a final answer that closes, archives, marks complete, abandons, or replaces the monitoring window.
2. Use a wakeup, automation, timer, or thread-continuation mechanism for the next check when available. If unavailable, say that limitation and the exact next check time, but do not claim monitoring is complete.
3. Do not nudge or steer a running thread with messages like "continue", "hurry", "are you done", or "report progress".
4. Read only recent status while monitoring. Use `turnLimit: 2 or 3` and `includeOutputs: false` by default.
5. Use `includeOutputs: true` only for failure diagnosis, a small cited final output, or an explicit Owner request.
6. Stop polling only when a final report, failure, blocker, handoff, or Owner-input request is visible.
7. After completion, read the final report seriously, then check named artifacts and governing fact files only as needed before recommending the next allowed action.

If you dispatch the worker yourself, ask it for one final completion/failure report. Do not ask it to send routine progress updates unless the task boundary requires them.

## Non-Interruption

Do not message the worker while it is reading, writing, reviewing, researching, self-checking, or producing a final report.

Send a follow-up only when:

- The Owner changes the task boundary.
- The worker is about to violate a hard boundary.
- The worker asks for Owner input.
- The worker reports a blocker/failure needing bounded clarification.
- The final report is complete and the next authorized step requires a new prompt.

## Completion Test

Terminal states:

- Final report matching the requested output shape.
- Clear completed status plus final answer.
- Clear failure or blocker report.
- Clear handoff saying the thread cannot proceed.
- Owner-input request.

Not terminal:

- "正在执行", "继续读取", "正在核查", "还在跑", "我会继续".
- Tool progress without a final report.
- Partial checklist or draft status.

## Timing Goal

Minimize expected wasted waiting time:

```text
wasted_wait = next_monitor_read_time - worker_completion_time, when the worker finishes before the next read
```

Do not use a fixed rule like "always wait at least 5 minutes". Choose the next read from task size, elapsed time, latest status, and estimated remaining time.

If only 1-2 minutes likely remain, check in 1-2 minutes. Do not round up to a generic 8-10 minute interval.

## Timing Table

| Latest evidence | Next check |
|---|---:|
| Final report, failure, blocker, or Owner-input request visible | Immediately read/absorb; stop polling |
| Finalizing, final self-check, preparing final report, writing summary, "马上/快完成/最后核查" | 1-3 minutes |
| Very small task, elapsed time already near expected finish | 60-120 seconds |
| New quick handoff/status/readonly confirmation | 90 seconds-3 minutes |
| Small planning or small file review, no near-finish signal | 3-5 minutes |
| Normal file review, bounded write, or self-check in middle work | 4-7 minutes |
| Long review/research/source gathering/platform rules/video/audio/many files in middle work | 8-15 minutes |
| Repeated long-running work with clear progress and no near-finish signal | 15-30 minutes |
| Idle with no final report | 2-4 minutes once, then light diagnostic read |
| Owner asks for status | Read once immediately, then reschedule from this table |

Normally avoid intervals under 60 seconds. Do not poll every few seconds merely to see whether the thread is active.

Near-finish override: when the latest status implies final packaging, final answer writing, or short self-check, the next check is 1-3 minutes. Scheduling 8-10 minutes in this state is a monitoring error.

## Adaptive Rule

Classify the task:

- `quick_readonly`: handoff confirmation, small status check.
- `file_review`: readonly review over local files.
- `bounded_write`: limited write plus self-check.
- `absorption`: Control Hub or Knowledge Hub registration/absorption.
- `planning`: route planning, schema planning, strategic design.
- `research`: web/platform/source research.
- `media_learning`: video/audio download, transcription, learning-card work.
- `long_review`: complete-chain review, large audit.

Use known or estimated P25/P50/P80 completion milestones when available.

When still running at elapsed time `t`:

1. If latest status is near-finish, ignore class defaults and check in 1-3 minutes.
2. If `t` is before P25, schedule near P25, respecting the minimum gap.
3. If `t` is between P25 and P50, schedule near P50 or in 2-5 minutes, whichever is sooner.
4. If `t` is between P50 and P80, schedule near P80 or in 3-7 minutes, whichever is sooner.
5. If `t` is past P80 but progress is normal, widen the interval in proportion to task size.
6. If progress appears stopped or idle without final report, do one light diagnostic read.

If uncertain, use:

```text
next_interval = clamp(estimated_remaining_time / 2, minimum_gap, maximum_gap)
```

Suggested clamps:

| Situation | Minimum | Maximum |
|---|---:|---:|
| Near-finish | 60 seconds | 3 minutes |
| Quick/small task | 90 seconds | 5 minutes |
| Normal review/write | 2 minutes | 7 minutes |
| Long research/review | 5 minutes | 15 minutes |
| Repeated long progress | 10 minutes | 30 minutes |

## Evidence Scope

Before terminal state: read only enough to determine `running / completed / failed / blocked / asks Owner`.

After terminal state, read in this order:

1. Latest 1-3 turns or thread status.
2. Final answer/report.
3. Artifact paths named in the report.
4. Actual artifact files if needed.
5. Governing fact files if routing, gates, or permissions depend on them.
6. Older transcript only if the final report is missing, vague, or contradictory.

Avoid whole legacy transcripts, long tool outputs, and worker reasoning history.

## Status Format

While still running, use interim wording, not a final completion answer:

```text
低频巡检中，不是最终结论。
目标窗口还在执行。
下一次巡检：约 HH:MM。
当前动作：等待，不打断窗口。
```

If environment cannot keep the monitor alive:

```text
目标窗口还在执行。当前环境无法自动保持巡检窗口活跃；建议下一次巡检时间：HH:MM。监控未完成。
```

After terminal state:

```text
我低频读了一次窗口。当前状态是：已完成 / 已阻塞 / 失败 / 等 Owner。
现在能确认：...
还不能确认：...
下一步建议：...
```

## Control Hub / Knowledge Hub Safeguards

- Worker self-report is not approval.
- Review pass is not automatic authorization.
- Absorption record is separate from work result.
- Candidate, active, display, and consume states must not be merged.
- Next action must come from the current fact source, not chat memory.
