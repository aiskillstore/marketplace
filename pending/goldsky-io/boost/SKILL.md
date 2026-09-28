---
name: boost
description: "Use this skill whenever the user wants to cut their RPC bill, or asks about Goldsky Boost — the free CDN that sits in front of an RPC endpoint they already pay for, serving cacheable reads from Goldsky's indexed data and forwarding everything else to their own provider unchanged. Triggers on: 'Boost', 'goldsky boost', 'edge.goldsky.com/boost', 'cut my RPC bill', 'reduce RPC costs', 'lower my Alchemy/QuickNode/Infura bill', 'cache my RPC calls', 'RPC caching proxy', 'CDN in front of my RPC', 'x-cache HIT', 'x-edge-billable', 'x-edge-source', 'connect my QuickNode/Alchemy account to Goldsky', 'boost upstream/provider', 'why is my cache hit rate low', 'why does eth_getLogs still forward', 'boost verification' / 'verified organization'. Also use it when a user is paying a third-party RPC provider and wants to spend less without migrating off them — Boost is the answer that keeps their provider, keys, and behavior intact. Boost and Edge are different products on the same host: Boost fronts the provider the user ALREADY has (free, bring-your-own upstream), while Edge is Goldsky's own managed RPC they'd buy instead (/edge). If the user wants to replace their provider rather than reduce its bill, use /edge. Do NOT trigger on Turbo, Mirror, Subgraph, or Compose questions — those have their own skills."
---

# Goldsky Boost

Boost is a CDN in front of the RPC endpoint the user already pays for. Every request is checked against Goldsky's indexed data first: if Boost has the answer it serves it, and the provider never sees the call (so never bills for it). If it doesn't, the request forwards to the user's endpoint unchanged and the response comes back verbatim.

**Boost is free.** CDN hits and forwarded requests both cost nothing from Goldsky. That shapes how to talk about it: there is no upsell here, and the only number that matters to the user is how much of their *existing provider bill* disappears.

## The mental model that prevents most mistakes

Three facts explain nearly every question users have:

1. **An API key *is* a Boost endpoint.** Configuration lives on the key, not in the request. The key in the URL is how Boost knows which upstream to forward to. The user's own provider URL never travels with a request.
2. **A project has exactly one Boost.** There are no named Boost endpoints to create or list. If you find yourself reaching for `goldsky boost create` or `goldsky boost list`, those commands do not exist — see [Command surface](#command-surface).
3. **Boost never guesses about the head of the chain.** Block tags always forward. This is the single most common "why didn't it cache?" question and the answer is deliberate design, not a bug.

## Endpoint format

```
https://edge.goldsky.com/boost/{chain}?key={GOLDSKY_API_KEY}
```

`{chain}` is a chain name or a chain ID, case-insensitive — `/boost/ethereum` and `/boost/1` are the same endpoint.

`?key=` is required on every request, and the two ways it can fail look different. Both verified against production:

| Request | Response | Means |
| --- | --- | --- |
| no `?key=`, `?key=` empty, or `?KEY=` (the name is **case-sensitive**) | `401`, empty body | the edge never resolved a key at all |
| `?key=<something unrecognised>` | `404` + `{"error":{"code":-32000,"message":"no Boost configuration for this key"}}` | a key was read, but it carries no Boost config |

That split is the fastest diagnostic you have: an **empty-body 401 is a malformed URL** (missing, blank, or misnamed param — check for an unset env var interpolating to nothing), while a **JSON 404 is a real key pointed at the wrong project or a Boost that was never enabled**.

The docs page says a keyless caller gets an x402 payment challenge. That is Edge's behaviour on `/standard/evm/...`, which does return `402` with a large JSON body. `/boost/...` never does. A real x402 challenge is loud, so an empty body is itself proof this isn't one — and telling a user to expect a payment challenge sends them hunting for a billing problem that cannot exist on a free product.

The key also disambiguates auth headers — see [Sending the provider's own auth](#sending-the-providers-own-auth).

### The drop-in swap

The whole value proposition is that nothing else changes. Show the user this, not a migration guide:

```typescript
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

const client = createPublicClient({
  chain: mainnet,
  transport: http('https://edge.goldsky.com/boost/ethereum?key=YOUR_KEY'),
})
```

Same methods, same params, same response shapes.

### Verifying it works

```bash
curl -i "https://edge.goldsky.com/boost/ethereum?key=YOUR_KEY" \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":["0x1b4",false]}'
```

**Run it twice.** The first call for a block Boost hasn't served recently can come back `MISS` while the reader warms that range from storage. A user who tests once and sees `MISS` will conclude Boost is broken — tell them to repeat before they draw that conclusion.

## What the CDN serves

| Method | Served from the CDN when |
| --- | --- |
| `eth_getBlockByNumber` | the block is a concrete hex height |
| `eth_getBlockByHash` | always eligible |
| `eth_getTransactionByHash` | always eligible |
| `eth_getTransactionReceipt` | always eligible |
| `eth_getLogs` | `fromBlock` and `toBlock` are concrete hex heights, or `blockHash` is set |
| `eth_getBlockReceipts` | the block is a concrete hex height |

`eth_chainId` and `net_version` are answered at the edge without touching either backend.

**Everything else forwards, free.** Writes, traces, `eth_call`, `eth_getBalance` — all passthrough. Eligible is not guaranteed: a method in this table still forwards if Boost doesn't hold that specific data yet.

### Block tags always forward

A request for `latest`, `pending`, `safe`, `finalized`, or `earliest` is never served from the CDN. Goldsky's view of the head can trail the user's provider by a block or two, so serving `latest` would occasionally hand back a stale or soon-reorged block. The user's endpoint is the authority on the head.

The same applies to `eth_getLogs` with a tag as a range bound — which is why a user who ranges `fromBlock: "0x..."` to `toBlock: "latest"` sees a 0% hit rate. Pin `toBlock` to a concrete height and the CDN engages.

This is the highest-leverage thing to check when someone reports a low hit rate.

## Reading the response headers

| Header | Values | Meaning |
| --- | --- | --- |
| `x-cache` | `HIT`, `MISS` | whether Boost served it or forwarded it |
| `x-edge-source` | `cache`, `static`, `endpoint` | who actually answered |
| `x-edge-billable` | integer | how many items Boost served. The name predates Boost being free — it is a count, not a charge |
| `x-edge-duration-ms` | integer | wall-clock time Boost spent serving it |
| `x-edge-region` | AWS region | which edge region served it |
| `x-edge-version` | build string | the Boost build that served it |

`x-cache` is the one to graph — it's the standard CDN header, so existing tooling already understands it. Counting `HIT`s gives the exact number of calls the provider didn't bill for.

Every response header is readable from browser JavaScript (`Access-Control-Expose-Headers: *`).

## Batching

Boost serves a JSON-RPC batch **per item**: cacheable items come from the CDN, the rest forward to the provider in a single onward batch. Nothing to enable — post an array to the same address.

Two things that bite people:

- **`x-cache` is `HIT` only when *every* item was served.** A batch where 44 of 45 items came from the CDN still reports `MISS`. For batches, read `x-edge-billable` (the count of items served), not `x-cache`.
- **Arrays over 100 items forward whole**, as one free passthrough with no CDN lookups. Split larger batches into 100-item chunks to keep the hits.

Give every item a unique `id` — JSON-RPC doesn't guarantee response order, so match by `id`, not position.

## Supported networks

Boost offers only chains the CDN covers **from genesis**. A chain whose coverage starts at a later block is not offered at all, because the CDN would answer recent history and silently miss everything below the floor — the opposite of what Boost is for.

| Network | Path name | Chain ID |
| --- | --- | --- |
| Ethereum | `ethereum` | 1 |
| Base | `base` | 8453 |
| Polygon | `polygon` | 137 |
| Optimism | `optimism` | 10 |
| Avalanche | `avalanche` | 43114 |
| HyperEVM | `hyperevm` | 999 |
| Arc | `arc` | 5042 |
| Robinhood Chain | `robinhood` | 4663 |
| Ethereum Sepolia | `sepolia` | 11155111 |
| Base Sepolia | `base-sepolia` | 84532 |

Chains Goldsky indexes but does **not** offer for Boost today include Arbitrum, BNB Chain, Celo, Gnosis, Sei, Tron, Abstract and Monad — each is covered from a block well above genesis. If a user asks for one of those, that is the reason, and Edge (`/edge`) is the alternative.

`goldsky boost chains` is the live list and beats this table the day a backfill lands. Run it rather than asserting from memory.

## Command surface

**A project has one Boost, so no command takes a name.** Older docs describe `boost create <name>`, `list`, `pause`, `resume`, and `delete`; those were removed. If the user is following a page that shows them, that page is stale — the current shape is below, and `goldsky boost --help` settles any disagreement.

| Command | What it does |
| --- | --- |
| `goldsky boost enable` | enable the project's Boost; a first enable walks through provider setup |
| `goldsky boost disable` | stop serving, keep configuration and key |
| `goldsky boost get` | providers, serving URLs, and status per chain |
| `goldsky boost update` | `--allowed-domains`, `--provider-rate` |
| `goldsky boost reveal` | reveal the API key Boost serves under |
| `goldsky boost metrics` | JSON: hits, latencies, miss reasons, per-provider stats, savings |
| `goldsky boost requests` | per-request history: method, chain, hit or forward, which provider, duration |
| `goldsky boost chains` | chains Boost can cache, and how far back each is cached |
| `goldsky boost validate <url>` | probe a provider URL: detect its chain, check it answers |
| `goldsky boost set --chain <c>` | switch a chain on/off, set `--forward-timeout` / `--cache-timeout` |
| `goldsky boost provider …` | manage upstreams — see below |

Useful flags:

- `boost enable --chain <c> --provider-url <url> --header k:v` — one-shot setup that configures the first provider right after enabling.
- `boost metrics --from <iso> --to <iso> --bucket-size 1m|5m|1h|6h|1d --chain <c>`
- `boost requests --chain <c> --method eth_getLogs --errors --limit <n>` (pages of 50)
- `boost validate <url> --chain <c>` verifies the URL's chain matches what the user intends.

### Providers (upstreams)

| Command | Required flags |
| --- | --- |
| `boost provider connect` | `--vendor quicknode\|alchemy`, `--key`, repeatable `--chain` |
| `boost provider add` | `--chain`, `--url`, repeatable `--header k:v`, optional `--id` |
| `boost provider replace` | `--chain`, `--id`, `--url`, `--header`, `--clear-headers` |
| `boost provider activate` | `--chain`, `--id` |
| `boost provider remove` | `--chain`, `--id`, `--force` |
| `boost provider set` | `--chain`, `--id`, `--timeout`, `--vendor` |
| `boost provider disconnect` | `--vendor`, `--force` |

**Omit `--key` on `provider connect`.** The CLI prompts for it, which keeps the credential out of shell history. Never ask the user to paste a provider credential into the chat — the same rule as Goldsky tokens in `/auth-setup`.

Several upstreams can exist per chain, but only one is active. Failover is an explicit `provider activate`, not something Boost does silently — so if a user expects automatic failover, correct that expectation.

## Setting it up

Two paths. Ask which the user wants rather than assuming:

**Connect a provider account** — Boost creates the endpoints per chain.

| Vendor | Credential | What Boost creates |
| --- | --- | --- |
| QuickNode | an API key with **Admin API** access (Dashboard → API Keys). Paid plans only | one endpoint per chain, in their account |
| Alchemy | an **access key** with Admin API **App Management** read+write (Dashboard → Settings → Security). *Not* an app's API key | one app, allowlisted to the chosen chains |

Boost only touches what it created: disconnecting deletes those endpoints and nothing else.

**Or paste a URL** — any `https`-reachable endpoint, including a self-run node or Goldsky's own Edge RPC. Private, loopback, and link-local addresses are rejected.

Validate before committing:

```bash
goldsky boost validate https://my-provider.example/rpc --chain ethereum
```

## Verification gate

Turning Boost on and changing it afterwards requires a **verified organization**. A team qualifies automatically as soon as one member *above Viewer* has a business email address — a personal mailbox (`gmail.com`, `outlook.com`, `proton.me`) doesn't count. There's no form and no review; the check runs at the moment of the action, and approval is permanent.

What matters when a user hits this: **verification is a control-plane gate, not a runtime one.**

| Action | Needs verification |
| --- | --- |
| Enable Boost; connect/disconnect a provider; add, replace, activate, remove an upstream; switch a chain or change timeouts; reveal the API key | Yes |
| Read configuration, chains, and metrics | No |
| Disable or delete Boost | No |
| **Serving traffic on an endpoint that already exists** | **No** |

An already-configured endpoint keeps answering regardless of verification state. Nothing here can interrupt traffic a user is already serving — say that plainly, because "verification required" reads like an outage risk and isn't one.

The fix is usually adding a teammate with a business email, effective immediately. If that doesn't fit (shared domain, pre-setup evaluation, misclassified domain), point them at support@goldsky.com with their team ID from the dashboard URL. If verification can't be *checked* at all, the change is refused with a retry rather than a denial and no state is written.

## Sending the provider's own auth

Because the Goldsky key rides in the query string, `Authorization` and `X-API-Key` headers on the request are unambiguously the provider's, and forward untouched. This only works with `?key=` present — without it Boost can't tell whose credential an `Authorization` header is.

For a credential that never changes, prefer the endpoint's configured headers (`provider add --header k:v`): stored once, applied to every forward, and callers never hold them.

Credentials given as URL userinfo (`https://user:pass@…`) are converted to `Authorization: Basic` before the request leaves Goldsky. URLs and headers are stored encrypted at rest and never written to logs, errors, or metrics.

## Troubleshooting

Work down this list — it's ordered by how often each is the real cause.

| Symptom | Likely cause and fix |
| --- | --- |
| `401` with an empty body | No key resolved: `?key=` missing, empty, or misnamed (`?KEY=` fails — it is case-sensitive). Usually an unset env var interpolating to nothing. Not a billing problem; Boost is free. |
| `404` with `-32000 no Boost configuration for this key` | The key was read but has no Boost config — wrong project, or Boost never enabled. `goldsky boost get` to confirm, `goldsky boost reveal` for the right key. |
| Hit rate near zero | Block tags in the request. `latest`/`pending`/`safe`/`finalized`/`earliest` always forward, including as an `eth_getLogs` range bound. Pin to concrete hex heights. |
| First call is `MISS`, and the user stops there | The reader warms that range from storage. Repeat the call. |
| A large batch reports `MISS` despite obvious hits | For batches `x-cache` is `HIT` only if *every* item was served. Read `x-edge-billable`. Also check the array is ≤100 items — larger ones forward whole. |
| An eligible method still forwards | Boost doesn't hold that specific data yet. Eligible ≠ guaranteed; confirm with `boost requests --method <m>`, which shows the miss reason. |
| Requests on a chain are rejected | The chain has no active upstream, or is switched off. `goldsky boost get` shows status per chain; `boost set --chain <c> --enabled true` re-enables. |
| Chain isn't available at all | Boost only offers genesis-covered chains. Check `goldsky boost chains`; if absent, Edge (`/edge`) is the alternative. |
| A config change is refused | Verification gate. See above — and confirm existing traffic is unaffected. |
| Provider rejecting forwarded calls | There is **no fixed egress IP list** to allowlist; Boost forwards from Fargate tasks in `us-east-1`, `us-west-2`, `eu-central-1` with addresses that rotate. Authenticate Boost with a credential (endpoint URL or configured header) instead of allowlisting it. |
| Subscriptions don't work | Boost is HTTP-only, no WebSocket. Keep `eth_subscribe` / `wss://` pointed at the provider. |
| Browser calls blocked by CORS | Allowed domains are set on the endpoint (`boost update --allowed-domains`), not by the provider. Credentialed requests aren't permitted. |
| Rate limit questions | Boost's budget is Goldsky-managed and the API *refuses* a rate-limit budget sent for a Boost endpoint — unlike Edge. Unmetered within fair use. |

Start a real diagnosis with:

```bash
goldsky boost get                                  # per-chain status and active upstreams
goldsky boost requests --limit 50                  # what actually happened, with miss reasons
goldsky boost metrics --from <iso> --bucket-size 1h
```

## Header forwarding

On a forward, the provider receives the caller's headers plus any configured on the endpoint (configured ones win on a name clash). Boost withholds only what it manages: `X-ERPC-Secret-Token`, `Host`, `Content-Type`/`Accept` (pinned to `application/json`), `Content-Length`, `Accept-Encoding`/`Content-Encoding`, `Cookie`, `Proxy-Authorization`, and hop-by-hop headers. Trace context (`traceparent`, `tracestate`, `b3`, `baggage`), `User-Agent`, and custom `x-*` pass through.

`X-Forwarded-For` reaches the provider as a whole unmodified chain. **Read the last entry** — that's the address Goldsky's load balancer observed; earlier entries are caller-supplied and untrusted.

Coming back, the provider's `Cache-Control`, `Retry-After`, `ETag` and custom `x-*` ride through. Dropped: `Content-Encoding`, `Content-Type`, `Content-Length`, `Set-Cookie`, `Access-Control-*`, `x-cache`/`x-edge-*`, `x-goldsky-*`.

## Boost or Edge?

They share a host and are easy to confuse:

- **Boost** fronts the provider the user **already has**. Free, bring-your-own upstream, only genesis-covered chains, HTTP only. Use it to make an existing bill smaller.
- **Edge** (`/edge`) is Goldsky's **own** managed RPC, which they'd buy instead of a provider. Far more chains, configurable rate limits, hedging and failover.

"I want to spend less with Alchemy" → Boost. "I want to stop using Alchemy" → Edge. A user can also point Boost's upstream *at* Edge.

## Related

- Docs: https://docs.goldsky.com/boost — dashboard: https://app.goldsky.com/dashboard/edge/boost
- API: https://api.goldsky.com/api/v1/docs/#all/tag/boost (bearer token, project-scoped)
- `/edge` — Goldsky's managed RPC; `/auth-setup` — CLI login and project selection
- For CLI syntax, trust `goldsky boost --help` over any doc page.
