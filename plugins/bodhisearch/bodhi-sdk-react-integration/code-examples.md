# Code Examples

Reusable code snippets for common bodhi-js-sdk integration patterns.

## Basic Provider Setup

### Minimal (Development)

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import App from './App';

const DEV_CLIENT_ID = 'app-dev-client-id';

function Root() {
  return (
    <BodhiProvider authClientId={DEV_CLIENT_ID}>
      <App />
    </BodhiProvider>
  );
}

export default Root;
```

### With Environment Variables

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import App from './App';

const CLIENT_ID = import.meta.env.VITE_BODHI_CLIENT_ID;
const AUTH_SERVER = import.meta.env.VITE_BODHI_AUTH_SERVER;

function Root() {
  return (
    <BodhiProvider
      authClientId={CLIENT_ID}
      clientConfig={{
        authServerUrl: AUTH_SERVER,
        logLevel: import.meta.env.DEV ? 'debug' : 'warn',
      }}
    >
      <App />
    </BodhiProvider>
  );
}

export default Root;
```

### GitHub Pages with basePath

```tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import App from './App';

const CLIENT_ID = import.meta.env.VITE_BODHI_CLIENT_ID;
const BASE_PATH = '/my-repo';

function Root() {
  return (
    <BodhiProvider
      authClientId={CLIENT_ID}
      basePath={BASE_PATH}
      callbackPath={`${BASE_PATH}/callback`}
      clientConfig={{
        redirectUri: `https://username.github.io${BASE_PATH}/callback`,
      }}
    >
      <App />
    </BodhiProvider>
  );
}

export default Root;
```

## State Management Hooks

### Connection Status Component

```tsx
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function ConnectionStatus() {
  const { isOverallReady, isReady, isServerReady, isExtension, clientState } = useBodhi();

  if (!isReady) {
    return <div className="status warning">Client not ready: {clientState.status}</div>;
  }

  if (!isServerReady) {
    return <div className="status warning">Server not ready: {clientState.server.status}</div>;
  }

  return <div className="status success">Connected ({isExtension ? 'extension' : 'direct'} mode)</div>;
}

export default ConnectionStatus;
```

### Authentication Guard

```tsx
import { useBodhi } from '@bodhiapp/bodhi-js-react';
import { ReactNode } from 'react';

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

function AuthGuard({ children, fallback }: AuthGuardProps) {
  const { isOverallReady, isAuthenticated, showSetup, login } = useBodhi();

  if (!isOverallReady) {
    return (
      fallback || (
        <div>
          <p>Setup required to connect to Bodhi</p>
          <button onClick={showSetup}>Open Setup</button>
        </div>
      )
    );
  }

  if (!isAuthenticated) {
    return (
      fallback || (
        <div>
          <p>Please login to continue</p>
          <button onClick={login}>Login</button>
        </div>
      )
    );
  }

  return <>{children}</>;
}

export default AuthGuard;
```

### Login/Logout Button

```tsx
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function AuthButton() {
  const { isAuthenticated, canLogin, isAuthLoading, login, logout, auth } = useBodhi();

  if (isAuthenticated) {
    return (
      <div>
        <span>Logged in as {auth.user?.username}</span>
        <button onClick={logout}>Logout</button>
      </div>
    );
  }

  return (
    <button onClick={login} disabled={!canLogin}>
      {isAuthLoading ? 'Logging in...' : 'Login'}
    </button>
  );
}

export default AuthButton;
```

## Models API

### Load Models with AsyncGenerator

```tsx
import { useState, useEffect } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function ModelSelector() {
  const { client, isOverallReady, isAuthenticated } = useBodhi();
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState('');

  const loadModels = async () => {
    setLoading(true);
    try {
      const modelList: string[] = [];
      for await (const model of client.models.list()) {
        modelList.push(model.id);
      }
      setModels(modelList);
      if (modelList.length > 0) {
        setSelected(modelList[0]);
      }
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOverallReady && isAuthenticated) {
      loadModels();
    }
  }, [isOverallReady, isAuthenticated]);

  return (
    <div>
      <select value={selected} onChange={e => setSelected(e.target.value)} disabled={loading || models.length === 0}>
        {loading ? (
          <option>Loading models...</option>
        ) : models.length === 0 ? (
          <option>No models available</option>
        ) : (
          models.map(model => (
            <option key={model} value={model}>
              {model}
            </option>
          ))
        )}
      </select>
      <button onClick={loadModels} disabled={loading}>
        Refresh
      </button>
    </div>
  );
}

export default ModelSelector;
```

### Models with localStorage Cache

```tsx
import { useState, useEffect } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

const CACHE_KEY = 'bodhi_models_cache';
const CACHE_EXPIRY_MS = 3600000; // 1 hour

interface ModelsCache {
  models: string[];
  expiry: number;
}

function useModels() {
  const { client, isOverallReady, isAuthenticated } = useBodhi();
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const loadModels = async (bustCache = false) => {
    if (!bustCache) {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        try {
          const { models: cachedModels, expiry }: ModelsCache = JSON.parse(cached);
          if (Date.now() < expiry) {
            setModels(cachedModels);
            return;
          }
        } catch (err) {
          console.error('Cache parse error:', err);
        }
      }
    }

    setLoading(true);
    try {
      const modelList: string[] = [];
      for await (const model of client.models.list()) {
        modelList.push(model.id);
      }
      setModels(modelList);

      const cache: ModelsCache = {
        models: modelList,
        expiry: Date.now() + CACHE_EXPIRY_MS,
      };
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOverallReady && isAuthenticated) {
      loadModels();
    }
  }, [isOverallReady, isAuthenticated]);

  return { models, loading, loadModels };
}

export default useModels;
```

## Chat Completions

### Streaming Chat Component

```tsx
import { useState, FormEvent } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

interface ChatProps {
  model: string;
}

function Chat({ model }: ChatProps) {
  const { client } = useBodhi();
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !model) return;

    setLoading(true);
    setResponse('');

    try {
      const stream = client.chat.completions.create({
        model,
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

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="text" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Ask me anything..." disabled={loading} />
        <button type="submit" disabled={loading || !model}>
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

### Multi-Turn Conversation

```tsx
import { useState, FormEvent } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function Conversation({ model }: { model: string }) {
  const { client } = useBodhi();
  const [messages, setMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !model) return;

    const userMessage: Message = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);
    setPrompt('');
    setLoading(true);

    try {
      const stream = client.chat.completions.create({
        model,
        messages: [...messages, userMessage],
        stream: true,
      });

      let assistantContent = '';
      for await (const chunk of stream) {
        const content = chunk.choices?.[0]?.delta?.content || '';
        assistantContent += content;
        setMessages(prev => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (updated[lastIdx]?.role === 'assistant') {
            updated[lastIdx] = { role: 'assistant', content: assistantContent };
          } else {
            updated.push({ role: 'assistant', content: assistantContent });
          }
          return updated;
        });
      }
    } catch (err) {
      const errorMsg: Message = {
        role: 'assistant',
        content: `Error: ${err instanceof Error ? err.message : String(err)}`,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input type="text" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Continue the conversation..." disabled={loading} />
        <button type="submit" disabled={loading || !model}>
          {loading ? 'Generating...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default Conversation;
```

### Non-Streaming Chat

```tsx
import { useState, FormEvent } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function SimpleChat({ model }: { model: string }) {
  const { client } = useBodhi();
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !model) return;

    setLoading(true);
    setResponse('');

    try {
      const result = await client.chat.completions.create({
        model,
        messages: [{ role: 'user', content: prompt }],
        stream: false,
      });

      setResponse(result.choices?.[0]?.message?.content || 'No response');
    } catch (err) {
      setResponse(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="text" value={prompt} onChange={e => setPrompt(e.target.value)} disabled={loading} />
        <button type="submit" disabled={loading || !model}>
          {loading ? 'Loading...' : 'Send'}
        </button>
      </form>
      {response && <p>{response}</p>}
    </div>
  );
}

export default SimpleChat;
```

## Complete App Examples

### Full Chat Application

```tsx
// App.tsx
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';
import ChatApp from './ChatApp';

const CLIENT_ID = import.meta.env.VITE_BODHI_CLIENT_ID;

function App() {
  return (
    <BodhiProvider authClientId={CLIENT_ID}>
      <ChatApp />
    </BodhiProvider>
  );
}

export default App;

// ChatApp.tsx
import { useState, useEffect } from 'react';
import { useBodhi } from '@bodhiapp/bodhi-js-react';

function ChatApp() {
  const { client, isOverallReady, isAuthenticated, login, showSetup } = useBodhi();
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

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
    return (
      <div className="setup-screen">
        <h1>Setup Required</h1>
        <button onClick={showSetup}>Open Setup Wizard</button>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="login-screen">
        <h1>Login Required</h1>
        <button onClick={login}>Login with OAuth</button>
      </div>
    );
  }

  return (
    <div className="chat-app">
      <header>
        <h1>Bodhi Chat</h1>
        <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
          {models.map(m => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </header>

      <main>
        {response && (
          <div className="response">
            <p style={{ whiteSpace: 'pre-wrap' }}>{response}</p>
          </div>
        )}
      </main>

      <footer>
        <form onSubmit={handleSubmit}>
          <input type="text" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Ask me anything..." disabled={loading} />
          <button type="submit" disabled={loading || !selectedModel}>
            {loading ? 'Generating...' : 'Send'}
          </button>
        </form>
      </footer>
    </div>
  );
}

export default ChatApp;
```

## Environment Configuration

**.env.development**:

```env
VITE_BODHI_CLIENT_ID=app-dev-client-id-uuid
VITE_BODHI_AUTH_SERVER=https://main-id.getbodhi.app/realms/bodhi
VITE_BODHI_REDIRECT_URI=http://localhost:5173/callback
```

**.env.production**:

```env
VITE_BODHI_CLIENT_ID=app-prod-client-id-uuid
VITE_BODHI_AUTH_SERVER=https://id.getbodhi.app/realms/bodhi
VITE_BODHI_REDIRECT_URI=https://myapp.com/callback
```

**vite-env.d.ts**:

```typescript
interface ImportMetaEnv {
  readonly VITE_BODHI_CLIENT_ID: string;
  readonly VITE_BODHI_AUTH_SERVER?: string;
  readonly VITE_BODHI_REDIRECT_URI?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## TypeScript Types

```typescript
import type { BodhiContext, ClientContextState, AuthState, UIClient } from '@bodhiapp/bodhi-js-react';

import type { CreateChatCompletionRequest, CreateChatCompletionResponse, CreateChatCompletionStreamResponse, Model, ChatCompletionMessage } from '@bodhiapp/bodhi-js-core';

// Example typed component
interface ChatProps {
  model: string;
  onResponse?: (response: string) => void;
}

function TypedChat({ model, onResponse }: ChatProps) {
  const context: BodhiContext = useBodhi();
  // ... implementation
}
```

## Testing Patterns

```tsx
// Mock BodhiProvider for tests
import { ReactNode } from 'react';
import { BodhiProvider } from '@bodhiapp/bodhi-js-react';

export function TestBodhiProvider({ children }: { children: ReactNode }) {
  return <BodhiProvider authClientId="test-client-id">{children}</BodhiProvider>;
}

// Usage in tests
import { render } from '@testing-library/react';
import { TestBodhiProvider } from './test-utils';
import Chat from './Chat';

test('renders chat component', () => {
  render(
    <TestBodhiProvider>
      <Chat model="test-model" />
    </TestBodhiProvider>
  );
});
```

## Additional Resources

- **SDK Docs**: `bodhi-js-sdk/docs/` for comprehensive guides
- **Reference App**: `sdk-test-app/` for production-ready example
- **API Reference**: `bodhi-js-sdk/docs/api-reference.md` for complete API
