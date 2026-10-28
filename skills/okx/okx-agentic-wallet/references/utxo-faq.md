# UTXO FAQ

When the user asks any semantic equivalent of one of the questions below, follow the matching entry and translate its reply template to the user's language without extra explanation.

## What is available balance?

Triggers include `available balance`, `available BTC`, `spendable balance`, and `spendable BTC` when the user is asking for the definition rather than their current amount.

```text
Available balance is the amount currently available for BTC transfers and network fees. It excludes locked and dust UTXOs.
```

## What is a locked UTXO?

Triggers include `locked UTXO`, `protected UTXO`, and questions asking why a UTXO is locked.

```text
A locked UTXO is excluded from ordinary BTC transactions to protect the inscription assets it carries. You can explicitly unlock that UTXO.
```

## What are the risks of unlocking a UTXO?

Triggers include `unlock UTXO risk`, `is unlocking safe`, and questions asking what happens after a UTXO is unlocked.

```text
After unlocking, the UTXO is treated as ordinary BTC. If it is spent, the inscription assets it carries will be permanently lost.
```

## What is a dust UTXO?

Triggers include `dust`, `dust UTXO`, `small UTXO`, and questions asking why a small BTC UTXO is unavailable.

```text
A dust UTXO contains a very small amount of BTC. Spending it increases transaction data size and network fees, so it is excluded from the available balance.
```

## What is unavailable balance?

Triggers include `unavailable balance`, `unavailable BTC`, `locked balance`, `what is the remaining BTC?`, `why is it unavailable?`, and questions asking what unavailable balance means or how much is currently unavailable. Run `wallet utxo unavailable --chain bitcoin`; do not use a stored balance or derive this amount from total BTC holdings.

First reply:

```text
Unavailable balance is BTC that currently cannot be used for BTC transfers or network fees, including locked and dust UTXOs.
```

Then use the current `unavailable.unavailableBreakdown` to append one matching reply:

- If `totalUnavailableCount` is `0`: `You currently have no unavailable BTC balance.`
- If `assetLocked` contains UTXOs: `You currently have {unavailableBalance} BTC unavailable. The following UTXOs are locked:` Then list each returned locked UTXO as `- {txHash}:{voutIndex}: {amount} BTC`. If `feeUneconomic` also contains UTXOs, append: `The remaining {dustBalance} BTC is dust UTXOs. Spending them increases network fees.`
- If `assetLocked` is empty and `feeUneconomic` is the only non-empty category: `You currently have {unavailableBalance} BTC unavailable, all of which is dust UTXOs. Spending them increases network fees.`
- If any other category is non-empty: show its returned category, UTXOs, and amounts. Do not describe it as locked or dust.

Use the returned `totalUnavailableSumSats` for `{unavailableBalance}` and returned UTXO amounts for `{amount}` / `{dustBalance}`. If a required amount is absent, omit that aggregate sentence rather than calculating or inferring it.
