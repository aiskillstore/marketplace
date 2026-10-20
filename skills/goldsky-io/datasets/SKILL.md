---
name: datasets
description: "Use this skill when the user needs to look up or verify Goldsky blockchain dataset names, chain prefixes, dataset types, or versions. Triggers on questions like 'what\\'s the dataset name for X?', 'what prefix does Goldsky use for chain Y?', 'what version should I use for Z?', or 'what datasets are available for Solana/Stellar/Arbitrum/etc?'. Also use for chain-specific dataset questions (e.g., polygon vs matic prefix, stellarnet balance datasets, solana token transfer dataset names), and to answer 'is there a dataset for X?' where X is a domain rather than a chain — decoded logs, token transfers and balances, mint/burn events for circulating supply, DEX or prediction-market activity (Polymarket), or the raw blocks, transactions and traces behind wallet history and reconciliation. Do NOT trigger for questions about CLI commands, pipeline setup, or general Goldsky architecture unless the core question is about finding the right dataset name or chain prefix. Wallet Feeds API queries are /feeds."
---

# Goldsky Dataset Reference

Reference tables for blockchain datasets available in Turbo pipelines.

For quick dataset questions (e.g., "what dataset for Solana transfers?"), answer directly: identify the chain prefix (see Popular Chain Prefixes below), identify the dataset type (see Common Datasets), and return a YAML snippet like:

```yaml
sources:
  my_source:
    type: dataset
    dataset_name: <chain>.<dataset>
    version: 1.0.0
    start_at: earliest
```

> **Tip:** Verify a dataset exists with `goldsky dataset get <chain>.<dataset> --outputFormat json` — returns the exact slug, version, schema, and `isTurboOnly` (`false` = usable by Turbo **and** Mirror; `true` = Turbo-only). To browse or search: `goldsky dataset list --output json` (optionally `--group <chain>`; the list is a slim index and omits `isTurboOnly` — use `dataset get` for that). `goldsky turbo validate file.yaml` validates a whole **Turbo** pipeline config — it is *not* a dataset-existence check (Turbo-specific, needs the `turbo` binary).
>
> ⚠️ **Plain `goldsky dataset list` with no flags is an interactive picker that only works in a real terminal** — in an agent/CI/piped context it produces **no output** at all. Always pass `--output json` (or `--group`). On an older CLI without those flags, fall back to the public read-only endpoint: `curl -s https://api.goldsky.com/api/public/datasets/v1`.

---

## Dataset Reference Files

> **Chain prefix and chain ID information is in the `data/` folder.**

| File                  | Contents                                           |
| --------------------- | -------------------------------------------------- |
| `chain-prefixes.json` | All chain prefixes, chain IDs, and common mistakes |

**Data location:** `data/` (relative to this skill's directory)

> **Dataset versions are not pinned in this skill.** Version numbers drift as datasets are revised, so confirm the exact version with `goldsky dataset get <name> --outputFormat json` rather than trusting a static list. The dataset-type and schema tables below are stable references; treat any version number in them as a starting point to validate, not ground truth.

---

## Quick Reference

| Action             | Command                               | Notes                        |
| ------------------ | ------------------------------------- | ---------------------------- |
| Verify a dataset     | `goldsky dataset get <name> --outputFormat json`     | **Preferred** — slug, version, schema, `isTurboOnly` |
| Search datasets      | `goldsky dataset list --output json \| grep -i name` | Non-interactive                                    |
| List all datasets    | `goldsky dataset list --output json`                 | Plain `dataset list` is TTY-only — always `--output json` |

---

## Common Datasets

| What You Need            | Dataset                    | Example                              |
| ------------------------ | -------------------------- | ------------------------------------ |
| Token transfers (ERC-20) | `<chain>.erc20_transfers`  | `base.erc20_transfers` (v1.2.0)      |
| NFT transfers (ERC-721)  | `<chain>.erc721_transfers` | `ethereum.erc721_transfers` (v1.0.0) |
| Transactions             | `<chain>.raw_transactions` | `ethereum.raw_transactions` (v1.0.0) |
| Event logs               | `<chain>.raw_logs`         | `base.raw_logs` (v1.0.0)             |
| Solana tokens            | `solana.token_transfers`   | v1.0.0                               |
| Bitcoin transactions     | `bitcoin.raw.transactions` | v1.0.0                               |
| Stellar transfers        | `stellar_mainnet.transfers`| v1.1.0                               |

> **Important:** Use `raw_transactions`, NOT `transactions`

---

## Popular Chain Prefixes

| Chain     | Prefix             | Note                              |
| --------- | ------------------ | --------------------------------- |
| Ethereum  | `ethereum`         |                                   |
| Base      | `base`             |                                   |
| Polygon   | `matic`            | **NOT** `polygon`                 |
| Arbitrum  | `arbitrum`         |                                   |
| Optimism  | `optimism`         |                                   |
| BSC       | `bsc`              |                                   |
| Avalanche | `avalanche`        |                                   |
| Solana    | `solana`           | Uses `start_block` not `start_at` |
| Bitcoin   | `bitcoin.raw`      | Uses `start_at` like EVM          |
| Stellar   | `stellar_mainnet`  | Uses `start_at` like EVM          |
| Sui       | `sui`              | Uses `start_at` like EVM          |
| NEAR      | `near`             | Uses `start_at` like EVM          |
| Starknet  | `starknet`         | Uses `start_at` like EVM          |
| Fogo      | `fogo`             | Uses `start_at` like EVM          |

**See `data/chain-prefixes.json` for complete list with chain IDs.**

---

## Common Dataset Types

### EVM Chains

| Dataset Type        | Description                 | Use Case                             |
| ------------------- | --------------------------- | ------------------------------------ |
| `blocks`            | Block headers with metadata | Block explorers, timing analysis     |
| `raw_transactions`  | Transaction data            | Wallet activity, gas analysis        |
| `raw_logs`          | Raw event logs              | Custom event filtering               |
| `raw_traces`        | Internal transaction traces | MEV analysis, contract interactions  |
| `erc20_transfers`   | Fungible token transfers    | Token tracking, DeFi analytics       |
| `erc721_transfers`  | NFT transfers               | NFT marketplaces, ownership tracking |
| `erc1155_transfers` | Multi-token transfers       | Gaming, multi-token standards        |

> **Important:** Use `raw_transactions`, NOT `transactions`. Use `raw_logs`, NOT `logs` (though `logs` works as an alias on some chains).
>
> **There is no consumable `decoded_logs` source dataset.** For decoded contract events, source from `<chain>.raw_logs` and decode in a SQL transform via `_gs_log_decode(_gs_fetch_abi(<explorer-url>, <source>), topics, data)`. See `/turbo-transforms` for the full pattern.

### Solana

| Dataset Type                     | Description                       | Use Case                     |
| -------------------------------- | --------------------------------- | ---------------------------- |
| `blocks`                         | Block data with leader info       | Chain analysis               |
| `transactions`                   | Transaction data with balances    | Wallet activity              |
| `transactions_with_instructions` | Transactions + nested instructions| Multi-instruction analysis   |
| `instructions`                   | Individual instructions           | Program-specific analysis    |
| `token_transfers`                | SPL token transfers               | Token tracking               |
| `native_balances`                | SOL balance changes               | Whale tracking               |
| `token_balances`                 | SPL token balance changes         | Portfolio tracking           |
| `rewards`                        | Validator rewards                 | Staking analysis             |

### Bitcoin

| Dataset Type           | Description              | Use Case                     |
| ---------------------- | ------------------------ | ---------------------------- |
| `bitcoin.raw.blocks`       | Block data (hash, difficulty, size) | Network analysis     |
| `bitcoin.raw.transactions` | Transactions (inputs, outputs, values) | Payment tracking |

### Stellar

All datasets use version `1.1.0`:

| Dataset Type                       | Description                       | Use Case                     |
| ---------------------------------- | --------------------------------- | ---------------------------- |
| `stellar_mainnet.transactions`     | All network transactions          | Account monitoring           |
| `stellar_mainnet.transfers`        | All transfer events               | Asset tracking               |
| `stellar_mainnet.events`           | All events (contract + operation) | Contract monitoring          |
| `stellar_mainnet.operations`       | Operations within transactions    | Action tracking              |
| `stellar_mainnet.ledger_entries`   | Ledger state changes              | State analysis               |
| `stellar_mainnet.ledgers`          | Ledger metadata                   | Network analysis             |
| `stellar_mainnet.balances`         | Account balance changes           | Balance tracking             |

### Sui

| Dataset Type            | Description                       | Use Case                     |
| ----------------------- | --------------------------------- | ---------------------------- |
| `sui.checkpoints`       | Checkpoint data                   | Chain analysis               |
| `sui.transactions`      | Transaction data                  | Activity monitoring          |
| `sui.events`            | Move contract events              | dApp event tracking          |
| `sui.packages`          | Deployed Move packages            | Package discovery            |
| `sui.epochs`            | Epoch data with validators        | Staking/validator analysis   |

### NEAR

| Dataset Type                 | Description                       | Use Case                     |
| ---------------------------- | --------------------------------- | ---------------------------- |
| `near.receipts`              | Execution receipts                | Contract interaction tracking|
| `near.transactions`          | Signed transactions               | Activity monitoring          |
| `near.execution_outcomes`    | Execution results                 | Success/failure analysis     |

### Starknet

| Dataset Type                 | Description                       | Use Case                     |
| ---------------------------- | --------------------------------- | ---------------------------- |
| `starknet.blocks`            | Block data                        | Chain analysis               |
| `starknet.transactions`      | Transaction data                  | Activity monitoring          |
| `starknet.events`            | Contract events                   | dApp event tracking          |
| `starknet.messages`          | L1↔L2 messages                    | Bridge monitoring            |

### Fogo

| Dataset Type                          | Description                     | Use Case                     |
| ------------------------------------- | ------------------------------- | ---------------------------- |
| `fogo.transactions_with_instructions` | Transactions with instructions  | Full activity tracking       |
| `fogo.rewards`                        | Validator rewards               | Staking analysis             |
| `fogo.blocks`                         | Block data                      | Chain analysis               |

---

## Dataset Schemas

> **Source:** [docs.goldsky.com](https://docs.goldsky.com/turbo-pipelines/sources/solana.md). Do not use field names not listed here — run `goldsky dataset get <chain>.<dataset> --outputFormat json` to inspect unknown schemas.

### Solana

#### `solana.transactions`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `index` | integer | tx position in block |
| `block_slot` | integer | slot number |
| `block_hash` | string | |
| `block_timestamp` | timestamp | |
| `signature` | string | transaction signature |
| `recent_block_hash` | string | |
| `fee` | integer | in lamports |
| `status` | integer | 1 = success |
| `err` | string \| null | error if failed |
| `accounts` | string[] | **all** involved accounts |
| `balance_changes` | object[] | `{account, before, after}` in lamports |
| `log_messages` | string[] | program execution logs |
| `compute_units_consumed` | integer | |

> **No `from_address` or `to_address` on Solana transactions** — use `accounts` array instead.

#### `solana.transactions_with_instructions`
All fields from `solana.transactions` plus:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `pre_token_balances` | object[] | token balances before tx |
| `post_token_balances` | object[] | token balances after tx |
| `instructions` | object[] | see below |

**Instruction object fields:** `id`, `index`, `parent_index`, `block_slot`, `block_timestamp`, `block_hash`, `tx_signature`, `tx_fee`, `tx_index`, `program_id`, `data` (base58), `accounts` (string[]), `instruction_type`

#### `solana.instructions`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `block_slot` | integer | |
| `block_hash` | string | |
| `block_timestamp` | timestamp | |
| `tx_signature` | string | transaction signature |
| `index` | integer | position in tx |
| `parent_index` | integer \| null | for inner instructions |
| `accounts` | string[] | instruction accounts |
| `data` | string | base58 encoded |
| `program` | string | program name/label |
| `program_id` | string | executing program address |
| `instruction_type` | string | decoded instruction type |
| `params` | object | decoded instruction params |
| `parsed` | object | parsed payload |

#### `solana.token_transfers`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `token_mint_address` | string | mint address |
| `from_token_account` | string | source token account |
| `to_token_account` | string | dest token account |
| `amount` | number | raw amount |
| `decimals` | integer | token decimals |
| `block_slot` | integer | |
| `block_timestamp` | timestamp | |
| `signature` | string | tx signature |

#### `solana.native_balances`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `block_slot` | integer | slot number |
| `block_hash` | string | |
| `block_timestamp` | timestamp | |
| `tx_index` | integer | transaction position in block |
| `signature` | string | transaction signature |
| `account` | string | account pubkey |
| `amount_before` | integer | lamports |
| `amount_after` | integer | lamports |
| `_gs_op` | string | Goldsky internal operation type |

#### `solana.blocks`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `slot` | integer | |
| `parent_slot` | integer | |
| `hash` | string | |
| `timestamp` | timestamp | |
| `height` | integer | |
| `previous_block_hash` | string | |
| `transaction_count` | integer | |
| `leader` | string | validator pubkey |
| `leader_reward` | integer | lamports |
| `skipped` | boolean | |

#### `solana.rewards`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `block_slot` | integer | |
| `block_hash` | string | |
| `block_timestamp` | timestamp | |
| `pub_key` | string | validator pubkey |
| `lamports` | integer | reward amount |
| `post_balance` | integer | balance after reward |
| `reward_type` | string | |
| `commission` | integer | |

#### `solana.token_balances`
> **Schema not fully documented** — do not guess field names. Inspect with `goldsky dataset get solana.token_balances --outputFormat json`.

---

### EVM Chains

#### `<chain>.raw_logs` / `<chain>.logs`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `block_number` | integer | |
| `block_hash` | string | |
| `transaction_hash` | string | |
| `transaction_index` | integer | |
| `log_index` | integer | |
| `address` | string | contract address (lowercase) |
| `data` | string | hex encoded event data |
| `topics` | string | comma-separated hex topic hashes |
| `block_timestamp` | integer | unix timestamp |

> `topics` is a comma-separated string, not an array. Topic 0 is the event signature hash.

#### `<chain>.raw_transactions`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `hash` | string | |
| `nonce` | integer | |
| `block_hash` | string | |
| `block_number` | integer | |
| `transaction_index` | integer | |
| `from_address` | string | |
| `to_address` | string | |
| `value` | decimal | ETH value in wei |
| `gas` | decimal | |
| `gas_price` | decimal | |
| `input` | string | hex calldata |
| `transaction_type` | integer | |
| `block_timestamp` | integer | unix timestamp |
| `receipt_gas_used` | decimal | |
| `receipt_contract_address` | string \| null | if contract creation |
| `receipt_status` | integer | 1 = success |
| `receipt_effective_gas_price` | decimal | |

> L2 chains also include: `receipt_l1_fee`, `receipt_l1_gas_used`, `receipt_l1_gas_price`, `receipt_l1_fee_scalar`

#### `<chain>.blocks`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `number` | integer | block number |
| `hash` | string | |
| `parent_hash` | string | |
| `miner` | string | |
| `gas_limit` | integer | |
| `gas_used` | integer | |
| `timestamp` | integer | unix timestamp |
| `transaction_count` | integer | |
| `base_fee_per_gas` | integer | |
| `difficulty` | double | |

#### `<chain>.erc20_transfers`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `sender` | string | from address |
| `recipient` | string | to address |
| `amount` | decimal | token amount |
| `address` | string | token contract address |
| `block_number` | integer | |
| `block_timestamp` | integer | unix timestamp |
| `block_hash` | string | |
| `transaction_hash` | string | |
| `transaction_index` | integer | |
| `log_index` | integer | |

#### `<chain>.erc721_transfers`
| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | |
| `from_address` | string | |
| `to_address` | string | |
| `token_id` | decimal | |
| `address` | string | NFT contract address |
| `block_number` | integer | |
| `block_timestamp` | integer | unix timestamp |
| `block_hash` | string | |
| `transaction_hash` | string | |
| `transaction_index` | integer | |
| `log_index` | integer | |

---

## Dataset Name Format

All datasets follow the pattern: `<chain_prefix>.<dataset_type>`

**Examples:**

- `ethereum.erc20_transfers` - ERC-20 transfers on Ethereum mainnet
- `base.logs` - All event logs on Base
- `matic.blocks` - Block data on Polygon
- `solana.token_transfers` - SPL token transfers on Solana

---

## Finding Dataset Versions

Datasets are versioned. To find available versions:

```bash
goldsky dataset get base.erc20_transfers --outputFormat json
```

**Common versions:**

- `1.0.0` - Initial version
- `1.2.0` - Enhanced schema (common for ERC-20 transfers)

When in doubt, use the latest version shown by `goldsky dataset get <name> --outputFormat json`.

---

## Common Discovery Patterns

### "I want to track USDC transfers on Base"

1. Dataset: `base.erc20_transfers`
2. Filter by contract address in your pipeline transform:

```yaml
transforms:
  usdc_only:
    type: sql
    primary_key: id
    sql: |
      SELECT * FROM source_name
      WHERE address = lower('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
```

### "I want all NFT activity on Ethereum"

Dataset: `ethereum.erc721_transfers`

### "I want to monitor a specific smart contract"

1. Source: `<chain>.raw_logs`, filtered to the contract address in the source filter
2. To decode events: add a SQL transform calling `_gs_log_decode(_gs_fetch_abi(<explorer-url>, <source>), topics, data) AS decoded`, then filter downstream by `WHERE decoded.event_signature = '<EventName>(<types>)'`. Never put topic0 hashes in the source filter.

### "I need multi-chain data"

Use multiple sources in your pipeline:

```yaml
sources:
  eth_transfers:
    type: dataset
    dataset_name: ethereum.erc20_transfers
    version: 1.0.0
    start_at: latest
  base_transfers:
    type: dataset
    dataset_name: base.erc20_transfers
    version: 1.2.0
    start_at: latest
```

---

## Troubleshooting

### Dataset not found

```
Error: Source 'my_source' references unknown dataset 'invalid.dataset'
```

**Fix:**

1. Check the chain prefix is correct (e.g., `matic` not `polygon`)
2. Check the dataset type exists (e.g., `erc20_transfers` not `erc20`)
3. Run `goldsky dataset list --output json` to see all available options

### Chain not listed

If you can't find a chain in the tables above:

```bash
goldsky dataset list --output json | grep -i "<chain_name>"
```

Some chains use non-obvious prefixes (e.g., Polygon uses `matic`).

### Version mismatch

```
Error: Version '2.0.0' not found for dataset 'base.erc20_transfers'
```

**Fix:** Check available versions:

```bash
goldsky dataset get base.erc20_transfers --outputFormat json
```

Use a version that exists in the output.

---

## Related

- **`/turbo-builder`** — Interactive wizard to build pipelines using these datasets
