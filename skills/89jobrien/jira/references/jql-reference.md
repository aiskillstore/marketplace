---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: jira
---

# JQL (Jira Query Language) Reference

JQL is used to search for issues in Jira. Queries follow the pattern:
`field operator value [AND/OR field operator value]`

## Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `status = "In Progress"` |
| `!=` | Not equals | `assignee != currentUser()` |
| `>` | Greater than | `created > -7d` |
| `>=` | Greater than or equal | `priority >= High` |
| `<` | Less than | `duedate < endOfWeek()` |
| `<=` | Less than or equal | `updated <= -1w` |
| `~` | Contains (text search) | `summary ~ "bug"` |
| `!~` | Does not contain | `description !~ "test"` |
| `IN` | In list | `status IN ("Open", "In Progress")` |
| `NOT IN` | Not in list | `priority NOT IN (Low, Lowest)` |
| `IS` | Is (for empty/null) | `assignee IS EMPTY` |
| `IS NOT` | Is not empty | `fixVersion IS NOT EMPTY` |
| `WAS` | Previous value | `status WAS "Open"` |
| `WAS IN` | Was in list | `status WAS IN ("Open", "Reopened")` |
| `WAS NOT` | Was not value | `assignee WAS NOT jsmith` |
| `CHANGED` | Field changed | `status CHANGED` |

## Common Fields

### Issue Fields

- `project` - Project key (e.g., "AOP")
- `issuetype` - Issue type (Task, Bug, Story, Epic)
- `status` - Current status
- `summary` - Issue title (text search with ~)
- `description` - Issue description (text search with ~)
- `priority` - Priority level
- `resolution` - Resolution status
- `labels` - Issue labels

### People Fields

- `assignee` - Assigned user
- `reporter` - Issue creator
- `creator` - Same as reporter
- `watcher` - Users watching

### Date Fields

- `created` - Creation date
- `updated` - Last update date
- `duedate` - Due date
- `resolved` - Resolution date
- `lastViewed` - Last viewed date

### Agile Fields

- `sprint` - Sprint name or ID
- `fixVersion` - Fix version
- `affectedVersion` - Affected version
- `component` - Component name
- `epic` - Epic link (for stories)
- `parent` - Parent issue (for subtasks)

## Functions

### User Functions

- `currentUser()` - Logged-in user
- `membersOf("group")` - Members of a group

### Date Functions

- `now()` - Current timestamp
- `startOfDay()` - Start of today
- `endOfDay()` - End of today
- `startOfWeek()` - Start of current week
- `endOfWeek()` - End of current week
- `startOfMonth()` - Start of current month
- `endOfMonth()` - End of current month
- `startOfYear()` - Start of current year
- `endOfYear()` - End of current year

### Sprint Functions

- `openSprints()` - Active sprints
- `closedSprints()` - Completed sprints
- `futureSprints()` - Planned sprints

### Other Functions

- `issueHistory()` - Issues in history
- `linkedIssues(KEY)` - Issues linked to KEY
- `votedIssues()` - Issues you voted for
- `watchedIssues()` - Issues you're watching

## Relative Dates

Use relative time with +/- and units:

- `1d` - 1 day
- `1w` - 1 week
- `1m` - 1 month (note: not minutes)
- `1y` - 1 year
- `1h` - 1 hour

Examples:

- `-7d` - 7 days ago
- `-2w` - 2 weeks ago
- `+1d` - 1 day from now

## Common JQL Patterns

### My Open Issues

```
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC
```

### Issues Updated Recently

```
updated >= -1d ORDER BY updated DESC
```

### Bugs in Current Sprint

```
issuetype = Bug AND sprint in openSprints()
```

### Unassigned Issues in Project

```
project = AOP AND assignee IS EMPTY AND status != Done
```

### Issues Due This Week

```
duedate >= startOfWeek() AND duedate <= endOfWeek()
```

### High Priority Blockers

```
priority = Highest AND status != Done AND issuetype = Bug
```

### My Team's Work

```
assignee IN membersOf("my-team") AND sprint in openSprints()
```

### Recently Created by Me

```
reporter = currentUser() AND created >= -7d
```

### Issues Changed Status Today

```
status CHANGED AFTER startOfDay()
```

### Text Search

```
summary ~ "login" OR description ~ "authentication"
```

### Complex Query

```
project = AOP
AND issuetype IN (Bug, Task)
AND status NOT IN (Done, Closed)
AND (assignee = currentUser() OR assignee IS EMPTY)
ORDER BY priority DESC, created ASC
```

## ORDER BY

Sort results with ORDER BY:

- `ORDER BY created DESC` - Newest first
- `ORDER BY priority DESC, updated DESC` - By priority, then update date
- `ORDER BY rank ASC` - Board ranking order

## Tips

1. Quote values with spaces: `status = "In Progress"`
2. Field names are case-insensitive
3. Use parentheses for complex logic: `(A OR B) AND C`
4. Escape special chars with backslash: `summary ~ "test\-case"`
5. Empty check: `field IS EMPTY` not `field = ""`
