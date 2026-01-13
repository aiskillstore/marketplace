---
name: api-endpoint-creation
description: Next.js 15+ API endpoint creation patterns with Supabase and workspace validation
---

# API Endpoint Creation Skill
## Next.js 15+ API Route Patterns

**When to Use**: Creating new API endpoints in src/app/api/

---

## Standard Pattern

```typescript
import { NextRequest } from 'next/server';
import { getSupabaseServer } from '@/lib/supabase';
import { validateUserAndWorkspace } from '@/lib/api-helpers';
import { successResponse, errorResponse } from '@/lib/api-helpers';
import { withErrorBoundary } from '@/lib/error-boundary';

export const GET = withErrorBoundary(async (req: NextRequest) => {
  // 1. Extract workspace_id from query params
  const workspaceId = req.nextUrl.searchParams.get("workspaceId");
  if (!workspaceId) {
    return errorResponse("workspaceId required", 400);
  }

  // 2. Validate user has access to workspace
  await validateUserAndWorkspace(req, workspaceId);

  // 3. Get Supabase client (server-side)
  const supabase = getSupabaseServer();

  // 4. Query with workspace_id filter (MANDATORY)
  const { data, error } = await supabase
    .from("your_table")
    .select("*")
    .eq("workspace_id", workspaceId);

  if (error) {
    return errorResponse(error.message, 500);
  }

  // 5. Return success response
  return successResponse(data);
});
```

---

## POST Endpoint Pattern

```typescript
export const POST = withErrorBoundary(async (req: NextRequest) => {
  const workspaceId = req.nextUrl.searchParams.get("workspaceId");
  if (!workspaceId) {
    return errorResponse("workspaceId required", 400);
  }

  const user = await validateUserAndWorkspace(req, workspaceId);
  const supabase = getSupabaseServer();

  // Parse request body
  const body = await req.json();
  const { name, data } = body;

  // Validation
  if (!name) {
    return errorResponse("name required", 400);
  }

  // Insert with workspace_id
  const { data: result, error } = await supabase
    .from("your_table")
    .insert({
      workspace_id: workspaceId,
      name,
      data,
      created_by: user.id
    })
    .select()
    .single();

  if (error) {
    return errorResponse(error.message, 500);
  }

  return successResponse(result, 201);
});
```

---

## Required Imports

```typescript
import { NextRequest } from 'next/server';
import { getSupabaseServer } from '@/lib/supabase';
import { validateUserAndWorkspace } from '@/lib/api-helpers';
import { successResponse, errorResponse } from '@/lib/api-helpers';
import { withErrorBoundary } from '@/lib/error-boundary';
```

---

## Checklist

- [ ] Use withErrorBoundary wrapper
- [ ] Validate workspace_id from query params
- [ ] Call validateUserAndWorkspace
- [ ] Use getSupabaseServer() for DB access
- [ ] Filter ALL queries by workspace_id
- [ ] Return successResponse or errorResponse
- [ ] Handle errors properly
- [ ] Add TypeScript types

---

**Standard**: Every API route MUST validate workspace and filter by workspace_id
