# Shared: IPFS Upload Guidance
<!-- Source: curate-v1/curate-light-skill.md §5, curate-v1/pgtcr-stake-curate-skill.md §6, curate-v1-scout/scout-skills.md §9, kleros-ipfs-upload/SKILL.md, CLAUDE.md -->
<!-- Applies to: LGTCR, PGTCR, Scout — no flavor subsections; upload procedure is identical -->

## Durability rationale

Third-party pins can vanish — service changes, token expiry, account cancellation break the pin without notice.

Once a CID is recorded in a MetaEvidence or item event onchain, the artifact must remain retrievable for the full dispute lifecycle. Disputes run for weeks or months after submission; a missing artifact means jurors cannot evaluate evidence.

## Default upload path: Kleros x402 gateway

Use the `kleros-ipfs-upload` skill by default for every IPFS upload related to Kleros interactions. This
includes Curate artifacts, dispute evidence, appeal evidence, MetaEvidence, policies, item metadata, images,
logos, and visual proofs.

That skill uploads through the Kleros x402 endpoint:

```text
POST https://kleros-ipfs-gateway.fly.dev/upload-to-ipfs
```

The gateway is operated for Kleros ecosystem artifacts and pins through the Kleros-backed upload path used by
this repo. This is the only upload flow explained here because Curate artifacts become onchain references:
if the file disappears, jurors, challengers, and users may be unable to verify the submission.

Agents may use another IPFS pinning source only if the user explicitly accepts that it is outside the skill's
safe path and at the user's own risk. External or self-managed pins can become unpinned because of account
cancellation, token expiry, service changes, or operator error. If a policy, MetaEvidence, evidence file,
logo, or item payload becomes unavailable after an onchain transaction, the user can lose deposits, challenge
opportunities, rewards, or dispute credibility.

Do not document or suggest Pinata, The Graph IPFS node, ad-hoc gateway uploads, or temporary local nodes as
normal Curate upload paths. Those are outside the skill's safe path.

## Submission format rule

Use `/ipfs/<CID>` in all onchain fields — `_evidence` parameter, MetaEvidence JSON, item.json values:

```text
/ipfs/<CID>
```

Never use a full gateway URL (`https://cdn.kleros.link/ipfs/...`, `https://ipfs.io/ipfs/...`).

WHY: gateway URLs are mutable — the domain can change or the service can go offline. The CID is the permanent, content-addressed identifier; gateways are interchangeable.

## Double-slash trap

`cids[]` from the Kleros gateway already includes the `/ipfs/` prefix (e.g. `/ipfs/QmXXX...`). Build CDN display URLs as:

```text
"https://cdn.kleros.link" + cid      ✓
"https://cdn.kleros.link/ipfs/" + cid  ✗  (double-slash)
```

Alternatively, use the `urls[]` field from the API response directly — it contains fully-formed URLs with no construction needed.

## Image guidance

- Prefer PNG
- Token logos: at least 128×128 pixels, ideally square
- CDN visual proof: screenshot must show the exact domain/subdomain page with address context visible — not just the image in isolation

## External pinning risk note

Agents may have access to other IPFS tools, but using them for Curate artifacts is outside this skill's
recommended flow. If the user insists on another provider, state the durability and money-loss risks clearly,
record the user's approval, and still require an IPFS round-trip fetch before any onchain transaction.
