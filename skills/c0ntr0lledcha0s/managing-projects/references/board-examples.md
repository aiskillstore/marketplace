# Project Board Configuration Examples

## Sprint Board

### Field Configuration
```json
{
  "fields": [
    {
      "name": "Status",
      "type": "SINGLE_SELECT",
      "options": ["Backlog", "Sprint Backlog", "In Progress", "In Review", "Done"]
    },
    {
      "name": "Priority",
      "type": "SINGLE_SELECT",
      "options": ["Critical", "High", "Medium", "Low"]
    },
    {
      "name": "Sprint",
      "type": "ITERATION",
      "duration": 14,
      "startDay": "MONDAY"
    },
    {
      "name": "Story Points",
      "type": "NUMBER"
    },
    {
      "name": "Assignee",
      "type": "ASSIGNEES"
    }
  ]
}
```

### Board View Setup
- **Group by**: Status
- **Sort by**: Priority (descending), then Story Points
- **Filter**: Sprint = Current Sprint

### Automation
- New issues → Backlog
- PR opened → In Review
- PR merged → Done
- Issue closed → Done

---

## Kanban Board

### Field Configuration
```json
{
  "fields": [
    {
      "name": "Status",
      "type": "SINGLE_SELECT",
      "options": ["Icebox", "Todo", "In Progress", "Review", "Done"]
    },
    {
      "name": "Type",
      "type": "SINGLE_SELECT",
      "options": ["Bug", "Feature", "Chore", "Spike"]
    },
    {
      "name": "Size",
      "type": "SINGLE_SELECT",
      "options": ["XS", "S", "M", "L", "XL"]
    },
    {
      "name": "Due Date",
      "type": "DATE"
    }
  ]
}
```

### WIP Limits
| Column | Limit |
|--------|-------|
| Todo | 10 |
| In Progress | 3 per person |
| Review | 5 |

### Board View Setup
- **Group by**: Status
- **Color by**: Type
- **Sort by**: Due Date (ascending)

---

## Roadmap Board

### Field Configuration
```json
{
  "fields": [
    {
      "name": "Quarter",
      "type": "SINGLE_SELECT",
      "options": ["Q1", "Q2", "Q3", "Q4"]
    },
    {
      "name": "Theme",
      "type": "SINGLE_SELECT",
      "options": ["Core Features", "Performance", "UX", "Infrastructure"]
    },
    {
      "name": "Status",
      "type": "SINGLE_SELECT",
      "options": ["Planned", "In Progress", "Completed", "Deferred"]
    },
    {
      "name": "Target Date",
      "type": "DATE"
    },
    {
      "name": "Dependencies",
      "type": "TEXT"
    }
  ]
}
```

### Board View Setup
- **Layout**: Roadmap/Timeline
- **Group by**: Theme
- **Date field**: Target Date

---

## Bug Triage Board

### Field Configuration
```json
{
  "fields": [
    {
      "name": "Triage Status",
      "type": "SINGLE_SELECT",
      "options": ["New", "Triaged", "Scheduled", "In Progress", "Fixed", "Won't Fix"]
    },
    {
      "name": "Severity",
      "type": "SINGLE_SELECT",
      "options": ["Critical", "Major", "Minor", "Trivial"]
    },
    {
      "name": "Component",
      "type": "SINGLE_SELECT",
      "options": ["API", "Frontend", "Backend", "Database", "Infrastructure"]
    },
    {
      "name": "Reported Date",
      "type": "DATE"
    },
    {
      "name": "Workaround",
      "type": "TEXT"
    }
  ]
}
```

### Views
1. **Triage Queue**: Filter by Status = "New", Sort by Reported Date
2. **By Severity**: Group by Severity
3. **By Component**: Group by Component

---

## Release Board

### Field Configuration
```json
{
  "fields": [
    {
      "name": "Release Status",
      "type": "SINGLE_SELECT",
      "options": ["Queued", "In Development", "Testing", "Ready", "Released"]
    },
    {
      "name": "Release Version",
      "type": "SINGLE_SELECT",
      "options": ["v1.1.0", "v1.2.0", "v2.0.0"]
    },
    {
      "name": "Type",
      "type": "SINGLE_SELECT",
      "options": ["Feature", "Bug Fix", "Breaking Change"]
    },
    {
      "name": "Release Date",
      "type": "DATE"
    }
  ]
}
```

### Views
1. **By Version**: Group by Release Version
2. **Release Checklist**: Filter by Release Version = specific version

---

## CLI Setup Commands

### Create Sprint Board
```bash
# Create project
gh project create --owner @me --title "Sprint Board"

# Add fields
gh project field-create 1 --owner @me --name "Status" --data-type SINGLE_SELECT \
  --single-select-options "Backlog,Sprint Backlog,In Progress,In Review,Done"

gh project field-create 1 --owner @me --name "Priority" --data-type SINGLE_SELECT \
  --single-select-options "Critical,High,Medium,Low"

gh project field-create 1 --owner @me --name "Story Points" --data-type NUMBER
```

### Create Kanban Board
```bash
gh project create --owner @me --title "Kanban Board"

gh project field-create 1 --owner @me --name "Status" --data-type SINGLE_SELECT \
  --single-select-options "Icebox,Todo,In Progress,Review,Done"

gh project field-create 1 --owner @me --name "Type" --data-type SINGLE_SELECT \
  --single-select-options "Bug,Feature,Chore,Spike"

gh project field-create 1 --owner @me --name "Size" --data-type SINGLE_SELECT \
  --single-select-options "XS,S,M,L,XL"
```

---

## Filtering Patterns

### Common Filters
```
# High priority items
Priority: High,Critical

# Current sprint work
Sprint: @current AND Status: In Progress,In Review

# My items
Assignee: @me

# Overdue
Due Date: <@today

# Bugs in triage
Type: Bug AND Status: New,Triaged
```

### Complex Filters
```
# Sprint items needing review
Sprint: @current AND Status: In Review AND Assignee: @me

# Unestimated high priority
Priority: High,Critical AND Story Points: ""
```
