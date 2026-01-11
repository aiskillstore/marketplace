# Testing Anti-Patterns

**Load this reference when:** Writing tests involving mocks, test doubles, or test utilities.

## Contents

- Anti-Pattern 1: Testing Mock Behavior
- Anti-Pattern 2: Test-Only Methods in Production
- Anti-Pattern 3: Mocking Without Understanding
- Anti-Pattern 4: Incomplete Mocks
- Anti-Pattern 5: Over-Specifying Interaction Order
- Quick Reference

## Anti-Pattern 1: Testing Mock Behavior

**Bad:**
```typescript
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**Problem:** Verifies the mock exists, not that the component works. Test passes when mock is present, fails when it's not. Tells you nothing about real behavior.

**Fix:** Test real component or don't mock it:
```typescript
test('renders sidebar', () => {
  render(<Page />);  // Don't mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

**Query priority:** Prefer `getByRole`, `getByLabelText`, `getByText` (user-facing). Use `getByTestId` as escape hatch when:
- Role/label unavailable or ambiguous
- Performance critical (large DOM, `getByRole` is expensive)
- Third-party component with no accessible selectors

`data-testid` is acceptable, not ideal. Never assert on `*-mock` test IDs.

**Gate:** Before asserting on any mock element, ask: "Am I testing real behavior or mock existence?" If mock existence, delete the assertion or unmock the component.

## Anti-Pattern 2: Test-Only Methods in Production

**Bad:**
```typescript
class Session {
  async destroy() {  // Only used in tests!
    await this._workspaceManager?.destroyWorkspace(this.id);
  }
}

// In tests
afterEach(() => session.destroy());
```

**Problem:** Production class polluted with test-only code. Dangerous if accidentally called in production. Violates separation of concerns.

**Distinction:** If the class genuinely owns a resource (file handle, connection, stream), `dispose()/close()` is legitimate API—it's real lifecycle management, not test pollution.

**Gate:** Ask: "Is this lifecycle method part of real domain/resource ownership, or exclusively for test convenience?"
- `DatabaseConnection.close()` → Real resource ownership, legitimate
- `Session.destroy()` that only tests call → Test pollution, move to test utilities

**Fix for test-only cleanup:**
```typescript
// In test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// In tests
afterEach(() => cleanupSession(session));
```

## Anti-Pattern 3: Mocking Without Understanding

**Bad:**
```typescript
test('detects duplicate server', () => {
  // Mock prevents config write that test depends on!
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // Should throw - but won't!
});
```

**Problem:** Mocked method had a side effect (writing config) the test depended on. Over-mocking "to be safe" breaks actual behavior.

**Fix:** Mock at the correct level:
```typescript
test('detects duplicate server', () => {
  vi.mock('MCPServerManager'); // Just mock slow server startup

  await addServer(config);  // Config written
  await addServer(config);  // Duplicate detected ✓
});
```

**Gate:** Before mocking any method:
1. What side effects does the real method have?
2. Does this test depend on any of those side effects?
3. If yes, mock at lower level (the actual slow/external operation)

Red flags: "I'll mock this to be safe", "This might be slow, better mock it", mocking without understanding the dependency chain.

## Anti-Pattern 4: Incomplete Mocks

**Bad:**
```typescript
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // Missing: metadata that downstream code uses
};
// Later: breaks when code accesses response.metadata.requestId
```

**Problem:** Partial mocks hide structural assumptions. Downstream code depends on fields you didn't include. Tests pass but integration fails.

**Fix:** Mirror real API structure completely:
```typescript
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
};
```

**Better fix:** Use recorded fixtures from real responses:
- Capture actual API responses during integration tests
- Store as JSON fixtures (`__fixtures__/api/user-response.json`)
- Import in unit tests
- Update fixtures when API schema changes

This prevents schema drift—manual mocks become stale as APIs evolve.

**Gate:** Before creating mock responses, check what fields the real API returns. Include ALL fields the system might consume downstream.

## Anti-Pattern 5: Over-Specifying Interaction Order

**Bad:**
```typescript
test('processes order', async () => {
  await processOrder(order);
  
  expect(validateInventory).toHaveBeenCalledBefore(chargePayment);
  expect(chargePayment).toHaveBeenCalledBefore(sendConfirmation);
  expect(sendConfirmation).toHaveBeenCalledWith(order.email);
});
```

**Problem:** Test asserts exact call sequence when only the final observable matters. Any refactor (parallel execution, reordering for perf, extracting helpers) breaks the test even if behavior is correct.

**Fix:** Assert on observable outcomes, not internal choreography:
```typescript
test('processes order', async () => {
  const result = await processOrder(order);
  
  expect(result.status).toBe('confirmed');
  expect(result.confirmationSent).toBe(true);
  expect(inventory.get(order.itemId).quantity).toBe(originalQty - 1);
});
```

**Gate:** Before asserting call order/sequence, ask: "Does the order actually matter to correctness, or just to my current implementation?" If only implementation, assert outcome instead.

**When order DOES matter:** Payment before shipping, auth before data access. In these cases, the sequence IS the requirement—assert it explicitly and document why.

## Quick Reference

| Anti-Pattern | Fix |
|--------------|-----|
| Assert on mock elements | Test real component or unmock it |
| Test-only methods in production | Move to test utilities (unless real resource ownership) |
| Mock without understanding | Understand dependencies first, mock minimally |
| Incomplete mocks | Use recorded fixtures from real responses |
| Over-specifying call order | Assert observable outcomes, not internal choreography |
| Over-complex mocks | Consider integration tests instead |

## Red Flags

- Assertion checks for `*-mock` test IDs
- Methods only called in test files
- Mock setup is >50% of test code
- Test fails when you remove a mock
- Can't explain why mock is needed
- Mocking "just to be safe"
