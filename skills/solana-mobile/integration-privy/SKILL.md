---
name: integration-privy
description: Add Privy authentication to a Solana Expo Android app on top of Mobile Wallet Adapter, using Sign-In-With-Solana. Use when installing @privy-io/expo, mounting PrivyProvider, logging a user in with useLoginWithSiws, linking a wallet to an existing Privy account, reading the Privy access token from a backend, or debugging a Privy plus MWA setup.
---

# Privy on Solana mobile

Privy owns the **user**: a durable account identifier and a JWT a backend can verify. Mobile
Wallet Adapter owns the **keys**. Privy signs nothing in this setup — every signature still
comes from the wallet app.

Sign-In-With-Solana joins the two. Privy generates a message, MWA signs it, Privy exchanges
the signature for a session.

Reach for this when an app needs a stable user record across devices, a server-verifiable
session, or login methods beyond a wallet. An app that only needs a connected address does not
need Privy — use the `solana-mobile-wallet` skill alone.

**Android only, and a development build only.** MWA has no iOS support and does not run in
Expo Go, which caps the whole integration.

## Before you start

| Requirement | Where it comes from |
| --- | --- |
| A working `useMobileWallet()` | `solana-mobile-wallet` skill |
| A development build on Android | `solana-mobile` skill |
| A Privy app ID and client ID | The Privy dashboard — step 1 |

## Step 1: create the Privy app

Do this first. Two of these values are compile-time environment variables, and one dashboard
toggle decides whether login works at all.

1. Sign in at https://dashboard.privy.io and click **New app** on the organization overview
2. Name it, select **Mobile app**, create it, and save the **App ID**
3. Under **User management > Authentication**, in the **External wallets** card, enable
   **SVM (Solana) wallets**
4. Under **App settings > Clients**, set the app identifier to the `expo.android.package`
   value from `app.json`, and save the **Client ID**

The **SVM wallets** toggle is the one that is easy to skip and expensive to debug — while it is
off, `login` rejects every SIWS attempt even though the wallet signed correctly. The **app
identifier** matters because Privy checks the calling app's package name against the client.

```bash
EXPO_PUBLIC_PRIVY_APP_ID=your-privy-app-id
EXPO_PUBLIC_PRIVY_CLIENT_ID=your-privy-client-id
```

Both are public client-side identifiers, so `EXPO_PUBLIC_` is correct. **The Privy app secret
never belongs in a mobile app** — anything prefixed `EXPO_PUBLIC_` is readable in the shipped
bundle. The secret is for server code only.

## Step 2: install and configure

```bash
npx expo install @privy-io/expo @privy-io/expo-native-extensions
```

`@privy-io/expo` carries a long peer dependency list that shifts between releases — passkeys,
secure store, web browser, crypto, `viem`. Install what the version you picked asks for rather
than copying a list from anywhere, including from here.

Three pieces of native wiring are required, and the SDK fails in a different place for each:

- Crypto and text-encoding polyfills, loaded from the entry module before anything else
- `expo-secure-store` and `expo-web-browser` in `app.json` plugins
- A Metro resolver override so `jose` resolves to its browser build

Full contents for each, and how to confirm they took: [references/setup.md](references/setup.md).
Rebuild natively (`npx expo run:android`) after this step — a JS reload will not pick up the
new native modules.

## Step 3: mount the providers

```tsx
import { PrivyProvider } from '@privy-io/expo'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type AppIdentity, createSolanaDevnet, MobileWalletProvider } from '@wallet-ui/react-native-kit'
import type { ReactNode } from 'react'

const cluster = createSolanaDevnet()
const identity: AppIdentity = { name: 'My App', uri: 'myapp://myapp' }
const privyAppId = process.env.EXPO_PUBLIC_PRIVY_APP_ID
const privyClientId = process.env.EXPO_PUBLIC_PRIVY_CLIENT_ID
const queryClient = new QueryClient()

export function AppProviders({ children }: { children: ReactNode }) {
  if (!privyAppId || !privyClientId) {
    throw new Error('Missing Privy environment variables')
  }

  return (
    <QueryClientProvider client={queryClient}>
      <PrivyProvider appId={privyAppId} clientId={privyClientId}>
        <MobileWalletProvider cluster={cluster} identity={identity}>
          {children}
        </MobileWalletProvider>
      </PrivyProvider>
    </QueryClientProvider>
  )
}
```

`PrivyProvider` and `MobileWalletProvider` do not depend on each other, so their relative
nesting is free — but both must sit above every screen, and `QueryClientProvider` above both
if the hooks below are queries and mutations.

Throwing on missing environment variables is deliberate. Undefined values reach Privy as a
malformed app ID and surface much later as an opaque initialization error.

`clientId` is typed optional in `PrivyProviderProps`, which is misleading here: Privy's mobile
documentation treats it as required, and the dashboard issues one per mobile client. Pass it.

## Step 4: wait for `isReady`

`usePrivy()` returns state that is meaningless until the SDK finishes reading stored tokens:

| Value | Type | Notes |
| --- | --- | --- |
| `isReady` | `boolean` | Everything else is provisional until this is `true` |
| `user` | `User \| null` | `null` when unauthenticated — not `undefined` |
| `error` | `Error \| null` | Initialization failures, typically storage access |
| `logout` | `() => Promise<void>` | No-op when nobody is signed in |
| `getAccessToken` | `() => Promise<string \| null>` | Call per request; never cache the result |

```tsx
const { error, isReady, user } = usePrivy()

if (!isReady) return <Loading />
if (error) return <ErrorCard message={error.message} />
```

Rendering a signed-out state while `isReady` is `false` makes an already-authenticated user
flash through a login screen on every cold start.

## Step 5: sign in with SIWS

The whole integration is this one sequence: generate, sign, exchange.

```tsx
import { useLoginWithSiws } from '@privy-io/expo'
import type { Address } from '@solana/kit'
import { useMutation } from '@tanstack/react-query'
import { fromUint8Array, useMobileWallet } from '@wallet-ui/react-native-kit'

const siwsDomain = 'myapp.com'
const siwsUri = 'myapp://privy-login'

export function usePrivySignInMutation(address: Address) {
  const { generateMessage, login } = useLoginWithSiws()
  const { signMessages } = useMobileWallet()

  return useMutation({
    mutationFn: async () => {
      const { message } = await generateMessage({
        from: { domain: siwsDomain, uri: siwsUri },
        wallet: { address: address.toString() },
      })

      const signedPayload = await signMessages(new TextEncoder().encode(message))

      await login({ message, signature: fromUint8Array(signedPayload) })
    },
  })
}
```

Call it only once a wallet is connected — `useMobileWallet().account` must be defined, since
`signMessages` triggers its own authorization otherwise.

Three encoding details decide whether this works:

1. **Pass `account.address`, which is base58.** `account.addressBase64` also exists; it is
   MWA's wire format and Privy will not accept it. Privy's own recipe spends three lines
   converting base64 to base58 because it drives the raw protocol — `@wallet-ui/react-native-kit`
   has already done that conversion for you.
2. **`fromUint8Array` produces base64, not base58.** It is a re-export of `js-base64`. Privy
   wants the base64 string here; base58 fails verification.
3. **Do not slice the bytes.** `signMessages` resolves to MWA's *signed payload*, not a bare
   64-byte signature. Base64-encode it whole and hand it over — the template and Privy's
   recipe both do exactly this.

`from.domain` is an RFC 3986 authority: a bare host, no scheme and no path. `from.uri` is a
full URI and is normally your app's deep link. Keep both stable — they are embedded in the
signed message the user sees in their wallet.

Linking a wallet to an account that already exists, and verifying the session on a server:
[references/siws.md](references/siws.md).

## Step 6: sign out of both

```tsx
const { logout } = usePrivy()
const { disconnect } = useMobileWallet()

await logout()
await disconnect()
```

Doing one without the other leaves the app in a half-signed-out state. `disconnect()` alone
keeps a live Privy session with no wallet behind it; `logout()` alone leaves the wallet
authorized and re-signs in silently on the next attempt.

## Which side owns what

| Concern | Owner |
| --- | --- |
| Private keys and signing | The wallet app, over MWA |
| Connected address | `useMobileWallet().account` |
| User identity across devices | `usePrivy().user` |
| Server-verifiable session | `usePrivy().getAccessToken()` |
| Sending transactions | `useMobileWallet().sendTransactions` |

There is no Privy signer in this setup. A user is signed in to Privy and connected over MWA as
two independent facts, and the UI has to handle every combination — most usefully "connected
but not signed in", which is where the sign-in button belongs.

## Reference material

- [references/setup.md](references/setup.md) — polyfills, Metro config, `app.json` plugins,
  environment variables, and how to verify each one landed
- [references/siws.md](references/siws.md) — the SIWS exchange in depth, linking additional
  wallets, server-side token verification, and the raw-protocol variant without Wallet UI
- [references/troubleshooting.md](references/troubleshooting.md) — Privy-specific failures and
  their causes

The patterns here follow
[`expo-kit-privy`](https://github.com/solana-mobile/templates/tree/main/mobile/expo-kit-privy),
a complete working app. Read it when this file is ambiguous:

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-privy --skip-install
```

## Related skills

- `solana-mobile-wallet` — MWA connection, signing, and sending, which this builds on
- `solana-mobile` — development builds, emulators, toolchain checks
- `seeker-genesis-token` — SIWS verified server-side without Privy, when a JWT is overkill

## Links

- Privy Solana MWA recipe: https://docs.privy.io/recipes/solana/adding-solana-mwa
- Privy Expo SIWS login: https://docs.privy.io/guide/expo/authentication/siws
- Privy dashboard: https://dashboard.privy.io
