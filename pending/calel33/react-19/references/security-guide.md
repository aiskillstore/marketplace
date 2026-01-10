# React 19 Security Guide

## Critical Vulnerability: CVE-2025-55182

### Severity: CRITICAL (CVSS 10.0)

**Discovery Date:** December 3, 2025

### Affected Versions

❌ React 19.0.0  
❌ React 19.1.0  
❌ React 19.1.1  
❌ React 19.2.0

### Affected Packages

- `react-server-dom-webpack`
- `react-server-dom-parcel`
- `react-server-dom-turbopack`

### Root Cause

Unsafe deserialization of attacker-controlled data in the React Server Components "Flight" protocol. When React decodes payloads sent to React Server Function endpoints, it does not properly validate the input, allowing remote code execution.

### Fixed Versions

✅ React 19.0.1  
✅ React 19.1.2  
✅ React 19.2.1

### Immediate Action Required

```bash
# Update React
npm install react@19.2.1 react-dom@19.2.1

# Verify no vulnerabilities
npm audit
```

### Framework-Specific Patches

| Framework | Vulnerable Versions | Fixed Versions |
|-----------|-------------------|----------------|
| **Next.js** | 14.3.0-canary.77+, 15.x, 16.x | 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7 |
| **Remix** | All using RSC | Update React to 19.2.1+ |
| **Vite + RSC** | All using RSC | Update React to 19.2.1+ |

---

## Security Gotchas & Secure Patterns

### Gotcha 1: Server Actions Are Public Endpoints

Server Actions are callable by anyone unless explicitly protected.

#### ❌ VULNERABLE

```javascript
'use server';
export async function deleteUser(userId) {
  await db.users.delete(userId); // Anyone can delete any user!
}
```

#### ✅ SECURE

```javascript
'use server';
import { getCurrentUser } from '@/lib/auth';

export async function deleteUser(userId) {
  const currentUser = await getCurrentUser();
  
  if (!currentUser) {
    throw new Error('Unauthorized');
  }
  
  if (currentUser.id !== userId && !currentUser.isAdmin) {
    throw new Error('Forbidden');
  }
  
  await db.users.delete(userId);
}
```

---

### Gotcha 2: Client Components Can Import Server Actions

Risk: Exposing server-side secrets in client bundles.

#### ❌ VULNERABLE

```javascript
'use server';
const API_SECRET = process.env.API_SECRET; // Bundled in client!

export async function fetchData() {
  return fetch('https://api.example.com', {
    headers: { 'Authorization': `Bearer ${API_SECRET}` }
  });
}
```

#### ✅ SECURE

```javascript
'use server';
export async function fetchData() {
  // Read secret inside function, not module scope
  const API_SECRET = process.env.API_SECRET;
  
  return fetch('https://api.example.com', {
    headers: { 'Authorization': `Bearer ${API_SECRET}` }
  });
}
```

---

### Gotcha 3: XSS via Unsanitized User Input

Risk: Server Components rendering user input without sanitization.

#### ❌ VULNERABLE

```javascript
async function UserProfile({ userId }) {
  const user = await db.users.findById(userId);
  
  return (
    <div>
      <h1>{user.name}</h1>
      {/* If user.bio contains <script>, it will execute! */}
      <div dangerouslySetInnerHTML={{ __html: user.bio }} />
    </div>
  );
}
```

#### ✅ SECURE

```javascript
import DOMPurify from 'isomorphic-dompurify';

async function UserProfile({ userId }) {
  const user = await db.users.findById(userId);
  const sanitizedBio = DOMPurify.sanitize(user.bio);
  
  return (
    <div>
      <h1>{user.name}</h1>
      <div dangerouslySetInnerHTML={{ __html: sanitizedBio }} />
    </div>
  );
}
```

---

### Gotcha 4: Data Exposure via Props

Risk: Passing sensitive data to Client Components.

#### ❌ VULNERABLE

```javascript
async function PaymentPage({ orderId }) {
  const order = await db.orders.findById(orderId);
  const apiKey = process.env.STRIPE_SECRET_KEY;
  
  return (
    <ClientPaymentForm 
      order={order} 
      apiKey={apiKey} // This will be in client bundle!
    />
  );
}
```

#### ✅ SECURE

```javascript
async function PaymentPage({ orderId }) {
  const order = await db.orders.findById(orderId);
  
  // Create Server Action for payment processing
  async function processPayment(formData) {
    'use server';
    const apiKey = process.env.STRIPE_SECRET_KEY; // Stays on server
    // ... process payment
  }
  
  return (
    <ClientPaymentForm 
      order={order} 
      processPayment={processPayment} // Function reference, not secret
    />
  );
}
```

---

### Gotcha 5: Boundary Violations

Risk: Importing server-only code in Client Components.

#### ❌ VULNERABLE

```javascript
'use client';
import { db } from '@/lib/database'; // Server-only module!

function MyComponent() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    // This will fail - db doesn't exist in browser!
    db.users.getAll().then(setData);
  }, []);
  
  return <div>{data.map(...)}</div>;
}
```

#### ✅ SECURE

```javascript
'use client';
import { getUsers } from '@/app/actions'; // Server Action

function MyComponent() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    getUsers().then(setData); // Calls server-side code safely
  }, []);
  
  return <div>{data.map(...)}</div>;
}
```

---

## Security Checklist

### Immediate Actions

- [ ] **🔴 CRITICAL: Check React version**
  ```bash
  npm list react react-dom
  ```
  Must be 19.0.1, 19.1.2, 19.2.1 or later

- [ ] **🔴 CRITICAL: Update if vulnerable**
  ```bash
  npm install react@19.2.1 react-dom@19.2.1
  ```

- [ ] **Run security audit**
  ```bash
  npm audit
  npm audit fix
  ```

- [ ] **Check framework version**
  Update Next.js, Remix, etc. to patched versions

### Server Actions Security

- [ ] **Authentication on all Server Actions**
  ```javascript
  'use server';
  export async function action() {
    const user = await getCurrentUser();
    if (!user) throw new Error('Unauthorized');
    // ... rest of action
  }
  ```

- [ ] **Authorization checks**
  - Verify user has permission for action
  - Don't trust client-provided IDs

- [ ] **Input validation**
  ```javascript
  import { z } from 'zod';
  
  const schema = z.object({
    email: z.string().email(),
    age: z.number().min(0).max(150)
  });
  
  const result = schema.safeParse(input);
  ```

- [ ] **Rate limiting**
  ```javascript
  import { ratelimit } from '@/lib/redis';
  
  const { success } = await ratelimit.limit(userId);
  if (!success) throw new Error('Too many requests');
  ```

### Data Security

- [ ] **No secrets in Client Components**
  - Check for `process.env` in client code
  - Use Server Actions for API calls with secrets

- [ ] **Sanitize user input**
  ```javascript
  import DOMPurify from 'isomorphic-dompurify';
  const clean = DOMPurify.sanitize(userInput);
  ```

- [ ] **File upload validation**
  - Check file size (< 5MB recommended)
  - Validate file type
  - Scan for malware if applicable

- [ ] **Parameterized queries**
  ```javascript
  // ✅ GOOD
  await db.query('SELECT * FROM users WHERE id = $1', [userId]);
  
  // ❌ BAD
  await db.query(`SELECT * FROM users WHERE id = ${userId}`);
  ```

### XSS Prevention

- [ ] **Never use `dangerouslySetInnerHTML` without sanitization**
- [ ] **Validate and escape user-generated content**
- [ ] **Use Content Security Policy (CSP) headers**
  ```javascript
  // next.config.js
  module.exports = {
    headers: async () => [{
      source: '/:path*',
      headers: [{
        key: 'Content-Security-Policy',
        value: "default-src 'self'; script-src 'self' 'unsafe-inline'"
      }]
    }]
  };
  ```

### Network Security

- [ ] **HTTPS only** - No HTTP in production
- [ ] **CORS configured properly**
- [ ] **CSRF tokens** - For state-changing operations
- [ ] **Security headers** - HSTS, X-Frame-Options, etc.

### Monitoring

- [ ] **Error tracking** - Sentry, Datadog, etc.
- [ ] **Audit logging** - Log sensitive actions
- [ ] **Rate limit monitoring** - Alert on abuse
- [ ] **Regular security scans** - Penetration testing

---

## Temporary Mitigations

⚠️ **Only if you cannot upgrade immediately:**

### 1. Disable React Server Components

```javascript
// next.config.js
module.exports = {
  experimental: {
    serverActions: false,
    serverComponents: false
  }
};
```

### 2. Add WAF Rules

- Block requests to `/_next/data/*` from untrusted origins
- Rate limit requests to Server Action endpoints
- Validate `Content-Type` headers

### 3. Network-Level Protection

- Place application behind authenticated proxy
- Restrict access to Server Action endpoints

---

## Best Practices Summary

1. **Always authenticate** - Check user identity in every Server Action
2. **Validate everything** - Never trust client input
3. **Secrets stay on server** - Read environment variables inside functions
4. **Sanitize HTML** - Use DOMPurify for user-generated content
5. **Use parameterized queries** - Prevent SQL injection
6. **Rate limit** - Protect against abuse
7. **Monitor actively** - Track errors and suspicious activity
8. **Update regularly** - Keep dependencies current
