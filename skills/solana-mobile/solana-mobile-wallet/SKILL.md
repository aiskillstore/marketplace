---
name: solana-mobile-wallet
description: Connect Solana wallets and sign or send transactions in React Native Expo apps using Mobile Wallet Adapter and Wallet UI. Use when adding a connect wallet button, showing a connected address, disconnecting, signing messages, sign-in with Solana, transferring SOL, or sending any transaction from a Solana mobile app.
---

# Solana wallets on mobile

Wallet connection and transaction signing through Mobile Wallet Adapter (MWA), wrapped by
`@wallet-ui/react-native-kit` (or `@wallet-ui/react-native-web3js` on the legacy stack).

**MWA requires a development build on Android. Expo Go will not work.** If the project has
no development build yet, or does not exist, start with the `solana-mobile` skill.

## Step 1: pick the stack — do this before writing any code

**Write kit code.** `@solana/kit` with `@wallet-ui/react-native-kit` is the stack to reach for,
and everything in this file describes it.

There is exactly one reason to write `@solana/web3.js` instead: the project already runs on it.
Check `package.json` first.

| `package.json` says | Do this |
| --- | --- |
| `@wallet-ui/react-native-kit`, or no Solana client yet | Kit. This file, plus [references/kit.md](references/kit.md) |
| `@wallet-ui/react-native-web3js` is the app's Solana client | [references/web3js.md](references/web3js.md) |
| The user explicitly asked for web3.js | [references/web3js.md](references/web3js.md), and say why kit would be better |

Do not introduce web3.js into a kit project, or mix the two in one app. Their provider props,
hook return values, and transaction construction all differ, so code from one silently fails on
the other. If a project has no Solana client at all, that is a new build — use kit.

Adding a *new* wallet feature to an existing web3.js app is not a reason to migrate mid-task.
Match what is there, and mention migration as a follow-up if it seems worth it.

## Step 2: confirm the provider is mounted

`useMobileWallet` returns empty state without `MobileWalletProvider` above it. Look for it in
the root layout or an app-providers module.

Build the cluster with the `createSolana*` helpers rather than by hand — a `SolanaCluster` also
needs a `label`, which the helpers fill in:

```tsx
import {
  type AppIdentity,
  createSolanaDevnet,
  MobileWalletProvider,
  type SolanaCluster,
} from '@wallet-ui/react-native-kit'

const identity: AppIdentity = { name: 'My App' }
const cluster: SolanaCluster = createSolanaDevnet({ url: 'https://api.devnet.solana.com' })

<MobileWalletProvider cluster={cluster} identity={identity}>
  {children}
</MobileWalletProvider>
```

`createSolanaDevnet`, `createSolanaTestnet`, and `createSolanaLocalnet` take optional props;
`createSolanaMainnet` requires a `url`, since there is no sensible public default for mainnet.

The provider props are `cluster`, `identity`, and optional `cache`, `createClient`, `children`.
There is **no `chain` prop and no `endpoint` prop** — passing those does nothing.

Every `AppIdentity` field is optional. `name` alone is enough to get started; add `uri` as a
real deep link for anything shipping, since wallets display it during authorization and a
placeholder can read as a phishing attempt.

Put `QueryClientProvider` from `@tanstack/react-query` above the wallet provider — the hook
patterns below are queries and mutations.

## Step 3: use the hook

```tsx
import { useMobileWallet } from '@wallet-ui/react-native-kit'

const { account, connect, disconnect, client } = useMobileWallet()
```

What the hook actually returns on the kit stack:

| Value | Type | Notes |
| --- | --- | --- |
| `account` | `Account \| undefined` | `undefined` when disconnected, not `null` |
| `accounts` | `Account[] \| null` | All authorized accounts |
| `connect` | `() => Promise<Account>` | Opens the wallet picker |
| `disconnect` | `() => Promise<void>` | |
| `client` | `Client` | Kit client — use `client.rpc` for RPC calls |
| `chain` | `SolanaClusterId` | The active cluster. Put it in query keys |
| `sendTransactions` | `(instructions: Instruction[]) => Promise<string>` | Simplest send path |
| `signAndSendTransaction` | `(tx, minContextSlot) => Promise<SignatureBytes>` | Note the second argument |
| `signTransaction` | `(tx) => Promise<Transaction>` | Sign without broadcasting |
| `signMessages` | `(msg: Uint8Array) => Promise<Uint8Array>` | |
| `signIn` | `(payload) => Promise<SignInOutput>` | Sign-in with Solana; can also connect |
| `identity`, `store` | | Config and authorization store |

Singular aliases exist for several of these — `sendTransaction`, `signMessage`,
`signTransactions` — with the same signatures. The templates use the plural forms; either
works, so follow whatever the project already uses.

Four things that trip people up:

1. **There is no `connected` boolean.** Derive it: `const connected = !!account`.
2. **`signAndSendTransaction` takes `minContextSlot` as a second argument.** Calling it with
   only a transaction fails. Get the slot from `getLatestBlockhash`, or use
   `sendTransactions(instructions)`, which handles this for you.
3. **The kit hook exposes `client`, not `connection`.** `connection` only exists on the
   web3.js stack.
4. **Include `chain` in every React Query key that holds chain data.** Otherwise switching
   cluster serves the previous network's cached balances, which looks like a wallet bug.

`account.address` is a kit `Address` (a branded string), so it interpolates into text directly.
`account.label` is the wallet-supplied name and may be undefined.

## Connect and disconnect

```tsx
import { Pressable, Text } from 'react-native'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function ConnectButton() {
  const { account, connect, disconnect } = useMobileWallet()

  async function onPress() {
    try {
      if (account) await disconnect()
      else await connect()
    } catch (error) {
      // The user dismissing the wallet picker lands here. Do not treat it as a crash.
      console.error(error)
    }
  }

  return (
    <Pressable onPress={onPress}>
      <Text>{account ? 'Disconnect' : 'Connect Wallet'}</Text>
    </Pressable>
  )
}
```

Always wrap `connect()` in try/catch — cancelling the wallet picker rejects the promise.
Cancellation is a normal outcome, not an error state worth alarming the user about; see
[references/kit.md](references/kit.md) for how to tell cancellation apart from real
failures.

Authorization is cached, so the app reconnects on restart without a new prompt.

## Read chain data

Use `client` from the hook. There is no need to build a client of your own:

```tsx
import type { Address } from '@solana/kit'
import { useQuery } from '@tanstack/react-query'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function useGetBalance({ address }: { address: Address }) {
  const { chain, client } = useMobileWallet()

  return useQuery({
    queryFn: () => client.rpc.getBalance(address).send(),
    queryKey: ['get-balance', chain, address],
  })
}
```

Kit RPC calls are lazy: `client.rpc.someMethod(...)` builds a request and `.send()` runs it.
Forget `.send()` and nothing errors — the data simply never arrives.

Balances come back as `bigint` lamports. Convert deliberately, and never with `parseFloat`:

```ts
export function lamportsToSol(lamports: bigint) {
  return Number(lamports) / 1e9
}
```

## Send a transaction

Build instructions and hand them over. This covers most cases:

```tsx
import { getAddMemoInstruction } from '@solana-program/memo'
import type { Instruction } from '@solana/kit'

const { sendTransactions } = useMobileWallet()

const instructions: Instruction[] = [getAddMemoInstruction({ memo: 'gm' })]
const signature = await sendTransactions(instructions)
```

`sendTransactions` handles blockhash, `minContextSlot`, fee payer, and signature decoding.

Reach for the explicit `pipe` form only when you need fee-payer control, a specific blockhash
lifetime, or a fee pre-check. Full worked example, with the balance-versus-fee assertion and
signature decoding: [references/kit.md](references/kit.md).

## Reference material

- [references/kit.md](references/kit.md) — kit stack: clusters and config, reading chain data,
  transactions, sign-in with Solana, message signing, error handling
- [references/web3js.md](references/web3js.md) — legacy `@solana/web3.js` stack, and a migration
  sketch
- [references/troubleshooting.md](references/troubleshooting.md) — connection and signing
  failures with known causes

When something here is ambiguous, read the template. The patterns in this skill follow
[`expo-kit-minimal`](https://github.com/solana-mobile/templates/tree/main/mobile/expo-kit-minimal),
which is a complete working app and stays current in a way prose does not:

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-minimal --skip-install
```

## Related skills

- `solana-mobile` — project setup, templates, emulators, development builds
- `integration-privy` — add Privy accounts and sessions on top of this wallet connection
- `seeker-genesis-token` — verify Seeker device ownership after connecting
- `seeker-domains` — display `.skr` names instead of raw addresses

## Links

- Wallet UI: https://wallet-ui.dev
- MWA docs: https://docs.solanamobile.com/react-native/overview
- Solana Kit: https://www.solanakit.com
