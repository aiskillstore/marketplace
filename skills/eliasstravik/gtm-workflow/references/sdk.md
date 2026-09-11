# SDK choices

Use a fixed `"use step"` function when inputs and calls are known. Use `agent()` for one structured model answer. Use `agentStage()` when the model must choose among declared HTTP MCP tools across several turns.

The library does not wrap the rest of Vercel Workflow or the AI SDK. Import `WorkflowAgent`, hooks, webhooks, `sleep`, streams, and other primitives directly when a workflow needs them. Keep environment reads and network effects inside `"use step"` functions.

Read the installed Vercel Workflow documentation under `node_modules/workflow/docs/` for runtime details and the AI SDK agent documentation at <https://ai-sdk.dev/docs/agents> for agent-loop behavior.
