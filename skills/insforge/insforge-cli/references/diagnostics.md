# Diagnostics and Logs

Use `diagnose` for backend health checks and `logs` for source-specific runtime logs.

## Diagnostics

```bash
npx -y @insforge/cli diagnose
npx -y @insforge/cli diagnose --ai "<issue description>"
npx -y @insforge/cli diagnose metrics --range 24h
npx -y @insforge/cli diagnose advisor --severity critical
npx -y @insforge/cli diagnose db --check bloat,slow-queries
npx -y @insforge/cli diagnose logs --limit 100
npx -y @insforge/cli diagnose incident
```

- `diagnose` - full health report across all checks.
- `diagnose --ai "<issue>"` - natural-language debugging for a concrete error, failing URL, status, or symptom.
- `diagnose incident` - why the project is down or returning gateway timeouts (504): verdict + evidence + what to do. Built entirely from cloud-side sources, so it works while the instance itself is unreachable. Requires Platform login; not available via `--api-key` link mode.
- `diagnose metrics [--range 1h|6h|24h|7d] [--metrics <list>]` - EC2 instance metrics such as CPU, memory, disk, and network.
- `diagnose advisor [--severity critical|warning|info] [--category security|performance|health] [--limit <n>]` - latest advisor scan results.
- `diagnose db [--check <checks>]` - database checks such as `connections`, `slow-queries`, `bloat`, `size`, `index-usage`, `locks`, and `cache-hit`.
- `diagnose logs [--source <name>] [--limit <n>]` - aggregate error-level logs.

## Logs

```bash
npx -y @insforge/cli logs function.logs --limit 50
npx -y @insforge/cli logs postgres.logs --limit 50
npx -y @insforge/cli logs insforge.logs --limit 50
npx -y @insforge/cli logs postgrest.logs --limit 50
```

| Source                 | Description                   |
| ---------------------- | ----------------------------- |
| `insforge.logs`        | Main backend logs             |
| `postgrest.logs`       | PostgREST API layer logs      |
| `postgres.logs`        | PostgreSQL database logs      |
| `function.logs`        | Edge function execution logs  |
| `function-deploy.logs` | Edge function deployment logs |

Source names are case-insensitive; `postgrest.logs` and `postgREST.logs` are equivalent.

## Common Debugging Scenarios

| Problem                           | Check                                                                                  |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| Function runtime issue            | `logs function.logs`                                                                   |
| Function deployment issue         | `logs function-deploy.logs`                                                            |
| Database query failing            | `logs postgres.logs`, `logs postgrest.logs`                                            |
| Auth or API error                 | `logs insforge.logs`                                                                   |
| API returning 500 errors          | `logs insforge.logs`, `logs postgrest.logs`                                            |
| General health or performance     | `diagnose` or `diagnose metrics`                                                       |
| Database bloat or slow queries    | `diagnose db`                                                                          |
| Security or config issue          | `diagnose advisor --category security`                                                 |
| Compute service not starting      | `compute events <id>`                                                                  |
| Compute source-mode deploy failed | Check that `flyctl` is on PATH, then rerun if the short-lived deploy token expired     |
| Compute image-mode deploy failed  | Confirm the image is publicly pullable, or configure registry credentials if supported |
