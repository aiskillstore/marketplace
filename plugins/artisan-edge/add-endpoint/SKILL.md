---
name: add-endpoint
description: Add new HTTP endpoints to Catalyst-Relay server. Use when creating routes, API endpoints, or HTTP handlers.
---

# Adding HTTP Endpoints

## When to Use

- Creating a new HTTP route
- Adding an API endpoint
- Wiring a new handler to the Hono app

## Route File Pattern

Each endpoint gets its own file with colocated schema, types, and handler.

**Location:** `src/server/routes/{category}/{endpoint}.ts`

```typescript
// src/server/routes/auth/login.ts

import { z } from 'zod';
import type { Context } from 'hono';
import type { ISessionManager } from '../types';

// 1. Request schema (colocated)
export const loginRequestSchema = z.object({
    url: z.string().url(),
    client: z.string().min(1).max(3),
    auth: authConfigSchema
});

// 2. Response type (colocated)
export interface LoginResponse {
    sessionId: string;
    username: string;
    expiresAt: number;
}

// 3. Single handler export (factory pattern)
export function loginHandler(sessionManager: ISessionManager) {
    return async (c: Context) => {
        const body = await c.req.json();
        const validation = loginRequestSchema.safeParse(body);

        if (!validation.success) {
            return c.json({
                success: false as const,
                error: 'Invalid request',
                code: 'VALIDATION_ERROR'
            }, 400);
        }

        // ... implementation ...

        return c.json({ success: true as const, data: response });
    };
}
```

## Wiring Routes

Register routes in `src/server/routes/index.ts`:

```typescript
import { loginHandler } from './auth/login';

export function registerRoutes(app: Hono, sessionManager: ISessionManager) {
    // Auth routes
    app.post('/login', loginHandler(sessionManager));

    // Add your new route here
}
```

## Response Format

All endpoints use a consistent envelope:

```typescript
// Success
return c.json({ success: true as const, data: result });

// Error
return c.json({
    success: false as const,
    error: 'Human-readable message',
    code: 'MACHINE_CODE'
}, statusCode);
```

Use `as const` for literal types in discriminated unions.

## Library Mode Mapping

If the endpoint wraps core functionality, add a method to `ADTClient`:

| HTTP Endpoint | Library Method |
|--------------|----------------|
| `POST /login` | `client.login()` |
| `GET /packages` | `client.getPackages()` |
| `POST /objects/read` | `client.read(objects)` |

## Documentation Requirements

Create endpoint docs in `docs/endpoints/{category}.md`.

**Required structure:**

1. Title and description
2. `## Sections` TOC with anchor links
3. Per-endpoint:
   - Description paragraph
   - Request table (Method, Path, Auth Required)
   - Request Body table (Field, Type, Required, Description)
   - Response table (Field, Type, Description)
   - Example request/response JSON
   - Error codes table
   - Use cases list
   - Library Usage section

See `docs/endpoints/auth.md` for a complete example.

## Checklist

```
- [ ] Create route file in src/server/routes/{category}/
- [ ] Add Zod schema for request validation
- [ ] Add response type interface
- [ ] Export handler function (factory pattern)
- [ ] Wire route in src/server/routes/index.ts
- [ ] Add library method to ADTClient if applicable
- [ ] Document in docs/endpoints/{category}.md
- [ ] Run typecheck: bun run typecheck
```
