---
name: Backend Fundamentals
description: Auto-invoke when reviewing API routes, server logic, Express/Node.js code, or backend architecture. Enforces REST conventions, middleware patterns, and separation of concerns.
---

# Backend Fundamentals Review

> "APIs are contracts. Break them, and you break trust."

## When to Apply

Activate this skill when reviewing:
- API route handlers
- Express/Fastify/Hono middleware
- Database queries and models
- Authentication/authorization logic
- Server-side business logic

---

## Review Checklist

### API Design

- [ ] **RESTful**: Do routes follow REST conventions? (GET for read, POST for create, etc.)
- [ ] **Naming**: Are endpoints nouns, not verbs? (`/users` not `/getUsers`)
- [ ] **Versioning**: Is API versioned for future changes? (`/api/v1/`)
- [ ] **Status Codes**: Are correct HTTP status codes returned?

### Separation of Concerns

- [ ] **Routes**: Do routes only handle HTTP concerns (req/res)?
- [ ] **Controllers**: Is business logic in controllers/services, not routes?
- [ ] **Services**: Is data access abstracted from business logic?
- [ ] **Models**: Are models responsible only for data shape/validation?

### Error Handling

- [ ] **Try/Catch**: Are async operations wrapped properly?
- [ ] **Error Responses**: Are errors returned with proper status codes?
- [ ] **Logging**: Are errors logged with context?
- [ ] **No Leaks**: Are internal errors hidden from clients?

### Security

- [ ] **Input Validation**: Is ALL input validated before use?
- [ ] **Authentication**: Are protected routes actually protected?
- [ ] **Authorization**: Can users only access their own data?
- [ ] **Rate Limiting**: Are endpoints protected from abuse?

---

## Common Mistakes (Anti-Patterns)

### 1. Fat Routes
```
❌ app.post('/users', async (req, res) => {
     // 100 lines of validation, business logic, DB queries
   });

✅ app.post('/users', validateUser, userController.create);
```

### 2. No Input Validation
```
❌ const { email } = req.body;
   await db.query(`SELECT * FROM users WHERE email = '${email}'`);

✅ const { email } = validateBody(req.body, userSchema);
   await User.findByEmail(email); // parameterized
```

### 3. Wrong Status Codes
```
❌ res.status(200).json({ error: 'Not found' });

✅ res.status(404).json({ error: 'User not found' });
```

### 4. Leaking Internal Errors
```
❌ catch (error) {
     res.status(500).json({ error: error.message, stack: error.stack });
   }

✅ catch (error) {
     logger.error('User creation failed', { error, userId });
     res.status(500).json({ error: 'Something went wrong' });
   }
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Architecture**: "If I wanted to switch from Express to Fastify, what would need to change?"
2. **Validation**: "What happens if someone sends malformed JSON?"
3. **Auth**: "How do you know this user owns this resource?"
4. **Errors**: "What does the client see when the database is down?"
5. **Testing**: "How would you test this endpoint in isolation?"

---

## HTTP Status Code Reference

| Code | When to Use |
|------|-------------|
| 200 | Success (with body) |
| 201 | Created (after POST) |
| 204 | Success (no content, after DELETE) |
| 400 | Bad request (validation failed) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (logged in but not allowed) |
| 404 | Not found |
| 409 | Conflict (duplicate resource) |
| 500 | Server error (hide details from client) |

---

## Architecture Layers

```
Request → Route → Controller → Service → Repository → Database
                     ↓
              Middleware (auth, validation, logging)
```

| Layer | Responsibility |
|-------|----------------|
| Route | HTTP verbs, paths, middleware chain |
| Controller | Request/response handling, calling services |
| Service | Business logic, orchestration |
| Repository | Data access, queries |

---

## Red Flags to Call Out

| Flag | Question to Ask |
|------|-----------------|
| SQL in route handler | "Should data access be in a separate layer?" |
| No try/catch on async | "What happens if this fails?" |
| req.body used directly | "What if someone sends unexpected fields?" |
| Hardcoded secrets | "How would this work in production?" |
| No pagination on list endpoints | "What if there are 10,000 records?" |
