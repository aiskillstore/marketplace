# Testing Patterns for ChatGPT Apps

Strategies for testing MCP servers, tools, and widgets effectively.

---

## Test Pyramid for ChatGPT Apps

```
                    ┌─────────┐
                    │   E2E   │  ← Full workflow tests in ChatGPT
                   ┌┴─────────┴┐
                   │Integration│  ← Tool handlers with real database
                  ┌┴───────────┴┐
                  │    Unit     │  ← Pure functions, utilities
                  └─────────────┘
```

**Recommended distribution**:
- 60% Unit tests (fast, isolated)
- 30% Integration tests (tool handlers with database)
- 10% E2E tests (manual golden prompt testing in ChatGPT)

---

## Test Framework Setup (Vitest)

Vitest works well with TypeScript and ESM modules:

### vitest.config.ts
```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["tests/**/*.test.ts"],
    setupFiles: ["tests/setup.ts"],
    testTimeout: 30000,  // Longer timeout for database tests
    hookTimeout: 30000,
  },
});
```

### tests/setup.ts
```typescript
import { beforeAll, afterAll } from "vitest";
import dotenv from "dotenv";

// Load test environment variables
dotenv.config({ path: ".env.test" });

// Global setup
beforeAll(async () => {
  // Initialize database connection, etc.
});

// Global teardown
afterAll(async () => {
  // Clean up connections
});
```

### package.json scripts
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration"
  }
}
```

---

## Unit Testing Utilities

Test pure functions in isolation:

### tests/unit/formatting.test.ts
```typescript
import { describe, it, expect } from "vitest";
import { formatCurrency, formatDate, formatRelativeTime } from "../../src/lib/formatting";

describe("formatCurrency", () => {
  it("formats positive amounts", () => {
    expect(formatCurrency(1000)).toBe("$1,000");
    expect(formatCurrency(1234.56)).toBe("$1,234.56");
  });

  it("handles zero", () => {
    expect(formatCurrency(0)).toBe("$0");
  });

  it("handles null/undefined", () => {
    expect(formatCurrency(null)).toBe("-");
    expect(formatCurrency(undefined)).toBe("-");
  });
});

describe("formatDate", () => {
  it("formats ISO dates", () => {
    expect(formatDate("2024-01-15")).toBe("Jan 15, 2024");
  });

  it("handles invalid dates", () => {
    expect(formatDate("invalid")).toBe("-");
  });
});
```

---

## Integration Testing Tool Handlers

Test tool handlers with real database:

### tests/helpers/test-db.ts
```typescript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

// Generate unique test user ID per test run
export function createTestUserId(): string {
  return `test-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

// Clean up all data for a test user
export async function cleanupTestUser(userId: string): Promise<void> {
  // Delete in correct order (foreign key constraints)
  await supabase.from("activities").delete().eq("user_id", userId);
  await supabase.from("items").delete().eq("user_id", userId);
  await supabase.from("users").delete().eq("id", userId);
}

// Create test user with sample data
export async function createTestUserWithData(userId: string): Promise<void> {
  await supabase.from("users").insert({ id: userId, email: "test@example.com" });
  await supabase.from("items").insert([
    { user_id: userId, title: "Test Item 1", status: "active" },
    { user_id: userId, title: "Test Item 2", status: "completed" },
  ]);
}
```

### tests/integration/tools/get-items.test.ts
```typescript
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { handleGetItems } from "../../../src/tools/get-items";
import { createTestUserId, cleanupTestUser, createTestUserWithData } from "../../helpers/test-db";

describe("handleGetItems", () => {
  let testUserId: string;

  beforeEach(async () => {
    testUserId = createTestUserId();
    await createTestUserWithData(testUserId);
  });

  afterEach(async () => {
    await cleanupTestUser(testUserId);
  });

  it("returns all items for user", async () => {
    const result = await handleGetItems({ status: "all" }, testUserId);

    expect(result.content[0].text).toContain("Found 2");
    expect(result.structuredContent.items).toHaveLength(2);
  });

  it("filters by status", async () => {
    const result = await handleGetItems({ status: "active" }, testUserId);

    expect(result.structuredContent.items).toHaveLength(1);
    expect(result.structuredContent.items[0].title).toBe("Test Item 1");
  });

  it("respects limit", async () => {
    const result = await handleGetItems({ limit: 1 }, testUserId);

    expect(result.structuredContent.items).toHaveLength(1);
    expect(result.structuredContent.hasMore).toBe(true);
  });

  it("returns empty for user with no items", async () => {
    const emptyUserId = createTestUserId();

    const result = await handleGetItems({}, emptyUserId);

    expect(result.content[0].text).toContain("No items");
    expect(result.structuredContent.items).toHaveLength(0);
  });
});
```

---

## Mocking External Dependencies

### Mock OpenAI embeddings
```typescript
// tests/mocks/openai.ts
import { vi } from "vitest";

export const mockEmbeddings = vi.fn().mockResolvedValue({
  data: [{ embedding: new Array(1536).fill(0.1) }],
});

// In tests/setup.ts
vi.mock("openai", () => ({
  default: class MockOpenAI {
    embeddings = {
      create: mockEmbeddings,
    };
  },
}));
```

### Mock external API
```typescript
// tests/mocks/api-client.ts
import { vi } from "vitest";

export const mockApiClient = {
  getProfile: vi.fn(),
  createItem: vi.fn(),
};

// In test file
import { mockApiClient } from "../mocks/api-client";

vi.mock("../../src/lib/api-client", () => ({
  apiClient: mockApiClient,
}));

describe("handleGetProfile", () => {
  it("returns profile data", async () => {
    mockApiClient.getProfile.mockResolvedValue({
      name: "Test User",
      email: "test@example.com",
    });

    const result = await handleGetProfile({ id: "123" });

    expect(result.structuredContent.name).toBe("Test User");
  });
});
```

---

## E2E Testing with Golden Prompts

### tests/e2e/golden-prompts.test.ts
```typescript
import { describe, it, expect } from "vitest";

// These are manual tests - document expected behavior
describe("Golden Prompts (Manual E2E)", () => {
  describe("Direct prompts (should trigger)", () => {
    it.todo("'Show my tasks' → triggers get_tasks");
    it.todo("'Create a task called Review PR' → triggers create_task");
    it.todo("'Mark the Review PR task as complete' → triggers complete_task");
  });

  describe("Indirect prompts (should trigger)", () => {
    it.todo("'What should I work on today?' → triggers get_tasks with status=active");
    it.todo("'Help me prioritize my work' → triggers get_tasks");
  });

  describe("Negative prompts (should NOT trigger)", () => {
    it.todo("'Create a reminder for tomorrow' → should NOT trigger our app");
    it.todo("'What time is it?' → should NOT trigger our app");
  });
});
```

### Golden Prompt Testing Workflow
1. Start local server: `npm run dev`
2. Create ngrok tunnel: `ngrok http 8000`
3. Add connector in ChatGPT with ngrok URL
4. Test each golden prompt manually
5. Document results in test file

---

## Test Database Isolation

### Pattern: Unique test user per suite
```typescript
describe("Item CRUD operations", () => {
  // Unique user ID ensures complete isolation
  const testUserId = `test-crud-${Date.now()}`;

  beforeAll(async () => {
    await createTestUser(testUserId);
  });

  afterAll(async () => {
    // Clean up ALL test data
    await cleanupTestUser(testUserId);
  });

  // Tests run in isolation...
});
```

### Pattern: Transaction rollback (if supported)
```typescript
import { beforeEach, afterEach } from "vitest";

let transaction: any;

beforeEach(async () => {
  transaction = await db.transaction();
});

afterEach(async () => {
  await transaction.rollback();  // Undo all changes
});
```

---

## Coverage Goals

| Category | Target | Notes |
|----------|--------|-------|
| Tool handlers | 90%+ | Critical path, test thoroughly |
| Utilities | 80%+ | Pure functions, easy to test |
| Server setup | 50%+ | Integration covers most paths |
| Widget code | Manual | Test in browser/ChatGPT |

### vitest.config.ts with coverage
```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.ts"],
      exclude: ["src/**/*.d.ts", "src/widget/**"],
    },
  },
});
```

---

## Test Structure Recommendation

```
tests/
├── setup.ts                     # Global setup, env loading, mocks
├── mocks/
│   ├── openai.ts               # Mock embeddings
│   └── api-client.ts           # Mock external APIs
├── helpers/
│   └── test-db.ts              # Database utilities
├── unit/
│   ├── formatting.test.ts      # Pure function tests
│   ├── validation.test.ts      # Schema validation tests
│   └── utils.test.ts           # Utility function tests
├── integration/
│   └── tools/
│       ├── get-items.test.ts   # Tool handler tests
│       ├── create-item.test.ts
│       └── update-item.test.ts
└── e2e/
    └── golden-prompts.test.ts  # Manual E2E documentation
```

---

## CI/CD Integration

### .github/workflows/test.yml
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    env:
      SUPABASE_URL: ${{ secrets.TEST_SUPABASE_URL }}
      SUPABASE_SERVICE_KEY: ${{ secrets.TEST_SUPABASE_KEY }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - run: npm ci

      - run: npm run build

      - run: npm run test:coverage

      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

---

## Debugging Test Failures

### Verbose logging
```typescript
it("handles edge case", async () => {
  const args = { status: "unknown" };
  console.log("Test input:", args);

  const result = await handleGetItems(args, testUserId);
  console.log("Test output:", JSON.stringify(result, null, 2));

  expect(result.structuredContent.error).toBe(true);
});
```

### Snapshot testing for responses
```typescript
it("returns consistent response structure", async () => {
  const result = await handleGetItems({}, testUserId);

  // First run creates snapshot, subsequent runs compare
  expect(result.structuredContent).toMatchSnapshot();
});
```
