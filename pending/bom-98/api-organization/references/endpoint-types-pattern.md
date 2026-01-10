# Endpoint Types Pattern

Structure for `endpoint-types.ts` - TypeScript type definitions for all API endpoints.

## File Organization

```typescript
/**
 * Type definitions for all API endpoints
 * Organized by domain/feature category
 */

// ==========================================
// COMMON TYPES (reusable across domains)
// ==========================================

export interface ApiErrorResponse {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  [key: string]: any;
}

// ==========================================
// DOMAIN - Response Types
// ==========================================

export interface EntityListItem {
  id: string;
  name: string;
  // ... list view fields
}

export interface EntityDetail {
  id: string;
  name: string;
  // ... full entity fields
}

// ==========================================
// REQUEST BODY DTOs
// ==========================================

export interface CreateEntityDto {
  name: string;
  // ... required creation fields
}

export interface UpdateEntityDto extends CreateEntityDto {
  // Optional: add update-specific fields
}

// ==========================================
// ENDPOINT PARAMETER TYPES
// ==========================================

export interface EndpointParams {
  domain: {
    list: { categoryId: string }; // Required params
    get: { id: string };
    create: void; // No params
    update: { id: string };
    delete: { id: string };
  };
}

// ==========================================
// ENDPOINT RESPONSE TYPES
// ==========================================

export interface EndpointResponses {
  domain: {
    list: EntityListItem[];
    get: EntityDetail;
    create: EntityDetail;
    update: EntityDetail;
    delete: void;
  };
}

// ==========================================
// ENDPOINT REQUEST BODY TYPES
// ==========================================

export interface EndpointBodies {
  domain: {
    create: CreateEntityDto;
    update: UpdateEntityDto;
  };
}

// ==========================================
// UTILITY TYPES
// ==========================================

export type ApiResponse<
  Category extends keyof EndpointResponses,
  Operation extends keyof EndpointResponses[Category]
> = EndpointResponses[Category][Operation];

export type ApiRequestBody<
  Category extends keyof EndpointBodies,
  Operation extends keyof EndpointBodies[Category]
> = EndpointBodies[Category][Operation];

export type ApiParams<
  Category extends keyof EndpointParams,
  Operation extends keyof EndpointParams[Category]
> = EndpointParams[Category][Operation];
```

## Naming Conventions

### Response Types
- **List items**: `{Entity}ListItem` - Lightweight for lists
- **Details**: `{Entity}Detail` or just `{Entity}` - Full object
- **Settings**: `{Entity}Settings` - Configuration objects

### DTOs (Data Transfer Objects)
- **Create**: `Create{Entity}Dto`
- **Update**: `Update{Entity}Dto`
- **Custom**: `{Action}{Entity}Dto` (e.g., `AddUserToGroupsDto`)

### Structure Interfaces
- **Params**: `EndpointParams[category][operation]`
- **Responses**: `EndpointResponses[category][operation]`
- **Bodies**: `EndpointBodies[category][operation]`

## Type Organization Rules

1. **Group by domain** - Keep related types together
2. **Common first** - Shared types at top
3. **Response before DTOs** - Data models before mutations
4. **Three interfaces** - Params, Responses, Bodies
5. **Utility last** - Helper types at bottom

## Examples

### Simple CRUD Domain

```typescript
// Responses
export interface Product {
  id: string;
  name: string;
  price: number;
  sku: string;
}

// DTOs
export interface CreateProductDto {
  name: string;
  price: number;
  sku: string;
}

export interface UpdateProductDto extends CreateProductDto {}

// Params
products: {
  list: void;
  get: { id: string };
  create: void;
  update: { id: string };
  delete: { id: string };
}

// Responses
products: {
  list: Product[];
  get: Product;
  create: Product;
  update: Product;
  delete: void;
}

// Bodies
products: {
  create: CreateProductDto;
  update: UpdateProductDto;
}
```

### Nested/Scoped Domain

```typescript
// Params for nested resources
categoryProducts: {
  list: { categoryId: string };
  create: { categoryId: string };
  get: { categoryId: string; productId: string };
  update: { categoryId: string; productId: string };
  delete: { categoryId: string; productId: string };
}
```

### Multiple Variations

```typescript
// When API has alternative endpoints
settings: {
  get: { instanceId: string };      // /instances/{id}/settings
  getAlt: void;                      // /settings (uses session)
  update: { instanceId: string };
  updateAlt: void;
}
```

## Common Patterns

### Pagination Params
```typescript
list: { page?: number; limit?: number; };
```

### Search/Filter Params
```typescript
search: { query: string; filters?: Record<string, any> };
```

### Batch Operations
```typescript
batchCreate: void;  // Body contains array
```

### Optional Fields in DTOs
```typescript
export interface UpdateUserDto {
  email?: string;
  firstName?: string;
  lastName?: string;
}
```

## Integration with Other Files

Types flow through the system:
1. Define in `endpoint-types.ts`
2. Reference in `endpoints.ts` (implicitly via params)
3. Import in `protected-endpoints.ts` for wrappers
4. Use in application code via `api.*` calls
