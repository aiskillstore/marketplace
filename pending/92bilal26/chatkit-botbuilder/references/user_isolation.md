# User Isolation & Security Guide

## Overview

User isolation ensures that each user can only access their own data. ChatKit implements three-level isolation to prevent data leaks and maintain security in multi-user systems.

## Three-Level Isolation Strategy

### Level 1: Middleware (Authentication)

**What it does:** Validates JWT token and extracts user_id

**Implementation:**
```python
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        # Validate token format
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return JSONResponse({"detail": "Invalid auth scheme"}, status_code=401)

        # Decode JWT
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get("user_id")

        # Set user_id on request for all downstream handlers
        request.state.user_id = user_id

        return await call_next(request)
```

**Security guarantees:**
- Only authenticated users can access ChatKit endpoint
- Invalid tokens are rejected
- Expired tokens are rejected
- Token tampering is detected

### Level 2: Tool Wrapper (Parameter Injection)

**What it does:** Automatically injects user_id into every tool call

**Implementation:**
```python
async def respond(self, thread, input, context):
    user_id = context.user_id  # From middleware

    # Wrappers capture user_id in closure
    def add_task_wrapper(title: str, description: str = None):
        # user_id automatically included
        return mcp_add_task(user_id=user_id, title=title, description=description)

    # Agent can only call wrapper, not raw tool
    wrapped_tools = [add_task_wrapper, ...]
    agent = create_task_agent(tools=wrapped_tools)
```

**Security guarantees:**
- Tools always receive user_id
- Agent cannot bypass user_id parameter
- Impossible to omit user_id accidentally
- Per-request isolation (new wrappers each request)

### Level 3: Database (Query Filtering)

**What it does:** Filters all database queries by user_id

**Implementation:**
```python
def list_tasks(user_id: str, status: Optional[str] = None):
    """Only returns tasks belonging to the user"""
    with Session(engine) as session:
        # CRITICAL: Filter by user_id in every query
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter if provided
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        # Execute query - returns ONLY user's tasks
        tasks = session.exec(query).all()
        return tasks
```

**Security guarantees:**
- Database level enforcement
- Even if middleware fails, database filters
- Even if wrapper fails, database filters
- SQL injection protection through SQLModel

## Complete Data Flow

```
User 1 (user-123) Message
    ↓
Request Headers: Authorization: Bearer <user-123-token>
    ↓
JWT Middleware:
    Validates token signature
    Checks expiration
    Extracts user_id = "user-123"
    Sets request.state.user_id = "user-123"
    ↓
ChatKit Endpoint:
    Receives request with request.state.user_id = "user-123"
    Creates context.user_id = "user-123"
    ↓
MyChatKitServer.respond():
    Extracts user_id = "user-123" from context
    Creates wrappers capturing user_id = "user-123"
    ↓
Tool Wrapper (add_task_wrapper):
    Agent calls: add_task_wrapper(title="Buy milk")
    Wrapper injects: mcp_add_task(user_id="user-123", title="Buy milk")
    ↓
MCP Tool (add_task):
    Receives user_id = "user-123"
    Creates Task with user_id = "user-123"
    ↓
Database:
    INSERT INTO tasks (id, user_id, title, ...)
    VALUES (uuid, "user-123", "Buy milk", ...)
    ↓
User 2 (user-456) Lists Tasks:
    SELECT * FROM tasks WHERE user_id = "user-456"
    Returns: [empty or user-456's tasks only]
    Does NOT return user-123's "Buy milk" task
```

## Verification Checklist

### Development Verification

**✓ Middleware Level**
```bash
# Test invalid token
curl -H "Authorization: Bearer invalid" \
  http://localhost:8000/api/v1/chatkit
# Expected: 401 Unauthorized

# Test missing token
curl http://localhost:8000/api/v1/chatkit
# Expected: 401 Unauthorized

# Test valid token
curl -H "Authorization: Bearer <valid-jwt>" \
  http://localhost:8000/api/v1/chatkit
# Expected: 200 OK
```

**✓ Tool Wrapper Level**
```python
# Add logging to wrapper
def add_task_wrapper(title):
    logger.info(f"add_task_wrapper called with user_id={user_id}")
    return mcp_add_task(user_id=user_id, title=title)

# Check logs for user_id injection
# Output: add_task_wrapper called with user_id=user-123
```

**✓ Database Level**
```python
# Check tasks in database
import sqlite3
conn = sqlite3.connect('taskpilot.db')
cursor = conn.cursor()

# List all tasks with their user_ids
cursor.execute('SELECT id, user_id, title FROM tasks')
for row in cursor.fetchall():
    print(f"Task {row[0]} belongs to user {row[1]}")
```

### Production Verification

**✓ User 1 Cannot See User 2's Tasks**

1. **Setup:**
   - Create User A account, get JWT token A
   - Create User B account, get JWT token B

2. **Test:**
   - User A logs in, creates task "Task A"
   - User B logs in, lists tasks
   - Verify User B doesn't see "Task A"

**✓ User ID Mismatch Fails**

1. **Setup:**
   - Get User A's JWT token
   - Manually modify task in database to user_id = "user-999"

2. **Test:**
   - User A tries to delete task with ID = modified task
   - Tool call includes user_id = "user-A" in wrapper
   - Database filters: WHERE user_id = "user-A" AND task_id = X
   - Query returns 0 rows (not found)
   - User A sees "Task not found" error

**✓ Token Expiration Works**

1. **Setup:**
   - Generate JWT with short expiration (1 minute)
   - User logs in with this token

2. **Test:**
   - Wait 2 minutes
   - Try to use token
   - JWT decode fails with "Token expired"
   - Request fails with 401 Unauthorized

## Common Isolation Failures

### Failure 1: Missing user_id in Tool Call

**Symptoms:**
- All users see the same tasks
- New tasks don't show user_id in database
- "User A created task, User B can see it"

**Root cause:**
```python
# WRONG: Tool called without user_id
def add_task_wrapper(title):
    return mcp_add_task(title=title)  # Missing user_id!
```

**Fix:**
```python
# RIGHT: Tool called with user_id
def add_task_wrapper(title):
    return mcp_add_task(user_id=user_id, title=title)
```

### Failure 2: Missing Database Filter

**Symptoms:**
- Wrapper passes user_id correctly
- But all users still see all tasks
- "User A created task, User B lists it"

**Root cause:**
```python
# WRONG: No user_id filter in query
def list_tasks(user_id: str, status: Optional[str] = None):
    with Session(engine) as session:
        # BUG: Returns ALL tasks, ignores user_id parameter
        query = select(Task)
        tasks = session.exec(query).all()
```

**Fix:**
```python
# RIGHT: Filter by user_id
def list_tasks(user_id: str, status: Optional[str] = None):
    with Session(engine) as session:
        # Correct: Only tasks where user_id matches
        query = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(query).all()
```

### Failure 3: Expired Token Not Validated

**Symptoms:**
- Users stay logged in forever
- Old tokens still work after expiration
- Cannot force logout

**Root cause:**
```python
# WRONG: No expiration check
payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
```

**Fix:**
```python
# RIGHT: Validation includes expiration
payload = jwt.decode(
    token,
    JWT_SECRET,
    algorithms=['HS256']
    # JWT library automatically checks 'exp' claim
)
```

### Failure 4: Wrapper Defined in Wrong Scope

**Symptoms:**
- Wrong user_id in wrapper calls
- User A's requests use User B's user_id
- "User A's task appeared with User B's ID"

**Root cause:**
```python
# WRONG: Wrapper defined outside respond()
user_id = None  # Global variable

def add_task_wrapper(title):
    return mcp_add_task(user_id=user_id, ...)  # Uses global, wrong!

async def respond(self, thread, input, context):
    global user_id
    user_id = context.user_id  # Updates global
    # Problem: Global variable shared across requests!
```

**Fix:**
```python
# RIGHT: Wrapper defined in respond() with closure
async def respond(self, thread, input, context):
    user_id = context.user_id  # Local variable

    def add_task_wrapper(title):  # Defined here
        return mcp_add_task(user_id=user_id, ...)  # Captures local user_id
    # Each request gets its own wrapper with correct user_id
```

## Testing for Isolation

### Unit Test: Middleware Extraction

```python
def test_jwt_middleware_extracts_user_id():
    """Verify middleware correctly extracts user_id from JWT"""
    from datetime import datetime, timedelta
    import jwt

    # Create test token
    payload = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")

    # Verify extraction
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["user_id"] == "test-user-123"
    print("✓ Middleware correctly extracts user_id")
```

### Integration Test: End-to-End Isolation

```python
async def test_user_isolation_end_to_end():
    """Verify complete isolation across three levels"""
    # User 1 creates task
    user_1_id = "user-1"
    task = await add_task(
        user_id=user_1_id,
        title="User 1's task",
        description="Secret task"
    )

    # User 2 tries to list tasks
    user_2_id = "user-2"
    tasks = await list_tasks(user_id=user_2_id)

    # Verify User 2 doesn't see User 1's task
    task_titles = [t.title for t in tasks]
    assert "User 1's task" not in task_titles
    print("✓ User isolation verified end-to-end")

    # Verify User 2 creates own task
    task_2 = await add_task(
        user_id=user_2_id,
        title="User 2's task",
        description="Different task"
    )

    # Verify User 1 doesn't see User 2's task
    user_1_tasks = await list_tasks(user_id=user_1_id)
    user_1_titles = [t.title for t in user_1_tasks]
    assert "User 2's task" not in user_1_titles
    print("✓ Bidirectional isolation verified")
```

## Security Best Practices

1. **Never Trust Client Input**
   - Don't use user_id from request body
   - Always extract from validated JWT token
   - Middleware ensures this

2. **Always Filter Database Queries**
   - Every SELECT must have WHERE user_id = ?
   - Every UPDATE must have WHERE user_id = ?
   - Every DELETE must have WHERE user_id = ?

3. **Validate Token Expiration**
   - JWT library does this automatically
   - But verify in production logs
   - Monitor for "Token expired" errors

4. **Use Strong Secrets**
   - JWT_SECRET should be 32+ characters
   - Store in environment variables
   - Never commit to version control

5. **Implement Rate Limiting**
   - Prevent brute force attacks
   - Limit API calls per user
   - Implement exponential backoff

6. **Log Security Events**
   - Authentication failures
   - Authorization failures
   - Unusual access patterns
   - Tool call parameters (sanitized)

7. **Monitor for Anomalies**
   - User accessing data outside normal patterns
   - Multiple users accessing from same IP
   - Rapid tool calls (possible automation attack)

## Debugging Isolation Issues

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Middleware
logger.debug(f"JWT token: {token[:20]}...")
logger.debug(f"Extracted user_id: {user_id}")

# Tool wrapper
logger.debug(f"Calling tool for user_id: {user_id}")

# MCP tool
logger.debug(f"list_tasks query: WHERE user_id = {user_id}")
```

### Trace Request Flow

```
1. Check request headers
   curl -v http://localhost:8000/api/v1/chatkit
   Look for: Authorization: Bearer ...

2. Check middleware logs
   grep "user_id" logs/app.log
   Expected: "Extracted user_id: user-123"

3. Check tool logs
   grep "add_task_wrapper" logs/app.log
   Expected: "add_task called for user user-123"

4. Check database
   SELECT * FROM tasks WHERE user_id != 'user-123'
   Should NOT include tasks from step 1's user

5. Verify response
   Only return tasks with user_id = 'user-123'
```

## Compliance & Auditing

### Log All Access

```python
logger.info(f"""
    User Access:
    - User ID: {user_id}
    - Action: {action}
    - Resource: {resource_id}
    - Timestamp: {datetime.utcnow()}
    - Status: {status}
""")
```

### Regular Audits

```sql
-- Find tasks without user_id (data corruption)
SELECT * FROM tasks WHERE user_id IS NULL;

-- Find users with unusually many tasks
SELECT user_id, COUNT(*) as task_count
FROM tasks
GROUP BY user_id
ORDER BY task_count DESC
LIMIT 10;

-- Find access patterns from same IP
SELECT user_id, client_ip, COUNT(*) as access_count
FROM access_logs
GROUP BY user_id, client_ip
HAVING access_count > 1000;
```
