# GitHub Pages Deployment

Key concepts for deploying bodhi-js-sdk integrated React apps to GitHub Pages.

## Overview

GitHub Pages serves static files from a repository. Two main challenges when deploying React+Bodhi apps:

1. **basePath**: GitHub Pages serves from `/repo-name/` subdirectory
2. **SPA Routing**: GitHub returns 404 for frontend routes (like `/callback`)

## basePath Configuration

### Vite Config

Set the base path in `vite.config.ts`:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/repo-name/', // Replace with your repository name
});
```

This ensures all asset paths (JS, CSS, images) are correctly prefixed.

### BodhiProvider Config

Configure BodhiProvider to match the base path:

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';

const CLIENT_ID = import.meta.env.VITE_BODHI_CLIENT_ID;

function App() {
  return (
    <BodhiProvider
      authClientId={CLIENT_ID}
      basePath="/repo-name"
      callbackPath="/repo-name/callback"
      clientConfig={{
        redirectUri: 'https://username.github.io/repo-name/callback',
      }}
    >
      <YourApp />
    </BodhiProvider>
  );
}
```

**Why basePath matters**:

- OAuth callback path: `/repo-name/callback`
- localStorage keys: Scoped to base path
- Setup modal URLs: Correctly resolved

## SPA 404 Redirect Hack

GitHub Pages doesn't support SPA routing natively. When a user visits `/repo-name/callback` directly (OAuth redirect), GitHub returns 404.

### The Solution (rafgraph/spa-github-pages)

Use a 404.html redirect hack:

1. **404.html** - Captures unknown routes, encodes path as query string
2. **index.html** - Decodes query string back to path
3. **React Router** - Handles the route normally

### Implementation

**public/404.html**:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Redirecting...</title>
    <script>
      // GitHub Pages 404 redirect hack
      // Store the path in sessionStorage and redirect to index.html
      sessionStorage.setItem('redirectPath', window.location.pathname);
      window.location.replace('/repo-name/');
    </script>
  </head>
  <body></body>
</html>
```

**index.html** (add to `<head>` before other scripts):

```html
<script>
  // Restore path from 404 redirect
  (function () {
    var redirectPath = sessionStorage.getItem('redirectPath');
    if (redirectPath) {
      sessionStorage.removeItem('redirectPath');
      history.replaceState(null, null, redirectPath);
    }
  })();
</script>
```

**Alternative (rafgraph approach)**: See https://github.com/rafgraph/spa-github-pages for a more sophisticated implementation that encodes paths in query strings.

## Environment Variables

Use GitHub Secrets for OAuth client ID:

**.github/workflows/deploy.yml**:

```yaml
- name: Build
  env:
    VITE_BODHI_CLIENT_ID: ${{ secrets.VITE_BODHI_CLIENT_ID }}
  run: npm run build
```

**Repository Settings → Secrets → Actions**:

- Add secret: `VITE_BODHI_CLIENT_ID` = your production client ID

## OAuth Registration

Register production client at https://developer.getbodhi.app:

- **Environment**: Production
- **Redirect URI**: `https://username.github.io/repo-name/callback`
- **Auth Server**: `https://id.getbodhi.app/realms/bodhi` (or omit - it's default)

## Workflow Considerations

Key steps for GitHub Pages deployment:

1. **Install dependencies**: `npm ci`
2. **Build with basePath**: `npm run build` (uses vite.config.ts base)
3. **Set environment vars**: Pass `VITE_BODHI_CLIENT_ID` from secrets
4. **Upload artifact**: Upload `dist/` directory
5. **Deploy to Pages**: Use `actions/deploy-pages` action

See GitHub Actions documentation for full workflow examples:

- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://vitejs.dev/guide/static-deploy.html#github-pages

## Enable GitHub Pages

**Repository Settings → Pages**:

- **Source**: GitHub Actions (not "Deploy from branch")
- Workflow will deploy automatically on push to main

## Testing Deployment

After deployment:

1. Visit `https://username.github.io/repo-name/`
2. Click "Open Setup" → Verify modal loads
3. Click "Login" → Should redirect to auth server
4. OAuth redirects to `/repo-name/callback` → Should work (not 404)
5. After auth → Should load chat interface

## Common Issues

### Assets 404 (CSS/JS not loading)

**Cause**: Incorrect base path.
**Solution**: Verify `base: '/repo-name/'` in vite.config.ts matches repository name.

### OAuth callback 404

**Cause**: Missing 404.html redirect or incorrect redirect URI.
**Solution**:

- Add 404.html to public/
- Verify redirect URI in developer portal matches `https://username.github.io/repo-name/callback`

### "Client not ready" after OAuth

**Cause**: localStorage keys using wrong base path.
**Solution**: Verify `basePath="/repo-name"` in BodhiProvider matches vite config.

### Environment variable not working

**Cause**: Secret not set or workflow not passing it.
**Solution**:

- Add secret in Repository Settings → Secrets
- Pass secret in workflow: `env: VITE_BODHI_CLIENT_ID: ${{ secrets.VITE_BODHI_CLIENT_ID }}`

## Complete Example Config

**vite.config.ts**:

```ts
export default defineConfig({
  plugins: [react()],
  base: '/my-chat-app/',
});
```

**App.tsx**:

```tsx
<BodhiProvider
  authClientId={import.meta.env.VITE_BODHI_CLIENT_ID}
  basePath="/my-chat-app"
  callbackPath="/my-chat-app/callback"
  clientConfig={{
    redirectUri: 'https://username.github.io/my-chat-app/callback',
  }}
>
  <YourApp />
</BodhiProvider>
```

**public/404.html**: Simple redirect to index with path in sessionStorage

**Environment**: `VITE_BODHI_CLIENT_ID` secret in GitHub repository

## Additional Resources

- **rafgraph/spa-github-pages**: https://github.com/rafgraph/spa-github-pages (comprehensive 404 hack)
- **Vite Static Deploy**: https://vitejs.dev/guide/static-deploy.html#github-pages
- **GitHub Pages Actions**: https://github.com/actions/deploy-pages

## Summary

Key concepts for GitHub Pages deployment:

1. **basePath**: Set in both vite.config.ts and BodhiProvider
2. **404 redirect**: Use 404.html to capture SPA routes
3. **OAuth**: Register with full GitHub Pages URL
4. **Environment**: Use GitHub Secrets for client ID
5. **Workflow**: Build → Upload → Deploy with GitHub Actions

These concepts enable successful deployment - adapt to your specific needs.
