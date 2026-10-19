---
name: turbo-operations
description: "Turbo pipeline operations reference — lifecycle commands (pause, resume, restart, delete), pipeline states, checkpoint behavior, streaming vs job-mode differences, CLI syntax for `inspect`/`logs`, TUI shortcuts, and error pattern lookup. Triggers on: 'how do I pause/restart/delete', 'will deleting lose my data', 'what does this error mean', 'inspect TUI shortcuts'. For interactive diagnosis of a broken pipeline, use /turbo-doctor."
---

# Turbo Pipeline Operations

Lifecycle commands, monitoring, and error reference for running Turbo pipelines. This is a lookup reference — for interactive troubleshooting of a broken pipeline, use `/turbo-doctor`. For building new pipelines, use `/turbo-builder`.

## Pipeline States

| State     | Description                                  |
| --------- | -------------------------------------------- |
| running   | Pipeline is actively processing data         |
| starting  | Pipeline is initializing                     |
| paused    | Pipeline is paused (replicas set to 0)       |
| stopped   | Pipeline is not running (manually stopped)   |
| error     | Pipeline encountered an error                |
| completed | Job-mode pipeline finished processing range  |

## Streaming vs Job Mode Lifecycle

| Operation     | Streaming Pipeline            | Job-Mode Pipeline (`job: true`)             |
| ------------- | ----------------------------- | ------------------------------------------- |
| **List**      | Shows as `running`/`paused`   | Shows as `running`/`completed`              |
| **Pause**     | Supported                     | Not supported                               |
| **Resume**    | Supported                     | Not supported                               |
| **Restart**   | Supported                     | Not supported — use delete + apply          |
| **Delete**    | Supported                     | Supported (auto-cleanup ~1hr after done)    |
| **Apply**     | Updates in place              | Must delete first, then re-apply            |

### Job-Mode Pipeline Lifecycle

Job-mode pipelines (`job: true`) are one-time batch processes:

1. **Start** — process data from `start_at` to `end_block`
2. **Run** — process the bounded data range
3. **Complete** — automatically stop when range is processed
4. **Auto-cleanup** — ~1 hour after completion, automatically removed

Cannot pause, resume, or restart. Must delete before redeploying.

## Lifecycle Commands

### List Pipelines

```bash
goldsky turbo list
```

### Pause a Pipeline

Temporarily stop processing without deleting. Preserves all state for later resumption.

```bash
goldsky turbo pause <pipeline-name>
```

### Resume a Pipeline

Restore a paused pipeline. Can only resume a **paused** pipeline.

```bash
goldsky turbo resume <pipeline-name>
```

### Restart a Pipeline

Trigger a pod restart for a running or paused pipeline.

```bash
goldsky turbo restart <pipeline-name>
# To clear all checkpoints and reprocess from the beginning:
goldsky turbo restart <pipeline-name> --clear-state
```

### Delete a Pipeline

Permanently remove a pipeline. All checkpoints are lost. Data already written to sinks is preserved.

```bash
goldsky turbo delete <pipeline-name>
```

### Delete and Recreate (Fresh Start)

```bash
goldsky turbo delete my-pipeline
goldsky turbo apply my-pipeline.yaml
```

## Checkpoint Behavior

- Deleting a pipeline removes its checkpoints permanently
- Recreating with the same name starts fresh (no checkpoint recovery)
- To preserve checkpoints, use `apply` to update instead of delete/recreate
- Checkpoint state is tied to source names — renaming a source resets its checkpoint
- Checkpoint state is tied to pipeline names — renaming a pipeline resets all checkpoints

## Monitoring Commands

| Action                   | Command                                              |
| ------------------------ | ---------------------------------------------------- |
| List pipelines           | `goldsky turbo list`                                 |
| View live data           | `goldsky turbo inspect <name> -p`                    |
| Inspect specific node    | `goldsky turbo inspect <name> -n <node> -p`          |
| View logs                | `goldsky turbo logs <name>`                          |
| Follow logs              | `goldsky turbo logs <name> --follow`                 |
| Logs with timestamps     | `goldsky turbo logs <name> --timestamps`             |
| Last N lines             | `goldsky turbo logs <name> --tail N`                 |
| Logs since N seconds ago | `goldsky turbo logs <name> --since N`                |

## `goldsky turbo inspect` Flags

| Flag                   | Short | Description                                                  |
| ---------------------- | ----- | ------------------------------------------------------------ |
| `--print`              | `-p`  | Print records to stdout                                      |
| `--topology-node-keys` | `-n`  | Comma-separated node keys to filter (e.g. a transform name)  |
| `--buffer-size`        | `-b`  | Max records to keep in buffer (default: 10000)               |

Always use `-p`. Always include it in every `inspect` command you suggest.

### Log Analysis Script

Use the helper script to quickly analyze pipeline logs:

```bash
./scripts/analyze-logs.sh <pipeline-name>
./scripts/analyze-logs.sh <pipeline-name> --tail 100
```

The script checks for common error patterns and reports findings with recommendations.

## Common Error Patterns

> **Detailed error patterns and solutions are in `data/error-patterns.json`.**

| Error Pattern             | Likely Cause               | Fix                                            |
| ------------------------- | -------------------------- | ---------------------------------------------- |
| `connection refused`      | Database unreachable       | Check network/firewall settings                |
| `authentication failed`   | Wrong credentials          | Update secret with correct credentials         |
| `secret not found`        | Missing secret             | Create secret with `goldsky secret create`     |
| `SQL syntax error`        | Invalid transform SQL      | Fix SQL in YAML and redeploy                   |
| `duplicate key`           | Primary key collision      | Ensure unique primary key in transform          |
| `script transform error`  | TypeScript runtime failure | Check script logic, null handling, return types |
| `dynamic_table` error     | Backend connection issue   | Verify dynamic table secret/table exists        |
| `WASM execution failed`   | Script crash in sandbox    | Debug script — check for undefined access       |
| `handler timeout`         | External HTTP endpoint slow| Increase `timeout_ms` or fix handler endpoint   |

### Script Transform Issues

| Issue                        | Fix                                                    |
| ---------------------------- | ------------------------------------------------------ |
| `undefined` property access  | Add null checks: `input.field ?? ''`                   |
| Wrong return type            | Ensure returned object matches `schema` exactly        |
| Missing return fields        | All `schema` fields must be present in returned object |
| `invoke is not a function`   | Ensure script defines `function invoke(data)`          |
| BigInt errors                | Use `BigInt()` constructor, not direct number literals  |

### Dynamic Table Issues

| Issue                      | Fix                                                    |
| -------------------------- | ------------------------------------------------------ |
| Table not found            | Create the table in PostgreSQL before deploying         |
| No matches from check      | Verify data exists in the backing table                 |
| Stale data                 | For postgres backend, verify rows are actually there    |
| Memory pressure            | Large in_memory tables → switch to postgres backend     |

## Troubleshooting Quick Reference

| Symptom                  | Likely Cause           | Quick Fix                                       |
| ------------------------ | ---------------------- | ----------------------------------------------- |
| No data flowing          | `start_at: latest`     | Wait for new data or use `earliest`             |
| Auth failed              | Wrong credentials      | Update secret with correct password             |
| Connection refused       | Network/firewall       | Check host, whitelist Goldsky IPs               |
| Storage exceeded         | Neon free tier (512MB) | Upgrade plan or clear data                      |
| SQL error                | Bad transform syntax   | Validate YAML first                             |
| Pipeline not found       | Name mismatch          | Run `goldsky turbo list` to check names         |
| Permission denied        | Role insufficient      | Verify Editor or Admin role in the project      |
| `pipeline already exists`| Job-mode stale         | Delete first, then re-apply                     |
| Cannot pause/resume job  | Job-mode limitation    | Job pipelines don't support pause/resume        |
| Cannot restart job       | Job-mode limitation    | Delete + re-apply instead                       |
| Can't connect to inspect | Pipeline not running   | Check status with `goldsky turbo list`          |
| Logs are empty           | Pipeline just started  | Wait for data or check `start_at`               |
| TUI disconnects          | Pipeline interrupted   | Auto-reconnects within 30 min; check status     |

## Related

- **`/turbo-doctor`** — Interactive diagnostic skill for pipeline issues
- **`/turbo-builder`** — Build and deploy new pipelines
- **`/turbo-pipelines`** — YAML configuration and architecture reference
