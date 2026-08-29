# Privy troubleshooting

Failures specific to Privy on top of MWA. For connection and signing failures that would
happen without Privy in the app, see the `solana-mobile-wallet` skill's troubleshooting
reference — start there if the wallet never opens, since Privy is not involved until after a
signature comes back.

## `isReady` never becomes `true`

The SDK did not initialize. In order of likelihood:

1. **`appId` is `undefined`.** `EXPO_PUBLIC_*` values are inlined at bundle time, so editing
   `.env` and reloading changes nothing — restart with `npx expo start --clear`. Throwing in
   `AppProviders` when either variable is missing turns this into an immediate, obvious error.
2. **The app was not rebuilt** after installing the SDK. Native modules need
   `npx expo run:android`, not a reload.
3. **Secure store is missing.** Check `usePrivy().error` — storage failures surface there
   rather than as a thrown exception.

## SIWS login rejects even though the wallet signed

The wallet prompt appeared, the user approved, and `login` still throws. Work through these in
order — the first two are dashboard state, not code:

1. **SVM wallets are disabled.** User management > Authentication > External wallets >
   **SVM (Solana) wallets**. Off by default. This is the single most common cause.
2. **The app identifier does not match.** App settings > Clients must carry the
   `expo.android.package` value from `app.json`. Renaming the Android package without updating
   the client breaks login on the next build.
3. **The address is base64.** Passing `account.addressBase64` instead of `account.address`
   sends MWA's wire format to a verifier expecting base58.
4. **The signature was re-encoded.** `fromUint8Array` produces base64, which is what Privy
   wants. Converting to base58, or slicing the payload to 64 bytes first, both fail
   verification.
5. **The message was rebuilt.** Only the exact string from `generateMessage` verifies —
   Privy's nonce is inside it. Signing a message you assembled yourself always rejects.

## `Cannot find module 'jose'` or a crypto error from `jose`

Metro resolved the Node build. Add the `jose` browser-condition resolver to
`metro.config.js` — see [setup.md](setup.md) — then restart with `--clear`, since Metro caches
resolution results.

If a resolver is already configured for something else, chain through it rather than
overwriting it; a bare assignment silently disables the other plugin's resolution.

## Signing fails before the wallet ever opens

The crypto polyfill is missing or loaded too late. Privy and `@solana/kit` both need Web
Crypto, and the failure happens before MWA is contacted, so it reads as a Privy bug rather
than a setup bug.

`react-native-quick-crypto`'s `install()` must run from the module `main` points at, before
`expo-router/entry`. Importing it from a root layout is too late.

## The session survives but the wallet does not

`usePrivy().user` is populated on launch while `useMobileWallet().account` is `undefined`.
This is normal, not a bug: Privy persists its session in secure store and MWA persists its
authorization separately, and they expire on different schedules.

Handle it explicitly. A signed-in user with no connected wallet can still read their profile,
but every signing path needs to reconnect first. Treating `user` as proof of a usable wallet
produces a button that throws.

## Sign-out leaves the user signed in

Both sides need clearing:

```tsx
await logout()
await disconnect()
```

`disconnect()` alone leaves a live Privy session. `logout()` alone leaves the wallet
authorized, so the next sign-in completes with no prompt and looks like the sign-out never
happened.

## Login creates a second account instead of linking

`login` was called where `link` belonged. For a user who already has a Privy account from
another method, use `useLinkWithSiws().link` — `useLoginWithSiws().login` starts a fresh
account owned by the wallet and the original becomes unreachable from the app.

Pass `disableSignup: true` to `login` to make this loud: it rejects unknown wallets instead of
signing them up.

## A peer dependency version conflict on install

`@privy-io/expo` pins several peers to exact versions — `viem` and
`@privy-io/expo-native-extensions` in particular — and the pins move between minor releases.
`npx expo install` resolves against the Expo SDK, not against Privy's pins, so the two can
disagree.

Read the peers for the exact version being installed and match them:

```bash
npm view @privy-io/expo@<version> peerDependencies
```
</content>
