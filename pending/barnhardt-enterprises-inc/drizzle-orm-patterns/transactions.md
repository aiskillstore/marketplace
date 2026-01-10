# Transaction Patterns

Comprehensive guide to database transactions with Drizzle ORM for data consistency and integrity.

## Table of Contents

- [What Are Transactions?](#what-are-transactions)
- [Basic Transactions](#basic-transactions)
- [Transaction Rollback](#transaction-rollback)
- [Nested Transactions (Savepoints)](#nested-transactions-savepoints)
- [Isolation Levels](#isolation-levels)
- [Error Handling](#error-handling)
- [Concurrent Transactions](#concurrent-transactions)
- [Deadlock Prevention](#deadlock-prevention)
- [Transaction Best Practices](#transaction-best-practices)

---

## What Are Transactions?

Transactions ensure **ACID** properties:
- **Atomicity**: All operations succeed or all fail
- **Consistency**: Database remains in valid state
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed changes persist

**When to use transactions:**
- Multiple related database operations
- Financial operations (payments, transfers)
- Operations that must succeed together
- Preventing race conditions
- Maintaining referential integrity

---

## Basic Transactions

### Simple Transaction

```typescript
import { db } from '@/lib/db';
import { users, profiles } from '@/lib/schema';

// All operations succeed or all fail
await db.transaction(async (tx) => {
  // Insert user
  const [user] = await tx
    .insert(users)
    .values({
      email: 'test@example.com',
      name: 'Test User',
    })
    .returning();

  // Insert profile (uses user.id)
  await tx.insert(profiles).values({
    userId: user.id,
    bio: 'Hello world',
  });

  // If either operation fails, both are rolled back
});
```

### Transaction with Return Value

```typescript
type CreateUserResult = {
  user: typeof users.$inferSelect;
  profile: typeof profiles.$inferSelect;
};

const result = await db.transaction(async (tx): Promise<CreateUserResult> => {
  const [user] = await tx
    .insert(users)
    .values({ email: 'test@example.com', name: 'Test User' })
    .returning();

  const [profile] = await tx
    .insert(profiles)
    .values({ userId: user.id, bio: 'Hello' })
    .returning();

  return { user, profile };
});

console.log(`Created user ${result.user.id} with profile ${result.profile.id}`);
```

### Transaction with Multiple Operations

```typescript
import { eq } from 'drizzle-orm';

// Complex multi-step operation
await db.transaction(async (tx) => {
  // 1. Create order
  const [order] = await tx
    .insert(orders)
    .values({
      userId: 123,
      total: 99.99,
      status: 'pending',
    })
    .returning();

  // 2. Create order items
  await tx.insert(orderItems).values([
    { orderId: order.id, productId: 1, quantity: 2, price: 29.99 },
    { orderId: order.id, productId: 2, quantity: 1, price: 40.01 },
  ]);

  // 3. Update product inventory
  await tx
    .update(products)
    .set({ stock: sql`${products.stock} - 2` })
    .where(eq(products.id, 1));

  await tx
    .update(products)
    .set({ stock: sql`${products.stock} - 1` })
    .where(eq(products.id, 2));

  // 4. Create payment record
  await tx.insert(payments).values({
    orderId: order.id,
    amount: 99.99,
    status: 'pending',
  });
});
```

---

## Transaction Rollback

### Automatic Rollback on Error

```typescript
try {
  await db.transaction(async (tx) => {
    // Insert user
    const [user] = await tx
      .insert(users)
      .values({ email: 'test@example.com', name: 'Test' })
      .returning();

    // This will throw if email already exists
    await tx.insert(users).values({
      email: 'test@example.com', // Duplicate!
      name: 'Another User',
    });

    // This code won't execute if previous insert fails
    await tx.insert(profiles).values({ userId: user.id, bio: 'Hi' });
  });
} catch (error) {
  // All changes rolled back automatically
  console.error('Transaction failed:', error);
}
```

### Manual Rollback

```typescript
class TransactionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TransactionError';
  }
}

await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({ email: 'test@example.com', name: 'Test' })
    .returning();

  // Check business logic
  const existingOrders = await tx
    .select()
    .from(orders)
    .where(eq(orders.userId, user.id));

  if (existingOrders.length > 0) {
    // Throw to trigger rollback
    throw new TransactionError('User already has orders');
  }

  // Continue if validation passes
  await tx.insert(profiles).values({ userId: user.id, bio: 'Hi' });
});
```

### Conditional Rollback

```typescript
await db.transaction(async (tx) => {
  // Deduct from account
  const [account] = await tx
    .update(accounts)
    .set({
      balance: sql`${accounts.balance} - 100`,
    })
    .where(eq(accounts.id, 1))
    .returning();

  // Check if balance would go negative
  if (account.balance < 0) {
    throw new Error('Insufficient funds');
  }

  // Record transaction
  await tx.insert(transactions).values({
    accountId: account.id,
    amount: -100,
    type: 'withdrawal',
  });
});
```

---

## Nested Transactions (Savepoints)

### Basic Savepoints

```typescript
await db.transaction(async (tx) => {
  // Outer transaction
  const [user] = await tx
    .insert(users)
    .values({ email: 'test@example.com', name: 'Test' })
    .returning();

  try {
    // Nested transaction (savepoint)
    await tx.transaction(async (nested) => {
      await nested.insert(profiles).values({
        userId: user.id,
        bio: 'This might fail',
      });

      // Simulate error
      throw new Error('Profile creation failed');
    });
  } catch (error) {
    // Profile insert rolled back, but user insert remains
    console.error('Nested transaction failed:', error);
  }

  // User still exists, continue with other operations
  await tx.insert(settings).values({
    userId: user.id,
    theme: 'dark',
  });
});
```

### Multiple Savepoints

```typescript
await db.transaction(async (tx) => {
  // Create user (always happens)
  const [user] = await tx
    .insert(users)
    .values({ email: 'test@example.com', name: 'Test' })
    .returning();

  // Try to create profile
  try {
    await tx.transaction(async (sp1) => {
      await sp1.insert(profiles).values({
        userId: user.id,
        bio: 'Optional profile',
      });
    });
  } catch (error) {
    console.log('Profile creation failed, continuing...');
  }

  // Try to send welcome email
  try {
    await tx.transaction(async (sp2) => {
      await sp2.insert(emails).values({
        userId: user.id,
        subject: 'Welcome!',
        sent: true,
      });
    });
  } catch (error) {
    console.log('Email sending failed, continuing...');
  }

  // User creation succeeds regardless of profile/email failures
});
```

---

## Isolation Levels

### Read Uncommitted

```typescript
import { sql } from 'drizzle-orm';

// Lowest isolation (allows dirty reads)
// ⚠️ Rarely used - can read uncommitted data from other transactions
await db.transaction(
  async (tx) => {
    const users = await tx.select().from(users);
    // Might see uncommitted changes from other transactions
  },
  {
    isolationLevel: 'read uncommitted',
  }
);
```

### Read Committed (Default)

```typescript
// Default isolation level
// Prevents dirty reads, but allows non-repeatable reads
await db.transaction(
  async (tx) => {
    // Read 1: Get user count
    const [count1] = await tx.select({ count: count() }).from(users);

    // Another transaction commits new user here...

    // Read 2: Might return different count
    const [count2] = await tx.select({ count: count() }).from(users);

    // count1 !== count2 is possible
  },
  {
    isolationLevel: 'read committed', // Default
  }
);
```

### Repeatable Read

```typescript
// Prevents dirty reads AND non-repeatable reads
// Consistent snapshot throughout transaction
await db.transaction(
  async (tx) => {
    // Read 1: Get user count
    const [count1] = await tx.select({ count: count() }).from(users);

    // Another transaction commits new user here...

    // Read 2: Returns SAME count as read 1
    const [count2] = await tx.select({ count: count() }).from(users);

    // count1 === count2 guaranteed
  },
  {
    isolationLevel: 'repeatable read',
  }
);
```

### Serializable

```typescript
// Highest isolation (transactions execute as if serial)
// Prevents dirty reads, non-repeatable reads, AND phantom reads
// ⚠️ Highest overhead, use only when necessary
await db.transaction(
  async (tx) => {
    // This transaction sees completely isolated view of database
    const users = await tx
      .select()
      .from(users)
      .where(eq(users.status, 'active'));

    // Update based on count
    if (users.length > 100) {
      await tx
        .update(settings)
        .set({ maxUsers: 100 })
        .where(eq(settings.key, 'user_limit'));
    }

    // No other transaction can affect this logic
  },
  {
    isolationLevel: 'serializable',
  }
);
```

### When to Use Each Isolation Level

| Level | Use Case | Pros | Cons |
|-------|----------|------|------|
| Read Uncommitted | Reporting (stale data OK) | Fastest | Dirty reads |
| Read Committed | Most applications | Balance | Non-repeatable reads |
| Repeatable Read | Financial reports | Consistent reads | Phantom reads possible |
| Serializable | Critical operations | Full isolation | Slowest, deadlocks |

---

## Error Handling

### Try-Catch Pattern

```typescript
async function createUserWithProfile(
  email: string,
  name: string,
  bio: string
) {
  try {
    return await db.transaction(async (tx) => {
      const [user] = await tx
        .insert(users)
        .values({ email, name })
        .returning();

      const [profile] = await tx
        .insert(profiles)
        .values({ userId: user.id, bio })
        .returning();

      return { user, profile };
    });
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('unique constraint')) {
        throw new Error('Email already exists');
      }
      if (error.message.includes('foreign key')) {
        throw new Error('Invalid user reference');
      }
    }
    throw error;
  }
}
```

### Custom Error Types

```typescript
class InsufficientFundsError extends Error {
  constructor(accountId: number, balance: number, amount: number) {
    super(
      `Insufficient funds in account ${accountId}. Balance: ${balance}, Requested: ${amount}`
    );
    this.name = 'InsufficientFundsError';
  }
}

class TransferError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TransferError';
  }
}

async function transferMoney(
  fromAccountId: number,
  toAccountId: number,
  amount: number
) {
  try {
    await db.transaction(async (tx) => {
      // Get source account
      const [fromAccount] = await tx
        .select()
        .from(accounts)
        .where(eq(accounts.id, fromAccountId))
        .limit(1);

      if (!fromAccount) {
        throw new TransferError(`Account ${fromAccountId} not found`);
      }

      if (fromAccount.balance < amount) {
        throw new InsufficientFundsError(
          fromAccountId,
          fromAccount.balance,
          amount
        );
      }

      // Deduct from source
      await tx
        .update(accounts)
        .set({ balance: sql`${accounts.balance} - ${amount}` })
        .where(eq(accounts.id, fromAccountId));

      // Add to destination
      await tx
        .update(accounts)
        .set({ balance: sql`${accounts.balance} + ${amount}` })
        .where(eq(accounts.id, toAccountId));

      // Record transfer
      await tx.insert(transfers).values({
        fromAccountId,
        toAccountId,
        amount,
        status: 'completed',
      });
    });
  } catch (error) {
    if (error instanceof InsufficientFundsError) {
      console.error('Cannot complete transfer:', error.message);
      // Send notification to user
    } else if (error instanceof TransferError) {
      console.error('Transfer error:', error.message);
      // Log to error tracking service
    } else {
      console.error('Unexpected error:', error);
      throw error;
    }
  }
}
```

### Retry Logic for Serialization Failures

```typescript
async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  let lastError: Error;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // Check if error is due to serialization failure
      if (
        error instanceof Error &&
        error.message.includes('could not serialize')
      ) {
        if (attempt < maxRetries) {
          // Exponential backoff
          const delay = Math.pow(2, attempt) * 100;
          await new Promise((resolve) => setTimeout(resolve, delay));
          continue;
        }
      }

      // Not a serialization error or max retries reached
      throw error;
    }
  }

  throw lastError!;
}

// Usage
const result = await withRetry(async () => {
  return await db.transaction(
    async (tx) => {
      // Your transaction logic here
      return await tx.select().from(users);
    },
    {
      isolationLevel: 'serializable',
    }
  );
});
```

---

## Concurrent Transactions

### Optimistic Locking

```typescript
// Use version field to detect concurrent updates
export const documents = pgTable('documents', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  version: integer('version').notNull().default(1),
});

async function updateDocument(id: number, title: string, content: string) {
  return await db.transaction(async (tx) => {
    // Read current version
    const [doc] = await tx
      .select()
      .from(documents)
      .where(eq(documents.id, id))
      .limit(1);

    if (!doc) {
      throw new Error('Document not found');
    }

    // Update with version check
    const [updated] = await tx
      .update(documents)
      .set({
        title,
        content,
        version: doc.version + 1,
      })
      .where(
        and(
          eq(documents.id, id),
          eq(documents.version, doc.version) // Ensure version hasn't changed
        )
      )
      .returning();

    if (!updated) {
      throw new Error('Document was modified by another user');
    }

    return updated;
  });
}
```

### Pessimistic Locking (FOR UPDATE)

```typescript
import { sql } from 'drizzle-orm';

// Lock row for update (other transactions wait)
await db.transaction(async (tx) => {
  // SELECT FOR UPDATE locks the row
  const [account] = await tx
    .select()
    .from(accounts)
    .where(eq(accounts.id, 1))
    .for('update'); // Locks row until transaction completes

  // No other transaction can read or modify this row
  await tx
    .update(accounts)
    .set({ balance: account.balance - 100 })
    .where(eq(accounts.id, 1));
});
```

### FOR UPDATE SKIP LOCKED

```typescript
// Process queue items without blocking
async function processNextQueueItem() {
  return await db.transaction(async (tx) => {
    // Get first available (non-locked) item
    const [item] = await tx
      .select()
      .from(queueItems)
      .where(eq(queueItems.status, 'pending'))
      .orderBy(asc(queueItems.createdAt))
      .limit(1)
      .for('update', { skipLocked: true });

    if (!item) {
      return null; // No items available
    }

    // Update status
    await tx
      .update(queueItems)
      .set({ status: 'processing', startedAt: new Date() })
      .where(eq(queueItems.id, item.id));

    return item;
  });
}
```

---

## Deadlock Prevention

### 1. Order Lock Acquisition

```typescript
// ❌ BAD: Can cause deadlock
// Transaction A: locks account 1, then account 2
// Transaction B: locks account 2, then account 1
async function transferBad(from: number, to: number, amount: number) {
  await db.transaction(async (tx) => {
    await tx.select().from(accounts).where(eq(accounts.id, from)).for('update');
    await tx.select().from(accounts).where(eq(accounts.id, to)).for('update');
    // ... perform transfer
  });
}

// ✅ GOOD: Always lock in same order (by ID)
async function transferGood(from: number, to: number, amount: number) {
  await db.transaction(async (tx) => {
    const [firstId, secondId] = [from, to].sort((a, b) => a - b);

    await tx.select().from(accounts).where(eq(accounts.id, firstId)).for('update');
    await tx.select().from(accounts).where(eq(accounts.id, secondId)).for('update');

    // ... perform transfer
  });
}
```

### 2. Keep Transactions Short

```typescript
// ❌ BAD: Long-running transaction
await db.transaction(async (tx) => {
  const users = await tx.select().from(users);

  // External API call (slow!)
  for (const user of users) {
    await sendEmail(user.email);
  }

  await tx.update(users).set({ emailSent: true });
});

// ✅ GOOD: Quick transaction
await db.transaction(async (tx) => {
  const users = await tx.select().from(users);

  await tx.update(users).set({ emailQueued: true });
});

// Send emails outside transaction
for (const user of users) {
  await sendEmail(user.email);
}
```

### 3. Set Transaction Timeout

```typescript
// Prevent long-running transactions
await db.transaction(
  async (tx) => {
    // Set timeout for this transaction
    await tx.execute(sql`SET LOCAL statement_timeout = '5s'`);

    // Your transaction logic
    // Will throw error if exceeds 5 seconds
  },
  {
    isolationLevel: 'serializable',
  }
);
```

---

## Transaction Best Practices

### 1. Keep Transactions Small

```typescript
// ✅ GOOD: Transaction only includes database operations
async function createUser(email: string, name: string) {
  const user = await db.transaction(async (tx) => {
    const [user] = await tx.insert(users).values({ email, name }).returning();
    await tx.insert(profiles).values({ userId: user.id }).returning();
    return user;
  });

  // Send email AFTER transaction commits
  await sendWelcomeEmail(user.email);

  return user;
}
```

### 2. Avoid External Calls in Transactions

```typescript
// ❌ BAD: External API call inside transaction
await db.transaction(async (tx) => {
  const [order] = await tx.insert(orders).values({ total: 99.99 }).returning();

  // Payment API call (slow and can fail)
  const payment = await stripe.charges.create({ amount: 9999 });

  await tx.insert(payments).values({ orderId: order.id, stripeId: payment.id });
});

// ✅ GOOD: External call outside transaction
const [order] = await db
  .insert(orders)
  .values({ total: 99.99, status: 'pending' })
  .returning();

try {
  const payment = await stripe.charges.create({ amount: 9999 });

  await db.transaction(async (tx) => {
    await tx.insert(payments).values({ orderId: order.id, stripeId: payment.id });
    await tx
      .update(orders)
      .set({ status: 'paid' })
      .where(eq(orders.id, order.id));
  });
} catch (error) {
  // Mark order as failed
  await db.update(orders).set({ status: 'failed' }).where(eq(orders.id, order.id));
}
```

### 3. Use Appropriate Isolation Level

```typescript
// Read-heavy reporting (allow stale data)
const stats = await db.transaction(
  async (tx) => {
    return {
      userCount: await tx.select({ count: count() }).from(users),
      orderCount: await tx.select({ count: count() }).from(orders),
    };
  },
  { isolationLevel: 'read committed' } // Default, fast
);

// Financial transfer (strict consistency)
await db.transaction(
  async (tx) => {
    await tx
      .update(accounts)
      .set({ balance: sql`${accounts.balance} - 100` })
      .where(eq(accounts.id, 1));

    await tx
      .update(accounts)
      .set({ balance: sql`${accounts.balance} + 100` })
      .where(eq(accounts.id, 2));
  },
  { isolationLevel: 'serializable' } // Strictest
);
```

### 4. Handle Errors Appropriately

```typescript
async function createOrderSafe(userId: number, total: number) {
  try {
    return await db.transaction(async (tx) => {
      const [order] = await tx
        .insert(orders)
        .values({ userId, total, status: 'pending' })
        .returning();

      await tx.insert(orderItems).values([
        /* items */
      ]);

      return order;
    });
  } catch (error) {
    // Log error
    console.error('Order creation failed:', error);

    // Notify monitoring service
    if (process.env.NODE_ENV === 'production') {
      await notifyErrorTracking(error);
    }

    // Return user-friendly error
    throw new Error('Failed to create order. Please try again.');
  }
}
```

### 5. Test Transaction Rollback

```typescript
import { describe, it, expect, beforeEach } from 'vitest';

describe('Transaction Tests', () => {
  it('should rollback on error', async () => {
    // Count before transaction
    const [before] = await db.select({ count: count() }).from(users);

    try {
      await db.transaction(async (tx) => {
        await tx.insert(users).values({ email: 'test@example.com', name: 'Test' });
        // Simulate error
        throw new Error('Transaction failed');
      });
    } catch (error) {
      // Expected
    }

    // Count after transaction
    const [after] = await db.select({ count: count() }).from(users);

    // Count should be unchanged
    expect(after.count).toBe(before.count);
  });
});
```

---

## Edge Runtime Limitations

### Transactions on Vercel Edge

```typescript
// ⚠️ WARNING: Long-running transactions may timeout on Edge Runtime
// Edge functions have 25-second timeout

// ✅ GOOD: Quick transaction (< 1 second)
export const POST = async (request: Request) => {
  const data = await request.json();

  const result = await db.transaction(async (tx) => {
    const [user] = await tx.insert(users).values(data).returning();
    await tx.insert(profiles).values({ userId: user.id });
    return user;
  });

  return Response.json(result);
};

// ❌ BAD: Long transaction (may timeout)
export const POST = async (request: Request) => {
  await db.transaction(async (tx) => {
    // Processing thousands of records
    for (const item of largeDataset) {
      await tx.insert(items).values(item);
    }
  });
};
```

### Alternative: Use Background Jobs

```typescript
// ✅ GOOD: Queue large operations
export const POST = async (request: Request) => {
  const data = await request.json();

  // Quick transaction: create job
  const [job] = await db
    .insert(jobs)
    .values({
      type: 'import_data',
      data: JSON.stringify(data),
      status: 'pending',
    })
    .returning();

  // Process job in background worker (not Edge Runtime)
  await queueJob(job.id);

  return Response.json({ jobId: job.id });
};
```

---

**Official Docs**: https://orm.drizzle.team/docs/transactions
**Next**: [relations.md](./relations.md) for relationship patterns
