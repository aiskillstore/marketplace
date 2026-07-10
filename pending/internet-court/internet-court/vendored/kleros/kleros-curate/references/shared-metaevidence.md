# Shared: MetaEvidence Retrieval and Authoring
<!-- Sources: curate-v1/curate-light-skill.md §1-§2, curate-v1/pgtcr-stake-curate-skill.md §5A-5B -->

MetaEvidence is the onchain source of truth for every Curate workflow:
- **Policy document**: `fileURI` points to the human-readable registry rules.
- **Item schema**: `metadata.columns[]` defines field labels, types, identifiers, and item.json construction.

Do not ask users for schema fields until you have extracted `metadata.columns` from the current MetaEvidence.
Do not rely on screenshots, old docs, UI labels, policy prose, or memory. Fetch from live registry state every session.

---

## RPC log retrieval (`eth_getLogs`)

Fetch MetaEvidence events from the registry contract itself.

Filter:

```json
{
  "address": "<registryAddress>",
  "topics": [
    "0x61606860eb6c87306811e2695215385101daab53bd6ab4e9f9049aead9363c7d"
  ],
  "fromBlock": "<registry-deployment-block-or-earliest>",
  "toBlock": "latest"
}
```

Topic0:

```text
0x61606860eb6c87306811e2695215385101daab53bd6ab4e9f9049aead9363c7d
```

Event:

```solidity
MetaEvidence(uint256 indexed _metaEvidenceID, string _evidence)
```

`_evidence` is the IPFS pointer to the MetaEvidence JSON.

For full ABI context, see `shared-abi-fragments.md`.

---

## Sort and choose the current MetaEvidence

After retrieving logs, sort matching logs by:

1. `blockNumber`
2. `transactionIndex`
3. `logIndex`

Use ascending order for history and descending order for "latest first" inspection. Do not use an old cached
URI if a newer valid MetaEvidence event exists.

**Important:** do not assume `_metaEvidenceID = 0` and `_metaEvidenceID = 1` remain the only active IDs
forever. Factory deployment commonly emits initial registration and clearing MetaEvidence, but governor
updates can emit later MetaEvidence events with new IDs. The latest applicable event is what matters.

---

## Fetch the MetaEvidence JSON

Fetch `_evidence` via a gateway:

```text
https://cdn.kleros.link/ipfs/<CID>
https://ipfs.io/ipfs/<CID>
```

If the event path is `/ipfs/<CID>/metaEvidence.json`, prepend only the gateway host. Do not add a second
`/ipfs/` segment.

Parse the JSON and extract:

- `fileURI` - policy document URI.
- `metadata.columns[]` - canonical item schema.
- `metadata.logoURI` - list logo for production registries.
- title/description/rulingOptions - useful for classifying registration vs clearing streams.

Stop if the JSON cannot be fetched, parsed, or validated.

---

## LGTCR specifics

LightGeneralizedTCR uses separate registration and clearing MetaEvidence.

Use the correct policy stream:

- `addItem` flow - use the latest registration-like MetaEvidence.
- `removeItem` flow - use the latest clearing-like MetaEvidence.
- Challenging a registration request - use registration policy.
- Challenging a removal request - use clearing policy.

How to classify events:

1. Fetch recent MetaEvidence events for the registry using the topic above.
2. Sort latest first.
3. Fetch each candidate `_evidence` JSON.
4. Classify by explicit content:
   - registration: title/description/ruling options such as `Add`, `Add It`, `Don't Add It`.
   - clearing: title/description/ruling options such as `Remove`, `Remove It`, `Don't Remove It`.
5. Use the latest candidate matching the operation.

Do not rely only on event parity, hardcoded stream IDs, or the absolute latest log. Some update transactions
emit a registration MetaEvidence and then a clearing MetaEvidence in the same transaction; blindly taking the
last log can choose the clearing policy for an `addItem` task.

For the narrow task "recover the fields to compose item.json from a registry link", the agent may fetch the
latest valid MetaEvidence event, parse `_evidence`, and read `metadata.columns`. If the latest event is clearly
clearing and a same-block or nearby registration MetaEvidence exists, use the registration columns for `addItem`.
If schemas differ or classification is ambiguous, stop and ask.

Scout registries use these same LGTCR mechanics. Read `scout-registries.md` for Scout-specific registry
addresses and seed-template checks.

---

## PGTCR specifics

PermanentGTCR uses a single MetaEvidence URI. There is no registration/clearing split.

Primary path: query Goldsky for `registry.arbitrationSettings[0].metaEvidenceURI`.
Specific endpoints are in `stake-curate.md`.

Fallback path: use the same `eth_getLogs` method above and take the latest valid MetaEvidence event for the
registry. Fetch `_evidence`, parse JSON, and extract `metadata.columns[]`.

---

## MetaEvidence authoring rules

Before uploading or using MetaEvidence onchain, validate it as strictly as item.json.

Required production metadata:

- top-level `title`, `description`, `question`, `category`, `fileURI`, and `metadata`.
- `fileURI` must point to the human-readable policy.
- Strongly prefer a PDF policy document for human and juror review. Use a non-PDF policy only if the user
  explicitly accepts the review and compatibility risk.
- `metadata.logoURI` is required for production lists.
- `metadata.tcrTitle`, `metadata.tcrDescription`, `metadata.itemName`, and `metadata.itemNamePlural`
  must match the list.
- `metadata.columns` must be final and valid.
- LGTCR deployments need separate registration and clearing MetaEvidence.
- PGTCR deployments need one MetaEvidence.

Valid GTCR column `type` values when authoring new MetaEvidence:

- `text`
- `long text`
- `link`
- `address`
- `rich address`
- `image`
- `file`
- `number`
- `boolean`
- `GTCR address`

Current scope: this skill covers Light Curate / GTCR and Stake Curate / PGTCR. Do not author Curate V2-only
type spellings such as `longText`, `richAddress`, or `chain` for GTCR/PGTCR MetaEvidence unless the target
interface or live MetaEvidence proves that exact spelling is expected.

Never author unsupported aliases:

- `url` - use `link`
- `uri` - use `link` or `file`, depending on the field
- `string` - use `text`
- `markdown` - use `long text`
- `bool` - use `boolean`
- `integer`, `int`, `float`, `decimal` - use `number`

For `file` columns, include `allowedFileTypes`, for example `pdf`, `json`, or `pdf json`.

LGTCR registration MetaEvidence should clearly describe adding an item:

```json
{
  "title": "Add an item to <List Name>",
  "description": "Someone requested to add an item to <List Name>.",
  "question": "Does the item comply with the required criteria?",
  "category": "Curated Lists",
  "fileURI": "/ipfs/<POLICY_PDF_CID>",
  "metadata": {
    "tcrTitle": "<List Name>",
    "tcrDescription": "<List description>",
    "itemName": "<singular item name>",
    "itemNamePlural": "<plural item name>",
    "logoURI": "/ipfs/<LOGO_CID>",
    "requireRemovalEvidence": true,
    "columns": []
  }
}
```

LGTCR clearing MetaEvidence should clearly describe removing an item and should normally use the same
`metadata.columns` as registration MetaEvidence. Diverge only when the target contract/interface proves it is
expected.

```json
{
  "title": "Remove an item from <List Name>",
  "description": "Someone requested to remove an item from <List Name>.",
  "question": "Does the item fail to comply with the required criteria?",
  "category": "Curated Lists",
  "fileURI": "/ipfs/<POLICY_PDF_CID>",
  "metadata": {
    "tcrTitle": "<List Name>",
    "tcrDescription": "<List description>",
    "itemName": "<singular item name>",
    "itemNamePlural": "<plural item name>",
    "logoURI": "/ipfs/<LOGO_CID>",
    "requireRemovalEvidence": true,
    "columns": []
  }
}
```

PGTCR MetaEvidence is a single stream. Do not create a separate clearing MetaEvidence for PGTCR unless the
specific contract flow explicitly requires one.

```json
{
  "title": "Submit an item to <List Name>",
  "description": "Someone requested to submit an item to <List Name>.",
  "question": "Does the item comply with the required criteria?",
  "category": "Curated Lists",
  "fileURI": "/ipfs/<POLICY_PDF_CID>",
  "metadata": {
    "tcrTitle": "<List Name>",
    "tcrDescription": "<List description>",
    "itemName": "<singular item name>",
    "itemNamePlural": "<plural item name>",
    "logoURI": "/ipfs/<LOGO_CID>",
    "columns": []
  }
}
```

When deploying LGTCR, pass MetaEvidence URIs in the factory's expected order: registration first, clearing
second. Do not swap them.

Stop before upload or deployment if:

- JSON does not parse.
- `metadata.columns` is missing or empty.
- any column type is unsupported.
- any placeholder remains.
- `fileURI` is missing.
- production `metadata.logoURI` is missing.
- the policy is not a PDF and the user has not explicitly accepted the review and compatibility risk.
- the user has not confirmed schema, policy, logo, chain, arbitrator/court, and deploy parameters.
