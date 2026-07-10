---
name: Privy
description: Use when building wallet infrastructure, authenticating users, managing embedded wallets, configuring access controls and policies, or integrating blockchain transactions into applications. Reach for this skill when working with user onboarding, wallet creation, transaction signing, policy enforcement, or API integration across Ethereum, Solana, and other blockchains.
metadata:
    mintlify-proj: privy
    version: "1.0"
---

# Privy Skill

## Product summary

Privy is a wallet infrastructure and authentication platform that enables developers to embed wallets and user authentication into applications. It provides client-side SDKs (React, React Native, Swift, Android, Flutter, Unity) for user-facing features and server-side SDKs (Node.js, Go, Java, Rust, Ruby) for backend wallet management. Key entry points: **REST API** at `https://api.privy.io/v1/`, **PrivyProvider** component for React apps, **PrivyClient** for backend operations. Configuration happens in the Privy Dashboard at `https://dashboard.privy.io/`. The primary documentation is at https://docs.privy.io.

## When to use

Use Privy when:
- Building user authentication flows with email, SMS, social logins, passkeys, or wallet-based auth
- Creating embedded wallets for users (self-custodial, non-custodial, or custodial models)
- Sending transactions on Ethereum, Solana, Tempo, Bitcoin, Tron, Sui, or other blockchains
- Implementing wallet access controls with owners, signers, and policies
- Managing multi-party approval workflows or quorum-based signing
- Tracking wallet balances, transactions, and asset movements
- Setting up gas sponsorship, onramps/offramps, or yield earning
- Building trading apps, treasury management, agent wallets, or fintech applications
- Integrating with external wallets (MetaMask, Phantom, Rainbow, etc.)

## Quick reference

### Core concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| **User** | Unified identity across auth methods and wallets | Email + MetaMask linked to same user |
| **Embedded wallet** | Privy-managed wallet secured by key splitting | User wallet created on login |
| **Owner** | Entity with full control over a wallet | User, authorization key, or key quorum |
| **Signer** | Party with scoped permissions to sign transactions | Server automation, delegated access |
| **Policy** | Rules constraining wallet actions (amounts, recipients, contracts) | Max $1000 per transfer, approved recipients only |
| **Intent** | Proposed action awaiting approval (manual or quorum) | Transfer request pending team approval |

### SDK setup

**React/Next.js:**
```tsx
import {PrivyProvider} from '@privy-io/react-auth';

<PrivyProvider appId="your-app-id" clientId="your-client-id" config={{...}}>
  {children}
</PrivyProvider>
```

**Node.js:**
```ts
import {PrivyClient} from '@privy-io/node';
const privy = new PrivyClient({appId: 'your-app-id', appSecret: 'your-app-secret'});
```

**REST API:**
```bash
curl -X POST https://api.privy.io/v1/wallets \
  -H "Authorization: Basic <base64(appId:appSecret)>" \
  -H "privy-app-id: your-app-id"
```

### Key files and configuration

| Item | Location | Purpose |
|------|----------|---------|
| App ID & Secret | Privy Dashboard > Apps | API authentication credentials |
| Webhook signing secret | Dashboard > Configuration > Webhooks | Verify webhook payloads |
| App clients | Dashboard > Apps > App Clients | Environment-specific configuration |
| Login methods | Dashboard > Configuration > Login Methods | Enable email, SMS, OAuth, wallets, etc. |
| Policies | Dashboard or API | Define wallet action constraints |

### Common API endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/wallets` | POST | Create wallet |
| `/v1/wallets/{id}` | GET | Fetch wallet details |
| `/v1/wallets/{id}/ethereum/eth_sendTransaction` | POST | Send EVM transaction |
| `/v1/wallets/{id}/solana/signAndSendTransaction` | POST | Send Solana transaction |
| `/v1/users` | POST | Create user |
| `/v1/users/{id}` | GET | Fetch user |
| `/v1/policies` | POST | Create policy |
| `/v1/intents` | GET/POST | Fetch or create intents |

## Decision guidance

### When to use embedded vs. external wallets

| Scenario | Embedded | External |
|----------|----------|----------|
| New users without wallets | ✓ | ✗ |
| Users bringing existing wallets | ✗ | ✓ |
| Full control over UX | ✓ | ✗ |
| User controls keys directly | ✗ | ✓ |
| Seamless onboarding | ✓ | ✗ |
| Leverage existing balances | ✗ | ✓ |

### When to use Privy auth vs. JWT-based auth

| Scenario | Privy Auth | JWT-based |
|----------|-----------|-----------|
| No existing auth system | ✓ | ✗ |
| Multiple login methods needed | ✓ | ✓ |
| Existing auth provider (Auth0, Firebase) | ✗ | ✓ |
| Want Privy to manage sessions | ✓ | ✗ |
| Custom auth system | ✗ | ✓ |

### When to use client-side vs. server-side wallets

| Scenario | Client-side | Server-side |
|----------|------------|------------|
| User-controlled wallets | ✓ | ✗ |
| Application-owned wallets | ✗ | ✓ |
| Automated trading/agents | ✗ | ✓ |
| Consumer app | ✓ | ✗ |
| Treasury/business wallets | ✗ | ✓ |
| User signs transactions | ✓ | ✗ |

## Workflow

### 1. Set up your Privy app
- Create account at https://dashboard.privy.io/
- Create a new app in the Dashboard
- Copy your App ID and App Secret
- Configure login methods (email, SMS, OAuth, wallets, etc.)
- Set up app clients for different environments if needed

### 2. Initialize Privy in your application
- **For React:** Wrap your app with `PrivyProvider` at the root
- **For backend:** Instantiate `PrivyClient` with appId and appSecret
- **For REST:** Store credentials securely (environment variables)
- Wait for `ready` state before consuming Privy hooks/state

### 3. Authenticate users
- Use `useLoginWithEmail()`, `useLoginWithWallet()`, or other login hooks (React)
- Or call `/v1/users` to create users server-side
- Link multiple auth methods to same user if needed
- Retrieve user object with linked accounts and wallets

### 4. Create or fetch wallets
- **Client-side:** Configure `embeddedWallets.createOnLogin` in PrivyProvider config
- **Server-side:** Call `privy.wallets().create({chain_type: 'ethereum'})` or POST to `/v1/wallets`
- Specify owner (user ID, authorization key, or key quorum)
- Optionally set initial policies

### 5. Configure controls and policies
- Define owners and signers for the wallet
- Create policies with rules and conditions to constrain actions
- Use Dashboard or API to set up policies
- Test policy evaluation before production

### 6. Execute transactions
- **Client-side:** Use `useSendTransaction()` hook or sign methods
- **Server-side:** Call `privy.wallets().ethereum().sendTransaction()` or equivalent
- Provide transaction details (to, value, chain_id, etc.)
- Handle policy evaluation and approval flows

### 7. Monitor and react to events
- Set up webhooks in Dashboard > Configuration > Webhooks
- Verify webhook signatures using SDK or manual verification
- Subscribe to user, wallet, transaction, and intent events
- Update your backend state based on webhook payloads

## Common gotchas

- **Policy defaults to DENY:** If a wallet has a policy, you must explicitly allow every RPC method or wallet action it will use. Missing rules are denied by default.
- **Wallet ID vs. address:** Use wallet `id` (UUID) for API calls, not the wallet address. Address is for on-chain identification only.
- **Chain ID format:** Use CAIP-2 format for chain IDs (e.g., `eip155:1` for Ethereum mainnet, `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` for Solana).
- **Numeric values in wei/lamports:** Policy conditions and transaction values are evaluated exactly as passed—no automatic conversion. ETH is in wei, SOL in lamports, USDC in microdollars.
- **Webhook verification required:** Always verify webhook signatures before trusting the payload. Use `privy.webhooks().verify()` or manual verification.
- **Rate limits (HTTP 429):** Implement exponential backoff retry logic. Privy rate limits REST endpoints for fair usage.
- **Ready state not checked:** Don't use Privy hooks before `ready === true` in React. State may be stale or undefined.
- **Missing app client ID:** If deploying across multiple domains, configure app clients in the Dashboard and pass `clientId` to PrivyProvider.
- **Policy evaluation in TEE:** Policies are evaluated in secure enclaves—you cannot inspect or modify policy logic at runtime.
- **Idempotency keys:** Use idempotency keys for critical operations (wallet creation, transactions) to prevent duplicate processing on retries.

## Verification checklist

Before submitting work with Privy:

- [ ] App ID and App Secret are stored securely (environment variables, not hardcoded)
- [ ] PrivyProvider wraps the entire app (React) or PrivyClient is instantiated once (backend)
- [ ] `ready` state is checked before consuming Privy hooks (React)
- [ ] All required login methods are enabled in Dashboard
- [ ] Wallets are created with correct owner (user ID, key, or quorum)
- [ ] Policies are defined and tested if wallet has restrictions
- [ ] Transaction payloads use correct chain ID format (CAIP-2)
- [ ] Numeric values (amounts, gas) are in correct units (wei, lamports, etc.)
- [ ] Webhook endpoint is registered and signature verification is implemented
- [ ] Error handling catches `APIError` and `PrivyAPIError` (backend)
- [ ] Idempotency keys are used for critical operations
- [ ] Rate limit retry logic is implemented
- [ ] All sensitive data (secrets, keys) is never logged or exposed to client

## Resources

- **Comprehensive page index:** https://docs.privy.io/llms.txt
- **Key concepts guide:** https://docs.privy.io/basics/key-concepts
- **REST API reference:** https://docs.privy.io/api-reference/introduction
- **Policies and controls:** https://docs.privy.io/controls/policies/overview
- **Webhooks setup:** https://docs.privy.io/api-reference/webhooks/overview

---

> For additional documentation and navigation, see: https://docs.privy.io/llms.txt