/**
 * Neon PostgreSQL Connection Template
 *
 * Usage:
 * 1. Copy this file to src/db/index.ts
 * 2. Set DATABASE_URL in .env
 * 3. Choose the appropriate connection method
 */

// === OPTION 1: HTTP (Serverless - Recommended) ===
// Best for: Edge functions, serverless, one-shot queries

import { neon } from "@neondatabase/serverless";

export const sql = neon(process.env.DATABASE_URL!, {
  fetchOptions: {
    // Increase timeout for cold starts
    signal: AbortSignal.timeout(10000),
  },
});

// Usage:
// const users = await sql`SELECT * FROM users`;
// const user = await sql`SELECT * FROM users WHERE id = ${userId}`;


// === OPTION 2: WebSocket Pool ===
// Best for: Transactions, long-running connections

// import { Pool } from "@neondatabase/serverless";
//
// export const pool = new Pool({
//   connectionString: process.env.DATABASE_URL,
//   max: 10,
// });
//
// Usage:
// const { rows } = await pool.query("SELECT * FROM users");


// === OPTION 3: Drizzle ORM + Neon HTTP ===
// Best for: Type-safe queries with Drizzle

// import { neon } from "@neondatabase/serverless";
// import { drizzle } from "drizzle-orm/neon-http";
// import * as schema from "./schema";
//
// const sql = neon(process.env.DATABASE_URL!);
// export const db = drizzle(sql, { schema });
//
// Usage:
// const users = await db.select().from(schema.users);


// === OPTION 4: Drizzle ORM + Neon WebSocket ===
// Best for: Drizzle with transactions

// import { Pool } from "@neondatabase/serverless";
// import { drizzle } from "drizzle-orm/neon-serverless";
// import * as schema from "./schema";
//
// const pool = new Pool({ connectionString: process.env.DATABASE_URL });
// export const db = drizzle(pool, { schema });
//
// Usage:
// await db.transaction(async (tx) => {
//   await tx.insert(schema.users).values({ email: "user@example.com" });
// });
