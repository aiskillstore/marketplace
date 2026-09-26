---
name: lynx-devtool
description: Use when working with Lynx DevTool or debugging a Lynx app, page, or device, especially when the task mentions clients or sessions, CDP or App commands, DOM/CSS inspection, runtime or console logs, evaluating JavaScript on a device, screenshots, heap snapshots, performance traces, Page.reload or App.openPage, global switches, interactive snapshot refs and taps/fills/scrolls, inspecting or searching a ReactLynx component tree, linking DOM Snapshot refs to ReactLynx components (`reactlynx link`), or mutating ReactLynx props/state/context on Android, iOS, or Desktop.
---

# Agent Lynx DevTool Skill

This skill allows you to interact with Lynx applications running on connected devices (Android, iOS, Desktop) using the `agent-lynx` CLI.

## Usage

Use the `agent-lynx` CLI. The published package is `agent-lynx`.
This package, `@lynx-js/skill-lynx-devtool`, is the canonical source of this
Skill's instructions and resources. `agent-lynx` depends on it and reads it
directly for `skills list/get`. A compatibility launcher also keeps the historic
one-shot `npx -y @lynx-js/skill-lynx-devtool` invocation working.

The programmatic API is exported from `agent-lynx/connector`. This entry re-exports everything from `@lynx-js/devtool-connector`, `@lynx-js/devtool-connector/transport`, and `@lynx-js/devtool-connector/streams`, and also provides daemon-only `createDefaultTransports()` and `createDefaultConnector()` helpers. The helpers use one `DaemonTransport` so independent scripts share the daemon-owned device connection. Construct a `Connector` with explicit transports only when intentionally testing a non-daemon path.

Online CLI commands follow the same daemon-only default. `--no-daemon` is an
explicit escape hatch that replaces the daemon with direct Android, iOS,
OpenHarmony, and Desktop transports for that invocation. The built-in headless
runtime remains daemon-only. `ADB_SERVER_HOST` and `ADB_SERVER_PORT` configure
only this direct mode. Daemon mode ignores them with a stderr warning.

The `agent-lynx` CLI is normally available on `PATH`. If
`command -v agent-lynx` fails, use `npx` instead:

```bash
npx --yes agent-lynx <command>
```

This published skill does not ship a local CLI entry script. Use:

```bash
agent-lynx <command>
```

**Note:** Most command outputs are JSON. You can use `jq` or Node.js to process the data.

### Discover Built-in Skills

The installed `@lynx-js/skill-lynx-devtool` dependency provides the
`lynx-devtool` skill. Discover it or load its complete instructions with:

```bash
agent-lynx skills list
agent-lynx skills get lynx-devtool
```

`skills list` reads each name and description directly from that package's
`SKILL.md` YAML frontmatter. `skills get` returns the selected Markdown body and
recursively lists regular files under `references/`, `assets/`, and `examples/`
when those directories exist. Symlinks and build output are not included. The
stable name is `lynx-devtool`.

### Snapshot Workflow

```bash
agent-lynx snapshot
agent-lynx tap @e3 --snapshot
agent-lynx fill @e1 "Alice"
agent-lynx clear @e1
agent-lynx scroll @e2 --direction down
agent-lynx get text @e3
agent-lynx get style @e3 --property color,width
agent-lynx wait --text Ready
agent-lynx screenshot --annotate -o page.jpeg
```

Snapshot refs live in daemon memory across CLI invocations. Do not pass
`--no-daemon` to `snapshot`, `tap`, `long-press`, `fill`, `clear`, `scroll`,
`get text`, `get style`, `wait`, or `screenshot`. `wait` uses the daemon's SSE
command route; the other snapshot commands use `POST /command/<action>`.

`screenshot --annotate` refreshes and caches snapshot refs, then draws numbered
labels directly into one JPEG. Label `[N]` maps to ref `@eN`, so an agent can
inspect the image and immediately use the matching ref. The image labels a
sparse actionable subset of the visible refs: direct action targets, editable
fields, explicit test targets, and scroll containers. Generic layout and text
refs remain available in the cached snapshot without cluttering the image.
Viewport-sized scroll containers use a corner badge instead of a full-frame
border. With `--json`, the result also carries the complete fresh snapshot used
by this same ActionCore call, so consumers can compare the image and refs
without issuing a second refresh. Pixel mapping uses the screencast frame's
logical-size metadata separately from the potentially inset snapshot viewport;
the command fails instead of guessing when that metadata is unavailable. Do not
combine `--annotate` with `--fullscreen`; use unannotated
`screenshot --fullscreen` or the legacy
`take-screenshot --fullscreen` command instead. See
[Annotated Screenshots Reference](references/screenshot-annotate.md).

Programmatic connector imports require a project dependency:

```bash
npm install agent-lynx
```

This project-local install is needed only for connector workflows, not for
CLI-only use through the `agent-lynx` CLI on `PATH` or `npx`.

### Use as a Library

If you want to drive Lynx DevTool directly from JavaScript instead of shelling out to the CLI, import from `agent-lynx/connector`.

```js
import { Connector, createDefaultConnector } from "agent-lynx/connector";

const connector = createDefaultConnector();
const clients = await connector.listClients();

console.log(clients);
```

For fuller programmatic workflows, see [Library Usage Reference](references/library-usage.md) and [Programmatic Debugging Example](examples/programmatic-debugging.md).

You can also construct the connector manually if you intentionally need custom, non-daemon transports:

```js
import {
  AndroidTransport,
  Connector,
  DesktopTransport,
  iOSTransport,
} from "agent-lynx/connector";

const connector = new Connector([
  new AndroidTransport({ host: "127.0.0.1", port: 5037 }),
  new DesktopTransport(),
  new iOSTransport(),
]);
```

### Global Options

- `-h, --help`: Display help for command.
- `--no-daemon`: Bypass the shared daemon and use direct device transports for this invocation. Stop the daemon first if it may own a connection to the same DebugRouter target.

**Note:** Each subcommand supports the `--help` flag (e.g. `agent-lynx cdp --help`). Use this to view the full list of available arguments and their descriptions.

### Commands

#### 1. List Clients

List all available Lynx clients (apps with DevTool enabled).

```bash
agent-lynx list-clients
```

#### 2. Wait For Client

Wait until a client is available.

```bash
agent-lynx wait-for-client --client-name com.lynx.uiapp
```

- `--client-name <name>`: Optional package/app name to wait for. Matches `AppProcessName`, `bundleId`, `bundleName`, or `App`. If multiple clients match, all matching clients are returned. If omitted, the first non-headless client is returned. Output is always a JSON array.
- `--timeout <seconds>`: Maximum seconds to wait. Defaults to `30`.
- `--interval <seconds>`: Seconds between discovery attempts. Defaults to `1`.

#### 3. List Sessions

List all active debugging sessions. A session corresponds to a specific Lynx view or context.

```bash
agent-lynx list-sessions
# Optional: Filter by client ID
agent-lynx list-sessions --client <clientId>
```

#### 4. Send CDP Command

Send a Chrome DevTools Protocol (CDP) command to a specific session.

> Note that Lynx only supports a part of the standard CDP command.
> LynxView note: when the target session is a LynxView, you **MUST** read [Supported CDP Methods](references/cdp/index.md) before sending a CDP command.
> WebView note: when the target session is a WebView (for example `type: "web"` or an HTTP/HTTPS URL), use the standard Chrome DevTools Protocol documentation for CDP method names, parameters, and enable prerequisites. The local `references/cdp` pages focus on LynxView support and Lynx-specific extensions, which may return `method not found` on WebView targets.

```bash
agent-lynx cdp -m <method> [options] [params]
```

- `-m, --method <method>`: The CDP method name (e.g., `DOM.getDocument`, `Page.reload`).
- `-c, --client <clientId>`: (Optional) The Client ID. If omitted, uses the first available client.
- `-s, --session <sessionId>`: (Optional) The Session ID. If omitted, uses the latest session (with the largest session ID).
- `--thread <thread>`: (Optional) Target VM thread, `background` or `main`. Defaults to `background`.
- `[params]`: (Optional) JSON string of parameters for the command.

When `--thread main` is used, only `Debugger.*`, `Runtime.*`, `HeapProfiler.*`, and `Profiler.*` methods are supported.

Example:

```bash
# Get the document root
agent-lynx cdp -m DOM.getDocument
```

#### 5. Evaluate JavaScript

Evaluate a JavaScript expression. On the background VM, the current app's `lynx` and `nativeLynx` objects are available as local variables. Expressions targeting the main VM are sent unchanged.

```bash
agent-lynx evaluate 'JSON.stringify(lynx.__globalProps)'
agent-lynx evaluate '2 + 2' --thread main
agent-lynx evaluate 'lynx' --no-return-by-value
```

- `<expression>`: JavaScript expression to evaluate.
- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--thread <thread>`: (Optional) Target VM thread, `background` or `main`. Defaults to `background`. Only background expressions are wrapped to expose `lynx` and `nativeLynx`; main-thread expressions are sent unchanged.
- The command requests results by value by default. Engines that support `returnByValue` serialize ordinary JSON-like objects into `result.value`; current Android Lynx runtimes may ignore it for object values and still return an `objectId`. Use `JSON.stringify(lynx.__globalProps)` when JSON output is desired. Use `--no-return-by-value` to deliberately receive an `objectId` for later `Runtime.getProperties` or `Runtime.callFunctionOn` requests. `--return-by-value` remains accepted as an explicit form of the default.
- `--silent`, `--context-id`, `--throw-on-side-effect`, `--generate-preview`, `--object-group`, `--await-promise`, `--include-command-line-api`: Optional evaluation parameters. Engine support varies.

#### 6. Send App Command

Send an App-level command.

```bash
agent-lynx app -m <method> [options] [params]
```

- `-m, --method <method>`: The App method name (e.g., `App.openPage`).
- `-c, --client <clientId>`: (Optional) Client ID.
- `[params]`: (Optional) JSON string of parameters.

> You **MUST** read [Supported App Methods](references/app/index.md) before sending an App command.

#### 7. Open URL

Open a specific URL in the Lynx app.

```bash
agent-lynx open <url> [options]
```

- `<url>`: The URL to open.
- `-c, --client <clientId>`: (Optional) Client ID.

Example:

```bash
agent-lynx open "lynx://example/page"
```

#### 8. Get Console

Capture console logs from the device.

```bash
agent-lynx get-console [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--offset <number>`: Skip N messages.
- `--limit <number>`: Limit number of messages.
- `--include-stack-traces`: Include stack traces for non-error messages.
- `--level <levels>`: Filter log levels (e.g., `error,warning`).
- `--thread <thread...>`: Target VM thread(s): `background` or `main`. If omitted, both threads are collected by default.

#### 9. Get Sources

List all parsed scripts. This is useful for finding script IDs to use with other commands (e.g., `Debugger.getScriptSource`). The command automatically fetches all currently loaded scripts.

```bash
agent-lynx get-sources [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.

#### 10. Inspect

Print the DevTool inspector URL served by the connector daemon for a
client/session pair. Open the printed URL in a browser to attach a graphical
inspector to the same session the CLI targets.

```bash
agent-lynx inspect [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--port <port>`: (Optional) Daemon port. Defaults to `21783`.

#### 11. Agent Screenshot

Capture through ActionCore, optionally drawing fresh snapshot refs directly
into the resulting JPEG.

```bash
agent-lynx screenshot [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--annotate`: (Optional) Refresh refs and draw `[N]` labels, where `[N]` maps to `@eN`.
- `--fullscreen`: (Optional) Capture fullscreen instead of LynxView. Cannot be combined with `--annotate`.
- `-o, --output <path>`: (Optional) JPEG output path.
- `--json`: (Optional) Return the path, image dimensions, complete fresh snapshot, and annotation metadata.

This command requires the persistent daemon. See
[Annotated Screenshots Reference](references/screenshot-annotate.md) for its
single-image output contract and target restrictions.

#### 12. Legacy Take Screenshot

Take a direct screenshot of the current page using the pre-Agent-Lynx command.

```bash
agent-lynx take-screenshot [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--fullscreen`: (Optional) Capture the screenshot in `fullscreen` mode. Defaults to `lynxview` mode if not provided.
- `-o, --output <path>`: (Optional) Output file path.

#### 13. Take Content Screenshot

Capture the full scrollable content of the first node matching a CSS selector.

```bash
agent-lynx take-content-screenshot --selector <selector> [options]
```

- `--selector <selector>`: CSS selector for a `scroll-view` or compatible `list`. Required.
- `--format <jpeg|png>`: (Optional) Image format. Defaults to `jpeg`.
- `--scale <number>`: (Optional) Positive output scale. Defaults to `1`.
- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `-o, --output <path>`: (Optional) Output file path.

`takeContentScreenshot` is officially defined for `scroll-view`. The command accepts any CSS selector so runtimes that expose the same method on `list` can also be used; unsupported nodes return the UI Method failure.

See [Take Content Screenshot Reference](references/take-content-screenshot.md) for behavior and examples.

#### 14. Global Switch

Manage DevTool global switches.

```bash
# List all supported keys and their current values
agent-lynx global-switch list [options]

# Get one key
agent-lynx global-switch get --key <globalKey> [options]

# Set one key
agent-lynx global-switch set --key <globalKey> --status <on|off> [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.

`global-switch list` options:

- `--fail-fast`: Abort on first key-read failure.

`global-switch get` options:

- `--key <globalKey>`: Global switch key. (Required)

`global-switch set` options:

- `--key <globalKey>`: Global switch key. (Required)
- `--status <on|off>`: Target switch status. (Required)

For the full key list and examples, see [Global Switch Reference](references/global-switch.md).

#### 15. Take Heap Snapshot

Capture a QuickJS heap snapshot from the current Lynx session and save it as a `.heapsnapshot` file.

```bash
agent-lynx take-heap-snapshot [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--thread <thread>`: (Optional) Target VM thread, `background` or `main`. Defaults to `background`.
- `-o, --output <path>`: (Optional) Output file path. Defaults to the OS temp directory.

#### 16. Query Global Memory Usage

Query Lynx global memory usage through the global `Memory.*` CDP domain. Use the generic `cdp` command and send the request to the global DevTool handler with session ID `-1`.

```bash
# Get global Lynx memory usage across live instances
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage '{"timeoutMs":50000}'
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: CDP session ID. Use `-1` for the global DevTool handler unless you have a platform-specific reason to override it.
- `params.timeoutMs` (Optional): Non-negative timeout in milliseconds. Maximum value is `300000`.

The command prints the raw `Memory.getAllMemoryUsage` JSON. Do not expect the CLI output to contain derived `summary`, `topMemoryItems`, or `topInstances` wrapper fields.

When the DevTool MCP server is available, prefer the `Memory_getAllMemoryUsage` MCP tool for the same raw payload instead of shelling out to the CLI.

Agent-side reporting standard:

1. Save the complete raw JSON to a file when the user asks for a capture or when the result is too large to show inline.
2. Use binary units (`KiB`, `MiB`, `GiB`) with two decimal places. Render `ratioToApp` and contribution ratios as percentages with two decimal places.
3. Report this fixed summary first:
   - `collectionStatus`
   - `${completedInstanceCount}/${expectedInstanceCount}` Lynx instances
   - `totalBytes`
   - `appBytes`
   - `ratioToApp`
   - `elementNodeCount`
   - `viewBytes`
   - `mainThreadRuntimeBytes`
   - `backgroundThreadRuntimeBytes`
4. Then report "Top 5 Memory Contributors" using fine-grained candidate items from each `instances[]` entry:
   - `instances[i].backgroundThreadRuntimeBytes`
   - `instances[i].mainThreadRuntimeBytes`
   - `instances[i].elementBytes`
   - each `instances[i].viewDetail[category].sizeBytes`
   - if `instances[i].viewBytes` is larger than the sum of `viewDetail[*].sizeBytes`, include an `other view memory` item for the remainder.
5. Sort the Top 5 contributors by bytes descending. For each row include rank, item kind/category, size, `% of totalBytes`, `% of instance.totalBytes`, `instanceId`, and URL.
6. Then report "Instances" sorted by `instance.totalBytes` descending. For each instance include `instanceId`, URL, `totalBytes`, `mainThreadRuntimeBytes`, `backgroundThreadRuntimeBytes`, `viewBytes`, `elementBytes`, and a compact `viewDetail` summary such as `image=12 / 4.15 MiB`.
7. Do not invent missing fields. If `viewDetail` is empty or a category has `0` bytes, say so plainly. The current CDP payload does not expose a nested child LynxView object tree.

`Memory.getAllMemoryUsage` is different from `Runtime.getHeapUsage`: it returns a global Lynx-attributed memory snapshot across live registered Lynx instances, including element, view, main-thread runtime, background runtime, app footprint, and per-instance breakdowns. The current CDP payload does not expose a separate nested child LynxView memory tree; `viewDetail` is aggregated by UI view category or tag. For the full response shape, see [Memory CDP Methods](references/cdp/memory/index.md).

#### 17. Recording

Record Lynx page interactions via TestBench (CDP-based). Captures all actions (template loads, touch events, JS module calls, data updates) and produces a JSON replay file.

```bash
# Start recording (BEFORE opening the target page)
agent-lynx recorder start [options]

# Stop recording and save the replay file
agent-lynx recorder end [options]
```

- `-c, --client <clientId>`: (Optional) Client ID for `start` and `end`.
- `-o, --output <path>`: (Optional) Output file or directory path for `end`. Defaults to `~/.lynx-devtool/files/lynxrecorder/recording-<clientId>-<timestamp>.json`.

Workflow:

1. Run `recorder start`. If it enables `enable_debug_mode`, restart the app and run `recorder start` again.
2. User opens and interacts with the Lynx page.
3. Run `recorder end --output <file.json>` to stop and save.
4. Report the absolute file path to the user.

**Important:** For a replayable file, open or reload the target page after `recorder start` so the recording includes `loadTemplate`.

See [Recording Reference](references/recorder.md) for more details.

#### 18. Performance Trace Recording

Record a compressed Lynx performance trace and save it as a `.pftrace` file.
Start tracing before building or opening the target page so the capture includes
its first frame.

```bash
# Discover the client first; keep the same ID throughout the workflow.
agent-lynx list-clients

# Start before opening the target page.
agent-lynx trace start --client <clientId>

# Open and interact with the page, then stop and capture the stream handle.
agent-lynx trace end --client <clientId>

# Download the handle returned by trace end.
agent-lynx trace read-data --client <clientId> --stream <handle> -o ./my-trace.pftrace

# Inspect the downloaded file locally without a device or daemon.
agent-lynx trace event-summary ./my-trace.pftrace
agent-lynx trace query ./my-trace.pftrace \
  --sql "SELECT name, COUNT(*) AS count FROM slice GROUP BY name"
```

- `-c, --client <clientId>`: (Optional) Client ID. If several clients are
  connected, list them and select one explicitly.
- `trace start --no-systrace`: Disable systrace; it is enabled by default.
- `trace start --include-categories <categories>` /
  `--exclude-categories <categories>`: Include or exclude comma-separated trace
  categories.
- `trace start --enable-memory-trace`: Enable memory data collection.
- `trace start --no-force-gc`: Disable automatic garbage collection, which is
  enabled by default.
- `trace start --enable-auto-heap-snapshot`: Capture automatic heap snapshots
  for `shared-group` VMs. Add `--shared-group-id <id>` to select one VM.
- `trace start --js-profile-interval <interval>`: JS sampling interval. Defaults
  to `100` when profiling is enabled and the supplied interval is `0` or `-1`;
  otherwise it defaults to `-1`.
- `trace start --js-profile-type <quickjs|v8>`: Enable profiling for the
  selected JS runtime. Profiling is disabled when this option is omitted.
- `trace end --timeout <seconds>`: Time to wait for
  `Tracing.tracingComplete`. Defaults to `30`.
- `trace read-data --stream <handle>`: Numeric stream handle returned by
  `trace end`.
- `trace read-data -o, --output <path>`: Output path. Defaults to a timestamped
  `.pftrace` in the OS temporary directory.
- `trace read-data --timeout <seconds>`: Total download timeout. Defaults to
  `30`.
- `trace event-summary <trace>`: Print every Perfetto `slice.name` and its
  occurrence count, sorted by count descending. Add `--json` for structured
  evidence and `-o, --output <path>` to write it to a file.
- `trace query <trace> --sql <query>`: Run inline Perfetto SQL and emit JSON.
- `trace query <trace> --sql-file <path>`: Run SQL from a file. Use exactly one
  of `--sql` and `--sql-file`; `--max-rows` defaults to `1000`.

`trace query` and `trace event-summary` are local, offline commands. They do
not connect to a device, start the daemon, or create a connector transport.
Their JSON includes the trace's absolute path, byte length, and SHA-256 so an
agent can prove which file it inspected. SQL `bigint` values are decimal
strings and blobs are `{ "base64": "..." }` objects.

On Android, the first `trace start` may enable `enable_debug_mode` and ask for
an app restart. Restart the app and run `trace start` again before opening the
page. A runtime without trace support requires an Android local_test build or
an iOS Lynx Profile build. See [Performance Trace Reference](references/trace.md)
for the complete workflow and troubleshooting.

#### 19. ReactLynx Component Tree

Print the component tree of a running ReactLynx page, decoded from `@lynx-js/preact-devtools`. The CLI calls the connector daemon's ReactLynx ActionCore; the daemon owns the `Lynx.onVMEvent` stream, the `init`+`refresh` handshake, `operation_v2` decoding, and the per-session component cache. The CLI only renders the returned tree.

```bash
agent-lynx reactlynx tree [options]
```

- `-c, --client <clientId>`: (Optional) Client ID.
- `-s, --session <sessionId>`: (Optional) Session ID.
- `--depth <n>`: (Optional) Maximum tree depth to print. Default: unbounded.
- `--show-shells`: Include the synthetic `Fragment` / `Root` / `Anonymous` wrappers ReactLynx inserts. They are hidden by default.
- `--json`: Emit `{ labels, roots, nodes }` instead of ASCII; use this when a script will consume the tree.

Output uses `@cN [type] Name` references (the convention from `agent-react-devtools`). Labels are pre-order DFS over visible roots. `reactlynx tree` always captures a fresh generation and caches the exact label view it emitted, including `--depth`; later `component @cN` and `update-* @cN` calls reuse that view across independent CLI invocations. Compact and `--show-shells` label views are cached separately.

```
@c1 [fn] App
├─ @c2 [fn] Header
│  └─ @c3 [fn] Logo
└─ @c4 [fn] Body
```

Requirements:

- ReactLynx commands require the connector daemon; do not combine them with `--no-daemon`.
- The page must be a **dev build** running `@lynx-js/preact-devtools` (production bundles strip `setupReactLynx()`). Successful initialization logs `[PREACT DEVTOOLS] Devtools initialized successfully` to the device console.
- `@lynx-js/preact-devtools` must include the `document.body` and `preactDevtoolsCtx.Node` fixes (PR #2 + PR #5 against `lynx-family/preact-devtools`). Without them, the `refresh` channel will return zero `operation_v2` frames and the CLI will print the "stale preact-devtools" diagnostic.

When the tree comes back empty, the CLI exits with code `1` and writes one of three targeted diagnostics on stderr:

- **`saw 0 frames`**: nothing replied on the `PreactDevtools` channel. The App is most likely missing `@lynx-js/preact-devtools`, is a production build, has not finished `setupReactLynx()`, or you picked the wrong `--session`.
- **`saw N frames but no operation_v2`**: the hook is loaded but its `refresh` handler is buggy. Upgrade `@lynx-js/preact-devtools` to a build that contains PRs #2 and #5.
- **`tree is empty`**: every node was unmounted between commits -- rare, rerun with `DEBUG` (below) to see the raw envelopes.

For deep debugging, set `DEBUG=devtool-mcp-server:reactlynx` to log every PreactDevtools frame (type + payload size) on stderr while leaving stdout (the tree / JSON) clean:

```bash
DEBUG='devtool-mcp-server:reactlynx' agent-lynx reactlynx tree
# 2026-05-25T... devtool-mcp-server:reactlynx frame 1: type=operation_v2 dataSize=54
# 2026-05-25T... devtool-mcp-server:reactlynx frame 2: type=operation_v2 dataSize=756
# 2026-05-25T... devtool-mcp-server:reactlynx frame 3: type=root-order dataSize=1
# 2026-05-25T... devtool-mcp-server:reactlynx frame 4: type=root-order-page dataSize=object
```

#### 20. ReactLynx Component Inspect

Inspect a single ReactLynx component (props / state / hooks / context / signals) by sending the Preact DevTools `inspect` envelope and reading back `inspect-result`.

```bash
agent-lynx reactlynx component <ref> [options]
```

- `<ref>`: either a label `@cN` produced by `reactlynx tree` / `reactlynx find`, or a numeric vnode id.
  - With `@cN`, the daemon resolves the label against its latest matching label view. On a cache miss it captures a tree once. Pass `--show-shells` if (and only if) the label was generated with shells visible.
  - With a numeric id (e.g. `3856353762`), the component cache is bypassed.
- `-c, --client <clientId>`, `-s, --session <sessionId>`: (Optional) standard targeting flags.
- `--show-shells`: When resolving `@cN`, count synthetic Fragment / Root / Anonymous wrappers the same way `reactlynx tree --show-shells` does.
- `--refresh`: Capture a new full tree before resolving `@cN`. It has no effect on numeric ids.
- `--json`: Print the raw `InspectData` payload as JSON. Default output is a compact ASCII summary.

Example output:

```text
@c5 (id=3856353783) [fn] TUXIntroViewListCell key=1. HMR
  source: src/TUXIntroViewListCell.tsx:42:3
  props:
    {
      "title": "1. HMR",
      "icon": { "type": "vnode", "name": "TUXIcon" }
    }
```

Complex values are tagged by upstream's `serialize.ts` -- `{ "type": "function", "name": "..." }`, `{ "type": "vnode", "name": "..." }`, `{ "type": "signal", "value": ... }`, `{ "type": "map", "entries": [...] }`, etc. See [serialize.ts](https://github.com/lynx-family/preact-devtools/blob/main/src/adapter/shared/serialize.ts) for the full schema.

If the App fails to reply with an `inspect-result`, the daemon evicts that session's ReactLynx cache and the CLI exits with code `1`. Run `reactlynx tree` before retrying. The same `DEBUG=devtool-mcp-server:reactlynx` namespace traces every frame.

#### 21. ReactLynx Component Find

Find every component whose name matches a substring or regex. Output is ordered identically to `reactlynx tree` (pre-order DFS) so the `@cN` labels round-trip with the other subcommands.

```bash
agent-lynx reactlynx find <pattern> [options]
```

- `<pattern>`: substring (default, case-insensitive) or JavaScript regex with `--regex`.
- `-c, --client <clientId>`, `-s, --session <sessionId>`: (Optional) standard targeting flags.
- `--regex`: Treat `<pattern>` as a JavaScript regular expression (e.g. `--regex '^Toast(List)?$'`).
- `--show-shells`: Include synthetic Fragment / Root / Anonymous wrappers.
- `--refresh`: Capture a new component generation before searching. Without it, `find` reuses the daemon cache (and captures once on a cache miss).
- `--limit <n>`: Maximum number of matches to print. Default `50`.
- `--json`: Emit `[{ label, id, name, type, key, ancestors: [{label, name}] }, ...]` for scripted post-processing.

Example output:

```text
@c8 [fn] TUXCenterToastActivator
  in @c1 TUXApp > @c2 Provider > @c3 App
@c10 [fn] TUXTopToastActivator
  in @c1 TUXApp > @c2 Provider > @c3 App
```

`reactlynx find` is the recommended way to discover labels for follow-up `reactlynx component @cN` calls when the tree is too large to scan visually. A successful find publishes its full-depth label view as the latest view for the selected shell mode.

#### 22. ReactLynx Element/Component Link

Resolve one exact relationship between the latest daemon-cached DOM Snapshot
and the daemon-cached ReactLynx component tree:

```bash
# Snapshot element -> nearest surfaced ReactLynx component
agent-lynx snapshot
agent-lynx reactlynx link @e7

# ReactLynx component -> first host element in the latest Snapshot
agent-lynx reactlynx tree
agent-lynx reactlynx link @c8
```

The command also accepts a numeric Preact VNode id in place of `@cN` and
supports `--json`, `--show-shells`, and `--refresh`. By default it reuses the
latest component generation and exact label view for the selected shell mode;
on a component-cache miss it captures one generation. `--refresh` explicitly
replaces the component generation before resolving the relationship.

This is an exact identity lookup through Lynx `nodeId` / ReactLynx `uniqueId`;
it never falls back to coordinates, text, or tree-position matching. It uses
the existing App-side `element-picked` and `highlight` protocol, so the App
must contain a compatible `@lynx-js/preact-devtools` dev build. JSON returns
the complete Snapshot ref, component label/id/type/name/key, and component
cache generation.

The command deliberately does not refresh the DOM Snapshot: refreshing would
silently invalidate the `@eN` refs the user is trying to relate. Run
`agent-lynx snapshot` first, and rerun it explicitly when the daemon reports a
missing or stale ref. Component-to-element lookup returns the first host
element exposed by Preact DevTools; element-to-component lookup returns its
nearest surfaced component. These directions are therefore not guaranteed to
form a bijection for components that render multiple host elements.

#### 23. ReactLynx Component Update

Mutate one field and wait for the app-side adapter's post-update `inspect-result` confirmation:

```bash
agent-lynx reactlynx update-prop <ref> <path> <value> [options]
agent-lynx reactlynx update-state <ref> <path> <value> [options]
agent-lynx reactlynx update-context <ref> <path> <value> [options]
```

- `<ref>` follows the same cached `@cN` or numeric vnode-id rules as `reactlynx component`.
- `<path>` starts at the selected props/state/context object, such as `count`, `user.name`, or `items.0.title`. Do not prefix it with `root.`, `props.`, `state.`, or `context.`.
- `<value>` is parsed as JSON. Quote string JSON for the shell, or pass `--raw` to send the argument verbatim as a string.
- `--show-shells` selects the shell-inclusive label view; `--refresh` captures a new tree before resolving `@cN`.
- `--json` emits the raw post-update `InspectData` confirmation.

The daemon serializes ReactLynx operations for the same client/session so broadcast Preact VM events cannot cross-talk between concurrent commands. Different sessions can proceed in parallel. The cache is generation-based rather than a live subscription: `tree` and explicit `--refresh` replace it, `find` reuses it by default, and a failed cached inspect/update evicts it.
