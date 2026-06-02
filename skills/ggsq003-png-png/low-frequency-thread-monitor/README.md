# Low Frequency Thread Monitor

[![skills.sh](https://skills.sh/b/ggsq003-png/low-frequency-thread-monitor)](https://skills.sh/ggsq003-png/low-frequency-thread-monitor)

A lightweight Codex skill for keeping ordinary, non-Goal controller windows moving while background worker threads run.

It helps a controller window monitor workers with low-context, ETA-aware checks, without repeatedly reading long transcripts or closing the monitor before the worker reaches a terminal state.

## Why This Exists

When you run Codex with controller / worker / reviewer windows, ordinary windows can struggle with background work:

- The controller may treat waiting as completion and close too early.
- Repeated polling can waste quota and pollute the context.
- A worker may be near the final report, but the next check is scheduled 8-10 minutes later.
- Worker self-reports can accidentally get blurred with approval, absorption, or routing.

This skill adds a small monitoring protocol for those workflows.

It complements Goal mode; it is not a replacement for durable Goal workflows. The point is simpler: when you are using an ordinary Codex window as a controller, it gives that window a low-cost way to keep supervising background work without burning context.

## What It Does

- Keeps the monitor active until the worker reaches a terminal state.
- Uses ETA-aware next checks instead of a fixed "wait 5 minutes" rule.
- Checks in 1-3 minutes when the worker appears near the final report.
- Avoids nudging or interrupting a running worker.
- Reads only recent status while monitoring.
- Separates self-report, review, absorption, approval, and routing.

## How It Is Different

This is not a worker launcher, tmux wrapper, or health-check library.

| Tool / pattern | Main job | This skill's difference |
|---|---|---|
| Goal mode | Durable objective continuation | Useful when you are not using Goal mode, or want a lighter controller protocol |
| `codex-worker` style skills | Spawn Codex CLI workers in tmux/worktrees | Monitors existing Codex threads/windows; does not create workers |
| Background coding-agent skills | Run external agents as background processes | Focuses on quiet monitoring and terminal-state routing, not process execution |
| Worker health monitoring | Heartbeats, failure rates, stuck-job detection | Designed for human-in-the-loop Codex controller windows, not production worker fleets |
| Codex Monitor app | Full desktop command center | This is a small installable protocol skill, not a separate app |

The niche is ordinary Codex multi-window workflows: keep the controller alive, check less often, avoid context pollution, and still catch completion quickly.

## Related Work

Adjacent projects and skills solve nearby problems:

- [`codex-worker`](https://skills.sh/moonshotai/kimi-cli/codex-worker): orchestration for multiple Codex CLI agents in tmux/worktrees.
- [`coding-agent`](https://skills.sh/steipete/clawdis/coding-agent): background execution patterns for Codex, Claude Code, OpenCode, and Pi.
- [`worker-health-monitoring`](https://skills.sh/dadbodgeoff/drift/worker-health-monitoring): heartbeat and stuck-worker health monitoring.
- [Codex Monitor](https://www.codexmonitor.app/): full desktop command center for Codex agents.
- [OpenAI Codex issue #22099](https://github.com/openai/codex/issues/22099): discussion of nonblocking background task management.

This skill intentionally stays smaller: it is a protocol for quiet monitoring inside Codex, not a worker runtime or a separate app.

## Good Fit

Use this if you run Codex workflows like:

- controller window + background worker
- planner + reviewer
- bounded-write worker + independent review
- Control Hub / Knowledge Hub style routing
- long-running research or file-review threads

It is especially useful when you want ordinary Codex windows to keep moving without using Goal mode.

## Positioning

One-line pitch:

```text
Keep non-Goal Codex controller windows moving with low-context, ETA-aware background thread monitoring.
```

Short Chinese pitch:

```text
不启用 Goal，也能让 Codex 普通主控窗口低成本自主巡检后台任务。
```

## Install

Install with the Skills CLI:

```bash
npx skills add ggsq003-png/low-frequency-thread-monitor -g -y
```

Or clone this repository into your Codex skills folder:

```bash
git clone https://github.com/ggsq003-png/low-frequency-thread-monitor ~/.codex/skills/low-frequency-thread-monitor
```

Then restart Codex or open a new Codex window so the skill list refreshes.

## Use

Ask Codex to use the skill when monitoring a worker thread:

```text
Use low-frequency-thread-monitor to watch this background worker. Keep the monitor active, avoid interrupting the worker, and schedule ETA-aware checks until a final report, blocker, failure, or Owner-input request appears.
```

## Core Rule

If the target thread is still running and a next check is scheduled, monitoring is not complete.

The monitor should not close, archive, mark complete, or replace itself just because the worker has not finished yet.

## Timing Cheat Sheet

| Latest evidence | Next check |
|---|---:|
| Final report / failure / blocker / Owner-input request | Read immediately |
| Finalizing / writing summary / final self-check | 1-3 minutes |
| Very small task near expected finish | 60-120 seconds |
| Quick status or handoff | 90 seconds-3 minutes |
| Small planning or file review | 3-5 minutes |
| Normal review / bounded write / self-check | 4-7 minutes |
| Long research / long review / many files | 8-15 minutes |
| Repeated long progress with no near-finish signal | 15-30 minutes |

## Chinese Summary

这个 Codex Skill 用于不启用 Goal 的普通窗口。

它让主控窗口在后台 worker 运行时保持低成本自主巡检：少读、少污染上下文、不打断 worker，并按预计完成时间设置下一次检查。

适合多窗口工作流：主控 / worker / reviewer、有限写入、自检、复审、吸收、路由等场景。

安装：

```bash
git clone https://github.com/ggsq003-png/low-frequency-thread-monitor ~/.codex/skills/low-frequency-thread-monitor
```

## Follow

If this helps your Codex workflow:

- Star the repo.
- Use GitHub `Watch -> Custom -> Releases` to subscribe to updates.
- Share it with people running controller / worker / reviewer Codex workflows.
