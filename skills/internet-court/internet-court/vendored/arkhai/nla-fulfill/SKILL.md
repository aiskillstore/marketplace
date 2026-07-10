---
name: nla-fulfill
description: Fulfill an existing NLA escrow and collect tokens. Use when the user wants to submit fulfillment text for an on-chain escrow, check arbitration results, and collect approved funds. Covers the full fulfill-arbitrate-collect lifecycle.
metadata:
  author: arkhai
  version: "1.0"
compatibility: Requires nla CLI installed (npm install -g nla). Requires a funded Ethereum wallet and access to an EVM chain.
allowed-tools: Bash(nla:*) Read
---

# Fulfill NLA Escrow

Help the user fulfill an on-chain escrow by submitting text that satisfies the escrow's demand, then collect the tokens if approved.

## Step-by-step instructions

### 1. Understand the escrow

Get the escrow UID from the user, then check what it demands:

```bash
nla escrow:status --escrow-uid <uid>
```

This shows:
- The demand text
- Arbitration model and provider
- Oracle address
- Any existing fulfillments and their arbitration status

### 2. Craft the fulfillment

Help the user write fulfillment text that satisfies the demand:
- Read the demand carefully
- The fulfillment text is what the AI arbitrator evaluates against the demand
- Be specific and directly address what the demand asks for
- The default arbitration prompt evaluates whether the "fulfillment" satisfies the "demand" and returns true/false

### 3. Submit the fulfillment

```bash
nla escrow:fulfill \
  --escrow-uid <escrow_uid> \
  --fulfillment "<fulfillment text>" \
  --oracle <oracle_address>
```

This runs a multi-step on-chain commit-reveal flow:
1. Computes a commitment hash
2. Submits the commitment with a bond
3. Waits for next block confirmation
4. Reveals the fulfillment obligation and returns the bond
5. Requests arbitration from the oracle

The command outputs a **fulfillment UID** - record this for collection.

### 4. Monitor arbitration

Check if the oracle has made a decision:

```bash
nla escrow:status --escrow-uid <escrow_uid>
```

The oracle typically responds within seconds if it's running. Look for "APPROVED" or "REJECTED" in the output.

### 5. Collect tokens (if approved)

Once the oracle approves:

```bash
nla escrow:collect \
  --escrow-uid <escrow_uid> \
  --fulfillment-uid <fulfillment_uid>
```

This transfers the escrowed tokens to the fulfiller.

## Key details

- The fulfillment text is permanently recorded on-chain
- The commit-reveal process requires gas for multiple transactions
- If rejected, the tokens stay in escrow - another fulfillment attempt can be made by anyone
- The oracle address must match what was specified when the escrow was created (visible in status output)
- Collection only succeeds after the oracle records an approval

## Prerequisites

- `nla` CLI installed and configured
- Private key set via `nla wallet:set`, `--private-key` flag, or `PRIVATE_KEY` env var
- ETH in the fulfiller's account for gas
- The oracle must be running (or use the public demo on Sepolia)

## Example full flow

```bash
# 1. Check what the escrow demands
nla escrow:status --escrow-uid 0xabc123...

# 2. Submit fulfillment
nla escrow:fulfill \
  --escrow-uid 0xabc123... \
  --fulfillment "The sky appears blue due to Rayleigh scattering" \
  --oracle 0x70997970C51812dc3A010C7d01b50e0d17dc79C8

# 3. Check arbitration result
nla escrow:status --escrow-uid 0xabc123...

# 4. Collect if approved
nla escrow:collect \
  --escrow-uid 0xabc123... \
  --fulfillment-uid 0xdef456...
```
