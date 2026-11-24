# x402 payment flow

Reference for buying x402socks access. Prices are illustrative - read
`/catalog.json` and the live 402 challenge. For the wallet and `cast` side, see
`wallet.md`.

## 1. The challenge

```bash
curl -i -X POST https://payments.x402socks.com/v1/access/time_6h \
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
scheme, network, asset, recipient, EIP-712 asset domain, and exact amount must
all be pinned. The signer must be bound to the one requirement that matched.

Run `scripts/x402socks.sh quote <package_id>` first. Record its `network`,
`asset`, `pay_to`, `asset_name`, `asset_version`, and `amount_atomic` as the
approved terms (the template is `assets/purchase-approval.md`). Pass them to the
purchase as values the user approved - never read them from the 402 you are about
to sign.

Before signing, require **exactly one** entry in the live 402 `accepts[]` and
compare every field against the approval. Abort if the list has more than one
entry, if any field differs, or if anything is ambiguous. Do not filter the list
and pick the cheapest survivor; a challenge with an unapproved option is a
failed challenge, not a menu.

## 3. TypeScript

```bash
npm i @x402/fetch @x402/evm viem
```

`@x402/fetch` exposes the hooks needed to enforce this before signing:
`spendControls` caps value, `policies` reject a challenge that is not the
approved one, and `paymentRequirementsSelector` only ever sees the approved
requirement.

```ts
import { wrapFetchWithPaymentFromConfig } from "@x402/fetch";
import type {
  PaymentPolicy,
  SelectPaymentRequirements,
} from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm";

// Copy these from the quote the user approved. Never derive them from the 402
// that is about to be signed.
const APPROVED = {
  scheme: "exact",
  network: process.env.X402_APPROVED_NETWORK ?? "",
  asset: process.env.X402_APPROVED_ASSET ?? "",
  payTo: process.env.X402_APPROVED_PAY_TO ?? "",
  assetName: process.env.X402_APPROVED_ASSET_NAME ?? "",
  assetVersion: process.env.X402_APPROVED_ASSET_VERSION ?? "",
  amountAtomic: BigInt(process.env.X402_APPROVED_AMOUNT_ATOMIC ?? "0"),
};

if (
  !APPROVED.network ||
  !APPROVED.asset ||
  !APPROVED.payTo ||
  !APPROVED.assetName ||
  !APPROVED.assetVersion ||
  APPROVED.amountAtomic <= 0n
) {
  throw new Error("missing approved terms; run `quote` and record its output");
}

const same = (a: string, b: string) => a.toLowerCase() === b.toLowerCase();

// Require exactly one advertised option and require it to equal the approval
// field for field, including the exact amount. More than one option, an exact
// amount mismatch, or any difference is a failed challenge, not a menu.
const pinApprovedTerms: PaymentPolicy = (_version, options) => {
  if (options.length !== 1) {
    throw new Error(
      `402 advertised ${options.length} payment options; approval covers exactly one`,
    );
  }
  const option = options[0];
  const extra = (option.extra ?? {}) as { name?: string; version?: string };
  const matches =
    option.scheme === APPROVED.scheme &&
    option.network === APPROVED.network &&
    same(option.asset, APPROVED.asset) &&
    same(option.payTo, APPROVED.payTo) &&
    extra.name === APPROVED.assetName &&
    extra.version === APPROVED.assetVersion &&
    BigInt(option.amount) === APPROVED.amountAtomic;
  if (!matches) {
    throw new Error(
      "402 challenge differs from the approved scheme/network/asset/payTo/domain/amount",
    );
  }
  return [option];
};

// The selector can only ever return the one requirement the policy approved.
const selectApproved: SelectPaymentRequirements = (_version, options) => {
  if (options.length !== 1) {
    throw new Error("expected exactly one approved payment option");
  }
  return options[0];
};

import type { Account } from "viem";

// The host supplies a non-exportable signer (keystore, hardware wallet, or
// KMS/HSM). This skill never reads or prints a raw key; see wallet.md.
declare function loadHostSigner(): Promise<Account>;

const account = await loadHostSigner();

const fetchWithPayment = wrapFetchWithPaymentFromConfig(fetch, {
  schemes: [{ network: APPROVED.network, client: new ExactEvmScheme(account) }],
  // Second layer: the library enforces the exact cap before policies and signing.
  spendControls: {
    maxAmountPerPayment: Number(APPROVED.amountAtomic) / 1_000_000,
  },
  policies: [pinApprovedTerms],
  paymentRequirementsSelector: selectApproved,
});

const res = await fetchWithPayment(
  "https://payments.x402socks.com/v1/access/time_6h",
  { method: "POST", headers: { "content-type": "application/json" }, body: "{}" },
);

if (!res.ok) throw new Error(`purchase failed: ${res.status}`);

const { account: acct, token } = await res.json();
console.log("settlement:", res.headers.get("PAYMENT-RESPONSE"));
```

The wrapper handles the request loop: first request, 402 parse, authorization
signing, retry with `PAYMENT-SIGNATURE`. The policy runs on the challenge that is
actually about to be paid, so a price, asset, or recipient change between quote
and purchase aborts instead of signing.

## 4. Python

```bash
uv add "x402[httpx,evm]"
```

Read the live challenge before any signer exists, using the same approved terms:

```python
import base64, json
import httpx

# Copy these from the approved quote. Do not take them from this 402.
APPROVED = {
    "scheme": "exact",
    "network": "eip155:8453",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "payTo": "0x73BAE3c48d34d71C4CEa76DFdaa3bE2cF4d335a1",
    "assetName": "USD Coin",
    "assetVersion": "2",
    "amount_atomic": 1_000_000,
}

def approved(req):
    return (
        req.get("scheme") == APPROVED["scheme"]
        and req.get("network") == APPROVED["network"]
        and req.get("asset", "").lower() == APPROVED["asset"].lower()
        and req.get("payTo", "").lower() == APPROVED["payTo"].lower()
        and req.get("extra", {}).get("name") == APPROVED["assetName"]
        and req.get("extra", {}).get("version") == APPROVED["assetVersion"]
        and int(req.get("amount", "0")) == APPROVED["amount_atomic"]
    )

r = httpx.post("https://payments.x402socks.com/v1/access/time_6h", json={})
assert r.status_code == 402, r.status_code

raw = r.headers["payment-required"]
raw += "=" * (-len(raw) % 4)          # base64url may omit padding
challenge = json.loads(base64.urlsafe_b64decode(raw))
options = challenge.get("accepts", [])

# Require exactly one option and require it to equal the approval exactly.
if len(options) != 1 or not approved(options[0]):
    raise SystemExit("refusing: the 402 is not exactly the approved terms")
req = options[0]
```

The preflight alone does not close the race: the retry can carry a different
challenge. Apply the same check in the client's policy/selector hook. If it has
no hook, do not let it auto-pay - read the 402 yourself and sign exactly the
requirement you validated.

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
