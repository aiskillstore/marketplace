---
name: extension-authorization
description: Authorization system with role-based access control. Must-have for all apps that manage personal or access-restricted data.
version: 1.0.0
compatibility:
  mops:
    caffeineai-authorization: "~1.0.0"
  npm:
    "@caffeineai/core-infrastructure": "^1.0.0"
caffeineai-subscription: [none]
---

# Authorization
Authorization extendsion for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds an authentication and authorization system with role-based access control using the mixin pattern. The `MixinAuthorization` mixin provides standard authorization endpoints automatically.

# Backend

Authentication system with role-based access control.

There is a prefabricated library `mo:caffeineai-authorization/access-control.mo`. It provides core authentication with role-based access control.

## Module API

```mo:caffeineai-authorization/access-control.mo
module {
  public type UserRole = {
    #admin;
    #user;
    #guest;
  };

  public type AccessControlState = { /* internal state */ };

  public func initState() : AccessControlState;
  public func getUserRole(state : AccessControlState, caller : Principal) : UserRole;
  public func assignRole(state : AccessControlState, caller : Principal, user : Principal, role : UserRole);
  public func isAdmin(state : AccessControlState, caller : Principal) : Bool;
  public func hasPermission(state : AccessControlState, caller : Principal, requiredRole : UserRole) : Bool;
};
```

Initialization is handled internally by `MixinAuthorization` -- do not call `initialize` directly. The first authenticated user to log in automatically becomes admin; no token or secret is required.

IMPORTANT: The `include MixinAuthorization(accessControlState)` line MUST be placed in `main.mo`, not in a custom mixin file.

## Opting out / custom authentication

If the user asks to replace this authorization system with custom authentication (for example username/password auth, no Internet Identity, or no `MixinAuthorization`), remove the `caffeineai-authorization` mops package from the project. This is the only supported way to remove the `include-authorization` lint requirement, because that lint rule is shipped by the package. Do not add suppression comments or leave the package installed while omitting `include MixinAuthorization(accessControlState)`.

When removing the package, also remove all `mo:caffeineai-authorization/*` imports, the `accessControlState` initialization, `include MixinAuthorization(accessControlState)`, and any `AccessControl` guard calls that belonged to this component. Replace them with the custom authentication and authorization checks requested by the user.

## Setup in main.mo

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import Types "types";
import ProfileMixin "mixins/Profile";

actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  let userProfiles = Map.empty<Principal, Types.UserProfile>();

  include ProfileMixin(accessControlState, userProfiles);
};
```

## Type Definitions in types.mo

```motoko filepath=src/backend/types.mo
module {
  public type UserProfile = {
    name : Text;
  };
};
```

## Custom Mixin Example (mixins/Profile.mo)

The frontend requires `getCallerUserProfile`, `saveCallerUserProfile`, and `getUserProfile`. Pass `accessControlState` to your mixin so it can check permissions.

```motoko filepath=src/backend/mixins/Profile.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import AccessControl "mo:caffeineai-authorization/access-control";
import Types "../types";

mixin (
  accessControlState : AccessControl.AccessControlState,
  userProfiles : Map.Map<Principal, Types.UserProfile>,
) {
  public query ({ caller }) func getCallerUserProfile() : async ?Types.UserProfile {
    if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
      Runtime.trap("Unauthorized");
    };
    userProfiles.get(caller);
  };

  public shared ({ caller }) func saveCallerUserProfile(profile : Types.UserProfile) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
      Runtime.trap("Unauthorized");
    };
    userProfiles.add(caller, profile);
  };

  public query ({ caller }) func getUserProfile(user : Principal) : async ?Types.UserProfile {
    if (caller != user and not AccessControl.isAdmin(accessControlState, caller)) {
      Runtime.trap("Unauthorized: Can only view your own profile");
    };
    userProfiles.get(user);
  };
};
```

## Guard Patterns

Apply the appropriate guard to every public function:

```
// Admin-only:
if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
  Runtime.trap("Unauthorized: Only admins can perform this action");
};

// Users only:
if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
  Runtime.trap("Unauthorized: Only users can perform this action");
};

// Any user including guests: No check needed
```

## Design Guidelines

- Anonymous principals are treated as guests.
- `assignRole` includes an admin-only guard internally.
- Use `shared({ caller })` for authenticated endpoints that modify data.
- Use `query({ caller })` for authenticated endpoints that fetch data.
- Handle ownership verification where needed.
- Use `Runtime.trap` for authorization failures.

## Email Attributes

`MixinAuthorization` can capture the user's verified Internet Identity attributes (name and email) at sign-in. Pass a callback as the second argument instead of `null`; it runs once per sign-in, after the attribute bundle has been verified.

Do NOT use the `mo:identity-attributes` mixin directly -- always go through `MixinAuthorization`. The callback receives the caller principal and the verified attributes:

```
{
  name : ?Text;   // verified display name, when present
  email : ?Text;  // always the verified address -- sourced from II's `verified_email`, never the unverified `email` key
  sso : ?Text;    // SSO domain when the identity came from SSO, otherwise null
}
```

The field is named `email`, but it only ever holds II's `verified_email` value -- the unverified `email` key is never read. Use `attrs.email` in the callback (there is no `attrs.verified_email` field).

Store them in your own state and expose a getter to read them back:

```
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";

actor {
  let accessControlState = AccessControl.initState();

  let emails = Map.empty<Principal, Text>();

  include MixinAuthorization(
    accessControlState,
    ?(func(caller : Principal, attrs : { name : ?Text; email : ?Text; sso : ?Text }) {
      switch (attrs.email) {
        case (?email) { emails.add(caller, email) };
        case null {};
      };
    }),
  );

  public query ({ caller }) func getCallerEmail() : async ?Text {
    emails.get(caller);
  };
};
```

The `trusted_attribute_signers` and `frontend_origins` canister environment variables required for attribute verification are configured automatically by the Caffeine platform -- you do not set them.

### Fetching the Email on the Frontend

After sign-in, query the getter like any other authenticated actor method:

```typescript
const { data: callerEmail } = useQuery<string | null>({
  queryKey: ['callerEmail'],
  queryFn: () => actor.getCallerEmail(),
  enabled: !!actor && isAuthenticated,
});
```

# Frontend

Authentication system with role-based access control.

## User Profile Setup

When using Internet Identity, the user gets a principal id only after login. Anonymous principals are treated as guests. The principal id is not human-readable -- ask the user for their name the first time they log in with a new principal.

Backend API for profiles:
- `getCallerUserProfile(): Promise<UserProfile | null>` -- returns `null` if no profile exists
- `saveCallerUserProfile(profile: UserProfile): Promise<void>` -- saves name and profile data
- `getUserProfile(user: Principal): Promise<UserProfile | null>` -- fetch another user's profile

Rules:
- On login, if the user already has a profile, do not ask for the name again
- Display the user's profile name instead of the principal id
- Make sure the user must be logged in before seeing any application data
- When logging out, clear all cached application data including the cached user profile

### Preventing Profile Setup Modal Flash

```typescript
export function useGetCallerUserProfile() {
  const { actor, isFetching: actorFetching } = useActor();

  const query = useQuery<UserProfile | null>({
    queryKey: ['currentUserProfile'],
    queryFn: async () => {
      if (!actor) throw new Error('Actor not available');
      return actor.getCallerUserProfile();
    },
    enabled: !!actor && !actorFetching,
    retry: false,
  });

  return {
    ...query,
    isLoading: actorFetching || query.isLoading,
    isFetched: !!actor && query.isFetched,
  };
}
```

Then in your component:
```typescript
const showProfileSetup = isAuthenticated && !profileLoading && isFetched && userProfile === null;
```

## Auth State Lifecycle

The `useInternetIdentity` hook exposes two kinds of state — use the right one:

| Scenario | `loginStatus` | `isAuthenticated` |
|---|---|---|
| Page load, no stored session | `"idle"` | `false` |
| Page load, restoring stored session | `"initializing"` | `false` → `true` |
| Stored session restored after reload | `"idle"` | `true` |
| Interactive login in progress (popup open) | `"logging-in"` | `false` |
| Interactive login just completed | `"success"` | `true` |
| Login popup failed / cancelled | `"loginError"` | `false` |

**IMPORTANT:** `isLoginSuccess` (`loginStatus === "success"`) is only `true` after an interactive login via the popup. It is **NOT** `true` when a stored identity is restored on page reload. Never use `isLoginSuccess` to gate authenticated vs. unauthenticated UI — always use `isAuthenticated`.

Key states for the login button:
- `isInitializing` — `AuthClient` is loading from IndexedDB; disable the button to prevent clicks before the client is ready.
- `isLoggingIn` — the II popup is open; disable the button to prevent duplicate popups.

## Login Component

```typescript
import { useInternetIdentity } from '@caffeineai/core-infrastructure';
import { useQueryClient } from '@tanstack/react-query';

export default function LoginButton() {
  const { login, clear, isAuthenticated, isInitializing, isLoggingIn } = useInternetIdentity();
  const queryClient = useQueryClient();

  const handleAuth = () => {
    if (isAuthenticated) {
      clear();
      queryClient.clear();
    } else {
      login();
    }
  };

  return (
    <button
      onClick={handleAuth}
      disabled={isInitializing || isLoggingIn}
      className={`px-6 py-2 rounded-full transition-colors font-medium ${
        isAuthenticated
          ? 'bg-gray-200 hover:bg-gray-300 text-gray-800'
          : 'bg-blue-600 hover:bg-blue-700 text-white'
      } disabled:opacity-50`}
    >
      {isInitializing ? 'Loading...' : isAuthenticated ? 'Logout' : 'Login'}
    </button>
  );
}
```

The `login()` and `clear()` functions are fire-and-forget (they don't return promises that track the full flow). The hook's `isLoggingIn` / `isInitializing` states track the async lifecycle — do **not** wrap them in local `useState` / `isPending` logic.

Gate authenticated UI on `isAuthenticated` (covers both fresh login and restored sessions on page reload):
```typescript
{isAuthenticated ? (
  <AuthenticatedApp />
) : (
  <LoginScreen />
)}
```

## Comparing Current User with Data Author

```typescript
import { useInternetIdentity } from '@caffeineai/core-infrastructure';
import type { Principal } from '@icp-sdk/core/principal';

const { identity } = useInternetIdentity();

const isAuthor = (authorPrincipal: Principal): boolean => {
  if (!identity) return false;
  return authorPrincipal.toString() === identity.getPrincipal().toString();
};
```

## Access Control UI

For admin-only or personal applications, show an AccessDeniedScreen component when unauthorized users try to access the application.

## Error Handling

Handle authorization errors from backend `Debug.trap` calls gracefully in the UI with appropriate error messages shown to the user.

Note: The initialization of the first admin is done automatically in `@caffeineai/core-infrastructure`. The first authenticated user to log in becomes admin; no token or secret is needed.
