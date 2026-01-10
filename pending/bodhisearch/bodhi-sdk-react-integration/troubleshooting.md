# Troubleshooting Guide

Common issues and solutions when integrating bodhi-js-sdk with React applications.

## Connection Issues

### "Extension not detected"

**Symptoms**: Console shows no extension, `isExtension = false`, direct mode fallback.

**Causes**:

- Bodhi Browser extension not installed
- Extension disabled
- Extension crashed or not running

**Solutions**:

1. Install extension from Chrome Web Store
2. Reload app page (Cmd+R / Ctrl+R)
3. Check extension enabled: `chrome://extensions`
4. Check extension background script: Extensions → Bodhi Browser → "Inspect views: service worker"
5. Look for errors in extension console

**Verification**:

```tsx
const { isExtension, clientState } = useBodhi();
console.log('Extension mode:', isExtension);
console.log('Client state:', clientState);
```

Console should show:

```
[Bodhi/Web] Extension detected, version: 1.0.0
Extension mode: true
```

---

### "Server not reachable"

**Symptoms**: `isServerReady = false`, `clientState.server.status !== 'ready'`.

**Causes**:

- Bodhi App backend not running
- Wrong server URL
- Network/firewall blocking localhost

**Solutions**:

1. Start Bodhi App backend (download from https://getbodhi.app)
2. Verify server running: Open http://localhost:1135 in browser
3. Check server status: `curl http://localhost:1135/ping`
4. Extension settings: Verify backend URL is `http://localhost:1135`
5. Direct mode: Configure URL via Setup modal

**Verification**:

```tsx
const { isServerReady, clientState } = useBodhi();
console.log('Server ready:', isServerReady);
console.log('Server state:', clientState.server);
```

Console should show:

```
[Bodhi/Web] Server ready, version: 0.1.0
Server ready: true
```

---

### Setup modal not opening

**Symptoms**: `showSetup()` does nothing, no modal appears.

**Causes**:

- Modal HTML not loading
- iframe blocked by CSP
- JavaScript error preventing modal

**Solutions**:

1. Check console for errors
2. Verify modal HTML path (default: auto-detected from package)
3. Check CSP headers allow iframe
4. Test with custom modal path:
   ```tsx
   <BodhiProvider
     authClientId={CLIENT_ID}
     modalHtmlPath="/path/to/modal.html"
   >
   ```

**Verification**:

```tsx
const { setupState, showSetup } = useBodhi();
console.log('Setup state:', setupState);
await showSetup();
// setupState should change: 'ready' → 'loading' → 'loaded'
```

---

## Authentication Issues

### "OAuth redirect failed"

**Symptoms**: Login redirects but not authenticated, error in URL params.

**Causes**:

- Redirect URI mismatch
- Invalid client ID
- Wrong auth server
- State parameter mismatch

**Solutions**:

1. Verify redirect URI matches registration exactly:
   - Developer portal: `http://localhost:5173/callback`
   - BodhiProvider: Same URL in `clientConfig.redirectUri`
2. Check client ID copied correctly from developer portal
3. Verify auth server:
   - Dev: `https://main-id.getbodhi.app/realms/bodhi`
   - Prod: `https://id.getbodhi.app/realms/bodhi` (default)
4. Clear localStorage and retry

**Verification**:

```tsx
const { isAuthenticated, auth } = useBodhi();
console.log('Authenticated:', isAuthenticated);
console.log('Auth state:', auth);
```

After successful login:

```
Authenticated: true
Auth state: { status: 'authenticated', user: {...}, accessToken: '...' }
```

---

### Login button disabled

**Symptoms**: Can't click login, `canLogin = false`.

**Causes**:

- Client not ready (`isReady = false`)
- Auth operation in progress (`isAuthLoading = true`)

**Solutions**:

1. Wait for client initialization
2. Ensure extension detected or direct URL configured
3. Check server connection

**Verification**:

```tsx
const { canLogin, isReady, isAuthLoading } = useBodhi();
console.log('Can login:', canLogin);
console.log('Is ready:', isReady);
console.log('Auth loading:', isAuthLoading);
```

Login enabled when: `isReady === true && isAuthLoading === false`

---

### Tokens not persisting after page reload

**Symptoms**: Login works but user logged out after refresh.

**Causes**:

- localStorage blocked (incognito mode)
- localStorage quota exceeded
- Wrong base path (tokens stored under different key)

**Solutions**:

1. Exit incognito/private mode
2. Clear some localStorage data
3. Verify `basePath` matches actual app path
4. Check browser console for localStorage errors

**Verification**:

```javascript
// In browser console
localStorage.getItem('bodhi_auth_state');
// Should return JSON with tokens
```

---

## API and Streaming Issues

### Models not loading

**Symptoms**: Empty model dropdown, `client.models.list()` returns nothing.

**Causes**:

- Not authenticated
- Server not ready
- No models downloaded in Bodhi App
- API request error

**Solutions**:

1. Verify authenticated: `isAuthenticated === true`
2. Check server ready: `isServerReady === true`
3. Test API directly: `curl http://localhost:1135/v1/models`
4. Download models via Bodhi App UI
5. Check console for API errors

**Verification**:

```tsx
const { client, isAuthenticated, isServerReady } = useBodhi();

useEffect(() => {
  if (!isAuthenticated || !isServerReady) {
    console.log('Not ready for API calls');
    return;
  }

  (async () => {
    try {
      for await (const model of client.models.list()) {
        console.log('Model:', model.id);
      }
    } catch (err) {
      console.error('Models error:', err);
    }
  })();
}, [isAuthenticated, isServerReady]);
```

---

### Streaming not working

**Symptoms**: No chunks received, response empty, or non-streaming response.

**Causes**:

- `stream: false` instead of `stream: true`
- Not using `for await` loop
- Model not supporting streaming
- AsyncGenerator not iterated properly

**Solutions**:

1. Ensure `stream: true`:

   ```tsx
   const stream = client.chat.completions.create({
     model: selectedModel,
     messages: [{ role: 'user', content: prompt }],
     stream: true, // Must be true
   });
   ```

2. Use `for await` loop:

   ```tsx
   for await (const chunk of stream) {
     const content = chunk.choices?.[0]?.delta?.content || '';
     setResponse(prev => prev + content);
   }
   ```

3. Check model supports streaming (most do)

**Verification**:

```tsx
try {
  const stream = client.chat.completions.create({
    model: 'gemma-3n-e4b-it',
    messages: [{ role: 'user', content: 'Test' }],
    stream: true,
  });

  let chunks = 0;
  for await (const chunk of stream) {
    chunks++;
    console.log('Chunk', chunks, ':', chunk.choices?.[0]?.delta?.content);
  }
  console.log('Total chunks:', chunks);
} catch (err) {
  console.error('Streaming error:', err);
}
```

---

### API requests failing

**Symptoms**: API calls throw errors, network errors, CORS errors.

**Causes**:

- Server not running
- Extension not relaying requests
- Direct mode URL wrong
- Authentication expired

**Solutions**:

1. Check server: `curl http://localhost:1135/ping`
2. Verify client ready: `isOverallReady === true`
3. Check console for detailed error messages
4. Try logout/login to refresh tokens
5. Verify extension background script running

**Verification**:

```tsx
const { client, isOverallReady } = useBodhi();

const testApi = async () => {
  if (!isOverallReady) {
    console.error('Client not ready');
    return;
  }

  try {
    const result = await client.sendApiRequest('GET', '/ping');
    console.log('Ping result:', result);
  } catch (err) {
    console.error('API error:', err);
  }
};
```

---

## Build and Deployment Issues

### Assets 404 in production

**Symptoms**: JS/CSS files not loading, blank page in production.

**Causes**:

- Wrong base path in Vite config
- Assets served from wrong URL

**Solutions**:

1. Set correct base in `vite.config.ts`:

   ```ts
   export default defineConfig({
     base: '/repo-name/', // For GitHub Pages
   });
   ```

2. Verify build output paths:
   ```bash
   npm run build
   cat dist/index.html  # Check asset paths
   ```

---

### OAuth callback 404 on GitHub Pages

**Symptoms**: OAuth redirects to `/callback` → 404 error page.

**Causes**:

- GitHub Pages doesn't support SPA routing
- Missing 404.html redirect

**Solutions**:

1. Implement 404.html redirect (see [github-pages.md](./github-pages.md))
2. Verify redirect URI in developer portal includes full path
3. Test locally with `npx vite preview`

---

## Environment-Specific Issues

### Development vs Production Mismatch

**Symptoms**: Works in dev, fails in production (or vice versa).

**Causes**:

- Different OAuth client IDs
- Different auth servers
- Environment variables not set

**Solutions**:

1. Use separate client IDs for dev and prod
2. Environment variables:
   - `.env.development` → Dev client ID, dev auth server
   - `.env.production` → Prod client ID, prod auth server (or default)
3. Verify environment variables loaded correctly:
   ```tsx
   console.log('Client ID:', import.meta.env.VITE_BODHI_CLIENT_ID);
   ```

---

## Debugging Tips

### Enable Debug Logging

```tsx
<BodhiProvider
  authClientId={CLIENT_ID}
  logLevel="debug"
>
```

Logs all SDK operations to console with `[Bodhi/*]` prefix.

### Inspect Client State

```tsx
const { clientState, auth } = useBodhi();

useEffect(() => {
  console.log('Client state:', JSON.stringify(clientState, null, 2));
  console.log('Auth state:', JSON.stringify(auth, null, 2));
}, [clientState, auth]);
```

### Check Extension Background Script

1. Navigate to `chrome://extensions`
2. Find "Bodhi Browser"
3. Click "Inspect views: service worker"
4. Check console for errors
5. Look for `[Bodhi/background]` logs

### Verify localStorage

```javascript
// Browser console
Object.keys(localStorage).filter(k => k.startsWith('bodhi'));
// Should show: bodhi_auth_state, bodhi_client_state, etc.

localStorage.getItem('bodhi_auth_state');
localStorage.getItem('bodhi_client_state');
```

### Network Inspection

1. Open DevTools → Network tab
2. Filter by "localhost:1135" or extension ID
3. Check request/response for API calls
4. Verify streaming responses (chunked transfer)

---

## Common Error Messages

| Error                   | Cause                           | Solution                               |
| ----------------------- | ------------------------------- | -------------------------------------- |
| "Extension not found"   | Extension not installed/enabled | Install extension, reload page         |
| "Server not connected"  | Backend not running             | Start Bodhi App backend                |
| "Invalid client_id"     | Wrong OAuth client ID           | Verify client ID from developer portal |
| "redirect_uri_mismatch" | OAuth redirect URI wrong        | Match redirect URI exactly             |
| "Unauthorized"          | Tokens expired/invalid          | Logout and login again                 |
| "CORS error"            | Direct mode CORS issue          | Use extension mode or configure CORS   |
| "NetworkError"          | Server unreachable              | Check server running, network access   |

---

## Getting Help

If issues persist:

1. **Check SDK docs**: `bodhi-js-sdk/docs/` directory for comprehensive guides and examples
2. **Console logs**: Share logs with `logLevel="debug"`
3. **GitHub Issues**: https://github.com/BodhiSearch/bodhi-js/issues
4. **Developer Portal**: https://developer.getbodhi.app for OAuth issues

---

## Diagnostic Checklist

Before reporting issues, verify:

- [ ] Extension installed and enabled
- [ ] Bodhi App backend running (http://localhost:1135)
- [ ] Client ID registered at developer.getbodhi.app
- [ ] Redirect URI matches exactly
- [ ] Console shows no errors (with `logLevel="debug"`)
- [ ] `isOverallReady === true` before API calls
- [ ] `isAuthenticated === true` for auth-required operations
- [ ] Models downloaded in Bodhi App
- [ ] Browser DevTools Network tab shows successful requests
- [ ] localStorage not blocked (not incognito mode)
