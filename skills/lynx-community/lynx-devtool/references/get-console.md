# Get Console

Capture console logs from the device. This command connects to a Lynx session and streams console logs (Runtime.consoleAPICalled events) for a short duration or until a limit is reached.

## Usage

```bash
agent-lynx get-console [options]
```

## Options

- `-c, --client <clientId>`: Client ID. If not provided, the command will attempt to discover the first available client.
- `-s, --session <sessionId>`: Session ID. If not provided, the command will attempt to discover the latest session (with the largest session ID).
- `--offset <number>`: The number of console messages to skip before returning results. Default is `0`.
- `--limit <number>`: The maximum number of console messages to return. Values are clamped between 1 and 100.
- `--include-stack-traces`: By default, only error messages include stack traces. Set this flag to include stack traces for all message types.
- `--level <levels>`: A comma-separated list of log levels to filter. Default is `info,log,warning,error`.
- `--thread <thread...>`: Target VM thread(s): `background` or `main`. If omitted, the command collects logs from both threads.
- `-w, --watch`: Stream console logs as they arrive, printing each message immediately, until interrupted with `Ctrl+C` or `--limit` is reached. Without this flag, the command uses the short-window behavior described below.

## Behavior

Default mode (without `--watch`): the command listens for logs for up to 5 seconds and prints them all at once when finished. It stops early if:

- The `--limit` is reached.
- No new logs are received for 500ms.

Watch mode (`--watch`): the command streams console messages as they arrive, printing each one immediately. It only stops when:

- The process is interrupted with `Ctrl+C`, or
- The `--limit` is reached.

`--offset`, `--level`, `--include-stack-traces` and `--thread` apply in both modes.

By default, the command enables both background and main-thread runtimes to capture logs from both VMs.

## Output

The output is formatted text where each line represents a console message. The format is:
`- [<type>/<thread>]: <message>`

Thread label mapping:

- `main-thread`: messages from the main-thread VM (`consoleTag` is `Lepus`).
- `background`: messages from the background VM.

If a message contains an object or array, it will be represented with its description and `objectId` (e.g., `<Object (objectId:123)>` or `<Array(1) (objectId:456)>`).

If `--include-stack-traces` is set or the message type is `error`, the stack trace will be printed below the message.

## Examples

### Get all recent logs

```bash
agent-lynx get-console
```

### Get only errors

```bash
agent-lynx get-console --level error
```

### Get logs with stack traces

```bash
agent-lynx get-console --include-stack-traces
```

### Get only main-thread logs

```bash
agent-lynx get-console --thread main
```

### Pagination (Skip and Limit)

Skip the first 10 logs and get the next 5.

```bash
agent-lynx get-console --offset 10 --limit 5
```

### Watch logs live

Stream messages as they happen, until `Ctrl+C`:

```bash
agent-lynx get-console --watch
```

Watch only errors, and stop after the first 20:

```bash
agent-lynx get-console --watch --level error --limit 20
```
