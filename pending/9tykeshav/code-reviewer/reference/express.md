# Express.js Code Review Reference

## Middleware Order (CRITICAL)
Parse → Security (Helmet/CORS) → Auth → Routes → Error Handler (LAST)

## BAD Patterns to Flag

| Issue | BAD | Fix |
|-------|-----|-----|
| Async no wrapper | `app.get('/users', async (req, res) => { await User.find(); })` | Wrap with asyncHandler or use Express 5.x |
| Missing await | `User.create(req.body); res.json({})` | `await User.create()` |
| After next() | Modify req after `next()` | Modify before `next()` |
| Forgot next() | Middleware doesn't call `next()` or send response | Always call `next()` or send response |
| Swallow errors | `catch (e) { res.json([]); }` | `catch (e) { next(e); }` |
| Leak stack | `res.status(500).json({ stack: err.stack })` | Hide in production |
| Blocking ops | `readFileSync`, `pbkdf2Sync` | Use async versions |
| Route bloat | Validation + logic in one handler | Separate: validate → middleware → controller |

```js
// Async wrapper (Express 4.x)
const asyncHandler = fn => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
```

## Security Config to CHECK FOR

```js
// Helmet: CSP (defaultSrc: 'self', objectSrc/frameSrc: 'none'), HSTS (maxAge: 31536000), frameguard: deny, noSniff: true

// CORS - BAD: app.use(cors()); // DANGEROUS!
app.use(cors({ origin: (origin, cb) => allowedOrigins.includes(origin) ? cb(null, true) : cb(new Error('CORS')), credentials: true }));

// Rate Limiting: auth endpoints (max: 5/hour, skipSuccessfulRequests), general (max: 100/15min)
// Size Limits: { limit: '10kb' }
// Sanitization: mongoSanitize(), xss()
// Multer: limits { fileSize: 5MB, files: 5 }, fileFilter whitelist mimetypes
```

## Error Handling Patterns to Flag

```js
// Custom Error: constructor(message, statusCode, code); this.isOperational = true

// Centralized Handler (MUST BE LAST)
const errorHandler = (err, req, res, next) => {
  if (err.isOperational) return res.status(err.statusCode).json({ code: err.code, message: err.message });
  if (err.name === 'ValidationError') return res.status(400).json({ code: 'VALIDATION_ERROR', errors: Object.values(err.errors).map(e => e.message) });
  if (err.code === 11000) return res.status(409).json({ code: 'DUPLICATE_ERROR', message: `${Object.keys(err.keyPattern)[0]} exists` });
  if (err.name === 'JsonWebTokenError') return res.status(401).json({ code: 'INVALID_TOKEN' });
  if (err.name === 'TokenExpiredError') return res.status(401).json({ code: 'TOKEN_EXPIRED' });
  res.status(500).json({ message: process.env.NODE_ENV === 'production' ? 'Something went wrong' : err.message });
};
```

## Auth Patterns to CHECK FOR

```js
// Tokens: access (15m, type:'access'), refresh (7d, type:'refresh')
// Auth CHECK: Bearer token, type verification, user exists, .select('-password')
// Refresh CHECK: httpOnly cookie, stored in Redis/DB, old token revoked
// RBAC: (...roles) => roles.includes(req.user.role) ? next() : next(new AppError('Forbidden', 403))
// Ownership CHECK: Admin bypass, multiple fields (userId/authorId/owner)
```

## Validation - CHECK FOR

```js
// Joi CHECK: { abortEarly: false, stripUnknown: true }
// Express-Validator: validationResult(req), map errors to { field, message }
```

## Production - CHECK FOR

```js
// process.on('unhandledRejection'/'uncaughtException') with logging
// Graceful shutdown: SIGTERM/SIGINT → close connections → process.exit(0), 30s timeout
// Health checks: /health (200 OK), /health/ready (503 if deps down)
// Request ID: req.id = req.headers['x-request-id'] || uuidv4(); res.setHeader('X-Request-ID', req.id)
```

## Code Review Checklist

### Security (Critical)
- [ ] Helmet configured (CSP, HSTS, frameguard, noSniff)
- [ ] CORS whitelist (NOT `cors()` in production)
- [ ] Rate limiting on auth endpoints (5/hour)
- [ ] `mongoSanitize()` and `xss()` enabled
- [ ] Request size limits: `{ limit: '10kb' }`
- [ ] httpOnly cookies for refresh tokens
- [ ] bcrypt cost 12+
- [ ] Multer: fileSize limit, mimetype whitelist

### Error Handling
- [ ] Centralized error handler (LAST middleware)
- [ ] All async handlers wrapped
- [ ] Stack traces hidden in production
- [ ] 404 handler present
- [ ] Custom AppError class with isOperational flag
- [ ] Mongoose errors mapped (ValidationError, 11000, CastError)
- [ ] JWT errors mapped (JsonWebTokenError, TokenExpiredError)

### Middleware
- [ ] Order: Parse → Security → Auth → Routes → Errors
- [ ] All middleware calls `next()` or sends response
- [ ] Async errors caught (asyncHandler or Express 5.x)
- [ ] No modifications after `next()` called

### Authentication
- [ ] JWT expiry (15m access, 7d refresh)
- [ ] Token type verified (`access` vs `refresh`)
- [ ] User existence checked after decode
- [ ] Password excluded (`.select('-password')`)
- [ ] Refresh tokens stored in Redis/DB and revoked
- [ ] Rate limiting on login/register

### Validation
- [ ] All inputs validated (Joi or express-validator)
- [ ] `stripUnknown: true` (Joi)
- [ ] Error messages user-friendly (no DB internals)
- [ ] `abortEarly: false` to show all errors

### Production
- [ ] Structured logging (Winston/Bunyan)
- [ ] Health checks (`/health`, `/health/ready`)
- [ ] Graceful shutdown (SIGTERM/SIGINT)
- [ ] Unhandled rejection/exception handlers
- [ ] Request ID tracing (X-Request-ID)
- [ ] Compression enabled

### Performance & Anti-Patterns
- [ ] Compression enabled (threshold: 1024, level: 6)
- [ ] No blocking ops (`readFileSync`, `pbkdf2Sync`)
- [ ] No missing `await` on async operations
- [ ] No route handler bloat (separate validation/controller/service)
- [ ] No swallowed errors (always propagate with `next(error)`)
- [ ] RESTful routes (no `/getUsers`, use `GET /users`)

## Mongoose Error Status Codes

| Error | Status | Code |
|-------|--------|------|
| `ValidationError` | 400 | `VALIDATION_ERROR` |
| Duplicate key (11000) | 409 | `DUPLICATE_ERROR` |
| `JsonWebTokenError` | 401 | `INVALID_TOKEN` |
| `TokenExpiredError` | 401 | `TOKEN_EXPIRED` |
| `CastError` (invalid ObjectId) | 400 | `INVALID_ID` |
