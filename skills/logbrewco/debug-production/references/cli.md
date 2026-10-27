# LogBrew CLI map for debugging

Every command here is in the help of the released `logbrew` CLI. Run
`logbrew --help` or `logbrew <topic> --help` to see the version you have.

## Install and access

Install the CLI with one of these commands:

```bash
brew install LogBrewCo/tap/logbrew
npm install -g logbrew-cli@latest
```

Read access comes from one of 2 sources:

- Account access: a person runs `logbrew login` once. Check it with
  `logbrew status --json`.
- A project read key: set `LOGBREW_TOKEN` to a key of kind `read`. It reads 1
  project only, so commands do not need `--project`. `logbrew status`
  checks account access only, so test a read key with a read command.

## Commands by step

| Step | Command | Read in the JSON |
| --- | --- | --- |
| Access | `logbrew status --json` | Authentication state |
| 1. Find the issue | `logbrew read issues --project "$PROJECT_ID" --environment production --status unresolved --since 24h --json` | Issue IDs, titles, counts, release |
| 1. Start with urgent issues | `logbrew read issues --project "$PROJECT_ID" --status unresolved --priority high --since 24h --json` | Same, filtered by priority |
| 2. Stack and first release | `logbrew investigate issue "$ISSUE_ID" --occurrence recommended --json` | `subject.first_seen_at`, `event.id`, `event.occurred_at`, `occurrence_selection.reason`, `cause.status`, `fix.status`, `correlations.trace`, `impact.user_impact.status`, `evidence.status`, `next_actions` |
| 2. First occurrence | `logbrew investigate issue "$ISSUE_ID" --occurrence first --json` | The earliest retained occurrence |
| 2. Short summary | `logbrew explain issue "$ISSUE_ID" --json` | Same contract as `investigate issue` |
| 3. Trace | `logbrew read trace "$TRACE_ID" --project "$PROJECT_ID" --json` | Spans of 1 trace |
| 3. Trace summary | `logbrew explain trace "$TRACE_ID" --json` | Failure and correlation context |
| 3. Logs of the trace | `logbrew read logs --trace "$TRACE_ID" --project "$PROJECT_ID" --since 24h --json` | Logs linked to the trace |
| 3. Logs in a window | `logbrew read logs --project "$PROJECT_ID" --service "$SERVICE" --environment production --since "$WINDOW_START" --until "$WINDOW_END" --json` | Logs around the first event |
| 3. Error logs by text | `logbrew read logs --project "$PROJECT_ID" --severity error --search "$TEXT" --since 24h --json` | Matching error logs |
| 3. Error traces | `logbrew traces --project "$PROJECT_ID" --service "$SERVICE" --status error --since 24h --json` | Failed requests |
| 7. Verify a fix | `logbrew investigate issue "$ISSUE_ID" verify --baseline-occurrence "$OCCURRENCE_ID" --candidate-deployment "$DEPLOYMENT_ID" --json` | `status`: `recurrence_observed`, `no_recurrence_observed`, `insufficient_traffic`, or `unavailable` |
| 7. Watch live | `logbrew watch issues --json` | New issue events as they arrive |
| After approval | `logbrew resolve "$ISSUE_ID" --json` | Changes issue status; only with permission |

`--since` takes a duration such as `30m`, `24h`, or `7d`, or an RFC 3339
time. `--until` is an RFC 3339 time and is exclusive. Severity values are
`info`, `warning`, `error`, and `critical`.

## Read every page

A list returns 1 page. Add `--pagination cursor` and continue with
`--cursor-time` and `--cursor-id` from `next_cursor`. Keep the same filters
and `--limit` on each page. Stop when `next_cursor` is `null`.

```bash
logbrew read issues --project "$PROJECT_ID" --status unresolved --since 24h --pagination cursor --limit 100 --json
```

## Exit codes

- `0`: the command ran. A successful JSON result keeps the API shape and
  does not always have an `ok` field.
- `1`: the command failed while it ran.
- `2`: the CLI rejected the command. Read `error` and `next` on standard
  error, fix the syntax, then run it again.

Errors go to standard error. Do not merge standard output and standard error.
