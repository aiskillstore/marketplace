# MERN Full-Stack Critical Reference

## Auth Security (CRITICAL)

| Storage | Location | Config |
|---------|----------|--------|
| Access Token | Memory only (React state) | Never localStorage |
| Refresh Token | httpOnly cookie | `{ httpOnly: true, sameSite: 'strict', path: '/api/auth', secure: true }` |

### Token Refresh Anti-Pattern
```javascript
// BAD - Concurrent refresh calls
axios.interceptors.response.use(null, error => refreshToken())

// GOOD - Queue pattern
let isRefreshing = false, failedQueue = [];
// On 401: if refreshing, queue request; else refresh once, process queue
```

## API Anti-Patterns

| Issue | Bad | Fix |
|-------|-----|-----|
| Inconsistent response | `res.json(user)` | `res.json({ success: true, data: user })` |
| JWT in localStorage | `localStorage.setItem('token')` | Memory state only |
| Missing httpOnly | `res.cookie('token', val)` | Add `{ httpOnly: true, sameSite: 'strict' }` |
| Long access token | `expiresIn: '7d'` | `expiresIn: '15m'` max |
| No refresh queue | Concurrent refresh calls | Single refresh + queue |

## Type Mismatches (Frontend/Backend)

| Backend | Frontend Receives | Fix |
|---------|------------------|-----|
| `user._id` | `{ $oid: "..." }` | `user._id.toString()` |
| `new Date()` | `"2025-12-17T..."` | Type as `string`, convert client-side |
| `undefined` field | Missing property | Use `null` for optional fields |
| Empty array `[]` | Sometimes `null` | Coalesce: `arr || []` |

## State Sync Issues

### Optimistic Update Checklist
```javascript
onMutate: async (data) => {
  await queryClient.cancelQueries({ queryKey });          // 1. Cancel outgoing
  const prev = queryClient.getQueryData(queryKey);        // 2. Snapshot
  queryClient.setQueryData(queryKey, optimistic);         // 3. Update UI
  return { prev };                                        // 4. Context
},
onError: (err, vars, ctx) => {
  queryClient.setQueryData(queryKey, ctx.prev);           // 5. Rollback
},
onSettled: () => queryClient.invalidateQueries({ queryKey }) // 6. Refetch
```

### Cache Invalidation Matrix

| Operation | Invalidate | Direct Update | Reason |
|-----------|-----------|---------------|--------|
| Create | List queries | No | Unknown position |
| Update | No | Single + List | Known structure |
| Delete | No | Filter out | Known ID |
| Bulk | All related | No | Too many items |

### React Query Pitfalls

| Bad | Fix |
|-----|-----|
| `queryKey: ['users', { role }]` | `queryKey: ['users', role]` (flatten) |
| No `enabled` when params undefined | `enabled: !!userId` |
| Object params without stable keys | Flatten or `JSON.stringify` |

## File Upload Security

| Check | Implementation |
|-------|---------------|
| MIME type | Validate in `fileFilter` |
| File extension | Check against whitelist |
| File content | Validate magic bytes |
| Size limit | `limits: { fileSize: 5MB, files: 1 }` |
| Namespace | `uploads/${userId}/${Date.now()}-${filename}` |

### S3 Presigned Upload
```javascript
// Backend: Generate URL with ContentType enforcement
// Frontend: PUT with matching Content-Type header
```

## Error Handling

### Backend Error Map

| Mongoose Error | Status | Code | Action |
|----------------|--------|------|--------|
| ValidationError | 400 | VALIDATION_ERROR | Return field errors `[{field, message}]` |
| CastError | 400 | INVALID_ID | Generic message |
| 11000 duplicate | 409 | DUPLICATE | Field conflict |
| TokenExpiredError | 401 | TOKEN_EXPIRED | Trigger refresh |

### Frontend Error Pattern
```javascript
// Check error.code, NOT messages
if (error.code === 'VALIDATION_ERROR') error.errors.forEach(...)
else if (error.code === 'UNAUTHORIZED') logout()
```

## N+1 Query Anti-Patterns

| Bad | Fix |
|-----|-----|
| Frontend: `userIds.map(id => api.get(id))` | `api.list({ userIds: ids.join(',') })` |
| Backend: Loop with `await Model.find()` | Single query with `$in`, group results |

## WebSocket + React Query Sync

```javascript
socket.on('post:created', (post) => {
  queryClient.setQueryData(['posts'], (old) => [post, ...old]);
});
socket.on('post:updated', (post) => {
  queryClient.setQueryData(['posts', post.id], post);
  queryClient.setQueryData(['posts'], (old) => old?.map(p => p.id === post.id ? post : p));
});
socket.on('post:deleted', ({ id }) => {
  queryClient.setQueryData(['posts'], (old) => old?.filter(p => p.id !== id));
  queryClient.removeQueries({ queryKey: ['posts', id] });
});
```

### Socket Auth
```javascript
// Backend: Verify token, join user-specific room
io.use(async (socket, next) => {
  socket.user = jwt.verify(socket.handshake.auth.token);
  socket.join(`user:${socket.user.id}`);
});
// Frontend: Pass token in connection auth
```

## Environment Config

### Backend Validation Required
```javascript
// Joi schema: JWT_SECRET min 32 chars, validate all required vars
```

### Frontend Anti-Pattern
```javascript
// NEVER in frontend: JWT_SECRET, MONGODB_URI, API_KEY
// ONLY public: VITE_API_URL, VITE_SOCKET_URL
```

## Performance Red Flags

### Backend
- [ ] Missing indexes on queried fields
- [ ] No `.select()` on list endpoints
- [ ] No pagination on unbounded queries
- [ ] Synchronous file ops in handlers
- [ ] Missing `lean()` on read-only queries
- [ ] No caching on expensive queries

### Frontend
- [ ] No code splitting
- [ ] Images without lazy loading
- [ ] Missing React.memo on expensive components
- [ ] Fetching same data multiple times
- [ ] No prefetching

## Security Checklist

### Backend
- [ ] Rate limiting on auth endpoints
- [ ] Helmet middleware for headers
- [ ] Input sanitization (express-validator)
- [ ] CORS whitelist (specific origins)
- [ ] File upload: type + size + content validation
- [ ] bcrypt rounds >= 10

### Frontend
- [ ] Never `dangerouslySetInnerHTML` without sanitize
- [ ] httpOnly cookies + sameSite: 'strict'
- [ ] No secrets in code/env
- [ ] Token in memory, not localStorage

## Deployment Gotchas

### CORS
```javascript
// Dev: Different ports
Frontend: localhost:5173, Backend: localhost:3000
CORS: { origin: 'http://localhost:5173', credentials: true }

// Prod: Same domain or subdomain
CORS: { origin: 'https://myapp.com', credentials: true }
```

### Environment Variables
| Issue | Fix |
|-------|-----|
| Not loaded | Check `.env` location, `VITE_` prefix for frontend |
| Type mismatch | `process.env.PORT` is string, use `parseInt()` |
| Missing in prod | Set in hosting platform |

## Review Checklist

### API Design
- [ ] Consistent `{ success, data, error }` structure
- [ ] Proper HTTP status codes (200, 201, 400, 401, 404, 500)
- [ ] Pagination with `meta.pagination`
- [ ] Field selection to prevent over-fetching

### Auth Flow
- [ ] Access token in memory, refresh in httpOnly cookie
- [ ] Cookie: `sameSite: 'strict'`, `secure: true` in prod
- [ ] Token refresh with queue (no concurrent refreshes)
- [ ] Protected routes check auth on frontend + backend

### State Management
- [ ] Optimistic updates with rollback
- [ ] Cache invalidation after mutations
- [ ] Stable query keys (no inline objects)
- [ ] `enabled` flag when params can be undefined

### Error Handling
- [ ] Backend returns errors with `code` and `message`
- [ ] Frontend handles by code, not message text
- [ ] Field-level validation as array `[{field, message}]`
- [ ] Error boundary for React errors

### Security
- [ ] Input validation on backend
- [ ] No secrets in frontend
- [ ] File uploads: type + size + content validation
- [ ] Rate limiting on auth
- [ ] CORS with specific origins

### Performance
- [ ] Database indexes on queried fields
- [ ] Caching on expensive queries
- [ ] Code splitting by route
- [ ] No N+1 queries (frontend or backend)

### Types
- [ ] Shared types between frontend/backend
- [ ] MongoDB IDs to strings
- [ ] Dates as ISO 8601 strings
- [ ] Consistent null vs undefined
