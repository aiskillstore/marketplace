# Common Error Patterns Catalog

This catalog provides quick reference for frequent error patterns, their causes, and solutions.

## Python Errors

### AttributeError: 'NoneType' object has no attribute 'X'

**Pattern:**
```python
user.profile.name  # AttributeError if user.profile is None
```

**Common Causes:**
- Function returned None instead of expected object
- Database query found no results
- Optional relationship not populated
- API returned null

**Quick Fixes:**
```python
# Option 1: Null check
if user.profile:
    name = user.profile.name

# Option 2: Default value
name = user.profile.name if user.profile else "Anonymous"

# Option 3: getattr with default
name = getattr(user.profile, 'name', 'Anonymous')

# Option 4: Optional chaining (Python 3.10+)
# Not available yet, use walrus operator
if (profile := user.profile):
    name = profile.name
```

---

### KeyError: 'key'

**Pattern:**
```python
value = data['missing_key']  # KeyError
```

**Common Causes:**
- Expected key missing from dictionary
- Typo in key name
- API response structure changed
- JSON parsing incomplete

**Quick Fixes:**
```python
# Option 1: .get() with default
value = data.get('key', default_value)

# Option 2: Check before access
if 'key' in data:
    value = data['key']

# Option 3: Try/except
try:
    value = data['key']
except KeyError:
    value = default_value

# Option 4: defaultdict
from collections import defaultdict
data = defaultdict(lambda: 'default')
```

---

### IndexError: list index out of range

**Pattern:**
```python
item = items[5]  # IndexError if len(items) <= 5
```

**Common Causes:**
- Empty list
- Off-by-one error in loop
- Assuming minimum list size
- Incorrect slice indices

**Quick Fixes:**
```python
# Option 1: Check length
if len(items) > 5:
    item = items[5]

# Option 2: Try/except
try:
    item = items[5]
except IndexError:
    item = None

# Option 3: Use get-like pattern
def safe_get(lst, idx, default=None):
    try:
        return lst[idx]
    except IndexError:
        return default

item = safe_get(items, 5)

# Option 4: Slice (never raises IndexError)
item = items[5:6]  # Returns [] if out of range
item = item[0] if item else None
```

---

### TypeError: unsupported operand type(s) for +: 'int' and 'str'

**Pattern:**
```python
result = 5 + "10"  # TypeError
```

**Common Causes:**
- Type mismatch in operation
- Missing type conversion
- Wrong type from user input or API
- Variable reused with different type

**Quick Fixes:**
```python
# Option 1: Explicit conversion
result = 5 + int("10")  # 15
result = str(5) + "10"  # "510"

# Option 2: Type checking
def add_values(a, b):
    if isinstance(a, str):
        a = int(a)
    if isinstance(b, str):
        b = int(b)
    return a + b

# Option 3: Safe conversion
def to_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
```

---

### ImportError / ModuleNotFoundError: No module named 'X'

**Pattern:**
```python
import missing_module  # ModuleNotFoundError
```

**Common Causes:**
- Module not installed
- Wrong virtual environment
- Typo in module name
- Module name conflict
- PYTHONPATH issues

**Quick Fixes:**
```bash
# Install missing module
pip install module_name

# Check installed packages
pip list | grep module

# Install from requirements
pip install -r requirements.txt

# Reinstall in current environment
python -m pip install module_name

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

---

### RecursionError: maximum recursion depth exceeded

**Pattern:**
```python
def factorial(n):
    return n * factorial(n - 1)  # No base case!
```

**Common Causes:**
- Missing base case in recursion
- Infinite recursion
- Very deep recursion (>1000 levels)
- Circular references

**Quick Fixes:**
```python
# Option 1: Add base case
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Option 2: Increase limit (careful!)
import sys
sys.setrecursionlimit(10000)

# Option 3: Use iteration instead
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# Option 4: Use tail recursion with trampoline
def factorial(n, acc=1):
    if n <= 1:
        return acc
    return lambda: factorial(n - 1, n * acc)
```

## JavaScript/TypeScript Errors

### TypeError: Cannot read property 'X' of undefined

**Pattern:**
```javascript
user.profile.name  // TypeError if user.profile is undefined
```

**Common Causes:**
- Variable not initialized
- Async data not loaded yet
- API returned null/undefined
- Destructuring failed

**Quick Fixes:**
```javascript
// Option 1: Optional chaining (ES2020)
const name = user?.profile?.name;

// Option 2: Logical AND
const name = user && user.profile && user.profile.name;

// Option 3: Default values
const name = user?.profile?.name || 'Anonymous';

// Option 4: Nullish coalescing
const name = user?.profile?.name ?? 'Anonymous';

// Option 5: Guard clause
if (!user || !user.profile) {
    return;
}
const name = user.profile.name;
```

---

### ReferenceError: X is not defined

**Pattern:**
```javascript
console.log(undeclaredVariable);  // ReferenceError
```

**Common Causes:**
- Variable used before declaration
- Typo in variable name
- Scope issue (var/let/const)
- Missing import

**Quick Fixes:**
```javascript
// Option 1: Declare variable
let variableName = value;

// Option 2: Import if from module
import { variableName } from './module';

// Option 3: Check for existence
if (typeof variableName !== 'undefined') {
    console.log(variableName);
}

// Option 4: Use window for globals (browser)
if ('variableName' in window) {
    console.log(window.variableName);
}
```

---

### Uncaught (in promise) Error

**Pattern:**
```javascript
async function fetchData() {
    const response = await fetch(url);
    const data = await response.json();  // Might reject!
    return data;
}
// Calling without try/catch or .catch()
```

**Common Causes:**
- Missing error handler for promises
- Unhandled async/await exceptions
- No .catch() on promise chain
- Network request failure

**Quick Fixes:**
```javascript
// Option 1: Try/catch with async/await
async function fetchData() {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch failed:', error);
        throw error;  // Or handle gracefully
    }
}

// Option 2: .catch() on promise
fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));

// Option 3: Global handler
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
});

// Option 4: Wrapper function
const safeAsync = (fn) => {
    return async (...args) => {
        try {
            return await fn(...args);
        } catch (error) {
            console.error('Async error:', error);
            return null;
        }
    };
};
```

---

### SyntaxError: Unexpected token

**Pattern:**
```javascript
const data = JSON.parse(invalidJSON);  // SyntaxError
```

**Common Causes:**
- Invalid JSON format
- Missing quotes in JSON
- Trailing commas in JSON
- Single quotes instead of double quotes
- Malformed code structure

**Quick Fixes:**
```javascript
// Option 1: Validate JSON before parsing
function safeParseJSON(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        console.error('Invalid JSON:', e);
        return null;
    }
}

// Option 2: Check JSON validity
function isValidJSON(str) {
    try {
        JSON.parse(str);
        return true;
    } catch (e) {
        return false;
    }
}

// Option 3: Use a JSON validator library
// npm install jsonlint
const jsonlint = require('jsonlint');
jsonlint.parse(jsonString);

// For code syntax errors: Use linter
// npm install eslint
```

---

### Maximum call stack size exceeded

**Pattern:**
```javascript
function infinite() {
    infinite();  // No base case!
}
```

**Common Causes:**
- Infinite recursion
- Missing base case
- Circular object references
- Very deep recursion

**Quick Fixes:**
```javascript
// Option 1: Add base case
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Option 2: Use iteration
function factorial(n) {
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// Option 3: Trampoline for tail recursion
function trampoline(fn) {
    while (typeof fn === 'function') {
        fn = fn();
    }
    return fn;
}

function factorial(n, acc = 1) {
    if (n <= 1) return acc;
    return () => factorial(n - 1, n * acc);
}

const result = trampoline(factorial(5));
```

## Java Errors

### NullPointerException

**Pattern:**
```java
String name = user.getName();  // NPE if user is null
```

**Common Causes:**
- Null object reference
- Method called on null
- Uninitialized variable
- Failed object creation

**Quick Fixes:**
```java
// Option 1: Null check
if (user != null) {
    String name = user.getName();
}

// Option 2: Objects.requireNonNull
Objects.requireNonNull(user, "User cannot be null");
String name = user.getName();

// Option 3: Optional (Java 8+)
Optional<User> userOpt = Optional.ofNullable(user);
String name = userOpt.map(User::getName).orElse("Unknown");

// Option 4: Ternary operator
String name = (user != null) ? user.getName() : "Unknown";

// Option 5: @Nullable and @NotNull annotations
public String getName(@NotNull User user) {
    return user.getName();
}
```

---

### ClassCastException

**Pattern:**
```java
String str = (String) object;  // CCE if object is not String
```

**Common Causes:**
- Incorrect type cast
- Generic type erasure issues
- Wrong object returned from method
- Collection contains mixed types

**Quick Fixes:**
```java
// Option 1: instanceof check
if (object instanceof String) {
    String str = (String) object;
}

// Option 2: Use generics
List<String> list = new ArrayList<>();  // Type-safe

// Option 3: Pattern matching (Java 16+)
if (object instanceof String str) {
    // str is already String here
    System.out.println(str.toLowerCase());
}

// Option 4: Try/catch
try {
    String str = (String) object;
} catch (ClassCastException e) {
    // Handle wrong type
}
```

---

### ConcurrentModificationException

**Pattern:**
```java
for (String item : list) {
    list.remove(item);  // CME!
}
```

**Common Causes:**
- Modifying collection during iteration
- Multi-threaded access without synchronization
- Nested iteration modification

**Quick Fixes:**
```java
// Option 1: Use Iterator.remove()
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String item = it.next();
    if (shouldRemove(item)) {
        it.remove();  // Safe!
    }
}

// Option 2: Collect items to remove, then remove
List<String> toRemove = new ArrayList<>();
for (String item : list) {
    if (shouldRemove(item)) {
        toRemove.add(item);
    }
}
list.removeAll(toRemove);

// Option 3: Use removeIf (Java 8+)
list.removeIf(item -> shouldRemove(item));

// Option 4: CopyOnWriteArrayList for concurrent access
List<String> list = new CopyOnWriteArrayList<>();
// Can modify during iteration
```

---

### OutOfMemoryError: Java heap space

**Pattern:**
```
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
```

**Common Causes:**
- Memory leak
- Loading too much data at once
- Heap size too small
- Infinite loop creating objects

**Quick Fixes:**
```bash
# Option 1: Increase heap size
java -Xmx2g -Xms512m MyApp

# Option 2: Analyze heap dump
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heap.hprof MyApp

# Option 3: Use profiler (VisualVM, YourKit)
jvisualvm

# Code fixes:
# - Process data in batches
# - Close resources properly
# - Use weak references where appropriate
# - Clear collections when done
```

**Code Improvements:**
```java
// Bad: Load all at once
List<Record> records = database.findAll();  // Millions of records!

// Good: Process in batches
int pageSize = 1000;
for (int page = 0; ; page++) {
    List<Record> batch = database.findBatch(page, pageSize);
    if (batch.isEmpty()) break;

    processBatch(batch);
    batch.clear();  // Help GC
}

// Use try-with-resources
try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
    // Automatically closed
}
```

## Database Errors

### Connection Timeout / Connection Pool Exhausted

**Pattern:**
```
Caused by: java.sql.SQLTimeoutException: Connection is not available, request timed out after 30000ms
```

**Common Causes:**
- Too many concurrent connections
- Connections not closed properly
- Slow queries blocking pool
- Pool size too small

**Quick Fixes:**
```java
// Option 1: Always close connections
try (Connection conn = dataSource.getConnection()) {
    // Use connection
}  // Automatically returned to pool

// Option 2: Increase pool size (HikariCP)
hikari.setMaximumPoolSize(20);
hikari.setMinimumIdle(5);

// Option 3: Set reasonable timeouts
hikari.setConnectionTimeout(30000);
hikari.setIdleTimeout(600000);
hikari.setMaxLifetime(1800000);

// Option 4: Monitor and fix slow queries
// Add indexes, optimize queries

// Option 5: Use query timeout
Statement stmt = conn.createStatement();
stmt.setQueryTimeout(10);  // 10 seconds
```

---

### Deadlock Detected

**Pattern:**
```
Deadlock detected during wait for locking: transaction A waits for transaction B; transaction B waits for transaction A
```

**Common Causes:**
- Circular wait conditions
- Different lock ordering
- Long-running transactions
- Pessimistic locking

**Quick Fixes:**
```java
// Option 1: Consistent lock ordering
// Always acquire locks in same order
synchronized(lockA) {
    synchronized(lockB) {
        // Work
    }
}

// Option 2: Use timeout with tryLock
Lock lock1 = new ReentrantLock();
Lock lock2 = new ReentrantLock();

if (lock1.tryLock(1, TimeUnit.SECONDS)) {
    try {
        if (lock2.tryLock(1, TimeUnit.SECONDS)) {
            try {
                // Work
            } finally {
                lock2.unlock();
            }
        }
    } finally {
        lock1.unlock();
    }
}

// Option 3: Optimistic locking with version
@Entity
public class Account {
    @Version
    private Long version;
    // ...
}

// Option 4: Reduce transaction scope
// Keep transactions as short as possible
```

## Network/API Errors

### 404 Not Found

**Common Causes:**
- Wrong URL or endpoint
- Resource deleted
- Route not registered
- Typo in path

**Quick Fixes:**
```javascript
// Check URL construction
const url = `${baseUrl}/api/users/${userId}`;
console.log('Requesting:', url);

// Handle 404 gracefully
fetch(url)
    .then(response => {
        if (response.status === 404) {
            console.log('Resource not found');
            return null;
        }
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    });

// Server-side: Verify route
app.get('/api/users/:id', handler);  // Is this registered?
```

---

### 500 Internal Server Error

**Common Causes:**
- Unhandled exception on server
- Database connection failure
- Configuration error
- Null pointer in server code

**Quick Fixes:**
```python
# Add global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return {
        'error': 'Internal server error',
        'message': str(e) if app.debug else 'An error occurred'
    }, 500

# Client: Retry with exponential backoff
async function fetchWithRetry(url, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                return await response.json();
            }
            if (response.status >= 500 && i < retries - 1) {
                await sleep(Math.pow(2, i) * 1000);
                continue;
            }
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            if (i === retries - 1) throw error;
            await sleep(Math.pow(2, i) * 1000);
        }
    }
}
```

---

### CORS Error

**Pattern:**
```
Access to fetch at 'https://api.example.com' from origin 'https://app.example.com' has been blocked by CORS policy
```

**Common Causes:**
- Missing CORS headers
- Wrong origin in CORS config
- Preflight request failing
- Credentials without proper headers

**Quick Fixes:**
```python
# Python (Flask)
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://app.example.com'])

# Or specific route
@app.route('/api/data')
@cross_origin(origins=['https://app.example.com'])
def get_data():
    return jsonify(data)

# Express.js
const cors = require('cors');
app.use(cors({
    origin: 'https://app.example.com',
    credentials: true
}));

# Nginx
add_header 'Access-Control-Allow-Origin' 'https://app.example.com';
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
```

## Quick Reference Table

| Error | Primary Cause | First Check | Quick Fix |
|-------|--------------|-------------|-----------|
| NullPointerException | Null reference | Variable initialization | Add null check |
| AttributeError | None object | Function return value | Use getattr() or check |
| KeyError | Missing dict key | Key spelling | Use .get() |
| IndexError | Out of bounds | List length | Check len() first |
| TypeError | Type mismatch | Variable types | Convert types |
| 404 Not Found | Wrong URL | URL construction | Verify endpoint |
| 500 Server Error | Server exception | Server logs | Add error handler |
| CORS Error | Missing headers | CORS config | Add CORS middleware |
| Connection Timeout | Pool exhausted | Connection closing | Use try-with-resources |
| Memory Error | Heap overflow | Memory usage | Process in batches |
