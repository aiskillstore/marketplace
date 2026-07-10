---
name: nla-create
description: Create a Natural Language Agreement escrow on-chain. Use when the user wants to lock ERC20 tokens in an escrow with a natural language demand that an AI oracle will arbitrate. Handles demand crafting, parameter gathering, and CLI execution.
metadata:
  author: arkhai
  version: "1.0"
compatibility: Requires nla CLI installed (npm install -g nla). Requires a funded Ethereum wallet and access to an EVM chain.
allowed-tools: Bash(nla:*) Read
---

# Create NLA Escrow

Help the user create a blockchain escrow backed by a natural language demand using the `nla` CLI.

## Overview

An NLA escrow locks ERC20 tokens on-chain. Anyone can attempt to fulfill the escrow's natural language demand. An AI oracle evaluates fulfillments and releases the tokens if the demand is satisfied.

## Step-by-step instructions

### 1. Gather requirements

Collect the following from the user conversationally:

**Required:**
- **Demand**: The natural language condition that must be fulfilled. Help the user craft something clear and unambiguous.
- **Amount**: Number of tokens to escrow (in the token's smallest unit - no automatic decimal conversion).
- **Token address**: ERC20 token contract address (`0x...`).
- **Oracle address**: Address of the oracle that will arbitrate.

**Optional:**
- **Arbitration provider**: `OpenAI` (default), `Anthropic`, or `OpenRouter`.
- **Arbitration model**: e.g. `gpt-4o-mini` (default), `claude-3-5-sonnet-20241022`, `openai/gpt-4o`.
- **Arbitration prompt**: Custom prompt template with `{{demand}}` and `{{obligation}}` placeholders.

### 2. Check prerequisites

```bash
# Verify CLI is available
which nla

# Check current network
nla network

# Check wallet is configured
nla wallet:show
```

If no wallet is configured, the user must either:
- Run `nla wallet:set --private-key <key>`
- Pass `--private-key <key>` to the command
- Set the `PRIVATE_KEY` environment variable

### 3. Help craft the demand

Guide the user to write an effective demand:
- Be specific and evaluable by an LLM
- Consider: what counts as valid fulfillment? Is the condition verifiable?
- For claims requiring real-world knowledge, suggest models with search (Perplexity search is available if the oracle has it configured)
- The demand, provider, model, and prompt are all encoded on-chain and publicly visible - never include secrets

### 4. Execute escrow creation

```bash
nla escrow:create \
  --demand "<demand text>" \
  --amount <amount> \
  --token <token_address> \
  --oracle <oracle_address> \
  [--arbitration-provider "<provider>"] \
  [--arbitration-model "<model>"] \
  [--arbitration-prompt "<prompt>"]
```

### 5. Record output

The command outputs an escrow UID (`0x...`). This UID is needed for fulfillment and collection. Present it clearly to the user and explain next steps.

## Key details

- Available networks: `anvil` (local), `sepolia`, `base-sepolia`, `mainnet`. Switch with `nla switch <network>`.
- For local dev, `nla dev` starts Anvil, deploys contracts, creates mock tokens, and starts the oracle.
- Public demo oracle on Sepolia: `0xc5c132B69f57dAAAb75d9ebA86cab504b272Ccbc`.
- Default arbitration prompt:
  ```
  Evaluate the fulfillment against the demand and decide whether the demand was validly fulfilled

  Demand: {{demand}}

  Fulfillment: {{obligation}}
  ```

## Example

```bash
nla escrow:create \
  --demand "Provide a valid proof that P != NP" \
  --amount 1000000 \
  --token 0xa513e6e4b8f2a923d98304ec87f64353c4d5c853 \
  --oracle 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 \
  --arbitration-provider "Anthropic" \
  --arbitration-model "claude-3-5-sonnet-20241022"
```
