# React Bindings (@near-kit/react)

React hooks and providers for near-kit.

## Table of Contents
- [Installation](#installation)
- [Provider & Context](#provider--context)
- [View Hooks](#view-hooks)
- [Mutation Hooks](#mutation-hooks)
- [Account & Contract Hooks](#account--contract-hooks)
- [React Query Integration](#react-query-integration)
- [SWR Integration](#swr-integration)
- [Wallet Integration](#wallet-integration)
- [SSR / Next.js](#ssr--nextjs)

---

## Installation

```bash
npm install @near-kit/react
```

---

## Provider & Context

### NearProvider

Wrap your app to provide a Near client to all components:

```tsx
import { NearProvider } from "@near-kit/react"

// With configuration
<NearProvider config={{ network: "testnet" }}>
  <App />
</NearProvider>

// With existing Near instance
const near = new Near({ network: "testnet", privateKey: "..." })
<NearProvider near={near}>
  <App />
</NearProvider>
```

### useNear

Access the Near client for direct API calls or library integration:

```tsx
function MyComponent() {
  const near = useNear()
  // near.view(), near.call(), near.send(), near.transaction()
}
```

---

## View Hooks

### useView

Call view methods on contracts:

```tsx
const { data, isLoading, error, refetch } = useView<{ account_id: string }, string>({
  contractId: "token.testnet",
  method: "ft_balance_of",
  args: { account_id: "alice.testnet" },
  enabled: true, // optional
})
```

### useBalance

Fetch account NEAR balance:

```tsx
const { data: balance, isLoading } = useBalance({
  accountId: "alice.testnet",
})
```

### useAccountExists

Check if account exists:

```tsx
const { data: exists } = useAccountExists({
  accountId: "alice.testnet",
})
```

---

## Mutation Hooks

### useCall

Call change methods on contracts:

```tsx
const { mutate, isPending, isSuccess, isError, error, reset } = useCall<
  { amount: number },
  void
>({
  contractId: "counter.testnet",
  method: "increment",
  options: { gas: "30 Tgas" }, // optional defaults
})

await mutate({ amount: 1 })
await mutate({ amount: 1 }, { attachedDeposit: "0.1 NEAR" }) // override
```

### useSend

Send NEAR tokens:

```tsx
const { mutate: send, isPending } = useSend()

await send("bob.testnet", "1 NEAR")
```

---

## Account & Contract Hooks

### useAccount

Get current connected account state:

```tsx
const { accountId, isConnected, isLoading, refetch } = useAccount()
```

### useContract

Get typed contract instance with full TypeScript inference:

```tsx
import type { Contract } from "near-kit"

type MyContract = Contract<{
  view: {
    get_balance: (args: { account_id: string }) => Promise<string>
  }
  call: {
    transfer: (args: { to: string; amount: string }) => Promise<void>
  }
}>

function TokenBalance() {
  const contract = useContract<MyContract>("token.testnet")
  const balance = await contract.view.get_balance({ account_id: "..." })
}
```

---

## React Query Integration

For caching, polling, background refetching, use React Query with `useNear()`:

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useNear } from "@near-kit/react"

function useContractView<TArgs extends object, TResult>(
  contractId: string,
  method: string,
  args: TArgs
) {
  const near = useNear()
  return useQuery({
    queryKey: ["near", "view", contractId, method, args],
    queryFn: () => near.view<TResult>(contractId, method, args),
  })
}

function useContractCall<TArgs extends object, TResult>(
  contractId: string,
  method: string
) {
  const near = useNear()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (args: TArgs) => near.call<TResult>(contractId, method, args),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["near", "view", contractId] })
    },
  })
}
```

### With Polling

```tsx
const { data: balance } = useQuery({
  queryKey: ["near", "balance", accountId],
  queryFn: () => near.getBalance(accountId),
  refetchInterval: 5000,
})
```

---

## SWR Integration

Lighter alternative using SWR:

```tsx
import useSWR from "swr"
import useSWRMutation from "swr/mutation"
import { useNear } from "@near-kit/react"

function useContractView<TArgs extends object, TResult>(
  contractId: string,
  method: string,
  args: TArgs
) {
  const near = useNear()
  return useSWR(
    ["near", "view", contractId, method, JSON.stringify(args)],
    () => near.view<TResult>(contractId, method, args)
  )
}

function useContractCall<TArgs extends object, TResult>(
  contractId: string,
  method: string
) {
  const near = useNear()
  return useSWRMutation(
    ["near", "call", contractId, method],
    (_key, { arg }: { arg: TArgs }) =>
      near.call<TResult>(contractId, method, arg)
  )
}
```

---

## Wallet Integration

### With Wallet Selector

```tsx
import { setupWalletSelector } from "@near-wallet-selector/core"
import { fromWalletSelector } from "near-kit"

const selector = await setupWalletSelector({
  network: "testnet",
  modules: [/* wallet modules */],
})
const wallet = await selector.wallet()

<NearProvider
  config={{
    network: "testnet",
    wallet: fromWalletSelector(wallet),
  }}
>
  <App />
</NearProvider>
```

### With HOT Connect

```tsx
import { setupNearConnect } from "@hot-labs/near-connect"
import { fromHotConnect } from "near-kit"

const connect = await setupNearConnect({ network: "testnet" })

<NearProvider
  config={{
    network: "testnet",
    wallet: fromHotConnect(connect),
  }}
>
  <App />
</NearProvider>
```

---

## SSR / Next.js

Package is marked with `"use client"`. Wrap provider in client component:

```tsx
// app/providers.tsx
"use client"

import { NearProvider } from "@near-kit/react"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NearProvider config={{ network: "testnet" }}>
      {children}
    </NearProvider>
  )
}
```
