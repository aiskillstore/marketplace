# Funding and Receive

## Module Description

Business Reference for active wallet funding and for the shared insufficient-
balance flow entered automatically from another business.

- The user asks to deposit, top up, receive a token, show a receive address, or
  show its QR code.
- The latest structured result has `phase=funding_required`,
  `decision=blocked`, and `reason=insufficient_balance`.

An upstream business decides that the balance is insufficient and calls the
common CLI builder. Enter this Reference immediately and render the shared
Funding-required template with the returned balance, address, and QR in the
same response. Do not ask the user to choose Funding first.

When both conditions could match, the latest structured insufficient-balance
result has priority over a new active-funding intent. Enter Insufficient-balance
flow below; do not discard its `fundingNeed` by running a new generic
`wallet receive` query.

## Action Routing

Begin a route only from an action ID present in the latest Funding result's
`nextAction` array. A route may show its own read-only choice list before it
finishes.

An upstream business may attach its own bound continuation action to a shared
insufficient-balance result. Preserve it, but do not route it through this
table; the caller owns its execution after Funding presentation.

| Action ID | Reference |
| --- | --- |
| `specify_funding_chain` | If the user supplied a chain, run `wallet receive --chain <chain>`. Otherwise run `wallet chains` and show only the returned network choices. |
| `search_receive_token` | Use the user's token query with `wallet receive --token <query>`. |
| `select_receive_token` | Use the selected action's `params.chainIndex` with `wallet receive --chain <chainIndex>`. |
| `more_receive_tokens` | Use only the action's `params.query` and `params.cursor` with `wallet receive --token <query> --cursor <cursor>`. |

Validate the action and its required params before routing. Preserve returned
order; `recommend=true` affects presentation only. For a network list opened by
`specify_funding_chain`, a numeric reply selects only the corresponding item in
that latest list. For token candidates, it selects only the corresponding
`select_receive_token` action. Unknown, stale, or incomplete actions stop as
unsupported; never infer a route from labels or prose.

A structured `phase=funding_required`, `decision=blocked`,
`reason=insufficient_balance` result enters the Insufficient-balance flow
directly. It is not an action and authorizes no interrupted operation or write.

## Flow

### Active funding flow

1. Determine whether the current user input supplies a chain, a token, or
   neither.
2. Invoke exactly one read-only CLI entry:

   | Confirmed input | CLI call |
   | --- | --- |
   | Neither chain nor token | `onchainos wallet receive` |
   | Chain | `onchainos wallet receive --chain <chain>` |
   | Token without chain | `onchainos wallet receive --token <query>` |

3. Read `decision`, then `reason`, `nextAction`, and `payload` from the result.
4. Render the current intent from Output templates below.
5. Route a user-selected action only through Action routing above.

When both chain and token are explicit, the chain determines the receive
address. Use the chain call and do not add token metadata that the CLI result
did not return.

### Collect Parameters

#### Token selection constraints

- Preserve the CLI order and the full `chainIndex + tokenContractAddress`
  identity from the latest result.
- A numeric reply can select only the corresponding `select_receive_token`
  action from that result.
- A "More" reply can use only the current `more_receive_tokens.params.query`
  and `params.cursor` through Action routing above.
- If the result is stale, missing, or incomplete, restart Token Search. Never
  reconstruct a candidate from symbol, name, an abbreviated address, or prose.

### Insufficient-balance entry

Match the common result by `phase=funding_required`, `decision=blocked`, and
`reason=insufficient_balance`. The payload contains only shared Funding fields;
it does not accept or preserve business-specific payload fields. `nextAction`
is normally empty, but may contain a caller-owned bound continuation that this
Reference preserves without executing.

Validate these common payload fields:

- `fundingTarget`: account, network, full receive address, same-network and gas
  facts.
- `qr`: QR representation for that exact address.
- `fundingNeed`: asset, token address, required amount, current balance, and
  CLI-calculated shortfall.

Render Fund an insufficient balance from Output templates below, including its
balance, shortfall, funding target, address, and QR, then wait for the user to
report that funding is complete. Do not query another address, reconstruct a
QR, or calculate a missing amount in the Skill.

When the user later says they funded the account:

If the latest Funding result contains a caller-owned continuation, return to
that business Reference immediately. Its return rule overrides the generic
verification flow below.

1. Use only `payload.fundingTarget.chainIndex` and
   `payload.fundingNeed.{tokenAddress,required,asset}` from the latest structured
   result. If any required fact is unavailable, ask for it or restart the
   funding query; never guess.
2. Run:
   `onchainos wallet funding-check --chain <chainIndex> [--token-address <tokenAddress>] --required <required> --asset <asset>`.
   Omit `--token-address` only when the structured value is empty for a native
   asset.
3. Render Verify funding from Output templates below.
4. If sufficient, infer the interrupted operation only from the current
   conversation context. When it is clear, ask whether the user wants to
   continue it. When it is not clear, use the generic continuation prompt from
   the template. This is a plain-language handoff, not a CLI action.
5. A request to continue is a new entry into the owning business Reference. It
   must re-query/re-preview current facts and obtain every confirmation required
   by that business. Never reuse an old preview, quote, payment ID, write
   command, or confirmation.

If the balance remains insufficient, retain the new verification result and
wait for another funding-complete event. A funding event authorizes no transfer,
swap, payment, signature, task creation, or broadcast.

If the balance query or refreshed funding target is unavailable, report that
verification is blocked and wait. On a later explicit request to check again,
rerun the same read-only `funding-check` from the latest Funding payload; do not
infer success, reuse an old address, or resume the interrupted business.

## Output Rules

### Address and QR output

1. Read the complete `receiveAddress` from the latest CLI result.
2. Render the localized receive-address label and the original address on one
   plain-text line. In a Chinese conversation, render
   `收款地址：{receiveAddress}` or
   `收款地址：{fundingTarget.receiveAddress}`.
3. Render the QR for that address immediately after the address.
4. Render the network notices from `sameNetworkRequired` and `gasFree`.

`gasFree: true` means on-chain gas is free after the funds arrive; it does not
cover exchange withdrawal fees — the exchange may charge one.

### Output templates

#### Choose a network

```text
Choose a network:
{sequence}. {showName}
```

#### Choose a token

```text
Choose a token for "{query}":
{sequence}. {tokenName} ({tokenSymbol}) · {networkName} · {tokenContractAddress or Native}

Reply with a sequence number.{optional "More results"}
```

No result:

```text
No token was found for "{query}". Try another name, symbol, or contract address.
```

#### Show receive information

Repeat the address block when multiple networks are returned.

```text
Network: {chainName}
Token: {tokenName} ({tokenSymbol})
Contract: {tokenContractAddress}
Receive address: {receiveAddress}
{qr}
{network notices}
```

#### Fund an insufficient balance

```text
The {asset} balance is insufficient.
Current: {balance or Unavailable} {asset}
Required: {required} {asset}
Shortfall: {shortfall} {asset}

Network: {fundingTarget.chainName}
Receive address: {fundingTarget.receiveAddress}
{qr}
{network notices}

Tell me when funding is complete. I will verify the balance before continuing.
```

#### Verify funding

```text
Sufficient: Latest balance: {currentBalance} {asset.symbol}. Continue {interrupted operation}?

Insufficient: Latest balance: {currentBalance} {asset.symbol}. Still required: {shortfall} {asset.symbol}.
Receive address: {fundingTarget.receiveAddress}
{qr}

Unavailable: The latest balance could not be verified. Funding completion is not confirmed.
```
