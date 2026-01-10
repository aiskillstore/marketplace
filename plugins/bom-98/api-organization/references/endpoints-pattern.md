# Endpoints Pattern

Structure for `endpoints.ts` - Centralized API endpoint URL definitions.

## File Structure

```typescript
/**
 * Centralized API Endpoints Configuration
 *
 * All API endpoint URLs defined in one place.
 * Organized by feature/domain for easy maintenance.
 */

// Base URLs from environment variables
const API_BASE = process.env.INSTANCE_API_URL || '';
const NEXT_API_BASE = ''; // Empty for relative Next.js routes

/**
 * API Endpoints organized by feature/domain
 */
export const API_ENDPOINTS = {
  // ==========================================
  // DOMAIN NAME (matches endpoint-types.ts)
  // ==========================================
  domain: {
    // GET /api/domains
    list: () => `${API_BASE}/api/domains`,

    // GET /api/domains/:id
    get: (id: string) => `${API_BASE}/api/domains/${id}`,

    // POST /api/domains
    create: () => `${API_BASE}/api/domains`,

    // PUT /api/domains/:id
    update: (id: string) => `${API_BASE}/api/domains/${id}`,

    // DELETE /api/domains/:id
    delete: (id: string) => `${API_BASE}/api/domains/${id}`,
  },

  // ==========================================
  // NESTED RESOURCES
  // ==========================================
  categoryProducts: {
    // GET /api/categories/:categoryId/products
    list: (categoryId: string) =>
      `${API_BASE}/api/categories/${categoryId}/products`,

    // POST /api/categories/:categoryId/products
    create: (categoryId: string) =>
      `${API_BASE}/api/categories/${categoryId}/products`,

    // GET /api/categories/:categoryId/products/:productId
    get: (categoryId: string, productId: string) =>
      `${API_BASE}/api/categories/${categoryId}/products/${productId}`,

    // PUT /api/categories/:categoryId/products/:productId
    update: (categoryId: string, productId: string) =>
      `${API_BASE}/api/categories/${categoryId}/products/${productId}`,
  },
};
```

## Organization Rules

### Domain Grouping
Match structure in `endpoint-types.ts`:
```typescript
// endpoint-types.ts has:
export interface EndpointParams {
  products: { ... }
}

// endpoints.ts must have:
export const API_ENDPOINTS = {
  products: { ... }
}
```

### Function Signatures
All endpoint functions:
- Accept parameters that appear in URL or query string
- Return complete URL string
- Use arrow function syntax

```typescript
// Path parameters
get: (id: string) => `${API_BASE}/api/items/${id}`

// Multiple path parameters
getVersion: (id: string, version: number) =>
  `${API_BASE}/api/items/${id}/versions/${version}`

// Query parameters (handled by client, not in URL builder)
// Don't include query params in these functions
```

### Base URL Selection

```typescript
// External API (environment variable)
const API_BASE = process.env.INSTANCE_API_URL || 'https://api.example.com';

// Next.js internal routes (relative paths)
const NEXT_API_BASE = '';

// Use in endpoints:
externalApi: {
  list: () => `${API_BASE}/api/resources`
},

internalApi: {
  list: () => `${NEXT_API_BASE}/api/internal/resources`
}
```

## Naming Conventions

### Operation Names
Match CRUD operations:
- `list` - GET collection
- `listAll` - GET all (no pagination)
- `get` - GET single item
- `create` - POST new item
- `update` - PUT/PATCH item
- `delete` - DELETE item
- `{action}` - Custom operation (e.g., `activate`, `archive`)

### Alternative Endpoints
Use suffix when multiple endpoints exist:
```typescript
settings: {
  get: (instanceId: string) => `${API_BASE}/api/settings/${instanceId}`,
  getAlt: () => `${API_BASE}/api/settings`, // Uses session context

  update: (instanceId: string) => `${API_BASE}/api/settings/${instanceId}`,
  updateGeneral: () => `${API_BASE}/api/settings`, // General endpoint
}
```

## Common Patterns

### Resource Collections
```typescript
users: {
  list: () => `${API_BASE}/api/users`,
  get: (id: string) => `${API_BASE}/api/users/${id}`,
  create: () => `${API_BASE}/api/users`,
  update: (id: string) => `${API_BASE}/api/users/${id}`,
  delete: (id: string) => `${API_BASE}/api/users/${id}`,
}
```

### Nested Resources
```typescript
posts: {
  comments: {
    list: (postId: string) => `${API_BASE}/api/posts/${postId}/comments`,
    create: (postId: string) => `${API_BASE}/api/posts/${postId}/comments`,
    get: (postId: string, commentId: string) =>
      `${API_BASE}/api/posts/${postId}/comments/${commentId}`,
  }
}
```

### Scoped Endpoints
```typescript
// Instance-scoped resources
instanceResources: {
  list: (instanceId: string) =>
    `${API_BASE}/api/instances/${instanceId}/resources`,
}

// User-scoped resources
userResources: {
  list: (userId: string) =>
    `${API_BASE}/api/users/${userId}/resources`,
}
```

### Action Endpoints
```typescript
users: {
  // CRUD operations
  get: (id: string) => `${API_BASE}/api/users/${id}`,

  // Custom actions
  activate: (id: string) => `${API_BASE}/api/users/${id}/activate`,
  deactivate: (id: string) => `${API_BASE}/api/users/${id}/deactivate`,
  resetPassword: (id: string) => `${API_BASE}/api/users/${id}/reset-password`,
}
```

### Legacy/Backward Compatible
```typescript
audience: {
  // New API
  list: (instanceId: string) => `${API_BASE}/api/instances/${instanceId}/audiences`,

  // Legacy API (keep for backward compatibility)
  getSavedAudiences: (instanceId: string) =>
    `${API_BASE}/api/instances/${instanceId}/qualificationgroups`,
}
```

## Environment Variables

Required in `.env.local`:
```bash
INSTANCE_API_URL=https://api.example.com
```

Access in endpoints.ts:
```typescript
const API_BASE = process.env.INSTANCE_API_URL || '';
```

## Integration Examples

### Usage in protected-endpoints.ts
```typescript
import { API_ENDPOINTS } from './endpoints';
import { apiGet } from './api-client';

export const api = {
  users: {
    async list() {
      return apiGet(API_ENDPOINTS.users.list());
    },
    async get(id: string) {
      return apiGet(API_ENDPOINTS.users.get(id));
    }
  }
};
```

### Usage in Server Actions
```typescript
'use server';

import { API_ENDPOINTS } from '@/lib/api/endpoints';
import { apiPost } from '@/lib/api/api-client';

export async function createUser(data: CreateUserDto) {
  return apiPost(
    API_ENDPOINTS.users.create(),
    data
  );
}
```

## Comments

Add comments for:
- Complex URL structures
- Backward compatibility notes
- Alternative endpoints
- Domain/feature sections

```typescript
/**
 * User Management Endpoints
 * Handles user CRUD, permissions, and authentication
 */
users: {
  // Standard CRUD
  list: () => `${API_BASE}/api/users`,

  // Note: This endpoint requires SuperAdmin role
  listAll: () => `${API_BASE}/api/admin/users/all`,
}
```
