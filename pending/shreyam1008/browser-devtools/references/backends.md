# Chrome connection and tool setup

Use **native `agent-browser` plus installed Chrome** for ordinary network, console, storage, DOM, React, and focused trace work. Keep one persistent session. Chrome still supplies the browser/renderer processes; Rust describes the controller, not a replacement browser engine or a measured speed guarantee.

## Discover and launch

1. Resolve `agent-browser` on PATH or the project's configured tool path. A personal portable installation may live under `${CODEX_HOME}/tools/browser-devtools/` (or `~/.codex/tools/browser-devtools/`), with `.exe` on Windows. Inspect its recorded version/hash if present. Do not assume another machine has it installed.
2. Read `--version` and `--help`, then narrow operation help. If narrow help falls back to generic output, consult the installed release's [official documentation/source](https://github.com/vercel-labs/agent-browser). A guide advertised in documentation may be absent from a standalone executable; inspect availability rather than repeatedly requesting a missing guide. Avoid loading the full command catalog for each action.
3. Reuse an installed Google Chrome executable through the supported executable-path option. For a new investigation, select the Chrome engine explicitly and use an owned, isolated headless session/namespace. Inspect effective config, environment, provider, and attachment settings so a local session is actually local. A scoped scratch config can override inherited defaults without modifying user configuration.
4. Keep the same session identity/settings across calls. Use a fresh owned profile directory with no auth restore for a disposable investigation. Preserve normal cache/worker behavior and visible scrollbars (`--hide-scrollbars false` in current releases). Use the supported WebMCP opt-out for ordinary diagnostics; inspect dialog handling and opt out of automatic dismissal when dialogs matter. Add `--enable react-devtools` at launch only for React tasks, before React loads.
5. Take a compact snapshot, act on observed selectors/references, and wait for the expected UI state. Batch small independent reads or already-understood actions when the installed CLI supports it. Do not batch dependent actions that require an unseen result, or run concurrent navigation/recording on one session. Close the owned session/daemon and confirm cleanup when done.

Keep output small with supported filters, tree depth, and compact/JSON output. A truncated result is not complete evidence; save large artifacts and inspect the relevant portion. Refresh element references after navigation or structural changes. Command success does not prove the intended application action completed.

Minimal PowerShell pattern, after resolving placeholders and checking installed flags:

```powershell
$browserCli = '<resolved-agent-browser-executable>'
$chromeArgs = @('--namespace', '<unique-task>', '--session', 'inspect',
  '--engine', 'chrome', '--executable-path', '<installed-Chrome>',
  '--profile', '<task-scratch>/chrome-profile', '--headed', 'false',
  '--no-webmcp', '--hide-scrollbars', 'false', '--restore-save', 'never')
& $browserCli @chromeArgs open '<url>'
& $browserCli @chromeArgs snapshot -i
# Collect relevant evidence/reproduce with the same arguments.
& $browserCli @chromeArgs close
```

Keep profile/capture directories outside watched source roots to avoid dev-server reloads or file locks. Confirm the owned processes stopped before removing the owned scratch profile. For a requested existing session, use its documented attachment path instead of this launch pattern. Verify the intended tab; use supported tab pinning (currently `--pin-tab`) to fail if that tab disappears rather than falling back to another. Never substitute the user's Chrome profile directory into the launch pattern.

If a Windows Node wrapper waits after a complete successful response, check the client process exit: the daemon can keep inherited capture pipes open. Bound the wrapper, consume the complete response, and release its captured streams after client exit. This is separate from closing the browser session. The direct PowerShell pattern needs no wrapper.

## Installation and maintenance

If the native tool is missing, install only this controller using an official package or the [release asset](https://github.com/vercel-labs/agent-browser/releases) for the host architecture. Resolve an exact version at setup, verify available authoritative digest/signature metadata before executing downloaded binaries, and record the source/version/hash. A portable binary avoids global PATH/config changes and extra platform binaries. Reuse existing Chrome; download a compatible browser only if missing or required by a verified compatibility gap.

Do not resolve `latest` or upgrade on every investigation. Update explicitly, review release notes, and rerun a local smoke scenario for requests, console, storage, trace capture, and React when used. Read schemas/help again after updates. Skill installation itself installs instructions, not a browser connection.

## Advanced Chrome DevTools fallback

Use the [official Chrome DevTools MCP/CLI](https://github.com/ChromeDevTools/chrome-devtools-mcp) when the native CLI lacks the needed operation: heap snapshots/retainers, richer trace insights, breakpoint debugging, or discovered page developer tools. Use existing connected tools first. For a CLI, read installed help and the release-matched [CLI guide](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/cli.md); scope an owned daemon's file access to the task workspace when supported. For MCP, discover exposed tools/schemas and select the intended page/frame. Optional categories and modes affect the actual inventory; neither remembered tool counts nor outdated prose establish capabilities.

Choose one controller/recorder for an action. Prefer analyzing an existing capture over recreating the browser unnecessarily. For a live fallback, coordinate attachment or create a comparable owned Chrome session and label changed conditions. Do not close or relaunch a user's browser. For manual teaching/UI access, use the corresponding current DevTools panel.

React third-party discovery requires tools registered by the page; it is not automatic React access. See the [React workflow](react.md). Current maintained [Chrome agent skills](https://github.com/ChromeDevTools/chrome-devtools-mcp/tree/main/skills), [tool reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md), and [configuration](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/configuration.md) are operation references; use the installed release rather than copying their catalog here.

## Specific CDP gap

Use an existing client for a specific remaining operation. Keep local debugging on loopback with a separate profile. [Chrome remote debugging](https://developer.chrome.com/blog/remote-debugging-port) requires a non-default user-data directory for debugging switches in ordinary Chrome; never target the user's default profile.

When an HTTP debug endpoint exists, `/json/version` identifies the endpoint/browser and `/json/protocol` supplies its schema. Otherwise use the transport's supported discovery and matching [CDP documentation](https://chromedevtools.github.io/devtools-protocol/). The historical stable 1.3 label and tip-of-tree are not the installed target's manifest. Enable only relevant domains, subscribe before the action, track frame/worker/session/request IDs, and inspect the schema after an unsupported operation instead of guessing signatures. Stop recordings, drain/close returned streams, and detach cleanly.
