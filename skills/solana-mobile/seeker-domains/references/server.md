# Server implementation reference

Express implementation of `.skr` resolution. Adapt the routing to whatever framework the project
already uses — see [Other frameworks](#other-frameworks). The resolution logic itself is
framework-agnostic.

`.skr` names live on Solana **mainnet**, whatever cluster the app targets.

This uses the Kit resolver from [kit-resolver.md](kit-resolver.md), which is the default. For the
`@onsol/tldparser` route, see [the section below](#onsoltldparser-alternative).

## Full Express code

```typescript
// backend/src/index.ts
import express, { Request, Response } from 'express';
import { address, createSolanaRpc, type Address } from '@solana/kit';
import cors from 'cors';
import { normalizeSkrName, resolveSkrDomain, resolveSkrNames } from './skr';

const app = express();
const PORT = Number(process.env.PORT ?? 3000);

// Public endpoints are rate-limited and will not survive resolving a list view. Point this at
// a dedicated provider in production, and keep the key server-side. The reverse route needs
// getProgramAccounts, which some providers disable — check before deploying.
const RPC_ENDPOINT = process.env.SOLANA_MAINNET_RPC_URL ?? 'https://api.mainnet-beta.solana.com';

// Build the RPC client once at module scope, not per request.
const rpc = createSolanaRpc(RPC_ENDPOINT);

app.use(cors());
app.use(express.json());

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

// Resolve .skr domain to wallet address
app.post('/api/resolve-domain', async (req: Request, res: Response) => {
  const { domain } = req.body;

  if (!domain || typeof domain !== 'string') {
    return res.status(400).json({ error: 'Domain name is required' });
  }

  // Reject malformed input before spending RPC quota on it.
  if (!normalizeSkrName(domain)) {
    return res.status(400).json({ error: 'Not a valid .skr domain' });
  }

  try {
    const owner = await resolveSkrDomain(rpc, domain);

    // null is a genuine "not registered". A throw means the RPC failed — see below.
    if (!owner) {
      return res.status(404).json({ error: 'Domain not found' });
    }

    res.json({ address: owner });
  } catch (error) {
    console.error('RPC failure resolving domain:', error);
    res.status(503).json({ error: 'Resolution temporarily unavailable' });
  }
});

// Reverse lookup: resolve wallet address to .skr domain
app.post('/api/resolve-address', async (req: Request, res: Response) => {
  const { address: input } = req.body;

  if (!input || typeof input !== 'string') {
    return res.status(400).json({ error: 'Wallet address is required' });
  }

  // address() throws on malformed base58, so validate separately from the RPC call to keep
  // bad input a 400 rather than a 503.
  let owner: Address;
  try {
    owner = address(input);
  } catch {
    return res.status(400).json({ error: 'Invalid wallet address' });
  }

  try {
    const domains = await resolveSkrNames(rpc, owner);

    if (domains.length === 0) {
      return res.status(404).json({ error: 'No .skr domain found for this address' });
    }

    // Already sorted, so this is stable across calls for multi-domain owners.
    res.json({ domain: domains[0] });
  } catch (error) {
    console.error('RPC failure resolving address:', error);
    res.status(503).json({ error: 'Resolution temporarily unavailable' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
```

## Package Configuration

```json
{
  "name": "skr-backend",
  "version": "1.0.0",
  "scripts": {
    "dev": "ts-node src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@noble/hashes": "^1.8.0",
    "@solana/kit": "^8.0.0",
    "cors": "^2.8.5",
    "express": "^4.21.0"
  },
  "devDependencies": {
    "@types/cors": "^2.8.17",
    "@types/express": "^5.0.0",
    "@types/node": "^22.10.2",
    "ts-node": "^10.9.2",
    "typescript": "^5.7.2"
  }
}
```

## TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

## Key implementation notes

1. **RPC endpoint**: the public mainnet endpoint is fine for development. It will not survive a
   list view that resolves many addresses — use a dedicated provider in production and keep the
   key in server-side environment variables only.

2. **Forward lookup**: `resolveSkrDomain` accepts `alice.skr` or `alice`, and returns `null` when
   the name is unregistered. Validate with `normalizeSkrName` first so malformed input is a 400
   rather than a wasted RPC round trip.

3. **Reverse lookup**: `resolveSkrNames` returns **all** `.skr` names owned by an address, sorted.
   Take `[0]` for a display name; the sort is what keeps it stable between calls. It relies on
   `getProgramAccounts`, which some providers restrict — verify yours supports it.

4. **Error handling**: 400 for invalid input, 404 for a genuine "no domain registered", 503 for
   RPC failures. The resolver makes this easy: `null` is not-found, a rejected promise is an
   outage. Do not collapse RPC failures into 404 — an outage would then look like every user
   having no name.

5. **Cache**: names change rarely. A short-TTL in-memory cache, keyed on the address or name,
   removes most repeated RPC calls — this is the main reason to proxy rather than resolve from
   the client.

6. **CORS**: open CORS is for local development. Restrict `origin` to known callers before
   deploying.

## Other frameworks

Only the routing changes; the resolver calls are identical.

| Framework | Where the routes go |
| --- | --- |
| Fastify | `fastify.post('/api/resolve-domain', handler)` |
| NestJS | A controller plus an injectable service holding the RPC client |
| Hono | `app.post('/api/resolve-domain', handler)` |
| Koa | Router middleware |
| Next.js | Route handlers at `app/api/resolve-domain/route.ts` |

Construct the RPC client **once** at module scope, not per request. Building it per request adds
latency and, on some providers, trips connection limits.

## @onsol/tldparser alternative

Use the SDK when you need ANS features the Kit resolver does not implement — records, avatars, or
a user's `MainDomain`. For plain forward and reverse resolution the helper is less trouble.

Pin the current major. The skill previously pinned `^0.6.7`, which still installs but is two
majors behind what `npm install @onsol/tldparser` gives you:

```json
{
  "dependencies": {
    "@onsol/tldparser": "^1.2.1",
    "@solana/web3.js": "^1.98.4"
  }
}
```

```typescript
import { TldParser } from '@onsol/tldparser';
import { Connection, PublicKey } from '@solana/web3.js';

const connection = new Connection(RPC_ENDPOINT, 'confirmed');
const parser = new TldParser(connection);

// Forward — pass the FULL domain. A bare 'alice' throws.
try {
  const owner = await parser.getOwnerFromDomainTld('alice.skr');
  res.json({ address: owner.toBase58() });
} catch {
  // Unregistered and malformed are indistinguishable here; both throw the same TypeError.
  res.status(404).json({ error: 'Domain not found' });
}

// Reverse — TLD without the leading dot. '.skr' silently returns [].
const domains = await parser.getParsedAllUserDomainsFromTld(publicKey, 'skr');
// domains[n].domain already includes the suffix, e.g. 'alice.skr'.
const sorted = domains.map((d) => d.domain).sort();
```

Behaviour verified against mainnet on 1.2.1, and identical on 0.6.7 — the full-domain
requirement is not a recent API change:

- **`getOwnerFromDomainTld` requires the full domain.** It splits the argument on `.` and treats
  the second segment as the TLD, so `'alice'` derives a name account under the TLD `.undefined`.
- **It throws rather than returning null.** `getNameOwner` dereferences `.owner` on a name record
  it never checked for `undefined`, so any account it cannot fetch — unregistered name, typo,
  bare label — raises `TypeError: Cannot read properties of undefined (reading 'owner')`. There
  is no falsy-return path to branch on.
- **To distinguish not-found from bad input**, call `getNameRecordFromDomainTld(domain)`. It
  returns `undefined` for a missing account instead of throwing, so you can validate first and
  keep genuine RPC errors mapped to a 503.
- **`getMainDomain` throws when the user has never set a main domain**, which is the common case.
  It is not a null-returning lookup either.

### The ESM build is broken

`dist/esm/index.js` uses extensionless relative imports (`from './parsers'`), which Node's ESM
resolver rejects:

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '.../dist/esm/parsers'
  imported from .../dist/esm/index.js
```

The CJS build is fine, so any ESM project (`"type": "module"`) has to reach for it explicitly:

```typescript
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { TldParser } = require('@onsol/tldparser');
```

A bundler that resolves extensionless paths will paper over this; plain Node will not. The Kit
resolver has no such problem, which is one more reason it is the default.
