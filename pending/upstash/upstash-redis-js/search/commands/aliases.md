# Aliases

## Overview

Index aliases provide an indirection layer between your application and the actual index. You can point an alias to any index and swap it atomically, enabling zero-downtime reindexing.

## Good For

- Zero-downtime index rebuilds (blue/green reindexing)
- A/B testing different index configurations
- Versioned index management

## Examples

### Add an Alias

```typescript
import { Redis, s } from "@upstash/redis";

const redis = Redis.fromEnv();

// Create an index
const index = await redis.search.createIndex({
  name: "products-v1",
  prefix: "product:",
  dataType: "json",
  schema: s.object({ name: s.string(), price: s.number("F64") }),
});

// Add alias via the index instance
await index.addAlias({ alias: "products" });

// Or via the redis.search.alias API
await redis.search.alias.add({ indexName: "products-v1", alias: "products" });
```

### List All Aliases

```typescript
const aliases = await redis.search.alias.list();
// { "products": "products-v1", "users": "users-v2" }
```

### Delete an Alias

```typescript
await redis.search.alias.delete({ alias: "products" });
// Returns 1 if deleted, 0 if alias didn't exist
```

### Zero-Downtime Reindexing

```typescript
// 1. Resolve the alias's current target before swapping
const aliases = await redis.search.alias.list();
const oldIndexName = aliases["products"]; // "products-v1"

// 2. Create new index with updated schema
const newIndex = await redis.search.createIndex({
  name: "products-v2",
  prefix: "product:",
  dataType: "json",
  schema: s.object({
    name: s.string(),
    price: s.number("F64"),
    description: s.string(), // new field
  }),
});

// 3. Wait for new index to finish scanning existing keys
await newIndex.waitIndexing();

// 4. Atomically swap the alias to the new index
// (addAlias updates the alias if it already exists)
await redis.search.alias.add({ indexName: "products-v2", alias: "products" });

// 5. Drop the old index by name
const oldIndex = redis.search.index({ name: oldIndexName });
await oldIndex.drop();
```

After step 4 the alias resolves to `products-v2`, so dropping by the alias name would drop the new index — resolve it before the swap.
