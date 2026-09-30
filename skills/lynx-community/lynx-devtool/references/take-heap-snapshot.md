# Take Heap Snapshot

Take a QuickJS heap snapshot from the current Lynx session and save it as a `.heapsnapshot` file.

## Usage

```bash
agent-lynx take-heap-snapshot [options]
```

## Options

- `-c, --client <clientId>`: Client ID. If not provided, the command will use the first available client.
- `-s, --session <sessionId>`: Session ID. If not provided, the command will use the latest session.
- `--thread <thread>`: Target VM thread. Supported values are `background` and `main`. Defaults to `background`.
- `-o, --output <path>`: Output file path. Defaults to `<tmpdir>/heap-<thread>-<timestamp>.heapsnapshot`.

## Behavior

The command enables `HeapProfiler`, requests `HeapProfiler.takeHeapSnapshot`, collects all `HeapProfiler.addHeapSnapshotChunk` events, and writes the merged payload to disk.

When `--thread main` is used, the command targets the Lynx main-thread VM by sending CDP requests with `sessionId: "Main"`.

The command waits up to 60 seconds in total and stops early if the stream goes idle for 15 seconds.

## Output

On success, the command writes the snapshot to disk and prints the saved path:

```
Heap snapshot saved to /tmp/heap-background-1234567890.heapsnapshot
```

## Examples

### Save a background-thread snapshot to the default temp file

```bash
agent-lynx take-heap-snapshot
```

### Save a main-thread snapshot

```bash
agent-lynx take-heap-snapshot --thread main
```

### Save to a specific file

```bash
agent-lynx take-heap-snapshot --output ./session.heapsnapshot
```
