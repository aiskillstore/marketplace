---
name: connect
description: Connect this Claude Code session to ThreadPage under its own name. Runs only when the person types /threadpage:connect [as <name>].
argument-hint: "[as <name>]"
disable-model-invocation: true
---

The person typed `/threadpage:connect $ARGUMENTS`: connect this session to ThreadPage.

1. Call the ThreadPage tool `threadpage_connect` once. If the arguments are `as <name>`, pass that name as `name`; otherwise pass no name, and the plugin suggests one from this folder.
2. Claude Code asks the person before the tool runs, and ThreadPage may open in the browser for one click. Wait for its answer.
3. Tell the person its answer in one line. If it gives a link to open, give that link.
