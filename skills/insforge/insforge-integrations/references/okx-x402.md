
# InsForge + OKX x402 Payments Integration Guide

OKX acts as the **x402 facilitator** for the x402 HTTP payment protocol. Your server returns `402 Payment Required` with a challenge; the client signs an EIP-3009 `TransferWithAuthorization`; the server forwards the signed payload to OKX's `/verify` and `/settle` endpoints. USDG on X Layer settles with zero gas (OKX pays the gas). Payment records and realtime dashboards live in InsForge.

## Key packages

- `@insforge/sdk` — InsForge client for DB writes, AI calls, and realtime subscription
- `viem` — EIP-712 typed data signing + chain switching on the client
- No x402 SDK is required; the facilitator is plain REST

## Recommended Workflow

Each step below maps 1:1 to an agent prompt. Run them in order — each step produces concrete files with a verification checkpoint before moving on.

```text
1. Schema & Realtime           → migrations/db_init.sql + db import
2. Server Primitives & Env     → lib/okx-facilitator.ts, lib/x402.ts, lib/insforge.ts, .env
3. Paid Endpoint & Aggregate   → app/api/report + app/api/payments (AI content generator)
4. Client Libs & Consumer Flow → lib/x402-client.ts (incl. chain switch) + fetch→sign→retry state machine
5. Realtime Dashboard          → SSR from /api/payments + subscribe x402_payments + try-it + report view
6. Diagnostics & Go-Live       → scripts/check-domain.mjs, scripts/check-usdg.mjs, MOCK off, first real payment
```

## Prerequisites (manual, cannot be automated)

### OKX Web3 API credentials

- Go to [OKX Onchain OS Dev Portal](https://web3.okx.com/onchainos/dev-portal) and connect your wallet
- Create a project, then link email + phone (required to enable API key creation)
- Create API Key → save **API Key**, **Secret Key**, and the **passphrase** you set (secret shown only once)
- **Do NOT reuse an OKX exchange trading API key** — it returns `Invalid Authority` (code 50114). The Web3 API is a separate system at `web3.okx.com/onchainos/dev-portal`, not `okx.com/account/my-api`

### Payment recipient wallet

- Any EVM address on X Layer (chainId 196) works as the payee
- If using OKX Wallet, copy the **0x-prefixed** address (not the `XKO...` native format)
- Fund the **paying** wallet (not the recipient) with USDG on X Layer for real settlements — OKX facilitator covers gas

### InsForge project

- Create via `npx -y @insforge/cli create` or link via `npx -y @insforge/cli link --project-id <id>`
- Get **URL**, **Anon Key**, and **Service Role Key** from dashboard → Project Settings → API Keys

## Chain + Asset constants (X Layer)

| Constant | Value |
|----------|-------|
| Chain ID | `196` (hex `0xc4`) |
| CAIP-2 network | `eip155:196` |
| USDG contract | `0x4ae46a509f6b1d9056937ba4500cb143933d2dc8` |
| EIP-712 domain name | `Global Dollar` (NOT `"USDG"`) |
| EIP-712 domain version | `1` (NOT `"2"`) |
| Decimals | 6 |
| RPC | `https://rpc.xlayer.tech` |

**Domain name/version are the most common source of `Invalid Authority` errors.** Always run `scripts/check-domain.mjs` (Step 6) before the first real payment to confirm against the on-chain `DOMAIN_SEPARATOR`.

## Explorer URLs by chain

Render the tx hash in the dashboard as a link so users can verify on-chain:

| Chain (stored in `payments.chain`) | Explorer tx URL pattern |
|---|---|
| `xlayer` | `https://www.okx.com/web3/explorer/xlayer/tx/{hash}` |
| `base` | `https://basescan.org/tx/{hash}` |
| `optimism` | `https://optimistic.etherscan.io/tx/{hash}` |
| `arbitrum` | `https://arbiscan.io/tx/{hash}` |

```typescript
// src/lib/explorer.ts
const EXPLORERS: Record<string, string> = {
  xlayer: "https://www.okx.com/web3/explorer/xlayer/tx/",
  base: "https://basescan.org/tx/",
  optimism: "https://optimistic.etherscan.io/tx/",
  arbitrum: "https://arbiscan.io/tx/",
};
export function txUrl(chain: string | null, hash: string) {
  return (EXPLORERS[chain ?? "xlayer"] ?? EXPLORERS.xlayer) + hash;
}
```

## Environment variables

| Variable | Source | Used by |
|----------|--------|---------|
| `OKX_API_KEY` | OKX Onchain OS Dev Portal (Web3 API, NOT exchange API) | server |
| `OKX_SECRET_KEY` | OKX Onchain OS Dev Portal | server |
| `OKX_PASSPHRASE` | Chosen by you when creating the API key | server |
| `PAYMENT_RECIPIENT` | Your EVM wallet address on X Layer (`0x...`) | server |
| `NEXT_PUBLIC_INSFORGE_URL` | InsForge Dashboard → Project Settings | client + server |
| `NEXT_PUBLIC_INSFORGE_ANON_KEY` | InsForge Dashboard → Project Settings | client |
| `INSFORGE_SERVICE_KEY` | InsForge Dashboard → Project Settings (server-only) | server |
| `OPENROUTER_API_KEY` | InsForge Dashboard → Model Gateway → Overview | server |
| `MOCK_OKX_FACILITATOR` | `true` for local/demo; unset or `false` for production | server |
| `NEXT_PUBLIC_MOCK_OKX_FACILITATOR` | Mirror of `MOCK_OKX_FACILITATOR` if you want the UI to show a "mock mode" badge | client |

**Mock mode contract:** `MOCK_OKX_FACILITATOR=true` skips real on-chain verify/settle on the server and returns a random tx hash. The client-side signing flow **does not change** — the browser still prompts the wallet for a real signature. This keeps the UX identical to production; only the server-side on-chain calls are mocked. Never set `MOCK_OKX_FACILITATOR=true` in production.

---

# Step 1 — Schema & Realtime

Create a single-file migration and apply it with `db import`. This is idempotent and works for both first-time setup and re-runs in fresh environments.

```sql
-- migrations/db_init.sql

-- 1. Payment ledger
create table if not exists x402_payments (
  id uuid default gen_random_uuid() primary key,
  payer_address text not null,
  endpoint text not null,
  amount text not null,            -- smallest unit (6-decimal)
  tx_hash text not null unique,    -- UNIQUE prevents duplicate settlement records from retries
  chain text default 'xlayer',
  status text default 'settled',
  response_summary text,
  created_at timestamptz default now()
);

create index if not exists idx_x402_payments_payer on x402_payments (payer_address);
create index if not exists idx_x402_payments_created on x402_payments (created_at desc);

-- 2. RLS: public can read the ledger; writes come from the service key only
alter table x402_payments enable row level security;
drop policy if exists public_read on x402_payments;
create policy public_read on x402_payments for select using (true);

-- 3. Realtime channel
insert into realtime.channels (pattern, description, enabled)
values ('x402_payments', 'Payment events for dashboard', true)
on conflict do nothing;

-- 4. Trigger: publish every INSERT to the realtime channel
create or replace function notify_x402_payment()
returns trigger as $$
begin
  perform realtime.publish(
    'x402_payments',
    'INSERT_x402_payments',
    jsonb_build_object('new', row_to_json(new))
  );
  return new;
end;
$$ language plpgsql security definer
set search_path = pg_catalog, public, realtime;

drop trigger if exists x402_payment_realtime on x402_payments;
create trigger x402_payment_realtime
  after insert on x402_payments
  for each row
  execute function notify_x402_payment();
```

Apply:

```bash
npx -y @insforge/cli db import migrations/db_init.sql
```

**✓ Verify**

```bash
npx -y @insforge/cli db query "select count(*) from x402_payments" --json
# → rowCount: 1, count: "0"

npx -y @insforge/cli db query "select pattern, enabled from realtime.channels where pattern = 'x402_payments'" --json
# → enabled: true

npx -y @insforge/cli db query "select tgname from pg_trigger where tgrelid = 'x402_payments'::regclass and not tgisinternal" --json
# → tgname: "x402_payment_realtime"
```

---

# Step 2 — Server Primitives & Env

Install deps and create three library files. These have zero coupling to your route handler; you reuse them from any endpoint you want to monetize.

```bash
npm install @insforge/sdk viem openai
```

**`src/lib/okx-facilitator.ts`** — OKX HMAC-signed calls to `/verify` and `/settle`, with a MOCK branch for local dev.

```typescript
import crypto from "crypto";

const OKX_BASE = "https://web3.okx.com/api/v6/x402";
const MOCK = process.env.MOCK_OKX_FACILITATOR === "true";

function signOKX(timestamp: string, method: string, path: string, body: string) {
  return crypto
    .createHmac("sha256", process.env.OKX_SECRET_KEY!)
    .update(timestamp + method + path + body)
    .digest("base64");
}

function okxHeaders(method: string, path: string, body: string): Record<string, string> {
  const timestamp = new Date().toISOString();
  return {
    "OK-ACCESS-KEY": process.env.OKX_API_KEY!,
    "OK-ACCESS-SIGN": signOKX(timestamp, method, path, body),
    "OK-ACCESS-PASSPHRASE": process.env.OKX_PASSPHRASE!,
    "OK-ACCESS-TIMESTAMP": timestamp,
    "Content-Type": "application/json",
  };
}

export async function verifyPayment(paymentPayload: unknown, paymentRequirements: unknown) {
  if (MOCK) return { isValid: true, payer: (paymentPayload as any)?.payload?.authorization?.from };
  const path = "/api/v6/x402/verify";
  const body = JSON.stringify({ x402Version: 1, chainIndex: "196", paymentPayload, paymentRequirements });
  const res = await fetch(OKX_BASE + "/verify", { method: "POST", headers: okxHeaders("POST", path, body), body });
  const json = await res.json();
  return json.data?.[0] ?? { isValid: false, invalidReason: json.msg ?? "unknown" };
}

export async function settlePayment(paymentPayload: unknown, paymentRequirements: unknown) {
  if (MOCK) {
    const payer = (paymentPayload as any)?.payload?.authorization?.from;
    return { success: true, txHash: "0x" + crypto.randomBytes(32).toString("hex"), payer };
  }
  const path = "/api/v6/x402/settle";
  const body = JSON.stringify({ x402Version: 1, chainIndex: "196", syncSettle: true, paymentPayload, paymentRequirements });
  const res = await fetch(OKX_BASE + "/settle", { method: "POST", headers: okxHeaders("POST", path, body), body });
  const json = await res.json();
  return json.data?.[0] ?? { success: false, errorReason: json.msg ?? "unknown" };
}
```

**`src/lib/x402.ts`** — challenge builder, 402 response, header codecs. All wire-format concerns live here.

```typescript
const ASSET = "0x4ae46a509f6b1d9056937ba4500cb143933d2dc8"; // USDG on X Layer

export function buildPaymentRequirements(endpointUrl: string) {
  return {
    scheme: "exact",
    maxAmountRequired: "1",        // 0.000001 USDG (6 decimals, smallest unit)
    resource: endpointUrl,
    description: "Premium API endpoint",
    mimeType: "application/json",
    payTo: process.env.PAYMENT_RECIPIENT ?? "0x0000000000000000000000000000000000000000",
    maxTimeoutSeconds: 300,
    asset: ASSET,
    extra: { name: "Global Dollar", version: "1" }, // EIP-712 domain — verify with scripts/check-domain.mjs
  };
}

export function build402Response(paymentRequirements: ReturnType<typeof buildPaymentRequirements>) {
  const challenge = { x402Version: 1, accepts: [{ network: "eip155:196", ...paymentRequirements }] };
  return new Response(JSON.stringify({ error: "Payment required" }), {
    status: 402,
    headers: {
      "Content-Type": "application/json",
      "PAYMENT-REQUIRED": Buffer.from(JSON.stringify(challenge)).toString("base64"),
    },
  });
}

export function decodePaymentSignature(header: string) {
  return JSON.parse(Buffer.from(header, "base64").toString("utf-8"));
}

export function buildPaymentResponseHeader(settlement: { txHash: string; payer: string }) {
  return Buffer.from(JSON.stringify({
    success: true,
    transaction: settlement.txHash,
    network: "eip155:196",
    payer: settlement.payer,
  })).toString("base64");
}
```

**`src/lib/insforge.ts`** — one file exports both clients so you don't instantiate the SDK twice.

```typescript
import { createClient } from "@insforge/sdk";

// Server-side: full-privilege client for DB writes, AI calls, aggregate queries
export function createServiceClient() {
  return createClient({
    baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL!,
    anonKey: process.env.INSFORGE_SERVICE_KEY!, // service key goes through the anonKey slot (Bearer token)
  });
}

// Browser-side: anon client for reads (RLS-protected) and realtime subscriptions
export function createBrowserClient() {
  return createClient({
    baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL!,
    anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY!,
  });
}
```

**`.env`** — template with every required variable. Copy from `.env.example` and fill in.

```env
# OKX Web3 API (Step 1 of prerequisites)
OKX_API_KEY=
OKX_SECRET_KEY=
OKX_PASSPHRASE=

# Payee wallet on X Layer
PAYMENT_RECIPIENT=0x

# InsForge (dashboard → Project Settings → API Keys)
NEXT_PUBLIC_INSFORGE_URL=
NEXT_PUBLIC_INSFORGE_ANON_KEY=
INSFORGE_SERVICE_KEY=

# Model Gateway (dashboard → Model Gateway → Overview → Active OpenRouter key)
OPENROUTER_API_KEY=

# Demo mode — server skips on-chain calls, client still signs normally
MOCK_OKX_FACILITATOR=true
NEXT_PUBLIC_MOCK_OKX_FACILITATOR=true
```

**✓ Verify**

This check uses Node 20+ `--env-file` support.

```bash
node --env-file=.env -e "['OKX_API_KEY','OKX_SECRET_KEY','OKX_PASSPHRASE','PAYMENT_RECIPIENT','NEXT_PUBLIC_INSFORGE_URL','NEXT_PUBLIC_INSFORGE_ANON_KEY','INSFORGE_SERVICE_KEY','OPENROUTER_API_KEY'].forEach(k => console.log(k, process.env[k] ? 'ok' : 'MISSING'))"
# → every row 'ok'
```

---

# Step 3 — Paid Endpoint & Aggregate API

Two server routes:

1. **`POST /api/report`** — the payment-gated endpoint. Gates the response behind 402, verifies + settles, records the payment, then **generates real paid content** (an AI-written crypto market report).
2. **`GET /api/payments`** — dashboard backend. Returns recent rows + aggregate stats using the service key. The dashboard uses this for SSR / initial load so the first paint doesn't wait for the WebSocket.

**Paid content shape** — the consumer expects this JSON:

```typescript
{
  report: {
    title: string;
    generated_at: string;   // ISO timestamp
    model: string;          // e.g. "anthropic/claude-sonnet-4.5"
    assets: Array<{ symbol: string; price: number; change_24h: number; signal: "bullish" | "bearish" | "neutral" }>;
    analysis: string;       // markdown
  },
  payment: { tx_hash: string; payer: string; amount: string }
}
```

**`src/app/api/report/route.ts`**

```typescript
import { NextRequest } from "next/server";
import OpenAI from "openai";
import { verifyPayment, settlePayment } from "@/lib/okx-facilitator";
import { createServiceClient } from "@/lib/insforge";
import {
  buildPaymentRequirements,
  build402Response,
  decodePaymentSignature,
  buildPaymentResponseHeader,
} from "@/lib/x402";

interface Asset {
  symbol: string;
  price: number;
  change_24h: number;
  signal: "bullish" | "bearish" | "neutral";
}

function generateMarketSnapshot(): Asset[] {
  const rand = (min: number, max: number) => +(min + Math.random() * (max - min)).toFixed(2);
  const signals: Asset["signal"][] = ["bullish", "bearish", "neutral"];
  const pick = <T,>(arr: T[]) => arr[Math.floor(Math.random() * arr.length)];
  return [
    { symbol: "BTC", price: rand(83000, 86000), change_24h: rand(-3, 5), signal: pick(signals) },
    { symbol: "ETH", price: rand(1600, 1750), change_24h: rand(-4, 4), signal: pick(signals) },
    { symbol: "SOL", price: rand(125, 155), change_24h: rand(-3, 7), signal: pick(signals) },
    { symbol: "AVAX", price: rand(20, 28), change_24h: rand(-5, 6), signal: pick(signals) },
    { symbol: "LINK", price: rand(14, 18), change_24h: rand(-4, 5), signal: pick(signals) },
  ];
}

async function generateAIReport(assets: Asset[]): Promise<string> {
  const openai = new OpenAI({
    baseURL: "https://openrouter.ai/api/v1",
    apiKey: process.env.OPENROUTER_API_KEY,
  });
  const marketTable = assets
    .map((a) => `- ${a.symbol}: $${a.price.toFixed(2)} (${a.change_24h > 0 ? "+" : ""}${a.change_24h}% 24h, signal: ${a.signal})`)
    .join("\n");

  const prompt = `You are a crypto market analyst. Write a concise professional market report in markdown based on the following 24h snapshot. Keep it under 250 words.

Snapshot:
${marketTable}

Structure your response as:
## Market Overview
2-3 sentences on overall sentiment and flow.

## Key Movers
Brief commentary on the most notable assets (1-2 lines each).

## Signal Summary
One-line actionable takeaway.

Output ONLY the markdown. No preamble, no disclaimers.`;

  try {
    const completion = await openai.chat.completions.create({
      model: "anthropic/claude-sonnet-4.5",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 600,
    });
    return completion.choices[0]?.message?.content ?? "_AI response was empty._";
  } catch (err) {
    console.error("[AI] generation failed:", err);
    return "_AI service unavailable — falling back to raw data._";
  }
}

export async function POST(req: NextRequest) {
  const baseUrl = `${req.nextUrl.protocol}//${req.nextUrl.host}`;
  const paymentRequirements = buildPaymentRequirements(`${baseUrl}/api/report`);

  const paymentSigHeader = req.headers.get("PAYMENT-SIGNATURE");
  if (!paymentSigHeader) return build402Response(paymentRequirements);

  let paymentPayload: unknown;
  try {
    paymentPayload = decodePaymentSignature(paymentSigHeader);
  } catch {
    return Response.json({ error: "Invalid payment signature encoding" }, { status: 400 });
  }

  const verification = await verifyPayment(paymentPayload, paymentRequirements);
  if (!verification.isValid) {
    return Response.json({ error: "Payment invalid", reason: verification.invalidReason }, { status: 402 });
  }

  const settlement = await settlePayment(paymentPayload, paymentRequirements);
  if (!settlement.success) {
    return Response.json({ error: "Settlement failed", reason: settlement.errorReason }, { status: 500 });
  }

  // Record payment — ALWAYS check the error; settlement already moved money on-chain.
  const insforge = createServiceClient();
  const { error: insertError } = await insforge.database.from("x402_payments").insert([{
    payer_address: settlement.payer,
    endpoint: "/api/report",
    amount: paymentRequirements.maxAmountRequired,
    tx_hash: settlement.txHash,
    status: "settled",
    response_summary: "Crypto Market Analysis report",
  }]);
  if (insertError) console.error("[payment-log] insert failed:", insertError, "tx:", settlement.txHash);

  // Generate and return paid content
  const assets = generateMarketSnapshot();
  const analysis = await generateAIReport(assets);
  const report = {
    title: "Crypto Market Analysis",
    generated_at: new Date().toISOString(),
    model: "anthropic/claude-sonnet-4.5",
    assets,
    analysis,
  };

  return Response.json(
    { report, payment: { tx_hash: settlement.txHash, payer: settlement.payer, amount: "0.000001 USDG" } },
    { status: 200, headers: { "PAYMENT-RESPONSE": buildPaymentResponseHeader(settlement) } }
  );
}
```

**`src/app/api/payments/route.ts`** — SSR / initial load feeder for the dashboard.

```typescript
import { createServiceClient } from "@/lib/insforge";

export async function GET() {
  const insforge = createServiceClient();

  const { data: payments, error } = await insforge.database
    .from("x402_payments")
    .select()
    .order("created_at", { ascending: false })
    .limit(50);
  if (error) return Response.json({ error: error.message }, { status: 500 });

  const { data: allPayments, error: statsError } = await insforge.database
    .from("x402_payments")
    .select("amount");
  if (statsError) return Response.json({ error: statsError.message }, { status: 500 });

  const totalRequests = allPayments?.length ?? 0;
  const totalRevenue = (allPayments ?? []).reduce(
    (sum: number, p: { amount: string }) => sum + Number(p.amount),
    0
  );

  return Response.json({
    payments: payments ?? [],
    stats: { totalRequests, totalRevenue, latestPayment: payments?.[0]?.created_at ?? null },
  });
}
```

**✓ Verify** (with `MOCK_OKX_FACILITATOR=true`, server running):

```bash
# Expect 402 + PAYMENT-REQUIRED header
curl -sS -i -X POST http://localhost:3000/api/report | head -5

# Craft a fake payload, then expect 200 + paid content + DB row
PAYLOAD='{"x402Version":1,"scheme":"exact","network":"eip155:196","payload":{"signature":"0xdeadbeef","authorization":{"from":"0x1111111111111111111111111111111111111111","to":"'"$PAYMENT_RECIPIENT"'","value":"1","validAfter":"0","validBefore":"9999999999","nonce":"0x'"$(openssl rand -hex 32)"'"}}}'
SIG=$(printf '%s' "$PAYLOAD" | base64)
curl -sS -X POST -H "PAYMENT-SIGNATURE: $SIG" http://localhost:3000/api/report | head -c 400

# Aggregates
curl -sS http://localhost:3000/api/payments
# → { "payments": [...], "stats": { "totalRequests": 1, "totalRevenue": 1, ... } }
```

---

# Step 4 — Client Libs & Consumer Flow

Client-side wallet signing (`x402-client.ts`) **with complete X Layer chain switching** plus the fetch → sign → retry state machine every consumer component uses.

**`src/lib/x402-client.ts`**

```typescript
import { createWalletClient, custom, hexToBigInt, type WalletClient, type Address } from "viem";

const X_LAYER_CHAIN = {
  id: 196,
  name: "X Layer",
  nativeCurrency: { name: "OKB", symbol: "OKB", decimals: 18 },
  rpcUrls: { default: { http: ["https://rpc.xlayer.tech"] } },
} as const;

const EIP3009_TYPES = {
  TransferWithAuthorization: [
    { name: "from", type: "address" },
    { name: "to", type: "address" },
    { name: "value", type: "uint256" },
    { name: "validAfter", type: "uint256" },
    { name: "validBefore", type: "uint256" },
    { name: "nonce", type: "bytes32" },
  ],
} as const;

interface PaymentChallenge {
  x402Version: number;
  accepts: Array<{
    network: string;
    scheme: string;
    maxAmountRequired: string;
    resource: string;
    description: string;
    payTo: string;
    maxTimeoutSeconds: number;
    asset: string;
    extra: { name: string; version: string };
  }>;
}

export function decodeChallenge(base64Header: string): PaymentChallenge {
  return JSON.parse(atob(base64Header));
}

export async function connectWallet(): Promise<WalletClient> {
  if (!window.ethereum) throw new Error("NO_WALLET");

  const client = createWalletClient({ chain: X_LAYER_CHAIN, transport: custom(window.ethereum) });
  await client.requestAddresses();

  // Switch to X Layer if not already on it — otherwise signature verification will fail
  const chainId = await client.getChainId();
  if (chainId !== 196) {
    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: "0xc4" }], // 196 in hex
      });
    } catch (switchError: unknown) {
      // 4902 = chain not added to wallet yet
      if (
        typeof switchError === "object" &&
        switchError !== null &&
        "code" in switchError &&
        (switchError as { code: number }).code === 4902
      ) {
        await window.ethereum.request({
          method: "wallet_addEthereumChain",
          params: [{
            chainId: "0xc4",
            chainName: "X Layer",
            nativeCurrency: { name: "OKB", symbol: "OKB", decimals: 18 },
            rpcUrls: ["https://rpc.xlayer.tech"],
            blockExplorerUrls: ["https://www.okx.com/web3/explorer/xlayer"],
          }],
        });
      } else {
        throw switchError;
      }
    }
  }

  return client;
}

export async function signPayment(challenge: PaymentChallenge, walletClient: WalletClient): Promise<string> {
  const accept = challenge.accepts[0];
  if (!accept) throw new Error("Invalid challenge: accepts array is empty");
  const [account] = await walletClient.getAddresses();

  const nonceBytes = crypto.getRandomValues(new Uint8Array(32));
  const nonce = ("0x" + Array.from(nonceBytes).map((b) => b.toString(16).padStart(2, "0")).join("")) as `0x${string}`;
  const validBefore = BigInt(Math.floor(Date.now() / 1000) + accept.maxTimeoutSeconds);

  const authorization = {
    from: account,
    to: accept.payTo as Address,
    value: hexToBigInt(("0x" + BigInt(accept.maxAmountRequired).toString(16)) as `0x${string}`),
    validAfter: BigInt(0),
    validBefore,
    nonce,
  };

  const signature = await walletClient.signTypedData({
    account,
    domain: {
      name: accept.extra.name,          // "Global Dollar"
      version: accept.extra.version,    // "1"
      chainId: 196,
      verifyingContract: accept.asset as Address,
    },
    types: EIP3009_TYPES,
    primaryType: "TransferWithAuthorization",
    message: authorization,
  });

  const paymentPayload = {
    x402Version: challenge.x402Version,
    scheme: accept.scheme,
    network: accept.network,
    payload: {
      signature,
      authorization: {
        from: account,
        to: accept.payTo,
        value: accept.maxAmountRequired,
        validAfter: "0",
        validBefore: validBefore.toString(),
        nonce,
      },
    },
  };

  return btoa(JSON.stringify(paymentPayload));
}
```

**Consumer state machine** — the pattern any "Try it" / "Pay" button implements. React-style reducer shown here; port to your framework as needed.

```typescript
type FlowState =
  | { step: "idle" }
  | { step: "loading" }                                          // initial fetch
  | { step: "payment_required"; challengeHeader: string; body: unknown }   // got 402
  | { step: "signing" }                                          // wallet prompt open
  | { step: "done"; status: number; body: unknown }              // success (or non-402 error)
  | { step: "error"; message: string };

// 1. Initial call — no payment header
async function tryEndpoint(path: string, setFlow: (s: FlowState) => void) {
  setFlow({ step: "loading" });
  const res = await fetch(path, { method: "POST" });
  const body = await res.json();
  if (res.status === 402) {
    const challengeHeader = res.headers.get("payment-required");
    if (!challengeHeader) return setFlow({ step: "error", message: "Missing challenge header" });
    setFlow({ step: "payment_required", challengeHeader, body });
  } else {
    setFlow({ step: "done", status: res.status, body });
  }
}

// 2. User confirms payment → connect wallet → sign → retry with PAYMENT-SIGNATURE
async function confirmPayment(path: string, challengeHeader: string, walletRef: { current: WalletClient | null }, setFlow: (s: FlowState) => void) {
  setFlow({ step: "signing" });
  try {
    if (!walletRef.current) walletRef.current = await connectWallet();
    const challenge = decodeChallenge(challengeHeader);
    const paymentSignature = await signPayment(challenge, walletRef.current);

    setFlow({ step: "loading" });
    const res = await fetch(path, {
      method: "POST",
      headers: { "PAYMENT-SIGNATURE": paymentSignature },
    });
    setFlow({ step: "done", status: res.status, body: await res.json() });
  } catch (err) {
    walletRef.current = null; // reset on failure so next attempt re-prompts
    const msg = err instanceof Error && err.message === "NO_WALLET"
      ? "Please install MetaMask or OKX Wallet"
      : `Payment failed: ${err instanceof Error ? err.message : String(err)}`;
    setFlow({ step: "error", message: msg });
  }
}
```

Key details:
- Cache the `WalletClient` in a ref so the user isn't prompted to reconnect on every retry. Reset it on any failure.
- The `payment-required` header is case-insensitive on the fetch response (HTTP is case-insensitive), but send as `PAYMENT-SIGNATURE` on retries to match what the server's `req.headers.get("PAYMENT-SIGNATURE")` looks for.
- In **mock mode**, the client flow is identical — wallet still prompts for a real EIP-3009 signature. Only the server skips the on-chain calls.

**✓ Verify** — open the try-it UI (Step 5) in a browser and click the button; the wallet should prompt for a signature on X Layer, and a new row should appear in `x402_payments`.

---

# Step 5 — Realtime Dashboard

The dashboard combines three feeds into one UI:

1. **Initial data** — fetched once from `GET /api/payments` (gives stats + last 50 rows without waiting for WebSocket)
2. **Realtime stream** — subscribe to the `x402_payments` channel, listen for `INSERT_x402_payments`, merge into state
3. **Try-it playground** — the consumer state machine from Step 4, renders the paid `report` on success

**Browser SDK singleton** (avoid creating multiple WebSocket clients):

```typescript
// src/lib/insforge-browser.ts
"use client";
import { createBrowserClient } from "@/lib/insforge";
import type { InsForgeClient } from "@insforge/sdk";

let cached: InsForgeClient | null = null;
export function getBrowserClient(): InsForgeClient {
  if (!cached) cached = createBrowserClient();
  return cached;
}
```

**Realtime subscription pattern:**

```typescript
"use client";
import { useEffect, useState } from "react";
import { getBrowserClient } from "@/lib/insforge-browser";

type Payment = { id: string; payer_address: string; endpoint: string; amount: string; tx_hash: string; chain: string | null; status: string | null; created_at: string };

export function usePayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [stats, setStats] = useState<{ totalRequests: number; totalRevenue: number; latestPayment: string | null } | null>(null);
  const insforge = getBrowserClient();

  useEffect(() => {
    // 1. Initial load from aggregate route (no WS latency for first paint)
    fetch("/api/payments").then((r) => r.json()).then((data) => {
      setPayments(data.payments ?? []);
      setStats(data.stats ?? null);
    });

    // 2. Realtime stream
    const onInsert = (payload: { new?: Payment }) => {
      if (!payload?.new?.id) return;
      setPayments((prev) => prev.some((p) => p.id === payload.new!.id) ? prev : [payload.new!, ...prev].slice(0, 50));
      setStats((s) => s ? { ...s, totalRequests: s.totalRequests + 1, totalRevenue: s.totalRevenue + Number(payload.new!.amount), latestPayment: payload.new!.created_at } : s);
    };
    insforge.realtime.on("INSERT_x402_payments", onInsert);

    insforge.realtime.connect()
      .then(() => insforge.realtime.subscribe("x402_payments"))
      .catch(console.error);

    return () => {
      insforge.realtime.off("INSERT_x402_payments", onInsert);
      insforge.realtime.unsubscribe("x402_payments");
    };
  }, [insforge]);

  return { payments, stats };
}
```

**UI composition** (framework-agnostic outline — see [demo source](https://github.com/InsForge/insforge-integration/tree/main/payment/okx-x402/src/components) for complete Tailwind components):

```tsx
<Dashboard>
  <FlowSteps />              // 4-step visual: Request → Sign → Settle → Deliver
  <ApiPlayground>            // Uses Step 4 state machine
    <Endpoint card + Try it button>
    {flow.step === "payment_required" && <ConfirmPaymentButton />}
    {flow.step === "done" && <ReportView body={flow.body} />}
  </ApiPlayground>
  <StatsCards stats={stats} />     // Total Requests / Total Revenue / Latest
  <PaymentLog payments={payments}> // Live table, flash on insert
    <tr>
      <td>{timeAgo(p.created_at)}</td>
      <td>{shortAddr(p.payer_address)}</td>
      <td><a href={txUrl(p.chain, p.tx_hash)} target="_blank" rel="noopener noreferrer">{shortAddr(p.tx_hash)}</a></td>  {/* Step 0: Explorer URLs */}
      <td>{formatAmount(p.amount)}</td>
    </tr>
  </PaymentLog>
</Dashboard>
```

**ReportView** — renders the paid content from `POST /api/report`:

```typescript
import ReactMarkdown from "react-markdown";

export function ReportView({ body }: { body: { report: any; payment: any } }) {
  const { report, payment } = body;
  return (
    <div>
      <h2>{report.title}</h2>
      <p>Generated at {report.generated_at} by {report.model}</p>
      <table>
        {report.assets.map((a: any) => (
          <tr key={a.symbol}>
            <td>{a.symbol}</td>
            <td>${a.price.toFixed(2)}</td>
            <td>{a.change_24h > 0 ? "+" : ""}{a.change_24h}%</td>
            <td>{a.signal}</td>
          </tr>
        ))}
      </table>
      <ReactMarkdown>{report.analysis}</ReactMarkdown>
      <p>
        Paid <strong>{payment.amount}</strong> · tx{" "}
        <a href={txUrl("xlayer", payment.tx_hash)} target="_blank" rel="noopener noreferrer">{payment.tx_hash.slice(0, 10)}…</a>
      </p>
    </div>
  );
}
```

**✓ Verify**

1. Open the dashboard — stats + recent rows should populate within one second (from `/api/payments`).
2. Click **Try it** → wallet prompts → confirm signature → response renders the AI-generated report + tx link.
3. The new row should **flash into the live log without a page refresh** (realtime trigger working).
4. Open a second browser tab with the dashboard; trigger a payment in one — the other tab should update live.

---

# Step 6 — Diagnostics & Go-Live

Before removing `MOCK_OKX_FACILITATOR=true` and accepting real payments, run both diagnostic scripts to confirm your EIP-712 domain and your USDG contract assumptions match on-chain reality. These catch 90% of first-deploy `Invalid Authority` errors.

**`scripts/check-domain.mjs`** — compute `DOMAIN_SEPARATOR` for candidate `(name, version)` pairs and compare against the on-chain value.

```javascript
import { keccak256, encodeAbiParameters, stringToBytes } from "viem";

const USDG = "0x4ae46a509f6b1d9056937ba4500cb143933d2dc8";
const CHAIN_ID = 196;
// Read from chain with check-usdg.mjs first, then paste here:
const ON_CHAIN_DOMAIN = "0x415f0706e345fcaf25d5be24c4fd7830d0054fc5742c51a0db9319c759bd3743";

const DOMAIN_TYPEHASH = keccak256(
  stringToBytes("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
);

function computeDomain(name, version) {
  return keccak256(
    encodeAbiParameters(
      [{ type: "bytes32" }, { type: "bytes32" }, { type: "bytes32" }, { type: "uint256" }, { type: "address" }],
      [DOMAIN_TYPEHASH, keccak256(stringToBytes(name)), keccak256(stringToBytes(version)), BigInt(CHAIN_ID), USDG]
    )
  );
}

const candidates = [
  ["Global Dollar", "1"], ["Global Dollar", "2"], ["Global Dollar", "v1"], ["Global Dollar", "v2"],
  ["USDG", "1"], ["USDG", "2"],
];

for (const [name, version] of candidates) {
  const hash = computeDomain(name, version);
  console.log(`${hash === ON_CHAIN_DOMAIN ? "✓" : "✗"} name="${name}" version="${version}" → ${hash}`);
}
console.log("On-chain:", ON_CHAIN_DOMAIN);
```

**`scripts/check-usdg.mjs`** — read `name()`, `version()`, `DOMAIN_SEPARATOR()`, and `eip712Domain()` directly from the USDG contract. Use the output of `DOMAIN_SEPARATOR` to populate `ON_CHAIN_DOMAIN` in `check-domain.mjs`.

```javascript
import { createPublicClient, http } from "viem";

const RPCS = [
  "https://rpc.xlayer.tech",
  "https://xlayerrpc.okx.com",
  "https://rpc.ankr.com/xlayer",
  "https://xlayer-rpc.publicnode.com",
];

let client;
for (const rpc of RPCS) {
  try {
    const c = createPublicClient({ transport: http(rpc) });
    await c.getChainId();
    client = c;
    console.log("Using RPC:", rpc);
    break;
  } catch {
    console.log("Failed:", rpc);
  }
}
if (!client) { console.error("No RPC reachable"); process.exit(1); }

const USDG = "0x4ae46a509f6b1d9056937ba4500cb143933d2dc8";
const abi = [
  { name: "name", type: "function", stateMutability: "view", inputs: [], outputs: [{ type: "string" }] },
  { name: "version", type: "function", stateMutability: "view", inputs: [], outputs: [{ type: "string" }] },
  { name: "DOMAIN_SEPARATOR", type: "function", stateMutability: "view", inputs: [], outputs: [{ type: "bytes32" }] },
  { name: "eip712Domain", type: "function", stateMutability: "view", inputs: [], outputs: [
    { name: "fields", type: "bytes1" }, { name: "name", type: "string" }, { name: "version", type: "string" },
    { name: "chainId", type: "uint256" }, { name: "verifyingContract", type: "address" },
    { name: "salt", type: "bytes32" }, { name: "extensions", type: "uint256[]" },
  ]},
];

async function tryRead(fnName) {
  try {
    const result = await client.readContract({ address: USDG, abi, functionName: fnName });
    console.log(`✓ ${fnName}:`, result);
  } catch (e) {
    console.log(`✗ ${fnName}:`, e.shortMessage || e.message?.slice(0, 200));
  }
}

await tryRead("name");
await tryRead("version");
await tryRead("DOMAIN_SEPARATOR");
await tryRead("eip712Domain");
```

Run:

```bash
node scripts/check-usdg.mjs
# → name: "Global Dollar", version: "1", DOMAIN_SEPARATOR: 0x415f…3743

node scripts/check-domain.mjs
# → ✓ name="Global Dollar" version="1" → 0x415f…3743 (match)
```

## Go-live checklist

- [ ] `scripts/check-usdg.mjs` prints expected `name` / `version` / `DOMAIN_SEPARATOR`
- [ ] `scripts/check-domain.mjs` shows **exactly one `✓`** — the pair you have in `buildPaymentRequirements.extra`
- [ ] `MOCK_OKX_FACILITATOR` unset (or `false`) in prod env
- [ ] `NEXT_PUBLIC_MOCK_OKX_FACILITATOR` unset on client too (no misleading "mock" badge in prod)
- [ ] Paying wallet funded with USDG on X Layer (payer pays USDG; OKX facilitator covers gas)
- [ ] `PAYMENT_RECIPIENT` is a 0x-prefixed EVM address (not XKO... native format)
- [ ] Make one real payment end-to-end: wallet prompts → settles → row in `x402_payments` → tx hash resolves on `okx.com/web3/explorer/xlayer/tx/{hash}`
- [ ] Monitor `postgres.logs` and app logs for `[payment-log] insert failed` — this means money moved but the record is lost; reconcile manually

---

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| ❌ Using OKX exchange trading API key | ✅ Create a separate Web3 API key at `web3.okx.com/onchainos/dev-portal` |
| ❌ EIP-712 domain `name: "USDG"` / `version: "2"` | ✅ Run `scripts/check-domain.mjs`; correct values are `name: "Global Dollar"`, `version: "1"` |
| ❌ Missing `chainIndex: "196"` on `/verify` | ✅ Both `/verify` and `/settle` require `chainIndex` (else `50014 chainIndex not empty or should be numeric`) |
| ❌ Wallet on Ethereum mainnet when user clicks pay | ✅ `connectWallet()` must call `wallet_switchEthereumChain` → fallback to `wallet_addEthereumChain` on error 4902 |
| ❌ Ignoring result of `insert(...)` after settlement | ✅ Always check `{ error }` — settlement already took money; a silent DB failure loses the record |
| ❌ `tx_hash text not null` without UNIQUE | ✅ Add `UNIQUE` to prevent duplicate records from retries |
| ❌ Hardcoding `xlayer` in explorer URL | ✅ Use `payment.chain` column + `txUrl()` helper for multi-chain support |
| ❌ `MOCK_OKX_FACILITATOR=true` in production | ✅ Demo mode only — removes on-chain guarantee; always unset in prod |
| ❌ Dashboard loads empty then pops | ✅ SSR initial data from `/api/payments` before subscribing to realtime |
| ❌ Creating multiple `createClient` instances in the browser | ✅ Singleton via `getBrowserClient()` — otherwise duplicate WebSocket connections |
| ❌ Forgetting RLS on `x402_payments` | ✅ Enable RLS + `public_read` SELECT policy; writes go through service key which bypasses RLS |
