# Wallet

## Module Description

Wallet lifecycle: authentication, balance, addresses, token transfers, transaction history, contract calls, and message signing. Shared Confirming / display / security policy is in SKILL.md.

## Intent Routing

| User intent | Reference | Hot command |
| --- | --- | --- |
| View my current wallet balance or total assets (excluding BTC, BRC-20, and explicitly specified token+chain holdings) | — | `onchainos wallet balance` |
| View balance or total assets across all wallet accounts | — | `onchainos wallet balance --all` |
| View my active account or login status | — | `onchainos wallet status` |
| View my wallet or account addresses (not a receive/deposit request) | — | `onchainos wallet addresses` |
| View my recent transaction history | — | `onchainos wallet history` |
| List supported wallet chains | — | `onchainos wallet chains` |

## Flow

### Authentication

Run `wallet balance`, `wallet send`, `wallet contract-call`, `wallet history`, and `wallet sign-message` directly. If a command reports that login is required, follow the login flow below.

1. **Log in** — orchestrate one continuous `init` → display link → `poll` flow:
   a. **Generate the link and open the page.** Run `wallet login --phase init`.
      It creates the login session, opens `loginUrl` in the browser, and returns
      `{ loginUrl, authSessionId, opened, nextSteps }`. Keep `authSessionId` for
      the later poll.
   b. **Show the link + reminder in the Agent conversation.** After `init`
      returns, send this block as a visible Agent commentary message and
      complete that message before invoking `poll` (translate to the user's
      language; keep the structure,
      substitute `authSessionId` and `loginUrl`):
      > Your login link is ready — I'll open it in your browser.
      > • Session ID (session_id): `<authSessionId>`
      > • Login link (you can also click it manually): `<loginUrl>`
      >
      > Fetching the login result will block your other operations for up to 5 minutes.
   c. **Auto-poll after the visible message is sent.** Run
      `wallet login --phase poll --session-id <authSessionId>` using the id from
      step a immediately after sending the login block. Follow
      `nextSteps.requiredOrder`: `displayLoginUrl`, then `completeLogin`. On a
      timeout or empty result, ask the user to finish login on the open page and
      choose either a new poll with the same id or a new `--phase init` session.
2. **After login — post-login display (fixed order).** After a successful `poll`, run `wallet status`, then render these blocks in **this exact order**, **omitting any block whose data is absent** — never fabricate a value and never issue an extra CLI call to fill a gap:
   1. **Wallet info** — the Account Info template (below), from the `poll` response.
   2. **Product intro** — On OKX.AI, you can search for a service to help you, swap tokens, or explore DApps.
   3. **Policy** — output the Policy Settings template ([portal-actions.md](wallet-portal-actions.md)) **only when `data.isNew == true`**; when `false`, skip it. `isNew == true` means a **first-ever** user — an existing user adding another account keeps `isNew == false` (the value comes from the wallet backend, not from client logic).
   4. **Subscription** — when `data.postLoginSubscriptions.activeSubscriptionCount` is a positive integer, render:

   > You have {activeSubscriptionCount} active subscription tasks.
   > Reply `1` to view your subscription list.

   If the user replies `1` or otherwise asks to view or refresh the subscription
   list, switch to the [`okx-ai` skill](../../okx-ai/SKILL.md) and follow
   [subscription.md](../../okx-ai/references/a2a/user/subscription.md).

   **NEVER**: run a separate `subscription-list` or `device-list` command after a successful poll — the poll response already carries what the display needs, and an extra call adds a model round on the normal path. **NEVER**: include Wallet Export in this post-login display — export is a user-triggered action only (§Policy & Wallet Export), never advertised in the login snapshot.

   Behind the scenes the CLI always sends the best-effort device-registration heartbeat before returning. When it resolves a non-empty User `agenticId`, it independently queries subscriptions and includes `activeSubscriptionCount` only when the count is positive. Login does not query or update device routing.

Login creates the first account automatically — never call `wallet add` for it. Use `wallet add` only when already logged in and the user explicitly wants another account (then output the Policy Settings template, see [portal-actions.md](wallet-portal-actions.md)).

### Template: Account Info (login success)

Render verbatim from the `wallet login --phase poll` response `data`:

> **Account Info**
> - Login method: {method}{ ({email}) }
> - Current account: OKX Wallet - {accountName} ({accountCount} accounts total)
> - Total assets: ${totalValueUsd}
>
> **Addresses**
> - EVM: {evmAddress}
> - Solana: {solAddress}
> - Bitcoin: {btcAddress}
> - Sui: {suiAddress}

Field rules:
- `{method}` ← `loginType`: `email`→"Email", `google`→"Google", `apple`→"Apple", `ak`→"API Key".
- Append ` ({email})` only if `email` is non-empty; otherwise omit the parentheses.
- Omit the "Total assets" line if `totalValueUsd` is empty; omit an address line if its corresponding value (`evmAddress`, `solAddress`, `btcAddress`, or `suiAddress`) is empty.
- **NEVER**: issue a separate `wallet balance` / portfolio call to populate "Total assets" — render it only from the `poll` response's `totalValueUsd` and omit the line when that field is absent; a second call would add a model round on the normal login path.

### Collect Parameters

**`--chain`** accepts numeric IDs (`1`, `501`, `196`) and names (`ethereum`, `solana`, `xlayer`). If <100% confident, run `wallet chains`. On `"unsupported chain: ..."`, ask the user to confirm.

**Amounts** — `wallet send`: pass `--readable-amount <human_amount>` (CLI converts; use `--amt` only for raw minimal units). `wallet contract-call`: `--amt` is the native value for payable functions in minimal units (default `"0"`; EVM 18, SOL 9 decimals). Never compute minimal units manually.

**Native BTC fee rate** — After the initial transfer preview, ask the user to confirm the current fee rate. If they provide a new sat/vB value, rerun the initial command with `--fee-rate <value>`. Show the fresh preview, remind them that the custom fee rate applies only to that transaction, and wait for confirmation.

**Bitcoin UTXOs and BRC-20** — See [utxo-cli-reference.md](utxo-cli-reference.md) for BTC UTXO management and [brc20-cli-reference.md](brc20-cli-reference.md) for BRC-20 management. To query a BRC-20 ticker balance, run `onchainos wallet balance --chain bitcoin --token-address <btc-brc20-ticker>` and use that reference's reply template.

### Send vs Contract Call (funds-loss risk — determine intent first)

| Operation | Command family |
|---|---|
| Token transfer | `wallet send --chain <chain>` |
| Contract call | `wallet contract-call --chain <chain>` |

For a SUI contract call, provide the unsigned PTB from the maintained integration or SDK with `--sui-tx-bytes`.

### Insufficient-Balance Top-up Recovery (Wallet Send)

When `wallet send` returns `phase=funding_required`, `decision=blocked`,
and `reason=insufficient_balance`, enter the shared Funding Reference
immediately. Full field list:
[wallet-cli-reference.md](wallet-cli-reference.md) → Common insufficient-balance result.

The CLI produces this common Funding result for a real backend `code=10004`, or when
`executeResult=false` is followed by a fresh chain-and-token balance query that
proves `requested > balance`. It must not classify from `executeErrorMsg` text
alone. If that balance query cannot confirm a shortfall, keep the ordinary
simulation-failure path and show `executeErrorMsg`. When `balance` is `null`,
show "Balance is currently unavailable".

**Recovery flow**:

1. Follow [funding.md](funding.md) immediately. Its shared Funding-required
   template displays the balance, shortfall, address, and QR in the same
   response. Do not duplicate its address, QR, network, or fallback rules here.
2. After shared Funding verifies a sufficient balance, it asks whether to
   continue the interrupted operation using the current conversation context.
   If the user continues this transfer, treat that reply as a new Wallet Send
   intent and rebuild the request from current user/context input.
3. Run `wallet send` without `--force`. The new preview replaces every prior
   result and requires the ordinary explicit confirmation. If the original
   transfer details are no longer clear, ask for them instead of reconstructing
   or guessing them.

A "funded" event authorizes only the read-only refresh. A later explicit request
to continue authorizes only a new preview request.
It never authorizes the transfer, and no previous confirmation survives the new
CLI result.

### Policy & Wallet Export

Policy config is completed by the user on the Web portal; wallet export is done by the user in the OKX Wallet extension or app. The Agent only detects the trigger, explains the consequences, gives the Policy jump link, and renders the verbatim export copy — it never performs the export itself. On any trigger below, load [portal-actions.md](wallet-portal-actions.md) and follow its Trigger flows exactly:
- New user login (`isNew: true`) — also handled in Authentication step 2 (output the Policy Settings template)
- After a successful `wallet add`
- User asks about Policy (spending / daily limit, whitelist)
- User asks about wallet export (export mnemonic, migrate, import to hardware wallet)

Never display mnemonic phrases, seed phrases, or private keys in the conversation.

### Third-Party Plugin Pre-flight (Solana)

Before dispatching a third-party Solana DeFi plugin (kamino-plugin, raydium-plugin, …) that internally calls `wallet contract-call --force`, run the Gas Station pre-flight in [plugin-preflight.md](wallet-plugin-preflight.md).

## Security

### Approvals (via contract-call)

Never execute unlimited approvals. Do not set the approve amount to `type(uint256).max` / `2^256-1` / any "infinite" value, and do not call `setApprovalForAll(operator, true)`. If the user explicitly requests unlimited approval: warn it is irreversible and lets the spender drain all tokens, require a second explicit confirmation, and even then cap the amount to what is needed (e.g. swap amount + 10%). If the user still insists, refuse and suggest they execute manually via a block explorer.

### MEV Protection

`--mev-protection` is a `contract-call` flag only (`wallet send` does not support it). Load [mev-protection.md](wallet-mev-protection.md) when the user requests MEV protection, or before a high-value / DEX-swap `contract-call` — it holds the supported-chain table and the Solana `--jito-unsigned-tx` requirement.

### TEE Signing

The private key is generated and stored inside a server-side secure enclave and never leaves the TEE — the Agent cannot export or locally sign with it.

## Render Rules

### Wallet-specific Notes

- **X Layer Testnet faucet**: when the user asks for testnet tokens, or `wallet balance --chain xlayer_test` shows OKB = 0, point them to https://web3.okx.com/xlayer/faucet.
- **XKO address**: if a user-supplied address starts with `XKO` / `xko`, display verbatim:
  > "XKO address format is not supported yet. Please find the 0x address by switching to your commonly used address, then you can continue."

## CLI Reference

- [wallet-cli-reference.md](wallet-cli-reference.md)

## Troubleshooting

> Load on error: [wallet-troubleshooting.md](wallet-troubleshooting.md)
