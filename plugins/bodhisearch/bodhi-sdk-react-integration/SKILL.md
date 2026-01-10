---
name: bodhi-sdk-react-integration
description: >
  Integrate React+Vite web apps with bodhi-js-sdk for local LLM integration. Use when user asks to:
  "integrate bodhi", "add bodhi sdk", "connect to bodhi", "setup bodhi provider",
  "bodhi react integration", "deploy bodhi to github pages", or troubleshoot bodhi-js-sdk connection/auth issues.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(npm:*), Bash(npx:*)
---

# Bodhi JS SDK React Integration

Guide for integrating React+Vite applications with bodhi-js-sdk to enable local LLM chat capabilities through the Bodhi Browser ecosystem.

## When to Use This Skill

- User wants to integrate a React app with bodhi-js-sdk
- User needs to add chat/LLM capabilities to their React+Vite app
- User is deploying a bodhi-integrated app to GitHub Pages
- User is troubleshooting SDK connection, authentication, or streaming issues

## Quick Integration Checklist

1. **Install**: `npm install @bodhiapp/bodhi-js-react`
2. **Register**: Create OAuth client at https://developer.getbodhi.app
3. **Wrap App**: Add `<BodhiProvider authClientId={...}>` around your app
4. **Use Hook**: Access `useBodhi()` for client, auth state, and actions
5. **Build UI**: Create chat interface with streaming support

## Core Concepts

### Package Architecture

- `@bodhiapp/bodhi-js-react` - Preset package for web apps (auto-creates WebUIClient)
- `@bodhiapp/bodhi-js-react-ext` - Preset package for Chrome extensions (auto-creates ExtUIClient)
- Both include React bindings + OpenAI-compatible API

### Connection Modes

- **Extension mode**: Via Bodhi Browser extension (preferred)
- **Direct mode**: Direct HTTP to local server (fallback)
- SDK auto-detects and switches modes automatically

### Authentication

- OAuth 2.0 + PKCE flow
- Two auth servers:
  - **Dev**: `https://main-id.getbodhi.app/realms/bodhi` (allows localhost)
  - **Prod**: `https://id.getbodhi.app/realms/bodhi` (requires real domain)

## Basic Integration Steps

### Step 1: Install Package

```bash
npm install @bodhiapp/bodhi-js-react
```

### Step 2: Wrap App with BodhiProvider

```tsx
// App.tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import Chat from './Chat';

const CLIENT_ID = 'your-client-id-from-developer.getbodhi.app';

function App() {
  return (
    <BodhiProvider authClientId={CLIENT_ID}>
      <div className="app">
        <h1>My Bodhi Chat App</h1>
        <Chat />
      </div>
    </BodhiProvider>
  );
}

export default App;
```

### Step 3: Create Chat Component

```tsx
// Chat.tsx
import { useState, useEffect } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function Chat() {
  const { client, isOverallReady, isAuthenticated, login, showSetup } = useBodhi();
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('');

  // Load models on mount
  useEffect(() => {
    if (isOverallReady && isAuthenticated) {
      loadModels();
    }
  }, [isOverallReady, isAuthenticated]);

  const loadModels = async () => {
    const modelList: string[] = [];
    for await (const model of client.models.list()) {
      modelList.push(model.id);
    }
    setModels(modelList);
    if (modelList.length > 0) setSelectedModel(modelList[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !selectedModel) return;

    setLoading(true);
    setResponse('');

    try {
      const stream = client.chat.completions.create({
        model: selectedModel,
        messages: [{ role: 'user', content: prompt }],
        stream: true,
      });

      for await (const chunk of stream) {
        const content = chunk.choices?.[0]?.delta?.content || '';
        setResponse(prev => prev + content);
      }
    } catch (err) {
      setResponse(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOverallReady) {
    return <button onClick={showSetup}>Open Setup</button>;
  }

  if (!isAuthenticated) {
    return <button onClick={login}>Login</button>;
  }

  return (
    <div>
      <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
        {models.map(model => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
      <form onSubmit={handleSubmit}>
        <input value={prompt} onChange={e => setPrompt(e.target.value)} />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Send'}
        </button>
      </form>
      {response && <div>{response}</div>}
    </div>
  );
}

export default Chat;
```

## Key APIs and Hooks

### useBodhi() Hook

```tsx
const {
  client, // SDK client instance (OpenAI-compatible API)
  isOverallReady, // Both client AND server ready (most common check)
  isAuthenticated, // User has valid OAuth token
  login, // Initiate OAuth login flow
  logout, // Logout and clear tokens
  showSetup, // Open setup wizard modal

  // Additional properties
  isReady, // Client initialized (extension or direct URL)
  isServerReady, // Server status is 'ready'
  isInitializing, // client.init() in progress
  isExtension, // Using extension mode
  isDirect, // Using direct HTTP mode
  canLogin, // isReady && !isAuthLoading
  isAuthLoading, // Auth operation in progress
} = useBodhi();
```

### Client Methods (OpenAI-Compatible)

```tsx
// List models (AsyncGenerator)
for await (const model of client.models.list()) {
  console.log(model.id);
}

// Streaming chat
const stream = client.chat.completions.create({
  model: 'gemma-3n-e4b-it',
  messages: [{ role: 'user', content: 'Hello!' }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices?.[0]?.delta?.content || '';
  // Append to response
}

// Non-streaming chat
const response = await client.chat.completions.create({
  model: 'gemma-3n-e4b-it',
  messages: [{ role: 'user', content: 'Hello!' }],
  stream: false,
});
```

## Advanced Configuration

### Custom Client Config

```tsx
<BodhiProvider
  authClientId={CLIENT_ID}
  clientConfig={{
    redirectUri: 'https://myapp.com/callback',
    basePath: '/app',
    logLevel: 'debug',
  }}
>
  <App />
</BodhiProvider>
```

### basePath for Sub-paths or GitHub Pages

When your app runs on a sub-path (e.g., GitHub Pages at `/repo-name/`):

```tsx
// Vite config
export default defineConfig({
  base: '/repo-name/',
});

// BodhiProvider
<BodhiProvider authClientId={CLIENT_ID} basePath="/repo-name" callbackPath="/repo-name/callback">
  <App />
</BodhiProvider>;
```

## Common Patterns

### Conditional Rendering

```tsx
function App() {
  const { isOverallReady, isAuthenticated, showSetup, login } = useBodhi();

  if (!isOverallReady) {
    return <button onClick={showSetup}>Setup Required</button>;
  }

  if (!isAuthenticated) {
    return <button onClick={login}>Login Required</button>;
  }

  return <ChatInterface />;
}
```

### Model Loading with Caching

```tsx
const loadModels = async () => {
  const cached = localStorage.getItem('bodhi_models');
  if (cached) {
    const { models: cachedModels, expiry } = JSON.parse(cached);
    if (Date.now() < expiry) {
      setModels(cachedModels);
      return;
    }
  }

  const modelList: string[] = [];
  for await (const model of client.models.list()) {
    modelList.push(model.id);
  }
  setModels(modelList);

  localStorage.setItem(
    'bodhi_models',
    JSON.stringify({
      models: modelList,
      expiry: Date.now() + 3600000, // 1 hour
    })
  );
};
```

### Error Handling

```tsx
try {
  const stream = client.chat.completions.create({ ... });
  for await (const chunk of stream) {
    // Process chunk
  }
} catch (err) {
  if (err instanceof Error) {
    console.error('Chat error:', err.message);
    setError(err.message);
  }
}
```

## Detailed Guides

For comprehensive information on specific topics, see the supporting documentation:

- **[Quick Start Guide](./quick-start.md)** - Complete 5-minute integration walkthrough
- **[OAuth Setup](./oauth-setup.md)** - Dev vs prod environments, client registration
- **[GitHub Pages Deployment](./github-pages.md)** - basePath config, 404 hack, workflows
- **[Troubleshooting](./troubleshooting.md)** - Common issues and solutions
- **[Code Examples](./code-examples.md)** - Copy-paste snippets for common patterns

## SDK Documentation Reference

The bodhi-js-sdk repository contains comprehensive documentation:

- `bodhi-js-sdk/docs/quick-start.md` - Official quick start
- `bodhi-js-sdk/docs/react-integration.md` - Deep dive into React integration
- `bodhi-js-sdk/docs/authentication.md` - OAuth flow details
- `bodhi-js-sdk/docs/streaming.md` - Streaming patterns
- `bodhi-js-sdk/docs/api-reference.md` - Complete API documentation

## Implementation Approach

When user asks to integrate bodhi-js-sdk:

1. **Check existing setup**: Look for package.json, existing React components
2. **Install package**: Run `npm install @bodhiapp/bodhi-js-react`
3. **Add BodhiProvider**: Wrap root component with provider
4. **Create/update components**: Add useBodhi() hook to components
5. **Test connection**: Verify extension detection or direct mode
6. **Add OAuth**: Guide user to register at developer.getbodhi.app
7. **Implement chat**: Create streaming chat interface
8. **Handle errors**: Add proper error boundaries and user feedback

When troubleshooting:

1. **Check connection status**: Use `isOverallReady`, `isReady`, `isServerReady`
2. **Verify auth state**: Check `isAuthenticated`, `auth` object
3. **Inspect logs**: Look for `[Bodhi/Web]` prefixed logs in console
4. **Review config**: Verify authClientId, redirectUri, basePath
5. **Test backend**: Ensure local server at http://localhost:1135
6. **Check extension**: Verify Bodhi Browser extension installed

## Testing Integration

After integration, verify:

1. **Extension detection**: Check console for `[Bodhi/Web] Extension detected`
2. **Server connection**: Verify `[Bodhi/Web] Server ready`
3. **Setup flow**: Click "Open Setup" to test modal
4. **Authentication**: Click "Login" to test OAuth flow
5. **Model loading**: Verify models populate in dropdown
6. **Streaming**: Send message and verify real-time response streaming
7. **Error handling**: Test with server offline to verify error states

## Common Integration Tasks

When user requests:

- **"Add bodhi to my React app"** → Follow basic integration steps
- **"Setup OAuth for bodhi"** → Guide to oauth-setup.md, developer.getbodhi.app
- **"Deploy to GitHub Pages"** → Reference github-pages.md for basePath and 404 hack
- **"Chat not working"** → Check troubleshooting.md for connection/auth issues
- **"Models not loading"** → Verify server, check models endpoint, review async iteration
- **"Streaming broken"** → Verify stream:true, check AsyncGenerator pattern

## Key Files to Reference

When implementing integration:

- `bodhi-js-sdk/docs/quick-start.md` - Primary integration guide
- `bodhi-js-sdk/docs/react-integration.md` - React-specific patterns
- `bodhi-js-sdk/docs/` - Comprehensive documentation and examples

## Notes

- Focus on React+Vite projects only
- Always use `@bodhiapp/bodhi-js-react` preset package (simplest)
- Auto-callback handling is enabled by default (`handleCallback={true}`)
- OAuth callback happens automatically without custom routes
- Default backend: http://localhost:1135
- Extension mode is preferred over direct mode
- AsyncGenerator pattern for streaming (OpenAI-compatible)
