# Recording

Record Lynx page interactions via TestBench (CDP-based). Captures all actions (template loads, touch events, JS module calls, data updates) and produces a JSON replay file.

## Usage

```bash
agent-lynx recorder start [options]
agent-lynx recorder end [options]
```

## Options

### recorder start / recorder end

- `-c, --client <clientId>`: Client ID. If not provided, the command will use the first available client.
- `-o, --output <path>`: Output file or directory path for `end`. Defaults to `~/.lynx-devtool/files/lynxrecorder/recording-<clientId>-<timestamp>.json`.

## Behavior

### recorder start

`recorder start` first checks the `enable_debug_mode` global switch. If the switch is off, the command enables it, exits, and asks the user to restart the app before running `recorder start` again. This restart is required for the native TestBench recorder path to become available.

After `enable_debug_mode` is already on, `Recording.start` is sent as a CDP message via the connector. For the cleanest replay, open or reload the target page after recording starts so the file includes `loadTemplate`.

The recording target session is implicitly session `-1` (the global session).

### recorder end

`Recording.end` is sent via the streaming CDP endpoint. The command waits for the `Recording.recordingComplete` event, then reads the recorded stream data via `IO.read` in 1 MB chunks. Each session's stream is saved to a separate JSON file.

If `--output` is specified as a directory path, files are named `<directory>/recording-<clientId>-<timestamp>[-session<N>].json`.

## Workflow

1. Run `recorder start`. If it enables `enable_debug_mode`, restart the app and run `recorder start` again.
2. User opens and interacts with the Lynx page.
3. Run `recorder end` to stop and save.
4. Report the saved file path to the user.

## Output

On success `recorder end` writes the recording to disk:

```json
{
  "success": true,
  "message": "Recording ended successfully.",
  "savedFiles": ["/path/to/recording-xxx.json"]
}
```

## Examples

### Start recording

```bash
agent-lynx recorder start
```

### Start recording with a specific client

```bash
agent-lynx recorder start --client <clientId>
```

### Stop recording and save to a custom path

```bash
agent-lynx recorder end --output ./my-recording.json
```

## Diagnosing Recording Files

A recording JSON file is either a top-level array of actions, or an object with an `"Action List"` array. Some files are base64-encoded zlib-compressed JSON. Each action has a `"Function Name"` field.

### Key sections in a healthy recording

| Section       | Indicator                                                      | Meaning                                                            |
| ------------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| Template load | Action with `"Function Name": "loadTemplate"`                  | The page was loaded during recording — required for a valid replay |
| Touch events  | `"SendTouchEvent"` or `"sendEventDarwin"` actions              | User interactions were captured                                    |
| Other actions | Any other function names (JS module calls, data updates, etc.) | Additional page lifecycle events                                   |

### Diagnosing recordings

| Symptom                                               | Likely cause                                                                                          | Action                                                                                                                                                                 |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File is empty or unparseable                          | Recording was interrupted, device disconnected mid-stream, or file was corrupted during write         | Re-run from `recorder start` with a stable connection                                                                                                                  |
| Zero actions (`"Action List": []`)                    | Recording started and ended immediately with no page activity in between                              | Ensure the user opens and interacts with the page between `start` and `end`                                                                                            |
| Has touch events but no `loadTemplate`                | Recording started on a page that was already open — the template load happened before recording began | Still useful for analyzing interactions (JSB calls, gestures), but cannot be replayed in Lynx Explorer. For a replayable file, start recording before opening the page |
| Has actions but no `loadTemplate` and no touch events | Partial capture — page may have been in an intermediate state                                         | Still useful for inspecting recorded behavior. For a replayable file, re-record from a fresh app launch                                                                |

### Automated analysis on `recorder end`

`recorder end` automatically analyzes each saved file after writing. It warns if a file is truly unusable (empty or unparseable), and notes when files lack `loadTemplate` (not replayable but still informative). No separate diagnostic step is needed.
