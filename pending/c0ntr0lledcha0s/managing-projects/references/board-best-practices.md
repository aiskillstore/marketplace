# Project Board Best Practices

## Board Templates

### Kanban (Default)
```
Backlog → Todo → In Progress → In Review → Done
```
Best for: Continuous flow, maintenance

### Sprint
```
Backlog → Sprint Backlog → In Progress → Review → Done
```
Best for: Time-boxed iterations

### Roadmap
```
Q1 → Q2 → Q3 → Q4
```
Best for: Long-term planning

## Column Guidelines

| Column | WIP Limit | Purpose |
|--------|-----------|---------|
| Backlog | None | Unprioritized work |
| Todo | 10 | Ready to start |
| In Progress | 3 per person | Active work |
| In Review | 5 | Awaiting review |
| Done | None | Completed |

## Custom Fields

### Essential Fields
- **Status** (SingleSelect): Workflow state
- **Priority** (SingleSelect): High/Medium/Low
- **Sprint** (Iteration): Time period
- **Estimate** (Number): Story points

### Optional Fields
- **Due Date** (Date): Deadlines
- **Assignee** (Text): Owner
- **Type** (SingleSelect): Bug/Feature/Task

## Automation Rules

### Auto-add
- New issues → Backlog
- New PRs → In Review

### Auto-move
- PR merged → Done
- Issue closed → Done

### Auto-archive
- Done items after 7 days

## Views Configuration

### Table View
- Default for backlog grooming
- Show: Title, Status, Priority, Assignee

### Board View
- Default for sprint tracking
- Group by: Status
- Filter: Current sprint

### Roadmap View
- Long-term planning
- Group by: Milestone or Quarter

## Workflow Patterns

### Feature Development
1. Create issue → Backlog
2. Refine → Sprint Backlog
3. Start work → In Progress
4. Submit PR → In Review
5. Merge → Done

### Bug Triage
1. Report → Backlog
2. Triage → Prioritize
3. Schedule → Sprint Backlog
4. Fix → In Progress
5. Verify → Done

## Anti-Patterns

- Too many columns (> 7)
- No WIP limits
- Stale items (> 30 days untouched)
- Missing automation
- No regular grooming
