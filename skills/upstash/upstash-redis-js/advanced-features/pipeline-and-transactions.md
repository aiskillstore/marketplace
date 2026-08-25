# Pipelines and Transactions

## Overview

**Pipelines** batch multiple commands for efficiency. **Transactions** (MULTI/EXEC) execute commands sequentially, with no other client's commands interleaved.

## Good For

- **Pipelines**: Reducing round trips for independent operations
- **Transactions**: Running a group of commands with no other client interleaving
- **Lua scripts (`redis.eval`)**: Atomic multi-step logic in one round trip — all-or-nothing writes, read-then-write

## Limitations

- Pipeline commands execute independently (no atomicity, no isolation)
- **Transactions do not roll back.** If a command fails at runtime (e.g. a WRONGTYPE error), the commands that already ran keep their effects and the rest still execute — the transaction can be left partially applied. Use a Lua script when you need all-or-nothing.
- No WATCH / optimistic locking over the REST client — use a Lua script (`redis.eval`) for atomic check-and-set

## Examples

```typescript
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv();

// Manual Pipeline - batch operations for efficiency
const pipeline = redis.pipeline();
pipeline.set("user:1:name", "Alice");
pipeline.set("user:1:email", "alice@example.com");
pipeline.incr("user:count");
pipeline.lpush("recent:users", "user:1");

const results = await pipeline.exec();
// Returns array of results: [OK, OK, 1, 1]

// Transaction (MULTI/EXEC) - no other client interleaves, but no rollback
const tx = redis.multi();
tx.decrby("inventory:item:1", 5); // Deduct inventory
tx.incrby("user:123:purchases", 5); // Add to user purchases
tx.lpush("orders", JSON.stringify({ userId: 123, itemId: 1, qty: 5 }));

const txResults = await tx.exec();
// If decrby fails, the incrby and lpush still apply
```

### Lua Scripts (`redis.eval`)

The whole script runs as one unit in a single round trip, so you can validate every precondition before the first write — and beyond all-or-nothing writes, branch, loop and use variables across multiple Redis calls.

```typescript
const script = `
  local stock = tonumber(redis.call("GET", KEYS[1]) or "0")
  local qty = tonumber(ARGV[1])
  if stock < qty then
    return -1
  end

  redis.call("DECRBY", KEYS[1], qty)
  redis.call("INCRBY", KEYS[2], qty)
  redis.call("LPUSH", KEYS[3], ARGV[2])
  return stock - qty
`;

const remaining = await redis.eval<number>(
  script,
  ["inventory:item:1", "user:123:purchases", "orders"],
  ["5", JSON.stringify({ userId: 123, itemId: 1, qty: 5 })]
);
// -1 means nothing was written
```
