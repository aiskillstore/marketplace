# VibeKanban MCP API Reference

VibeKanban provides task and project management through MCP tools.

## Core Tools

### list_projects

List all available projects.

**Parameters**: None

**Response**:

```json
[
  {
    "id": "uuid",
    "name": "project-name",
    "description": "Project description",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

**Usage**:

```text
mcp__vibe_kanban__list_projects()
```

---

### list_tasks

List tasks in a project with optional filtering.

**Parameters**:

| Parameter  | Type   | Required | Description                                         |
| ---------- | ------ | -------- | --------------------------------------------------- |
| project_id | UUID   | Yes      | Project to list tasks from                          |
| status     | string | No       | Filter: todo, inprogress, inreview, done, cancelled |
| limit      | int    | No       | Max tasks to return (default: 50)                   |

**Response**:

```json
[
  {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "status": "todo",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

**Usage**:

```text
mcp__vibe_kanban__list_tasks(project_id="<uuid>")
mcp__vibe_kanban__list_tasks(project_id="<uuid>", status="inprogress")
```

---

### get_task

Get detailed information about a specific task.

**Parameters**:

| Parameter | Type | Required | Description      |
| --------- | ---- | -------- | ---------------- |
| task_id   | UUID | Yes      | Task to retrieve |

**Response**:

```json
{
  "id": "uuid",
  "title": "Task title",
  "description": "Full task description with details",
  "status": "inprogress",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "attempts": [
    {
      "id": "uuid",
      "executor": "CLAUDE_CODE",
      "status": "running",
      "started_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**Usage**:

```text
mcp__vibe_kanban__get_task(task_id="<uuid>")
```

---

### create_task

Create a new task in a project.

**Parameters**:

| Parameter   | Type   | Required | Description               |
| ----------- | ------ | -------- | ------------------------- |
| project_id  | UUID   | Yes      | Project to create task in |
| title       | string | Yes      | Task title                |
| description | string | No       | Task description          |

**Response**:

```json
{
  "id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "status": "todo",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Usage**:

```text
mcp__vibe_kanban__create_task(
  project_id="<uuid>",
  title="Bug: Fix login on mobile",
  description="## Problem\nLogin button unresponsive...\n\n## Acceptance Criteria\n- [ ] Works on Safari"
)
```

---

### update_task

Update an existing task's title, description, or status.

**Parameters**:

| Parameter   | Type   | Required | Description                                             |
| ----------- | ------ | -------- | ------------------------------------------------------- |
| task_id     | UUID   | Yes      | Task to update                                          |
| title       | string | No       | New title                                               |
| description | string | No       | New description                                         |
| status      | string | No       | New status: todo, inprogress, inreview, done, cancelled |

**Response**:

```json
{
  "id": "uuid",
  "title": "Updated title",
  "status": "inprogress",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Usage**:

```text
mcp__vibe_kanban__update_task(task_id="<uuid>", status="done")
mcp__vibe_kanban__update_task(task_id="<uuid>", title="New title", description="Updated desc")
```

---

### delete_task

Delete a task from a project.

**Parameters**:

| Parameter | Type | Required | Description    |
| --------- | ---- | -------- | -------------- |
| task_id   | UUID | Yes      | Task to delete |

**Response**:

```json
{
  "success": true
}
```

**Usage**:

```text
mcp__vibe_kanban__delete_task(task_id="<uuid>")
```

---

### list_repos

List repositories associated with a project.

**Parameters**:

| Parameter  | Type | Required | Description                |
| ---------- | ---- | -------- | -------------------------- |
| project_id | UUID | Yes      | Project to list repos from |

**Response**:

```json
[
  {
    "id": "uuid",
    "name": "repo-name",
    "url": "https://github.com/org/repo",
    "default_branch": "main"
  }
]
```

**Usage**:

```text
mcp__vibe_kanban__list_repos(project_id="<uuid>")
```

---

### start_workspace_session

Start working on a task by creating and launching a new workspace session.

**Parameters**:

| Parameter | Type   | Required | Description                                                    |
| --------- | ------ | -------- | -------------------------------------------------------------- |
| task_id   | UUID   | Yes      | Task to work on                                                |
| executor  | string | Yes      | Agent type: CLAUDE_CODE, CODEX, GEMINI, CURSOR_AGENT, OPENCODE |
| repos     | array  | Yes      | Repo configurations: [{repo_id, base_branch}]                  |
| variant   | string | No       | Executor variant if needed                                     |

**Response**:

```json
{
  "id": "uuid",
  "task_id": "uuid",
  "executor": "CLAUDE_CODE",
  "status": "running",
  "started_at": "2025-01-01T00:00:00Z"
}
```

**Usage**:

```text
mcp__vibe_kanban__start_workspace_session(
  task_id="<task-uuid>",
  executor="CLAUDE_CODE",
  repos=[{"repo_id": "<repo-uuid>", "base_branch": "main"}]
)
```

## Common Workflows

### Initialize Coordination Session

```python
# 1. List projects
projects = mcp__vibe_kanban__list_projects()

# 2. Select project (by name or let user choose)
project_id = projects[0]["id"]

# 3. Get repos for the project
repos = mcp__vibe_kanban__list_repos(project_id=project_id)

# 4. List current backlog
tasks = mcp__vibe_kanban__list_tasks(project_id=project_id)
```

### Create and Assign Task

```python
# 1. Create task
task = mcp__vibe_kanban__create_task(
    project_id=project_id,
    title="Bug: Fix mobile login",
    description="..."
)

# 2. Get repo info
repos = mcp__vibe_kanban__list_repos(project_id=project_id)

# 3. Start agent
attempt = mcp__vibe_kanban__start_workspace_session(
    task_id=task["id"],
    executor="CLAUDE_CODE",
    repos=[{"repo_id": repos[0]["id"], "base_branch": "main"}]
)
```

### Monitor Progress

```python
# Get in-progress tasks
active = mcp__vibe_kanban__list_tasks(
    project_id=project_id,
    status="inprogress"
)

# Check specific task
for task in active:
    details = mcp__vibe_kanban__get_task(task_id=task["id"])
    print(f"{details['title']}: {details['status']}")
    if details.get('attempts'):
        print(f"  Agent: {details['attempts'][-1]['executor']}")
```

### Complete Task

```python
# Mark task as done
mcp__vibe_kanban__update_task(
    task_id=task_id,
    status="done"
)
```

## Task Status Flow

```text
                    ┌─────────────┐
                    │    todo     │
                    └──────┬──────┘
                           │ start_workspace_session
                           ▼
                    ┌─────────────┐
           ┌────────│ inprogress  │────────┐
           │        └──────┬──────┘        │
           │               │               │
           │ blocked       │ PR created    │ cancelled
           │               ▼               │
           │        ┌─────────────┐        │
           │        │  inreview   │        │
           │        └──────┬──────┘        │
           │               │               │
           │               │ merged        │
           │               ▼               ▼
           │        ┌─────────────┐  ┌───────────┐
           └───────▶│    done     │  │ cancelled │
                    └─────────────┘  └───────────┘
```

## Error Handling

### Common Errors

| Error               | Cause                  | Resolution                         |
| ------------------- | ---------------------- | ---------------------------------- |
| Project not found   | Invalid project_id     | Use list_projects to get valid IDs |
| Task not found      | Invalid task_id        | Use list_tasks to get valid IDs    |
| Repo not configured | Missing repo setup     | Contact project admin              |
| Agent unavailable   | Executor not available | Try different executor             |

### Retry Pattern

```python
import time

def start_with_retry(task_id, executor, repos, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return mcp__vibe_kanban__start_workspace_session(
                task_id=task_id,
                executor=executor,
                repos=repos
            )
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```
