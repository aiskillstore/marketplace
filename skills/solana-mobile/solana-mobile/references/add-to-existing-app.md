# Adding Solana to an existing Expo app

For projects that already have an Expo app and need wallet support added. If there is no
project yet, `npx solana-mobile@latest create` does all of this — use it instead.

Before starting, confirm the app is not depending on Expo Go. MWA needs a development build.

## 1. Compare against a template first

The fastest way to get this right is to scaffold the matching template somewhere temporary
and diff the wiring against the existing app:

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-wallet --skip-install
```

Files worth comparing: `index.js`, `polyfill.js`, the `main` field in `package.json`,
`metro.config.js`, and the app-providers module. This catches version-specific details that
prose goes stale on.

## 2. Install dependencies

**Use kit** unless the app's Solana client is already `@solana/web3.js`. This is what
`expo-kit-minimal` ships:

```bash
npm install @wallet-ui/react-native-kit @solana/kit @tanstack/react-query react-native-quick-crypto
```

Add `@solana-program/memo` or other program clients as you need instruction builders.

Only if the app is already committed to web3.js — matching an existing client beats mixing two:

```bash
npm install @wallet-ui/react-native-web3js @solana/web3.js @tanstack/react-query react-native-quick-crypto
```

`react-native-quick-crypto` is a native module. It needs a rebuild, not just a Metro restart.

## 3. Install the crypto polyfill

Both stacks need Web Crypto before any Solana code runs. Put `install()` in its own module so
import ordering cannot be reshuffled by a formatter, linter, or import-sorting rule:

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

Then point `package.json` at it:

```json
{
  "main": "./index.js"
}
```

For a non-Expo-Router app, replace `expo-router/entry` with the app's existing entry import
(`registerRootComponent`, or whatever it uses today) — the requirement is only that the
polyfill import comes first.

Skipping this, or relying on an import-order comment inside a file that has other imports,
produces signing failures that look like wallet bugs: the crypto call fails before the wallet
is ever contacted.

## 4. Mount the provider

Wrap the app in `MobileWalletProvider`, above anything that calls `useMobileWallet`. The
props differ between the two stacks:

```tsx
// Kit
import {
  type AppIdentity,
  createSolanaDevnet,
  MobileWalletProvider,
} from '@wallet-ui/react-native-kit'

const identity: AppIdentity = { name: 'My App' }
const cluster = createSolanaDevnet({ url: 'https://api.devnet.solana.com' })

<MobileWalletProvider cluster={cluster} identity={identity}>
  {children}
</MobileWalletProvider>
```

Use the `createSolana*` helpers rather than a hand-written object — a `SolanaCluster` also needs
a `label`, and the helpers supply it. `createSolanaMainnet` requires an explicit `url`.

```tsx
// Legacy web3.js
import { MobileWalletProvider } from '@wallet-ui/react-native-web3js'

<MobileWalletProvider
  chain="solana:devnet"
  endpoint="https://api.devnet.solana.com"
  identity={{ name: 'My App', uri: 'myapp://myapp' }}
>
  {children}
</MobileWalletProvider>
```

`identity.uri` should be a real deep link for the app — wallets display it to the user during
authorization, so a placeholder both looks wrong and can read as a phishing attempt.

Most apps also want `QueryClientProvider` from `@tanstack/react-query` above the wallet
provider, since the hook examples in the `solana-mobile-wallet` skill use queries and
mutations.

## 5. Set the cluster from configuration

Hard-coding a cluster into a component is how apps ship devnet-only code to production, or
the reverse. Read it from the environment:

```bash
# .env
EXPO_PUBLIC_SOLANA_CLUSTER=devnet
EXPO_PUBLIC_SOLANA_RPC_URL=https://api.devnet.solana.com
```

`EXPO_PUBLIC_`-prefixed variables are inlined into the bundle at build time, so anyone with
the APK can read them. **Never put a paid RPC key or any other secret in one.** Route
authenticated RPC through a backend you control and keep the key there.

## 6. Build

```bash
npx expo prebuild --clean
npx expo run:android
```

`prebuild --clean` regenerates the native projects, which is needed after adding native
modules like `react-native-quick-crypto`. It discards manual edits to `android/` and `ios/`,
so commit those first or reapply them through a config plugin.

## 7. Verify

```bash
npx solana-mobile@latest doctor
```

Then connect a wallet in the app. If connect does nothing, the emulator has no wallet app
installed — see the main skill. For anything else, see
[troubleshooting.md](troubleshooting.md).

Once the app builds and a wallet connects, use the `solana-mobile-wallet` skill for the
connection and transaction code.
