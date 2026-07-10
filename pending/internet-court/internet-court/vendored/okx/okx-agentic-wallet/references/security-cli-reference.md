# Security Scanning — CLI Reference

Syntax, parameters, return fields, and risk catalogs for the 5 `onchainos security` subcommands. Behavior/policy is in [security.md](security.md). Verify flags with `onchainos security <subcommand> --help` when unsure.

## `security token-scan`

Batch token risk / honeypot detection (all chains).

```bash
onchainos security token-scan --tokens "<chainId>:<addr>[,...]"   # primary mode (max 50 pairs)
onchainos security token-scan [--chain <chain>]                    # logged-in wallet shortcut
onchainos security token-scan --address <addr> [--chain <chain>]   # public-address shortcut
```

`--tokens`: comma-separated `chainId:contractAddress` (chain as name or ID). The `--chain` / `--address` modes query the balance API first, then batch-scan. Native tokens (empty contract address) are skipped in all modes.

Return (per token): `chainId`, `tokenAddress`, `isChainSupported`, `riskLevel` (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`), `buyTaxes` / `sellTaxes` (string|null), and the boolean labels below.

### Token risk label catalog

**Critical (block buy):** `isHoneypot` (cannot sell after buying), `isRubbishAirdrop` (spam/scam airdrop), `isAirdropScam` (gas-mint scam).

**High (pause buy for confirmation):** `isHasAssetEditAuth` (privileged address — Solana only, `chainId 501`), `isLowLiquidity`, `isDumping`, `isLiquidityRemoval`, `isPump`, `isWash`, `isFakeLiquidity`, `isWash2`, `isFundLinkage` (rugpull gang), `isVeryLowLpBurn`, `isVeryHighLpHolderProp`, `isHasBlockingHis` (freeze history), `isOverIssued`, `isCounterfeit`, `isNotOpenSource`.

**Medium (info):** `isMintable`, `isHasFrozenAuth` (freeze authority), `isNotRenounced` (ownership retained).

Tax thresholds feed `riskLevel` server-side (do NOT recompute): ≥50% → contributes CRITICAL; 21–50% → HIGH; 0–21% → MEDIUM; 0/null → no tax risk. Display tax % when non-null; omit when null.

Interpretation: read `riskLevel` (authoritative); collect `true` boolean labels for display (include `isHasAssetEditAuth` only on Solana); if `riskLevel` is non-LOW but no label is true, display "flagged by composite analysis, no specific label identified". Apply the buy/sell action matrix (see [security.md](security.md)).

## `security dapp-scan`

DApp / URL phishing detection (chain-agnostic).

```bash
onchainos security dapp-scan --domain "https://some-dapp.xyz"
```

Returns `isMalicious` (boolean). `true` → do NOT access.

## `security tx-scan`

Transaction pre-execution scan (EVM + Solana).

```bash
# EVM
onchainos security tx-scan --chain <chain> --from <0x_addr> --data <calldata_hex> \
  [--to <address>] [--value <wei_dec_or_hex>] [--gas <n>] [--gas-price <n>]
# Solana
onchainos security tx-scan --chain solana --from <base58_addr> --encoding <base58|base64> --transactions <p1,p2,...>
```

EVM `--value` accepts decimal or hex wei (decimal auto-converted). Solana requires `--encoding` and `--transactions` (comma-separated payloads).

## `security sig-scan`

Message signature scan (EVM only).

```bash
onchainos security sig-scan --chain <chain> --from <0x_addr> \
  --sig-method <personal_sign|eth_sign|eth_signTypedData|eth_signTypedData_v3|eth_signTypedData_v4> \
  --message <message_or_typed_data_json>
```

### tx-scan / sig-scan shared return

`action` (`""` safe / `"warn"` / `"block"`), `riskItemDetail[]` (`name`, `description` map, `reason[]`, `action`), `simulator` (`gasLimit` / `gasUsed`, `revertReason`), `warnings[]`.

Risk items:

| Risk item | Meaning | Level | Action |
|---|---|---|---|
| `black_tag` | Target/asset/receiving address blacklisted | CRITICAL | block |
| `from_risk_reject` | Sender blacklisted | CRITICAL | block |
| `SPENDER_ADDRESS_BLACK` | Approval target blacklisted | CRITICAL | block |
| `ASSET_RECEIVE_ADDRESS_BLACK` | Asset receiving address blacklisted | CRITICAL | block |
| `purchase_malicious_token` | Purchasing a malicious token | CRITICAL | block |
| `ACCOUNT_IN_RISK` | Account has existing malicious approvals | CRITICAL | block — guide user to `security approvals` and revoke |
| `evm_7702_risk` | EIP-7702 high-risk sub-tx (no asset increase; ≈ permanent control / unlimited approval) | CRITICAL | block |
| `evm_7702_auth_address_not_in_whitelist` | 7702 upgrade contract not whitelisted (delegates to unverified contract) | CRITICAL | block |
| `evm_okx7702_loop_calls_are_not_allowed` | 7702 recursive call (re-entrancy drain) | CRITICAL | block |
| `TRANSFER_TO_SIMILAR_ADDRESS` | Vanity-address phishing | HIGH | warn — show full address comparison, require explicit confirmation |
| `SOLANA_SIGN_ALL_TRANSACTIONS` | Solana sign-all request | HIGH | warn |
| `multicall_phishing_risk` | Approval via multicall (phishing) | HIGH | warn |
| `approve_anycall_contract` | Approval to arbitrary external-call contract | HIGH | warn |
| `to_is_7702_address` | Target is a 7702-upgraded address | MEDIUM | warn |
| `TRANSFER_TO_CONTRACT_ADDRESS` | Transfer directly to a contract | MEDIUM | warn |
| `TRANSFER_TO_MULTISIGN_ADDRESS` | Tron transfer to multisig | MEDIUM | warn |
| `approve_eoa` | Approval to an EOA | MEDIUM | warn |
| `increase_allowance` | Increasing approval allowance | LOW | warn |
| `ACCOUNT_INSUFFICIENT_PERMISSIONS` | Tron account insufficient permissions | LOW | warn |

## `security approvals`

Token approval / Permit2 authorization query (EVM only).

```bash
onchainos security approvals --address <0x_addr> [--chain <names_or_ids>] [--limit <n>] [--cursor <string>]
```

`--chain` comma-separated (omit → all supported EVM chains); `--limit` default 20; `--cursor` from the previous response. Returns `approvalList[]` (`tokenSymbol`, `tokenAddress`, `chainIndex`, `spenderAddress`, `allowance` — raw, `"unlimited"` for max uint256, `riskLevel`) and `cursor`.
