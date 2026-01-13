# OAuth Setup: Dev vs Production

Guide for configuring OAuth authentication with bodhi-js-sdk for development and production environments.

## Overview

Bodhi uses OAuth 2.0 + PKCE for authentication. Two auth servers are available:

| Environment     | Auth Server                                 | Allowed Redirect URIs                        |
| --------------- | ------------------------------------------- | -------------------------------------------- |
| **Development** | `https://main-id.getbodhi.app/realms/bodhi` | `localhost`, `127.0.0.1`, loopback addresses |
| **Production**  | `https://id.getbodhi.app/realms/bodhi`      | Real domains only (no localhost)             |

## Development Setup

### 1. Register Application

Visit https://developer.getbodhi.app and create a new application:

- **Application Name**: "My App (Dev)"
- **Environment**: Development
- **Redirect URI**: `http://localhost:5173/callback` (or your dev server URL)
- **Auth Server**: `https://main-id.getbodhi.app/realms/bodhi`

Copy the generated `client_id` (UUID format).

### 2. Configure BodhiProvider

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';

const DEV_CLIENT_ID = 'app-abc123-uuid-from-dev-portal';

function App() {
  return (
    <BodhiProvider
      authClientId={DEV_CLIENT_ID}
      clientConfig={{
        authServerUrl: 'https://main-id.getbodhi.app/realms/bodhi',
        redirectUri: 'http://localhost:5173/callback',
      }}
    >
      <YourApp />
    </BodhiProvider>
  );
}
```

**Note**: If `authServerUrl` is omitted, it defaults to production auth server.

### 3. Test OAuth Flow

1. Run `npm run dev`
2. Open http://localhost:5173
3. Click "Login" button
4. Redirects to `https://main-id.getbodhi.app` → Enter credentials
5. Redirects back to `http://localhost:5173/callback`
6. BodhiProvider handles callback automatically
7. User is authenticated

## Production Setup

### 1. Register Production Application

Visit https://developer.getbodhi.app and create production application:

- **Application Name**: "My App"
- **Environment**: Production
- **Redirect URI**: `https://myapp.com/callback` (real domain required)
- **Auth Server**: `https://id.getbodhi.app/realms/bodhi`

Copy the production `client_id`.

### 2. Configure BodhiProvider

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';

const PROD_CLIENT_ID = 'app-xyz789-uuid-from-prod-portal';

function App() {
  return (
    <BodhiProvider
      authClientId={PROD_CLIENT_ID}
      clientConfig={{
        // Production auth server (can be omitted - it's the default)
        authServerUrl: 'https://id.getbodhi.app/realms/bodhi',
        redirectUri: 'https://myapp.com/callback',
      }}
    >
      <YourApp />
    </BodhiProvider>
  );
}
```

**Note**: Production auth server is the default, so `authServerUrl` can be omitted.

### 3. Environment-Based Config

Use environment variables to switch between dev and prod:

```tsx
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_BODHI_CLIENT_ID: string;
  readonly VITE_BODHI_AUTH_SERVER?: string;
  readonly VITE_BODHI_REDIRECT_URI?: string;
}

// App.tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';

const CLIENT_ID = import.meta.env.VITE_BODHI_CLIENT_ID;
const AUTH_SERVER = import.meta.env.VITE_BODHI_AUTH_SERVER;
const REDIRECT_URI = import.meta.env.VITE_BODHI_REDIRECT_URI;

function App() {
  return (
    <BodhiProvider
      authClientId={CLIENT_ID}
      clientConfig={{
        authServerUrl: AUTH_SERVER,
        redirectUri: REDIRECT_URI || `${window.location.origin}/callback`,
      }}
    >
      <YourApp />
    </BodhiProvider>
  );
}
```

**.env.development**:

```
VITE_BODHI_CLIENT_ID=app-dev-client-id
VITE_BODHI_AUTH_SERVER=https://main-id.getbodhi.app/realms/bodhi
VITE_BODHI_REDIRECT_URI=http://localhost:5173/callback
```

**.env.production**:

```
VITE_BODHI_CLIENT_ID=app-prod-client-id
VITE_BODHI_AUTH_SERVER=https://id.getbodhi.app/realms/bodhi
VITE_BODHI_REDIRECT_URI=https://myapp.com/callback
```

## OAuth Callback Handling

### Automatic (Recommended)

By default, BodhiProvider handles callbacks automatically:

```tsx
<BodhiProvider
  authClientId={CLIENT_ID}
  handleCallback={true} // Default - can omit
  callbackPath="/callback" // Default - can omit
>
  <App />
</BodhiProvider>
```

When OAuth redirects to `/callback?code=...&state=...`:

1. Provider detects callback parameters
2. Exchanges code for tokens automatically
3. Stores tokens in localStorage
4. Redirects to basePath (`/` by default)
5. User is authenticated

No custom callback route needed!

### Manual (Advanced)

If you need custom callback logic:

```tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function CallbackPage() {
  const navigate = useNavigate();
  const { client } = useBodhi();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');

    if (code && state) {
      client
        .handleOAuthCallback(code, state)
        .then(() => {
          console.log('Auth successful');
          navigate('/dashboard');
        })
        .catch(err => {
          console.error('Auth failed:', err);
          navigate('/login?error=' + err.message);
        });
    }
  }, [client, navigate]);

  return <div>Authenticating...</div>;
}
```

Disable automatic handling:

```tsx
<BodhiProvider client={client} handleCallback={false}>
  <App />
</BodhiProvider>
```

## Redirect URI Patterns

### Single-Page Apps (No Router)

```
redirectUri: `${window.location.origin}/callback`
```

### React Router

```tsx
// App.tsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/callback" element={<div>Authenticating...</div>} />
</Routes>
```

With automatic callback handling, the callback route just needs to exist - no logic required.

### GitHub Pages (Sub-path)

```tsx
// basePath: '/my-repo'
<BodhiProvider
  authClientId={CLIENT_ID}
  basePath="/my-repo"
  callbackPath="/my-repo/callback"
  clientConfig={{
    redirectUri: 'https://username.github.io/my-repo/callback',
  }}
>
```

See [github-pages.md](./github-pages.md) for details.

## Common OAuth Configurations

### Minimal (Dev)

```tsx
<BodhiProvider authClientId="dev-client-id">
  <App />
</BodhiProvider>
```

Defaults:

- Auth server: Production (`https://id.getbodhi.app`)
- Redirect URI: `${window.location.origin}/callback`
- Callback handling: Automatic

### Explicit Dev

```tsx
<BodhiProvider
  authClientId="dev-client-id"
  clientConfig={{
    authServerUrl: 'https://main-id.getbodhi.app/realms/bodhi',
    redirectUri: 'http://localhost:5173/callback',
  }}
>
  <App />
</BodhiProvider>
```

### Production with basePath

```tsx
<BodhiProvider
  authClientId="prod-client-id"
  basePath="/app"
  clientConfig={{
    redirectUri: 'https://myapp.com/app/callback',
  }}
>
  <App />
</BodhiProvider>
```

### Debug Mode

```tsx
<BodhiProvider authClientId={CLIENT_ID} logLevel="debug">
  <App />
</BodhiProvider>
```

Logs all OAuth flow steps to console.

## Troubleshooting OAuth

### "Invalid redirect_uri"

**Cause**: Redirect URI doesn't match registered URI exactly.
**Solution**:

- Check developer portal - ensure URI matches exactly (including protocol, port, path)
- Common mismatch: `http://localhost:5173` vs `http://localhost:5173/`

### "Client not found"

**Cause**: Wrong client_id or client not registered.
**Solution**:

- Verify client_id copied correctly from developer portal
- Ensure using correct environment (dev vs prod)

### "redirect_uri not allowed for this client"

**Cause**: Using localhost URI with production client, or vice versa.
**Solution**:

- Dev client → Use `https://main-id.getbodhi.app` auth server
- Prod client → Use real domain, not localhost

### OAuth redirects but not authenticated

**Cause**: Callback not handling code exchange.
**Solution**:

- Verify `handleCallback={true}` (default)
- Check console for errors during callback
- Verify `callbackPath` matches redirect URI path

### Tokens not persisting

**Cause**: localStorage not accessible or cleared.
**Solution**:

- Check browser console for localStorage errors
- Verify not in incognito/private mode
- Check for localStorage quota issues

## Security Best Practices

1. **Never commit credentials**: Use environment variables
2. **Separate dev/prod clients**: Different client_ids for dev and prod
3. **HTTPS in production**: Always use HTTPS for production redirect URIs
4. **Validate state parameter**: SDK handles this automatically
5. **Token refresh**: SDK auto-refreshes tokens before expiry

## Additional Resources

- `bodhi-js-sdk/docs/authentication.md` - Deep dive into OAuth flow
- `bodhi-js-sdk/docs/advanced/token-management.md` - Manual token handling
- Developer Portal: https://developer.getbodhi.app
