# Inngest Reference

## File Structure
-   **Client**: `src/lib/inngest/client.ts`
-   **Registry**: `src/lib/inngest/functions/index.ts`
-   **Definitions**: `src/lib/inngest/functions/[domain]/[action].ts`

## Code Snippets

### Basic Step
```typescript
const result = await step.run("step-id", async () => {
  return await db.query();
});
```

### Sleep (Delay)
```typescript
// Wait for time
await step.sleep("wait-10m", "10m");

// Wait until date
await step.sleepUntil("wait-for-launch", new Date("2025-01-01"));
```

### Wait For Event
```typescript
const event = await step.waitForEvent("wait-approval", {
  event: "app/approval.received",
  match: "data.proposalId", // Correlate events
  timeout: "3d",
  ifExpression: "event.data.approved == true" // Optional condition
});
```

### Send Event
```typescript
await step.sendEvent("broadcast", [
  { name: "user.notify", data: { msg: "Hello" } },
  { name: "analytics.track", data: { event: "ping" } }
]);
```

### Invoke Other Function
```typescript
const result = await step.invoke("call-worker", {
  function: require("./worker").workerFn,
  data: { jobId: 123 }
});
```

### Config Object
```typescript
{
  id: "function-id",
  concurrency: { limit: 5, key: "event.data.accountId" },
  rateLimit: { limit: 100, period: "1h" },
  debounce: { period: "1m", key: "event.data.id" },
  priority: { run: "event.data.isVip ? 100 : 0" },
  retries: 3, // 0 to disable
  cancelOn: [{ event: "app/process.cancel", match: "data.id" }],
  onFailure: async ({ error, step }) => { ... }
}
```

### Error Handling
```typescript
import { NonRetriableError } from "inngest";

// Stop retrying immediately
throw new NonRetriableError("Config missing");

// Retry logic is automatic for standard Errors
throw new Error("API unavailable"); // Will retry
```
