# Take Content Screenshot

Capture the full scrollable content of the first node matching a CSS selector and save it as an image.

## Usage

```bash
agent-lynx take-content-screenshot --selector <selector> [options]
```

## Options

- `--selector <selector>`: CSS selector for a `scroll-view` or compatible `list`. Required.
- `--format <jpeg|png>`: Image format. Defaults to `jpeg`.
- `--scale <number>`: Positive output scale. Defaults to `1`.
- `-c, --client <clientId>`: Client ID. Auto-discovered when omitted.
- `-s, --session <sessionId>`: Session ID. The latest session is used when omitted.
- `-o, --output <path>`: Output path. Defaults to `content-screenshot-<timestamp>.<format>`.

## Behavior

The command evaluates a selector query in the background Lynx VM, invokes the node's asynchronous `takeContentScreenshot` UI Method, and polls for its callback for up to 30 seconds. The returned image data URL is decoded and written to disk. Temporary callback state is removed from `globalThis` on success or failure.

The upstream API is officially defined for `scroll-view`. The command accepts any CSS selector so it also works with `list` implementations or runtime extensions that expose `takeContentScreenshot`; an unsupported node reports the UI Method failure.

## Example

```bash
agent-lynx take-content-screenshot --selector '#feed' --format png --scale 1 -o feed.png
```

On success, the command prints the saved path and full image dimensions.
