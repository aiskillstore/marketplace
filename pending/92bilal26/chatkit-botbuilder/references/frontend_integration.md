# ChatKit Frontend Integration Guide

## Next.js Setup

### 1. Install Dependencies

```bash
npm install @openai/chatkit-react better-auth jose
```

### 2. ChatKit Configuration File

Create `lib/chatkit-config.ts`:

```typescript
import type { UseChatKitOptions } from '@openai/chatkit-react'

// Environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const DOMAIN_KEY = process.env.NEXT_PUBLIC_DOMAIN_KEY || 'chatkit-app-dev'

// ChatKit endpoint
const API_URL = `${API_BASE_URL}/api/v1/chatkit`

/**
 * Extract JWT token from multiple possible locations
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null

  // Try access_token (standard from API client)
  let token = localStorage.getItem('access_token')
  if (token) return token

  // Try auth_token (alternative)
  token = localStorage.getItem('auth_token')
  if (token) return token

  // Try session token (Better Auth)
  token = localStorage.getItem('authjs.session-token')
  if (token) return token

  // Try sessionStorage
  token = sessionStorage.getItem('access_token')
  if (token) return token

  return null
}

/**
 * Custom fetch function with JWT authentication
 * All ChatKit API calls go through this function
 */
async function authenticatedFetch(
  input: string | URL | Request,
  options?: RequestInit
): Promise<Response> {
  const token = getAuthToken()

  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string> || {}),
  }

  // Add JWT token if available
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Add domain key for ChatKit verification
  headers['X-ChatKit-Domain-Key'] = DOMAIN_KEY

  return fetch(input, {
    ...options,
    headers,
  })
}

/**
 * ChatKit Configuration
 * Ready-to-use configuration for ChatKit widget
 */
export const chatKitConfig: UseChatKitOptions = {
  api: {
    url: API_URL,
    domainKey: DOMAIN_KEY,
    fetch: authenticatedFetch,
  },

  theme: 'light',

  header: {
    enabled: true,
    title: {
      enabled: true,
      text: 'TaskPilot AI Chat',
    },
  },

  history: {
    enabled: true,
    showDelete: true,
    showRename: true,
  },

  composer: {
    placeholder: 'Ask me to add, update, or delete tasks...',
  },

  disclaimer: {
    text: 'ChatKit powered by OpenAI • Managed by TaskPilot AI',
  },

  // Event handlers
  onReady: () => {
    console.log('ChatKit is ready!')
  },

  onError: (error: { error: Error }) => {
    console.error('ChatKit error:', error.error)
  },

  onResponseStart: () => {
    console.log('Assistant is responding...')
  },

  onResponseEnd: () => {
    console.log('Assistant response complete')
  },

  onThreadChange: (event: { threadId: string | null }) => {
    if (event.threadId) {
      localStorage.setItem('chatkit_thread_id', event.threadId)
    }
  },
}

/**
 * Get current ChatKit thread ID
 */
export function getChatKitThreadId(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('chatkit_thread_id')
}

/**
 * Clear ChatKit thread from localStorage
 */
export function clearChatKitThread(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem('chatkit_thread_id')
}

/**
 * Validate ChatKit configuration
 */
export function validateChatKitConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!API_BASE_URL) {
    errors.push('NEXT_PUBLIC_API_URL is not configured')
  }

  if (!API_URL) {
    errors.push('ChatKit endpoint URL could not be constructed')
  }

  if (!DOMAIN_KEY || typeof DOMAIN_KEY !== 'string') {
    errors.push('NEXT_PUBLIC_DOMAIN_KEY is not properly configured')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}
```

### 3. Environment Configuration

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DOMAIN_KEY=chatkit-app-dev
```

### 4. ChatKit Widget Component

```typescript
import React from 'react'
import { ChatKitWidget } from '@openai/chatkit-react'
import { chatKitConfig } from '@/lib/chatkit-config'

interface ChatKitPanelProps {
  authToken?: string
  userId?: string
}

export function ChatKitPanel({ authToken, userId }: ChatKitPanelProps) {
  if (!authToken || !userId) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Loading authentication...
      </div>
    )
  }

  return (
    <div className="w-full h-full overflow-hidden flex flex-col bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">TaskPilot AI Chat</h3>
        <p className="text-sm text-gray-500 mt-1">Powered by OpenAI ChatKit</p>
      </div>
      <div className="flex-1 overflow-hidden">
        <ChatKitWidget {...chatKitConfig} />
      </div>
    </div>
  )
}
```

### 5. Integration into Dashboard

```typescript
'use client'

import { useState, useEffect } from 'react'
import { ChatKitPanel } from '@/components/ChatKit/ChatKitPanel'

export default function DashboardPage() {
  const [authToken, setAuthToken] = useState<string>('')
  const [userId, setUserId] = useState<string>('')
  const [showChat, setShowChat] = useState(false)
  const [tasks, setTasks] = useState([])

  // Extract user ID from JWT
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        setAuthToken(token)
        try {
          const parts = token.split('.')
          if (parts.length === 3) {
            const decoded = JSON.parse(atob(parts[1]))
            setUserId(decoded.user_id || decoded.sub || '')
          }
        } catch (e) {
          console.error('Failed to decode token:', e)
        }
      }
    }
  }, [])

  // Auto-refresh tasks when ChatKit is active
  useEffect(() => {
    if (!showChat) return

    // Fetch immediately
    fetchTasks()

    // Fetch every 1 second
    const interval = setInterval(() => {
      fetchTasks()
    }, 1000)

    return () => clearInterval(interval)
  }, [showChat])

  const fetchTasks = async () => {
    const response = await fetch('/api/tasks', {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    })
    if (response.ok) {
      const data = await response.json()
      setTasks(data.tasks || [])
    }
  }

  return (
    <div className="flex gap-4 p-6">
      {/* Tasks Section */}
      <div className={`flex-1 ${showChat ? 'w-1/2' : 'w-full'}`}>
        <button
          onClick={() => setShowChat(!showChat)}
          className={showChat ? 'bg-green-600' : 'bg-blue-600'}
        >
          {showChat ? '✓ Chat Active' : '💬 Open Chat'}
        </button>

        {/* Your task list UI here */}
        <div className="space-y-4 mt-4">
          {tasks.map((task) => (
            <div key={task.id} className="p-4 border rounded">
              <h3>{task.title}</h3>
              <p>{task.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ChatKit Section */}
      {showChat && (
        <div className="w-1/2 min-w-0">
          <ChatKitPanel authToken={authToken} userId={userId} />
        </div>
      )}
    </div>
  )
}
```

## Authentication Flow

### 1. User Login

```typescript
// User logs in via Better Auth or your auth system
const { data } = await authClient.signIn.email({
  email: 'user@example.com',
  password: 'password',
})

// JWT token is returned and stored
localStorage.setItem('access_token', data.token)
```

### 2. Token in localStorage

```typescript
// Token structure
// Header: { alg: "HS256", typ: "JWT" }
// Payload: { user_id: "user-123", email: "user@example.com", iat: ... }
// Signature: ...
```

### 3. authenticatedFetch Adds Token

```typescript
// Every fetch call includes authorization
const response = await authenticatedFetch('/api/v1/chatkit', {
  method: 'POST',
  body: JSON.stringify({ message: 'Create a task' }),
})

// Becomes:
// Authorization: Bearer <token>
```

### 4. Backend Validates Token

```python
# JWT middleware extracts and validates
payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
user_id = payload.get('user_id')
request.state.user_id = user_id  # Available to ChatKit endpoint
```

## Real-Time Synchronization

### Auto-Refresh Strategy

```typescript
// When chat is active, refresh task list every 1 second
useEffect(() => {
  if (!showChat) return

  const interval = setInterval(() => {
    fetchTasks()
  }, 1000)

  return () => clearInterval(interval)
}, [showChat])
```

### Why This Works

1. **User creates task in ChatKit** - "Create 'Buy milk'"
2. **ChatKit calls add_task tool** - Tool creates in database with user_id
3. **Dashboard auto-refreshes** - GET /tasks called with same user_id
4. **Task appears** - Dashboard shows newly created task

## Environment Variables

Create `.env.local`:

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# ChatKit Configuration
NEXT_PUBLIC_DOMAIN_KEY=chatkit-app-dev

# OpenAI (if frontend needs it)
NEXT_PUBLIC_OPENAI_API_KEY=sk-your-key-here
```

## Development vs Production

### Development
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DOMAIN_KEY=chatkit-dev
```

### Production
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_DOMAIN_KEY=chatkit-production
```

## Debugging

### Check Token in Console

```typescript
const token = localStorage.getItem('access_token')
const decoded = JSON.parse(atob(token.split('.')[1]))
console.log('User ID:', decoded.user_id)
```

### Check ChatKit Config

```typescript
import { validateChatKitConfig } from '@/lib/chatkit-config'
const { valid, errors } = validateChatKitConfig()
if (!valid) console.error('Config errors:', errors)
```

### Monitor Network Requests

1. Open DevTools → Network
2. Send message in ChatKit
3. Look for POST to `/api/v1/chatkit`
4. Check headers for `Authorization: Bearer <token>`
5. Check response for StreamingResult

## Performance Tips

1. **Lazy load ChatKit widget** - Only load when user opens chat
2. **Batch refresh requests** - Use debounce instead of direct calls
3. **Cache tokens** - Store in localStorage, refresh on expiry
4. **Minimize re-renders** - Use useCallback for fetch functions
5. **Monitor polling** - Adjust interval based on your needs
