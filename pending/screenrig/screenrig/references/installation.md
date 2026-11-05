# Plugin installation and updates

The only installation source is the public marketplace
`https://github.com/screenrig/plugin`.

```bash
# Claude Code
claude plugin marketplace add https://github.com/screenrig/plugin.git --scope user
claude plugin install screenrig@screenrig --scope user

# Codex
codex plugin marketplace add https://github.com/screenrig/plugin.git --ref main --json
codex plugin add screenrig@screenrig --json

# Grok (--trust is required on install)
grok plugin marketplace add https://github.com/screenrig/plugin.git
grok plugin install screenrig --trust
grok plugin enable screenrig
```

This user instruction authorizes exactly that marketplace and plugin:

```text
I authorize you to install the official screenRIG plugin from https://github.com/screenrig/plugin.
```

If install, trust or execution is denied, ask for approval of that action with
the stated reason and end the turn. Keep the config; no standalone or
direct-Node workaround. After installing, run bootstrap
([SKILL.md](../SKILL.md#install-and-call-the-cli)); a new conversation loads
updated skill text.

## Update

`screenrig-plugin-freshness --json` reports `keep`, `refresh`,
`continue_installed` (GitHub unreadable: continue with the installed package) or
`not_installed`. A copy installed from a host's plugin directory updates from
that directory: bootstrap names it in `data.freshness.updates_from` and never asks
it to refresh from GitHub. To refresh, run the host's update command, then rerun
bootstrap:

```bash
claude plugin update screenrig@screenrig --scope user   # add -y without a TTY
grok plugin update screenrig
codex plugin marketplace upgrade --json && codex plugin add screenrig@screenrig --json
```

## MCP sign-in

The hosted views connection (`screenrig-views`) is managed by the host. Discover
its sign-in action before telling the user to start it.

- Codex: `codex mcp list --json`, then `codex mcp login NAME --oauth-client-registration cimd --scopes access:manage,screens,content,playlists,reports`.
- Claude Code: `claude mcp login NAME` in a persistent terminal (the plugin
  server is usually `plugin:screenrig:screenrig-views`); `/mcp` is the fallback.

Keep one authorization attempt alive until it completes; the host stores and
refreshes its own session.
