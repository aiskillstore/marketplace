# Portal Actions — Policy Settings & Wallet Export

## Module Description

> Load when: new user login (`isNew: true`), after `wallet add`, the user asks about Policy / spending limits / whitelist, or the user asks to export wallet / mnemonic / migrate / import a hardware wallet.

Policy configuration must be completed by the user on the Web portal. The Agent only detects the scenario, explains the risk, gives the jump link, and outputs the verbatim template below. The Agent must **never** display any mnemonic phrase or private key content in the conversation.

## Output Rules

### Template: Policy Settings

> You can set per-transaction and daily limits for trades and transfers, as well as a transfer whitelist, to prevent excessive operations or transfers to unauthorized addresses. Go to Policy Setting → {policy_url}
>
> {policy_hint}

| `loginType` | `{policy_url}` | `{policy_hint}` |
|---|---|---|
| `email` | `https://web3.okx.com/portfolio/agentic-wallet-policy` | Log in to your Agentic Wallet, then hover over your profile in the top-right corner and select "Policy Setting" from the dropdown menu. |
| `ak` | `https://web3.okx.com/onchainos/dev-portal` | Log in with the EOA wallet that created the Agentic Wallet and open the OKX Web3 Dev platform, and click on the Agentic Wallet - Policy Setting in the upper right corner to set security rules. |

## Security

### Available Policy Rules

Policy **only** includes the following rules. Do NOT invent or mention any rules beyond this list (e.g., no "transaction count limit", no "gas limit", no "token blacklist"):

| Rule | Description | Field (from `wallet status`) |
|---|---|---|
| Per-transaction limit | Max USD amount per single transaction or transfer | `singleTxLimit` / `singleTxFlag` |
| Daily transfer limit | Max USD amount for transfers per day (resets at UTC 0:00) | `dailyTransferTxLimit` / `dailyTransferTxFlag` / `dailyTransferTxUsed` |
| Daily trade limit | Max USD amount for trades (swaps) per day (resets at UTC 0:00) | `dailyTradeTxLimit` / `dailyTradeTxFlag` / `dailyTradeTxUsed` |
| Transfer whitelist | Only allow transfers to pre-approved addresses | Configured on Web portal only |

## Flow

### Resolve policy template

For the **Policy Settings** template, select the `email` or `ak` row from the
current `loginType` in the login response or `wallet status`. If it is unknown
or unrecognized, run `onchainos wallet status` and use `email` as the fallback.

### Trigger flows

The following are **trigger conditions** — when any is met, the Agent **MUST** output the corresponding guidance. Do not skip or omit.

### New user login (`isNew: true`)

Handled in [Wallet Authentication step 2](wallet.md) — when `isNew: true`, output the **Policy Settings template** (above), regardless of `loginType`.

### New account via `wallet add`

After a successful `wallet add`, **MUST** output the **Policy Settings template** (above), prefixed with a short line such as "New account created.".

### User asks about Policy

e.g., "How do I set a spending limit?", "What's my daily limit?", "How to configure whitelist?"
- Run `onchainos wallet status` and check the `policy` field.
- If any flag is true, first display the current settings (limits, used amounts).
- Then output the **Policy Settings template** (above).

### User asks about wallet export

e.g., "How do I export my mnemonic?", "I want to migrate my wallet", "How do I import my wallet into a hardware wallet?"

For any account type, output the following copy verbatim as the complete response:

> Export your seed phrase in the OKX Wallet extension or app.
> Please note: After export, your wallet will be permanently unlinked from your social account, and the Agent will no longer be able to operate it.
> Before exporting, move your assets to a secure address and stop any active tasks. After exporting, back up your seed phrase securely and never share it with anyone.
