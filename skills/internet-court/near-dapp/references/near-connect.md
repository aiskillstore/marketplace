# @hot-labs/near-connect

Zero-dependency, secure wallet connector for NEAR blockchain.

## Installation

```bash
npm install @hot-labs/near-connect
# or
yarn add @hot-labs/near-connect
```

CDN alternative:

```html
<script type="importmap">
  { "imports": { "@hot-labs/near-connect": "https://esm.sh/@hot-labs/near-connect" } }
</script>
<script type="module">
  import { NearConnector } from "@hot-labs/near-connect";
</script>
```

## Quick Start

```typescript
import { NearConnector } from "@hot-labs/near-connect";

const connector = new NearConnector({ network: "mainnet" });

connector.on("wallet:signIn", async (t) => {
  const wallet = await connector.wallet();
  const address = t.accounts[0].accountId;
});

connector.on("wallet:signOut", async () => {});

// Check if already signed in
try {
  const wallet = await connector.wallet();
  const accounts = await wallet.getAccounts();
  if (accounts.length > 0) {
    console.log("Already signed in:", accounts[0].accountId);
  }
} catch (e) {
  // Not signed in
}
```

## NearConnector Options

```typescript
interface NearConnectorOptions {
  network?: "mainnet" | "testnet";
  features?: Partial<WalletFeatures>;      // Filter wallets by features
  excludedWallets?: string[];              // Wallet IDs to exclude
  autoConnect?: boolean;                   // Default: true
  walletConnect?: { projectId: string; metadata: any };
  signIn?: { contractId?: string; methodNames?: string[] };
  footerBranding?: null | { icon: string; heading: string; link: string; linkText: string };
}
```

## NearConnector Methods

```typescript
// Connect to wallet (shows selector popup if no ID provided)
await connector.connect(walletId?: string): Promise<NearWalletBase>

// Disconnect current wallet
await connector.disconnect(): Promise<void>

// Get current or specific wallet instance
await connector.wallet(id?: string): Promise<NearWalletBase>

// Show wallet selector popup
await connector.selectWallet(): Promise<string>

// Switch network (disconnects current wallet)
await connector.switchNetwork(network: "mainnet" | "testnet"): Promise<void>

// Get available wallets filtered by features
connector.availableWallets: NearWalletBase[]
```

## Events

```typescript
connector.on("wallet:signIn", ({ wallet, accounts, success }) => {});
connector.on("wallet:signOut", ({ success }) => {});
connector.on("selector:walletsChanged", () => {});

// Also: once(), off(), removeAllListeners()
```

## Wallet Interface

All wallets implement `NearWalletBase`:

```typescript
interface NearWalletBase {
  manifest: WalletManifest;

  signIn(data?: {
    network?: Network;
    contractId?: string;
    methodNames?: string[];
  }): Promise<Account[]>;

  signOut(data?: { network?: Network }): Promise<void>;

  getAccounts(data?: { network?: Network }): Promise<Account[]>;

  signAndSendTransaction(params: {
    signerId?: string;
    receiverId: string;
    actions: Action[];
    network?: Network;
  }): Promise<FinalExecutionOutcome>;

  signAndSendTransactions(params: {
    transactions: Transaction[];
    network?: Network;
  }): Promise<FinalExecutionOutcome[]>;

  signMessage(params: {
    message: string;
    recipient: string;
    nonce: Uint8Array;
    network?: Network;
  }): Promise<SignedMessage>;
}
```

## Types

```typescript
interface Account {
  accountId: string;
  publicKey: string;
}

interface SignedMessage {
  accountId: string;
  publicKey: string;
  signature: string;
}

type Network = "mainnet" | "testnet";
```

## Wallet Features Filter

```typescript
const connector = new NearConnector({
  features: { signMessage: true, testnet: true }
});
```

Available features: `signMessage`, `signTransaction`, `signAndSendTransaction`, `signAndSendTransactions`, `signInWithoutAddKey`, `testnet`, `mainnet`.

## Action Formats

Two formats supported for `signAndSendTransaction` actions:

**1. near-wallet-selector format (legacy):**
```typescript
{
  type: "FunctionCall",
  params: {
    methodName: "ft_transfer",
    args: { receiver_id: "bob.near", amount: "1000000000000000000000000" },
    gas: "30000000000000",
    deposit: "1"
  }
}
```

**2. near-api-js format (recommended):**
```typescript
import { transactions } from "near-api-js";
transactions.functionCall("ft_transfer", { receiver_id: "bob.near", amount: "1000000000000000000000000" }, "30000000000000", "1");
```

## WalletConnect Support (Optional)

```typescript
import SignClient from "@walletconnect/sign-client";
const walletConnect = SignClient.init({ projectId: "...", metadata: {} });

const connector = new NearConnector({ walletConnect });
```

Some wallets require WalletConnect to appear as connection options.

## Supported Wallets

HOT Wallet, Meteor Wallet, Intear Wallet, MyNearWallet, Nightly Wallet, NEAR Mobile, Unity Wallet, OKX Wallet, and any wallet via WalletConnect.

## Transaction Example

```typescript
const connector = new NearConnector({ network: "mainnet" });
await connector.connect();

const wallet = await connector.wallet();
const result = await wallet.signAndSendTransaction({
  receiverId: "contract.near",
  actions: [
    {
      type: "FunctionCall",
      params: {
        methodName: "ft_transfer",
        args: { receiver_id: "bob.near", amount: "1000000000000000000000000" },
        gas: "30000000000000",
        deposit: "1"
      }
    }
  ]
});

console.log("Transaction hash:", result.transaction.hash);
```
