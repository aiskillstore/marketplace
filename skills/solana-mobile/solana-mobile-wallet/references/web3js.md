# Legacy web3.js stack reference

**Only use this file when the project's Solana client is already `@solana/web3.js`, or the user
asked for it directly.** Anything else — a new app, a project with no Solana client yet, a kit
project gaining a wallet feature — belongs on kit. See [kit.md](kit.md).

Being here is not a reason to migrate mid-task either. Match what the project has, ship the
feature, and raise migration separately if it looks worthwhile. The
[migration sketch](#migrating-to-kit) at the end is for that conversation, not for doing it
opportunistically.

The two stacks differ in provider props, hook return values, and transaction construction, so
code from one silently fails on the other. Do not mix them in one app.

## Dependencies

```bash
npm install @wallet-ui/react-native-web3js @solana/web3.js @tanstack/react-query react-native-quick-crypto
```

## Crypto polyfill

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

Keep the polyfill in its own module imported first, so import ordering cannot be reshuffled.
Older guides used `react-native-get-random-values`; `react-native-quick-crypto` is what the
current templates ship and it covers more of the Web Crypto surface. A native rebuild is
required after installing it.

## Provider

Unlike the kit provider, this one takes `chain` and `endpoint`:

```tsx
import { MobileWalletProvider } from '@wallet-ui/react-native-web3js'
import type { Chain } from '@solana-mobile/mobile-wallet-adapter-protocol'

const chain: Chain = 'solana:devnet'

<MobileWalletProvider
  chain={chain}
  endpoint="https://api.devnet.solana.com"
  identity={{ name: 'My App', uri: 'myapp://myapp' }}
>
  {children}
</MobileWalletProvider>
```

Optional props: `cache`, `commitmentOrConfig`.

## Hook surface

```tsx
const { account, connect, disconnect, connection, signAndSendTransaction } = useMobileWallet()
```

| Value | Type | Notes |
| --- | --- | --- |
| `account` | `Account \| undefined` | `undefined` when disconnected |
| `accounts` | `Account[] \| null` | |
| `connect` | `() => Promise<Account>` | |
| `disconnect` | `() => Promise<void>` | |
| `connection` | `Connection` | web3.js connection — kit exposes `client` instead |
| `signAndSendTransaction` | `(tx, minContextSlot: number) => Promise<SignatureBytes>` | Second argument required |
| `signTransaction` | `(tx) => Promise<tx>` | Sign without broadcasting |
| `signMessage` | `(msg: Uint8Array) => Promise<Uint8Array>` | |
| `signIn` | `(payload) => Promise<SignInOutput>` | See [Sign-in with Solana](#sign-in-with-solana) |

There is **no `connected` boolean**. Derive it with `const connected = !!account`.

### account.address is a PublicKey here

On this stack `account.address` is a web3.js `PublicKey`, not a string. Call `.toString()`
whenever you display or interpolate it, or React renders the object and you get output like
`+9pgyt LK...MIiSdpI=`:

```tsx
<Text>{account.address.toString()}</Text>
```

`account.publicKey` also exists but is **deprecated in favour of `address`**. Prefer
`address`.

## Connect and disconnect

```tsx
import { Pressable, Text } from 'react-native'
import { useMobileWallet } from '@wallet-ui/react-native-web3js'

export function ConnectButton() {
  const { account, connect, disconnect } = useMobileWallet()

  async function onPress() {
    try {
      if (account) await disconnect()
      else await connect()
    } catch (error) {
      // Dismissing the wallet picker lands here — a normal outcome, not a crash.
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

Authorization is cached, so the app reconnects on restart without a fresh prompt.

## Transferring SOL

```tsx
import { useMobileWallet } from '@wallet-ui/react-native-web3js'
import { LAMPORTS_PER_SOL, PublicKey, SystemProgram, Transaction } from '@solana/web3.js'

export function useTransferSol() {
  const { account, connection, signAndSendTransaction } = useMobileWallet()

  return async function transfer({ amount, to }: { amount: number; to: string }) {
    if (!account) throw new Error('Connect a wallet first.')

    const { context, value: latestBlockhash } = await connection.getLatestBlockhashAndContext('confirmed')

    const transaction = new Transaction({
      blockhash: latestBlockhash.blockhash,
      feePayer: account.address,
      lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
    }).add(
      SystemProgram.transfer({
        fromPubkey: account.address,
        lamports: Math.round(amount * LAMPORTS_PER_SOL),
        toPubkey: new PublicKey(to),
      }),
    )

    const signature = await signAndSendTransaction(transaction, context.slot)

    await connection.confirmTransaction({
      blockhash: latestBlockhash.blockhash,
      lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
      signature: signature.toString(),
    })

    return signature
  }
}
```

Points that matter:

- **`signAndSendTransaction` needs `minContextSlot`.** Use
  `getLatestBlockhashAndContext()` rather than `getLatestBlockhash()` so you get the
  blockhash and its slot from one call — the two must agree or the wallet rejects the
  payload.
- **Use the hook's `connection`.** Constructing `new Connection(...)` separately gives you a
  client pointed at a possibly different cluster than the wallet authorized against.
- **Get a fresh blockhash per attempt.** They expire in roughly 60–90 seconds. Reusing one
  across a retry is a common cause of "payloads invalid for signing".
- Use `Math.round`, not `Math.floor`, when converting SOL to lamports, so `0.1` does not
  silently become one lamport short.

## Encoding bytes

`Buffer` is not present in React Native by default. Use the base64 helpers re-exported from
the wallet package:

```ts
import { fromUint8Array, toUint8Array } from '@wallet-ui/react-native-web3js'

const encoded = fromUint8Array(bytes)
const decoded = toUint8Array(encoded)
```

Avoid `btoa(String.fromCharCode(...bytes))`. Spreading a large array into arguments throws
`RangeError: Maximum call stack size exceeded`.

## Sign-in with Solana

`signIn` behaves the same here as on kit: it authorizes and proves wallet ownership in one round
trip. The payload and the rules around it are identical across both stacks, so
[kit.md](kit.md#sign-in-with-solana) is the full account — only the imports differ.

The part that does not change with the stack: **as soon as a backend grants anything based on
the result, the minimal payload is not enough.** Without a server-issued, single-use `nonce` the
signature is replayable, and without a `domain` it could have been farmed by another site. Build
the full payload — `domain`, `nonce`, `issuedAt`, `expirationTime`, `uri`, `version` — and
verify the signature server-side against the address that signed. The `seeker-genesis-token`
skill covers the verification half.

## Migrating to kit

Worth doing when you touch this code substantially. The rough shape:

1. Swap `@wallet-ui/react-native-web3js` for `@wallet-ui/react-native-kit`, and
   `@solana/web3.js` for `@solana/kit`.
2. Provider: replace `chain` and `endpoint` with a single `cluster`, built with
   `createSolanaDevnet()` or a sibling helper.
3. Replace `connection` with `client`, and `connection.getX()` with
   `client.rpc.getX().send()`. Add `chain` from the hook to your React Query keys.
4. Replace `Transaction`/`SystemProgram` construction with `sendTransactions(instructions)`,
   falling back to kit's `pipe` builders where you need fee-payer or lifetime control.
5. `account.address` becomes a branded string rather than a `PublicKey`, so drop the
   `.toString()` calls. Stop using `account.publicKey`, which is deprecated here too.
6. Lamport values become `bigint`. Audit every arithmetic site — mixing `bigint` and `number`
   throws at runtime rather than coercing, so this is where a sloppy migration breaks.

See [kit.md](kit.md) for the target shapes, and
[`expo-kit-minimal`](https://github.com/solana-mobile/templates/tree/main/mobile/expo-kit-minimal)
for a whole app in the shape you are migrating toward.
