# PairCoder CLI Complete Reference

> Updated: 2025-12-31 | Version: 2.8.4 | 120+ commands

## Contents

- [Command Groups Overview](#command-groups-overview)
- [Core Commands](#core-commands)
- [Preset Commands](#preset-commands)
- [Planning Commands](#planning-commands)
- [Task Commands](#task-commands)
- [Skills Commands](#skills-commands)
- [Flow Commands (Deprecated)](#flow-commands-deprecated)
- [Orchestration Commands](#orchestration-commands)
- [Intent Commands](#intent-commands)
- [GitHub Commands](#github-commands)
- [Standup Commands](#standup-commands)
- [Metrics Commands](#metrics-commands)
- [Budget Commands](#budget-commands)
- [Timer Commands](#timer-commands)
- [Benchmark Commands](#benchmark-commands)
- [Cache Commands](#cache-commands)
- [Session Commands](#session-commands)
- [Compaction Commands](#compaction-commands)
- [Security Commands](#security-commands)
- [Migrate Commands](#migrate-commands)
- [Trello Commands](#trello-commands)
- [Trello Task Commands (ttask)](#trello-task-commands-ttask)
- [MCP Commands](#mcp-commands)
- [Configuration](#configuration)
- [Environment Variables](#environment-variables)
- [Common Workflows](#common-workflows)

---

## Command Groups Overview

| Group | Purpose | Count |
|-------|---------|-------|
| Core | init, feature, pack, status, validate, ci, context-sync | 7 |
| Preset | Project presets | 4 |
| Planning | plan new/list/show/tasks/status/sync-trello/add-task/estimate | 8 |
| Task | Local task file management | 11 |
| Skills | Skill management and export | 7 |
| Flow | Workflow definitions (deprecated) | 4 |
| Orchestration | Multi-agent orchestration | 6 |
| Intent | Natural language intent detection | 3 |
| GitHub | GitHub PR integration | 7 |
| Standup | Generate standup summaries | 2 |
| Metrics | Token/cost tracking | 9 |
| Budget | Token budget management | 3 |
| Timer | Time tracking | 5 |
| Benchmark | Agent benchmarking | 4 |
| Cache | Context caching | 3 |
| Session | Session management | 2 |
| Compaction | Context compaction recovery | 5 |
| Security | Security scanning | 4 |
| Migrate | Migration commands | 2 |
| Trello | Trello board configuration | 10 |
| ttask | Trello card operations | 7 |
| MCP | MCP server for Claude Desktop | 3 |
| Upgrade | Version upgrades | 1 |
| **Total** | | **120+** |

---

## Core Commands

| Command | Description |
|---------|-------------|
| `init [path] [--preset]` | Initialize repo with PairCoder structure |
| `feature <name>` | Create feature branch with context |
| `pack [--lite]` | Package context for AI agents |
| `context-sync` | Update the context loop |
| `status` | Show current context and recent changes |
| `validate` | Check repo structure and consistency |
| `ci` | Run local CI checks (tests + linting) |

### Examples

```bash
# Initialize new project
bpsai-pair init my-project --preset bps

# Create feature branch
bpsai-pair feature add-auth --type feature --primary "Add authentication"

# Package context (lite for Codex 32KB limit)
bpsai-pair pack --lite --out context.tgz

# Check status
bpsai-pair status
```

---

## Preset Commands

| Command | Description |
|---------|-------------|
| `preset list` | List available presets |
| `preset show <name>` | Show preset details |
| `preset preview <name>` | Preview generated config |
| `init --preset <name>` | Initialize with preset |

**Available Presets:** python-cli, python-api, react, fullstack, library, minimal, autonomous, bps

### Examples

```bash
bpsai-pair preset list
bpsai-pair preset show bps
bpsai-pair preset preview autonomous
bpsai-pair init my-project --preset bps
```

---

## Planning Commands

| Command | Description |
|---------|-------------|
| `plan new <slug>` | Create a new plan |
| `plan list` | List all plans |
| `plan show <id>` | Show plan details |
| `plan tasks <id>` | List tasks for a plan |
| `plan status [id]` | Show progress with task breakdown |
| `plan sync-trello <id>` | Sync tasks to Trello board |
| `plan add-task <id>` | Add a task to a plan |
| `plan estimate <id>` | Estimate plan token cost |

### Examples

```bash
# Create feature plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# Show plan with progress
bpsai-pair plan status plan-2025-12-my-feature

# Sync to Trello
bpsai-pair plan sync-trello plan-2025-12-my-feature --dry-run
bpsai-pair plan sync-trello plan-2025-12-my-feature --target-list "Planned/Ready"
```

---

## Task Commands

| Command | Description |
|---------|-------------|
| `task list` | List all tasks |
| `task show <id>` | Show task details |
| `task update <id> --status` | Update task status (fires hooks) |
| `task next` | Get next recommended task |
| `task next --start` | Auto-start next task |
| `task auto-next` | Full auto-assignment with Trello |
| `task archive` | Archive completed tasks |
| `task restore <id>` | Restore from archive |
| `task list-archived` | List archived tasks |
| `task cleanup` | Clean old archives |
| `task changelog-preview` | Preview changelog entry |

### Examples

```bash
# Get and start next task
bpsai-pair task next --start

# Update task status (fires hooks)
bpsai-pair task update TASK-001 --status in_progress
bpsai-pair task update TASK-001 --status done

# Archive completed tasks
bpsai-pair task archive --completed
bpsai-pair task changelog-preview --since 2025-12-01
```

---

## Skills Commands

| Command | Description |
|---------|-------------|
| `skill list` | List all skills |
| `skill validate [name]` | Validate skill format against spec |
| `skill export <name>` | Export to Cursor/Continue/Windsurf |
| `skill install <source>` | Install skill from URL/path |
| `skill suggest` | AI-powered skill suggestions |
| `skill gaps` | Detect missing skills from patterns |
| `skill generate <name>` | Generate skill from detected gap |

### Examples

```bash
# List and validate
bpsai-pair skill list
bpsai-pair skill validate
bpsai-pair skill validate designing-and-implementing

# Export to other platforms
bpsai-pair skill export my-skill --format cursor
bpsai-pair skill export --all --format windsurf
bpsai-pair skill export my-skill --format continue --dry-run

# Install from URL or path
bpsai-pair skill install https://example.com/skill.tar.gz
bpsai-pair skill install ./my-skill/

# AI-powered suggestions
bpsai-pair skill suggest
bpsai-pair skill gaps
bpsai-pair skill generate gap-name
```

---

## Flow Commands (Deprecated)

> ⚠️ **DEPRECATED:** Flows are deprecated in favor of skills. Use `bpsai-pair skill` commands instead.
> See [Migration Guide](../../../docs/MIGRATION.md) for conversion instructions.

| Command | Description |
|---------|-------------|
| `flow list` | List available flows |
| `flow show <name>` | Show flow details |
| `flow run <name>` | Run a flow |
| `flow validate <name>` | Validate flow definition |

---

## Orchestration Commands

| Command | Description |
|---------|-------------|
| `orchestrate task <id>` | Route task to best agent |
| `orchestrate analyze <id>` | Analyze task complexity |
| `orchestrate handoff <id>` | Create handoff package |
| `orchestrate auto-run` | Run single task workflow |
| `orchestrate auto-session` | Run autonomous session |
| `orchestrate workflow-status` | Show current workflow state |

### Examples

```bash
# Analyze task complexity
bpsai-pair orchestrate analyze TASK-001

# Create handoff for another agent
bpsai-pair orchestrate handoff TASK-001 \
  --from claude-code --to codex \
  --progress "Completed step 1 and 2"

# Run autonomous session
bpsai-pair orchestrate auto-session --max-tasks 3
```

---

## Intent Commands

| Command | Description |
|---------|-------------|
| `intent detect <text>` | Detect work intent from text |
| `intent should-plan <text>` | Check if planning needed |
| `intent suggest-flow <text>` | Suggest appropriate workflow |

### Examples

```bash
bpsai-pair intent detect "fix the login bug"
# Output: bugfix

bpsai-pair intent should-plan "refactor the database layer"
# Output: true

bpsai-pair intent suggest-flow "review the PR"
# Output: reviewing-code
```

---

## GitHub Commands

| Command | Description |
|---------|-------------|
| `github status` | Check GitHub connection |
| `github create` | Create a pull request |
| `github list` | List pull requests |
| `github merge <pr>` | Merge PR and update task |
| `github link <task>` | Link task to PR |
| `github auto-pr` | Auto-create PR from branch |
| `github archive-merged` | Archive tasks for merged PRs |

### Examples

```bash
# Auto-create PR from branch (detects TASK-xxx)
bpsai-pair github auto-pr
bpsai-pair github auto-pr --no-draft

# Archive all tasks for merged PRs
bpsai-pair github archive-merged --all
```

---

## Standup Commands

| Command | Description |
|---------|-------------|
| `standup generate` | Generate daily summary |
| `standup post` | Post summary to Trello |

### Examples

```bash
bpsai-pair standup generate --format slack
bpsai-pair standup generate --since 48  # Last 48 hours
bpsai-pair standup post
```

---

## Metrics Commands

| Command | Description |
|---------|-------------|
| `metrics summary` | Show metrics for time period |
| `metrics task <id>` | Show metrics for a task |
| `metrics breakdown` | Cost breakdown by dimension |
| `metrics budget` | Show budget status |
| `metrics export` | Export metrics to file |
| `metrics velocity` | Show velocity metrics |
| `metrics burndown` | Show burndown chart data |
| `metrics accuracy` | Show estimation accuracy |
| `metrics tokens` | Show token usage |

### Examples

```bash
bpsai-pair metrics summary
bpsai-pair metrics breakdown --by model
bpsai-pair metrics export --format csv --output metrics.csv
```

---

## Budget Commands

| Command | Description |
|---------|-------------|
| `budget estimate` | Estimate task token cost |
| `budget status` | Show current budget usage |
| `budget check` | Check if task fits budget |

### Examples

```bash
bpsai-pair budget status
bpsai-pair budget estimate TASK-001
bpsai-pair budget check --task TASK-001
```

---

## Timer Commands

| Command | Description |
|---------|-------------|
| `timer start <task>` | Start timer for a task |
| `timer stop` | Stop current timer |
| `timer status` | Show current timer |
| `timer show <task>` | Show time entries |
| `timer summary` | Show time summary |

### Examples

```bash
bpsai-pair timer start TASK-001
bpsai-pair timer status
bpsai-pair timer stop
bpsai-pair timer summary --plan plan-2025-12-feature
```

---

## Benchmark Commands

| Command | Description |
|---------|-------------|
| `benchmark run` | Run benchmark suite |
| `benchmark results` | View results |
| `benchmark compare` | Compare agents |
| `benchmark list` | List benchmarks |

### Examples

```bash
bpsai-pair benchmark run --suite default
bpsai-pair benchmark results --latest
bpsai-pair benchmark compare claude-code codex
```

---

## Cache Commands

| Command | Description |
|---------|-------------|
| `cache stats` | Show cache statistics |
| `cache clear` | Clear context cache |
| `cache invalidate <file>` | Invalidate specific file |

### Examples

```bash
bpsai-pair cache stats
bpsai-pair cache clear
bpsai-pair cache invalidate .paircoder/context/state.md
```

---

## Session Commands

| Command | Description |
|---------|-------------|
| `session check` | Check session status (quiet mode for hooks) |
| `session status` | Show detailed session info with budget |

### Examples

```bash
bpsai-pair session check --quiet
bpsai-pair session status
```

---

## Compaction Commands

| Command | Description |
|---------|-------------|
| `compaction snapshot save` | Save context snapshot |
| `compaction snapshot list` | List snapshots |
| `compaction check` | Check for compaction events |
| `compaction recover` | Recover from compaction |
| `compaction cleanup` | Clean old snapshots |

### Examples

```bash
bpsai-pair compaction snapshot save --trigger "manual"
bpsai-pair compaction snapshot list
bpsai-pair compaction check
bpsai-pair compaction recover
bpsai-pair compaction cleanup --older-than 7
```

---

## Security Commands

| Command | Description |
|---------|-------------|
| `security scan-secrets` | Scan for leaked secrets |
| `security pre-commit` | Run pre-commit checks |
| `security install-hook` | Install git hooks |
| `security scan-deps` | Scan dependency vulnerabilities |

### Examples

```bash
bpsai-pair security scan-secrets --staged
bpsai-pair security scan-deps
bpsai-pair security install-hook
```

---

## Migrate Commands

| Command | Description |
|---------|-------------|
| `migrate` | Run pending migrations |
| `migrate status` | Show migration status |

### Examples

```bash
bpsai-pair migrate status
bpsai-pair migrate
```

---

## Trello Commands

| Command | Description |
|---------|-------------|
| `trello connect` | Connect to Trello |
| `trello status` | Check connection |
| `trello disconnect` | Remove credentials |
| `trello boards` | List available boards |
| `trello use-board <id>` | Set active board |
| `trello lists` | Show board lists |
| `trello config` | View/modify config |
| `trello progress <task>` | Post progress comment |
| `trello webhook serve` | Start webhook server |
| `trello webhook status` | Check webhook status |

### Examples

```bash
bpsai-pair trello connect
bpsai-pair trello boards
bpsai-pair trello use-board 694176ebf4b9d27c6e7a0e73
bpsai-pair trello status
bpsai-pair trello progress TASK-001 --completed "Feature done"
```

---

## Trello Task Commands (ttask)

| Command | Description |
|---------|-------------|
| `ttask list` | List tasks from board |
| `ttask show <id>` | Show task details |
| `ttask start <id>` | Start working on task |
| `ttask done <id>` | Complete task |
| `ttask block <id>` | Mark as blocked |
| `ttask comment <id>` | Add comment |
| `ttask move <id>` | Move to different list |

### Examples

```bash
# List and show
bpsai-pair ttask list
bpsai-pair ttask list --list "In Progress"
bpsai-pair ttask show TRELLO-abc123

# Lifecycle
bpsai-pair ttask start TRELLO-abc123
bpsai-pair ttask done TRELLO-abc123 --summary "Implemented feature" --list "Deployed/Done"
bpsai-pair ttask block TRELLO-abc123 --reason "Waiting for API"

# Comments
bpsai-pair ttask comment TRELLO-abc123 "50% complete"
```

### When to Use `task` vs `ttask`

| Scenario | Command |
|----------|---------|
| Working with local task files | `task` |
| Need hooks to fire (timer, state.md) | `task update` |
| Working directly with Trello cards | `ttask` |
| Adding progress comments to cards | `ttask comment` |
| Card doesn't have local task file | `ttask` |
| Card has linked local task | Either works |

**Recommended workflow:**
- Use `task update` for status changes (fires all hooks)
- Use `ttask comment` for progress notes
- Use `ttask` commands when Trello is your only source

---

## MCP Commands

| Command | Description |
|---------|-------------|
| `mcp serve` | Start MCP server (stdio transport) |
| `mcp tools` | List available tools |
| `mcp test <tool>` | Test tool locally |

### Examples

```bash
bpsai-pair mcp serve
bpsai-pair mcp tools
bpsai-pair mcp test paircoder_task_list
```

### Available MCP Tools (13)

| Tool | Description |
|------|-------------|
| `paircoder_task_list` | List tasks with filters |
| `paircoder_task_next` | Get next recommended task |
| `paircoder_task_start` | Start a task |
| `paircoder_task_complete` | Complete a task |
| `paircoder_context_read` | Read project context |
| `paircoder_plan_status` | Get plan progress |
| `paircoder_plan_list` | List available plans |
| `paircoder_orchestrate_analyze` | Analyze task complexity |
| `paircoder_orchestrate_handoff` | Create handoff package |
| `paircoder_metrics_record` | Record token usage |
| `paircoder_metrics_summary` | Get metrics summary |
| `paircoder_trello_sync_plan` | Sync plan to Trello |
| `paircoder_trello_update_card` | Update Trello card |

---

## Configuration

### Config File Location

`.paircoder/config.yaml`

### Key Settings

```yaml
version: "2.8"

project:
  name: "my-project"
  description: "Project description"
  primary_goal: "Main objective"
  coverage_target: 80

models:
  navigator: claude-opus-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5

routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }

token_budget:
  warning_threshold: 75
  critical_threshold: 90

hooks:
  enabled: true
  on_task_start:
    - check_token_budget
    - start_timer
    - sync_trello
    - update_state
  on_task_complete:
    - stop_timer
    - record_metrics
    - sync_trello
    - update_state
    - check_unblocked
  on_task_block:
    - sync_trello
    - update_state

trello:
  enabled: true
  board_id: "your-board-id"
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `TRELLO_API_KEY` | Trello API key |
| `TRELLO_TOKEN` | Trello OAuth token |
| `GITHUB_TOKEN` | GitHub personal access token |
| `TOGGL_API_TOKEN` | Toggl time tracking token |
| `PAIRCODER_CONFIG` | Override config file path |

---

## Common Workflows

### Start of Day

```bash
bpsai-pair status           # Check current state
bpsai-pair task list        # See pending tasks
bpsai-pair task next        # Find what to work on
bpsai-pair task update TASK-XXX --status in_progress
```

### During Work (Progress Updates)

```bash
bpsai-pair ttask comment TASK-XXX "Completed API, starting tests"
```

### End of Task

```bash
pytest -v                   # Run tests
git add -A
git commit -m "feat: TASK-XXX - description"
bpsai-pair task update TASK-XXX --status done
bpsai-pair task next        # See what's next
```

### End of Day

```bash
bpsai-pair standup generate # Generate summary
git push                    # Push changes
```

### Sprint Planning

```bash
bpsai-pair plan new sprint-15 --type feature --title "Security & Sandboxing"
# Add tasks to plan...
bpsai-pair plan sync-trello plan-2025-12-sprint-15-security
bpsai-pair trello status    # Verify cards created
```

### Working Directly with Trello

```bash
bpsai-pair ttask list --agent             # Show AI-assigned cards
bpsai-pair ttask start TRELLO-abc123      # Start card
# ... do work ...
bpsai-pair ttask done TRELLO-abc123 --summary "Feature complete" --list "Deployed/Done"
```

### Exporting Skills

```bash
# Export to Cursor
bpsai-pair skill export --all --format cursor

# Export to Windsurf
bpsai-pair skill export my-skill --format windsurf

# Preview export
bpsai-pair skill export my-skill --format continue --dry-run
```
