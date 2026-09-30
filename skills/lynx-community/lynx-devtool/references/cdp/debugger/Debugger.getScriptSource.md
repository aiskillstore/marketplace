# Debugger.getScriptSource

- `Debugger.getScriptSource` - Returns source for the script with given id.
- Input: `{scriptId: string}`
- Output: `{scriptSource: string}`
- Description: Returns source for the script with given id.

## Usage

First, use `get-sources` command to find the script ID.

```bash
agent-lynx get-sources
```

Output:

```json
[
  {
    "scriptId": "1",
    "url": "file:///main-thread.js"
  },
  {
    "scriptId": "5",
    "url": "file:///krypton.js"
  }
]
```

Then, use the `cdp` command to get the source.

```bash
agent-lynx cdp --method Debugger.getScriptSource '{"scriptId": "1"}'
```

Output:

```json
{
  "scriptSource": "{globalThis.currentDebugAppId = \"5\"}"
}
```

## Notes

- If the `scriptId` is unknown to the selected VM thread, Lynx can return `{ "scriptSource": "" }`.
- Script ids are scoped to the target VM thread. A script id returned for the background thread may not be available when calling `Debugger.getScriptSource` with `--thread main`.
