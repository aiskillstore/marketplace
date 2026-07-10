# Wallet Integration

Browser wallet integration using HOT Connect or Wallet Selector.

## Table of Contents
- [HOT Connect](#hot-connect)
- [Wallet Selector](#wallet-selector)
- [Universal Factory Pattern](#universal-factory-pattern)

---

## HOT Connect

Modern wallet connector with iframe isolation and WalletConnect v2.

### Installation

```bash
npm install @hot-labs/near-connect
```

### Basic Setup

```typescript
import { NearConnector } from "@hot-labs/near-connect"
import { Near, fromHotConnect } from "near-kit"

// 1. Initialize Connector
const connector = new NearConnector({
  network: "mainnet", // or "testnet"
  walletConnect: {
    projectId: "your-walletconnect-project-id",
    metadata: {
      name: "My dApp",
      description: "Built with near-kit",
      url: "https://myapp.com",
      icons: ["https://myapp.com/icon.png"],
    },
  },
})

// 2. Listen for Sign In
connector.on("wallet:signIn", async (event) => {
  const accountId = event.accounts[0]?.accountId
  if (!accountId) return

  console.log("Connected:", accountId)

  // 3. Create Near Instance
  const near = new Near({
    network: "mainnet",
    wallet: fromHotConnect(connector),
  })

  // 4. Use near-kit API (same as server-side)
  const balance = await near.view("token.near", "ft_balance_of", {
    account_id: accountId,
  })

  await near.call(
    "guestbook.near",
    "add_message",
    { text: "Hello!" },
    { signerId: accountId, gas: "30 Tgas" }
  )

  await near.send("friend.near", "1 NEAR")
})

// 5. Listen for Sign Out
connector.on("wallet:signOut", () => {
  console.log("Disconnected")
})

// 6. Trigger Connection (in UI)
// <button onClick={() => connector.show()}>Connect</button>
connector.connect()
```

### React Component Example

```tsx
import { useEffect, useState } from "react"
import { NearConnector } from "@hot-labs/near-connect"
import { Near, fromHotConnect } from "near-kit"

function WalletConnector() {
  const [near, setNear] = useState<Near | null>(null)
  const [accountId, setAccountId] = useState<string | null>(null)

  useEffect(() => {
    const connector = new NearConnector({
      network: "mainnet",
      walletConnect: {
        projectId: "your-project-id",
        metadata: {
          name: "My App",
          description: "Near-kit powered dApp",
          url: window.location.origin,
          icons: [],
        },
      },
    })

    connector.on("wallet:signIn", (event) => {
      const account = event.accounts[0]?.accountId
      if (account) {
        setAccountId(account)
        setNear(new Near({
          network: "mainnet",
          wallet: fromHotConnect(connector),
        }))
      }
    })

    connector.on("wallet:signOut", () => {
      setAccountId(null)
      setNear(null)
    })
  }, [])

  return (
    <div>
      {accountId ? (
        <p>Connected: {accountId}</p>
      ) : (
        <button onClick={() => connector.show()}>Connect Wallet</button>
      )}
    </div>
  )
}
```

---

## Wallet Selector

Traditional NEAR wallet integration with multiple wallet support.

### Installation

```bash
npm install @near-wallet-selector/core @near-wallet-selector/modal-ui
# Add wallet modules as needed:
npm install @near-wallet-selector/my-near-wallet
npm install @near-wallet-selector/here-wallet
npm install @near-wallet-selector/meteor-wallet
```

### Basic Setup

```typescript
import { setupWalletSelector } from "@near-wallet-selector/core"
import { setupModal } from "@near-wallet-selector/modal-ui"
import { setupMyNearWallet } from "@near-wallet-selector/my-near-wallet"
import { setupHereWallet } from "@near-wallet-selector/here-wallet"
import { Near, fromWalletSelector } from "near-kit"

// 1. Setup Wallet Selector
const selector = await setupWalletSelector({
  network: "testnet",
  modules: [
    setupMyNearWallet(),
    setupHereWallet(),
  ],
})

// 2. Setup Modal (optional, for UI)
const modal = setupModal(selector, {
  contractId: "guestbook.near-examples.testnet",
})

// 3. Show Modal to Connect
modal.show()

// 4. Listen for Account Changes
const subscription = selector.store.observable.subscribe(async (state) => {
  if (state.accounts.length > 0) {
    const accountId = state.accounts[0]?.accountId
    if (!accountId) return

    // 5. Get Wallet Instance
    const wallet = await selector.wallet()

    // 6. Create Near Instance
    const near = new Near({
      network: "testnet",
      wallet: fromWalletSelector(wallet),
    })

    // 7. Use near-kit API
    await near.call(
      "guestbook.near-examples.testnet",
      "add_message",
      { text: "Hello from Wallet Selector" },
      { signerId: accountId, gas: "30 Tgas" }
    )
  }
})
```

### Cleanup

```typescript
// Unsubscribe when component unmounts
subscription.unsubscribe()
```

---

## Universal Factory Pattern

Write once, run anywhere - same code for server and browser.

```typescript
import { Near, fromHotConnect, fromWalletSelector, type WalletConnection, type PrivateKey } from "near-kit"

type NearConfig =
  | { env: "server"; privateKey: PrivateKey; signerId: string }
  | { env: "browser"; wallet: WalletConnection }

function createNear(config: NearConfig): Near {
  if (config.env === "server") {
    return new Near({
      network: "mainnet",
      privateKey: config.privateKey,
      defaultSignerId: config.signerId,
    })
  } else {
    return new Near({
      network: "mainnet",
      wallet: config.wallet,
    })
  }
}

// Business logic works in ANY environment
async function addMessage(near: Near, signerId: string, text: string) {
  return await near.call(
    "guestbook.near",
    "add_message",
    { text },
    { signerId, gas: "30 Tgas" }
  )
}

// Server usage
const serverNear = createNear({
  env: "server",
  privateKey: "ed25519:...",
  signerId: "bot.near",
})
await addMessage(serverNear, "bot.near", "From server")

// Browser usage (after wallet connect)
const browserNear = createNear({
  env: "browser",
  wallet: fromHotConnect(connector), // or fromWalletSelector(wallet)
})
await addMessage(browserNear, "user.near", "From browser")
```