# Quetrex Development Workflow Skill

**Purpose:** Bootstrap new Claude Code sessions with complete Quetrex project context and enable efficient issue-driven development.

**When to Use:**
- At the start of any new Claude Code session working on Quetrex
- When you need to understand what work is pending
- When creating issues for AI agent automation
- When deciding what to work on next

---

## Quick Reference

### Key Commands

```bash
# Query pending issues
gh issue list --label "ai-feature" --state open

# Query recent completed work
gh pr list --state merged --limit 10

# Create issue for AI agent
gh issue create --template ai-feature.md --label ai-feature

# Trigger workflow manually
gh workflow run "Quetrex AI Agent Worker" -f issue_number=123
```

### Critical Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context (loaded every session) |
| `.quetrex/status.yml` | Current roadmap position |
| `docs/PROJECT-CHECKLIST.md` | Comprehensive task checklist |
| `.github/workflows/ai-agent.yml` | Agent automation workflow |
| `.claude/scripts/ai-agent-worker.py` | Agent execution script |

---

## 1. What is Quetrex?

**Quetrex** is a voice-first AI agent control center - a mission control dashboard for managing multiple AI-powered projects.

### Core Capabilities
- Voice-driven requirements gathering (OpenAI Realtime API)
- Automatic spec generation (Claude AI)
- Spec approval workflow with versioning
- Automated agent spawning via GitHub Actions
- Real-time monitoring and analytics
- Cost tracking and controls
- Security-first architecture (3-phase model)

### Tech Stack
- **Frontend:** Next.js 15.5, React 19, TypeScript (strict), TailwindCSS, ShadCN UI
- **Backend:** Next.js API Routes, Drizzle ORM, PostgreSQL
- **AI/Voice:** Claude Sonnet 4.5, OpenAI Realtime API, Whisper, TTS
- **Infrastructure:** Vercel Edge Runtime, Docker containers, GitHub Actions

---

## 2. How the Automation Works

### Trigger Flow

```
1. Create GitHub Issue
   └─> Use "AI Feature Request" template
   └─> Add "ai-feature" label

2. GitHub Actions Triggers
   └─> .github/workflows/ai-agent.yml activates
   └─> Runs in secure Docker container

3. Agent Worker Executes
   └─> Fetches issue details
   └─> Loads project context from .quetrex/memory/
   └─> Builds comprehensive prompt
   └─> Executes via Claude Code CLI

4. Implementation Phase
   └─> Agent uses specialized sub-agents:
       - orchestrator (complex features)
       - test-writer (TDD first)
       - implementation (code)
       - code-reviewer (quality)

5. Quality Gates
   └─> PreToolUse: Blocks dangerous commands
   └─> PostToolUse: Validates changes
   └─> Stop: Unbypassable final gate
   └─> Tests, coverage, linting, build

6. Pull Request Created
   └─> Feature branch pushed
   └─> PR with detailed description
   └─> Ready for human review
```

### Constraints Per Issue
- **Max execution time:** 45 minutes
- **Max API calls:** 150
- **Max file changes:** 75
- **Tests required:** Configurable (currently false)

---

## 3. Creating Effective Issues

### Issue Template Location
`.github/ISSUE_TEMPLATE/ai-feature.md`

### What Makes a Good AI-Agent Issue

**DO:**
- Be specific about what needs to be built
- List acceptance criteria as checkboxes
- Reference existing files/patterns to follow
- Specify testing requirements
- Include priority level

**DON'T:**
- Be vague ("make it better")
- Combine multiple unrelated tasks
- Skip acceptance criteria
- Forget to add `ai-feature` label

### Example Well-Structured Issue

```markdown
## Summary
Add cost tracking display to project cards in dashboard

## Description
Each project card should show the current month's API costs
with a small trend indicator (up/down arrow).

## Acceptance Criteria
- [ ] Cost displayed in USD format ($X.XX)
- [ ] Trend arrow shows increase/decrease from last week
- [ ] Tooltip shows breakdown by provider (OpenAI/Anthropic)
- [ ] Updates every 5 minutes via React Query

## Technical Context
**Relevant Files:**
- `src/components/ProjectCard.tsx` - Add cost display
- `src/services/cost-tracker.ts` - Use existing service
- `src/hooks/useDashboard.ts` - Add cost query

**Patterns to Follow:**
- Use existing stats display pattern from dashboard header
- Follow cost formatting from SettingsPanel

## Testing Requirements
- [x] Unit tests required (cost formatting)
- [x] Integration tests required (API integration)
- [ ] E2E tests required
- [ ] Visual regression tests required

## Priority
- [x] P1 - High (needed soon)
```

---

## 4. Current Project Status

### How to Query Live State

```bash
# Open issues ready for AI agent
gh issue list --label "ai-feature" --state open --json number,title,labels

# Recently completed work
gh pr list --state merged --limit 5 --json number,title,mergedAt

# Current branch status
git status
git log --oneline -5
```

### Status File Location
`.quetrex/status.yml` - Maintained snapshot of:
- Current phase
- Active focus areas
- Completion percentages
- Recent milestones

### Project Checklist
`docs/PROJECT-CHECKLIST.md` - Comprehensive tracking:
- Feature completion by category
- Blockers and dependencies
- Priority levels
- Time estimates

---

## 5. Architecture Decisions

### Key ADRs to Know

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Browser native echo cancellation | Accepted |
| ADR-002 | Drizzle ORM for Edge Runtime | Accepted |
| ADR-006 | Claude Code CLI over Anthropic SDK | Active |

### Security Architecture (3-Phase)

1. **Phase 1 (Complete):** Docker containerization
   - Read-only filesystem, non-root user
   - Resource limits, capability dropping

2. **Phase 2 (In Production):** Credential proxy
   - No credentials in container environment
   - Unix socket validation, audit logging

3. **Phase 3 (Q1 2026):** gVisor migration
   - User-space kernel for maximum isolation

### Agent Execution Architecture

**We use Claude Code CLI, NOT direct Anthropic SDK.**

Reasons:
- Built-in specialized agents (orchestrator, test-writer, code-reviewer)
- Quality hooks (PreToolUse, PostToolUse, Stop)
- Automatic updates from Anthropic
- No maintenance burden for tool execution

See: `.claude/docs/ARCHITECTURE-AGENT-WORKER.md`

---

## 6. Quality Enforcement

### 6-Layer Defense System

1. **PreToolUse Hook** - Blocks dangerous commands
2. **PostToolUse Hook** - Validates every file change
3. **Stop Hook** - Unbypassable quality gate
4. **TypeScript Strict** - No `any`, no `@ts-ignore`
5. **Test Coverage** - 75%+ overall, 90%+ services
6. **CI/CD** - Prevents merge if any check fails

### Test Requirements

```
Overall:        75%+ (enforced)
src/services/: 90%+ (enforced)
src/utils/:    90%+ (enforced)
Components:    60%+ (enforced)
```

### TDD Workflow (Mandatory)

1. Write test describing behavior
2. Verify test FAILS (red)
3. Write minimal code to pass
4. Verify test PASSES (green)
5. Refactor while keeping green

---

## 7. Development Patterns

### File Organization

```
src/
├── app/           # Next.js App Router pages
├── components/    # React components
├── services/      # Business logic (90%+ coverage)
├── hooks/         # Custom React hooks
├── lib/           # Third-party integrations
├── db/            # Database schema (Drizzle)
└── schemas/       # Zod validation schemas
```

### Naming Conventions

- Components: `PascalCase.tsx`
- Services: `kebab-case.ts`
- Hooks: `useCamelCase.ts`
- Types: Adjacent `types.ts` or inline

### Import Order

1. External packages
2. Internal components (`@/components/`)
3. Hooks (`@/hooks/`)
4. Services (`@/services/`)
5. Types

---

## 8. Common Workflows

### Starting a New Feature

```bash
# 1. Check what's pending
gh issue list --label "ai-feature" --state open

# 2. If nothing suitable, create new issue
gh issue create --template ai-feature.md

# 3. Add label to trigger automation
gh issue edit <number> --add-label "ai-feature"

# 4. Or work on it directly from here
# (for complex features or when you want more control)
```

### Reviewing AI Agent Work

```bash
# Check recent PRs
gh pr list --author "github-actions[bot]" --state open

# Review specific PR
gh pr view <number>
gh pr diff <number>

# Merge if approved
gh pr merge <number> --squash
```

### Debugging Failed Runs

```bash
# List recent workflow runs
gh run list --workflow="ai-agent.yml" --limit 5

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id> -n agent-logs-<issue-number>
```

---

## 9. Memory System

### Location: `.quetrex/memory/`

| File | Purpose |
|------|---------|
| `patterns.md` | Architectural patterns to follow |
| `project-overview.md` | High-level project context |
| `PHASE_3_EVOLVER.md` | Phase 3 documentation |
| `ARCHITECTURE-INTELLIGENCE-SYSTEM.md` | Architecture intelligence |

### Status Tracking: `.quetrex/status.yml`

Updated after each session with:
- Current focus area
- Recent completions
- Pending priorities
- Blockers

---

## 10. Getting Help

### Documentation Locations

- **Architecture:** `docs/architecture/`
- **Features:** `docs/features/`
- **Roadmap:** `docs/roadmap/`
- **ADRs:** `docs/decisions/`

### Key Documents

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Primary project context |
| `docs/PROJECT-CHECKLIST.md` | Comprehensive task list |
| `docs/AI-AGENT-AUTOMATION-STATUS.md` | Agent system status |
| `docs/CONTRIBUTING.md` | Development standards |

---

## Session Checklist

When starting a new session:

- [ ] Run `/new-context` to load this skill and query state
- [ ] Review pending issues (`gh issue list --label ai-feature`)
- [ ] Check recent PRs for context on recent work
- [ ] Decide: Create issue for agent OR work directly
- [ ] Follow TDD: Write tests FIRST
- [ ] Use specialized agents for complex features
- [ ] Update `.quetrex/status.yml` before ending session

---

*Last Updated: 2025-11-26*
*Created by Glen Barnhardt with help from Claude Code*
