---
name: groove
description: "Groove engineering workflow system. Top-level entry point. Use groove-daily-*, groove-work-*, groove-utilities-*, groove-admin-* for all workflow and admin commands."
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash(git:*) Bash(beans:*) Bash(gh:*) Bash(linear:*) Bash(npx:*) Bash(mkdir:*) AskUserQuestion
metadata:
  author: andreadellacorte
  version: "0.21.2"
---

<!-- groove:managed — do not edit; changes will be overwritten by groove update -->

# groove

Conversational front door to the groove workflow system. Use `$ARGUMENTS` as a natural-language request, figure out which groove skill best serves it, and **invoke that skill** — so the user never has to memorise the ~44 command names.

## No arguments → show the catalog

If `$ARGUMENTS` is empty, print the grouped command catalog below and stop (do not route). Hide the **Groovebook** group unless `groovebook:` is set in `.groove/index.md`.

## With arguments → route and invoke

1. Read `$ARGUMENTS` as intent. Pick the single best-matching skill from the **intent map** below.
2. Pass any residual specifics through as that skill's `$ARGUMENTS`. Example: `/groove spec the auth flow` → invoke `/groove-work-spec auth flow`; `/groove stats for the month` → `/groove-utilities-stats month`.
3. **Confidence:**
   - **Clear single match** → invoke it, prefixed by one line stating what you're running (e.g. "Routing to `/groove-work-plan`…").
   - **Several plausible** → use `AskUserQuestion` to offer the top 2–4 matches; invoke the chosen one.
   - **No good match** → list the 2–3 closest commands from the catalog and ask the user to pick or rephrase; do not guess.
4. **Destructive/outward guard:** for `/groove-admin-install`, `/groove-admin-update`, `/groove-admin-config`, and `/groove-groovebook-publish`, confirm with the user before invoking even on a clear match (these change config, pull/migrate, or publish externally).
5. **Config-aware:** only route to `/groove-groovebook-*` when `groovebook:` is set in `.groove/index.md`.

Invoke a skill the same way the rest of groove does — by running `/groove-<skill> <args>`.

## Intent map / catalog

<!-- Keep in sync with README.md, groove-admin-help, and groove-utilities-prime. Trigger words are hints, not exhaustive. -->

**Daily**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-daily-start` | Start the workday | start, morning, begin, kick off, what's today |
| `/groove-daily-end` | End the workday | end, wrap up, eod, closeout, done for the day |

**Work**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-work-brainstorm` | Clarify scope through dialogue | brainstorm, explore, scope, ideas, figure out |
| `/groove-work-plan` | Write an implementation plan | plan, design, approach, how should I build |
| `/groove-work-exec` | Execute the plan | exec, implement, build, do it, start coding |
| `/groove-work-review` | Evaluate output | review, evaluate, check my work, accept/rework |
| `/groove-work-compound` | Capture lessons | compound, capture lessons, what did I learn |
| `/groove-work-spec` | Create an outcome spec | spec, specify, outcome, requirements |
| `/groove-work-audit` | Review branch for blindspots | audit, blindspots, what am I missing |
| `/groove-work-doc` | Document how a component works | doc, document, how does X work, explain |

**Utilities — Tasks**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-utilities-task-list` | List active tasks | tasks, list tasks, what's on my plate |
| `/groove-utilities-task-create` | Create a task | new task, add task, todo |
| `/groove-utilities-task-update` | Update a task | update task, change task, move task |
| `/groove-utilities-task-archive` | Archive a completed task | archive, close out task |
| `/groove-utilities-task-analyse` | Analyse task status | analyse tasks, task status, breakdown |
| `/groove-utilities-task-install` | Set up task backend | set up tasks, task backend |
| `/groove-utilities-task-config` | Configure task backend | configure tasks, task settings |
| `/groove-utilities-task-doctor` | Health-check task backend | task health, tasks broken |

**Utilities — Memory**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-utilities-memory-log-daily` | Write the daily memory log | log today, daily log, record the day |
| `/groove-utilities-memory-log-weekly` | Roll up the weekly log | weekly log, week rollup |
| `/groove-utilities-memory-log-monthly` | Roll up the monthly log | monthly log, month rollup |
| `/groove-utilities-memory-log-git` | Record git activity | log git, git summary |
| `/groove-utilities-memory-install` | Set up memory backend | set up memory, memory backend |
| `/groove-utilities-memory-doctor` | Health-check memory | memory health, memory broken |
| `/groove-utilities-memory-mistakes` | Log & resolve a workflow mistake | mistake, error, went wrong, prevent recurring |
| `/groove-utilities-memory-promises` | Capture/resolve deferred items | promise, deferred, come back to, later |
| `/groove-utilities-memory-retrospective` | Analyse ratings/mistakes/learnings | retrospective, reflect, trends, patterns |
| `/groove-utilities-memory-graduate` | Promote a lesson to AGENTS.md | graduate, make permanent, promote lesson |

**Utilities — Session**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-utilities-prime` | Load workflow context | prime, load context, catch up |
| `/groove-utilities-check` | Check for a newer version | check version, update available |
| `/groove-utilities-stats` | Compound-loop metrics dashboard | stats, metrics, dashboard, how are we doing |
| `/groove-utilities-onboard` | Generate GROOVE.md onboarding | onboard, onboarding guide, GROOVE.md |

**Admin**
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-admin-help` | Show all commands | help, commands, what can I do |
| `/groove-admin-install` | Install backends & bootstrap | install, set up groove |
| `/groove-admin-config` | Create/update config | config, settings, configure groove |
| `/groove-admin-update` | Pull latest & migrate | update groove, upgrade, migrate |
| `/groove-admin-doctor` | Run all health checks | doctor, health check, is groove ok |
| `/groove-admin-claude-hooks` | Install Claude Code hooks | claude hooks, native hooks |
| `/groove-admin-cursor-hooks` | Install Cursor hooks | cursor hooks |
| `/groove-admin-claude-statusline` | Install the statusline | statusline, status line |

**Groovebook** *(only if `groovebook:` is set in `.groove/index.md`)*
| Skill | Purpose | Triggers |
|---|---|---|
| `/groove-groovebook-publish` | Publish a learning to the commons | publish learning, share lesson |
| `/groove-groovebook-review` | Review open learning PRs | review learnings, groovebook PRs |
