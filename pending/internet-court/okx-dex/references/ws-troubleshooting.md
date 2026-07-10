# Capability: WS — Troubleshooting

Error handling and edge cases for the WS capability. Operational flow lives in `ws.md`.

## Edge Cases

- **`ws poll` returns no events**: not an error — there are simply no new events since the last poll. For low-traffic channels (e.g. a single token's `trades`), gaps of minutes are normal. Poll again later rather than restarting the session.
- **Session not found on `ws poll` / `ws stop`**: the session likely hit its idle-timeout (default `30m` without a poll) and auto-stopped. Run `onchainos ws list` to see live sessions; restart with `ws start` if needed. For long-gap monitoring, pass a larger `--idle-timeout` (`1h`, `2h`) or `0` to disable.
- **Missing required parameter on `ws start`**: each channel has its own required params (see the Channel Quick Reference in `ws.md`) — `--token-pair` for per-token channels, `--chain-index` for per-chain channels, `--wallet-addresses` for the address tracker. `--token-pair` format is `chainIndex:tokenContractAddress`.
- **`--wallet-addresses` cap**: max 200 addresses per session — split larger sets across sessions.
- **Custom script cannot connect / auth fails**: verify the endpoint is `wss://wsdex.okx.com/ws/v6/dex`, HMAC-SHA256 login is performed before subscribing, and a `"ping"` heartbeat is sent every 25s (server closes idle unauthenticated connections). Full protocol per channel group: the `*-ws-protocol.md` files listed in `ws.md`.
- **Events stop after ~30s of connection in a custom script**: almost always a missing heartbeat — send `"ping"` every 25s and expect `"pong"`.

## Region Restrictions (IP Blocking)

When a command fails with error code `50125` or `80001`, display:

> DEX is not available in your region. Please switch to a supported region and try again.

Do not expose raw error codes or internal error messages to the user.
