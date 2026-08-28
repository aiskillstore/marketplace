---
name: seeker-domains
description: Resolve and display .skr domain names in Solana mobile apps, in both directions between names and wallet addresses. Use when showing .skr names instead of wallet addresses in profiles, friend lists, or transaction history, resolving a .skr domain to an address, reverse-looking-up an address to a domain, or validating .skr input.
---

# .skr domain resolution

`.skr` domains are AllDomains names on Solana mainnet. Seeker users get one by default, which
makes them a good substitute for truncated addresses in a UI.

Two directions:

- **Forward** — `alice.skr` to a wallet address
- **Reverse** — a wallet address to the `.skr` names it owns

Both live on **mainnet**, regardless of which cluster the rest of the app targets. An app on
devnet still resolves names against mainnet.

## Decide where resolution runs

Resolution reads public on-chain data, so a client can do it directly. Proxy it through a
backend when you want:

- **RPC key protection.** A key in `EXPO_PUBLIC_*` is readable by anyone with the APK. If you
  use a paid RPC, it has to be server-side.
- **Shared caching.** Names change rarely. One server-side cache beats every client
  re-resolving the same addresses.
- **Batch lookups.** Resolving a whole friend list in one request beats N round trips from a
  phone.
- **`getProgramAccounts` access.** Reverse lookup needs it, and plenty of providers disable or
  heavily rate-limit the method. One server-side endpoint against a provider you have checked
  beats discovering the restriction on user devices.

Direct client-side resolution against a public RPC is reasonable for a prototype or a
low-traffic app. Public endpoints are rate-limited, so it will not survive a list view that
resolves dozens of addresses.

Ask which the user wants if it is not obvious from the project. Default to the proxy for
anything heading to production.

## Integrating with an existing backend

**Check what exists before writing a new server.** Adding an Express app beside someone's
NestJS service is a mess to maintain.

1. Look for backend dependencies in every `package.json` — `express`, `fastify`, `hono`,
   `@nestjs/core`, `koa`, or a Next.js app with API routes.
2. Look for entry points: `server.ts`, `app.ts`, `main.ts`, `index.ts`.
3. Look for route organisation: `routes/`, `api/`, `controllers/`.
4. Ask if it is still ambiguous — "I see a Fastify server in `apps/api`; should the `.skr`
   endpoints go there?"

Add routes to what exists, matching its conventions for routing, validation, and error
handling. Only scaffold a minimal server when there is genuinely no backend.

## Core resolution logic

Resolution is framework-agnostic; only the routing around it changes. Two options, and the
default is the first.

### Kit (default)

`.skr` names are AllDomains (ANS) accounts, and resolving one is a PDA derivation plus a single
account read — small enough to own outright rather than take an SDK for.

```bash
npm install @solana/kit @noble/hashes
```

```ts
import { address, createSolanaRpc } from '@solana/kit'
import { resolveSkrDomain, resolveSkrNames } from './skr'

// Always mainnet, whatever cluster the rest of the app targets.
const rpc = createSolanaRpc(process.env.SOLANA_MAINNET_RPC_URL)

const owner = await resolveSkrDomain(rpc, 'alice.skr') // Address, or null
const names = await resolveSkrNames(rpc, address('5FHw...')) // ['alice.skr'], sorted
```

Copy the implementation from [references/kit-resolver.md](references/kit-resolver.md) — about 140
lines, typechecked under `tsc --strict`, and free of `Buffer`/`TextEncoder`, so the same file runs
on a server and in React Native. It accepts `alice.skr` or `alice`, returns `null` for an
unregistered name, and only rejects when the RPC itself fails.

Reach for the SDK instead when you need ANS records, avatars, or a user's `MainDomain`, none of
which the helper implements.

### @onsol/tldparser (alternative)

```bash
npm install @onsol/tldparser @solana/web3.js
```

```ts
import { TldParser } from '@onsol/tldparser'
import { Connection } from '@solana/web3.js'

const connection = new Connection(process.env.SOLANA_MAINNET_RPC_URL, 'confirmed')
const parser = new TldParser(connection)

// Forward: pass the FULL domain, including the .skr suffix.
const owner = await parser.getOwnerFromDomainTld('alice.skr')

// Reverse: TLD without the leading dot. Returns [{ nameAccount, domain: 'alice.skr' }].
const domains = await parser.getParsedAllUserDomainsFromTld(publicKey, 'skr')
```

Four things to get right, all verified against mainnet on 1.2.1:

- **`getOwnerFromDomainTld` needs the full domain.** `'alice.skr'` resolves; `'alice'` throws.
  It splits on `.` and uses the second segment as the TLD, so a bare name derives a PDA under
  the TLD `.undefined` and finds nothing.
- **It throws instead of returning null, and an unregistered name is indistinguishable from
  malformed input** — both surface as `TypeError: Cannot read properties of undefined (reading
  'owner')`, because the SDK dereferences a name record it never null-checked. Wrap every call
  in `try`/`catch`; never branch on a falsy return. To tell the two apart, call
  `getNameRecordFromDomainTld(domain)`, which returns `undefined` cleanly for a missing account.
- **`getParsedAllUserDomainsFromTld` wants the TLD without a dot.** `'skr'` works; `'.skr'`
  silently returns `[]`. The `domain` field of each result already includes the suffix.
- **Reverse lookup returns an array.** An address can own several `.skr` names, and the order is
  not a ranking. Sort and take the first, or the displayed name will change between calls.

Its ESM build is also broken — see
[references/server.md](references/server.md#onsoltldparser-alternative) for that and the
`createRequire` workaround.

## API shape

Two endpoints, adapted to whatever framework is in use:

| Route | Body | Success | Not found |
| --- | --- | --- | --- |
| `POST /api/resolve-domain` | `{ domain: "alice.skr" }` | `{ address }` | 404 |
| `POST /api/resolve-address` | `{ address: "5FHw..." }` | `{ domain }` | 404 |

Validate input before touching RPC: reject a malformed base58 address or a domain that does
not end in `.skr` with a 400, so bad input does not consume RPC quota.

Distinguish "no domain registered" (404) from "RPC failed" (503). Collapsing both into 404
makes an outage look like every user having no name.

Full Express implementation, plus notes for Fastify, NestJS, Hono, and Next.js route
handlers: [references/server.md](references/server.md).

## Client integration

```ts
const { data: domain } = useResolveAddress(account?.address)
const label = domain ?? ellipsify(account?.address)
```

Always fall back to a truncated address. A name that fails to resolve should degrade to
something usable, never to a blank space or a spinner that never resolves.

Cache results — `@tanstack/react-query` with a long `staleTime` is enough, since names change
rarely.

For an Android emulator, `localhost` is the emulator itself. Reach the host machine at
`http://10.0.2.2:3000`. On a physical device use the host's LAN IP. Hard-coding either into
source is what breaks the app for the next person — read it from
`EXPO_PUBLIC_API_URL`.

The snippet above assumes the proxy. If you resolve directly from the app instead, the Kit
resolver runs unchanged under Hermes — call it from the same hook in place of `fetch`.

Hook, components, and the truncation helper: [references/client.md](references/client.md).

## Reference material

- [references/kit-resolver.md](references/kit-resolver.md) — the default resolver, how `.skr`
  names are stored on chain, and what the helper deliberately leaves out
- [references/server.md](references/server.md) — Express implementation, other frameworks,
  validation and error handling
- [references/client.md](references/client.md) — resolution hook, display components,
  emulator networking

## Related skills

- `solana-mobile-wallet` — the wallet connection supplying the address to resolve
- `seeker-genesis-token` — verifying Seeker ownership

## Links

- AllDomains developer guide: https://docs.alldomains.id/protocol/developer-guide/ad-sdks/svm-sdks/solana-mainnet-sdk
- `@onsol/tldparser`: https://www.npmjs.com/package/@onsol/tldparser
- `@onsol/tldparser` source, for the account layouts: https://github.com/onsol-labs/tld-parser
- `@solana/kit`: https://www.npmjs.com/package/@solana/kit
