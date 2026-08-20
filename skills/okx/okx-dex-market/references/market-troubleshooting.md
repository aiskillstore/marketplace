# Capability: Market — Troubleshooting

Error handling, edge cases, and region restrictions for the Market capability. Operational flow lives in `market.md`; parameter schemas in `market-cli-reference.md`.

## Region Restrictions (IP Blocking)

Some services are geo-restricted. When a command fails with error code `50125` or `80001`, return a friendly message without exposing the raw error code:

| Service | Restricted Regions | Blocking Method |
|---|---|---|
| DEX | United Kingdom | API key auth |
| DeFi | Hong Kong | API key auth + backend |
| Wallet | None | None |
| Global | Sanctioned countries | Gateway (403) |

**Error handling**: When the CLI returns error `50125` or `80001`, display:

> {service_name} is not available in your region. Please switch to a supported region and try again.

Examples:
- "DEX is not available in your region. Please switch to a supported region and try again."
- "DeFi is not available in your region. Please switch to a supported region and try again."

Do not expose raw error codes or internal error messages to the user.

## Edge Cases

- **Invalid token address**: returns empty data or error — prompt user to verify, or use `onchainos token search` to resolve
- **Unsupported chain**: the CLI will report an error — try a different chain name
- **No candle data**: may be a new token or low liquidity — inform user
- **Solana SOL price/kline**: The native SOL address (`11111111111111111111111111111111`) does not work for `market price` or `market kline`. Use the wSOL SPL token address (`So11111111111111111111111111111111111111112`) instead. Note: for **swap** operations, the native address must be used — see `okx-agentic-wallet`.
- **Unsupported chain for portfolio PnL**: not all chains support PnL — always verify with `onchainos market portfolio-supported-chains` first
- **`portfolio-dex-history` requires `--begin` and `--end`**: both timestamps (Unix milliseconds) are mandatory; if the user says "last 30 days" compute them before calling
- **`portfolio-recent-pnl` `unrealizedPnlUsd` returns `SELL_ALL`**: this means the address has sold all its holdings of that token
- **`portfolio-token-pnl` `isPnlSupported = false`**: PnL calculation is not supported for this token/chain combination
- **Network error**: retry once, then prompt user to try again later
