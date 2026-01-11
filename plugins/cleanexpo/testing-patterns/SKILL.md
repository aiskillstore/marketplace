---
name: testing-patterns
description: ```typescript
---

# Testing Patterns Skill
## Vitest Testing Strategy

**When to Use**: Writing tests for new features, agents, API routes

---

## Framework: Vitest

**Command**: `npm run test`
**Required**: 100% pass rate
**Location**: `tests/` directory

---

## Unit Test Pattern

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MyService } from '@/lib/services/my-service';

describe('MyService', () => {
  let service: MyService;

  beforeEach(() => {
    vi.clearAllMocks();
    service = new MyService();
  });

  it('should process data correctly', () => {
    const input = { value: 42 };
    const result = service.process(input);

    expect(result).toBeDefined();
    expect(result.value).toBe(42);
  });

  it('should handle errors', () => {
    expect(() => service.process(null)).toThrow();
  });
});
```

---

## Agent Test Pattern

```typescript
import { describe, it, expect, vi } from 'vitest';
import { MyAgent } from '@/lib/agents/my-agent';

// Mock Supabase
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      select: vi.fn().mockReturnThis(),
      eq: vi.fn().mockResolvedValue({ data: [], error: null })
    }))
  }))
}));

describe('MyAgent', () => {
  it('processes task successfully', async () => {
    const agent = new MyAgent();
    const task = {
      id: 'test-1',
      workspace_id: 'ws-123',
      task_type: 'test',
      payload: {},
      priority: 5,
      retry_count: 0,
      max_retries: 3
    };

    const result = await agent.processTask(task);

    expect(result).toBeDefined();
  });
});
```

---

## API Test Pattern

```typescript
import { describe, it, expect } from 'vitest';
import { GET } from '@/app/api/my-endpoint/route';
import { NextRequest } from 'next/server';

describe('GET /api/my-endpoint', () => {
  it('requires workspace_id', async () => {
    const req = new NextRequest('http://localhost:3008/api/my-endpoint');

    const response = await GET(req);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain('workspaceId required');
  });
});
```

---

## Mocking Supabase

```typescript
const mockSelect = vi.fn().mockReturnThis();
const mockEq = vi.fn().mockReturnThis();
const mockInsert = vi.fn().mockReturnThis();
const mockFrom = vi.fn(() => ({
  select: mockSelect,
  eq: mockEq,
  insert: mockInsert
}));

vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    from: mockFrom
  }))
}));

// Set return values
mockEq.mockResolvedValue({ data: [{ id: '1', name: 'Test' }], error: null });
```

---

## Coverage Requirements

- **Unit Tests**: All services, utilities, helpers
- **Integration Tests**: API routes, agent workflows
- **E2E Tests**: Critical user flows (Playwright)

**Target**: 100% pass rate (no failures allowed)

---

**Standard**: All code must have tests, all tests must pass
