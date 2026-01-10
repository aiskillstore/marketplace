---
name: redis-patterns
description: Upstash Redis patterns for caching and rate limiting.
---

# Upstash Redis Patterns

## Setup

```typescript
// lib/redis.ts
import { Redis } from '@upstash/redis';

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});
```

## Basic Caching

```typescript
// Cache with TTL
async function getCachedUser(id: string): Promise<User | null> {
  const cacheKey = `user:${id}`;

  // Try cache first
  const cached = await redis.get<User>(cacheKey);
  if (cached) return cached;

  // Fetch from DB
  const user = await db.query.users.findFirst({
    where: eq(users.id, id),
  });

  if (user) {
    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, user);
  }

  return user;
}
```

## Cache Invalidation

```typescript
// Invalidate on update
async function updateUser(id: string, data: UpdateUserInput): Promise<User> {
  const user = await db.update(users)
    .set(data)
    .where(eq(users.id, id))
    .returning();

  // Invalidate cache
  await redis.del(`user:${id}`);

  // Also invalidate list caches
  await redis.del('users:list');

  return user[0];
}
```

## Rate Limiting

```typescript
import { Ratelimit } from '@upstash/ratelimit';

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
  analytics: true,
});

// In API route or middleware
export async function POST(request: Request) {
  const ip = request.headers.get('x-forwarded-for') ?? 'anonymous';
  const { success, limit, reset, remaining } = await ratelimit.limit(ip);

  if (!success) {
    return new Response('Too Many Requests', {
      status: 429,
      headers: {
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
        'X-RateLimit-Reset': reset.toString(),
      },
    });
  }

  // Process request...
}
```

## Session Storage

```typescript
interface Session {
  userId: string;
  expiresAt: number;
}

async function createSession(userId: string): Promise<string> {
  const sessionId = crypto.randomUUID();
  const session: Session = {
    userId,
    expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 days
  };

  await redis.setex(`session:${sessionId}`, 7 * 24 * 60 * 60, session);
  return sessionId;
}

async function getSession(sessionId: string): Promise<Session | null> {
  return await redis.get<Session>(`session:${sessionId}`);
}

async function deleteSession(sessionId: string): Promise<void> {
  await redis.del(`session:${sessionId}`);
}
```

## Pub/Sub for Real-time

```typescript
// Publisher
async function publishEvent(channel: string, data: unknown): Promise<void> {
  await redis.publish(channel, JSON.stringify(data));
}

// Usage
await publishEvent('user:updates', { userId: '123', action: 'updated' });
```

## Leaderboard

```typescript
// Add score
await redis.zadd('leaderboard', { score: 100, member: 'user:123' });

// Get top 10
const topUsers = await redis.zrevrange('leaderboard', 0, 9, { withScores: true });

// Get user rank
const rank = await redis.zrevrank('leaderboard', 'user:123');
```

## Cache Patterns

```typescript
// Cache-aside pattern
async function getData<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 300
): Promise<T> {
  const cached = await redis.get<T>(key);
  if (cached) return cached;

  const data = await fetcher();
  await redis.setex(key, ttl, data);
  return data;
}

// Usage
const user = await getData(
  `user:${id}`,
  () => db.query.users.findFirst({ where: eq(users.id, id) }),
  300
);
```
