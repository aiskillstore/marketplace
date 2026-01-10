---
name: api-organization
description: Explains the standardized API organization pattern for this codebase. Use when creating new API endpoints, API clients, or modifying existing API structure. Covers the 5-file system (endpoint-types, endpoints, api-client, admin-api-client, protected-endpoints), role-based access patterns (admin vs regular users), and TypeScript type safety across the API layer. All API code lives in src/lib/api/ following this exact pattern.
---

# API Organization Pattern

This skill defines the standardized API organization pattern used throughout this codebase. All external API integrations follow the same 5-file structure for consistency, type safety, and maintainability.

## When to Use This Skill

Use this skill when:
- Creating new API endpoints or integrations
- Adding new API categories or domains
- Implementing role-based API access (admin vs regular users)
- Modifying existing API structure
- Setting up authentication for API calls
- Creating type-safe API wrappers

## Core Principles

1. **Single Source of Truth** - All API URLs defined once in `endpoints.ts`
2. **Type Safety** - Full TypeScript coverage from params to responses
3. **Role-Based Access** - Separate clients for regular vs admin endpoints
4. **Centralized Auth** - Authentication handled automatically by clients
5. **DRY Code** - Reusable client functions, no duplicate endpoint definitions

## The 5-File System

All API code lives in `src/lib/api/` with exactly these files:

```
src/lib/api/
├── endpoint-types.ts       # TypeScript types for all endpoints
├── endpoints.ts            # URL definitions organized by domain
├── api-client.ts           # Generic authenticated API client
├── admin-api-client.ts     # Admin-only API client with role checks
└── protected-endpoints.ts  # Type-safe wrapper functions
```

### File Purposes

**1. endpoint-types.ts**
- Define all TypeScript interfaces for API data
- Organize types by domain (e.g., audiences, instances, membership)
- Include param types, response types, and request body DTOs
- Provide utility types for extracting types

See `references/endpoint-types-pattern.md` for detailed structure.

**2. endpoints.ts**
- Define all API endpoint URLs in one place
- Organize by feature/domain matching types
- Use functions that accept parameters and return URLs
- Support environment variable base URLs

See `references/endpoints-pattern.md` for detailed structure.

**3. api-client.ts**
- Generic API client with automatic authentication
- Error parsing and handling
- Support for GET, POST, PUT, DELETE methods
- Server-side only ('use server')

See `references/api-client-pattern.md` for implementation.

**4. admin-api-client.ts**
- Admin-specific API client
- Role validation (Admin/SuperAdmin groups)
- Permission checking functions
- Throws AdminAuthError if unauthorized

See `references/admin-api-client-pattern.md` for implementation.

**5. protected-endpoints.ts**
- Type-safe wrapper functions combining URLs + types + clients
- Organized to match endpoint-types structure
- Provides clean import: `import { api } from '@/lib/api/protected-endpoints'`
- No 'use server' directive (exports objects)

See `references/protected-endpoints-pattern.md` for detailed structure.

## Authentication System

This application uses **Supabase Auth** for authentication. All API requests require authentication via Supabase access tokens.

### Supabase Client Structure
```
src/lib/supabase/
├── client.ts      # Browser-side Supabase client
├── server.ts      # Server-side Supabase client (RSC, Server Actions)
└── middleware.ts  # Middleware helper for auth cookie refresh
```

### Auth Flow
1. User authenticates via Supabase (email/password, OAuth, etc.)
2. Supabase stores session in httpOnly cookies
3. Middleware refreshes session on every request
4. Server components/actions use `createClient()` from `server.ts`
5. API client extracts access token from session automatically

See `references/supabase-auth-integration.md` for detailed implementation.

## Role-Based Access Pattern

### Regular User Endpoints
Use `api-client.ts` functions with automatic Supabase auth:
```typescript
import { apiGet, apiPost } from '@/lib/api/api-client';

// Access token extracted from Supabase session automatically
const data = await apiGet<ResponseType>(url);
```

### Admin-Only Endpoints
Use `admin-api-client.ts` functions with role validation:
```typescript
import { adminApiRequest, checkAdminPermission } from '@/lib/api/admin-api-client';

// Validate admin access first (checks user role from database)
await checkAdminPermission(); // Throws if not admin

// Make admin API request
const data = await adminApiRequest<ResponseType>(url, options);
```

### Admin Roles
Admin roles are stored in the `users` table:
- `users.role` = `'admin'` - Standard admin access
- `users.role` = `'member'` - Regular user access

First user in a family is automatically assigned admin role.

## Adding New API Endpoints

Follow this exact order when integrating a new API into the application:

### Step 1: Define Types in endpoint-types.ts

```typescript
// 1. Define response type(s)
export interface ResourceItem {
  id: string;
  name: string;
  // ... other fields from your API response
}

// 2. Define request DTO(s) for mutations
export interface CreateResourceDto {
  name: string;
  // ... fields required to create
}

// 3. Add parameter types to EndpointParams interface
export interface EndpointParams {
  // ... existing domains

  resources: {
    list: void;              // No params needed
    get: { id: string };     // Requires ID
    create: void;            // Body in request, not params
    update: { id: string };
    delete: { id: string };
  };
}

// 4. Add response types to EndpointResponses interface
export interface EndpointResponses {
  // ... existing domains

  resources: {
    list: ResourceItem[];
    get: ResourceItem;
    create: ResourceItem;
    update: ResourceItem;
    delete: void;
  };
}

// 5. Add request body types to EndpointBodies interface (if needed)
export interface EndpointBodies {
  // ... existing domains

  resources: {
    create: CreateResourceDto;
    update: CreateResourceDto;
  };
}
```

### Step 2: Define URLs in endpoints.ts

```typescript
export const API_ENDPOINTS = {
  // ... existing categories

  resources: {
    list: () => `${API_BASE}/api/resources`,
    get: (id: string) => `${API_BASE}/api/resources/${id}`,
    create: () => `${API_BASE}/api/resources`,
    update: (id: string) => `${API_BASE}/api/resources/${id}`,
    delete: (id: string) => `${API_BASE}/api/resources/${id}`,
  },
};
```

### Step 3: Add Wrapper in protected-endpoints.ts

```typescript
export const api = {
  // ... existing domains

  resources: {
    async list(): Promise<ResourceItem[]> {
      return apiGet<ResourceItem[]>(
        API_ENDPOINTS.resources.list()
      );
    },

    async get(id: string): Promise<ResourceItem> {
      return apiGet<ResourceItem>(
        API_ENDPOINTS.resources.get(id)
      );
    },

    async create(data: CreateResourceDto): Promise<ResourceItem> {
      return apiPost<ResourceItem, CreateResourceDto>(
        API_ENDPOINTS.resources.create(),
        data
      );
    },

    async update(id: string, data: CreateResourceDto): Promise<ResourceItem> {
      return apiPut<ResourceItem, CreateResourceDto>(
        API_ENDPOINTS.resources.update(id),
        data
      );
    },

    async delete(id: string): Promise<void> {
      return apiDelete<void>(
        API_ENDPOINTS.resources.delete(id)
      );
    },
  },
};
```

### Step 4: Use in Application Code

```typescript
'use server';

import { api } from '@/lib/api/protected-endpoints';

// In a server component or server action
const resources = await api.resources.list();
const resource = await api.resources.get(id);
const newResource = await api.resources.create({
  name: 'New Resource'
});
```

## Naming Conventions

### Endpoint Operations
- `list` / `listAll` - GET multiple items
- `get` - GET single item
- `create` - POST new item
- `update` - PUT/PATCH existing item
- `delete` - DELETE item

### Type Naming
- Response types: PascalCase describing entity (e.g., `AudienceListItem`)
- DTOs: PascalCase with suffix (e.g., `CreateUserDto`, `UpdateSettingsDto`)
- Interfaces match plural for collections, singular for items

## Error Handling

All API clients handle errors automatically:

```typescript
try {
  const data = await api.myFeature.get(id);
} catch (error) {
  // Error already parsed and formatted
  console.error('API error:', error.message);
}
```

Common error types:
- `AdminAuthError` - Admin permission denied
- `AdminApiError` - Admin API request failed
- Generic errors from `api-client` with parsed messages

## Authentication Flow

### Regular Endpoints
1. Client calls protected endpoint wrapper (e.g., `api.resources.list()`)
2. Wrapper calls apiGet/apiPost/etc from api-client
3. api-client calls `getAuthHeaders()`
4. getAuthHeaders uses Supabase server client to get session:
   ```typescript
   const supabase = await createClient();
   const { data: { session } } = await supabase.auth.getSession();
   const accessToken = session?.access_token;
   ```
5. Access token added to Authorization header
6. Request sent with automatic authentication

### Admin Endpoints
Same flow as above, but with additional role check:
1. Call `checkAdminPermission()` first
2. checkAdminPermission queries `users` table for current user's role
3. Throws `AdminAuthError` if role is not 'admin'
4. Then proceeds with normal authentication flow

## Best Practices

1. **Never hardcode URLs** - Always use `API_ENDPOINTS`
2. **Always define types first** - Types drive implementation
3. **One wrapper per endpoint** - Keep protected-endpoints clean
4. **Group by domain** - Match structure across all 5 files
5. **Use helper functions** - `apiGet`, `apiPost`, etc. handle auth
6. **Validate admin access early** - Call `checkAdminPermission()` first
7. **Document complex endpoints** - Add JSDoc comments
8. **Handle errors gracefully** - API clients provide good error messages

## Environment Variables

### Required for Supabase Auth
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Supabase anonymous public key

### Required for API Clients
- `INSTANCE_API_URL` or `API_URL` - Base URL for external API endpoints
- `NEXT_PUBLIC_SITE_URL` - Site URL for redirects (optional, defaults to localhost:3000)

### Database
- Supabase connection is handled automatically via the Supabase client
- No manual connection strings needed

## Migration from Other Patterns

If migrating existing API code to this pattern:

1. Extract all endpoint URLs to `endpoints.ts`
2. Create types in `endpoint-types.ts` for params/responses
3. Replace direct fetch calls with `apiGet`/`apiPost`/etc
4. Add wrappers to `protected-endpoints.ts`
5. Update imports to use `api` object

Example migration:
```typescript
// Before (scattered fetch calls)
const response = await fetch(`${API_BASE}/api/resources/${id}`, {
  headers: { Authorization: `Bearer ${token}` }
});
const resource = await response.json();

// After (centralized pattern)
import { api } from '@/lib/api/protected-endpoints';
const resource = await api.resources.get(id); // Auth automatic, types included
```

## References

See reference files for detailed implementation patterns:
- `references/supabase-auth-integration.md` - Supabase auth setup and integration
- `references/endpoint-types-pattern.md` - Type definition structure
- `references/endpoints-pattern.md` - URL organization pattern
- `references/api-client-pattern.md` - Generic client implementation with Supabase
- `references/admin-api-client-pattern.md` - Admin client with role-based access
- `references/protected-endpoints-pattern.md` - Wrapper function patterns
