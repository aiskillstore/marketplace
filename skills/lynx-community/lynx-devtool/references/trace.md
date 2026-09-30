# Performance Trace Recording

Record Lynx performance events through the global DevTool tracing controller
and save the compressed result as a Perfetto `.pftrace` file.

## Requirements

- Android must use a package from the `local_test` channel.
- iOS must use a Lynx Profile package.
- The target app must have Lynx DevTool enabled and appear in
  `agent-lynx list-clients`.

See the [Lynx trace recording guide](https://lynxjs.org/guide/devtool/trace/record-trace.html#setup)
for runtime integration details.

## Workflow

The order is important. Start tracing before building or opening the target
page to capture its first frame.

1. List clients:

   ```bash
   agent-lynx list-clients
   ```

   If several clients are connected, select one and pass the same client ID to
   every following command.

2. Start tracing:

   ```bash
   agent-lynx trace start --client <clientId>
   ```

   On Android, this may enable `enable_debug_mode` and return
   `restartRequired: true`. Restart the app and run `trace start` again before
   continuing.

   Translate memory, category, and JS profiling requirements from the user's
   request into `trace start` flags. For example:

   ```bash
   agent-lynx trace start \
     --client <clientId> \
     --enable-memory-trace \
     --enable-auto-heap-snapshot \
     --shared-group-id xxx
   ```

3. Build or open the page, then perform the interactions to measure.

4. Stop tracing and retain the returned stream handle:

   ```bash
   agent-lynx trace end --client <clientId>
   ```

5. Download the stream to a `.pftrace` file:

   ```bash
   agent-lynx trace read-data \
     --client <clientId> \
     --stream <handle> \
     --output ./my-trace.pftrace
   ```

## Commands

### `trace start`

`trace start` sends `Tracing.start` to session `-1`, the app-global DevTool
mediator. Its default configuration matches the former `lynx-trace-record`
script:

- continuous recording;
- included and excluded trace categories both set to `*`;
- systrace enabled;
- memory data collection disabled;
- automatic garbage collection enabled;
- automatic heap snapshots disabled;
- no `shared-group` VM filter;
- native trace buffer setting `200 * 1024`;
- JS profiling disabled;
- compressed output.

Options:

- `-c, --client <clientId>`: Client ID. The first available non-headless client
  is used when omitted.
- `--no-systrace`: Disable systrace. Systrace is enabled by default.
- `--include-categories <categories>`: Comma-separated trace categories to
  include. Defaults to `*`.
- `--exclude-categories <categories>`: Comma-separated trace categories to
  exclude. Defaults to `*`.
- `--enable-memory-trace`: Enable memory data collection. Disabled by default.
- `--force-gc` / `--no-force-gc`: Enable or disable automatic garbage
  collection. Enabled by default.
- `--enable-auto-heap-snapshot`: Automatically capture heap snapshots for
  `shared-group` VMs. Disabled by default.
- `--shared-group-id <id>`: Limit automatic heap snapshots to the specified
  `shared-group` VM. Defaults to an empty string.
- `--js-profile-type <quickjs|v8>`: Enable profiling for the selected JS
  runtime. JS profiling is disabled when this option is omitted.
- `--js-profile-interval <interval>`: `-1` or a non-negative integer. Defaults
  to `100` when `--js-profile-type` is set and the supplied interval is `0` or
  `-1`; otherwise defaults to `-1`.

Common trace categories are `lynx`, `vitals`, `javascript`, and `devtool`.
When a request asks for only Lynx engine and JavaScript events, for example,
use:

```bash
agent-lynx trace start \
  --client <clientId> \
  --include-categories lynx,javascript
```

To record all events, omit `--include-categories`. To suppress categories, pass
them through `--exclude-categories`, for example
`--exclude-categories devtool,vitals`.

### `trace end`

`trace end` sends `Tracing.end` over a streaming CDP connection and waits for
`Tracing.tracingComplete`. The success JSON includes:

```json
{
  "success": true,
  "message": "Tracing completed successfully. Download the stream with `trace read-data`.",
  "stream": "42",
  "dataLossOccurred": false
}
```

Options:

- `-c, --client <clientId>`: Use the same client selected for `trace start`.
- `--timeout <seconds>`: Time to wait for completion. Defaults to `30`.

### `trace read-data`

`trace read-data` repeatedly calls `IO.read` in 5 MiB chunks, decodes each
base64 payload, closes the native stream with `IO.close`, and atomically
publishes the output file. A failed or interrupted download does not replace an
existing output file.

Options:

- `-s, --stream <handle>`: Required numeric stream handle returned by
  `trace end`.
- `-c, --client <clientId>`: Use the same client selected for `trace start`.
- `-o, --output <path>`: Output path. Parent directories are created. Defaults
  to `<tmpdir>/trace-<timestamp>.pftrace`.
- `--timeout <seconds>`: Total download timeout. Defaults to `30`.

### `trace event-summary`

`trace event-summary <trace>` parses a local trace with Perfetto and lists
every non-empty `slice.name` with its occurrence count. Results are sorted by
count descending and then by name, making this a useful first check before
writing a narrower query.

```bash
# Human-readable table.
agent-lynx trace event-summary ./my-trace.pftrace

# Machine-readable evidence written atomically to a file.
agent-lynx trace event-summary ./my-trace.pftrace \
  --json \
  --output ./event-summary.json
```

The JSON includes `success`, `parseSucceeded`, `eventSource`, `totalEvents`,
`uniqueEventNames`, the complete `events` array, and trace identity fields
(`path`, `bytes`, and `sha256`). The command does not truncate the event list.

### `trace query`

`trace query <trace>` executes Perfetto SQL against a local trace and emits
machine-readable JSON. Provide exactly one SQL source:

```bash
agent-lynx trace query ./my-trace.pftrace \
  --sql "SELECT name, COUNT(*) AS count FROM slice GROUP BY name"

agent-lynx trace query ./my-trace.pftrace \
  --sql-file ./query.sql \
  --max-rows 5000 \
  --output ./query-result.json
```

The default maximum is 1,000 returned rows. The `agent-lynx` CLI does not
rewrite the SQL; the result reports `totalRows`, `returnedRows`, and `truncated` so callers
can distinguish a complete result from bounded output. It also records the SQL
text, source, SHA-256, and resolved SQL-file path, plus the input trace's byte
length and SHA-256. SQL `bigint` values are decimal strings. SQL blobs are
encoded as `{ "base64": "..." }`.

Both inspection commands accept any readable local trace path; `.pftrace` is a
convention rather than an enforced extension. Parse and query failures produce
structured JSON with `success: false`, `parseSucceeded`, and an error phase of
`processor`, `parse`, or `query`, then exit non-zero.

## State and Transport

The `agent-lynx` CLI does not persist trace leases or stream handles. The
target app's global trace controller owns recording state across `start`, `end`, and
`read-data`. Those recording commands use the normal connector transport and
also work with `--no-daemon`; ActionCore and snapshot refs are not involved.

`query` and `event-summary` are fully local and offline. They do not start the
daemon, connect to Android debug-router, or create any
connector transport. A device and `--no-daemon` are therefore unnecessary.

## Troubleshooting

### `restartRequired: true`

`enable_debug_mode` was off and the `agent-lynx` CLI enabled it. Force-close
and restart the app, then run `agent-lynx trace start` again before opening the page.

### Tracing is not supported

Use an Android `local_test` package or an iOS Lynx Profile package. Ordinary
release runtimes may not provide the native trace controller.

### Tracing is not started

Run `trace start` first. Keep the same client ID for `start`, `end`, and
`read-data`.

### Download timeout or invalid stream handle

Use the exact `stream` value returned by the latest successful `trace end`.
Keep the device connected until `read-data` finishes. A stream is closed after
the download attempt and should not be reused.

### A trace file is non-empty but may not contain the expected events

Run `trace event-summary --json` to see all available slice names and counts,
then use `trace query` with exact event names. Treat successful parsing, the
trace SHA-256, and non-zero query rows as delivery evidence; file size alone
does not prove that the intended workload was captured.
