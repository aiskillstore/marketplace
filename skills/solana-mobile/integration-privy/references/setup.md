# Privy setup on Expo

Everything the Privy Expo SDK needs beyond `npm install`. Each item here fails at a different
point in the app's life, so skipping one produces a symptom that looks unrelated to the cause.

## Dashboard values

| Value | Where | Used as |
| --- | --- | --- |
| App ID | Organization overview, after creating the app | `EXPO_PUBLIC_PRIVY_APP_ID` |
| Client ID | App settings > Clients | `EXPO_PUBLIC_PRIVY_CLIENT_ID` |
| App secret | App settings | **Server only. Never in the app.** |

Two dashboard settings are load-bearing:

- **User management > Authentication > External wallets > SVM (Solana) wallets** must be
  enabled. Off is the default, and while it is off every SIWS login rejects.
- **App settings > Clients > app identifier** must equal `expo.android.package` from
  `app.json`. Privy checks the calling package against the client.

Change the Android package later and the client identifier has to change with it, or the app
stops authenticating on the next build.

## Environment variables

```bash
# .env
EXPO_PUBLIC_PRIVY_APP_ID=your-privy-app-id
EXPO_PUBLIC_PRIVY_CLIENT_ID=your-privy-client-id
```

`EXPO_PUBLIC_*` values are inlined into the JS bundle at build time. That is correct for these
two — they are public client identifiers — and disqualifying for the app secret, which grants
server-side control of the Privy app.

Because they are inlined at build time, editing `.env` requires a bundler restart with
`--clear`, not just a reload.

## Entry point polyfills

Privy and `@solana/kit` both need Web Crypto and `TextEncoder`, and both need them before any
other module runs. Point `main` at a wrapper that installs them first:

```json
{ "main": "./index.js" }
```

```js
// index.js
import './polyfill'
import 'expo-router/entry'
```

```js
// polyfill.js
import 'fast-text-encoding'

import { install } from 'react-native-quick-crypto'

install()
```

```bash
npx expo install fast-text-encoding react-native-quick-crypto
```

Importing the polyfills from a root layout is too late — Expo Router's entry has already
evaluated the route tree by then. The failure shows up as signing errors rather than as a
missing-polyfill error, because the first thing to need crypto is a signature.

## `app.json` plugins

```json
{
  "expo": {
    "android": { "package": "com.example.myapp" },
    "plugins": ["expo-router", "expo-secure-store", "expo-web-browser"],
    "scheme": "myapp"
  }
}
```

`expo-secure-store` backs Privy's token storage; without it sessions do not survive a restart.
`expo-web-browser` backs OAuth login methods. `scheme` is what your SIWS `uri` and the MWA
`AppIdentity.uri` deep link into.

## Metro: the `jose` resolver

Privy pulls in `jose` for JWT handling, which ships several conditional builds. Metro picks the
Node build by default and it does not run in React Native. Force the browser condition:

```js
// metro.config.js
const { getDefaultConfig } = require('expo/metro-config')

const config = getDefaultConfig(__dirname)
const defaultResolveRequest = config.resolver.resolveRequest

config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (moduleName === 'jose') {
    const ctx = { ...context, unstable_conditionNames: ['browser'] }

    return ctx.resolveRequest(ctx, moduleName, platform)
  }

  return defaultResolveRequest
    ? defaultResolveRequest(context, moduleName, platform)
    : context.resolveRequest(context, moduleName, platform)
}

module.exports = config
```

Chaining through `defaultResolveRequest` rather than replacing it matters when another plugin —
NativeWind, Uniwind, a monorepo resolver — already set one. Overwriting it silently disables
that plugin's resolution.

## Peer dependencies

`@privy-io/expo` declares a wide peer set and it changes between minor versions. Read the peers
for the version you are installing instead of copying a list:

```bash
npm view @privy-io/expo@<version> peerDependencies
```

As of `0.70.x` that includes `@privy-io/expo-native-extensions`, `expo-apple-authentication`,
`expo-application`, `expo-clipboard`, `expo-crypto`, `expo-linking`, `expo-secure-store`,
`expo-web-browser`, `permissionless`, `react-native-passkeys`, `react-native-qrcode-styled`,
`react-native-safe-area-context`, `react-native-svg`, `react-native-webview`, and a pinned
`viem`. Several are pinned to exact versions, so `npx expo install` will not always resolve
them for you — install the pinned version the peer range names.

## Rebuild, then verify

```bash
npx expo run:android
```

Native modules arrived, so a Metro reload is not enough. Once it boots, check the pieces in
order — each depends on the one above it:

1. `usePrivy().isReady` turns `true`. If it stays `false`, the SDK never initialized: check
   the app ID and client ID reached the bundle.
2. `usePrivy().error` is `null`. A non-null error here is almost always secure-store access,
   meaning the plugin is missing or the app was not rebuilt.
3. `useMobileWallet().connect()` returns an account. If not, this is an MWA problem, not a
   Privy one — see the `solana-mobile-wallet` skill.
4. SIWS login succeeds. Failures at this point are covered in
   [troubleshooting.md](troubleshooting.md).
