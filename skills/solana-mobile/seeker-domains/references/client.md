# Frontend Implementation Reference

React Native implementation for .skr domain resolution with Mobile Wallet Adapter integration.

## Framework Note

This reference shows React Native implementation. **For other frontends**, the same pattern applies—you're simply making two API calls to the backend:

- `POST /api/resolve-domain` with `{ domain: "alice.skr" }` → returns `{ address: "..." }`
- `POST /api/resolve-address` with `{ address: "5FHw..." }` → returns `{ domain: "alice.skr" }`

Adapt this to your frontend framework:
- **React (web)**: Use `fetch` or `axios` in a custom hook
- **Vue**: Use composables with `fetch`
- **Svelte**: Use stores or `fetch` in `onMount`
- **Angular**: Use HttpClient in a service
- **Plain JS**: Use `fetch` directly

The core logic is identical—just HTTP POST requests to your backend.

## Domain Resolution Hook

Create a custom hook to handle API calls to the backend:

```typescript
// hooks/use-domain-lookup.ts
import { useState } from 'react';

// 10.0.2.2 is the Android emulator's alias for the host machine's localhost.
// Set EXPO_PUBLIC_API_URL per environment rather than committing either value.
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:3000';

interface DomainLookupResult {
  address?: string;
  domain?: string;
  error?: string;
}

export function useDomainLookup() {
  const [loading, setLoading] = useState(false);

  /**
   * Resolve .skr domain to wallet address
   * @param domain - Domain name (with or without .skr extension)
   * @returns Wallet address or error
   */
  const resolveDomain = async (domain: string): Promise<DomainLookupResult> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/resolve-domain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain }),
      });

      if (!response.ok) {
        const error = await response.json();
        return { error: error.error || 'Failed to resolve domain' };
      }

      const data = await response.json();
      return { address: data.address };
    } catch (error) {
      console.error('Error resolving domain:', error);
      return { error: 'Network request failed' };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reverse lookup: resolve wallet address to .skr domain
   * @param address - Solana wallet address (base58)
   * @returns .skr domain name or error
   */
  const resolveAddress = async (address: string): Promise<DomainLookupResult> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/resolve-address`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address }),
      });

      if (!response.ok) {
        const error = await response.json();
        return { error: error.error || 'Failed to resolve address' };
      }

      const data = await response.json();
      return { domain: data.domain };
    } catch (error) {
      console.error('Error resolving address:', error);
      return { error: 'Network request failed' };
    } finally {
      setLoading(false);
    }
  };

  return {
    resolveDomain,
    resolveAddress,
    loading,
  };
}
```

## Resolving directly, without a backend

For a prototype, the app can resolve on its own. The Kit resolver in
[kit-resolver.md](kit-resolver.md) uses only Kit's codecs, `@noble/hashes`, and `DataView` — no
`Buffer`, `TextEncoder`, or Node built-ins — so it needs no polyfills of its own beyond whatever
`@solana/kit` already requires in your app.

```typescript
// hooks/use-resolve-address.ts
import { useQuery } from '@tanstack/react-query';
import { address, createSolanaRpc } from '@solana/kit';
import { resolveSkrNames } from '../utils/skr';

// .skr lives on mainnet regardless of the cluster the rest of the app targets.
const rpc = createSolanaRpc(process.env.EXPO_PUBLIC_SOLANA_MAINNET_RPC_URL!);

export function useResolveAddress(walletAddress?: string) {
  return useQuery({
    queryKey: ['skr-name', walletAddress],
    enabled: !!walletAddress,
    staleTime: 1000 * 60 * 60, // names change rarely
    queryFn: async () => {
      const names = await resolveSkrNames(rpc, address(walletAddress!));
      return names[0] ?? null; // already sorted, so this is stable
    },
  });
}
```

Two caveats before shipping this rather than the proxy:

- The RPC URL ships inside the APK. `EXPO_PUBLIC_*` is readable by anyone who unzips it, so this
  only works with an endpoint you do not mind exposing.
- Reverse lookup calls `getProgramAccounts`, which many providers restrict. A public endpoint
  will also rate-limit a list view that resolves dozens of addresses.

Both point the same way for production: proxy it, and use the hook below.

## Usage in Components

### Example 1: Display User's .skr Domain

```typescript
// app/index.tsx - Main screen showing personalized welcome
import { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import { useMobileWallet } from '@wallet-ui/react-native-kit';
import { useDomainLookup } from '../hooks/use-domain-lookup';
import { ellipsify } from '../utils/ellipsify';

export default function HomeScreen() {
  const { account } = useMobileWallet();
  const { resolveAddress, loading } = useDomainLookup();
  const [displayName, setDisplayName] = useState<string>('');

  useEffect(() => {
    if (!account) return;

    // On the kit stack `address` is already a string. On the web3.js stack it is a
    // PublicKey, so call .toString() there.
    const address = account.address.toString();

    resolveAddress(address).then((result) => {
      setDisplayName(result.domain ?? ellipsify(address));
    });
  }, [account]);

  return (
    <View>
      {loading ? (
        <Text>Loading...</Text>
      ) : (
        <Text>Welcome, {displayName || 'Guest'}!</Text>
      )}
    </View>
  );
}
```

### Example 2: Domain Search Component

```typescript
// components/domain-search.tsx - Search for domains or addresses
import { useState } from 'react';
import { View, TextInput, Button, Text } from 'react-native';
import { useDomainLookup } from '../hooks/use-domain-lookup';

export function DomainSearch() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<string>('');
  const { resolveDomain, resolveAddress, loading } = useDomainLookup();

  const handleSearch = async () => {
    if (!query.trim()) return;

    // Check if input looks like a domain (.skr) or address
    if (query.includes('.skr')) {
      // Domain to address lookup
      const res = await resolveDomain(query);
      if (res.address) {
        setResult(`Address: ${res.address}`);
      } else {
        setResult(`Error: ${res.error}`);
      }
    } else {
      // Address to domain lookup
      const res = await resolveAddress(query);
      if (res.domain) {
        setResult(`Domain: ${res.domain}`);
      } else {
        setResult(`Error: ${res.error}`);
      }
    }
  };

  return (
    <View>
      <TextInput
        placeholder="Enter .skr domain or wallet address"
        value={query}
        onChangeText={setQuery}
      />
      <Button title="Search" onPress={handleSearch} disabled={loading} />
      {result && <Text>{result}</Text>}
    </View>
  );
}
```

### Example 3: Display .skr Instead of Address in Lists

```typescript
// components/wallet-list-item.tsx - Show .skr domain in user lists
import { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import { useDomainLookup } from '../hooks/use-domain-lookup';
import { ellipsify } from '../utils/ellipsify';

interface WalletListItemProps {
  address: string;
}

export function WalletListItem({ address }: WalletListItemProps) {
  const { resolveAddress } = useDomainLookup();
  const [displayName, setDisplayName] = useState(ellipsify(address));

  useEffect(() => {
    // Try to fetch .skr domain
    resolveAddress(address).then((result) => {
      if (result.domain) {
        setDisplayName(result.domain);
      }
    });
  }, [address]);

  return (
    <View>
      <Text>{displayName}</Text>
    </View>
  );
}
```

## Utility: Address Truncation

```typescript
// utils/ellipsify.ts
export function ellipsify(str: string, len = 4): string {
  if (str.length <= len * 2) return str;
  return `${str.slice(0, len)}...${str.slice(-len)}`;
}
```

## Key Implementation Notes

1. **API URL**: `http://10.0.2.2:3000` reaches the host machine from an Android emulator. Physical devices need the host's LAN IP. Read it from `EXPO_PUBLIC_API_URL` instead of committing either value.

2. **Caching**: Cache resolved domains. `@tanstack/react-query` with a long `staleTime` is enough — names change rarely, and a list view otherwise re-resolves the same addresses on every render pass.

3. **Error Handling**: Always fall back to a truncated address. A failed lookup should degrade to something readable, never to a blank or a permanent spinner.

4. **Loading States**: Show a loading indicator, but render the truncated address underneath rather than an empty string, so the UI never shows a nameless user.

5. **Validation**: The backend validates input; validating on the client too avoids a round trip for obviously malformed input.

6. **Wallet hook**: The hook is `useMobileWallet()`, from `@wallet-ui/react-native-kit` or `@wallet-ui/react-native-web3js` depending on the stack. There is no `useMobileWalletAdapter` export. On the kit stack `account.address` is a string; on web3.js it is a `PublicKey` needing `.toString()`. See the `solana-mobile-wallet` skill.
