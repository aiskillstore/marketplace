# Troubleshooting

Use these debug namespaces when `devtool` cannot discover clients or sessions, or when a command fails during transport setup.

## Quick Triage

- `list-clients` returns `[]`: check whether any port in `8901-8910` ever returns `Register` after `Initialize`.
- Client found but later commands fail: discovery worked, so focus on `list-sessions`, `clientId`, `sessionId`, and the specific request payload.

## Discovery Model

The connector works like this:

1. Call `listDevices()` on each transport.
2. For each device, probe ports `8901-8910`.
3. Send `Initialize` to each port. A port that responds with `Register` is treated as a client.
4. Try `SetGlobalSwitch(enable_devtool=true)` on that same client port.
5. Send later commands such as `list-sessions`, `cdp`, and `app` to that same client port.

`listDevices()` is an internal step in this flow. At the CLI level, the user-visible result is usually just whether `list-clients` returns clients or `[]`.

In practice:

- one client usually corresponds to one app process such as `LynxExplorer`
- one session corresponds to one Lynx page inside that client
- one device may have multiple clients
- one client may have multiple sessions

The connector is stateless and uses short-lived connections. Repeated `connect` / `close connection` logs are normal. It also means IDs are snapshots, not durable handles: if the app restarts you should expect to rediscover the client, and if a Lynx page is reopened or replaced you should expect to refresh the session.

One more important detail: `list-clients` uses `Promise.allSettled()`. Many transport and port-level failures are intentionally swallowed during discovery, so a broken discovery pass often shows up as `[]` rather than a thrown error. Use `DEBUG='devtool-mcp-server:connector*'` when `[]` is surprising.

## Debug Namespaces

Start with the base connector logs:

```bash
DEBUG='devtool-mcp-server:connector' agent-lynx list-clients
```

Then narrow or widen as needed:

```bash
DEBUG='devtool-mcp-server:connector*' agent-lynx list-clients
DEBUG='devtool-mcp-server:connector:android' agent-lynx list-clients
DEBUG='devtool-mcp-server:connector:ios' agent-lynx list-clients
DEBUG='devtool-mcp-server:connector:desktop' agent-lynx list-clients
```

- `devtool-mcp-server:connector`: high-level connector flow like `Initialize`, `Register`, `SetGlobalSwitch`, and `close connection`
- `devtool-mcp-server:connector*`: connector logs plus all transport subdomains
- `devtool-mcp-server:connector:android`: Android transport details such as `listDevices`, ADB connection attempts, and socket failures
- `devtool-mcp-server:connector:ios`: iOS transport details such as device discovery and connection lifecycle
- `devtool-mcp-server:connector:desktop`: desktop transport details such as localhost probing and `ECONNREFUSED`

## Healthy Signals

- Without `DEBUG`, `stdout` should just be the JSON result from the command.
- With `DEBUG='devtool-mcp-server:connector'`, `stderr` should usually show a flow like `Initialize` -> `Register` -> `SetGlobalSwitch` -> `close connection`.
- With `DEBUG='devtool-mcp-server:connector*'`, you will also see lower-level transport logs such as Android `listDevices`, Android socket failures, desktop localhost probes, or iOS device scans.
- Because the connector is stateless, repeated reconnects across commands are expected.

```text
connect <clientId> input stream send '{"event":"Initialize","data":8901}'
connect <clientId> output stream receive { event: 'Register', ... }
connect <clientId> input stream send '{"event":"Customized","data":{"type":"SetGlobalSwitch",...}}'
```

If you can see the `Register` / `Customized` flow and still get an empty JSON result, the connector is alive and the next thing to inspect is client or session selection.

## Symptoms And Fixes

### `list-clients` returns `[]`

What it usually means:

- either the transport found nothing useful to probe
- or the target app did not expose any client on ports `8901-8910`

How to confirm:

- use `DEBUG='devtool-mcp-server:connector*'`
- if you see no meaningful transport activity, the transport likely did not find anything useful
- if you see transport activity but never see `Register` after `Initialize`, no client was discovered

What to do:

- make sure the target device, simulator, or desktop app is actually running
- for Android, verify the device is present in `adb devices`
- for iOS, verify the device or simulator is available to the iOS transport
- for desktop, make sure the target desktop app is actually running
- open or relaunch the target app that should expose the client
- make sure you are targeting a build that supports DevTool
- if the app was just launched, wait a moment and rerun `list-clients`
- if only one platform matters, switch from `connector*` to `connector:android` or `connector:ios` to reduce noise

### `No response received from <deviceId>:<port>`

What it usually means:

- the connector established a transport connection, but no valid response came back before the request finished
- the target may be offline, hung, speaking a different protocol, or timing out
- the request itself may be invalid, so the app never sent a response

How to confirm:

- use `DEBUG='devtool-mcp-server:connector'`
- look for `input stream send` without a matching usable response
- if needed, widen to `DEBUG='devtool-mcp-server:connector*'` to inspect lower-level transport failures
- compare the failing method and params with the supported docs to see whether the request shape is valid

What to do:

- rerun `list-clients` to make sure the client still exists
- if the client was rediscovered on a different run, use the fresh `clientId`
- if needed, relaunch the app to rediscover the client, then re-enter the target Lynx page
- double-check the method name, params, and whether the request requires a valid `sessionId`
- if this only happens on one platform, switch to the platform-specific debug namespace and inspect transport logs

### You see `Initialize` and `Register`, but later commands still fail

What it usually means:

- discovery succeeded, so the port is a client for an app
- the failure is now in session discovery or in later command routing on that same client port

How to confirm:

- rerun `list-sessions` for the same client with `DEBUG='devtool-mcp-server:connector'`
- check whether the client is reachable but returns no sessions, or whether the later request times out

What to do:

- rerun `list-clients` and `list-sessions` and use fresh IDs
- if the app restarted, the old `clientId` may be stale
- if the Lynx page was reopened or replaced, the old `sessionId` may be stale
- make sure the Lynx page you want to inspect is currently open
- if `list-sessions` is empty, open the target Lynx page and retry

### `list-sessions` works, but `cdp` commands fail

What it usually means:

- the client port is alive, but the specific `cdp` command failed due to wrong parameters, wrong session, or a transient transport issue

How to confirm:

- use `DEBUG='devtool-mcp-server:connector'` for request and response logs
- verify the selected `clientId` and `sessionId`
- compare the failing request with the supported method docs

What to do:

- rerun `list-sessions` and choose the current session again
- if the client has multiple sessions, choose the one for the Lynx page you actually want to inspect
- double-check the method name and params payload
- if the session disappeared, reopen the target Lynx page and retry from `list-sessions`

### `app` commands fail, but `list-clients` works

What it usually means:

- the client is reachable, but the specific app-level method or params are invalid for that app
- unlike `cdp`, `app` commands do not depend on a `sessionId`

How to confirm:

- use `DEBUG='devtool-mcp-server:connector'` for request and response logs
- verify the selected `clientId`
- compare the failing method and params with the supported App method docs

What to do:

- rerun `list-clients` and use a fresh `clientId` if the app restarted
- double-check the App method name and params payload
- if the target app was relaunched, rediscover the client before retrying

### `connector*` is too noisy to be useful

What it usually means:

- wildcard logging is showing all transport activity, including expected failures on transports you do not care about

How to confirm:

- you see mixed Android, iOS, and desktop logs in the same run

What to do:

- use `DEBUG='devtool-mcp-server:connector'` for high-level flow only
- use `DEBUG='devtool-mcp-server:connector:android'` when focusing on Android transport issues
- use `DEBUG='devtool-mcp-server:connector:ios'` when focusing on iOS transport issues
- use `DEBUG='devtool-mcp-server:connector:desktop'` when focusing on desktop transport issues

## Keeping JSON Output Clean

Debug logs are written to `stderr`. If you still want to pipe the JSON result into `jq`, redirect `stderr` to a file:

```bash
DEBUG='devtool-mcp-server:connector' agent-lynx list-clients 2> /tmp/devtool-connector-debug.log
```
