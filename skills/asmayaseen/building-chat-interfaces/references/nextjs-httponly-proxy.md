# Next.js httpOnly Cookie Proxy Patterns

## Why Proxy is Needed

httpOnly cookies are a security feature - they CANNOT be read by JavaScript. This protects against XSS attacks stealing tokens.

When your auth system stores JWT tokens in httpOnly cookies (like Auth0, Better Auth, etc.), the frontend cannot:
- Read the token to add to headers
- Check if user is authenticated (directly)
- Forward tokens to API calls

## Solution: Server-Side API Route Proxy

Create a Next.js API route that:
1. Reads httpOnly cookies (server-side only)
2. Adds Authorization header
3. Proxies request to backend
4. Streams SSE responses back

## Complete Proxy Implementation

```typescript
// app/api/chatkit/route.ts
import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();

  // Read httpOnly cookie (only accessible server-side)
  const idToken = cookieStore.get("taskflow_id_token")?.value;

  if (!idToken) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  // Build target URL - note: ChatKit endpoint is at /chatkit, NOT /api/chatkit
  const url = new URL("/chatkit", API_BASE);

  try {
    const body = await request.text();

    // Forward request with Authorization header
    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${idToken}`,
        "Content-Type": "application/json",
        // Forward custom headers
        "X-User-ID": request.headers.get("X-User-ID") || "",
        "X-Page-URL": request.headers.get("X-Page-URL") || "",
      },
      body: body || undefined,
    });

    // Handle SSE streaming responses
    if (response.headers.get("content-type")?.includes("text/event-stream")) {
      return new Response(response.body, {
        status: response.status,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // Return JSON for non-streaming responses
    const data = await response.json().catch(() => null);
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[ChatKit Proxy] Error:", error);
    return NextResponse.json({ error: "ChatKit proxy request failed" }, { status: 500 });
  }
}
```

## Frontend Usage with Proxy

```typescript
const chatkitProxyUrl = "/api/chatkit"; // Proxy handles auth

const { control, sendUserMessage } = useChatKit({
  api: {
    url: chatkitProxyUrl,
    domainKey: domainKey,

    // Custom fetch - auth handled by proxy, inject context
    fetch: async (input: RequestInfo | URL, options?: RequestInit) => {
      const url = typeof input === 'string' ? input : input.toString();

      // Client-side auth check (proxy will verify token)
      if (!isAuthenticated) {
        throw new Error('User must be logged in');
      }

      const userId = user.sub;
      const pageContext = getPageContext();

      // Inject metadata into request body
      let modifiedOptions = { ...options } as RequestInit;
      if (modifiedOptions.body && typeof modifiedOptions.body === 'string') {
        try {
          const parsed = JSON.parse(modifiedOptions.body);
          if (parsed.params?.input) {
            parsed.params.input.metadata = {
              ...parsed.params.input.metadata,
              userId,
              userInfo: { id: userId, name: user.name },
              pageContext,
            };
            modifiedOptions.body = JSON.stringify(parsed);
          }
        } catch { /* Ignore non-JSON */ }
      }

      return fetch(url, {
        ...modifiedOptions,
        credentials: 'include', // Include cookies for proxy auth
        headers: {
          ...modifiedOptions.headers,
          'X-User-ID': userId,
          'X-Page-URL': pageContext?.url || '',
          'Content-Type': 'application/json',
        },
      });
    },
  },
});
```

## Script Loading for Web Components

ChatKit uses web components that must be defined before React renders them:

```tsx
// app/layout.tsx
import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* MUST be in <head> with beforeInteractive for web components */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong backend endpoint | 404 errors | Route to `/chatkit` not `/api/chatkit` |
| Script loading too late | "ChatKit web component unavailable" | Use `beforeInteractive` in `<head>` |
| Cookies not sent | Auth fails silently | Add `credentials: 'include'` to fetch |
| SSE not streaming | Response arrives all at once | Return `Response(body)` not `NextResponse.json()` |