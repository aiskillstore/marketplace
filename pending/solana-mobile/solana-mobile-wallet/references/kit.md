# Kit stack reference

For projects using `@wallet-ui/react-native-kit` with `@solana/kit`. This is the current
default. For `@wallet-ui/react-native-web3js`, see [web3js.md](web3js.md) instead.

## Dependencies

What `expo-kit-minimal` ships, which is the smallest working set:

```bash
npm install @wallet-ui/react-native-kit @solana/kit @tanstack/react-query react-native-quick-crypto
```

Add `@solana-program/memo` (or whichever program clients you need) for instruction builders.

`react-native-quick-crypto` needs a native rebuild after install (`expo run:android`), not just
a Metro restart.

## Crypto polyfill

Kit needs Web Crypto. Install it before anything else runs, in its own module so import
ordering cannot be reshuffled by a formatter or linter:

```js
// polyfill.js
import { install } from 'react-native-quick-crypto'

install()
```

```js
// index.js
import './polyfill'
import 'expo-router/entry'
```

Point `package.json` `"main"` at `./index.js`. Getting this wrong produces signing failures
that look like wallet bugs — the crypto calls fail before the wallet is ever reached.

## Clusters and config

Build clusters with the `createSolana*` helpers. A `SolanaCluster` needs `id`, `label`, and
`url`, and the helpers fill in everything but the URL:

```ts
import {
  type AppIdentity,
  createSolanaDevnet,
  createSolanaTestnet,
  type SolanaCluster,
} from '@wallet-ui/react-native-kit'

export class AppConfig {
  static identity: AppIdentity = { name: 'my-app' }
  static networks: SolanaCluster[] = [
    createSolanaDevnet({ url: 'https://api.devnet.solana.com' }),
    createSolanaTestnet({ url: 'https://api.testnet.solana.com' }),
  ]
}
```

`createSolanaDevnet`, `createSolanaTestnet`, and `createSolanaLocalnet` take optional props.
`createSolanaMainnet` requires a `url` — there is no public default worth shipping for mainnet.
Keep any paid RPC key server-side; an `EXPO_PUBLIC_*` variable is readable from the APK.

## Reading chain data

Use the `client` the provider already built, reachable from the hook:

```ts
import type { Address } from '@solana/kit'
import { useQuery } from '@tanstack/react-query'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function useAccountGetBalance({ address }: { address: Address }) {
  const { chain, client } = useMobileWallet()

  return useQuery({
    queryFn: () => client.rpc.getBalance(address).send(),
    queryKey: ['get-balance', chain, address],
  })
}
```

`chain` belongs in the query key. Without it, switching cluster serves the previous network's
cached values — which presents as a wallet bug rather than a caching one.

Kit RPC calls are lazy: `client.rpc.someMethod(...)` builds a request, `.send()` executes it.
Forgetting `.send()` leaves you holding a pending request object — nothing errors, the data is
simply never fetched.

Balances come back as `bigint` lamports:

```ts
export function lamportsToSol(lamports: bigint) {
  return Number(lamports) / 1e9
}
```

Convert at the display boundary only, and never with `parseFloat`.

### Building your own client

Only needed for a cluster the provider does not hold, or a custom transport. This pulls in
`@solana/kit-plugin-rpc`, which the minimal template does not use:

```ts
import { createClient } from '@solana/kit'
import { solanaRpcConnection } from '@solana/kit-plugin-rpc'
import type { SolanaCluster } from '@wallet-ui/react-native-kit'

export function createSolanaClient(cluster: SolanaCluster) {
  return createClient().use(
    solanaRpcConnection({ rpcSubscriptionsUrl: cluster.urlWs, rpcUrl: cluster.url }),
  )
}

export type SolanaClient = ReturnType<typeof createSolanaClient>
```

## Sending a transaction: the short path

```tsx
import { getAddMemoInstruction } from '@solana-program/memo'
import type { Address, Instruction } from '@solana/kit'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function useSendMemo({ address }: { address: Address }) {
  const { sendTransactions } = useMobileWallet()

  return async function send(memo: string) {
    const instructions: Instruction[] = [getAddMemoInstruction({ memo })]

    return sendTransactions(instructions)
  }
}
```

`sendTransactions` handles blockhash, `minContextSlot`, fee payer, and signature decoding, and
returns the signature as a string. Use it unless you need control over one of those.

## Sending a transaction: the explicit path

Needed when you want a fee pre-check, a specific lifetime, or multiple instructions with a
non-default fee payer.

```ts
import {
  type Address,
  appendTransactionMessageInstruction,
  assertIsTransactionMessageWithSingleSendingSigner,
  compileTransactionMessage,
  createTransactionMessage,
  getBase58Decoder,
  getBase64Decoder,
  getCompiledTransactionMessageEncoder,
  pipe,
  setTransactionMessageFeePayerSigner,
  setTransactionMessageLifetimeUsingBlockhash,
  signAndSendTransactionMessageWithSigners,
  type TransactionMessageBytesBase64,
  type TransactionSendingSigner,
} from '@solana/kit'
import { getAddMemoInstruction } from '@solana-program/memo'

export async function sendMemo({
  address,
  client,
  getTransactionSigner,
  text,
}: {
  address: Address
  client: SolanaClient
  getTransactionSigner: (address: Address, minContextSlot: bigint) => TransactionSendingSigner
  text: string
}) {
  const {
    context: { slot: minContextSlot },
    value: latestBlockhash,
  } = await client.rpc.getLatestBlockhash({ commitment: 'confirmed' }).send()

  const signer = getTransactionSigner(address, minContextSlot)

  const message = pipe(
    createTransactionMessage({ version: 0 }),
    (m) => setTransactionMessageFeePayerSigner(signer, m),
    (m) => setTransactionMessageLifetimeUsingBlockhash(latestBlockhash, m),
    (m) => appendTransactionMessageInstruction(getAddMemoInstruction({ memo: text }), m),
  )

  assertIsTransactionMessageWithSingleSendingSigner(message)

  const signatureBytes = await signAndSendTransactionMessageWithSigners(message)
  return getBase58Decoder().decode(signatureBytes)
}
```

Points that matter:

- `getTransactionSigner(address, minContextSlot)` comes from `useMobileWallet()`. The
  `minContextSlot` must come from the same `getLatestBlockhash` response used for the
  lifetime — mismatching them causes the wallet to reject the payload.
- `signAndSendTransactionMessageWithSigners` returns raw bytes. Decode with
  `getBase58Decoder()` to get a signature string.
- The `assertIsTransactionMessageWithSingleSendingSigner` call is not optional ceremony; it
  is what narrows the type so the send function accepts the message.

### Checking the fee before sending

Failing early with a clear message beats a wallet-side rejection:

```ts
const encoded = getCompiledTransactionMessageEncoder().encode(compileTransactionMessage(message))

const [{ value: balance }, { value: fee }] = await Promise.all([
  client.rpc.getBalance(signer.address, { commitment: 'confirmed' }).send(),
  client.rpc
    .getFeeForMessage(getBase64Decoder().decode(encoded) as TransactionMessageBytesBase64, {
      commitment: 'confirmed',
    })
    .send(),
])

if (fee === null) throw new Error('Could not estimate the transaction fee.')
if (balance < fee) {
  throw new Error(`Balance ${balance} lamports is below the ${fee} lamport fee.`)
}
```

Both are `bigint`, so compare them directly — no `Number()` conversion, which would lose
precision on large balances.

## Signing a message

```ts
const { signMessages } = useMobileWallet()

const signature = await signMessages(new TextEncoder().encode('hello'))
```

Takes and returns `Uint8Array`. To display or transmit the result, use kit's decoders
(`getBase58Decoder()`, `getBase64Decoder()`) or `fromUint8Array` re-exported from
`@wallet-ui/react-native-kit`.

Do **not** reach for `btoa(String.fromCharCode(...bytes))`. Spreading a large array into
arguments throws `RangeError: Maximum call stack size exceeded`, and it is unnecessary when
kit ships decoders.

## Sign-in with Solana

`signIn` authorizes and proves wallet ownership in one round trip, which is fewer prompts than
`connect()` followed by a message signature. It also works with no connected account, in which
case it connects and signs in together.

### The minimal form

For in-app UX where nothing server-side depends on the result, most payload fields are
optional. Take `chain` and `identity` from the hook:

```tsx
import { type Account, useMobileWallet } from '@wallet-ui/react-native-kit'

export function SignInButton({ account }: { account?: Account }) {
  const { chain, identity, signIn } = useMobileWallet()

  return (
    <Button
      onPress={async () => {
        const result = await signIn({
          address: account?.address.toString(),
          chainId: chain,
          uri: identity.uri,
        })

        console.log('signed in as', result.account.address)
      }}
      title={account ? `Sign in with ${account.label}` : 'Sign in and connect'}
    />
  )
}
```

Omitting `address` lets the wallet choose the account, which is what you want for the
connect-and-sign-in-together case.

### The verified form

**As soon as a backend grants anything based on the result, the minimal form is not enough.**
Without a server-issued nonce the signature is replayable, and without a domain the signature
could have been farmed by another site. Build the full payload:

```ts
import { type SignInPayload, type SolanaClusterId } from '@wallet-ui/react-native-kit'
import * as Linking from 'expo-linking'

const APP_DOMAIN = 'myapp'
const APP_URI = Linking.createURL('/')

export function createSignInPayload({
  address,
  cluster,
  nonce,
  requestId,
  statement,
}: {
  address: string
  cluster: SolanaClusterId
  nonce: string
  requestId: string
  statement: string
}): SignInPayload {
  const issuedAt = new Date()

  return {
    address,
    chainId: cluster,
    domain: APP_DOMAIN,
    expirationTime: new Date(issuedAt.getTime() + 60_000).toISOString(),
    issuedAt: issuedAt.toISOString(),
    nonce,
    notBefore: issuedAt.toISOString(),
    requestId,
    statement,
    uri: APP_URI,
    version: '1',
  }
}
```

```ts
const { signIn } = useMobileWallet()
const output = await signIn(createSignInPayload({ ... }))
```

The `nonce` must be generated server-side and be single-use, otherwise the signature is
replayable and the whole exercise proves nothing. Verify the returned signature on your
backend — see the `seeker-genesis-token` skill for the verification half.

## Telling cancellation apart from failure

Dismissing the wallet picker rejects with an association error. Surfacing that as "wallet
connection failed" is misleading, so branch on it:

```ts
function isWalletConnectionCanceled(error: unknown) {
  const code = error !== null && typeof error === 'object' && 'code' in error ? String(error.code) : ''
  const message = error instanceof Error ? error.message : ''

  return (
    code === 'ERROR_ASSOCIATION_CANCELLED' ||
    message.includes('CancellationException') ||
    message.includes('Local association cancelled by user')
  )
}
```

Treat cancellation as a no-op with a retry affordance; treat everything else as an error
worth reporting.

For everything else, normalise the value before showing it — thrown values are not always
`Error` instances:

```ts
export function formatError(error: unknown) {
  if (error instanceof Error) return error.message
  if (error && typeof error === 'object' && 'message' in error) return String(error.message)
  if (typeof error === 'string' && error.trim().length > 0) return error

  return 'Unknown error occurred'
}
```

Rendering a raw non-`Error` throw gives the user `[object Object]`.
