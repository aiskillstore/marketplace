---
name: snippet-manager
description: Save, organize, search, and retrieve code snippets with tags, categories, and smart search capabi...
---

# Snippet Manager Skill

Save, organize, search, and retrieve code snippets with tags, categories, and smart search capabilities.

## Instructions

You are a code snippet management expert. When invoked:

1. **Save Code Snippets**:
   - Extract reusable code patterns
   - Add metadata (language, tags, description)
   - Organize by category and use case
   - Version snippet variations

2. **Search and Retrieve**:
   - Search by language, tags, or keywords
   - Find similar patterns
   - Suggest relevant snippets based on context
   - Filter by framework or library

3. **Snippet Organization**:
   - Categorize snippets logically
   - Tag with relevant keywords
   - Group related snippets
   - Create snippet collections

4. **Snippet Enhancement**:
   - Add usage examples
   - Document parameters and options
   - Include edge cases
   - Provide alternative implementations

## Snippet Categories

- **Language Basics**: Common patterns, idioms, syntax helpers
- **Data Structures**: Arrays, objects, maps, sets manipulation
- **Algorithms**: Sorting, searching, recursion, dynamic programming
- **API Patterns**: REST clients, error handling, authentication
- **Database**: Queries, migrations, ORM patterns
- **Testing**: Test setups, mocks, assertions
- **React/Vue/Angular**: Component patterns, hooks, directives
- **Node.js**: Express middleware, streams, file operations
- **Python**: Decorators, context managers, generators
- **DevOps**: Docker, CI/CD, deployment scripts
- **Utilities**: Date/time, string manipulation, validation

## Usage Examples

```
@snippet-manager Save API error handler
@snippet-manager --search "react hooks"
@snippet-manager --category testing
@snippet-manager --language python
@snippet-manager --tag async
@snippet-manager --collection "authentication patterns"
```

## Snippet Format

### Basic Snippet Structure

```markdown
# Snippet: Async Error Handler Wrapper

**Language**: JavaScript/TypeScript
**Category**: Error Handling
**Tags**: async, error-handling, middleware, express
**Framework**: Express.js
**Use Case**: Wrap async route handlers to catch errors

## Code

```javascript
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Usage
app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
}));
```

## Parameters
- `fn`: Async function to wrap (Request, Response, NextFunction) => Promise<void>

## Returns
Express middleware function that handles promise rejections

## Notes
- Eliminates try-catch blocks in route handlers
- Passes errors to Express error handler middleware
- Works with any async function

## Related Snippets
- [Express Error Handler Middleware](#express-error-handler)
- [Custom Error Classes](#custom-error-classes)
```

## JavaScript/TypeScript Snippets

### Debounce Function

```javascript
// Snippet: Debounce
// Category: Performance
// Tags: debounce, performance, optimization

function debounce(func, wait, immediate = false) {
  let timeout;

  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };

    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func.apply(this, args);
  };
}

// Usage
const handleSearch = debounce((query) => {
  fetchResults(query);
}, 300);

// In React
const [searchTerm, setSearchTerm] = useState('');

const debouncedSearch = useMemo(
  () => debounce((term) => {
    // Perform search
    console.log('Searching for:', term);
  }, 500),
  []
);

useEffect(() => {
  debouncedSearch(searchTerm);
}, [searchTerm, debouncedSearch]);
```

### Deep Clone Object

```javascript
// Snippet: Deep Clone
// Category: Data Structures
// Tags: clone, deep-copy, objects

// Method 1: JSON (simple objects only)
const deepClone = (obj) => JSON.parse(JSON.stringify(obj));

// Method 2: Structured Clone (modern browsers/Node.js)
const deepClone2 = (obj) => structuredClone(obj);

// Method 3: Custom recursive (handles complex types)
function deepClone3(obj, hash = new WeakMap()) {
  if (Object(obj) !== obj) return obj; // primitives
  if (hash.has(obj)) return hash.get(obj); // cyclic reference

  const result = Array.isArray(obj)
    ? []
    : obj.constructor
      ? new obj.constructor()
      : Object.create(null);

  hash.set(obj, result);

  return Object.assign(
    result,
    ...Object.keys(obj).map(key => ({
      [key]: deepClone3(obj[key], hash)
    }))
  );
}

// Usage
const original = { a: 1, b: { c: 2 }, d: [3, 4] };
const cloned = deepClone(original);
cloned.b.c = 999; // original.b.c remains 2
```

### Retry with Exponential Backoff

```typescript
// Snippet: Retry with Exponential Backoff
// Category: Error Handling
// Tags: retry, async, error-handling, resilience

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    factor?: number;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    factor = 2,
  } = options;

  let lastError: Error;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (attempt === maxRetries) {
        throw new Error(
          `Failed after ${maxRetries} retries: ${lastError.message}`
        );
      }

      console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));

      delay = Math.min(delay * factor, maxDelay);
    }
  }

  throw lastError!;
}

// Usage
const data = await retryWithBackoff(
  () => fetch('https://api.example.com/data').then(r => r.json()),
  { maxRetries: 5, initialDelay: 500 }
);
```

### Local Storage with Expiry

```javascript
// Snippet: Local Storage with Expiry
// Category: Browser APIs
// Tags: localstorage, cache, expiry

const storage = {
  set(key, value, expiryMs = null) {
    const item = {
      value,
      expiry: expiryMs ? Date.now() + expiryMs : null,
    };
    localStorage.setItem(key, JSON.stringify(item));
  },

  get(key) {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) return null;

    const item = JSON.parse(itemStr);

    if (item.expiry && Date.now() > item.expiry) {
      localStorage.removeItem(key);
      return null;
    }

    return item.value;
  },

  remove(key) {
    localStorage.removeItem(key);
  },

  clear() {
    localStorage.clear();
  },
};

// Usage
storage.set('user', { id: 1, name: 'John' }, 3600000); // 1 hour
const user = storage.get('user');
```

## React Snippets

### Custom useDebounce Hook

```typescript
// Snippet: useDebounce Hook
// Category: React Hooks
// Tags: react, hooks, debounce, performance

import { useEffect, useState } from 'react';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm) {
      // Perform search
      fetchResults(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
    />
  );
}
```

### Custom useAsync Hook

```typescript
// Snippet: useAsync Hook
// Category: React Hooks
// Tags: react, hooks, async, data-fetching

import { useEffect, useState, useCallback } from 'react';

type Status = 'idle' | 'loading' | 'success' | 'error';

interface AsyncState<T> {
  status: Status;
  data: T | null;
  error: Error | null;
}

function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true
) {
  const [state, setState] = useState<AsyncState<T>>({
    status: 'idle',
    data: null,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ status: 'loading', data: null, error: null });

    try {
      const data = await asyncFunction();
      setState({ status: 'success', data, error: null });
      return data;
    } catch (error) {
      setState({ status: 'error', data: null, error: error as Error });
      throw error;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { ...state, execute };
}

// Usage
function UserProfile({ userId }) {
  const { status, data, error } = useAsync(
    () => fetch(`/api/users/${userId}`).then(r => r.json()),
    true
  );

  if (status === 'loading') return <div>Loading...</div>;
  if (status === 'error') return <div>Error: {error.message}</div>;
  if (status === 'success') return <div>User: {data.name}</div>;

  return null;
}
```

### Custom useLocalStorage Hook

```typescript
// Snippet: useLocalStorage Hook
// Category: React Hooks
// Tags: react, hooks, localstorage, persistence

import { useState, useEffect } from 'react';

function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] {
  // Get from local storage then parse stored json or return initialValue
  const readValue = (): T => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  };

  const [storedValue, setStoredValue] = useState<T>(readValue);

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;

      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  useEffect(() => {
    setStoredValue(readValue());
  }, []);

  return [storedValue, setValue];
}

// Usage
function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Current theme: {theme}
    </button>
  );
}
```

## Python Snippets

### Retry Decorator

```python
# Snippet: Retry Decorator
# Category: Error Handling
# Tags: python, decorator, retry, error-handling

import time
import functools
from typing import Callable, Type

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator

# Usage
@retry(max_attempts=5, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Context Manager for Timing

```python
# Snippet: Timing Context Manager
# Category: Performance
# Tags: python, context-manager, timing, profiling

import time
from contextlib import contextmanager
from typing import Optional

@contextmanager
def timer(name: Optional[str] = None):
    """
    Context manager to time code execution

    Usage:
        with timer("Database query"):
            result = db.query(...)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        label = f"{name}: " if name else ""
        print(f"{label}Elapsed time: {elapsed:.4f}s")

# Usage
with timer("API call"):
    response = requests.get("https://api.example.com/data")
    data = response.json()

# Alternative: As a decorator
def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timed
def process_data(data):
    # Process data
    pass
```

### Memoization with LRU Cache

```python
# Snippet: Memoization
# Category: Performance
# Tags: python, cache, memoization, optimization

from functools import lru_cache, wraps
import pickle
import hashlib

# Simple memoization with lru_cache
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Custom memoization for unhashable arguments
def memoize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create hashable key from arguments
        key = hashlib.md5(
            pickle.dumps((args, tuple(sorted(kwargs.items()))))
        ).hexdigest()

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    wrapper.cache_clear = lambda: cache.clear()
    wrapper.cache_info = lambda: f"Cache size: {len(cache)}"

    return wrapper

# Usage with unhashable types (lists, dicts)
@memoize
def expensive_computation(data: list[int]) -> int:
    return sum(x ** 2 for x in data)

result = expensive_computation([1, 2, 3, 4, 5])
```

## Node.js Snippets

### Rate Limiter Middleware

```javascript
// Snippet: Rate Limiter
// Category: Middleware
// Tags: nodejs, express, rate-limiting, security

class RateLimiter {
  constructor(options = {}) {
    this.windowMs = options.windowMs || 60000; // 1 minute
    this.maxRequests = options.maxRequests || 100;
    this.requests = new Map();
  }

  middleware() {
    return (req, res, next) => {
      const key = req.ip || req.connection.remoteAddress;
      const now = Date.now();

      if (!this.requests.has(key)) {
        this.requests.set(key, []);
      }

      const userRequests = this.requests.get(key);

      // Remove old requests outside the window
      const validRequests = userRequests.filter(
        timestamp => now - timestamp < this.windowMs
      );

      if (validRequests.length >= this.maxRequests) {
        const oldestRequest = validRequests[0];
        const resetTime = oldestRequest + this.windowMs;
        const retryAfter = Math.ceil((resetTime - now) / 1000);

        res.set('Retry-After', retryAfter.toString());
        return res.status(429).json({
          error: 'Too many requests',
          retryAfter: retryAfter,
        });
      }

      validRequests.push(now);
      this.requests.set(key, validRequests);

      res.set('X-RateLimit-Limit', this.maxRequests.toString());
      res.set('X-RateLimit-Remaining',
        (this.maxRequests - validRequests.length).toString()
      );

      next();
    };
  }

  // Cleanup old entries periodically
  cleanup() {
    const now = Date.now();
    for (const [key, timestamps] of this.requests.entries()) {
      const valid = timestamps.filter(t => now - t < this.windowMs);
      if (valid.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, valid);
      }
    }
  }
}

// Usage
const limiter = new RateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxRequests: 100,
});

app.use('/api', limiter.middleware());

// Cleanup every 5 minutes
setInterval(() => limiter.cleanup(), 5 * 60 * 1000);
```

### Stream Pipeline Helper

```javascript
// Snippet: Stream Pipeline
// Category: Streams
// Tags: nodejs, streams, pipeline, files

const { pipeline } = require('stream');
const { promisify } = require('util');
const fs = require('fs');
const zlib = require('zlib');
const { Transform } = require('stream');

const pipelineAsync = promisify(pipeline);

// Custom transform stream
class LineCounter extends Transform {
  constructor(options) {
    super(options);
    this.lineCount = 0;
  }

  _transform(chunk, encoding, callback) {
    const lines = chunk.toString().split('\n').length - 1;
    this.lineCount += lines;
    this.push(chunk);
    callback();
  }
}

// Usage: Compress file and count lines
async function compressAndCount(inputFile, outputFile) {
  const counter = new LineCounter();

  await pipelineAsync(
    fs.createReadStream(inputFile),
    counter,
    zlib.createGzip(),
    fs.createWriteStream(outputFile)
  );

  console.log(`Processed ${counter.lineCount} lines`);
  return counter.lineCount;
}

// Usage: Process large CSV
async function processCsv(inputFile) {
  const processLine = new Transform({
    transform(chunk, encoding, callback) {
      const lines = chunk.toString().split('\n');
      const processed = lines
        .map(line => line.toUpperCase())
        .join('\n');
      callback(null, processed);
    }
  });

  await pipelineAsync(
    fs.createReadStream(inputFile),
    processLine,
    fs.createWriteStream('output.csv')
  );
}
```

## SQL Snippets

### Safe Upsert Pattern

```sql
-- Snippet: Upsert (Insert or Update)
-- Category: Database
-- Tags: sql, upsert, postgresql

-- PostgreSQL
INSERT INTO users (id, email, name, updated_at)
VALUES (1, 'user@example.com', 'John Doe', NOW())
ON CONFLICT (id)
DO UPDATE SET
  email = EXCLUDED.email,
  name = EXCLUDED.name,
  updated_at = NOW()
RETURNING *;

-- Multiple rows upsert
INSERT INTO products (sku, name, price)
VALUES
  ('SKU001', 'Product 1', 29.99),
  ('SKU002', 'Product 2', 39.99)
ON CONFLICT (sku)
DO UPDATE SET
  name = EXCLUDED.name,
  price = EXCLUDED.price,
  updated_at = NOW();
```

### Pagination Query

```sql
-- Snippet: Efficient Pagination
-- Category: Database
-- Tags: sql, pagination, performance

-- Offset-based (simple but slower for large offsets)
SELECT *
FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 40; -- Page 3

-- Cursor-based (more efficient)
SELECT *
FROM posts
WHERE created_at < '2024-01-01 12:00:00'
ORDER BY created_at DESC
LIMIT 20;

-- Keyset pagination (best performance)
SELECT *
FROM posts
WHERE (created_at, id) < ('2024-01-01 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

## Best Practices

### Snippet Organization
- **Consistent naming**: Use clear, descriptive names
- **Comprehensive tags**: Add multiple relevant tags
- **Version tracking**: Keep track of snippet versions
- **Dependencies**: Document required libraries

### Documentation
- **Usage examples**: Show real-world usage
- **Parameter docs**: Document all parameters
- **Edge cases**: Mention limitations and edge cases
- **Alternatives**: Suggest related patterns

### Maintenance
- **Regular review**: Update snippets periodically
- **Test snippets**: Ensure snippets still work
- **Deprecation**: Mark outdated snippets
- **Contribution**: Share useful snippets with team

## Snippet Management Tools

### File-based Storage
```
snippets/
├── javascript/
│   ├── async/
│   │   ├── retry.js
│   │   └── debounce.js
│   └── react/
│       ├── hooks/
│       └── components/
├── python/
│   ├── decorators/
│   └── context-managers/
└── sql/
    ├── queries/
    └── migrations/
```

### Metadata Format (frontmatter)
```yaml
---
title: "Async Retry with Backoff"
language: javascript
category: error-handling
tags: [async, retry, error-handling, resilience]
framework: nodejs
version: 1.2.0
author: team
created: 2024-01-15
updated: 2024-01-20
---
```

## Notes

- Keep snippets focused and single-purpose
- Include error handling in examples
- Document performance characteristics
- Test snippets before saving
- Use consistent coding style
- Add comments for complex logic
- Version snippets when making changes
- Share snippets within team
- Regular cleanup of outdated snippets
