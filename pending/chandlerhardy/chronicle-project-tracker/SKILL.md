---
name: chronicle-project-tracker
description: Manage Chronicle project development using database-tracked milestones, next steps, and roadmap visualization. Works with MCP tools (fast, structured) or CLI commands (portable). Use when planning features, tracking progress, viewing roadmap, or linking sessions to milestones. Eliminates manual DEVELOPMENT_HISTORY.md updates.
---

# Chronicle Project Tracker

This skill helps you manage project development meta-state using Chronicle's built-in project tracking features. Use MCP tools for programmatic access or CLI commands for portability.

## Auto-Activation

> **This skill auto-activates!** (Milestone #13)
>
> Prompts like "what's next?" or "show roadmap" automatically trigger this skill. No manual loading needed!
>
> **Trigger patterns:** what's next, show roadmap, create milestone, track progress
> **See:** `docs/HOOKS.md` for full details

## When to Use This Skill

Use this skill when:
- Planning new features or milestones
- Tracking development progress
- Viewing project roadmap
- Linking sessions to milestones
- Checking what's in progress or planned
- Answering "what should I work on next?"
- Generating progress reports

## Available Tools (MCP + CLI)

### MCP Tools (Programmatic Access)

**Query Tools:**
- `mcp__chronicle__get_milestones(status, milestone_type, limit)` - List milestones
- `mcp__chronicle__get_milestone(milestone_id)` - Get milestone details
- `mcp__chronicle__get_next_steps(completed, milestone_id, limit)` - List next steps
- `mcp__chronicle__get_roadmap(days)` - View project roadmap

**Update Tools:**
- `mcp__chronicle__update_milestone_status(milestone_id, new_status)` - Update status
- `mcp__chronicle__complete_next_step(step_id)` - Mark step complete

### CLI Commands (Portable)

**See "CLI Commands Reference" section below for full list.**

Key commands:
- `chronicle milestones` - List milestones
- `chronicle roadmap` - View roadmap
- `chronicle next-steps` - List next steps
- `chronicle milestone-complete <id>` - Mark complete

## Workflow: Planning a New Feature

When user wants to add a new feature:

1. **Check existing roadmap** to avoid duplicates:
   ```python
   roadmap = mcp__chronicle__get_roadmap(days=30)
   # Review planned milestones
   ```

2. **Create milestone** via CLI (user runs this):
   ```bash
   chronicle milestone "Feature name" \
     --description "What it does" \
     --type feature \
     --priority 1 \
     --tags "phase-5,api,backend"
   ```

3. **Break down into next steps**:
   ```bash
   chronicle next-step "Design API endpoints" --priority 1 --effort medium --milestone <ID>
   chronicle next-step "Write tests" --priority 2 --effort small --milestone <ID>
   chronicle next-step "Document in README" --priority 3 --effort small --milestone <ID>
   ```

4. **Update status when starting work**:
   ```python
   mcp__chronicle__update_milestone_status(milestone_id=1, new_status="in_progress")
   ```

## Workflow: Session Linking

When completing a development session:

1. **Get session ID** from recent sessions:
   ```python
   sessions = mcp__chronicle__get_sessions(limit=5)
   latest_session_id = sessions[0]['id']
   ```

2. **Find active milestone**:
   ```python
   milestones = mcp__chronicle__get_milestones(status="in_progress")
   active_milestone_id = milestones[0]['id']
   ```

3. **Link them** (user runs this):
   ```bash
   chronicle link-session <session_id> --milestone <milestone_id>
   ```

4. **Complete next steps** as work progresses:
   ```python
   mcp__chronicle__complete_next_step(step_id=1)
   ```

## Workflow: Generating Progress Reports

When user asks "what did I accomplish this week?":

1. **Get roadmap**:
   ```python
   roadmap = mcp__chronicle__get_roadmap(days=7)
   ```

2. **Extract info**:
   - `roadmap['recently_completed']` - Milestones completed in last 7 days
   - `roadmap['in_progress']` - Current active work
   - `roadmap['summary']` - Statistics

3. **Get linked sessions** for each completed milestone:
   ```python
   for milestone in roadmap['recently_completed']:
       milestone_details = mcp__chronicle__get_milestone(milestone['id'])
       sessions = milestone_details['linked_sessions']
       # Summarize work done
   ```

4. **Format report** showing:
   - Completed milestones with linked sessions
   - Git commits from those sessions
   - Time spent (from session durations)
   - Key files modified

## Workflow: Viewing Roadmap

When user asks "what's next?" or "show me the roadmap":

```python
# Get full roadmap
roadmap = mcp__chronicle__get_roadmap(days=7)

# Present in organized format:
print("🚧 IN PROGRESS:")
for m in roadmap['in_progress']:
    print(f"  - {m['title']} ({len(m['related_sessions'])} sessions)")

print("\n📋 PLANNED (High Priority):")
for m in roadmap['planned_high_priority']:
    print(f"  - [P{m['priority']}] {m['title']}")

print("\n🔜 NEXT STEPS:")
for step in roadmap['pending_next_steps']:
    effort = f" [{step['estimated_effort']}]" if step['estimated_effort'] else ""
    print(f"  - [P{step['priority']}] {step['description']}{effort}")

print("\n✅ RECENTLY COMPLETED:")
for m in roadmap['recently_completed']:
    print(f"  - {m['title']} ({m['completed_at']})")
```

## Workflow: Completing a Milestone

When all work for a milestone is done:

1. **Verify all next steps completed**:
   ```python
   steps = mcp__chronicle__get_next_steps(milestone_id=<ID>, completed=False)
   if len(steps['next_steps']) == 0:
       # All done!
   ```

2. **Mark milestone complete** (user runs):
   ```bash
   chronicle milestone-complete <ID>
   ```

3. **Auto-generates documentation** by querying:
   ```python
   milestone = mcp__chronicle__get_milestone(<ID>)
   # Has all linked sessions, commits, duration
   # Can auto-update DEVELOPMENT_HISTORY.md or export to Obsidian
   ```

## Querying Examples

### "What features are in progress?"
```python
milestones = mcp__chronicle__get_milestones(status="in_progress")
for m in milestones['milestones']:
    sessions = len(m['related_sessions'])
    print(f"{m['title']}: {sessions} sessions so far")
```

### "What's the highest priority work?"
```python
roadmap = mcp__chronicle__get_roadmap()
top_planned = roadmap['planned_high_priority'][0]
print(f"Next up: {top_planned['title']} (P{top_planned['priority']})")
```

### "Show me all optimization work"
```python
milestones = mcp__chronicle__get_milestones(milestone_type="optimization")
```

### "What work did session 16 contribute to?"
```python
# Get all milestones
all_milestones = mcp__chronicle__get_milestones(limit=100)
for m in all_milestones['milestones']:
    if 16 in m['related_sessions']:
        print(f"Session 16 worked on: {m['title']}")
```

## Statistics & Reports

### Weekly Progress Report
```python
roadmap = mcp__chronicle__get_roadmap(days=7)

completed_count = len(roadmap['recently_completed'])
in_progress_count = len(roadmap['in_progress'])

print(f"Week of {date}:")
print(f"✅ {completed_count} milestones completed")
print(f"🚧 {in_progress_count} milestones in progress")
print(f"⏰ {roadmap['summary']['total_next_steps'] - roadmap['summary']['completed_next_steps']} pending tasks")
```

### Milestone Velocity
```python
# Get all completed milestones
completed = mcp__chronicle__get_milestones(status="completed", limit=100)

# Calculate average time from creation to completion
durations = []
for m in completed['milestones']:
    created = datetime.fromisoformat(m['created_at'])
    completed_at = datetime.fromisoformat(m['completed_at'])
    durations.append((completed_at - created).days)

avg_days = sum(durations) / len(durations)
print(f"Average milestone completion time: {avg_days:.1f} days")
```

## Auto-Documentation Pattern

Instead of manually updating DEVELOPMENT_HISTORY.md:

```python
# Query completed milestones
completed = mcp__chronicle__get_milestones(status="completed")

# For each milestone, get details
for milestone in completed['milestones']:
    details = mcp__chronicle__get_milestone(milestone['id'])

    # Extract:
    # - Title, description
    # - Related sessions (with summaries)
    # - Related commits (with messages)
    # - Duration (from session data)
    # - Files modified (from commits)

    # Generate markdown section
    md = f"### {details['title']}\n"
    md += f"{details['description']}\n\n"
    md += f"**Status**: {details['status']}\n"
    md += f"**Sessions**: {len(details['linked_sessions'])}\n"
    md += f"**Commits**: {len(details['linked_commits'])}\n"

    # Could write to DEVELOPMENT_HISTORY.md or Obsidian
```

## Integration with Other Skills

### With chronicle-workflow
After completing a session, use this skill to:
- Link session to active milestone
- Mark next steps as complete
- Check roadmap for what to work on next

### With chronicle-session-documenter
When documenting a session to Obsidian:
- Include milestone information
- Add wikilinks to related milestones
- Tag with milestone tags

### With chronicle-context-retriever
When searching past work:
- Filter by milestone
- Find all sessions for a feature
- See historical progress on similar work

## CLI Commands Reference

**Milestones:**
```bash
chronicle milestone "Title" --description "Desc" --type feature --priority 1 --tags "tag1,tag2"
chronicle milestones --status in_progress
chronicle milestone-show <ID>
chronicle milestone-status <ID> in_progress
chronicle milestone-complete <ID>
```

**Next Steps:**
```bash
chronicle next-step "Description" --priority 1 --effort medium --category feature --milestone <ID>
chronicle next-steps --milestone <ID>
chronicle next-step-complete <ID>
```

**Linking:**
```bash
chronicle link-session <session_id> --milestone <ID>
```

**Roadmap:**
```bash
chronicle roadmap --days 7
```

## Database Tables

### project_milestones
- `id` - Unique ID
- `title` - Milestone name
- `description` - Details
- `status` - planned, in_progress, completed, archived
- `milestone_type` - feature, bugfix, optimization, documentation
- `priority` - 1 (highest) to 5 (lowest)
- `created_at` - Creation timestamp
- `completed_at` - Completion timestamp
- `related_sessions` - JSON array of session IDs
- `related_commits` - JSON array of commit SHAs
- `tags` - JSON array of tags

### next_steps
- `id` - Unique ID
- `description` - What needs to be done
- `priority` - 1 (highest) to 5 (lowest)
- `estimated_effort` - small, medium, large
- `category` - feature, optimization, fix, docs
- `created_by` - session_16, manual, ai-suggestion
- `completed` - 0 or 1
- `created_at` - Creation timestamp
- `completed_at` - Completion timestamp
- `related_milestone_id` - FK to milestone

## Pro Tips

1. **Start milestones early** - Link sessions as you go
2. **Use priority levels** - Helps roadmap show what's important
3. **Tag milestones** - Makes filtering easier (e.g., "phase-5", "api", "frontend")
4. **Break down features** - Create next steps for each milestone
5. **Link sessions retroactively** - After work is done, link to milestone
6. **Query before planning** - Check roadmap to avoid duplicate work
7. **Use milestone types** - Distinguishes features from bugfixes
8. **Complete next steps** - Helps track progress within a milestone
9. **Auto-document** - Query completed milestones to generate reports
10. **Review roadmap weekly** - Stay aligned on priorities

## Benefits Over Manual Documentation

**Before (manual DEVELOPMENT_HISTORY.md):**
- Manual updates required
- Easy to forget to document
- Hard to query programmatically
- No linking between sessions/commits/features
- Becomes stale quickly

**After (database-tracked milestones):**
- Automatic tracking via MCP tools
- Queryable (e.g., "what's in progress?")
- Sessions auto-link to milestones
- Commits auto-link to sessions
- Real-time roadmap view
- Can generate reports on-demand
- Powers AI-driven development insights

## Example: Meta-Development

Chronicle uses Chronicle to track its own development:

```bash
# Milestone #1: Add project tracking to Chronicle
chronicle milestone "Add project tracking to Chronicle" \
  --description "Database-tracked milestones and next steps" \
  --type feature \
  --priority 1 \
  --tags "phase-5,project-tracking,meta"

# Break down work
chronicle next-step "Design database schema" --priority 1 --effort medium --milestone 1
chronicle next-step "Add CLI commands" --priority 1 --effort large --milestone 1
chronicle next-step "Add MCP tools" --priority 1 --effort medium --milestone 1
chronicle next-step "Create Chronicle Skills" --priority 2 --effort medium --milestone 1
chronicle next-step "Write tests" --priority 2 --effort small --milestone 1
chronicle next-step "Update documentation" --priority 3 --effort small --milestone 1

# Mark in progress
chronicle milestone-status 1 in_progress

# As work completes
chronicle next-step-complete 1
chronicle next-step-complete 2
# ... etc

# Link current session
chronicle link-session 18 --milestone 1

# When done
chronicle milestone-complete 1

# Generate report
chronicle milestone-show 1
```

This skill represents Chronicle's dogfooding: using Chronicle to build Chronicle!
