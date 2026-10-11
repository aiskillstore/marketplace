# Setup and operation examples

Inspected 2026-10-06 against upstream commit `f87265e4768e3456381d50ef24443e256f5315cd`. Released binaries may differ; installed help takes precedence.

Sources: [README](https://github.com/moeru-ai/auv/blob/f87265e4768e3456381d50ef24443e256f5315cd/README.md), [invoke help](https://github.com/moeru-ai/auv/blob/f87265e4768e3456381d50ef24443e256f5315cd/crates/auv-cli-invoke/src/help.rs), [input commands](https://github.com/moeru-ai/auv/blob/f87265e4768e3456381d50ef24443e256f5315cd/crates/auv-cli-invoke/src/commands/input.rs), [window commands](https://github.com/moeru-ai/auv/blob/f87265e4768e3456381d50ef24443e256f5315cd/crates/auv-cli-invoke/src/commands/window.rs), [result envelope](https://github.com/moeru-ai/auv/blob/f87265e4768e3456381d50ef24443e256f5315cd/crates/auv-cli-invoke/src/models/invoke_result.rs).

## Setup

Upstream's prebuilt macOS installation:

```sh
brew install moeru-ai/tap/auv
auv --version
```

Official releases include the signed helper. If needed on macOS 13+:

```sh
auv setup macos-helper install
auv setup macos-helper status
```

The user grants Accessibility for AX/input, Screen Recording for capture/OCR, and Automation for relevant activation fallbacks to the application launching AUV. This can be the agent's host rather than an interactive terminal. Restart that launcher after permission changes, then run `auv doctor` and `auv invoke app.probePermissions`. Helper setup can also require user approval of Background Items/Accessibility. Do not change OS permissions automatically.

Linux/Windows have native drivers, but individual core commands have narrower platform support. Follow upstream installation instructions and installed help rather than transplanting macOS selectors. Windows helper setup requires elevated PowerShell. Cargo/Nix builds do not embed the signed macOS helper. The inspected README lists a first-party Python SDK and AUV REPL as planned; do not assume they exist.

## Core examples

These demonstrate syntax; substitute identifiers/titles from live observations. Do not execute TextEdit examples as an incidental test on the user's desktop.

```sh
auv invoke window.list --json
auv invoke window.capture --target app:com.apple.TextEdit --title Untitled --json
auv invoke window.findText 'Search' --target app:com.apple.TextEdit --title Untitled --json
auv invoke input.focusText 'Search' --target app:com.apple.TextEdit --json
auv invoke input.typeText 'example query' --target app:com.apple.TextEdit --input-policy foreground-preferred --json
auv invoke input.pressKeys cmd a --target app:com.apple.TextEdit --json
auv invoke window.waitForText 'Ready' --target app:com.apple.TextEdit --title Untitled --json
```

Inspect help for wait limits and OCR candidate selection. `window.clickText` locates/clicks OCR anchors: disambiguate instead of blindly using candidate zero. `input.clickPoint` accepts logical coordinates or target-local normalized values where supported. A window target supported by keyboard commands is not proof that capture/OCR accepts it.

For ordered keyboard actions, inspect `input.keyboard --help`; `--actions` accepts tagged JSON actions. Limit batches to actions safe without intermediate verification; do not bundle submission after unverified field edits.

## Plugins, MCP, remote targets

- `auv plugin list` discovers `auv-*` executables on PATH. Inspect `auv <plugin-name> --help`; core installation does not guarantee app/game plugins are installed.
- The optional stdio MCP server uses command `auv`, args `["mcp", "serve"]`. Use the host's supported registration flow when integration setup is requested. Starting a server alone does not expose tools to an active chat.
- `auv devices list` discovers daemon-visible Devices. Root selection precedes the subcommand: `auv --device-id <observed-id> invoke display.list --json`. Preserve selection for every related call. Pairing/enrollment is separate setup.
- Inspect `auv run --help` for correlation/inspection and `auv runner --help` for persistent execution when needed. Do not start network listeners, enroll unlock credentials, or modify host configuration incidentally for local one-off operations.
