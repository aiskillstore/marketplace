/**
 * Database Performance Optimization Patterns
 */

import { Pool } from 'pg';

// =============================================
// CONNECTION POOLING
// =============================================

export const pool = new Pool({
  max: 20,                       // Maximum connections
  min: 5,                        // Minimum connections
  idleTimeoutMillis: 30000,      // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Fail fast if can't connect
  maxUses: 7500,                 // Close connection after N uses
});

// =============================================
// N+1 QUERY FIXES
// =============================================

// BAD: N+1 queries - executes N additional queries
async function getUsersWithOrdersBad(db: any) {
  const users = await db.user.findMany();
  for (const user of users) {
    const orders = await db.order.findMany({ where: { userId: user.id } });
    // This executes N additional queries!
  }
}

// GOOD: Single query with join
async function getUsersWithOrdersGood(db: any) {
  const usersWithOrders = await db.user.findMany({
    include: { orders: true }
  });
  return usersWithOrders;
}

// =============================================
// PAGINATION
// =============================================

// BAD: Loading all records
async function getAllUsersBad(db: any) {
  return await db.user.findMany();
}

// GOOD: Cursor-based pagination
async function getUsersPaginated(db: any, lastUserId?: string) {
  return await db.user.findMany({
    take: 20,
    cursor: lastUserId ? { id: lastUserId } : undefined,
    orderBy: { id: 'asc' }
  });
}

// =============================================
// SQL OPTIMIZATION PATTERNS
// =============================================

/*
-- Find slow queries (PostgreSQL)
SELECT
  query,
  calls,
  total_time / 1000 as total_seconds,
  mean_time / 1000 as mean_seconds,
  rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;

-- Add missing index
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);

-- Verify improvement
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
-- Should show "Index Scan" instead of "Seq Scan"

-- BAD: Subquery in SELECT
SELECT
  u.*,
  (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count
FROM users u;

-- GOOD: Use JOIN with GROUP BY
SELECT
  u.*,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
*/
