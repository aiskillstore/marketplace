# Get Sources

List all parsed scripts in the current Lynx session.

## Usage

```bash
agent-lynx get-sources [options]
```

## Options

- `-c, --client <clientId>`: Client ID. If not provided, the command will attempt to discover the first available client.
- `-s, --session <sessionId>`: Session ID. If not provided, the command will attempt to discover the latest session (with the largest session ID).

## Behavior

1. **Connection**: Connects to the DevTool via WebSocket.
2. **Refresh Scripts**: Sends `Debugger.disable` followed by `Debugger.enable` to trigger the re-emission of `Debugger.scriptParsed` events for all existing scripts.
3. **Collection**: Listens for `Debugger.scriptParsed` events.
4. **Timeout**: The command runs for a maximum of 5 seconds. It also stops early if no new scripts are received for 2 seconds (idle timeout).

## Output

The output is a JSON array of objects, where each object represents a parsed script and contains:

- `scriptId`: The unique identifier for the script.
- `url`: The URL or path of the script.

```json
[
  {
    "scriptId": "12",
    "url": "file:///path/to/app-service.js"
  },
  {
    "scriptId": "13",
    "url": "file:///path/to/another-script.js"
  }
]
```

## Examples

### List currently known scripts

This command will list all scripts that are currently loaded in the VM.

```bash
agent-lynx get-sources
```
