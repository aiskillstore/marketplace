# AI Handler Reference

## Dependencies
- `replicate`
- `inngest` (for background processing)
- `src/lib/s3/uploadFromServer` (for persistence)

## Database Schema (Example)
```typescript
// src/db/schema/generations.ts
export const generations = pgTable("generations", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  userId: text("userId").notNull(),
  prompt: text("prompt"),
  status: text("status").default("pending"), // pending, processing, completed, failed
  url: text("url"), // S3 URL
  createdAt: timestamp("createdAt").defaultNow(),
});
```

## Replicate Polling Pattern
Use `step.sleep` loops for simple polling of long-running predictions.

```typescript
while (status !== "succeeded" && status !== "failed") {
  await step.sleep("poll", "2s");
  status = await checkStatus();
}
```
