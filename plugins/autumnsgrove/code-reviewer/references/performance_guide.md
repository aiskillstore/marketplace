# Performance Optimization Guide

Comprehensive guide for identifying and fixing performance issues during code review.

## Table of Contents

1. [Algorithm Efficiency](#algorithm-efficiency)
2. [Database Optimization](#database-optimization)
3. [Memory Management](#memory-management)
4. [Network & I/O](#network--io)
5. [Caching Strategies](#caching-strategies)
6. [Concurrency & Parallelism](#concurrency--parallelism)
7. [Language-Specific Optimizations](#language-specific-optimizations)

---

## Algorithm Efficiency

### Big-O Analysis

**❌ Inefficient - O(n²):**
```python
# Nested loops checking duplicates
def has_duplicates(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False
```

**✅ Optimized - O(n):**
```python
# Using set for O(1) lookup
def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False

# Even simpler
def has_duplicates(items):
    return len(items) != len(set(items))
```

### Common Optimizations

**Linear Search → Binary Search**
```python
# ❌ O(n) - Linear search
def find_item(sorted_list, target):
    for i, item in enumerate(sorted_list):
        if item == target:
            return i
    return -1

# ✅ O(log n) - Binary search
import bisect
def find_item(sorted_list, target):
    index = bisect.bisect_left(sorted_list, target)
    if index < len(sorted_list) and sorted_list[index] == target:
        return index
    return -1
```

**List Comprehension vs Loop**
```python
# ❌ Slower - Building list with append
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * 2)

# ✅ Faster - List comprehension
result = [i * 2 for i in range(1000) if i % 2 == 0]

# ✅ Even better for large datasets - Generator
result = (i * 2 for i in range(1000000) if i % 2 == 0)
```

**Unnecessary Sorting**
```python
# ❌ O(n log n) - Full sort to find max
def find_max(items):
    return sorted(items)[-1]

# ✅ O(n) - Direct max
def find_max(items):
    return max(items)
```

---

## Database Optimization

### N+1 Query Problem

**❌ N+1 Queries:**
```python
# SQLAlchemy - Lazy loading causes N+1
users = User.query.all()  # 1 query
for user in users:
    print(user.orders)  # N queries!
```

**✅ Eager Loading:**
```python
# SQLAlchemy - Eager loading with joinedload
from sqlalchemy.orm import joinedload

users = User.query.options(joinedload(User.orders)).all()  # 1 query
for user in users:
    print(user.orders)  # No additional queries
```

### SELECT * Optimization

**❌ Selecting All Columns:**
```sql
-- Returns 50+ columns, only need 3
SELECT * FROM users WHERE status = 'active';
```

**✅ Specific Columns:**
```sql
-- Only select needed columns
SELECT id, name, email FROM users WHERE status = 'active';
```

```python
# SQLAlchemy - Specify columns
users = db.session.query(User.id, User.name, User.email)\
    .filter_by(status='active').all()
```

### Index Usage

**❌ Missing Index:**
```sql
-- Slow full table scan
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
-- No index on (user_id, status)
```

**✅ Proper Indexing:**
```sql
-- Create composite index (order matters!)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Now fast index scan
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
```

**Index Guidelines:**
- Index columns used in WHERE clauses
- Index foreign keys
- Composite indexes: most selective column first
- Don't over-index (impacts writes)

### Query Optimization

**❌ Inefficient Subquery:**
```sql
-- Correlated subquery runs for each row
SELECT name,
       (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as order_count
FROM users;
```

**✅ JOIN Instead:**
```sql
-- Single query with JOIN
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

### Pagination

**❌ Loading All Records:**
```python
# Loads entire table into memory
all_users = User.query.all()
return jsonify([u.to_dict() for u in all_users])
```

**✅ Pagination:**
```python
# Load only requested page
page = request.args.get('page', 1, type=int)
per_page = 20

users = User.query.paginate(page=page, per_page=per_page, error_out=False)
return jsonify({
    'items': [u.to_dict() for u in users.items],
    'total': users.total,
    'page': page,
    'pages': users.pages
})
```

---

## Memory Management

### Memory Leaks

**❌ Unclosed Resources:**
```python
# File handle not closed
def read_file(filename):
    f = open(filename)
    data = f.read()
    return data  # File left open!
```

**✅ Proper Resource Management:**
```python
# Context manager ensures cleanup
def read_file(filename):
    with open(filename) as f:
        data = f.read()
    return data  # File closed automatically
```

### Large Data Processing

**❌ Loading Everything into Memory:**
```python
# Loads 10GB file into memory
with open('large_file.csv') as f:
    lines = f.readlines()  # All lines in memory!
    for line in lines:
        process(line)
```

**✅ Streaming/Chunking:**
```python
# Process line by line
with open('large_file.csv') as f:
    for line in f:  # One line at a time
        process(line)

# Or use pandas chunking
import pandas as pd
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process(chunk)
```

### Object Pooling

**❌ Creating New Objects Repeatedly:**
```python
def process_requests():
    for request in requests:
        connection = create_db_connection()  # New connection each time
        result = connection.query(request)
        connection.close()
```

**✅ Connection Pooling:**
```python
from sqlalchemy import create_engine, pool

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20
)

def process_requests():
    with engine.connect() as connection:
        for request in requests:
            result = connection.execute(request)
```

---

## Network & I/O

### Asynchronous Operations

**❌ Blocking Synchronous Calls:**
```python
import requests

def fetch_all_data(urls):
    results = []
    for url in urls:
        response = requests.get(url)  # Blocks for each request
        results.append(response.json())
    return results
```

**✅ Async/Concurrent:**
```python
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_all_data(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

# Or using ThreadPoolExecutor for requests
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_url(url):
    return requests.get(url).json()

def fetch_all_data(urls):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_url, urls))
    return results
```

### Timeout Configuration

**❌ No Timeout:**
```python
# Can hang indefinitely
response = requests.get('https://api.example.com/data')
```

**✅ Timeouts Configured:**
```python
# Connection timeout: 3s, Read timeout: 10s
response = requests.get(
    'https://api.example.com/data',
    timeout=(3, 10)
)
```

### Batch Operations

**❌ Individual API Calls:**
```python
# Makes 1000 API calls
for item_id in item_ids:
    api.get(f'/items/{item_id}')
```

**✅ Batch Endpoint:**
```python
# Single API call with batch
api.post('/items/batch', json={'ids': item_ids})
```

---

## Caching Strategies

### Function Memoization

**❌ Recalculating:**
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Exponential time!
```

**✅ Memoization:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Now O(n)
```

### Application-Level Caching

**❌ No Caching:**
```python
@app.route('/popular-products')
def popular_products():
    # Expensive query runs every request
    products = db.session.query(Product)\
        .join(OrderItem)\
        .group_by(Product.id)\
        .order_by(func.count(OrderItem.id).desc())\
        .limit(10)\
        .all()
    return jsonify([p.to_dict() for p in products])
```

**✅ Redis Caching:**
```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/popular-products')
def popular_products():
    # Check cache first
    cached = cache.get('popular_products')
    if cached:
        return cached

    # Query if not cached
    products = db.session.query(Product)\
        .join(OrderItem)\
        .group_by(Product.id)\
        .order_by(func.count(OrderItem.id).desc())\
        .limit(10)\
        .all()

    result = jsonify([p.to_dict() for p in products])

    # Cache for 5 minutes
    cache.setex('popular_products', 300, result.get_data())

    return result
```

### Cache Invalidation

```python
# Invalidate cache on update
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.update(request.json)
    db.session.commit()

    # Invalidate related caches
    cache.delete('popular_products')
    cache.delete(f'product:{product_id}')

    return jsonify(product.to_dict())
```

---

## Concurrency & Parallelism

### Thread Pool for I/O-Bound Tasks

**❌ Sequential Processing:**
```python
def process_images(image_paths):
    results = []
    for path in image_paths:
        result = download_and_resize(path)  # I/O bound
        results.append(result)
    return results
```

**✅ Thread Pool:**
```python
from concurrent.futures import ThreadPoolExecutor

def process_images(image_paths):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_and_resize, image_paths))
    return results
```

### Process Pool for CPU-Bound Tasks

**❌ Single Process:**
```python
def analyze_data(datasets):
    results = []
    for data in datasets:
        result = heavy_computation(data)  # CPU intensive
        results.append(result)
    return results
```

**✅ Process Pool:**
```python
from multiprocessing import Pool

def analyze_data(datasets):
    with Pool(processes=4) as pool:
        results = pool.map(heavy_computation, datasets)
    return results
```

---

## Language-Specific Optimizations

### Python

**String Concatenation:**
```python
# ❌ Slow - Creates new string each iteration
result = ""
for item in items:
    result += str(item)  # O(n²)

# ✅ Fast - Join is O(n)
result = "".join(str(item) for item in items)
```

**Dictionary Lookups:**
```python
# ❌ Checking key multiple times
if 'key' in my_dict:
    value = my_dict['key']

# ✅ EAFP (Easier to Ask Forgiveness than Permission)
try:
    value = my_dict['key']
except KeyError:
    value = default

# ✅ Or use get()
value = my_dict.get('key', default)
```

**List vs Set Membership:**
```python
# ❌ O(n) - List membership test
valid_ids = [1, 2, 3, 4, 5, ..., 10000]
if user_id in valid_ids:  # Slow for large lists
    process()

# ✅ O(1) - Set membership test
valid_ids = {1, 2, 3, 4, 5, ..., 10000}
if user_id in valid_ids:  # Fast
    process()
```

### JavaScript

**Array Operations:**
```javascript
// ❌ Mutating array in place inefficiently
let filtered = [];
for (let i = 0; i < items.length; i++) {
    if (items[i].active) {
        filtered.push(items[i]);
    }
}

// ✅ Use built-in methods
let filtered = items.filter(item => item.active);
```

**Object Lookup:**
```javascript
// ❌ Array.find for repeated lookups
users.forEach(user => {
    const department = departments.find(d => d.id === user.deptId);  // O(n) each time
});

// ✅ Create lookup map
const deptMap = new Map(departments.map(d => [d.id, d]));
users.forEach(user => {
    const department = deptMap.get(user.deptId);  // O(1)
});
```

### Go

**Preallocate Slices:**
```go
// ❌ Growing slice incrementally
var items []Item
for i := 0; i < 1000; i++ {
    items = append(items, generateItem(i))  // Multiple reallocations
}

// ✅ Preallocate capacity
items := make([]Item, 0, 1000)
for i := 0; i < 1000; i++ {
    items = append(items, generateItem(i))  // No reallocation
}
```

---

## Performance Profiling

### Python Profiling

```python
import cProfile
import pstats

# Profile a function
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = expensive_function()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

# Line profiler for detailed analysis
# Install: pip install line_profiler
# Usage: kernprof -l -v script.py
@profile
def expensive_function():
    # Code here
    pass
```

### Memory Profiling

```python
# Install: pip install memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    large_list = [i for i in range(10000000)]
    return sum(large_list)
```

---

## Quick Performance Checklist

- [ ] No O(n²) or worse algorithms when better exists
- [ ] Database queries are indexed
- [ ] No N+1 query problems
- [ ] Pagination for large datasets
- [ ] Resources properly closed (files, connections)
- [ ] Async/concurrent for I/O operations
- [ ] Appropriate caching strategy
- [ ] No blocking operations in hot paths
- [ ] Connection pooling configured
- [ ] Timeouts set for network calls
- [ ] Batch operations where possible
- [ ] Memory-efficient data structures chosen
- [ ] Profiling done for critical paths

---

*Always measure before optimizing. Use profiling tools to identify actual bottlenecks.*
