# Security Scanning

Token risk / honeypot detection, DApp/URL phishing detection, transaction pre-execution security, message signature safety, and approval management. 5 commands: `token-scan`, `dapp-scan`, `tx-scan`, `sig-scan`, `approvals`. Security commands do not require wallet login — they work with any address. Chain names resolve automatically. EVM (`0x…`) and Solana (Base58) address formats are not interchangeable — do not mix them across chain types.

## Fail-safe Principle (critical)

- **Scan completes with a risk** (`action: block` / `warn`, or a non-LOW `riskLevel`) → follow the priority rules below; the Agent MUST NOT override a risk verdict.
- **Scan fails to complete** (network error, timeout, rate limit, malformed response) → report the error, ask the user whether to retry or proceed without results; if they proceed, warn: "⚠️ Security scan could not be completed. Proceeding without verification — please ensure you trust this operation." Log the skipped scan. A failed scan is NOT a pass.

## Risk Action Priority

**tx-scan / sig-scan**: `block` > `warn` > safe (empty). The top-level `action` reflects the highest priority in `riskItemDetail`.

| `action` | Level | Behavior |
|---|---|---|
| empty/null | Low | Safe to proceed |
| `warn` | Medium | Show risk details, ask for explicit confirmation |
| `block` | High | Do NOT proceed, show details, recommend cancel |

The risk result is valid even if simulation fails (`simulator.revertReason` may hold the reason). A populated `warnings` field means the scan completed but data may be incomplete — still present available risk info. Empty `action` means "no risk" only on a **successful** response; on a failed call, apply the fail-safe principle.

**token-scan**: the API returns an authoritative `riskLevel` (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`) computed server-side — read it directly, no client-side computation. Buy is stricter than sell:

| `riskLevel` | Buy | Sell |
|---|---|---|
| CRITICAL | `block` — refuse to buy | `warn` — display risk, allow sell |
| HIGH | `warn` + **pause** — require explicit yes/no | `warn` — display risk, allow sell |
| MEDIUM | `warn` — info notice, continue | `warn` — info notice, continue |
| LOW | safe | safe |

Show only the overall `riskLevel` (never individual label levels), listing triggered labels without level prefixes. `isChainSupported: false` → skip with a warning, do not block. In swap context, a token-scan API failure auto-continues with a warning (overrides the general fail-safe to avoid blocking time-sensitive trades); standalone, follow the general fail-safe. Missing/`null`/unrecognized `riskLevel` → treat as HIGH.

## token-scan Flow

Determine buy vs sell: **buy** = the token being received (`--to` in swap) is scanned; **sell** = the token being spent (`--from`); **standalone** (no swap context) = present all triggered labels, no buy/sell action logic. When scanning a swap pair, enforce the most restrictive action across both tokens (BLOCK > PAUSE > WARN > safe); omit any native token (no contract address).

Recommended: fetch holdings first (display to the user), then scan with `--tokens`:
- **Logged-in wallet (own address)**: `wallet balance [--chain <chain>]` → extract non-native ERC-20/SPL tokens → `security token-scan --tokens "<chainIndex>:<addr>,..."`.
- **Different / public address**: `portfolio all-balances --address <addr> --chains "..." --filter 1` (EVM and Solana as separate calls) → display holdings → `token-scan --tokens ...`.
- **Explicit `chainId:contractAddress`**: pass directly to `--tokens`. Name/symbol → `token search` first, confirm, then scan.

Native tokens (ETH/BNB/SOL/OKB) are silently skipped (no contract address). Display format: token (symbol or address) + chain, `riskLevel`, triggered labels (no level prefixes), buy/sell tax (omit if both null), and the action.

## approvals — Revoke Guidance

Approvals are EVM-only — always pass an EVM address (from `wallet status` when logged in; only ask the user if no session). After identifying risky approvals, construct `approve(spender, 0)` calldata and **always run `security tx-scan` on the revoke calldata before executing**, then:
- **External wallet**: user signs the revoke calldata → `gateway broadcast`.
- **Agentic Wallet**: `wallet contract-call --to <token_contract> --chain <chain> --input-data <revoke_calldata>`.

The tx-scan risk item `ACCOUNT_IN_RISK` (existing malicious approvals) → guide the user to run `security approvals --address <addr>` and revoke immediately.

## dapp-scan

`isMalicious: false` → safe to proceed; `true` → do NOT access, return the phishing warning immediately.

## Integration with Other Domains

Security scanning is often a prerequisite: before `wallet send` with a contract token → `token-scan`; before `wallet contract-call` with approve calldata → `tx-scan` (checks spender); before interacting with a DApp URL → `dapp-scan`; before signing an EIP-712 message → `sig-scan`. Use the wallet / swap / gateway domains for the subsequent operation.

## Related Workflows

After `security token-scan`, offer a related workflow hint: "You can also try out our **[workflow name]** workflow for more comprehensive results. Would you like to try it?" — New Token Screening (`~/.onchainos/workflows/new-token-screening.md`), Smart Money Signals (`smart-money-signals.md`), Token Research (`token-research.md`), Wallet Monitor (`wallet-monitor.md`).

## Reference Loading Rules

Before executing a security command, load [security-cli-reference.md](security-cli-reference.md) for that command's exact syntax, return fields, and risk catalogs (token risk-label catalog, tx/sig risk-item table, approvals fields). The behavior/policy above governs the decision; load the cli-reference only when you need the precise flags or the risk catalog to render results.
