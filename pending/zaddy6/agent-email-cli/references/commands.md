# Command Reference

## Core commands

```bash
agent-email create
agent-email read <email|default> [--limit <n>] [--full] [--wait <s>] [--interval <s>]
agent-email show <email|default> <messageId>
agent-email delete <email|default> <messageId>
```

## Profile commands

```bash
agent-email accounts list
agent-email accounts remove <email|default>
agent-email use <email|default>
agent-email config path
agent-email about
```

## Output envelope

All commands return JSON by default:

```json
{
  "ok": true,
  "command": "create",
  "data": {}
}
```

or on failure:

```json
{
  "ok": false,
  "command": "read",
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "...",
    "hint": "..."
  }
}
```

## High-signal fields

- `create`: `data.email`, `data.accountId`, `data.activeEmail`
- `read`: `data.messages[]` with `id`, `from.address`, `subject`, `createdAt`, `seen`
- `show`: `data.message`, optional `data.source`

Do not extract or print secret fields (`password`, `token`) in summaries.

## Common automation snippets

Read active inbox and extract first message id:

```bash
agent-email read default | jq -r '.data.messages[0].id'
```

Fetch full first message:

```bash
MSG_ID=$(agent-email read default | jq -r '.data.messages[0].id')
agent-email show default "$MSG_ID"
```
