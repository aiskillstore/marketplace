# x402 payment flow

Reference for buying x402socks access. Prices are illustrative — read `/catalog.json` and the live 402 challenge.

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

- `network` — CAIP-2 chain id. `eip155:8453` is Base mainnet.
- `amount` — **atomic units**. USDC has 6 decimals, so `"1000000"` = $1.00.
- `asset` — the token contract to authorize.
- `payTo` — the recipient.
- `extra.name` / `extra.version` — EIP-712 domain for the authorization signature.

Treating `amount` as a decimal, or reusing an `asset`/`payTo` from an older quote, is the most common way to send a payment that the service rejects but the chain still settles.

## 2. Pay with a library (recommended)

An x402 payment wrapper will sign **whatever the next 402 asks for**. That is
fine when a human clicks "pay", and unsafe when an agent buys unattended. The
approved amount has to be enforced in code, against the exact challenge that is
about to be signed — not just checked once before the purchase.

### TypeScript

```bash
npm i @x402/fetch @x402/evm viem
```

```ts
import { wrapFetchWithPaymentFromConfig } from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm";
import { privateKeyToAccount } from "viem/accounts";

// The amount the user actually approved, in atomic USDC units.
// $1.00 -> 1_000_000n. Never derive this from the server's current quote.
const APPROVED_MAX_ATOMIC = 1_000_000n;
const EXPECTED_NETWORK = "eip155:8453";

const account = privateKeyToAccount(process.env.EVM_PRIVATE_KEY as `0x${string}`);

// Guard the base fetch: inspect every 402 BEFORE the payment wrapper signs.
const guardedFetch: typeof fetch = async (input, init) => {
  const res = await fetch(input, init);
  if (res.status !== 402) return res;

  const header = res.headers.get("PAYMENT-REQUIRED");
  if (!header) throw new Error("402 without PAYMENT-REQUIRED");

  const challenge = JSON.parse(Buffer.from(header, "base64").toString("utf8"));
  const req = challenge.accepts?.[0];
  if (!req) throw new Error("402 without a payment requirement");

  if (req.network !== EXPECTED_NETWORK) {
    throw new Error(`refusing to pay on ${req.network}`);
  }

  const amount = BigInt(req.amount);
  if (amount > APPROVED_MAX_ATOMIC) {
    throw new Error(
      `quote ${amount} exceeds approved ${APPROVED_MAX_ATOMIC} atomic units`,
    );
  }
  return res;
};

const fetchWithPayment = wrapFetchWithPaymentFromConfig(guardedFetch, {
  schemes: [{ network: EXPECTED_NETWORK, client: new ExactEvmScheme(account) }],
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
signing, retry with `PAYMENT-SIGNATURE`. The guard runs on the response that is
actually about to be paid, so a price change between quote and purchase cannot
slip through.

### Python

```bash
uv add "x402[httpx,evm]"
```

Do a preflight so the user sees the real amount before any signer exists:

```python
import base64, json, os
import httpx

APPROVED_MAX_ATOMIC = 1_000_000  # $1.00

r = httpx.post("https://payments.x402socks.com/v1/access/time_6h", json={})
assert r.status_code == 402, r.status_code

challenge = json.loads(base64.b64decode(r.headers["payment-required"]))
req = challenge["accepts"][0]
assert req["network"] == "eip155:8453"
assert int(req["amount"]) <= APPROVED_MAX_ATOMIC, (
    f"quote {req['amount']} exceeds approved {APPROVED_MAX_ATOMIC}"
)
```

```python
from x402 import x402Client
from x402.mechanisms.evm.exact import ExactEvmScheme

client = x402Client()                      # wrap your httpx transport with this client
client.register("eip155:8453", ExactEvmScheme(signer=my_signer))
```

The preflight alone does not close the race: the retry can carry a different
challenge. If the Python client exposes a pre-payment hook, apply the same
check there. If it does not, do not let it auto-pay — read the 402 yourself and
sign the amount you checked.

Pin the network to `eip155:8453` rather than a wildcard like `eip155:*`. A wildcard lets the client auto-pay on whatever chain a server advertises, which is exactly the wrong behavior when an agent is spending unattended.

## 3. Manual signing sketch

Only needed if you cannot use a library:

1. Build an EIP-3009 `TransferWithAuthorization` for `asset`, `payTo`, and `amount`.
2. Sign it with EIP-712 using domain `{ name: extra.name, version: extra.version, chainId: 8453, verifyingContract: asset }`.
3. Assemble the x402 v2 payment payload: `{ x402Version: 2, scheme: "exact", network, payload: { signature, authorization } }`.
4. Base64-encode it and send it as `PAYMENT-SIGNATURE` on the same URL, same body.

Success is `200` with `{"account": {...}, "token": "..."}` and a `PAYMENT-RESPONSE` header containing settlement metadata. Keep the `PAYMENT-RESPONSE` value or the settlement tx hash: it is the only proof of purchase and the input to recovery. Write the token straight to a file with mode `0600`; do not echo the response into a transcript or log.

## 4. Never pay twice

- A `502` means the payment settled but provisioning failed. **Do not resend.** The payment is already on-chain.
- A broadcast transfer may wait for confirmations. Confirmation is retried server-side; polling continues on the buyer side.
- If a token was lost after a settled payment, recover it (below) rather than purchasing again.
- If a recovery attempt fails with `502 recovery_unavailable`, retry later — it is explicitly safe.

## 5. Credential recovery (token lost)

```bash
# message to sign (EIP-191 personal_sign), no trailing newline:
x402socks credential recovery v1
tx_hash: 0xSETTLEMENT_TX_HASH
issued_at: 1792000000
```

Then:

```bash
curl -sS -X POST https://payments.x402socks.com/v1/access/recover \
  -H 'content-type: application/json' \
  -d '{"transaction":"0x...","signature":"0x...","issued_at":1792000000}'
```

The signing wallet must be the wallet that paid. `issued_at` must be within ±10 minutes of now. The original `PAYMENT-SIGNATURE` is deliberately rejected: it is public settlement calldata that anyone could replay.

Recovery returns a replacement token once. Save it to the `0600` token file and
print only the non-secret fields; `scripts/x402socks.sh recover` does this for
you.

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

`scripts/x402socks.sh recover-message <tx_hash>` prints a correctly formatted message with a fresh timestamp.
