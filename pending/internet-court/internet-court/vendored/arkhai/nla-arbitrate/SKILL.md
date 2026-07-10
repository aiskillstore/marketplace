---
name: nla-arbitrate
description: Manually arbitrate NLA escrow fulfillments as an alternative to the automated oracle. Use when the user wants to review pending arbitration requests, evaluate demands against fulfillments, and submit on-chain decisions. Supports both interactive and LLM-auto modes.
metadata:
  author: arkhai
  version: "1.0"
compatibility: Requires nla CLI installed (npm install -g nla). Requires a funded Ethereum wallet whose address matches the oracle specified in escrows.
allowed-tools: Bash(nla:*) Read
---

# Manual NLA Arbitration

Manually arbitrate escrow fulfillments using the `nla escrow:arbitrate` CLI command, bypassing the automated oracle listener.

## When to use this

- The user wants to manually review and decide on escrow fulfillments
- The user is the oracle (their wallet address was specified as the oracle when escrows were created)
- The automated oracle is not running, or the user wants more control over decisions

## Step-by-step instructions

### 1. Verify oracle identity

The user's wallet must be the oracle address specified in the escrow:

```bash
nla wallet:show
```

### 2a. Arbitrate a specific escrow

To review fulfillments for a known escrow UID:

```bash
# Interactive mode - prompts for approve/reject
nla escrow:arbitrate --escrow-uid <uid>

# Auto mode - uses the LLM specified in the escrow's demand
nla escrow:arbitrate --escrow-uid <uid> --auto
```

### 2b. Scan for all pending requests

To find all unarbitrated fulfillments where the user is the oracle:

```bash
# Interactive mode
nla escrow:arbitrate --escrow-uid all

# Auto mode
nla escrow:arbitrate --escrow-uid all --auto
```

### 3. Review and decide

In **interactive mode**, the command displays each pending fulfillment with:
- Escrow UID and fulfillment UID
- The demand text
- The fulfillment text
- The arbitration provider/model specified

Then prompts for a decision: `approve`, `reject`, or `skip`.

In **auto mode** (`--auto`), the command uses the LLM provider/model specified in the escrow's demand to arbitrate automatically. Requires at least one LLM API key via environment variables or flags (`--openai-api-key`, `--anthropic-api-key`, `--openrouter-api-key`).

### 4. Verify

After arbitration, check the result:

```bash
nla escrow:status --escrow-uid <escrow_uid>
```

## Key details

- The user's wallet address MUST match the oracle address in the escrow - otherwise the on-chain contract rejects the decision
- Each arbitration decision is recorded as a permanent on-chain attestation
- In interactive mode, type `skip` or `s` to skip a fulfillment without deciding
- Auto mode reads LLM API keys from environment variables (OPENAI_API_KEY, etc.) or CLI flags
- If no pending requests are found, the command explains possible reasons (no fulfillments yet, already arbitrated, or wrong oracle address)

## Prerequisites

- `nla` CLI installed and configured
- Private key set via `nla wallet:set`, `--private-key` flag, or `PRIVATE_KEY` env var
- ETH in the oracle's account for gas (submitting decisions costs gas)
- For auto mode: at least one LLM provider API key

## Examples

```bash
# Scan for all pending requests, decide interactively
nla escrow:arbitrate --escrow-uid all

# Auto-arbitrate a specific escrow using LLM
nla escrow:arbitrate --escrow-uid 0xabc123... --auto

# Auto-arbitrate all pending, with explicit API key
nla escrow:arbitrate --escrow-uid all --auto --openai-api-key sk-...
```
