---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: debugging
---

# Debugging Workflows

Reference guide for common debugging workflows and techniques across different scenarios.

## Debugging Workflows by Issue Type

### Production Errors

**Workflow:**

1. Capture error message and stack trace
2. Check error logs for context
3. Identify when error started (deployment, traffic spike, etc.)
4. Reproduce in staging environment
5. Add logging to trace execution path
6. Identify root cause
7. Implement fix with tests
8. Deploy and monitor

**Tools:**

- Error tracking (Sentry, Rollbar)
- Log aggregation (ELK, Datadog)
- APM tools (New Relic, AppDynamics)

### Test Failures

**Workflow:**

1. Read test failure message
2. Understand what the test expects
3. Run test in isolation
4. Check test data and setup
5. Trace through code execution
6. Identify why test fails
7. Fix code or test as appropriate
8. Verify test passes

**Tools:**

- Test runner debug mode
- IDE debugger
- Test coverage tools

### Performance Issues

**Workflow:**

1. Measure current performance
2. Identify slow operations
3. Profile to find bottlenecks
4. Analyze profiling data
5. Optimize identified bottlenecks
6. Measure improvement
7. Verify no regressions

**Tools:**

- Profilers (Chrome DevTools, py-spy)
- APM tools
- Performance monitoring

## Language-Specific Debugging

### JavaScript/Node.js

**Debugging Tools:**

- Chrome DevTools
- Node.js debugger
- console.log (strategic logging)
- debugger statement

**Common Issues:**

- Undefined variables
- Async/await errors
- Promise rejections
- Scope issues
- Type coercion

**Techniques:**

- Use debugger breakpoints
- Log variable states
- Check call stack
- Inspect closures
- Monitor event loop

### Python

**Debugging Tools:**

- pdb (Python debugger)
- ipdb (enhanced debugger)
- print() statements
- logging module

**Common Issues:**

- AttributeError
- TypeError
- IndentationError
- Import errors
- NameError

**Techniques:**

- Use pdb.set_trace()
- Check variable types
- Verify imports
- Check indentation
- Use type hints

### Java

**Debugging Tools:**

- IntelliJ debugger
- Eclipse debugger
- jdb (command line)
- Logging frameworks

**Common Issues:**

- NullPointerException
- ClassCastException
- OutOfMemoryError
- StackOverflowError

**Techniques:**

- Set breakpoints
- Inspect variables
- Check exception stack traces
- Monitor memory usage
- Use profilers

## Debugging Techniques

### Binary Search

**When to Use:**

- Large codebase
- Unclear where issue is
- Many potential causes

**Process:**

1. Divide code in half
2. Test which half has issue
3. Repeat on problematic half
4. Narrow down to specific location

### Rubber Duck Debugging

**Process:**

1. Explain code to "rubber duck" (or yourself)
2. Walk through execution step by step
3. Identify assumptions
4. Find where logic breaks

### Logging Strategy

**What to Log:**

- Function entry/exit
- Variable values at key points
- Decision points (if/else branches)
- Error conditions
- Performance metrics

**Log Levels:**

- DEBUG: Detailed diagnostic info
- INFO: General informational messages
- WARN: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical failures

### Reproducing Issues

**Steps:**

1. Identify exact conditions that trigger issue
2. Document steps to reproduce
3. Create minimal test case
4. Verify issue reproduces consistently
5. Isolate variables

**Common Challenges:**

- Intermittent issues
- Race conditions
- Environment-specific
- Data-dependent

## Debugging Checklist

### Before Starting

- [ ] Understand what should happen
- [ ] Understand what's actually happening
- [ ] Have reproduction steps
- [ ] Have access to logs/debugger

### During Debugging

- [ ] Form hypotheses
- [ ] Test hypotheses systematically
- [ ] Document findings
- [ ] Check assumptions
- [ ] Look for patterns

### After Finding Root Cause

- [ ] Verify root cause is correct
- [ ] Understand why it happened
- [ ] Implement fix
- [ ] Test fix thoroughly
- [ ] Check for similar issues
- [ ] Document solution

## Common Error Patterns

Reference guide for identifying and resolving common error patterns across different systems and languages.

### Database Errors

#### Connection Pool Exhaustion

**Symptoms:**

- `ECONNREFUSED` errors
- Errors spike during high traffic
- Connection pool size is smaller than concurrent requests

**Pattern:**

```
Error: ECONNREFUSED
Connection pool exhausted
Too many connections
```

**Root Causes:**

- Connection pool size too small
- Connections not being released
- Long-running transactions holding connections
- Missing connection cleanup in error handlers

**Solutions:**

- Increase connection pool size
- Ensure connections are released in finally blocks
- Add connection timeout
- Implement connection retry logic

#### N+1 Query Problem

**Symptoms:**

- Slow response times
- Many database queries for single operation
- Queries increase linearly with data size

**Pattern:**

```
SELECT * FROM users;
SELECT * FROM posts WHERE user_id = 1;
SELECT * FROM posts WHERE user_id = 2;
SELECT * FROM posts WHERE user_id = 3;
...
```

**Solutions:**

- Use eager loading (JOINs)
- Batch queries
- Use data loaders
- Implement query result caching

### Memory Leaks

#### Event Listener Leaks

**Symptoms:**

- Memory usage grows over time
- No decrease after component/page unload
- Correlates with user interactions

**Pattern:**

```javascript
// Problem: Listeners registered but never removed
window.addEventListener('resize', handler);
// Missing: window.removeEventListener('resize', handler);
```

**Solutions:**

- Always remove event listeners
- Use cleanup functions in React useEffect
- Use WeakMap for automatic cleanup
- Monitor listener count

#### Closure Leaks

**Symptoms:**

- Memory growth in long-running applications
- Large objects retained in closures
- Circular references

**Pattern:**

```javascript
// Problem: Large object retained in closure
function createHandler(largeData) {
  return function() {
    // largeData retained even if not used
  };
}
```

**Solutions:**

- Avoid retaining large objects in closures
- Use WeakMap/WeakSet when possible
- Clear references when done
- Use memory profilers to identify leaks

### Race Conditions

#### Concurrent Modification

**Symptoms:**

- Intermittent failures
- Data inconsistency
- Errors only under load

**Pattern:**

```
Thread 1: Read value (100)
Thread 2: Read value (100)
Thread 1: Write value (101)
Thread 2: Write value (101) // Lost update
```

**Solutions:**

- Use locks/mutexes
- Implement optimistic locking
- Use atomic operations
- Add request queuing

#### Async Race Conditions

**Symptoms:**

- Results arrive out of order
- Stale data displayed
- Race between multiple async operations

**Pattern:**

```javascript
// Problem: Race between requests
fetch('/api/users/1').then(setUser1);
fetch('/api/users/2').then(setUser2);
// Results may arrive in wrong order
```

**Solutions:**

- Use Promise.all for parallel operations
- Cancel previous requests
- Use request IDs to match responses
- Implement request deduplication

### Timeout Issues

#### Request Timeouts

**Symptoms:**

- Requests fail after specific duration
- Timeout errors in logs
- Slow external dependencies

**Pattern:**

```
Error: Request timeout after 30000ms
ETIMEDOUT
```

**Solutions:**

- Increase timeout for slow operations
- Implement retry with exponential backoff
- Add timeout configuration
- Optimize slow operations

#### Database Query Timeouts

**Symptoms:**

- Queries fail after timeout period
- Slow query logs show long-running queries
- Timeouts during peak load

**Solutions:**

- Optimize slow queries
- Add appropriate indexes
- Increase query timeout
- Implement query cancellation

### Authentication Errors

#### Token Expiration

**Symptoms:**

- 401 Unauthorized errors
- Errors after specific time period
- Token refresh needed

**Pattern:**

```
401 Unauthorized
Token expired
Invalid token
```

**Solutions:**

- Implement token refresh logic
- Handle token expiration gracefully
- Add token expiration checks
- Use refresh tokens

#### Session Expiration

**Symptoms:**

- Users logged out unexpectedly
- Session errors after inactivity
- Cookie expiration issues

**Solutions:**

- Extend session on activity
- Implement session refresh
- Handle expiration gracefully
- Clear expired sessions

### Network Errors

#### Connection Refused

**Symptoms:**

- Service unavailable errors
- Connection refused errors
- Service not running

**Pattern:**

```
ECONNREFUSED
Connection refused
Service unavailable
```

**Solutions:**

- Check if service is running
- Verify port configuration
- Check firewall rules
- Implement health checks

#### DNS Resolution Failures

**Symptoms:**

- Cannot resolve hostname
- DNS lookup failures
- Network configuration issues

**Pattern:**

```
ENOTFOUND
DNS resolution failed
getaddrinfo failed
```

**Solutions:**

- Verify DNS configuration
- Check hostname spelling
- Use IP addresses as fallback
- Implement DNS caching

### Application Errors

#### Null Reference Errors

**Symptoms:**

- NullPointerException (Java)
- TypeError: Cannot read property (JavaScript)
- AttributeError (Python)

**Pattern:**

```
TypeError: Cannot read property 'x' of undefined
NullPointerException
AttributeError: 'NoneType' object has no attribute
```

**Solutions:**

- Add null checks
- Use optional chaining
- Provide default values
- Validate inputs

#### Type Errors

**Symptoms:**

- Type mismatch errors
- Invalid type errors
- Casting failures

**Pattern:**

```
TypeError: expected string, got number
InvalidCastException
Type mismatch
```

**Solutions:**

- Add type validation
- Use type guards
- Implement proper type checking
- Handle type conversions

### Performance Errors

#### Out of Memory

**Symptoms:**

- Application crashes
- Memory limit exceeded
- Heap out of memory

**Pattern:**

```
OutOfMemoryError
Heap out of memory
Memory limit exceeded
```

**Solutions:**

- Increase memory limits
- Optimize memory usage
- Implement pagination
- Use streaming for large data

#### CPU Exhaustion

**Symptoms:**

- Slow response times
- High CPU usage
- Application freezing

**Pattern:**

- High CPU utilization (90%+)
- Slow processing
- Event loop blocking

**Solutions:**

- Optimize algorithms
- Use worker threads
- Implement caching
- Break up long-running tasks
