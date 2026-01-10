# OAuth Integration Guide

Set up authentication for ChatGPT Apps that require user-specific data or write operations.

## When Authentication is Required

You need OAuth if your app:
- Accesses user-specific data (their tasks, their orders, etc.)
- Performs write operations (create, update, delete)
- Connects to the user's account in your service

You do NOT need OAuth if:
- Your app only provides public/anonymous data
- No user identity is required

---

## OAuth 2.1 Architecture

ChatGPT implements OAuth 2.1 with PKCE and dynamic client registration:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ChatGPT    │────▶│  Your Auth   │────▶│  Your MCP    │
│   (Client)   │     │   Server     │     │   Server     │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │  1. Discover       │                    │
       │─────────────────▶  │                    │
       │                    │                    │
       │  2. Register       │                    │
       │─────────────────▶  │                    │
       │                    │                    │
       │  3. Auth + PKCE    │                    │
       │─────────────────▶  │                    │
       │                    │                    │
       │  4. Token          │                    │
       │◀─────────────────  │                    │
       │                    │                    │
       │  5. API Request with Bearer token       │
       │─────────────────────────────────────────▶
```

---

## Required Well-Known Endpoints

### 1. Protected Resource Metadata
**Endpoint**: `/.well-known/oauth-protected-resource`

```json
{
  "resource": "https://mcp.yourapp.com",
  "authorization_servers": ["https://auth.yourapp.com"],
  "scopes_supported": ["read:items", "write:items"],
  "resource_documentation": "https://yourapp.com/docs/api"
}
```

**Fields**:
- `resource`: Canonical URL of your MCP server (exact match required)
- `authorization_servers`: Array of OAuth provider URLs
- `scopes_supported`: Available permission scopes
- `resource_documentation`: Link to API docs (optional)

### 2. OAuth Authorization Server Metadata
**Endpoint**: `/.well-known/oauth-authorization-server`

```json
{
  "issuer": "https://auth.yourapp.com",
  "authorization_endpoint": "https://auth.yourapp.com/oauth2/authorize",
  "token_endpoint": "https://auth.yourapp.com/oauth2/token",
  "registration_endpoint": "https://auth.yourapp.com/oauth2/register",
  "code_challenge_methods_supported": ["S256"],
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "scopes_supported": ["read:items", "write:items", "offline_access"]
}
```

**Required Fields**:
- `issuer`: OAuth provider identifier
- `authorization_endpoint`: Where users authenticate
- `token_endpoint`: Where tokens are exchanged
- `registration_endpoint`: For dynamic client registration
- `code_challenge_methods_supported`: Must include `"S256"` (PKCE)

### Dynamic Client Registration (REQUIRED)

ChatGPT **requires** RFC 7591 Dynamic Client Registration. Your authorization server MUST expose a `/oauth/register` endpoint that accepts client registration requests. Without this, connector creation will fail with:

> "server doesn't support RFC 7591 Dynamic Client Registration"

This is non-negotiable—ChatGPT will not prompt for manual client credentials. The registration endpoint must:
- Accept POST requests with `client_name` and `redirect_uris`
- Return a `client_id` (and optionally `client_secret`)
- Be publicly accessible (no authentication required)

---

## Redirect URIs

Configure these redirect URIs in your OAuth provider:

**Production**:
```
https://chatgpt.com/connector_platform_oauth_redirect
```

**App Review**:
```
https://platform.openai.com/apps-manage/oauth
```

---

## Provider-Specific Setup

### Auth0

1. Create an API in Auth0 Dashboard
2. Configure Application:
   ```
   Application Type: Regular Web Application
   Allowed Callback URLs:
     https://chatgpt.com/connector_platform_oauth_redirect
     https://platform.openai.com/apps-manage/oauth
   Allowed Web Origins: https://chatgpt.com
   ```

3. Enable Dynamic Client Registration:
   ```
   Tenant Settings → Advanced → Enable Dynamic Client Registration
   ```

4. Auth0 provides well-known endpoints automatically:
   ```
   https://YOUR_DOMAIN.auth0.com/.well-known/oauth-authorization-server
   ```

### Stytch

1. Create a Stytch project
2. Configure OAuth:
   ```
   OAuth Settings → Redirect URLs:
     https://chatgpt.com/connector_platform_oauth_redirect
     https://platform.openai.com/apps-manage/oauth
   ```

3. Enable MCP Authorization in Stytch Dashboard

4. Stytch provides MCP-compatible endpoints automatically

### Self-Hosted OAuth Server (Recommended for Full Control)

For apps that want complete control over authentication, a self-hosted OAuth 2.1 server with PKCE works well. This approach doesn't require third-party services like Auth0 or Stytch.

**Required Endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/oauth-protected-resource` | Resource metadata |
| `/.well-known/oauth-authorization-server` | Auth server metadata |
| `/oauth/register` | Dynamic client registration (RFC 7591) |
| `/oauth/authorize` | User authorization |
| `/oauth/token` | Token exchange |

**Complete Implementation:**

```typescript
import { createHash, randomBytes } from "crypto";

// In-memory storage (use Redis/database for production)
const authCodes = new Map<string, AuthCode>();
const accessTokens = new Map<string, AccessToken>();
const clients = new Map<string, ClientInfo>();

interface AuthCode {
  clientId: string;
  redirectUri: string;
  codeChallenge: string;
  expiresAt: number;
}

interface AccessToken {
  clientId: string;
  expiresAt: number;
}

interface ClientInfo {
  clientName: string;
  redirectUris: string[];
}

// Well-known metadata endpoints
app.get("/.well-known/oauth-protected-resource", (req, res) => {
  res.json({
    resource: BASE_URL,
    authorization_servers: [BASE_URL],
    scopes_supported: ["read", "write"]
  });
});

app.get("/.well-known/oauth-authorization-server", (req, res) => {
  res.json({
    issuer: BASE_URL,
    authorization_endpoint: `${BASE_URL}/oauth/authorize`,
    token_endpoint: `${BASE_URL}/oauth/token`,
    registration_endpoint: `${BASE_URL}/oauth/register`,
    code_challenge_methods_supported: ["S256"],
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code", "refresh_token"]
  });
});

// Dynamic Client Registration (RFC 7591) - REQUIRED BY CHATGPT
app.post("/oauth/register", express.json(), (req, res) => {
  const { client_name, redirect_uris } = req.body;
  const client_id = `client-${randomBytes(16).toString("hex")}`;

  clients.set(client_id, {
    clientName: client_name,
    redirectUris: redirect_uris
  });

  res.status(201).json({
    client_id,
    client_name,
    redirect_uris,
    token_endpoint_auth_method: "none"
  });
});

// Authorization endpoint - show consent UI
app.get("/oauth/authorize", (req, res) => {
  const { client_id, redirect_uri, code_challenge, state } = req.query;

  // In production: show a proper consent UI
  // For demo: auto-approve and redirect

  const code = randomBytes(32).toString("base64url");
  authCodes.set(code, {
    clientId: client_id as string,
    redirectUri: redirect_uri as string,
    codeChallenge: code_challenge as string,
    expiresAt: Date.now() + 600000 // 10 minutes
  });

  res.redirect(`${redirect_uri}?code=${code}&state=${state}`);
});

// Token exchange endpoint
app.post("/oauth/token", express.urlencoded({ extended: true }), (req, res) => {
  const { grant_type, code, code_verifier, redirect_uri } = req.body;

  if (grant_type !== "authorization_code") {
    return res.status(400).json({ error: "unsupported_grant_type" });
  }

  const authCode = authCodes.get(code);
  if (!authCode || authCode.expiresAt < Date.now()) {
    return res.status(400).json({ error: "invalid_grant" });
  }

  // Verify PKCE (S256)
  const hash = createHash("sha256").update(code_verifier).digest("base64url");
  if (hash !== authCode.codeChallenge) {
    return res.status(400).json({ error: "invalid_grant", error_description: "PKCE verification failed" });
  }

  // Generate access token
  const access_token = randomBytes(32).toString("base64url");
  accessTokens.set(access_token, {
    clientId: authCode.clientId,
    expiresAt: Date.now() + 3600000 // 1 hour
  });

  authCodes.delete(code);

  res.json({
    access_token,
    token_type: "Bearer",
    expires_in: 3600
  });
});

// Token verification helper
function verifyAccessToken(authHeader: string | undefined): boolean {
  if (!authHeader?.startsWith("Bearer ")) return false;
  const token = authHeader.slice(7);
  const tokenData = accessTokens.get(token);
  return tokenData !== undefined && tokenData.expiresAt > Date.now();
}
```

**Production Considerations:**
- Use Redis or a database for token storage (in-memory tokens are lost on restart)
- Implement proper consent UI instead of auto-approve
- Add refresh token support for long-running sessions
- Consider rate limiting the registration endpoint
- Add proper error handling and logging

---

## Tool-Level Security Schemes

Mark which tools require authentication:

```typescript
server.registerTool(
  "myapp_get_items",
  {
    title: "Get Items",
    description: "...",
    inputSchema: GetItemsSchema,
    securitySchemes: [{
      type: "oauth2",
      scopes: ["read:items"]
    }],
    _meta: {
      "openai/readOnlyHint": true
    }
  },
  async (params, context) => {
    // Access token is in context
    const token = context.accessToken;
    // Verify and use token...
  }
);
```

### Security Scheme Types

```typescript
// No auth required
securitySchemes: [{ type: "noauth" }]

// OAuth required with specific scopes
securitySchemes: [{
  type: "oauth2",
  scopes: ["read:items", "write:items"]
}]
```

---

## Token Verification

Your MCP server must verify tokens independently:

```typescript
import jwt from "jsonwebtoken";
import jwksClient from "jwks-rsa";

const client = jwksClient({
  jwksUri: "https://auth.yourapp.com/.well-known/jwks.json",
  cache: true,
  rateLimit: true
});

async function verifyToken(token: string): Promise<TokenPayload> {
  return new Promise((resolve, reject) => {
    jwt.verify(
      token,
      (header, callback) => {
        client.getSigningKey(header.kid, (err, key) => {
          if (err) return callback(err);
          callback(null, key?.getPublicKey());
        });
      },
      {
        algorithms: ["RS256"],
        issuer: "https://auth.yourapp.com",
        audience: "https://mcp.yourapp.com"
      },
      (err, decoded) => {
        if (err) return reject(err);
        resolve(decoded as TokenPayload);
      }
    );
  });
}

// In tool handler
async function handleTool(params: unknown, context: ToolContext) {
  const authHeader = context.headers?.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return {
      content: [{ type: "text", text: "Authentication required" }],
      _meta: {
        "mcp/www_authenticate": [
          `Bearer resource_metadata="https://mcp.yourapp.com/.well-known/oauth-protected-resource", error="invalid_token"`
        ]
      },
      isError: true
    };
  }

  const token = authHeader.slice(7);

  try {
    const payload = await verifyToken(token);
    // Check scopes
    if (!payload.scope?.includes("read:items")) {
      throw new Error("Insufficient scope");
    }
    // Proceed with authorized request...
  } catch (error) {
    return {
      content: [{ type: "text", text: "Authentication failed" }],
      _meta: {
        "mcp/www_authenticate": [
          `Bearer resource_metadata="https://mcp.yourapp.com/.well-known/oauth-protected-resource", error="invalid_token"`
        ]
      },
      isError: true
    };
  }
}
```

### Accessing Tokens in SSE Transport Mode

**Important**: The MCP SDK does not automatically pass HTTP headers to tool handlers when using SSE transport. ChatGPT sends OAuth tokens as `Authorization: Bearer <token>` HTTP headers, NOT in the MCP message's `_meta.authorization` field.

You must manually bridge HTTP headers to your tool handlers:

```typescript
// Global to track current request's auth header
let currentRequestAuthHeader: string | undefined;

// In your HTTP POST handler for /mcp
if (url.pathname === "/mcp" && req.method === "POST") {
  // Capture the auth header before processing the message
  currentRequestAuthHeader = req.headers.authorization;

  // ... handle MCP message
}

// In your tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Use the captured HTTP header
  const authHeader = currentRequestAuthHeader;

  if (!authHeader?.startsWith("Bearer ")) {
    return authErrorResponse();
  }

  const token = authHeader.slice(7);
  const isValid = await verifyToken(token);
  // ...
});
```

**Why this is needed**: SSE transport receives messages via HTTP POST, but the MCP protocol layer doesn't expose the HTTP headers to the tool context. The token is in the HTTP request, not the JSON-RPC message body.

---

## Triggering Authentication UI

ChatGPT shows the OAuth login flow when:

1. Your resource metadata is published at well-known URL
2. Tool declares `securitySchemes` with `oauth2`
3. Server returns 401 with proper `WWW-Authenticate` header

### HTTP-Level Authentication (Recommended)

For 401 responses to properly trigger the OAuth flow, include the `WWW-Authenticate` header:

```typescript
// In your HTTP server handler
if (response.status === 401) {
  res.setHeader("WWW-Authenticate", "Bearer");
  res.writeHead(401).end("Unauthorized");
  return;
}
```

**Important**: Without the `WWW-Authenticate` header, 401 errors may show an error to users instead of the login prompt.

### Tool-Level Authentication Response

Alternatively, return authentication metadata from tool responses:

```typescript
// Return this to trigger auth flow
return {
  content: [{ type: "text", text: "Please connect your account" }],
  _meta: {
    "mcp/www_authenticate": [
      `Bearer resource_metadata="https://mcp.yourapp.com/.well-known/oauth-protected-resource", error="unauthorized"`
    ]
  },
  isError: true
};
```

**Format**: The `mcp/www_authenticate` field must be an **array of strings** following WWW-Authenticate header syntax, not an object.

---

## OAuth Flow Timing

Understanding when OAuth happens helps with debugging and architecture decisions:

### Flow Timeline

1. **User adds connector** → ChatGPT initiates OAuth flow
2. **User authenticates** → Redirected to your authorization endpoint
3. **User consents** → Authorization code exchanged for access token
4. **Token cached** → ChatGPT stores and reuses the token for all subsequent requests
5. **Tool calls** → Every request includes `Authorization: Bearer <token>` header

### Key Insights

- **OAuth happens ONCE** at connector creation, not per-request
- **ChatGPT caches the token** and sends it with every tool call
- **Server restarts** lose in-memory tokens, but ChatGPT still sends its cached copy
- **Token must be verified** on every request (ChatGPT sends it, you verify it)

### Production Considerations: Token Storage

**Critical**: In-memory token storage fails in production because server restarts lose all tokens.

```typescript
// ❌ In-memory token storage - tokens lost on restart
const accessTokens = new Map<string, TokenData>();

// ✅ Persistent storage - tokens survive restarts
```

**Option 1: Redis (recommended for high traffic)**
```typescript
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

async function storeToken(token: string, data: TokenData) {
  await redis.set(`token:${token}`, JSON.stringify(data), "EX", 3600);
}

async function getToken(token: string): Promise<TokenData | null> {
  const data = await redis.get(`token:${token}`);
  return data ? JSON.parse(data) : null;
}
```

**Option 2: Database (e.g., Supabase/PostgreSQL)**
```typescript
import { createClient } from "@supabase/supabase-js";
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

async function storeToken(token: string, userId: string, data: TokenData) {
  await supabase.from("oauth_tokens").upsert({
    token_hash: hashToken(token),  // Never store tokens in plain text
    user_id: userId,
    expires_at: new Date(Date.now() + 3600 * 1000),
    ...data,
  });
}
```

**Hybrid approach (LRU cache + database)**
```typescript
// Fast lookups with LRU cache, persistent storage for reliability
const tokenCache = new Map<string, TokenData>();
const MAX_CACHE_SIZE = 10000;

async function getToken(token: string): Promise<TokenData | null> {
  // Check cache first
  if (tokenCache.has(token)) {
    return tokenCache.get(token)!;
  }

  // Fall back to database
  const data = await loadFromDatabase(token);
  if (data) {
    // LRU eviction if at capacity
    if (tokenCache.size >= MAX_CACHE_SIZE) {
      const oldestKey = tokenCache.keys().next().value;
      tokenCache.delete(oldestKey);
    }
    tokenCache.set(token, data);
  }
  return data;
}
```

For development/demos, in-memory storage works fine. For production apps, use persistent storage.

---

## Test Credentials for Review

When submitting your app, you must provide test credentials:

1. Create a test account in your system with sample data
2. Document the credentials:
   ```
   Test Account:
   Email: reviewer@example.com
   Password: TestPassword123!

   Sample Data:
   - 5 sample items pre-populated
   - Test project "Demo Project"
   ```
3. Ensure the test account has full functionality
4. Don't require 2FA for the test account

**Common rejection reason**: Missing or non-functional test credentials.

---

## Security Checklist

- [ ] Well-known endpoints accessible and valid JSON
- [ ] PKCE (`S256`) supported
- [ ] Dynamic client registration enabled
- [ ] Redirect URIs configured for both production and review
- [ ] Token verification implemented in MCP server
- [ ] Scopes properly checked in tool handlers
- [ ] `_meta["mcp/www_authenticate"]` returned on auth errors
- [ ] Test credentials documented and functional
- [ ] Refresh token flow supported (for long sessions)
