# Verify Your List
<!-- Sources: Kleros Classic Curate docs, kleros/gtcr Classic submit modal, @kleros/gtcr-encoder -->

Use this file when a user wants a deployed Curate registry to be visible and verified in the Curate
frontend. This is a narrow list-of-lists workflow, not full Curate Classic support.

This workflow is recommended for list creators and for anyone who wants a deployed Curate registry to appear
in the frontend.

## Why verify a list

Deploying a registry does not automatically make it easy to find in the Curate UI. Verifying the list means
submitting the deployed registry to the network's list-of-lists so users can discover it from the frontend,
recognize it as a listed registry, and get more visibility.

List-of-lists submission is not mandatory. It is highly recommended for public registries and unnecessary
only when the list is intentionally private or stealth.

## Known list-of-lists

These registries are Curate Classic / `GeneralizedTCR`, not Light Curate / `LightGeneralizedTCR`.

| Network | Chain ID | List-of-lists |
|---------|----------|---------------|
| Mainnet | `1` | `0xba0304273a54dfec1fc7f4bccbf4b15519aecf15` |
| Gnosis | `100` | `0x2442D40B0aeCad0298C2724A97F2f1BbDF2C2615` |
| Sepolia | `11155111` | `0xD965Ce430afE0423Ff19A5eb08F7C5722EFabCaF` |

Do not use the Light Curate `addItem("/ipfs/<CID>")` transaction path for these registries.

## Simple Classic submission flow

1. **Choose the network list-of-lists** matching the deployed registry's chain.
2. **Confirm contract type** before building calldata:
   - `eth_getCode(listOfListsAddress)` must be non-empty.
   - Classic `addItem(bytes)` must be available.
   - Do not proceed with the Light Curate `addItem(string)` assumption.
3. **Fetch the latest MetaEvidence** from the list-of-lists contract using `shared-metaevidence.md`.
   Classic `GeneralizedTCR` emits the same `MetaEvidence(uint256,string)` event; use the shared
   `eth_getLogs` topic and latest-event procedure.
4. **Read the list-of-lists policy** from `fileURI`. Confirm the deployed registry satisfies that policy
   before encoding or submitting anything.
5. **Extract `metadata.columns`** and build values from the live schema. Do not assume field labels.
6. **Fill the deployed registry address** in the field indicated by the schema. If the schema uses
   `GTCR address`, the value is the deployed registry address on that same chain.
7. **Encode the item for Classic Curate** with `@kleros/gtcr-encoder` semantics:

   ```ts
   import { gtcrEncode } from "@kleros/gtcr-encoder";

   const encodedItem = gtcrEncode({
     columns,
     values
   });
   ```

   Classic Curate stores item data as encoded bytes. The encoder maps `GTCR address` and `address` to
   Solidity `address`, `number` to `int256`, `boolean` to `bool`, and text/file/image/link/rich-address
   style values to strings.

8. **Compute the full native-token Classic submission value live**:
   - `submissionBaseDeposit()`
   - `arbitrator()`
   - `arbitratorExtraData()`
   - `IArbitrator(arbitrator).arbitrationCost(arbitratorExtraData)`
   - `msg.value = submissionBaseDeposit + arbitrationCost`

   Never send only `submissionBaseDeposit()`. Classic `addItem(bytes)` requires the full
   `submissionBaseDeposit + arbitrationCost` value.

9. **Simulate the exact transaction**:

   ```text
   GeneralizedTCR.addItem(encodedItem)
   msg.value = submissionBaseDeposit + arbitrationCost
   ```

10. **Ask for explicit user approval** with:
   - target chain and list-of-lists address
   - policy compliance summary
   - fetched columns
   - final values
   - encoded item bytes
   - computed `msg.value`
11. **Submit only after approval**, then verify the request was created and the item decodes back to the
    expected values with the same columns.

## Stop conditions

Stop and ask instead of submitting if:

- the target chain is unclear.
- the registry address to verify is not the deployed registry address.
- MetaEvidence cannot be fetched or parsed.
- the list-of-lists policy was not read.
- the deployed registry does not clearly comply with the list-of-lists policy.
- `metadata.columns` is missing.
- the live schema does not contain a registry-address field.
- `@kleros/gtcr-encoder` semantics are unavailable.
- the contract ABI does not expose Classic `addItem(bytes)`.
- the deposit cannot be computed live.
- simulation fails.
- the user has not approved the final submission.
