# Hook Input JSON Patterns Reference

This document provides the JSON input structure for all Claude Code hook events, verified through actual runtime logging.

## Common Fields (All Events)

All hook events include these base fields:

```json
{
  "session_id": "uuid-string",
  "transcript_path": "/path/to/session.jsonl",
  "cwd": "/current/working/directory",
  "hook_event_name": "EventName"
}
```

| Field             | Type   | Description                               |
| ----------------- | ------ | ----------------------------------------- |
| `session_id`      | string | Unique UUID for the current session       |
| `transcript_path` | string | Path to the session transcript JSONL file |
| `cwd`             | string | Current working directory                 |
| `hook_event_name` | string | Name of the hook event being triggered    |

---

## Session-Level Events

### SessionStart

Triggered when a Claude Code session begins.

```json
{
  "session_id": "44da5a62-3516-47d0-8ce1-5ed48bdf2ef9",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "hook_event_name": "SessionStart",
  "source": "startup"
}
```

| Field    | Type   | Values                    | Description                                               |
| -------- | ------ | ------------------------- | --------------------------------------------------------- |
| `source` | string | `"startup"` \| `"resume"` | Whether this is a new session or resuming an existing one |

### SessionEnd

Triggered when a Claude Code session ends.

```json
{
  "session_id": "56e3f819-2cb2-4f36-a54f-3f2a03a0856a",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "hook_event_name": "SessionEnd",
  "reason": "prompt_input_exit"
}
```

| Field    | Type   | Values                | Description                    |
| -------- | ------ | --------------------- | ------------------------------ |
| `reason` | string | `"prompt_input_exit"` | Reason for session termination |

### SubagentStop

Triggered when a subagent (Task tool) completes execution.

```json
{
  "session_id": "56e3f819-2cb2-4f36-a54f-3f2a03a0856a",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "permission_mode": "default",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "5d6d7245",
  "agent_transcript_path": "/home/user/.claude/projects/-project-path/agent-5d6d7245.jsonl"
}
```

| Field                   | Type    | Description                                                    |
| ----------------------- | ------- | -------------------------------------------------------------- |
| `permission_mode`       | string  | Current permission mode (`"default"` \| `"bypassPermissions"`) |
| `stop_hook_active`      | boolean | Whether the stop hook is currently active                      |
| `agent_id`              | string  | Unique identifier for the subagent                             |
| `agent_transcript_path` | string  | Path to the subagent's transcript file                         |

### PreCompact

Triggered before context compaction occurs.

```json
{
  "session_id": "8ab3eafa-ab3c-4eac-af30-ded14633a789",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "hook_event_name": "PreCompact",
  "trigger": "auto",
  "custom_instructions": null
}
```

| Field                 | Type           | Values                                 | Description                   |
| --------------------- | -------------- | -------------------------------------- | ----------------------------- |
| `trigger`             | string         | `"auto"` \| `"manual"`                 | What triggered the compaction |
| `custom_instructions` | string \| null | Custom instructions for the compaction |

---

## User Interaction Events

### UserPromptSubmit

Triggered when the user submits a prompt.

```json
{
  "session_id": "56e3f819-2cb2-4f36-a54f-3f2a03a0856a",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "done. please continue"
}
```

| Field             | Type   | Description                      |
| ----------------- | ------ | -------------------------------- |
| `permission_mode` | string | Current permission mode          |
| `prompt`          | string | The user's submitted prompt text |

### Notification

Triggered when a notification is displayed to the user.

```json
{
  "session_id": "56e3f819-2cb2-4f36-a54f-3f2a03a0856a",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "hook_event_name": "Notification",
  "message": "Claude Code needs your approval for the plan",
  "notification_type": "permission_prompt"
}
```

| Field               | Type   | Values                | Description                      |
| ------------------- | ------ | --------------------- | -------------------------------- |
| `message`           | string | -                     | The notification message content |
| `notification_type` | string | `"permission_prompt"` | Type of notification             |

### PermissionRequest

Triggered when Claude requests permission to use a tool.

```json
{
  "session_id": "56e3f819-2cb2-4f36-a54f-3f2a03a0856a",
  "transcript_path": "/home/user/.claude/projects/-project-path/session.jsonl",
  "cwd": "/home/user/project",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PermissionRequest",
  "tool_name": "ExitPlanMode",
  "tool_input": {}
}
```

| Field             | Type   | Description                            |
| ----------------- | ------ | -------------------------------------- |
| `permission_mode` | string | Current permission mode                |
| `tool_name`       | string | Name of the tool requesting permission |
| `tool_input`      | object | The input parameters for the tool      |

---

## Tool Events (PreToolUse / PostToolUse)

All tool events share a common structure with additional tool-specific fields.

### Common PreToolUse Structure

```json
{
  "session_id": "uuid",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/working/directory",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PreToolUse",
  "tool_name": "ToolName",
  "tool_input": {
    /* tool-specific input */
  },
  "tool_use_id": "toolu_xxxx"
}
```

### Common PostToolUse Structure

```json
{
  "session_id": "uuid",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/working/directory",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PostToolUse",
  "tool_name": "ToolName",
  "tool_input": {
    /* tool-specific input */
  },
  "tool_response": {
    /* tool-specific response */
  },
  "tool_use_id": "toolu_xxxx"
}
```

---

## Tool-Specific Patterns

### Read Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Read",
  "tool_input": {
    "file_path": "/absolute/path/to/file.txt",
    "offset": 1,
    "limit": 500
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "type": "text",
    "file": {
      "filePath": "/absolute/path/to/file.txt",
      "content": "file content here...",
      "numLines": 88,
      "startLine": 1,
      "totalLines": 88
    }
  }
}
```

### Bash Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "echo \"test bash command\"",
    "description": "Test bash for hook logging"
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "stdout": "test bash command",
    "stderr": "",
    "interrupted": false,
    "isImage": false
  }
}
```

### Glob Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Glob",
  "tool_input": {
    "pattern": "*.py",
    "path": "/home/user/project/.claude/hooks"
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "filenames": ["/path/to/file1.py", "/path/to/file2.py"],
    "durationMs": 63,
    "numFiles": 33,
    "truncated": false
  }
}
```

### Grep Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Grep",
  "tool_input": {
    "pattern": "def main",
    "path": "/home/user/project/.claude/hooks",
    "head_limit": 3,
    "output_mode": "files_with_matches",
    "-A": 15,
    "-B": 10,
    "-C": 5,
    "multiline": true
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "mode": "files_with_matches",
    "filenames": [".claude/hooks/file1.py", ".claude/hooks/file2.py"],
    "numFiles": 3,
    "appliedLimit": 3
  }
}
```

### Write Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/absolute/path/to/new-file.txt",
    "content": "File content to write"
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "type": "create",
    "filePath": "/absolute/path/to/new-file.txt",
    "content": "File content to write",
    "structuredPatch": [],
    "originalFile": null
  }
}
```

### Edit Tool

**PreToolUse Input:**

```json
{
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/absolute/path/to/file.txt",
    "old_string": "original text",
    "new_string": "replacement text"
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "filePath": "/absolute/path/to/file.txt",
    "oldString": "original text",
    "newString": "replacement text",
    "originalFile": "original text",
    "structuredPatch": [
      {
        "oldStart": 1,
        "oldLines": 1,
        "newStart": 1,
        "newLines": 1,
        "lines": [
          "-original text",
          "\\ No newline at end of file",
          "+replacement text",
          "\\ No newline at end of file"
        ]
      }
    ],
    "userModified": false,
    "replaceAll": false
  }
}
```

### TodoWrite Tool

**PreToolUse Input:**

```json
{
  "tool_name": "TodoWrite",
  "tool_input": {
    "todos": [
      {
        "content": "Test TodoWrite tool for hook logging",
        "status": "completed",
        "activeForm": "Testing TodoWrite"
      }
    ]
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "oldTodos": [],
    "newTodos": [
      {
        "content": "Test TodoWrite tool for hook logging",
        "status": "completed",
        "activeForm": "Testing TodoWrite"
      }
    ]
  }
}
```

### Task Tool (Subagent)

**PreToolUse Input:**

```json
{
  "tool_name": "Task",
  "tool_input": {
    "description": "Test Task tool logging",
    "prompt": "Return immediately with the text \"Test complete\"",
    "subagent_type": "Explore",
    "model": "haiku"
  }
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "status": "completed",
    "prompt": "Return immediately with the text \"Test complete\"",
    "agentId": "13d93d13",
    "content": [
      {
        "type": "text",
        "text": "Test complete"
      }
    ],
    "totalDurationMs": 2351
  }
}
```

### EnterPlanMode Tool

**PreToolUse Input:**

```json
{
  "tool_name": "EnterPlanMode",
  "tool_input": {}
}
```

**PostToolUse Response:**

```json
{
  "tool_response": {
    "message": "Entered plan mode. You should now focus on exploring the codebase and designing an implementation approach."
  }
}
```

### ExitPlanMode Tool

**PreToolUse Input:**

```json
{
  "tool_name": "ExitPlanMode",
  "tool_input": {}
}
```

**Note:** ExitPlanMode typically triggers a PermissionRequest before execution.

### SlashCommand Tool

**PreToolUse Input:**

```json
{
  "tool_name": "SlashCommand",
  "tool_input": {
    "command": "/git:commit"
  }
}
```

---

## Permission Mode Values

| Value                 | Description                                        |
| --------------------- | -------------------------------------------------- |
| `"default"`           | Standard permission checking enabled               |
| `"bypassPermissions"` | Running in bypass mode (e.g., after user approval) |

---

## Hook Output Patterns

Hooks can return JSON to stdout to control Claude's behavior:

### Block Tool Execution

```json
{
  "decision": "block",
  "reason": "Explanation of why the tool is blocked"
}
```

### Modify Tool Input

```json
{
  "decision": "modify",
  "tool_input": {
    "modified": "parameters"
  }
}
```

### Continue with No Changes

Return empty stdout or:

```json
{
  "decision": "continue"
}
```

---

## Usage Notes

1. **Tool Use ID**: The `tool_use_id` field is a unique identifier for tracking the tool invocation across PreToolUse and PostToolUse events.

2. **Permission Mode**: Check `permission_mode` to determine if standard permission rules apply.

3. **Response Types**: The `tool_response` structure varies significantly between tools - always check `tool_name` to parse correctly.

4. **File Paths**: All file paths in `tool_input` should be absolute paths.

5. **Structured Patches**: Edit tool responses include `structuredPatch` for programmatic diff analysis.
