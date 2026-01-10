---
name: Database & ORM
description: Interaction with NeonDB Postgres using Drizzle ORM.
---

# Database Logic

## Stack
- **Database**: Neon (Serverless Postgres)
- **ORM**: Drizzle ORM
- **Driver**: `@neondatabase/serverless`

## Connection
The database connection is initialized in `db/index.ts`.

```ts
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);
```

## Schema
Schema definitions are in `db/schema.ts`.
- `users`, `sessions`, `accounts`, `verifications`: Auth tables.
- `analyses`, `chatbot_history`: App specific tables.

## Operations
Example of a database query:

```ts
import { db } from "@/db";
import { users } from "@/db/schema";
import { eq } from "drizzle-orm";

// Select
const user = await db.select().from(users).where(eq(users.email, "test@example.com"));

// Insert
await db.insert(users).values({ ... });
```

## Migrations
- Generate: `npx drizzle-kit generate`
- Push: `npx drizzle-kit push` (or migrate script)
