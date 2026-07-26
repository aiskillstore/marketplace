---
name: env-doctor-free
description: Diagnose local project environment issues that prevent apps from starting or running. Use when the user says "why won't this run", "check my environment", "env doctor", "diagnose startup issue", "it works on my machine", or asks for help debugging missing dependencies, runtime versions, port conflicts, .env problems, file permissions, or stopped services.
license: MIT
metadata:
  version: 1.3.0
  author: JustHandled Labs
  triggers:
  - why won't this run
  - check my environment
  - env doctor
  - diagnose startup issue
  - it works on my machine
---
# Env Doctor

Diagnose the local environment before changing application code. Treat the project as innocent until the environment is ruled out.

## Workflow

1. Detect project type from files:
   - Node: `package.json`
   - Python: `requirements.txt`, `pyproject.toml`, `Pipfile`, or `manage.py`
   - Go: `go.mod`
   - Docker: `Dockerfile` or `docker-compose.yml`
2. Check runtime availability and versions:
   - Node: `node --version` and `npm --version`
   - Python: `python --version` or `python3 --version`
   - Go: `go version`
   - Docker: `docker --version` and `docker compose version`
3. Check dependencies:
   - Node projects with no `node_modules/`: flag as high priority and suggest `npm install`.
   - Python projects with no `.venv/`, `venv/`, or active virtual environment: flag and suggest creating one, then installing requirements.
   - Go projects: run `go mod tidy` only after explaining it mutates `go.mod`/`go.sum`; otherwise suggest it as the fix.
   - Docker projects: check whether Docker is running before suggesting rebuilds.
4. Check common port conflicts for `3000`, `3001`, `5000`, `8000`, and `8080`.
   - Detect the operating system before providing commands.
   - On macOS/Linux, inspect listeners with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, then identify the PID with `ps`.
   - On Windows PowerShell, inspect listeners with `Get-NetTCPConnection -LocalPort <port>`, then identify the owning PID with `Get-Process`.
   - Report the PID, executable or service name, and available ownership evidence before suggesting any stop action.
   - Prefer the application's documented stop command, `Ctrl+C` in its owning terminal, or a targeted service stop.
   - Never assume a listener is stale or belongs to the project. Do not terminate any process without the user's explicit approval.
   - Never default to `kill -9`, `Stop-Process -Force`, or a broad process-name kill. Escalation to a force-kill requires a confirmed target, a failed normal stop, and separate explicit approval.
5. Validate environment variables:
   - Compare `.env.example` against `.env` when both or either exist.
   - Flag missing `.env` if `.env.example` exists.
   - Flag missing required variables listed in `.env.example`.
   - Always flag missing `DATABASE_URL` when it appears in `.env.example` but is absent from `.env`.
   - Treat every value after the first `=` as a secret, including comments or examples that resemble credentials.
   - Parse only key names and whether each value is empty. Never print, quote, store, summarize, or retain values in findings, evidence, logs, or commands.
   - Do not use raw-display commands such as `cat .env`, `Get-Content .env`, or unredacted `grep` output.
   - Redact accidental value exposure immediately and refer to variables by key name only.
6. Check file permissions:
   - Verify the project directory is writable before running installers or build commands.
   - For Unix-like scripts referenced by `package.json`, `Makefile`, Docker, or shell commands, check whether executable bits may be required and suggest `chmod +x <script>`.
7. Check background services when the project appears to need them:
   - Postgres: referenced by `DATABASE_URL`, `postgres`, `pg`, `psycopg`, Prisma, Django, Rails-like config, or `docker-compose.yml`.
   - Redis: referenced by `REDIS_URL`, `redis`, Celery, BullMQ, Sidekiq-like config, or `docker-compose.yml`.
   - MySQL: referenced by `MYSQL_URL`, `mysql`, `mysqlclient`, `pymysql`, or `docker-compose.yml`.
   - Prefer non-destructive status checks. Suggest start commands only after identifying the likely service.

## Reference Loading

Read `references/checks.md` when the project type is known, when the user asks for a checklist, or when framework-specific `.env` validation is needed for Express, Django, Gin, or Flask. Read `references/safety-fixtures.md` before evaluating or changing the port or `.env` behavior of this skill.

## Output Shape

Return a prioritized checklist, highest impact first:

```markdown
**Env Doctor Findings**

1. [High] <issue>
   Evidence: `<command output or file reference>`
   Fix:
   <Use a `powershell` code fence on Windows or a `bash` code fence on macOS/Linux. Include only the matching OS command.>

2. [Medium] <issue>
   Evidence: `<command output or file reference>`
   Fix:
   <Use a `powershell` code fence on Windows or a `bash` code fence on macOS/Linux. Include only the matching OS command.>

**Likely Start Command**
`<command>`

**What I Checked**
Node/Python/Go/Docker runtimes, dependencies, ports, .env key presence, permissions, services. No .env values were displayed or retained.
```

If no issue is found, say that the environment looks healthy and identify the next best application-level debugging step.

## Required Quality Cases

- Missing `node_modules/` in a Node project must be reported with `npm install`.
- Port `3000` in use must be reported with an OS-appropriate inspection command and ownership evidence before any stop action.
- Missing `DATABASE_URL` in `.env`, when required by `.env.example`, must be reported as a high-priority environment variable issue.
- `.env` findings and evidence must contain key names and empty/present state only, never values.
- An unrelated process that owns a common port must not be stopped or given an unconditional termination command.
- POSIX commands must use a `bash` block and Windows commands must use a `powershell` block.
