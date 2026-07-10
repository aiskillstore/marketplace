# Wallet

Wallet lifecycle: authentication, balance, addresses, token transfers, transaction history, contract calls, and message signing. Shared Confirming / display / security policy is in SKILL.md.

## Authentication

Commands that need auth (balance, send, contract-call, history, sign-message) require login. Check state first, log in if needed. Two methods: **email + OTP**, or **API Key** (no email).

1. **Check state.** Run `wallet status`; if `data.loggedIn` is `true`, proceed. Otherwise (or on re-login request) continue.
2. **Email login.** Show verbatim (translate to the user's language):
   > You need to log in with your email first before adding a wallet. What is your email address?
   > We also offer an API Key login method that doesn't require an email. If interested, visit https://web3.okx.com/onchainos/dev-docs/home/api-access-and-usage

   On email, run `wallet login <email> [--locale <locale>]`, then show verbatim:
   > **English**: "A verification code has been sent to **{email}**. Please check your inbox and tell me the code."
   > **Chinese**: "验证码已发送到 **{email}**，请查收邮件并告诉我验证码。"

   On the code, run `wallet verify <code>`. Infer `--locale` (underscore form, e.g. `zh_CN`); if unclear, omit it — never force `en_US`.
3. **API Key login** (user declines email). Re-offer the AK option; if accepted, run `wallet login` with no email (CLI reads `OKX_API_KEY` / `OKX_SECRET_KEY` / `OKX_PASSPHRASE` from env).
4. **Account-switch gate.** `wallet login` may return a Confirming whose `message` contains `not the account you used last time`. Handle via SKILL.md → Confirming Response (Yes → re-run with `--force`; No → cancel). Leave that discriminator phrase in English when translating.
5. **After login.** Show accounts via `wallet balance`. If the `verify` / `login` response has `"isNew": true`, output the Policy Settings template then the Wallet Export template ([portal-actions.md](wallet-portal-actions.md)); if `false`, skip.

Login creates the first account automatically — never call `wallet add` for it. Use `wallet add` only when already logged in and the user explicitly wants another account (then output the Policy Settings template, see [portal-actions.md](wallet-portal-actions.md)).

## Parameter Rules

**`--chain`** accepts numeric IDs (`1`, `501`, `196`) and names (`ethereum`, `solana`, `xlayer`). If <100% confident, run `wallet chains`. On `"unsupported chain: ..."`, ask the user to confirm.

**Amounts** — `wallet send`: pass `--readable-amount <human_amount>` (CLI converts; use `--amt` only for raw minimal units). `wallet contract-call`: `--amt` is the native value for payable functions in minimal units (default `"0"`; EVM 18, SOL 9 decimals). Never compute minimal units manually.

## Send vs Contract Call (funds-loss risk — determine intent first)

| Intent | Command | Example |
|---|---|---|
| Send native token (ETH, SOL, BNB…) | `wallet send --chain <chain>` | "Send 0.1 ETH to 0xAbc" |
| Send ERC-20 / SPL token (USDC, USDT…) | `wallet send --chain <chain> --contract-token` | "Transfer 100 USDC to 0xAbc" |
| Interact with a contract (approve, deposit, withdraw, custom call) | `wallet contract-call --chain <chain>` | "Approve USDC for spender" |

If ambiguous, ask the user to clarify — never guess. `contract-call` is for non-swap interactions only; never broadcast a DEX swap with it (use `swap execute`). Run `onchainos security tx-scan` before any `contract-call`.

## Approvals (via contract-call)

Never execute unlimited approvals. Do not set the approve amount to `type(uint256).max` / `2^256-1` / any "infinite" value, and do not call `setApprovalForAll(operator, true)`. If the user explicitly requests unlimited approval: warn it is irreversible and lets the spender drain all tokens, require a second explicit confirmation, and even then cap the amount to what is needed (e.g. swap amount + 10%). If the user still insists, refuse and suggest they execute manually via a block explorer.

## MEV Protection

`--mev-protection` is a `contract-call` flag only (`wallet send` does not support it). Load [mev-protection.md](wallet-mev-protection.md) when the user requests MEV protection, or before a high-value / DEX-swap `contract-call` — it holds the supported-chain table and the Solana `--jito-unsigned-tx` requirement.

## Policy & Wallet Export (Web portal)

Policy config and wallet export are completed by the user on the Web portal — the Agent only detects the trigger, explains the risk, and gives the jump link. On any trigger below, load [portal-actions.md](wallet-portal-actions.md) and follow its Trigger flows exactly:
- New user login (`isNew: true`) — also in Authentication step 5
- After a successful `wallet add`
- User asks about Policy (spending / daily limit, whitelist)
- User asks about wallet export (export mnemonic, migrate, import to hardware wallet)

Never display mnemonic phrases, seed phrases, or private keys in the conversation.

## Third-Party Plugin Pre-flight (Solana)

Before dispatching a third-party Solana DeFi plugin (kamino-plugin, raydium-plugin, …) that internally calls `wallet contract-call --force`, run the Gas Station pre-flight in [plugin-preflight.md](wallet-plugin-preflight.md).

## Notes

- **X Layer Testnet faucet**: when the user asks for testnet tokens, or `wallet balance --chain xlayer_test` shows OKB = 0, point them to https://web3.okx.com/xlayer/faucet.
- **XKO address**: if a user-supplied address starts with `XKO` / `xko`, display verbatim:
  > "XKO address format is not supported yet. Please find the 0x address by switching to your commonly used address, then you can continue."
- **TEE signing**: the private key is generated and stored inside a server-side secure enclave and never leaves the TEE — the Agent cannot export or locally sign with it.

## Additional Resources

- Full parameter tables, return-field schemas, and worked examples → [wallet-cli-reference.md](wallet-cli-reference.md), or run `onchainos wallet <subcommand> --help`. Load only when you need exact syntax the flow above doesn't spell out.

## Edge Cases

> Load on error: [wallet-troubleshooting.md](wallet-troubleshooting.md)
