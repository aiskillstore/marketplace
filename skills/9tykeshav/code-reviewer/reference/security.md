# MERN Security Reference

## OWASP Top 10 MERN Map

| Category | Flag Pattern | BAD | GOOD |
|----------|-------------|-----|------|
| **A01: Access Control** | Missing auth, client checks, IDOR | `app.get('/api/users/:id', (req, res) => res.json(await User.findById(req.params.id)))` | `authenticateToken + if (req.params.id !== req.user.id && !admin) return 403` |
| **A02: Crypto** | MD5/SHA1, HTTP, plaintext | `crypto.createHash('md5').update(password)` | `bcrypt.hash(password, 12)` |
| **A03: Injection** | Direct object in queries, $where | `User.findOne({ email, password })` | `typeof email !== 'string' return 400; bcrypt.compare()` |
| **A04: Design** | Verbose errors | `res.status(404).json({ error: 'User not found' })` | `res.status(401).json({ error: 'Invalid credentials' })` |
| **A05: Config** | Wildcard CORS | `cors({ origin: '*', credentials: true })` | `cors({ origin: ALLOWED_ORIGINS, credentials: true })` |
| **A07: Auth** | No token expiry, weak secrets | `jwt.sign({ userId: 123 }, 'secret')` | `jwt.sign({ sub: user.id }, JWT_SECRET, { expiresIn: '15m', algorithms: ['HS256'] })` |
| **A08: Integrity** | ^ versions | `"express": "^4.18.2"` | `"express": "4.18.2"` + `npm ci` |
| **A10: SSRF** | Unvalidated URL | `axios.get(req.body.url)` | Validate protocol, whitelist hosts, block 127.*, 192.168.*, 10.* |

## NoSQL Injection

### Attack Vectors to Flag
- `User.findOne({ email, password })` - `{"email":{"$ne":null},"password":{"$ne":null}}` bypasses
- `User.find(req.query)` - Exposes all operators
- `User.find({ $where: \`this.username == '${req.query.username}'\` })` - `'; return true; //`
- `User.find({ username: { $regex: req.query.search } })` - `.*` matches all

### Defense Checklist
- [ ] Type check: `typeof email !== 'string'`
- [ ] `express-mongo-sanitize` middleware
- [ ] `schema.set('strict', true)`
- [ ] `mongoose.Types.ObjectId.isValid(id)`
- [ ] Never `$where` with user input
- [ ] Whitelist operators: `['$eq', '$gt', '$gte', '$lt', '$lte', '$in']`

## XSS in React

| Pattern | Vulnerable | Secure |
|---------|-----------|--------|
| **dangerouslySetInnerHTML** | `<div dangerouslySetInnerHTML={{ __html: content }} />` | `DOMPurify.sanitize(content, { ALLOWED_TAGS: ['p','br'] })` |
| **URL injection** | `<a href={url}>` allows `javascript:` | `['http:','https:'].includes(new URL(u).protocol)` |
| **Prop spread** | `<div {...userProps} />` | `const allowed = { className, id }; <div {...allowed} />` |
| **SSR inject** | `<script>window.__DATA__={data}</script>` | `serialize(data, { isJSON: true })` |
| **CSP** | No header | `helmet.contentSecurityPolicy({ directives: { defaultSrc: ["'self'"], scriptSrc: ["'self'"], objectSrc: ["'none'"] }})` |

## JWT Security

| Issue | Flag | Fix |
|-------|------|-----|
| **No algorithm** | `jwt.verify(token, secret)` | `jwt.verify(token, secret, { algorithms: ['HS256'] })` |
| **Weak secret** | < 32 chars | `crypto.randomBytes(64).toString('hex')` |
| **No expiry** | `jwt.sign({ userId })` | `jwt.sign({ sub: id }, secret, { expiresIn: '15m' })` |
| **Sensitive payload** | Password, CC, SSN in JWT | Only: sub, role, iat, jti |
| **No revocation** | No logout invalidation | Redis blacklist with TTL |
| **localStorage** | XSS steals token | httpOnly cookies, sameSite: 'strict' |

## Secrets Management

### Flags in Code
- Hardcoded: `apiKey = 'sk_live_'`, `password = 'MyPass123'`
- Comments: `// mongodb://admin:password@localhost`
- Git history: `git log --all -- "**/*.env"`
- Client-side: REACT_APP vars with backend secrets

### .gitignore Must Have
`.env*`, `*.pem`, `*.key`, `*.cert`, `config/secrets.json`

### Validation Startup
`['JWT_SECRET', 'MONGODB_URI', 'NODE_ENV'].forEach(v => { if (!process.env[v]) throw new Error(\`Missing \${v}\`); });`
`if (process.env.JWT_SECRET.length < 32) throw new Error('JWT_SECRET too weak');`

## File Upload Security

### Checklist
- [ ] MIME whitelist only
- [ ] Extension check
- [ ] Max 5MB
- [ ] `file-type` library content verification
- [ ] Random name: `crypto.randomBytes(16).toString('hex')`
- [ ] Path traversal: `path.basename()`
- [ ] Virus scan: ClamAV
- [ ] Images: sharp (removes EXIF)

### Path Traversal Fix
`const filename = path.basename(req.params.filename); const filePath = path.join(__dirname, 'uploads', filename); if (!filePath.startsWith(path.join(__dirname, 'uploads'))) return 403;`

## Rate Limiting & Brute Force

### Config
- API: `rateLimit({ windowMs: 15 * 60 * 1000, max: 100 })`
- Auth: `rateLimit({ windowMs: 15 * 60 * 1000, max: 5, skipSuccessfulRequests: true })`

### Account Lockout (Redis)
`const attempts = await redis.get(\`login_attempts:\${email}\`); if (parseInt(attempts) >= 5) return 429;`
`await redis.incr(\`login_attempts:\${email}\`); await redis.expire(\`login_attempts:\${email}\`, 15 * 60);`
Success: `redis.del(\`login_attempts:\${email}\`)`

## CORS Misconfigurations

| Dangerous | Why | Secure |
|-----------|-----|--------|
| `origin: '*'` + credentials | Any origin reads responses | `origin: ALLOWED_ORIGINS` |
| `origin: (o, cb) => cb(null, o)` | Reflects any origin | Validate against whitelist |
| `origin.includes('example.com')` | Matches `attacker-example.com` | `ALLOWED_ORIGINS.includes(origin)` |

## Auth Bypass Patterns

| Vulnerability | Example | Fix |
|---------------|---------|-----|
| **Missing auth** | `app.get('/api/admin', ...)` | `authenticateToken, authorize(['admin'])` middleware |
| **Client-only** | React: `if (user.role !== 'admin') <Navigate />` | Always validate backend |
| **Parameter tamper** | `User.create({ ...req.body })` attacker sends `role: 'admin'` | `User.create({ email, password, role: 'user' })` |
| **Session fixation** | `req.session.userId = user.id` no regen | `req.session.regenerate(() => { req.session.userId = user.id })` |
| **No logout invalid** | Frontend clears, backend doesn't blacklist | Redis: `redis.setex(\`blacklist:\${token}\`, ttl, '1')` |

### Password Reset Security
`const resetToken = crypto.randomBytes(32).toString('hex');` NOT `Math.random()`
`user.resetPasswordToken = crypto.createHash('sha256').update(resetToken).digest('hex');` Store hash
`user.resetPasswordExpires = Date.now() + 3600000;` 1 hour
`return res.json({ message: 'If email exists, reset link sent' });` Don't reveal existence

## Sensitive Data Exposure

### Patterns to Flag
- `res.json(user);` - Exposes password hash, email, internal fields
- `console.log('Login:', { email, password });` - NEVER log passwords
- `res.status(500).json({ error: error.message });` - Stack traces
- `GET /api/reset-password?token=abc&password=new` - URLs logged

### Mongoose Protection
`password: { type: String, select: false }` Never selected
`schema.methods.toJSON = function() { const obj = this.toObject(); delete obj.password; delete obj.apiKey; delete obj.__v; return obj; };`
`User.findById(id).select('username avatar bio');` Only public fields

## Input Validation

### Express-Validator Pattern
```javascript
const validate = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8, max: 128 }).matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/),
  body('role').optional().isIn(['user', 'admin'])
];
app.post('/api/users', validate, (req, res) => { if (!validationResult(req).isEmpty()) return 400; });
```

### Type Coercion
BAD: `if (req.body.age > 18)` - `"19abc"` coerces to 19
GOOD: `if (typeof req.body.age !== 'number' || req.body.age <= 18) return 400;`
GOOD: `if (req.body.isAdmin === true)` strict equality

### Whitelist
NEVER: `input.replace(/<script>/g, '')` - Bypassed with `<ScRiPt>`
ALWAYS: `const validateUsername = (u) => /^[a-zA-Z0-9_]{3,20}$/.test(u);`
ALWAYS: `const filterObject = (obj, allowed) => { const f = {}; allowed.forEach(k => { if (obj[k]) f[k] = obj[k]; }); return f; };`

## CSRF Protection

Generate: `res.cookie('XSRF-TOKEN', crypto.randomBytes(32).toString('hex'), { httpOnly: false, secure: true, sameSite: 'strict' });`
Validate: `if (!['GET','HEAD','OPTIONS'].includes(req.method) && req.cookies['XSRF-TOKEN'] !== req.headers['x-xsrf-token']) return 403;`

## Dependency Security

### npm audit Workflow
`npm audit --production` Check prod vulnerabilities
`npm ci` Clean install from lock (CI/CD)
`npm ls lodash minimist validator express` Check known vulnerabilities

### package.json
`"express": "4.18.2"` Exact version (NO ^ or ~)

## CRITICAL Checklist (Fix Now)
- [ ] All sensitive endpoints: `authenticateToken` middleware
- [ ] JWT secret: 64+ chars, env stored (not hardcoded)
- [ ] Passwords: `bcrypt.hash(pwd, 12)` never MD5/SHA1
- [ ] All `User.find*` queries: type-check `typeof === 'string'`
- [ ] No `$where` with user input
- [ ] File uploads: validate MIME + extension + size
- [ ] No secrets in git: `git log --all -- "**/*.env"`
- [ ] CORS origin: whitelisted (not `'*'` with credentials)
- [ ] HTTPS enforced in production

## HIGH Priority
- [ ] Rate limiting on `/api/auth/*`: max 5 per 15min
- [ ] `express-mongo-sanitize` middleware installed
- [ ] React: no `dangerouslySetInnerHTML` without DOMPurify
- [ ] Error messages generic: "Invalid credentials" not "User not found"
- [ ] Input validation on all POST/PUT: express-validator or Joi
- [ ] `helmet()` middleware configured
- [ ] JWT tokens: `expiresIn: '15m'` and `algorithms: ['HS256']`
- [ ] Auth middleware: check token blacklist (Redis)

## MEDIUM Priority
- [ ] Mongoose schemas: `.select(false)` on sensitive fields
- [ ] `toJSON()` method: removes password, apiKey, __v
- [ ] winston logger: redacts sensitive fields
- [ ] File paths: `path.basename()` prevent traversal
- [ ] Images: processed with sharp (removes EXIF)
- [ ] Account lockout: 5 failed logins (Redis counter)
- [ ] CSP header: blocks inline scripts
- [ ] npm audit runs in CI/CD

## Grep Patterns for Code Review
```bash
grep -r "findOne.*req\.(body|query|params)" .  # NoSQL injection
grep -r "jwt\.verify.*\[^,\]*\)" .             # Missing algorithm spec
grep -r "\.sendFile.*req\." .                  # Path traversal
grep -r "dangerouslySetInnerHTML" .            # XSS risk
grep -r "console\.log.*password" .             # Logging secrets
grep -r "origin.*\*" .                         # Wildcard CORS
grep -r "\$where" .                            # Dangerous MongoDB operator
```
