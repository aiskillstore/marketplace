---
name: near-dapp
description: >
  Build NEAR Protocol dApps. Use for: (1) creating new NEAR dApps with
  `create-near-app` (Vite+React, Next.js), (2) adding NEAR wallet connection
  to existing apps with `@hot-labs/near-connect` and `near-connect-hooks`,
  (3) building frontend UI for NEAR smart contracts, (4) integrating wallet
  sign-in/sign-out, contract calls, and transaction signing into web
  applications.
---

# NEAR dApp

## Decision Router

Determine which path to follow:

### Path A: New Project

User wants to create a new NEAR dApp from scratch.

1. Read [references/create-near-app.md](references/create-near-app.md)
2. Run scaffolding:

```bash
npx create-near-app@latest
```

Or with arguments:

```bash
npx create-near-app my-app --frontend vite-react --contract rs --install
```

**Framework options:** `vite-react` | `next-app` | `next-page`
**Contract options:** `rs` (Rust) | `ts` (TypeScript)

3. If user needs wallet connection in the scaffolded app, also follow Path B.

### Path B: Existing Project

User wants to add NEAR wallet connection to an existing React app.

1. Read [references/near-connect-hooks.md](references/near-connect-hooks.md) — React hooks API and patterns
2. If user needs low-level wallet API or non-React integration, also read [references/near-connect.md](references/near-connect.md)

**Quick setup:**

```bash
npm install near-connect-hooks @hot-labs/near-connect near-api-js
```

```tsx
// 1. Wrap app root with NearProvider
import { NearProvider } from 'near-connect-hooks';

<NearProvider config={{ network: 'mainnet' }}>
  <App />
</NearProvider>

// 2. Use hook in components
import { useNearWallet } from 'near-connect-hooks';

const { signedAccountId, signIn, signOut, viewFunction, callFunction } = useNearWallet();
```

### Path C: Non-React or Vanilla JS

Use `@hot-labs/near-connect` directly without React hooks.

1. Read [references/near-connect.md](references/near-connect.md)

```bash
npm install @hot-labs/near-connect
```

```typescript
import { NearConnector } from "@hot-labs/near-connect";

const connector = new NearConnector({ network: "mainnet" });
connector.on("wallet:signIn", async (t) => {
  const wallet = await connector.wallet();
  const address = t.accounts[0].accountId;
});
await connector.connect();
```

## Key Patterns

- **Read contract state** (no wallet): `viewFunction({ contractId, method, args })`
- **Write to contract** (wallet required): `callFunction({ contractId, method, args, deposit })`
- **Transfer NEAR**: `transfer({ receiverId, amount })`
- **NEAR ↔ yoctoNEAR**: Use `nearToYocto()` / `yoctoToNear()` from `near-api-js`
- **1 NEAR** = `"1000000000000000000000000"` yoctoNEAR
- **Default gas**: `"30000000000000"` (30 TGas)
