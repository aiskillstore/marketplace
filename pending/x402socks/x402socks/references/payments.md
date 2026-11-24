# x402 payment flow

Reference for buying x402socks access. Prices are illustrative - read
`/catalog.json` and the live 402 challenge. For the wallet and `cast` side, see
`wallet.md`.

## 1. The challenge

```bash
curl -q -i --proto '=https' --proto-redir '=https' \
     -X POST https://payments.x402socks.com/v1/access/time_6h \
     -H 'content-type: application/json' -d '{}'
```

Response:

```
HTTP/2 402
payment-required: <base64 of the JSON below>
```

Decoded `PAYMENT-REQUIRED` (real example, `time_6h`):

```json
{
  "x402Version": 2,
  "resource": {
    "url": "https://payments.x402socks.com/v1/access",
    "description": "Create an x402socks proxy access account",
    "mimeType": "application/json",
    "serviceName": "x402socks"
  },
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:8453",
      "amount": "1000000",
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "payTo": "0x73BAE3c48d34d71C4CEa76DFdaa3bE2cF4d335a1",
      "maxTimeoutSeconds": 300,
      "extra": { "name": "USD Coin", "version": "2" }
    }
  ]
}
```

Read every field from `accepts[]` at runtime:

- `network` - CAIP-2 chain id. `eip155:8453` is Base mainnet.
- `amount` - **atomic units**. USDC has 6 decimals, so `"1000000"` = $1.00.
- `asset` - the token contract to authorize.
- `payTo` - the recipient.
- `extra.name` / `extra.version` - EIP-712 domain for the authorization.

Treating `amount` as a decimal, or reusing an `asset`/`payTo` from an older quote,
is the most common way to send a payment the service rejects but the chain still
settles.

## 2. Approve the full terms before paying

An approval is the whole authorization, not just the amount or a package name:
job, authorized target hosts, exact request URL, package ID, challenge
`resource`, signer public address, scheme, network, asset, recipient, EIP-712
asset domain, and exact amount must all be pinned. The signer must be bound to
the one requirement that matched.

Run `scripts/x402socks.sh quote <package_id>` first. Record its `network`,
`asset`, `pay_to`, `asset_name`, `asset_version`, and `amount_atomic`, plus the
live 402 `resource.url`, `resource.description`, and `serviceName`, as the
approved terms. Use `assets/purchase-approval.md` and fill every blank from the
user's decision. Pass those values to the purchase as values the user approved,
never as literals copied from an example and never read from the 402 you are
about to sign.

Before signing, require **exactly one** entry in the live 402 `accepts[]` and
compare every field against the approval. Also require the request URL, package
ID, `resource`, and signer address to match. Abort if the list has more than one
entry, if any field differs, or if anything is ambiguous. Do not filter the list
and pick the cheapest survivor; a challenge with an unapproved option is a
failed challenge, not a menu. One approval covers one signed authorization. A
later 402 needs a fresh user decision, not another signature from the old one.

## 3. TypeScript

```bash
npm i @x402/fetch @x402/evm viem
```

`@x402/fetch` exposes the hooks needed to enforce this before signing:
`onPaymentRequired` sees the decoded challenge and the exact request URL,
`spendControls` caps value, `policies` reject an unapproved requirement, and
`paymentRequirementsSelector` only ever sees the approved requirement.

```ts
import { readFile } from "node:fs/promises";
import {
  wrapFetchWithPayment,
  x402Client,
  x402HTTPClient,
} from "@x402/fetch";
import type {
  Network,
  PaymentPolicy,
  PaymentRequired,
  SelectPaymentRequirements,
} from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm";
import type { Account } from "viem";

// The operator writes this private file from assets/purchase-approval.md after
// the user approves. No sample values and no URLs live in this code.
type Approved = {
  job: string;
  authorizedTargets: string[];
  requestUrl: string;
  packageId: string;
  resourceUrl: string;
  resourceDescription: string;
  serviceName: string;
  scheme: string;
  network: string;
  asset: string;
  payTo: string;
  assetName: string;
  assetVersion: string;
  amountAtomic: string;
  signerAddress: string;
  approvedBy: string;
  approvedAt: string;
};

const approvalPath = process.env.X402_APPROVAL_FILE;
if (!approvalPath) throw new Error("X402_APPROVAL_FILE is required");
const APPROVED = JSON.parse(await readFile(approvalPath, "utf8")) as Approved;

const textFields = [
  "job", "requestUrl", "packageId", "resourceUrl", "resourceDescription",
  "serviceName", "scheme", "network", "asset", "payTo", "assetName",
  "assetVersion", "amountAtomic", "signerAddress", "approvedBy", "approvedAt",
] as const;
for (const key of textFields) {
  const value = APPROVED[key];
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`approval is missing ${key}; ask the user again`);
  }
}
if (!Array.isArray(APPROVED.authorizedTargets) || APPROVED.authorizedTargets.length === 0) {
  throw new Error("approval has no authorized target hosts; ask the user again");
}
if (!/^\d+$/.test(APPROVED.amountAtomic) || APPROVED.amountAtomic === "0") {
  throw new Error("approved amount must be a positive integer in atomic USDC");
}

const same = (a: string, b: string) => a.toLowerCase() === b.toLowerCase();
const optionMatches = (option: {
  scheme: string;
  network: string;
  asset: string;
  payTo: string;
  amount: string;
  extra?: Record<string, unknown>;
}) => {
  const extra = (option.extra ?? {}) as { name?: string; version?: string };
  return (
    option.scheme === APPROVED.scheme &&
    option.network === APPROVED.network &&
    same(option.asset, APPROVED.asset) &&
    same(option.payTo, APPROVED.payTo) &&
    extra.name === APPROVED.assetName &&
    extra.version === APPROVED.assetVersion &&
    BigInt(option.amount) === BigInt(APPROVED.amountAtomic)
  );
};

// This guard receives the challenge and the actual request URL, so a copied
// client cannot use a fixed purchase URL or a different package.
function assertApprovedChallenge(challenge: PaymentRequired, requestUrl: string) {
  if (requestUrl !== APPROVED.requestUrl) {
    throw new Error("request URL is not the approved purchase URL");
  }
  const parsed = new URL(requestUrl);
  if (!parsed.pathname.endsWith(`/v1/access/${APPROVED.packageId}`)) {
    throw new Error("request URL is not the approved package");
  }
  if (challenge.x402Version !== 2) throw new Error("unexpected x402 version");
  if (challenge.resource.url !== APPROVED.resourceUrl) {
    throw new Error("challenge resource URL is not approved");
  }
  if ((challenge.resource.description ?? "") !== APPROVED.resourceDescription) {
    throw new Error("challenge entitlements are not approved");
  }
  if ((challenge.resource.serviceName ?? "") !== APPROVED.serviceName) {
    throw new Error("challenge service is not approved");
  }
  const options = challenge.accepts ?? [];
  if (options.length !== 1) {
    throw new Error(`402 advertised ${options.length} options; approval covers exactly one`);
  }
  if (!optionMatches(options[0])) {
    throw new Error("402 challenge differs from the approved terms");
  }
}

const pinApprovedTerms: PaymentPolicy = (_version, options) => {
  if (options.length !== 1) throw new Error("expected exactly one approved option");
  if (!optionMatches(options[0])) throw new Error("402 differs from the approved terms");
  return [options[0]];
};

const selectApproved: SelectPaymentRequirements = (_version, options) => {
  if (options.length !== 1) throw new Error("expected exactly one approved option");
  return options[0];
};

// The host supplies a non-exportable signer (keystore, hardware wallet, or
// KMS/HSM). This skill never reads or prints a raw key; see wallet.md.
declare function loadHostSigner(): Promise<Account>;
const account = await loadHostSigner();
if (!same(account.address, APPROVED.signerAddress)) {
  throw new Error("signer is not the approved paying wallet");
}

const client = new x402Client(selectApproved)
  .register(APPROVED.network as Network, new ExactEvmScheme(account))
  .registerPolicy(pinApprovedTerms)
  .setSpendControls({
    allowedAssets: [{
      network: APPROVED.network as Network,
      asset: APPROVED.asset,
      maxAmountPerPayment: APPROVED.amountAtomic,
    }],
  });

const httpClient = new x402HTTPClient(client).onPaymentRequired(
  async ({ paymentRequired, requestUrl }) => {
    assertApprovedChallenge(paymentRequired, requestUrl);
  },
);

const fetchWithPayment = wrapFetchWithPayment(fetch, httpClient);
const res = await fetchWithPayment(APPROVED.requestUrl, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: "{}",
});
if (!res.ok) throw new Error(`purchase failed: ${res.status}`);

const data = (await res.json()) as { token?: string };
if (typeof data.token !== "string") throw new Error("purchase response had no token");
// Pass data.token to your 0600 token store. Never log it or the raw response.
// Keep PAYMENT-RESPONSE locally if recovery needs the tx hash.
```

The wrapper handles the request loop: first request, 402 parse, authorization
signing, retry with `PAYMENT-SIGNATURE`. The `onPaymentRequired` hook and policy
run on the challenge that is actually about to be paid, so a URL, package,
entitlement, signer, price, asset, or recipient change aborts instead of
signing. The one protocol retry that sends this signed authorization is part of
the approved purchase. A later 402 is a new decision and needs fresh approval.

## 4. Python

```bash
uv add "x402[httpx,evm]"
```

Read the live challenge before any signer exists, using the same approved terms.
The approval file is written from `assets/purchase-approval.md` after the user
decides. This example contains no payment literals and never creates that file:

```python
import base64, json, os
import httpx

path = os.environ.get("X402_APPROVAL_FILE")
if not path:
    raise SystemExit("X402_APPROVAL_FILE is required")
with open(path, encoding="utf-8") as fh:
    approved = json.load(fh)

required = (
    "job", "request_url", "package_id", "resource_url",
    "resource_description", "service_name", "scheme", "network", "asset",
    "pay_to", "asset_name", "asset_version", "amount_atomic",
    "signer_address", "approved_by", "approved_at",
)
for key in required:
    value = approved.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit("approval is missing %s; ask the user again" % key)
if not approved.get("authorized_targets"):
    raise SystemExit("approval has no authorized target hosts; ask the user again")
if not approved["amount_atomic"].isdecimal() or int(approved["amount_atomic"]) <= 0:
    raise SystemExit("approved amount must be a positive integer in atomic USDC")
signer = os.environ.get("X402_SIGNER_ADDRESS", "").lower()
if signer != approved["signer_address"].lower():
    raise SystemExit("signer is not the approved paying wallet")

r = httpx.post(approved["request_url"], json={})
if r.status_code != 402:
    raise SystemExit("expected 402, got %s" % r.status_code)

raw = r.headers["payment-required"]
raw += "=" * (-len(raw) % 4)          # base64url may omit padding
challenge = json.loads(base64.urlsafe_b64decode(raw))
options = challenge.get("accepts", [])

if challenge.get("x402Version") != 2:
    raise SystemExit("refusing: unexpected x402 version")
resource = challenge.get("resource") or {}
if resource.get("url") != approved["resource_url"]:
    raise SystemExit("refusing: resource URL is not approved")
if (resource.get("description") or "") != approved["resource_description"]:
    raise SystemExit("refusing: entitlements are not approved")
if (resource.get("serviceName") or "") != approved["service_name"]:
    raise SystemExit("refusing: service is not approved")
if len(options) != 1:
    raise SystemExit("refusing: the 402 is not exactly one approved option")

req = options[0]
extra = req.get("extra") or {}
if not (
    req.get("scheme") == approved["scheme"]
    and req.get("network") == approved["network"]
    and req.get("asset", "").lower() == approved["asset"].lower()
    and req.get("payTo", "").lower() == approved["pay_to"].lower()
    and extra.get("name") == approved["asset_name"]
    and extra.get("version") == approved["asset_version"]
    and str(req.get("amount", "")).isdecimal()
    and int(req["amount"]) == int(approved["amount_atomic"])
):
    raise SystemExit("refusing: the 402 is not exactly the approved terms")
```

The preflight alone does not close the race: the retry can carry a different
challenge. Apply the same check in the client's policy or selector hook. If it
has no hook, do not let it auto-pay, read the 402 yourself and sign exactly the
requirement you validated. Do not re-sign a later 402 from this approval; stop
and ask for a new decision.

Pin the network to `eip155:8453` rather than a wildcard like `eip155:*`. A
wildcard lets the client auto-pay on whatever chain a server advertises, which is
exactly the wrong behavior when an agent is spending unattended.

## 5. Manual signing sketch

Only needed if you cannot use a library. `wallet.md` has the `cast` version.

1. Build an EIP-3009 `TransferWithAuthorization` for `asset`, `payTo`, and
   `amount`.
2. Sign it with EIP-712 using domain `{ name: extra.name, version: extra.version,
   chainId: 8453, verifyingContract: asset }`.
3. Assemble the x402 v2 payment payload:
   `{ x402Version: 2, scheme: "exact", network, payload: { signature, authorization } }`.
4. Base64-encode it and send it as `PAYMENT-SIGNATURE` on the same URL, same body.

Success is `200` with `{"account": {...}, "token": "..."}` and a
`PAYMENT-RESPONSE` header containing settlement metadata. Keep the
`PAYMENT-RESPONSE` value or the settlement tx hash: it is the only proof of
purchase and the input to recovery. Write the token straight to a file with mode
`0600`; do not echo the response into a transcript or log.

## 6. Never pay twice

- A `502` means the payment settled but provisioning failed. **Do not resend.**
  The payment is already on-chain.
- A broadcast transfer may wait for confirmations. Confirmation is retried
  server-side; polling continues on the buyer side.
- If a token was lost after a settled payment, recover it (below) rather than
  purchasing again.
- If a recovery attempt fails with `502 recovery_unavailable`, retry later - it
  is explicitly safe.

## 7. Credential recovery (token lost)

```bash
# message to sign (EIP-191 personal_sign), no trailing newline:
x402socks credential recovery v1
tx_hash: 0xSETTLEMENT_TX_HASH
issued_at: 1792000000
```

Then, with the signature written to a private file (never placed in argv), pass
back the **same** `issued_at` you signed:

```bash
read -r ISSUED_AT < ~/.config/x402socks/recovery.issued_at
read -r SIGNATURE < ~/.config/x402socks/recovery.sig
printf '%s\n' "$SIGNATURE" | scripts/x402socks.sh recover 0xSETTLEMENT_TX_HASH "$ISSUED_AT"
```

The signing wallet must be the wallet that paid. `issued_at` must be within
+/-10 minutes of now, and the helper sends the timestamp you supply, not a new
one; a mismatch makes the signature invalid. The original `PAYMENT-SIGNATURE` is
deliberately rejected: it is public settlement calldata that anyone could replay.

Recovery returns a replacement token once. The helper saves it atomically to the
`0600` token file and prints only non-secret fields. It refuses a plaintext or
non-x402socks `X402SOCKS_PAY` override before it reads the signature. If you call
the endpoint directly, build the JSON in a private `0600` file, send it with
`--data-binary @file`, and do not print the raw response - it is the only copy of
the replacement token.

| Error                       | Meaning                                                    |
| --------------------------- | ---------------------------------------------------------- |
| `400 invalid_request`       | malformed body                                             |
| `400 stale_recovery`        | `issued_at` outside the freshness window                   |
| `400 invalid_signature`     | non-hex signature                                          |
| `403 ownership_not_proven`  | signature does not recover to the paying wallet            |
| `404 not_recoverable`       | unknown, unsettled, or not-yet-provisioned tx              |
| `409 account_inactive`      | account no longer live; recovery is fail-closed            |
| `410 plan_expired`          | paid plan expired; no automatic catch-up                   |
| `502 recovery_unavailable`  | transient; safe to retry later                             |

`scripts/x402socks.sh recover-message <tx_hash>` prints a correctly formatted
message with a fresh timestamp and prints the exact `recover` command to run with
that same timestamp.

## 8. No wallet = no purchase

The x402 flow needs a signer with USDC on Base. If the agent has no wallet access,
it cannot buy a package; there is no free tier. See `wallet.md` for the `cast`
recipes and key-handling rules.
