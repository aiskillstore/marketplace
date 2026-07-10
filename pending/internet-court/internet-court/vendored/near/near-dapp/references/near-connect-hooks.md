# near-connect-hooks

React hooks for NEAR wallet integration using `@hot-labs/near-connect`.

## Installation

```bash
npm install near-connect-hooks @hot-labs/near-connect near-api-js
```

## Setup

Wrap app with `NearProvider`:

```tsx
import { NearProvider } from 'near-connect-hooks';

function App() {
  return (
    <NearProvider config={{ network: 'mainnet' }}>
      <YourApp />
    </NearProvider>
  );
}
```

### NearProvider Config

Accepts all `NearConnector` options. Key options:

```typescript
{
  network?: "mainnet" | "testnet";   // default: "testnet"
  features?: Partial<WalletFeatures>;
  excludedWallets?: string[];
  autoConnect?: boolean;             // default: true
  walletConnect?: { projectId: string; metadata: any };
}
```

Default RPC endpoints:
- mainnet: `https://free.rpc.fastnear.com`
- testnet: `https://test.rpc.fastnear.com`

## useNearWallet() Hook

```tsx
import { useNearWallet } from 'near-connect-hooks';

const {
  // State
  loading,            // boolean — true while initializing
  signedAccountId,    // string — connected account ID, "" if not connected
  network,            // "mainnet" | "testnet"

  // Auth
  signIn,             // () => Promise<void> — shows wallet selector
  signOut,            // () => Promise<void> — disconnects wallet

  // Read-only calls (no wallet required)
  viewFunction,       // (params) => Promise<any>
  getBalance,         // (accountId) => Promise<bigint>
  getAccessKeyList,   // (accountId) => Promise<AccessKeyList>

  // State-changing calls (wallet required)
  callFunction,       // (params) => Promise<FinalExecutionOutcome>
  transfer,           // (params) => Promise<FinalExecutionOutcome>
  addFunctionCallKey, // (params) => Promise<FinalExecutionOutcome>
  deleteKey,          // (params) => Promise<FinalExecutionOutcome>
  signNEP413Message,  // (params) => Promise<SignedMessage>

  // Low-level
  signAndSendTransaction,   // (params) => Promise<FinalExecutionOutcome>
  signAndSendTransactions,  // (transactions) => Promise<FinalExecutionOutcome[]>
  connector,                // NearConnector instance
  provider,                 // JsonRpcProvider instance
} = useNearWallet();
```

## API Details

### viewFunction

Read-only contract call, no wallet needed:

```typescript
const messages = await viewFunction({
  contractId: 'guestbook.testnet',
  method: 'get_messages',
  args: { from_index: '0', limit: '10' }
});
```

### callFunction

State-changing contract call with gas and optional deposit:

```typescript
await callFunction({
  contractId: 'guestbook.testnet',
  method: 'add_message',
  args: { text: 'Hello NEAR!' },
  gas: '30000000000000',        // default: 30 TGas
  deposit: '0',                 // default: "0", in yoctoNEAR
});
```

### transfer

```typescript
await transfer({
  receiverId: 'bob.near',
  amount: '1000000000000000000000000', // 1 NEAR in yoctoNEAR
});
```

### getBalance

```typescript
const balance = await getBalance('alice.near'); // returns bigint (yoctoNEAR)
```

### addFunctionCallKey

```typescript
await addFunctionCallKey({
  publicKey: 'ed25519:...',
  contractId: 'game.near',
  methodNames: ['play', 'claim'],  // empty array = any method
  allowance: '250000000000000000000000', // optional, in yoctoNEAR
});
```

### deleteKey

```typescript
await deleteKey({ publicKey: 'ed25519:...' });
```

### signNEP413Message

```typescript
const signed = await signNEP413Message({
  message: 'Authenticate with MyApp',
  recipient: 'myapp.near',
  nonce: new Uint8Array(32), // unique nonce
});
// signed: { accountId, publicKey, signature }
```

## Full Example: Guestbook dApp

### _app.tsx (Next.js Pages Router)

```tsx
import { NearProvider } from 'near-connect-hooks';

export default function App({ Component, pageProps }) {
  return (
    <NearProvider config={{ network: 'testnet' }}>
      <Navigation />
      <Component {...pageProps} />
    </NearProvider>
  );
}
```

### Navigation Component

```tsx
import { useNearWallet } from 'near-connect-hooks';

export function Navigation() {
  const { signedAccountId, loading, signIn, signOut } = useNearWallet();

  return (
    <nav>
      <button onClick={signedAccountId ? signOut : signIn}>
        {loading ? 'Loading...' : signedAccountId ? `Logout ${signedAccountId}` : 'Login'}
      </button>
    </nav>
  );
}
```

### Page with Contract Interaction

```tsx
import { useState, useEffect } from 'react';
import { useNearWallet } from 'near-connect-hooks';
import { nearToYocto } from 'near-api-js';

const CONTRACT = 'guestbook.testnet';

export default function Home() {
  const { signedAccountId, viewFunction, callFunction } = useNearWallet();
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    viewFunction({
      contractId: CONTRACT,
      method: 'get_messages',
      args: { from_index: '0', limit: '10' },
    }).then(setMessages);
  }, []);

  const addMessage = async (text: string, donation?: number) => {
    await callFunction({
      contractId: CONTRACT,
      method: 'add_message',
      args: { text },
      deposit: donation ? nearToYocto(donation).toString() : '0',
    });
  };

  return (
    <div>
      {signedAccountId ? (
        <button onClick={() => addMessage('Hello!')}>Say Hello</button>
      ) : (
        <p>Connect wallet to post messages</p>
      )}
      {messages.map((msg, i) => (
        <p key={i}>{msg.sender}: {msg.text}</p>
      ))}
    </div>
  );
}
```

## Unit Conversion

Use `near-api-js` utilities for NEAR/yoctoNEAR conversion:

```typescript
import { nearToYocto, yoctoToNear } from 'near-api-js';

nearToYocto(1);    // "1000000000000000000000000"
yoctoToNear("1000000000000000000000000"); // "1"
```
