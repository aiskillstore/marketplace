/**
 * Caching Patterns for Performance
 */

import Redis from 'ioredis';

const redis = new Redis();

// =============================================
// CACHE-ASIDE PATTERN
// =============================================

interface User {
  id: string;
  name: string;
  email: string;
}

export async function getUserWithCache(
  userId: string,
  db: { user: { findUnique: (args: any) => Promise<User | null> } }
): Promise<User | null> {
  const cacheKey = `user:${userId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Cache miss - fetch from database
  const user = await db.user.findUnique({ where: { id: userId } });

  // Store in cache with TTL
  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour TTL
  }

  return user;
}

// Cache invalidation on update
export async function updateUser(
  userId: string,
  data: Partial<User>,
  db: { user: { update: (args: any) => Promise<User> } }
): Promise<User> {
  const user = await db.user.update({
    where: { id: userId },
    data
  });

  // Invalidate cache
  await redis.del(`user:${userId}`);

  return user;
}

// =============================================
// CACHE HIERARCHY
// =============================================

/*
L1: In-Memory Cache (fastest, smallest)
    - LRU cache in application
    - Per-request memoization

L2: Distributed Cache (fast, shared)
    - Redis/Memcached
    - Session storage

L3: CDN Cache (edge, static content)
    - Static assets
    - API responses (with care)

L4: Database Query Cache (optional)
    - Query result caching
    - Materialized views
*/

// =============================================
// MEMOIZATION PATTERN
// =============================================

export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  getKey: (...args: Parameters<T>) => string = (...args) => JSON.stringify(args)
): T {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>) => {
    const key = getKey(...args);
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}
