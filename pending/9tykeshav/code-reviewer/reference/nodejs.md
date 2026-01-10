# Node.js - Critical Patterns & Anti-Patterns

## Async Anti-Patterns to Flag

| Pattern | BAD | GOOD |
|---------|-----|------|
| Sequential await | `const u = await f1(); const p = await f2();` | `const [u,p] = await Promise.all([f1(),f2()]);` |
| Await in loop | `for(const x of xs) await f(x);` | Batch with concurrency limit |
| Floating promises | `asyncFn(); next();` | `await asyncFn(); next();` |
| Missing unhandledRejection | No handler | `process.on('unhandledRejection', (r,p) => {})` |

**Promise Methods**
| Method | Use | Fails When |
|--------|-----|-----------|
| `Promise.all()` | All must succeed | Any rejects |
| `Promise.allSettled()` | Independent ops | Never (returns all) |
| `Promise.race()` | First wins | First rejects |
| `Promise.any()` | First success | All reject |

## Memory Leak Patterns

| Pattern | Example | Fix |
|---------|---------|-----|
| Unbounded cache | `cache[id] = data;` | Use LRU cache with max/ttl |
| Event listeners | `res.on('data', fn);` never removed | `res.once('end', () => res.removeListener())` |
| Closures capture | `const largeData = new Array(1e6); return () => {}` | Set to null when done |
| Timers not cleared | `setInterval(fn, 1000);` | Store ref, `clearInterval(timer)` |
| Buffer concat in loop | `result = Buffer.concat([result, chunk]);` | Collect chunks, concat once at end |

## Event Loop Gotchas

**Execution Order (Highest to Lowest)**
1. `process.nextTick()` - microtask queue, starves I/O if recursive
2. Promise callbacks - `.then()`, `async/await`
3. `setTimeout(fn, 0)` / `setInterval` - timers phase
4. `setImmediate()` - check phase (after I/O)

**Critical Rules**
- Use `setImmediate` for recursive ops (not `nextTick` - starves I/O)
- Never use sync I/O: `fs.readFileSync()`, `crypto.randomBytesSync()`, etc
- CPU loops > 50ms → offload to Worker Thread

## Error Handling

| Error Type | Examples | Action |
|------------|----------|--------|
| Operational | Network fail, file not found, invalid input | Log, return error response |
| Programmer | TypeError, ReferenceError, undefined | Crash and restart |

```javascript
// REQUIRED handlers
process.on('unhandledRejection', (reason, promise) => gracefulShutdown());
process.on('uncaughtException', (error) => {
  if (!error.isOperational) process.exit(1);
});
```

## Stream Backpressure

| Pattern | Code |
|---------|------|
| BAD - Ignores backpressure | `readable.on('data', c => writable.write(c));` |
| GOOD - Manual handling | `const ok = writable.write(c); if(!ok) readable.pause();` |
| BEST - Use pipeline | `await pipeline(readable, transform, writable);` |

## Security Vulnerabilities

### Prototype Pollution
```javascript
// VULNERABLE: for(const k in src) target[k] = src[k];
// FIX: Skip __proto__, constructor, prototype
// BEST: Use Map() instead of {}
```

### Command Injection
```javascript
// VULNERABLE: exec(`ping ${userInput}`);
// FIX: execFile('ping', ['-c', '4', userInput]);
```

### Path Traversal
```javascript
// VULNERABLE: path.join('/uploads', req.params.filename);
// FIX: const requested = path.resolve(uploadsDir, filename);
//      if(!requested.startsWith(uploadsDir + path.sep)) throw;
```

## Child Processes vs Workers

| Use Case | Solution | Notes |
|----------|----------|-------|
| Shell commands | `spawn`/`execFile` | Never `exec` with user input |
| CPU-intensive (same code) | Worker Threads | Share memory with SharedArrayBuffer |
| CPU-intensive (separate) | `fork` | IPC overhead |
| Stream large data | `spawn` | stdio pipes |

## Process Management

```javascript
// Graceful Shutdown - REQUIRED
function gracefulShutdown(signal) {
  server.close(async () => {
    await db.close(); await redis.quit();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 30000); // Force after 30s
}
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
```

## Circular Dependencies

| Problem | Solution |
|---------|----------|
| `a.js` requires `b.js` requires `a.js` | 1. Extract shared to separate module |
| | 2. Use late binding: `getB = () => require('./b')` |
| | 3. Dependency injection via constructor |

## File Operations

| Pattern | Code |
|---------|------|
| BAD - Sync in async | `fs.readFileSync()` |
| GOOD - Async | `fs.promises.readFile()` |
| Atomic write | Write to `.tmp`, then `fs.rename()` (atomic) |

## Debugging Commands

```bash
node --inspect-brk app.js              # Debug from start
node --expose-gc --max-old-space-size=4096 app.js
node --prof app.js                     # CPU profile
node --prof-process isolate-*.log
```

```javascript
// Heap snapshot
require('v8').writeHeapSnapshot('heap.heapsnapshot');
```

## Environment Config

```javascript
// Validate at startup - FAIL FAST
const required = ['MONGODB_URI', 'JWT_SECRET'];
const missing = required.filter(k => !process.env[k]);
if(missing.length) { console.error(`Missing: ${missing}`); process.exit(1); }
```

## Code Review Checklist

**Async**
- [ ] All async functions have try-catch or .catch()
- [ ] No floating promises (missing await)
- [ ] Parallel ops use Promise.all where possible
- [ ] Promise.allSettled for independent operations

**Event Loop**
- [ ] No sync I/O (fs.readFileSync, etc)
- [ ] No CPU-intensive loops in handlers
- [ ] CPU work offloaded to workers
- [ ] setImmediate used (not nextTick) for recursion

**Memory**
- [ ] No unbounded global caches
- [ ] Event listeners removed when done
- [ ] Timers cleared properly
- [ ] Streams used for large data
- [ ] Buffers not concatenated in loops

**Errors**
- [ ] unhandledRejection handler present
- [ ] uncaughtException handler present
- [ ] Operational vs programmer errors distinguished
- [ ] Errors don't leak sensitive info

**Security**
- [ ] No prototype pollution (check merges, JSON.parse)
- [ ] No command injection (use execFile, not exec)
- [ ] No path traversal (validate with path.resolve)
- [ ] User input validated/sanitized
- [ ] Dependencies audited (npm audit)

**Streams**
- [ ] Backpressure respected (or use pipeline)
- [ ] Stream errors handled
- [ ] Streams cleaned up on error

**Process**
- [ ] Graceful shutdown on SIGTERM/SIGINT
- [ ] Resources cleaned up (DB, Redis, etc)
- [ ] Zombie processes prevented
- [ ] Worker pools have size limits

**File System**
- [ ] Async operations used (not sync)
- [ ] Path traversal prevented
- [ ] Atomic writes for critical files
- [ ] File watchers closed on shutdown

**Anti-Patterns**
- [ ] No circular dependencies
- [ ] No require() in hot paths
- [ ] No blocking in event handlers
- [ ] No empty catch blocks
- [ ] Errors not silently swallowed
