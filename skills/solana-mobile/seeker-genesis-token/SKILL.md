---
name: seeker-genesis-token
description: Verify Seeker device ownership by checking for the Seeker Genesis Token (SGT) with Sign-in-with-Solana and server-side token verification. Use when gating content or rewards to Seeker owners, verifying a user holds an SGT, adding anti-Sybil checks to a Solana mobile app, or implementing one-claim-per-device logic.
---

# Seeker Genesis Token verification

The Seeker Genesis Token (SGT) is a Token-2022 NFT minted once per Seeker device. Holding one
is evidence of owning a Seeker, which makes it useful for gating rewards and for
one-claim-per-device logic.

Verification has two halves, and **both are required**:

1. **Prove the user controls the wallet** — Sign-in-with-Solana (SIWS)
2. **Prove that wallet holds an SGT** — inspect the wallet's Token-2022 mints

Doing only the second means anyone can submit a real Seeker owner's public address and pass.
Doing only the first proves wallet control but says nothing about a device.

## This must run on a server

**Never decide entitlement client-side.** A client can be patched, so a client-side `hasSGT`
boolean is worth nothing. The client's job is to collect a signature; the server verifies it
and owns the result.

Requirements:

- A backend you control that can make Solana mainnet RPC calls
- Storage for nonces and claim records
- An RPC endpoint. A paid provider helps, since the check may enumerate many token accounts —
  keep that key server-side only, never in an `EXPO_PUBLIC_*` variable

## Prerequisites

A working wallet connection. If the app has none, use the `solana-mobile-wallet` skill first;
this skill assumes `useMobileWallet()` is available.

Testing needs a physical Seeker device — an emulator cannot hold an SGT. Plan for a code path
you can exercise without one, such as a server-side allowlist in development.

## Step 1: issue a nonce from the server

The nonce must be **server-generated, single-use, and short-lived**. A client-generated or
reusable nonce makes the signature replayable, which defeats the exercise.

```ts
// POST /api/siws/nonce
const nonce = crypto.randomBytes(16).toString('hex')
await store.put(nonce, { issuedAt: Date.now(), used: false }, { ttlSeconds: 300 })
return { nonce }
```

## Step 2: sign in on the client

`signIn` from the wallet hook authorizes and proves ownership in a single prompt:

```ts
import { useMobileWallet } from '@wallet-ui/react-native-kit'

const { signIn } = useMobileWallet()

const output = await signIn({
  address: account.address.toString(),
  chainId: 'solana:mainnet',
  domain: 'yourdapp.com',
  issuedAt: new Date().toISOString(),
  nonce, // from step 1
  statement: 'Sign in to verify Seeker ownership',
  uri: 'https://yourdapp.com',
  version: '1',
})
```

`chainId` is pinned to `solana:mainnet` deliberately rather than taken from the hook's `chain`:
SGTs exist only on mainnet, so a signature scoped to devnet proves nothing about a device.

This is the fully-specified payload, not the short `signIn` form — `nonce`, `domain`, and
`version` are what make the signature non-replayable and bind it to your app. The
`solana-mobile-wallet` skill covers both forms and when each is appropriate.

Post `output` to the server.

## Step 3: verify the signature on the server

```bash
npm install @solana/wallet-standard-util
```

```ts
import { verifySignIn } from '@solana/wallet-standard-util'

function verifySiws(payload, result) {
  return verifySignIn(payload, {
    account: { ...result.account, publicKey: new Uint8Array(result.account.publicKey) },
    signature: new Uint8Array(result.signature),
    signedMessage: new Uint8Array(result.signedMessage),
  })
}
```

## Step 4: check the wallet for an SGT

See [references/sgt-verification.md](references/sgt-verification.md) for the full
implementation. It confirms three properties of a Token-2022 mint — mint authority, metadata
pointer, and token group membership — and all three must match.

## Step 5: combine the checks correctly

This is where the subtle bug lives. The address whose SGT you check **must be the address that
signed**, read out of the verified payload — not an address the client sent alongside it:

```ts
async function verifySeekerUser({ payload, result }) {
  // 1. The nonce must be one we issued, unused, and unexpired.
  const record = await store.get(payload.nonce)
  if (!record || record.used) throw new Error('Invalid or reused nonce.')
  await store.markUsed(payload.nonce)

  // 2. The signature must be valid for that payload.
  if (!verifySiws(payload, result)) throw new Error('Invalid signature.')

  // 3. The domain must be ours, or a signature farmed by another site would pass.
  if (payload.domain !== 'yourdapp.com') throw new Error('Wrong domain.')

  // 4. Check the SGT against the *signed* address only.
  const { hasSGT, mintAddress } = await checkWalletForSGT(payload.address)

  return { address: payload.address, hasSGT, mintAddress }
}
```

Taking the address from anywhere other than the verified payload lets a caller submit a real
Seeker owner's address with their own signature and be granted access.

## Anti-Sybil: one claim per device

An SGT is per-device, so the **mint address** is the device identity. Store that, not the
wallet address — a wallet can hold a different SGT later, and a device's SGT can move between
wallets.

```ts
const { hasSGT, mintAddress } = await verifySeekerUser({ payload, result })
if (!hasSGT) throw new Error('No Seeker Genesis Token found.')

if (await claims.exists(mintAddress)) throw new Error('This device has already claimed.')
await claims.insert({ claimedAt: new Date(), mintAddress })
```

Have `checkWalletForSGT` return the mint address rather than a bare boolean — see the end of
the reference file.

## Reference material

- [references/sgt-verification.md](references/sgt-verification.md) — full verification
  implementation, SGT constants, standard-RPC and Helius variants

## Related skills

- `solana-mobile-wallet` — wallet connection and the `signIn` payload builder
- `seeker-domains` — `.skr` domain resolution, which Seeker users have by default

## Links

- Detecting Seeker users: https://docs.solanamobile.com/react-native/detecting-seeker-users
- Sign-in-with-Solana spec: https://github.com/phantom/sign-in-with-solana
