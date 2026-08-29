# Sign-In-With-Solana against Privy

The exchange in full, plus the three variations on it: linking a second wallet, verifying the
session on a server, and driving the raw MWA protocol when Wallet UI is not in the project.

## The exchange

```
generateMessage  →  Privy builds a SIWS message bound to the address, domain, and uri
signMessages     →  the wallet app signs it, user approves in the wallet
login            →  Privy verifies the signature and returns a User
```

Privy owns the nonce and the expiry inside the message, which is the reason to call
`generateMessage` rather than assembling a SIWS message yourself. A hand-built message will not
carry a nonce Privy issued, and `login` rejects it.

## Exact hook signatures

`useLoginWithSiws()` from `@privy-io/expo`:

```ts
generateMessage: (args: {
  from: { domain: string; uri: string }
  wallet: { address: string }
}) => Promise<{ message: string }>

login: (opts: {
  disableSignup?: boolean
  message: string
  signature: string
  wallet?: { connectorType?: string; walletClientType?: string }
}) => Promise<User>
```

Notes that are not obvious from the shape:

- `wallet` on `login` is optional metadata that gets stored on the linked account. Omitting it
  is fine; the template does.
- `disableSignup: true` makes `login` reject rather than create an account for an unrecognized
  wallet. Use it when a separate onboarding flow owns account creation.
- The hook takes no `onSuccess` or `onError` options, unlike its React web counterpart. Handle
  both from the returned promise.
- `login` resolves to a `User`. Reading `usePrivy().user` immediately after is also fine — the
  provider state updates as part of the call.

## Encoding, end to end

This is where the integration goes wrong, so trace the types once:

| Step | Value | Encoding |
| --- | --- | --- |
| `account.address` | Kit `Address` | base58 — pass this to `generateMessage` |
| `account.addressBase64` | MWA wire format | base64 — Privy rejects it |
| `generateMessage` result | `{ message: string }` | plain text |
| `signMessages` argument | `Uint8Array` | `new TextEncoder().encode(message)` |
| `signMessages` result | `Uint8Array` | MWA *signed payload*, not a bare signature |
| `login` `signature` | `string` | `fromUint8Array(...)` — base64 |

`fromUint8Array` is exported from `@wallet-ui/react-native-kit` as a re-export of `js-base64`.
Use it rather than `btoa(String.fromCharCode(...bytes))`, which throws
`RangeError: Maximum call stack size exceeded` on payloads of any size.

Do not slice the signed payload down to its trailing 64 bytes. Both the `expo-kit-privy`
template and Privy's own MWA recipe pass the whole thing base64-encoded, and that is what
Privy's verifier expects.

## Choosing `domain` and `uri`

```ts
const siwsDomain = 'myapp.com'
const siwsUri = 'myapp://privy-login'
```

`domain` is an RFC 3986 *authority* — a host, optionally with a port. No scheme, no trailing
path. `uri` is a full URI identifying what is requesting the signature; a deep link into the
app is the natural choice on mobile.

Both are rendered inside the message the user approves in their wallet, so they are the only
thing distinguishing your request from a phishing one. Pick values that read as yours and then
leave them alone — changing them changes what users see at every login.

## Linking a wallet to an existing account

Same shape, different hook. Use this when the user already signed in some other way — email,
OAuth — and is now attaching a wallet:

```tsx
import { useLinkWithSiws } from '@privy-io/expo'

const { generateMessage, link } = useLinkWithSiws()

const { message } = await generateMessage({
  from: { domain: siwsDomain, uri: siwsUri },
  wallet: { address: address.toString() },
})
const signedPayload = await signMessages(new TextEncoder().encode(message))

await link({ message, signature: fromUint8Array(signedPayload) })
```

`link` takes the same options as `login` minus `disableSignup`, and returns the updated `User`
with the wallet in its linked accounts. Calling `login` here instead would start a second
account owned by the wallet, orphaning the original.

## Verifying the session on a server

The client's `user.id` proves nothing — it is a string the client could invent. Send the access
token and let the server decide:

```ts
const { getAccessToken } = usePrivy()

const token = await getAccessToken()

await fetch('https://api.myapp.com/claim', {
  headers: { authorization: `Bearer ${token}` },
  method: 'POST',
})
```

Fetch a token per request. It is short-lived and the SDK refreshes it on demand, so a cached
copy expires mid-session.

### Verify the token, and pin who it was issued for

Privy access tokens are ES256 JWTs. The server SDK runs the whole check and is the right
default:

```ts
import { PrivyClient } from '@privy-io/node'

const privy = new PrivyClient({
  appId: process.env.PRIVY_APP_ID,
  appSecret: process.env.PRIVY_APP_SECRET,
})

const claims = await privy.utils().auth().verifyAccessToken(token)
```

It resolves the app's JWKS for you and checks the audience against the `appId` you constructed
it with.

Without a Node SDK, verify against Privy's JWKS and pass `issuer` and `audience` explicitly:

```ts
import * as jose from 'jose'

const jwks = jose.createRemoteJWKSet(
  new URL(`https://api.privy.io/v1/apps/${process.env.PRIVY_APP_ID}/jwks.json`),
)

const { payload } = await jose.jwtVerify(token, jwks, {
  algorithms: ['ES256'],
  audience: process.env.PRIVY_APP_ID,
  issuer: 'privy.io',
})
```

`createRemoteJWKSet` caches the fetch and re-fetches on an unknown key ID, so signing-key
rotation does not need a deploy. The dashboard also exposes a single static verification key
under **Configuration > App settings**, usable via `jose.importSPKI(key, 'ES256')` in place of
`jwks` — but pin it only if you would rather redeploy than allow an outbound call to Privy.

**A valid signature is not proof the token was issued to you.** Privy mints tokens for every app
on the platform, and creating an app takes a minute. Check the signature without pinning
`audience` to your own app ID and a token minted for an attacker's Privy app authenticates
against your server — the signature is genuine, it was simply never issued for you. `audience`
is the claim that makes this authentication rather than a well-formedness check. Pin `issuer`
and `algorithms` in the same breath.

Verification yields the Privy user ID. Read the wallet address from the verified user's linked
accounts rather than from the request body.

Taking the address from the request body instead is the same class of bug the
`seeker-genesis-token` skill covers in detail: a caller supplies someone else's address
alongside their own valid token and inherits their entitlements.

## Without Wallet UI: the raw protocol

Only relevant if the project talks to `@solana-mobile/mobile-wallet-adapter-protocol` directly.
`@wallet-ui/react-native-kit` wraps all of this, so prefer it in new code.

Two things the wrapper is doing that you then have to do yourself:

1. **Address conversion.** `authorizationResult.accounts[0].address` is base64. Privy needs
   base58, so decode the bytes and re-encode — with `getBase58Decoder()` from `@solana/kit`, or
   `new PublicKey(bytes).toBase58()` on the web3.js stack.
2. **Session management.** Everything runs inside a single `transact` callback, and
   authorization is not cached between calls unless you cache it.

Signing still returns a signed payload that you base64-encode and pass to `login` unchanged —
that part does not differ. Privy's recipe has the full component:
https://docs.privy.io/recipes/solana/adding-solana-mwa

Note that the recipe is written against `@solana/web3.js` and `react-native-quick-base64`.
Neither is needed on the kit stack; `@solana/kit`'s codecs cover the same ground.
</content>
