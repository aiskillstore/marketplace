---
name: extension-core-infrastructure
description: Core infrastructure providing backend connection configuration, storage client, and React app entry point.
version: 1.1.0
compatibility:
  npm:
    "@caffeineai/core-infrastructure": "^1.1.0"
    "@caffeineai/object-storage": "^1.1.0"
caffeineai-subscription: [none]
---

# Core Infrastructure
Core infrastructure extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This component provides the foundational infrastructure for all projects: backend connection configuration, Internet Identity authentication hooks, and actor management utilities.

## Requirements

```
"@caffeineai/core-infrastructure": "^1.1.0"
"@caffeineai/object-storage": "^1.1.0"
"@icp-sdk/auth": "^7.1.0"
"@icp-sdk/core": "^5.3.0"
```

`@caffeineai/object-storage` is a peer dependency of core-infrastructure. Every project must install it as a direct npm dependency (the build template includes both packages).

## Integration

Core infrastructure is automatically included in every project. No manual integration steps are required.

# Frontend

The core-infrastructure frontend package (`@caffeineai/core-infrastructure`) is automatically included in every project.

## App Entry Point

Wrap the app with `InternetIdentityProvider` and `QueryClientProvider`:

```typescript
import { InternetIdentityProvider } from "@caffeineai/core-infrastructure";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ReactDOM from "react-dom/client";
import App from "./App";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <InternetIdentityProvider>
      <App />
    </InternetIdentityProvider>
  </QueryClientProvider>,
);
```

## `useInternetIdentity()` — Authentication Hook

Provides identity state, login, and logout for Internet Identity.

### Return Values

| Field | Type | Description |
|---|---|---|
| `identity` | `Identity \| undefined` | The user's identity (available after login or session restore) |
| `login` | `() => void` | Opens the II popup. Fire-and-forget — do not `await`. |
| `clear` | `() => void` | Logs out and clears stored identity. Fire-and-forget. |
| `isAuthenticated` | `boolean` | `true` when user has a valid identity. **Use this for UI gating.** |
| `isInitializing` | `boolean` | `true` while `AuthClient` is loading from IndexedDB |
| `isLoggingIn` | `boolean` | `true` while the II popup is open |
| `isLoginSuccess` | `boolean` | `true` only after interactive login (NOT after page reload restore) |
| `isLoginError` | `boolean` | `true` if login or initialization failed |
| `loginError` | `Error \| undefined` | The error object when `isLoginError` is `true` |

### Auth State Lifecycle

| Scenario | `loginStatus` | `isAuthenticated` |
|---|---|---|
| Page load, no stored session | `"idle"` | `false` |
| Restoring stored session | `"initializing"` | `false` → `true` |
| Stored session restored after reload | `"idle"` | `true` |
| Interactive login in progress | `"logging-in"` | `false` |
| Interactive login just completed | `"success"` | `true` |
| Login popup failed / cancelled | `"loginError"` | `false` |

**IMPORTANT:** `isLoginSuccess` is only `true` after an interactive login via the popup — NOT when a stored identity is restored on page reload. Always use `isAuthenticated` for conditional rendering.

### Usage

Gate authenticated UI on `isAuthenticated`:
```typescript
const { isAuthenticated } = useInternetIdentity();

{isAuthenticated ? <AuthenticatedApp /> : <LoginScreen />}
```

Disable the login button while initializing or logging in:
```typescript
const { login, isInitializing, isLoggingIn } = useInternetIdentity();

<button onClick={() => login()} disabled={isInitializing || isLoggingIn}>
  Sign in
</button>
```

`login()` and `clear()` are fire-and-forget — the hook's state fields (`isLoggingIn`, `isInitializing`) track the async lifecycle. Do not wrap them in local `useState` / `isPending` logic.

## `useActor()` — Backend Actor Hook

Creates and manages a typed backend actor instance. Automatically re-creates the actor when the user's identity changes (login/logout).

```typescript
import { useActor } from "@caffeineai/core-infrastructure";
import { createActor } from "declarations/backend";

function MyComponent() {
  const { actor, isFetching } = useActor(createActor);

  // actor is null while loading, then the typed backend actor
  if (!actor || isFetching) return <Loading />;

  // Call backend methods directly
  const data = await actor.myBackendMethod();
}
```

### Return Values

| Field | Type | Description |
|---|---|---|
| `actor` | `T \| null` | The typed backend actor, or `null` while loading |
| `isFetching` | `boolean` | `true` while the actor is being created |

When the identity changes (login, logout, or session restore), the actor is automatically re-created with the new identity and all dependent queries are invalidated and refetched.
