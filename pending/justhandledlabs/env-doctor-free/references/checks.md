# Env Doctor Checks

Use this reference for language-specific diagnosis and framework `.env` validation.

## Universal Checks

Run these before changing application code:

- Identify project files: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Dockerfile`, `docker-compose.yml`.
- Record runtime versions: `node --version`, `npm --version`, `python --version`, `python3 --version`, `go version`, `docker --version`.
- Check ports: `3000`, `3001`, `5000`, `8000`, `8080`.
- Compare `.env.example` key names against `.env` key names without displaying or retaining values.
- Verify project write access.
- Identify service dependencies: Postgres, Redis, MySQL.

## Node Checklist

Detect Node when `package.json` exists.

Checks:

- `node --version`
- `npm --version`
- `Test-Path node_modules` on Windows or `[ -d node_modules ]` on macOS/Linux
- `package.json` scripts, especially `dev`, `start`, `build`, and `test`
- Lockfile presence: `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`
- Common ports: `3000`, `3001`, `5000`, `8080`

Common findings and fixes:

- Missing `node_modules/`: suggest `npm install`.
- Package manager mismatch: use the lockfile to choose `npm install`, `pnpm install`, `yarn install`, or `bun install`.
- Port `3000` in use: inspect the listener and identify its owner. Do not stop it unless the user confirms that exact process and explicitly approves the stop.
- Missing `.env`: if `.env.example` exists, suggest copying it and filling required values.

## Python Checklist

Detect Python when `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `manage.py`, or `app.py` exists.

Checks:

- `python --version`
- `python3 --version`
- Virtual environment folders: `.venv/`, `venv/`, `env/`
- Dependency files: `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `uv.lock`
- Framework markers: `manage.py`, `flask`, `django`, `FastAPI`, `app.py`
- Common ports: `5000`, `8000`, `8080`

Common findings and fixes:

- Missing virtual environment: suggest `python -m venv .venv`.
- Missing dependencies: suggest `.venv\Scripts\pip install -r requirements.txt` on Windows or `.venv/bin/pip install -r requirements.txt` on macOS/Linux.
- Wrong Python version: compare runtime output to `requires-python` in `pyproject.toml` when present.
- Missing database environment variables: flag `DATABASE_URL` when required.

## Go Checklist

Detect Go when `go.mod` exists.

Checks:

- `go version`
- `go env GOPATH`
- `go.mod` module and Go version
- `go.sum` presence
- Common ports: `3000`, `5000`, `8000`, `8080`

Common findings and fixes:

- Missing modules or stale sums: suggest `go mod tidy` and explain it mutates `go.mod`/`go.sum`.
- Runtime too old: compare `go version` to the `go` directive in `go.mod`.
- Service dependency missing: inspect config for `DATABASE_URL`, `REDIS_URL`, or MySQL DSNs.

## Docker Checklist

Detect Docker when `Dockerfile`, `docker-compose.yml`, or `compose.yaml` exists.

Checks:

- `docker --version`
- `docker compose version`
- Docker daemon status
- Compose services for app, database, cache, and exposed ports
- `.env` used by Compose

Common findings and fixes:

- Docker not running: suggest starting Docker Desktop or the Docker service.
- Compose services stopped: suggest `docker compose ps`, then `docker compose up -d`.
- Port conflict: suggest `lsof -i :<port>` and update compose ports only after confirming the conflict.
- Missing `.env`: suggest creating it from `.env.example` if present.

## Port Conflict Checks

Common ports:

- `3000`: React, Next.js, Vite, Express
- `3001`: alternate Node dev server
- `5000`: Flask, Express alternatives
- `8000`: Django, Python HTTP servers, Go APIs
- `8080`: Docker, Go, Java-style dev servers

Inspection commands for macOS/Linux:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:3001 -sTCP:LISTEN
lsof -nP -iTCP:5000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:8080 -sTCP:LISTEN
ps -p <PID> -o pid=,ppid=,user=,command=
```

Inspection commands for Windows PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-Process -Id <PID> | Select-Object Id,ProcessName,Path
```

Stopping a process is not part of diagnosis. Prefer the application's documented stop command, `Ctrl+C` in the owning terminal, or a targeted service stop. If the user asks for remediation, first confirm the exact PID and executable or service. A normal targeted stop such as `kill <PID>` or `Stop-Process -Id <PID>` still requires explicit approval. Never default to `kill -9`, `Stop-Process -Force`, or a broad process-name kill; force requires a failed normal stop and separate explicit approval.

## Service Checks

Postgres indicators:

- `DATABASE_URL` starts with `postgres://` or `postgresql://`
- Packages: `pg`, `postgres`, `psycopg`, `psycopg2`, Prisma
- Compose service names: `postgres`, `db`

Fix commands:

```bash
docker compose ps
docker compose up -d postgres
```

Redis indicators:

- `REDIS_URL`
- Packages: `redis`, `ioredis`, `celery`, `bull`, `bullmq`
- Compose service names: `redis`, `cache`

Fix commands:

```bash
docker compose ps
docker compose up -d redis
```

MySQL indicators:

- `MYSQL_URL`, `MYSQL_HOST`, `DATABASE_URL` with `mysql://`
- Packages: `mysql`, `mysql2`, `mysqlclient`, `pymysql`
- Compose service names: `mysql`, `mariadb`

Fix commands:

```bash
docker compose ps
docker compose up -d mysql
```

## .env Validation Rules

Compare `.env.example` keys to `.env` keys. Treat variables with empty values as missing unless the example clearly documents them as optional.

Secret-safety rules:

- Treat all text after the first `=` as sensitive, even for apparently harmless or fake values.
- Extract only normalized key names and an empty/present state. Discard values immediately.
- Never print raw `.env` lines or include values in evidence, findings, summaries, logs, or suggested commands.
- Never use `cat .env`, `Get-Content .env`, or unredacted `grep` output.
- If a tool unexpectedly returns a value, redact it and do not repeat it.
- Refer to a missing or empty item only by key name, for example: `DATABASE_URL: missing`.

Always flag these as high priority when required by `.env.example` and absent from `.env`:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `JWT_SECRET`
- `SESSION_SECRET`
- `API_KEY`

## Express .env Rules

Likely required:

- `PORT`
- `DATABASE_URL`
- `SESSION_SECRET` or `JWT_SECRET`
- `REDIS_URL` when sessions, queues, or cache are present

Check package markers:

- `express`
- `pg`, `mongoose`, `prisma`, `sequelize`
- `express-session`, `jsonwebtoken`

## Django .env Rules

Likely required:

- `SECRET_KEY`
- `DATABASE_URL`
- `DJANGO_SETTINGS_MODULE`
- `ALLOWED_HOSTS`
- `DEBUG`

Check markers:

- `manage.py`
- `django`
- `settings.py`
- `DATABASES` config

## Gin .env Rules

Likely required:

- `PORT`
- `DATABASE_URL`
- `GIN_MODE`
- `JWT_SECRET` when auth middleware exists

Check markers:

- `github.com/gin-gonic/gin` in `go.mod`
- `gin.Default()`
- `gin.New()`

## Flask .env Rules

Likely required:

- `FLASK_APP`
- `FLASK_ENV` or `FLASK_DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`

Check markers:

- `flask` in `requirements.txt` or `pyproject.toml`
- `app = Flask(__name__)`
- `flask run`
