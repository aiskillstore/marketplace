# agent-transit

A transit map for your coding-agent sessions.

![Animated Transit map of a coding-agent session: tool families are lines, tool calls are stations, with DELAY and SERVICE ALERT markers on slow and failed calls](https://raw.githubusercontent.com/israelvicars/transit/main/docs/agent.gif)

## Example prompts

- “Make an MP4 of my last Claude Code session.”
- “Draw my latest Codex session as a transit map. Which tool calls were slow?”
- “Render my newest Cursor session as a GIF.”
- “Map this saved session log and show me where the tool errors were.”

## What it maps

Tool families become lines and tool calls become stations. Long calls receive DELAY markers, while errors or denials receive SERVICE ALERT markers.

Supported sources are Claude Code, Codex CLI, and Cursor (experimental). Session files and renders remain local.

## Install

```sh
npx skills add israelvicars/transit --skill agent-transit
```

## Privacy

Runs locally only, with no telemetry. By default it keeps only tool names, timing, status, target basenames, and the agent source.

[Back to the Transit README](https://github.com/israelvicars/transit#readme)
