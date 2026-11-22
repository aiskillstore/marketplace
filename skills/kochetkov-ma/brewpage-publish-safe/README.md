# BrewPage Publish Safe

This standalone Skillstore edition publishes to the BrewPage REST API. It saves anonymous owner tokens and private management links automatically, then uses the saved owner for a later update in the same workspace. Command output contains the reader link and storage status.

The regular BrewDoc, standalone and OpenClaw skills can deliver owner keys and management links in a verified private receipt. The regular MCP also supports private receipts and connected account authority. Use those editions for those workflows. This edition has its own version, stored in [`VERSION`](VERSION).

## Publish and update

Use Bash, Python 3.8 or newer, Node.js, curl and jq on macOS or Linux. ZIP sites also need `zip` and `unzip`. Install the tools in trusted absolute PATH locations outside the publication workspace. Start from the workspace where you want to reuse the same anonymous owner. Replace `{runner}` with the installed `scripts/brewpage-run.sh` path, quoted if needed. Pass each selected value as one argument. When filling a single-quoted slot, escape each internal `'` as `'\''`.

```bash
bash {runner} publish html --ns '{namespace}' --password-file '' --text '{content}'
bash {runner} publish site-dir --ns '{namespace}' --password-file '' --path '{directory}'
bash {runner} update html --target '{exact_saved_reader_link}' --password-file '' --path '{replacement_markdown}'
```

Use `public` as the namespace only when public listing is requested. A link-only publication is viewable by anyone with its link unless it has a password. An empty password-file value selects no password for a new publish and preserves the current password on update. For a requested password, supply an absolute path to an owner-only regular file. Use `html-file`, `json`, `file`, or `site-zip` for standalone HTML, JSON, a raw file, or a built ZIP.

Review the exact bytes you select for publication. The runner checks for common credential formats and selected password values, excludes known private inputs, and blocks opaque nested archives. Encoded secrets and unsupported formats may require separate review. For a site, the JSON manifest shows the archived entries and the number of skipped files. When it returns `CONFIRM`, re-run with `--confirmed --review-sha256 '{digest}'` only after approving that exact ZIP. Safe accepts BrewPage reader hosts. Use a regular edition for publication management on a custom reader domain. A missing target, a read-only target, or a rejected update leaves the existing item in place.

## Saved ownership and recovery

Safe stores owner records under `~/Library/Application Support/brewpage-publish-safe` on macOS or `$XDG_STATE_HOME/brewpage-publish-safe` on Linux. The Linux default is `~/.local/state/brewpage-publish-safe`. It selects a separate `0700` directory for each resolved workspace and uses `0600` owner records. The chosen storage location must be outside Git. An unsafe or unavailable store stops publishing before the request.

Use the same OS account and workspace to update the exact saved publication in a new session. When the runner reports `OWNER RECOVERY SAVED`, use `owner-recover` from that workspace. For a BrewPage subdomain, the runner verifies ownership and publication identity through the first-party API before using the link.

```bash
bash {runner} owner-recover
bash {runner} owner-pending
```

## Resolve an uncertain create

`owner-pending` reports the workspace slot, pending operation ID, request digest, and whether a protected fallback receipt is available. The ID and digest identify the local attempt. Use the exact request recorded in that slot's private `brewpage-pending-create.json` when verifying the outcome through first-party evidence. If proof is already available locally, run `owner-recover`.

If the outcome was independently verified, place `brewpage-reconciliation.json` in the same private application-state slot with mode `0600`. Set `schema` to `brewpage-safe-reconciliation-v1`, copy `operationId` and `requestSha256` from `owner-pending`, and record `evidence` with `source` equal to `owner-verified-first-party`, `verifiedByOperator` set to `true`, and `reference` pointing to the actual finding. The runner checks the local binding and records your verification. When verification is unavailable, leave the operation pending.

Use `outcome: "no-write"` for a verified absent write. For `outcome: "publication-owned"`, supply the protected `receipt` with the actual `origin`, `ownerApi`, `readerUrl`, `ownerToken`, `operationId`, and `identity` containing the publication ID and namespace. Include the actual private `manageUrl` when available. The runner checks the request and any originally selected authority. It consumes the reconciliation file after the local result is saved.

```bash
bash {runner} owner-reconcile
```
