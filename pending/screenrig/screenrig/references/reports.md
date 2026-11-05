# Reports, exports and schedules

Reports read aggregates (uptime rollups, alert history, screen state, direct campaign delivery), never raw events.

## Read a rollup

- `reports list` names the kinds and their filters: `fleet_health`, `uptime`, `publishing`, `alerts`, `alert_log` and `proof_of_play`.
- `reports show KIND --from DAY --to DAY` covers inclusive UTC days (default 30). A folder row counts every screen in it and in the folders inside it, and the first row is the whole project. `--group-by screen|tag`, `--folder-id ID` (with `--direct`: the folder's own screens or child folders) and `--tag TAG` narrow it.
- Rows carry `id`, `parent_id` and `depth` for a folder outline. Availability is online over recorded time; `recorded` says how much of the period screens reported.

## Write a file

- `--format csv|xlsx|pdf --output FILE` on `reports show`, `alerts list`, `project uptime|health-trend`, `screen uptime|health-history`, `playback list|plays|totals|completeness` and `ads reports delivery|fill|spend`, `ads direct report`. The envelope has `path`, `bytes` and `sha256`; quote them with the file.
- A sponsor's statement: `reports show proof_of_play --advertiser "Acme" --from 2026-10-01 --to 2026-10-31 --format pdf --output acme.pdf`. A play counts when the screen reports the media completed.

## Email on a schedule

- `reports subscriptions create --name NAME --kind KIND --cadence daily|weekly|monthly [--weekday D --day-of-month N] --hour H --timezone ZONE --format pdf|xlsx|csv --recipients MEMBERS [--filter NAME=VALUE]`.
- Recipients are project members (user id or member email; `owner` is the project's owner); anyone else is refused. Each run covers the period before it in UTC days. A failed run retries, then waits; read `last_status` and `last_error`. At most 50 per project.

## Export a project

- `project export DIR` writes `export.json` (every file with size and SHA-256), JSON for screens, folders, tags, schedules, playlists with every revision, campaigns, cards, sources, notifications, webhooks and application metadata, `media/files` with `media/manifest.json`, CSV under `data/` and `log/events.jsonl`. Secrets are never written. `--no-media` skips media and `--since DAY` starts the CSV data and the event log. Rerunning keeps complete media and continues partial downloads; `data.complete` false means a section failed: inspect its warning for recovery steps. `export_application_content_omitted` means retain the original application archives alongside this export for release files, including older playlist pins. Rerunning refreshes metadata; `--no-media` also reports this omission.

## Audit log

- `audit list` shows the project's configuration changes newest first: who (`actor`: person, agent, service client, staff, system), `source` (dashboard, api, cli, mcp, staff, device, webhook, system), `action` (`screen.update`, `playlist.create`), the `resource` and `changes`, each with a JSON Pointer `path` and its `before` and `after`. Filters: `--actor ID`, `--actor-kind`, `--source`, `--resource-type`, `--resource-id`, `--action CODE` (a trailing `*` is a prefix), `--field /label`, `--since`, `--until`, and `--after CURSOR` for the next page.
- `audit show ID` prints one entry. A credential reads `(redacted)` on both sides; everything else is the stored value. Pages and media bytes are not copied: the entry links the revision.
- `audit export --format csv|xlsx|pdf --output FILE` writes one row per changed field with the chain head in the file (the last 30 days unless `--since` says otherwise). Quote `path`, `bytes` and `sha256`.
- `audit head` prints `SEQ:HASH`; keep it. `audit verify` recomputes the hash chain (exit 13 and the entries at fault when it fails); `--anchor SEQ:HASH` also proves the history up to a kept head is unchanged. An entry has no `seq` for a few seconds after the change.
- Entries are kept 400 days and no command edits or deletes one. `project export DIR` writes `log/audit.jsonl` and `log/audit-head.json`.

