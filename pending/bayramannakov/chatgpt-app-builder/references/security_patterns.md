# Security Patterns for ChatGPT Apps

Essential security patterns to protect your ChatGPT App and users.

---

## 1. XSS Prevention

### The Problem
API responses may contain HTML entities or malicious scripts that could execute in your widget.

### Solution: Decode Then Escape

```typescript
/**
 * Decode HTML entities from API responses
 * APIs often encode special characters for transport
 */
function decodeHtmlEntities(text: string): string {
  if (!text) return '';
  return text
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/<br\s*\/?>/gi, '\n')  // Convert BR tags to newlines
    .replace(/<[^>]*>/g, '');        // Strip remaining HTML tags
}

/**
 * Escape HTML to prevent XSS when inserting into DOM
 */
function escapeHtml(text: string): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Safe text processing: decode API entities, then escape for display
 */
function safeText(apiText: string): string {
  return escapeHtml(decodeHtmlEntities(apiText));
}
```

### Safe DOM Methods

```javascript
// RECOMMENDED: Use textContent for plain text (auto-escapes)
element.textContent = data.bio;

// RECOMMENDED: Use createElement for structured content
function renderProfile(data) {
  const container = document.getElementById('profile');

  const name = document.createElement('h1');
  name.textContent = safeText(data.name);

  const bio = document.createElement('p');
  bio.textContent = safeText(data.bio);

  container.appendChild(name);
  container.appendChild(bio);
}
```

### Common Mistakes to Avoid

```javascript
// WRONG: Direct DOM insertion without escaping
container.insertAdjacentHTML('beforeend', data.bio);

// WRONG: Only escaping (double-encodes API entities)
element.textContent = escapeHtml(data.bio);

// CORRECT: Decode then escape, or use textContent
element.textContent = decodeHtmlEntities(data.bio);
```

---

## 2. Input Validation

### URL Validation (LinkedIn Example)

```typescript
// Valid LinkedIn URL patterns
const LINKEDIN_PATTERNS = {
  person: /^\/in\/([a-zA-Z0-9\-_]+)\/?$/,
  company: /^\/company\/([a-zA-Z0-9\-_]+)\/?$/,
  school: /^\/school\/([a-zA-Z0-9\-_]+)\/?$/,
};

// Valid slug pattern (alphanumeric, hyphens, underscores)
const SLUG_PATTERN = /^[a-zA-Z0-9\-_]+$/;

/**
 * Validate and normalize LinkedIn URLs
 * Prevents path traversal and injection attacks
 */
function normalizeLinkedInUrl(url: string): string {
  if (!url || typeof url !== 'string') {
    throw new Error('Invalid URL');
  }

  // Clean the input
  let normalized = url
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/^www\./, '')
    .replace(/\/+$/, '');

  // Must be LinkedIn domain
  if (!normalized.startsWith('linkedin.com')) {
    // Maybe just a slug?
    if (SLUG_PATTERN.test(normalized) && !normalized.includes('/')) {
      return `https://linkedin.com/in/${normalized}`;
    }
    throw new Error('Invalid LinkedIn URL');
  }

  // Extract path
  const path = normalized.substring('linkedin.com'.length);

  // Check for suspicious patterns
  if (path.includes('@') || path.includes('..') || path.includes('://')) {
    throw new Error('Invalid URL format');
  }

  // Validate path structure
  const pathParts = path.split('/').filter(Boolean);
  if (pathParts.length >= 2) {
    const type = pathParts[0];
    const slug = pathParts[1];

    if (!['in', 'company', 'school'].includes(type)) {
      throw new Error('Invalid LinkedIn path');
    }

    if (!SLUG_PATTERN.test(slug)) {
      throw new Error('Invalid profile identifier');
    }

    return `https://linkedin.com/${type}/${slug}`;
  }

  throw new Error('Invalid LinkedIn URL format');
}
```

### General URL Validation

```typescript
/**
 * Validate any URL for safety
 */
function validateUrl(url: string, allowedDomains?: string[]): URL {
  let parsed: URL;

  try {
    // Add protocol if missing
    const urlWithProtocol = url.startsWith('http') ? url : `https://${url}`;
    parsed = new URL(urlWithProtocol);
  } catch {
    throw new Error('Invalid URL format');
  }

  // Must be HTTPS
  if (parsed.protocol !== 'https:') {
    throw new Error('Only HTTPS URLs allowed');
  }

  // Check domain whitelist if provided
  if (allowedDomains && !allowedDomains.includes(parsed.hostname)) {
    throw new Error('Domain not allowed');
  }

  // Block suspicious patterns
  if (parsed.username || parsed.password) {
    throw new Error('Credentials in URL not allowed');
  }

  return parsed;
}
```

---

## 3. SSRF Protection for Image Proxies

### The Problem
If your app proxies images, attackers could request internal resources.

### Solution: Domain Whitelist + IP Blocklist

```typescript
const ALLOWED_IMAGE_DOMAINS = [
  'media.licdn.com',
  'static.licdn.com',
  'media.enrichlayer.com',
  // Add your trusted image domains
];

const BLOCKED_IP_PATTERNS = [
  /^localhost$/i,
  /^127\./,
  /^0\./,
  /^10\./,
  /^172\.(1[6-9]|2[0-9]|3[01])\./,
  /^192\.168\./,
  /^169\.254\.169\.254/,  // AWS metadata
  /^fd[0-9a-f]{2}:/i,     // IPv6 private
  /\.local$/i,
  /\.internal$/i,
  /\.localhost$/i,
];

/**
 * Check if a hostname is potentially internal/private
 */
function isBlockedHost(hostname: string): boolean {
  return BLOCKED_IP_PATTERNS.some(pattern => pattern.test(hostname));
}

/**
 * Safely proxy an image URL
 */
async function proxyImage(imageUrl: string): Promise<string | null> {
  try {
    const url = new URL(imageUrl);

    // Must be HTTPS
    if (url.protocol !== 'https:') {
      console.warn('Blocked non-HTTPS image:', imageUrl);
      return null;
    }

    // Check domain whitelist
    if (!ALLOWED_IMAGE_DOMAINS.includes(url.hostname)) {
      console.warn('Blocked non-whitelisted domain:', url.hostname);
      return null;
    }

    // Check for blocked patterns
    if (isBlockedHost(url.hostname)) {
      console.warn('Blocked internal hostname:', url.hostname);
      return null;
    }

    // Fetch with timeout and size limit
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(imageUrl, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'ChatGPT-App-Image-Proxy/1.0',
      },
    });

    clearTimeout(timeout);

    if (!response.ok) {
      return null;
    }

    // Check content type
    const contentType = response.headers.get('content-type');
    if (!contentType?.startsWith('image/')) {
      console.warn('Invalid content type:', contentType);
      return null;
    }

    // Limit size (100KB)
    const buffer = await response.arrayBuffer();
    if (buffer.byteLength > 100 * 1024) {
      console.warn('Image too large:', buffer.byteLength);
      return null;
    }

    // Convert to data URL
    const base64 = Buffer.from(buffer).toString('base64');
    return `data:${contentType};base64,${base64}`;

  } catch (error) {
    console.error('Image proxy error:', error);
    return null;
  }
}
```

---

## 4. Rate Limiting

### Per-Session Rate Limiter

```typescript
interface SessionLimit {
  hourlyCount: number;
  dailyCount: number;
  hourlyResetAt: number;
  dailyResetAt: number;
  lastAccessedAt: number;
}

class RateLimiter {
  private sessions = new Map<string, SessionLimit>();
  private readonly hourlyLimit: number;
  private readonly dailyLimit: number;
  private readonly maxSessions: number;

  constructor(config: {
    hourlyLimit?: number;
    dailyLimit?: number;
    maxSessions?: number;
  } = {}) {
    this.hourlyLimit = config.hourlyLimit || 10;
    this.dailyLimit = config.dailyLimit || 50;
    this.maxSessions = config.maxSessions || 10000;

    // Cleanup expired sessions every hour
    setInterval(() => this.cleanup(), 60 * 60 * 1000);
  }

  check(sessionId: string): { allowed: boolean; remaining: number; resetIn: number } {
    const now = Date.now();
    let session = this.sessions.get(sessionId);

    if (!session) {
      session = {
        hourlyCount: 0,
        dailyCount: 0,
        hourlyResetAt: now + 60 * 60 * 1000,
        dailyResetAt: now + 24 * 60 * 60 * 1000,
        lastAccessedAt: now,
      };
      this.sessions.set(sessionId, session);
      this.evictIfNeeded();
    }

    // Reset counters if windows expired
    if (now >= session.hourlyResetAt) {
      session.hourlyCount = 0;
      session.hourlyResetAt = now + 60 * 60 * 1000;
    }
    if (now >= session.dailyResetAt) {
      session.dailyCount = 0;
      session.dailyResetAt = now + 24 * 60 * 60 * 1000;
    }

    session.lastAccessedAt = now;

    // Check limits
    const hourlyRemaining = this.hourlyLimit - session.hourlyCount;
    const dailyRemaining = this.dailyLimit - session.dailyCount;
    const remaining = Math.min(hourlyRemaining, dailyRemaining);

    if (remaining <= 0) {
      const resetIn = Math.min(
        session.hourlyResetAt - now,
        session.dailyResetAt - now
      );
      return { allowed: false, remaining: 0, resetIn };
    }

    // Increment counters
    session.hourlyCount++;
    session.dailyCount++;

    return {
      allowed: true,
      remaining: remaining - 1,
      resetIn: session.hourlyResetAt - now,
    };
  }

  private evictIfNeeded(): void {
    if (this.sessions.size <= this.maxSessions) return;

    // LRU eviction - remove oldest accessed sessions
    const sorted = [...this.sessions.entries()]
      .sort((a, b) => a[1].lastAccessedAt - b[1].lastAccessedAt);

    const toRemove = sorted.slice(0, Math.floor(this.maxSessions * 0.1));
    for (const [id] of toRemove) {
      this.sessions.delete(id);
    }
  }

  private cleanup(): void {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours

    for (const [id, session] of this.sessions) {
      if (now - session.lastAccessedAt > maxAge) {
        this.sessions.delete(id);
      }
    }
  }
}

// Usage
const rateLimiter = new RateLimiter({
  hourlyLimit: 10,
  dailyLimit: 50,
  maxSessions: 10000,
});

// In tool handler
const result = rateLimiter.check(sessionId);
if (!result.allowed) {
  return {
    content: [{
      type: 'text',
      text: `Rate limit exceeded. Try again in ${Math.ceil(result.resetIn / 60000)} minutes.`,
    }],
  };
}
```

---

## 5. CORS Configuration

```typescript
const ALLOWED_ORIGINS = [
  'https://chat.openai.com',
  'https://chatgpt.com',
  'https://openai.com',
  'https://platform.openai.com',
];

function setCorsHeaders(
  req: http.IncomingMessage,
  res: http.ServerResponse
): void {
  const origin = req.headers.origin;

  // Only allow whitelisted origins
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else if (process.env.NODE_ENV !== 'production') {
    // Allow any origin in development
    res.setHeader('Access-Control-Allow-Origin', origin || '*');
  }

  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
}
```

---

## 6. Security Headers

```typescript
function setSecurityHeaders(res: http.ServerResponse): void {
  // Prevent MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');

  // Enable XSS filter (legacy browsers)
  res.setHeader('X-XSS-Protection', '1; mode=block');

  // Control referrer information
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  // For production, also consider:
  // res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
}
```

---

## 7. Error Handling (No Information Leakage)

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number = 500,
    public readonly code: string = 'UNKNOWN_ERROR'
  ) {
    super(message);
  }
}

function handleToolError(error: unknown, sessionId: string): ToolResult {
  // Log full error internally
  console.error(`[${sessionId}] Tool error:`, error);

  // Return generic message to user (no stack traces, no internal details)
  if (error instanceof AppError) {
    return {
      content: [{ type: 'text', text: error.message }],
      structuredContent: {
        error: true,
        code: error.code,
        message: error.message,
      },
    };
  }

  // Generic error for unexpected issues
  return {
    content: [{ type: 'text', text: 'An error occurred. Please try again.' }],
    structuredContent: {
      error: true,
      code: 'INTERNAL_ERROR',
      message: 'An error occurred. Please try again.',
    },
  };
}
```

---

## Security Checklist

### Before Deployment

- [ ] All user input is validated before use
- [ ] HTML output is properly escaped or uses safe DOM methods
- [ ] Only HTTPS URLs are allowed
- [ ] External requests use domain whitelists
- [ ] Internal IPs are blocked in proxy requests
- [ ] Rate limiting is implemented
- [ ] CORS is configured for ChatGPT domains only
- [ ] Security headers are set on all responses
- [ ] Errors don't leak internal information
- [ ] API keys are in environment variables, not code
- [ ] No sensitive data in logs

### Ongoing

- [ ] Monitor rate limit hits for abuse patterns
- [ ] Review and rotate API keys periodically
- [ ] Keep dependencies updated
- [ ] Monitor error logs for attack patterns

---

## Related Resources

- [OAuth Integration Guide](./oauth_integration.md)
- [Submission Requirements](./submission_requirements.md)
- [Troubleshooting Guide](./troubleshooting.md)
