# Quick Start Guide: Bodhi JS SDK React Integration

Complete walkthrough for integrating bodhi-js-sdk with a React+Vite application in 5 minutes.

## Prerequisites

- Node.js 18+
- React project (or create with `npm create vite@latest`)
- Bodhi App backend running (download from https://getbodhi.app)
- Bodhi Browser extension installed (optional - for extension mode)

## Step 1: Install Package

```bash
npm install @bodhiapp/bodhi-js-react
```

That's it! Single package includes everything: React bindings, web client, OAuth handling, streaming.

## Step 2: Register OAuth Client

1. Visit https://developer.getbodhi.app
2. Create new application
3. For development:
   - Use `http://localhost:5173` (or your dev server URL)
   - Auth server: `https://main-id.getbodhi.app/realms/bodhi`
4. Copy the `client_id` (UUID format)

## Step 3: Wrap App with BodhiProvider

Update `src/App.tsx`:

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import Chat from './Chat';

const CLIENT_ID = 'app-abc123-uuid-from-developer-portal';

function App() {
  return (
    <BodhiProvider authClientId={CLIENT_ID}>
      <div className="app">
        <h1>My Bodhi Chat</h1>
        <Chat />
      </div>
    </BodhiProvider>
  );
}

export default App;
```

## Step 4: Create Chat Component

Create `src/Chat.tsx`:

```tsx
import { useState, useEffect } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function Chat() {
  const { client, isOverallReady, isAuthenticated, login, showSetup } = useBodhi();
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('');

  useEffect(() => {
    if (isOverallReady && isAuthenticated) {
      loadModels();
    }
  }, [isOverallReady, isAuthenticated]);

  const loadModels = async () => {
    try {
      const modelList: string[] = [];
      for await (const model of client.models.list()) {
        modelList.push(model.id);
      }
      setModels(modelList);
      if (modelList.length > 0) {
        setSelectedModel(modelList[0]);
      }
    } catch (err) {
      console.error('Failed to load models:', err);
    }
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
    return (
      <div>
        <p>Setup required</p>
        <button onClick={showSetup}>Open Setup</button>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div>
        <p>Please login</p>
        <button onClick={login}>Login</button>
      </div>
    );
  }

  return (
    <div>
      <div>
        <label>
          Model:
          <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)} disabled={loading || models.length === 0}>
            {models.length === 0 ? (
              <option>Loading models...</option>
            ) : (
              models.map(model => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))
            )}
          </select>
        </label>
      </div>

      <form onSubmit={handleSubmit}>
        <input type="text" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Ask me anything..." disabled={loading} />
        <button type="submit" disabled={loading || !selectedModel}>
          {loading ? 'Generating...' : 'Send'}
        </button>
      </form>

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{response}</p>
        </div>
      )}
    </div>
  );
}

export default Chat;
```

## Step 5: Run Your App

```bash
npm run dev
```

Open http://localhost:5173 and:

1. If extension not installed → Click "Open Setup" → Follow wizard
2. If not authenticated → Click "Login" → OAuth flow
3. Select model → Type message → See streaming response

## What Just Happened?

### Single Package Install

`@bodhiapp/bodhi-js-react` includes everything - no need for multiple packages.

### Auto-Configured Provider

```tsx
<BodhiProvider authClientId={CLIENT_ID}>
```

Just pass your client ID - SDK handles:

- Auto-client creation
- Extension detection (or direct mode fallback)
- OAuth configuration
- Callback processing

### Powerful Hook

```tsx
const { client, isOverallReady, isAuthenticated, login, showSetup } = useBodhi();
```

Access client and state from any component.

### OpenAI-Style Streaming

```tsx
for await (const chunk of client.chat.completions.create({ stream: true, ... })) {
  // Real-time chunks
}
```

Familiar AsyncGenerator pattern for streaming.

## Testing Checklist

- [ ] Extension detected (console: `[Bodhi/Web] Extension detected`)
- [ ] Server ready (console: `[Bodhi/Web] Server ready`)
- [ ] Setup modal opens and closes
- [ ] OAuth login redirects and returns
- [ ] Models load in dropdown
- [ ] Streaming chat works in real-time
- [ ] Error states display properly

## Next Steps

- **OAuth Setup**: See [oauth-setup.md](./oauth-setup.md) for dev vs prod config
- **GitHub Pages**: See [github-pages.md](./github-pages.md) for deployment
- **Troubleshooting**: See [troubleshooting.md](./troubleshooting.md) for common issues
- **Code Examples**: See [code-examples.md](./code-examples.md) for more patterns

## Full Documentation

For comprehensive details:

- `bodhi-js-sdk/docs/quick-start.md` - Official quick start
- `bodhi-js-sdk/docs/react-integration.md` - Deep dive
- `bodhi-js-sdk/docs/` - Comprehensive guides and examples
