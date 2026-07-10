# Capability: Social — Troubleshooting

Error handling, edge cases, and region restrictions for the Social capability. Operational flow lives in `social.md`; parameter schemas in `social-cli-reference.md`.

## Edge Cases

- **Empty articles array**: no news matched the filters in the time window — suggest broadening (drop `--platform`, widen `--begin`/`--end`, drop `--sentiment` / `--importance`).
- **`news-detail` returns empty**: the article id may have expired or been delisted by the upstream platform. Ask the user to verify the id from a recent list call.
- **`sortBy` on `sentiment-ranking`**: only `1` (hot) is currently supported. If the user asks for "by mention count" or "by bullish ratio", explain the ranking is hot-only today and let them sort the result client-side.
- **Vibe symbol with no contract address**: the user asks "vibe for BTC" but the vibe pipeline is keyed by `chainIndex + tokenAddress`. Resolve to a contract address (e.g. the **Token** capability's `token search` for native bridged BTC), or explain why the request can't be answered as-is.
- **Vibe on a cold / new token**: `summary.score` may be `0` and `timeline` may be empty if there is no KOL chatter yet. Surface this rather than fabricating a trend.
- **`firstMention` is `null`**: the KOL had no first-mention recorded for this token in the window — render as "—" rather than a broken link.
- **Same-symbol collisions** (`PEPE` on Ethereum vs Solana): news / sentiment cannot disambiguate. If the user is asking about a specific contract, route to `vibe-timeline` / `vibe-top-kols` instead.
- **Language fallback**: not all upstream platforms translate every article. If the user requested `zh_CN` and the response is still in English, note that and proceed.
- **Network error**: retry once, then prompt the user to try again later.

## Region Restrictions (IP Blocking)

When a command fails with error code `50125` or `80001`, display:

> DEX is not available in your region. Please switch to a supported region and try again.

Do not expose raw error codes or internal error messages to the user.

## Error Codes

The social endpoints share the OKX standard error envelope. Common codes the agent should recognise (full list in the upstream `social-news-error-code` doc):

| Code | HTTP | Meaning | Suggested response |
|---|---|---|---|
| `0` | 200 | Success | — |
| `50011` | 429 | Rate limit exceeded | Back off 1–2s then retry once; on second failure, surface "the service is rate-limiting, please try again in a minute" |
| `50014` | 400 | Required parameter is empty | Re-check the call — typically a blank `tokenSymbols` / `articleId` / `chainIndex` / `tokenAddress` |
| `50026` | 500 | Upstream system error | Retry once; if still failing, surface "the service is temporarily unavailable" |
| `50103`–`50107` | 401 | Auth header missing (key / passphrase / sign / timestamp) | API credentials are not configured — ask the user to set `OKX_API_KEY` / `OKX_SECRET_KEY` / `OKX_PASSPHRASE` in their env or `~/.onchainos/.env` |
| `50111`–`50113` | 401 | Invalid API key / timestamp / signature | Credentials are present but rejected — suggest the user verify the keys in the OKX developer portal or check system clock skew |
| `50125` / `80001` | — | Region blocked (see section above) | Show the region message |
| `51000` | 400 | Parameter is invalid | Re-check enum codes — likely an out-of-range `importance` / `sentiment` / `sortBy` / `timeFrame` |

For x402 payment failures on payment-gated endpoints (`invalid payment header`, `payer_blocked`, `risk_address`, `not_yet_valid`, `expired`, `nonce_used`, `insufficient_balance`, `onchain_error`, `payment processing`, etc.), the canonical mapping lives in the upstream doc; the `notifications[]` handling in `_shared/payment-notifications.md` already covers the agent-side flow.

Never expose raw error codes or internal error messages to the user — always paraphrase per the rows above.
