# HTTP Security Headers

Essential security headers for web applications.

## Complete Header Set

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
X-XSS-Protection: 0
```

## Content-Security-Policy (CSP)

### Basic CSP

```
Content-Security-Policy: default-src 'self'
```

### Detailed CSP Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `default-src` | Fallback for other directives | `'self'` |
| `script-src` | JavaScript sources | `'self' https://cdn.example.com` |
| `style-src` | CSS sources | `'self' 'unsafe-inline'` |
| `img-src` | Image sources | `'self' data: https:` |
| `font-src` | Font sources | `'self' https://fonts.gstatic.com` |
| `connect-src` | AJAX, WebSocket, fetch | `'self' https://api.example.com` |
| `frame-src` | iframe sources | `'none'` |
| `frame-ancestors` | Who can embed this page | `'none'` |
| `base-uri` | Restrict base element | `'self'` |
| `form-action` | Form submission targets | `'self'` |
| `upgrade-insecure-requests` | Upgrade HTTP to HTTPS | (no value) |

### CSP Values

```
'self'          - Same origin
'none'          - Block all
'unsafe-inline' - Allow inline (avoid!)
'unsafe-eval'   - Allow eval() (avoid!)
'strict-dynamic' - Trust scripts loaded by trusted scripts
'nonce-abc123'  - Allow specific inline with nonce
'sha256-...'    - Allow specific inline by hash
https:          - Any HTTPS URL
data:           - Data URLs
```

### CSP for Common Frameworks

#### React/Vue/Angular (Production)

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https://api.yourapp.com
```

#### With CDN

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net
```

### Report-Only Mode

```
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

## Strict-Transport-Security (HSTS)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

- `max-age=31536000` - Browser remembers for 1 year
- `includeSubDomains` - Apply to all subdomains
- `preload` - Submit to browser preload lists

### Implementation

```python
# Flask
@app.after_request
def add_hsts(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Express
app.use(helmet.hsts({
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
}))
```

## X-Frame-Options

```
X-Frame-Options: DENY
```

- `DENY` - Never allow framing
- `SAMEORIGIN` - Only same origin can frame
- `ALLOW-FROM uri` - Specific origin (deprecated, use CSP)

## X-Content-Type-Options

```
X-Content-Type-Options: nosniff
```

Prevents MIME type sniffing. Always use this.

## Referrer-Policy

```
Referrer-Policy: strict-origin-when-cross-origin
```

| Value | Behavior |
|-------|----------|
| `no-referrer` | Never send referrer |
| `same-origin` | Only to same origin |
| `strict-origin` | Send origin only, not path |
| `strict-origin-when-cross-origin` | Full URL same-origin, origin cross-origin |

## Permissions-Policy

```
Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
```

Disable browser features you don't use:

```
Permissions-Policy:
  camera=(),              # Disable camera
  microphone=(),          # Disable microphone
  geolocation=(self),     # Only this origin
  payment=*               # Allow all
```

## Implementation Examples

### Python Flask

```python
from flask import Flask

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

### Python FastAPI

```python
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response
```

### Node.js Express (Helmet)

```javascript
const helmet = require('helmet');

app.use(helmet());

// Or with custom config
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", "cdn.example.com"],
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
    }
}));
```

### Nginx

```nginx
add_header Content-Security-Policy "default-src 'self'" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Testing Headers

```bash
# Check headers with curl
curl -I https://example.com

# Security header scanner
# https://securityheaders.com

# Mozilla Observatory
# https://observatory.mozilla.org
```

## Quick Checklist

- [ ] CSP with restrictive default-src
- [ ] HSTS with 1 year max-age
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] Referrer-Policy set
- [ ] Permissions-Policy restricting unused features
- [ ] No X-Powered-By header (remove it)
- [ ] Test with securityheaders.com
