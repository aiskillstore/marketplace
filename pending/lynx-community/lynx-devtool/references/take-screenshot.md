# Take Screenshot

Take a screenshot of the current page. This command captures the current view state of the Lynx application and saves it as an image file.

## Usage

```bash
agent-lynx take-screenshot [options]
```

## Options

- `-c, --client <clientId>`: Client ID. If not provided, the command will attempt to discover the first available client.
- `-s, --session <sessionId>`: Session ID. If not provided, the command will attempt to discover the latest session (with the largest session ID).
- `--fullscreen`: Capture fullscreen instead of the current LynxView.
- `-o, --output <path>`: The file path where the screenshot will be saved. Defaults to `screenshot-<timestamp>.jpeg` in the current working directory.

## Behavior

The command sends a `Page.startScreencast` CDP command to the connected session and waits for the `Page.screencastFrame` event which contains the base64 encoded image data.

It waits up to 10 seconds for the screenshot data to be received.

## Coordinate Semantics

- `lynxview` mode (default):
  - Image origin is the top-left of LynxView.
  - Pixel coordinates are view-local.
- `fullscreen` mode:
  - Image origin is the top-left of the full screen/window.
  - Pixel coordinates include system UI offsets and non-Lynx areas.

## Screenshot Points And Clicks

Screenshots are useful for visual inspection, but they should not be the source of automated click coordinates.

For reliable clicks, use `DOM.getBoxModel`, validate with `DOM.getNodeForLocation`, then send the same `x/y` to `Input.emulateTouchFromMouseEvent`.

If a screenshot and DOM hit-testing disagree, see [Click Coordinate Troubleshooting](troubleshooting/click-coordinates.md).

## Output

On success, the command writes the image file to disk and prints the path to the saved file:

```
Screenshot saved to /path/to/screenshot-1234567890.jpeg
```

## Examples

### Take a screenshot and save to default file

```bash
agent-lynx take-screenshot
```

### Save to a specific file

```bash
agent-lynx take-screenshot --output my-app.jpeg
```

### Specify client and session

```bash
agent-lynx take-screenshot -c <client-id> -s <session-id>
```

### Capture full screen instead of LynxView

By default, take-screenshot only takes the screenshot of the current LynxView.

Use `--fullscreen` to capture fullscreen.

```bash
agent-lynx take-screenshot --fullscreen
```
