# longbridge-subscriptions

Diagnostic listing of the active real-time subscriptions in the current `longbridge` CLI session.

`default_install: false` — not installed by default. Manual symlink only.

## CLI

```bash
longbridge subscriptions --format json
```

Returns an array of `{symbol, sub_types: [...], candlestick_periods: [...]}` for every active subscription in this CLI session.

## Local-only

The Longbridge MCP service is stateless HTTP — it has **no** WebSocket session concept and **no** equivalent tool. This skill requires the local `longbridge` CLI (which holds the OAuth + WebSocket session).

If `longbridge` is not installed, tell the user this skill is local-only and they need to install longbridge-terminal.

## Error handling

If `longbridge` is missing, surface the message — there is no MCP fallback. If stderr says `not logged in`, tell the user to run `longbridge auth login`.
