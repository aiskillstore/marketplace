# Wallet troubleshooting

Failures specific to wallet connection and signing. For build and toolchain failures, see
the `solana-mobile` skill's troubleshooting reference.

## "must be used in a secure context (`https`)"

```
SolanaMobileWalletAdapterError: The mobile wallet adapter protocol must be used in a secure context (`https`).
```

The bundler resolved the protocol package's browser/ESM build instead of its React Native
build. The web build checks for a secure browser context, which never holds in an app.

Confirm the app is running as a development build and not in Expo Go first — that is the
more common cause of this error than any resolution problem.

If it is a genuine resolution issue, force native resolution by removing the ESM output:

```bash
rm -rf node_modules/@solana-mobile/mobile-wallet-adapter-protocol/lib/esm
npx expo run:android
```

This is a workaround, not a fix: it is undone by the next `npm install`. Prefer correcting
the Metro `resolverMainFields` order so the React Native entry point wins, which survives
reinstalls.

## Nothing happens when tapping connect

No wallet app supporting MWA is installed. The tap does register and MWA does start a session
— it then fails to hand off, and by default nothing surfaces in the UI. Confirm in logcat
rather than guessing:

```bash
adb logcat -d --pid=$(adb shell pidof com.your.package) | grep SolanaMobileWalletAdapter
```

The signature is unambiguous:

```
D SolanaMobileWalletAdapterModule: startSession with config null
V LocalAssociationScenario: Creating local association scenario for ws://127.0.0.1:PORT/solana-wallet
E SolanaMobileWalletAdapterModule: Found no installed wallet that supports the mobile wallet protocol
E SolanaMobileWalletAdapterModule: android.content.ActivityNotFoundException: No Activity found
  to handle Intent { act=android.intent.action.VIEW cat=[android.intent.category.BROWSABLE]
  dat=solana-wallet:/... }
```

MWA dispatches an `android.intent.action.VIEW` intent for the `solana-wallet:` scheme. Check
whether anything on the device claims it:

```bash
adb shell pm query-activities --brief -a android.intent.action.VIEW -d "solana-wallet://"
```

`No activities found` means no wallet is installed. Install an MWA-compatible wallet APK, or
test on a physical Android device that has one.

Because the rejection is invisible by default, catch it and show something — a bare
`await connect()` inside a try/catch that only logs looks identical to a dead button.

## Connect rejects immediately

Usually the user dismissing the wallet picker. Check the error before reporting a failure:

```ts
code === 'ERROR_ASSOCIATION_CANCELLED'
message.includes('CancellationException')
message.includes('Local association cancelled by user')
```

Any of these means cancellation. Offer a retry rather than an error dialog.

## "payloads invalid for signing"

In order of likelihood:

1. **Expired blockhash.** They last roughly 60–90 seconds. Fetch a fresh one and rebuild the
   transaction; do not reuse a blockhash across a retry.
2. **`minContextSlot` missing or mismatched.** `signAndSendTransaction` takes it as a second
   argument, and it must come from the same response as the blockhash. On web3.js use
   `getLatestBlockhashAndContext()`; on kit read `context.slot` from `getLatestBlockhash()`.
3. **Malformed transaction.** No fee payer set, or no instructions.

## Signing fails but the wallet never appears

The crypto polyfill is missing or loaded too late. Kit and the MWA protocol both need Web
Crypto, and the failure happens before the wallet is contacted, so it presents as a signing
bug rather than a setup bug.

Check that `react-native-quick-crypto`'s `install()` runs in a module imported before
anything else — see the polyfill sections in [kit.md](kit.md) and [web3js.md](web3js.md) —
and that the app was rebuilt natively after installing it.

## Address renders as garbled text

```
+9pgyt LK...MIiSdpI=
```

On the web3.js stack `account.address` is a `PublicKey` object. Call `.toString()` before
rendering. On the kit stack it is already a string, so this error does not occur.

## Transaction fails only for some recipients

Some wallets refuse transfers to accounts that do not yet exist on chain, since the transfer
must also cover rent for account creation. Test against a known funded address to confirm,
then make sure the transfer amount clears the rent-exempt minimum.

## `RangeError: Maximum call stack size exceeded` when encoding

From `btoa(String.fromCharCode(...bytes))` — spreading a large array exceeds the argument
limit. Use `fromUint8Array` from the wallet package, or kit's `getBase64Decoder()`.

## Session lost on every app restart

Authorization is cached automatically. Losing it each launch means the cache is not
persisting — check that `@react-native-async-storage/async-storage` (or the storage backend
a custom `cache` prop uses) is installed and linked, and that a custom `cache` implementation
is not returning `undefined` unconditionally.
