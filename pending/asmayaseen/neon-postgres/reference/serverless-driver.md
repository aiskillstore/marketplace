# Neon Serverless Driver Reference

## Overview

The `@neondatabase/serverless` package provides two connection methods:
- **HTTP (neon)**: Stateless, one-shot queries via HTTP
- **WebSocket (Pool)**: Persistent connections with pooling

## Installation

```bash
npm install @neondatabase/serverless
```

## HTTP Driver (neon)

### Basic Usage

```typescript
import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL!);

// Tagged template literal
const users = await sql`SELECT * FROM users`;

// With parameters (safe from SQL injection)
const user = await sql`SELECT * FROM users WHERE id = ${userId}`;
```

### Insert

```typescript
const newUser = await sql`
  INSERT INTO users (email, name)
  VALUES (${email}, ${name})
  RETURNING *
`;
```

### Update

```typescript
const updated = await sql`
  UPDATE users
  SET name = ${newName}
  WHERE id = ${userId}
  RETURNING *
`;
```

### Delete

```typescript
await sql`DELETE FROM users WHERE id = ${userId}`;
```

### Transactions (HTTP)

HTTP transactions use a special syntax:

```typescript
import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL!);

const results = await sql.transaction([
  sql`INSERT INTO users (email) VALUES (${email}) RETURNING id`,
  sql`INSERT INTO profiles (user_id) VALUES (LASTVAL())`,
]);
```

### Configuration Options

```typescript
const sql = neon(process.env.DATABASE_URL!, {
  // Fetch options
  fetchOptions: {
    // Timeout for cold starts
    signal: AbortSignal.timeout(10000),
  },

  // Array mode (returns arrays instead of objects)
  arrayMode: false,

  // Full results (includes row count, fields metadata)
  fullResults: false,
});
```

### Type Safety

```typescript
interface User {
  id: string;
  email: string;
  name: string;
}

const sql = neon(process.env.DATABASE_URL!);

// Type the result
const users = await sql<User[]>`SELECT * FROM users`;

// Single result
const [user] = await sql<User[]>`SELECT * FROM users WHERE id = ${userId}`;
```

## WebSocket Driver (Pool)

### Basic Usage

```typescript
import { Pool } from "@neondatabase/serverless";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Query
const { rows } = await pool.query("SELECT * FROM users");

// With parameters
const { rows: [user] } = await pool.query(
  "SELECT * FROM users WHERE id = $1",
  [userId]
);
```

### Transactions

```typescript
const client = await pool.connect();

try {
  await client.query("BEGIN");

  await client.query(
    "INSERT INTO users (email) VALUES ($1)",
    [email]
  );

  await client.query(
    "INSERT INTO profiles (user_id) VALUES (LASTVAL())"
  );

  await client.query("COMMIT");
} catch (e) {
  await client.query("ROLLBACK");
  throw e;
} finally {
  client.release();
}
```

### Pool Configuration

```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,

  // Maximum connections
  max: 10,

  // Connection timeout (ms)
  connectionTimeoutMillis: 10000,

  // Idle timeout (ms)
  idleTimeoutMillis: 30000,
});
```

## When to Use Each

| Scenario | Driver |
|----------|--------|
| Edge/Serverless functions | HTTP (neon) |
| Simple CRUD operations | HTTP (neon) |
| Transactions | WebSocket (Pool) |
| Connection pooling | WebSocket (Pool) |
| Long-running processes | WebSocket (Pool) |
| Next.js API routes | HTTP (neon) |
| Next.js Server Actions | HTTP (neon) |

## Error Handling

```typescript
import { neon, NeonDbError } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL!);

try {
  await sql`INSERT INTO users (email) VALUES (${email})`;
} catch (error) {
  if (error instanceof NeonDbError) {
    // PostgreSQL error codes
    switch (error.code) {
      case "23505": // unique_violation
        throw new Error("Email already exists");
      case "23503": // foreign_key_violation
        throw new Error("Referenced record not found");
      case "23502": // not_null_violation
        throw new Error("Required field missing");
      default:
        throw error;
    }
  }
  throw error;
}
```

## Common PostgreSQL Error Codes

| Code | Name | Description |
|------|------|-------------|
| 23505 | unique_violation | Duplicate key value |
| 23503 | foreign_key_violation | Foreign key constraint |
| 23502 | not_null_violation | NULL in non-null column |
| 23514 | check_violation | Check constraint failed |
| 42P01 | undefined_table | Table doesn't exist |
| 42703 | undefined_column | Column doesn't exist |

## Next.js Integration

### Server Component

```typescript
// app/users/page.tsx
import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL!);

export default async function UsersPage() {
  const users = await sql`SELECT * FROM users ORDER BY created_at DESC`;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Server Action

```typescript
// app/actions.ts
"use server";

import { neon } from "@neondatabase/serverless";
import { revalidatePath } from "next/cache";

const sql = neon(process.env.DATABASE_URL!);

export async function createUser(formData: FormData) {
  const email = formData.get("email") as string;
  const name = formData.get("name") as string;

  await sql`INSERT INTO users (email, name) VALUES (${email}, ${name})`;

  revalidatePath("/users");
}
```

### API Route

```typescript
// app/api/users/route.ts
import { neon } from "@neondatabase/serverless";
import { NextResponse } from "next/server";

const sql = neon(process.env.DATABASE_URL!);

export async function GET() {
  const users = await sql`SELECT * FROM users`;
  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const { email, name } = await request.json();

  const [user] = await sql`
    INSERT INTO users (email, name)
    VALUES (${email}, ${name})
    RETURNING *
  `;

  return NextResponse.json(user, { status: 201 });
}
```
