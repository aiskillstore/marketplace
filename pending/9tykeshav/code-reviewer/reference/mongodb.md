# MongoDB Code Review

MongoDB 7.x / Mongoose 8.x | Dec 2025

## Schema Patterns

| Pattern | When | Flag |
|---------|------|------|
| Embed | Read together, small/bounded, rare updates | Array > 100 items |
| Reference | Read independently, large/unbounded, frequent updates | Unused embedded data |
| Bucket | Time-series data | Count limit (200 measurements) |
| Computed | Denormalized stats | Missing update logic |

```javascript
// BAD: Unbounded array → 16MB limit
{ comments: [{ author, text }] }  // GOOD: Separate collection + count

// M2M junction
.index({ student: 1, course: 1 }, { unique: true })
```

## Index Anti-Patterns

| Issue | BAD | GOOD |
|-------|-----|------|
| ESR violation | `{ createdAt: 1, status: 1 }` | `{ status: 1, createdAt: -1 }` (Equality → Sort → Range) |
| Boolean index | `{ isActive: 1 }` | `{ isActive: 1, userId: 1 }` (compound) |
| Sparse data | `{ deletedAt: 1 }` (90% null) | `partialFilterExpression: { deletedAt: { $exists: true } }` |
| Uncovered query | Projection includes unindexed field | `{ _id: 0, indexedField1: 1, indexedField2: 1 }` |

```javascript
// N+1 Flag: Loop with await
for (const post of posts) {
  await Comment.find({ postId: post._id });  // N queries!
}
// GOOD: $lookup or populate once
```

## Query Red Flags

```javascript
// BAD: Skip pagination (scans 1980 docs for page 100)
.skip((page - 1) * 20)
// GOOD: Cursor-based
.find({ _id: { $lt: lastSeenId } }).sort({ _id: -1 }).limit(20)

// BAD: $where (no index, JS eval)
{ $where: 'this.firstName + " " + this.lastName === "John Doe"' }

// BAD: Unanchored regex (full scan)
{ email: /gmail\.com/ }
// GOOD: Anchored
{ email: /^john/ }

// BAD: $ne (scans almost all docs)
{ status: { $ne: 'deleted' } }
// GOOD: Positive match
{ status: { $in: ['active', 'pending'] } }
```

// explain() red flags: COLLSCAN | totalDocsExamined/nReturned > 2 | executionTimeMillis > 100

## Security Gotchas

| Vulnerability | Attack | Fix |
|--------------|--------|-----|
| NoSQL injection | `{ username: { "$gt": "" } }` | `express-mongo-sanitize()` + schema validation |
| Operator injection | `?age[$gt]=0` | Parse/validate: `parseInt(req.query.age, 10)` |
| Mass assignment | `req.body` sets `{ role: "admin" }` | Whitelist fields before update |
| Invalid ObjectId | Crashes on malformed ID | `mongoose.Types.ObjectId.isValid(id)` |
| Password leak | Returns in JSON | `password: { type: String, select: false }` |

```javascript
// toJSON protection
userSchema.set('toJSON', { transform: (doc, ret) => { delete ret.password; delete ret.__v; return ret; } });

// .lean() - 5-10x faster for read-only
await User.find({}).lean();

// Populate projection
.populate({ path: 'author', select: 'name avatar', options: { limit: 10 } })

// Async validator
userSchema.path('email').validate(async function(val) {
  return await User.countDocuments({ email: val, _id: { $ne: this._id } }) === 0;
}, 'Email exists');

// Duplicate key middleware
userSchema.post('save', function(error, doc, next) {
  if (error.code === 11000) next(new Error('Duplicate key'));
  else next(error);
});
```

## Aggregation

```javascript
// BAD: $match at end → GOOD: $match first, $project early
{ $match: { status: 'active' } },  // Filter early
{ $project: { _id: 1, items: 1 } },  // Reduce doc size

// $lookup with pipeline projection
{ $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user',
  pipeline: [{ $project: { name: 1 } }] }}

// Large pipelines: .allowDiskUse(true)
```

## Transactions & Batching

```javascript
// Transaction pattern
const session = await mongoose.startSession();
try {
  session.startTransaction();
  await Order.create([data], { session });
  await Product.updateOne({ _id }, { $inc: { stock: -qty } }, { session });
  await session.commitTransaction();
} catch (err) { await session.abortTransaction(); throw err; }
finally { session.endSession(); }
// BAD: External API inside transaction (holds locks!)

// Cursor batching (avoid OOM on 1M+ docs)
let lastId = null;
while (true) {
  const batch = await User.find(lastId ? { _id: { $gt: lastId } } : {}).sort({ _id: 1 }).limit(1000).lean();
  if (!batch.length) break;
  await Promise.all(batch.map(process));
  lastId = batch[batch.length - 1]._id;
}
```

## Code Review Checklist

### Schema
- [ ] Arrays bounded (no unbounded growth)
- [ ] Embed vs reference documented
- [ ] Schema validation on all fields
- [ ] `select: false` on sensitive fields
- [ ] Denormalization has update strategy

### Indexes
- [ ] All query patterns indexed
- [ ] Compound indexes use ESR rule
- [ ] No redundant indexes
- [ ] `explain()` verified (no COLLSCAN)
- [ ] Partial/sparse where appropriate

### Queries
- [ ] No N+1 patterns
- [ ] Cursor pagination (not skip)
- [ ] Projections limit fields
- [ ] No `$where` or unanchored regex
- [ ] `.lean()` for read-only

### Security
- [ ] Input sanitization (mongo-sanitize)
- [ ] ObjectId validation
- [ ] Mass assignment whitelisted
- [ ] No password/token in responses
- [ ] No query operator injection

### Transactions
- [ ] Multi-doc ops use transactions
- [ ] Short transaction duration
- [ ] Retry logic for transient errors
- [ ] Session cleanup in finally

### Performance
- [ ] Cursors for large datasets
- [ ] `$match` first in aggregations
- [ ] Connection pooling configured
- [ ] Slow query logging enabled
- [ ] Memory usage considered

---

## Common Gotchas

1. **16MB Document Limit**: Unbounded arrays hit this
2. **Index on Boolean**: Low selectivity, combine with other fields
3. **Skip Pagination**: Scans all skipped docs (use cursor)
4. **$ne Query**: Scans almost everything (use $in)
5. **Populate Everything**: Slows queries, project selectively
6. **No Lean**: 10x slower for read-only
7. **N+1 in Loops**: Use $lookup or populate outside loop
8. **Schema-less**: Leads to data inconsistency
9. **Single Connection**: Don't reconnect per request
10. **Transaction for Single Doc**: Unnecessary (atomic by default)
