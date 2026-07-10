# Shared: Strict item.json Construction
<!-- Sources: curate-v1/curate-light-skill.md §3, curate-v1/pgtcr-stake-curate-skill.md §5C, curate-v1-scout/scout-skills.md §8 -->

Curate item submissions are high risk. Do not produce, upload, or submit an item.json until the active
MetaEvidence has been fetched and validated. Fetch MetaEvidence first: `shared-metaevidence.md`.

---

## Required output shape

Every item.json submitted to any Curate registry must contain exactly these top-level parts:

```json
{
  "columns": [
    {
      "label": "Exact Label",
      "description": "Exact description from MetaEvidence.",
      "type": "text",
      "isIdentifier": true
    }
  ],
  "values": {
    "Exact Label": "user-provided value"
  }
}
```

Rules:

- `columns` must be a verbatim deep copy of `MetaEvidence.metadata.columns`.
- `values` is the only dynamic part.
- `Object.keys(values)` must exactly equal `columns.map(c => c.label)` in the same order.
- The order that matters is `MetaEvidence.metadata.columns`, `item.json.columns`, and `item.json.values`
  keys. Do not rely on unrelated top-level JSON key order.
- No missing keys, extra keys, renamed labels, reordered labels, or placeholder values.
- Do not submit only a `values` object.
- Do not reconstruct schema from UI text, screenshots, policy text, examples, or memory.

If MetaEvidence was not fetched in the current task, do not output a final item.json. Ask for the registry
URL or `(chainId, registryAddress)` and fetch MetaEvidence first.

---

## Output protocol

When producing an item.json for the user:

1. Print `Fetched columns (verbatim):`.
2. Display the exact `MetaEvidence.metadata.columns` array.
3. Print the final item.json with those exact columns and only `values` filled dynamically.

This makes schema drift auditable. Do not paraphrase labels, descriptions, types, or `isIdentifier`.

---

## Values construction

For each column in order:

- Key = `column.label`, exact string match.
- Value = user-provided value encoded for `column.type`.
- Empty values are forbidden unless the registry policy explicitly allows omission.

If the user has not provided enough information for every required value, create only a draft and mark it
not submission-ready. Never upload or submit a draft.

---

## GTCR field-value types

Use the live MetaEvidence type exactly when copying columns. For new schemas, use GTCR-compatible type
strings only.

Current scope: this skill covers Light Curate / GTCR and Stake Curate / PGTCR. Do not author Curate V2-only
type spellings such as `longText`, `richAddress`, or `chain` for GTCR/PGTCR schemas unless the target
interface or live MetaEvidence proves that exact spelling is expected. For item submissions, always copy
the live MetaEvidence type verbatim even if it differs from the authoring allowlist below.

| Type | Value format |
|------|--------------|
| `text` | Plain string |
| `long text` | Plain string, multi-line allowed |
| `link` | URL string |
| `address` | `0x`-prefixed EVM address |
| `rich address` | CAIP-like value such as `eip155:<chainId>:0xAddress` |
| `image` | `/ipfs/<CID>` path, not a gateway URL |
| `file` | `/ipfs/<CID>` path; file type must satisfy `allowedFileTypes` |
| `number` | Match existing submissions for the same MetaEvidence; strings are common |
| `boolean` | Match existing submissions; strings `"true"` / `"false"` are common |
| `GTCR address` | GTCR list address, only for list-of-lists style schemas |

### Column object validation

Every column object must be treated as part of the schema contract:

- `label` must be unique and non-empty.
- `label` is the exact key used in `item.json.values`.
- `description` must be copied verbatim from MetaEvidence.
- `type` must be copied verbatim from MetaEvidence for item submissions.
- `isIdentifier` must not be changed.

When authoring new GTCR MetaEvidence:

- At least one identifier column is required for normal item lists.
- At most five identifier columns are allowed in legacy GTCR factory flows.
- `image`, `file`, and `long text` fields must not be identifiers.
- Choose stable searchable identifiers; do not mark unstable display fields as identifiers.
- `file` columns require `allowedFileTypes`, using space-separated extensions without dots, for example
  `pdf`, `json`, or `pdf json`.

### Rich address values

Ask the user which chain a `rich address` value targets; never infer it from earlier
context. A bare address under the wrong `referenceId` resolves to a different account on a
different chain and fails registry compliance.

For `rich address`, use the format:

```text
<namespaceId>:<referenceId>:<address>
```

For EVM addresses:

```text
eip155:<chainId>:0x1234567890123456789012345678901234567890
```

Known GTCR rich-address namespaces include:

| Namespace | Meaning |
|-----------|---------|
| `eip155` | EVM chains |
| `bip122` | Bitcoin-like chains |
| `solana` | Solana |
| `tvm` | TON |
| `stacks` | Stacks |

Confirmed EIP-155 reference IDs in GTCR include:

| Chain | Reference ID |
|-------|--------------|
| Ethereum Mainnet | `1` |
| Sepolia | `11155111` |
| BNB Smart Chain | `56` |
| Gnosis | `100` |
| Polygon | `137` |
| Base | `8453` |
| Arbitrum One | `42161` |
| Moonbeam | `1284` |
| Linea | `59144` |
| Optimism | `10` |
| MegaETH | `4326` |
| PulseChain | `369` |
| Fantom | `250` |
| Moonriver | `1285` |
| Avalanche | `43114` |
| Cronos | `25` |
| BitTorrent | `199` |
| Polygon zkEVM | `1101` |
| WEMIX | `1111` |
| Scroll | `534352` |
| Celo | `42220` |
| zkSync | `324` |
| Sonic | `146` |
| Blast | `81457` |
| Plasma | `9745` |
| Hyperliquid | `999` |
| Katana | `747474` |
| Unichain | `130` |
| Berachain | `80094` |
| World Chain | `480` |

Forbidden aliases in authored MetaEvidence or item schema:

| Bad alias | Use instead |
|-----------|-------------|
| `url` | `link` |
| `uri` | `link` or `file`, depending on meaning |
| `string` | `text` |
| `markdown` | `long text` |
| `bool` | `boolean` |
| `integer` | `number` |
| `int` | `number` |
| `float` | `number` |
| `decimal` | `number` |

Using an unsupported type can break Curate interfaces with errors like `Unhandled input type url`.

---

## Schema confirmation via NewItem sampling

Perform this check once per MetaEvidence version before the first submission to a registry:

1. Find the block of the latest applicable MetaEvidence update (`B_meta`).
2. Find a `NewItem(bytes32 _itemID, string _data, bool _addedDirectly)` event after `B_meta`.
3. Fetch `_data` from IPFS.
4. Parse the prior item.json.
5. Confirm `item.columns` matches `MetaEvidence.metadata.columns` by labels, order, types, and flags.
6. Observe value encoding for `number`, `boolean`, `file`, `image`, and address-like fields.

If a sample exists and conflicts with MetaEvidence or the proposed item.json, stop and ask. If no sample
exists and value encoding is ambiguous, stop and warn the user instead of improvising.

---

## Pre-upload validation

Before uploading item.json to IPFS, all checks must pass:

1. JSON parses.
2. `columns` deep-equals active `MetaEvidence.metadata.columns`.
3. `Object.keys(values)` exactly equals `columns.map(c => c.label)`.
4. No value is empty unless policy explicitly permits omission.
5. No placeholder remains.
6. No unsupported `type` appears.
7. `image` and `file` values use durable IPFS paths where applicable.
8. `file` values satisfy the column's `allowedFileTypes`.
9. The policy has been read for compliance.
10. The user has confirmed the final values if the agent is going to upload or submit.

After upload, fetch the uploaded JSON back from IPFS and parse it before using the URI onchain.

---

## Four validation passes

Run these checks before any upload or transaction.

### Pass 1: JSON structure

- Parse every JSON file.
- Confirm required top-level keys exist.
- Confirm no placeholder remains.
- Confirm `metadata.columns` is a non-empty array when validating MetaEvidence.
- Confirm `item.json.columns` is an array and `item.json.values` is an object.

### Pass 2: Curate type safety

- Reject unknown field types.
- Reject forbidden aliases.
- Validate identifier constraints.
- Validate `allowedFileTypes` for file columns.
- Validate rich-address values when the schema uses `rich address`.

### Pass 3: IPFS round trip

- Upload the file only after user approval.
- Fetch the file back from the exact URI that will be used onchain.
- Parse the fetched content.
- Compare fetched JSON to local JSON.

### Pass 4: Onchain/UI compatibility

- Simulate the contract call before sending.
- For first item submissions, inspect a `NewItem` sample after the active MetaEvidence when available.
- If sample encoding and MetaEvidence disagree, stop and ask.

---

## Hard stop conditions

Stop. Do not upload, submit, or continue automatically if:

- MetaEvidence cannot be fetched or parsed.
- `metadata.columns` is missing.
- item.json columns do not exactly match MetaEvidence columns.
- a value is missing or still a placeholder.
- a field type is unsupported or uses a forbidden alias.
- the JSON is malformed.
- the policy document cannot be reached.
- the user has not explicitly approved upload or onchain submission.

Broken JSON, broken MetaEvidence, and half-baked item drafts must never be submitted.

---

## Common failure modes

Avoid these construction mistakes:

- **Renaming labels** - `"Name"` to `"Token Name"` breaks the schema contract.
- **Reordering columns** - order must match MetaEvidence exactly.
- **Rewriting descriptions** - even grammar fixes violate the verbatim-copy rule.
- **Changing `isIdentifier` flags** - alters identity/display behavior.
- **Using `type: "url"`** - use `type: "link"` instead.
- **Using `richAddress` for GTCR schemas** - use `rich address` unless fetched live MetaEvidence says otherwise.
- **Using `longText` for GTCR schemas** - use `long text` unless fetched live MetaEvidence says otherwise.
- **Submitting drafts** - placeholders and incomplete values are not valid submissions.
