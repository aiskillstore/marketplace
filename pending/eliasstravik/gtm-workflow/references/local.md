# Local use

`gtm run` starts the Nitro server on a free loopback port when no configured server answers, records it in ignored `.gtm-local.json`, and prints `Started the local server.` The first local command also writes a `GTM_RUN_SECRET` into `.env`; nothing needs to be typed.

Open `/_workflow` for traces and run `npm run db:studio` for Data. Set `GTM_BASE_URL` only when choosing an already-running origin.

A paused local run waits only while the local server is up.

Local AI steps use the CLI named by `GTM_HOST`, written into `.env` at scaffold time. Capabilities recorded from `claude --help` and `codex exec --help` on 2026-09-11:

| CLI | Budget cap | Turn cap | Tool restriction | Structured output | `agentStage()` without a key |
| --- | --- | --- | --- | --- | --- |
| Claude Code 2.1.268 | `--max-budget-usd` | none; the stage deadline bounds it | `--tools ""` disables built-ins, `--allowedTools mcp__*` and `--strict-mcp-config` allow only the declared MCP servers | `--json-schema` | runs |
| Codex 0.154.0 | none | none | `--sandbox read-only`, which still permits reads | `--output-schema` | refuses; add an AI key |

Short `agent()` calls run on either CLI. On Codex, an `agent()` call with untrusted input also needs an AI key because tools cannot be disabled.
