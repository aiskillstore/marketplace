# API Authentication Patterns

Comprehensive guide to implementing authentication and authorization in APIs.

## Table of Contents

- [OAuth 2.0 Flows](#oauth-20-flows)
- [JWT Token Design](#jwt-token-design)
- [API Key Authentication](#api-key-authentication)
- [Session-Based Authentication](#session-based-authentication)
- [Security Best Practices](#security-best-practices)

## OAuth 2.0 Flows

### Authorization Code Flow

**Use Case**: Web applications with backend server

**Flow Diagram**:
```
1. Client redirects user to authorization server
   GET /oauth/authorize?
     client_id=CLIENT_ID&
     redirect_uri=CALLBACK_URL&
     response_type=code&
     scope=read write&
     state=RANDOM_STATE

2. User authenticates and grants permission

3. Authorization server redirects back with code
   GET CALLBACK_URL?code=AUTH_CODE&state=RANDOM_STATE

4. Client exchanges code for token
   POST /oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "redirect_uri": "CALLBACK_URL",
     "client_id": "CLIENT_ID",
     "client_secret": "CLIENT_SECRET"
   }

5. Response contains access token
   {
     "access_token": "eyJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "def50200...",
     "scope": "read write"
   }
```

**Security Considerations**:
- Always validate `state` parameter to prevent CSRF attacks
- Use HTTPS for all OAuth endpoints
- Store client_secret securely, never expose to client-side code
- Implement token expiration and refresh
- Validate redirect_uri against registered URIs

### Client Credentials Flow

**Use Case**: Service-to-service authentication (machine-to-machine)

**Flow**:
```
POST /oauth/token
{
  "grant_type": "client_credentials",
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET",
  "scope": "read write"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

**Best Practices**:
- Use for server-to-server communication only
- Limit scope to minimum required permissions
- Rotate client secrets regularly
- Monitor and log all client credential usage
- Implement rate limiting per client

### PKCE Flow (Proof Key for Code Exchange)

**Use Case**: Mobile apps and Single Page Applications (SPAs)

**Flow**:
```
1. Generate code_verifier (random string, 43-128 characters)
   Example: dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk

2. Generate code_challenge from code_verifier
   code_challenge = BASE64URL(SHA256(code_verifier))

3. Authorization request
   GET /oauth/authorize?
     client_id=CLIENT_ID&
     redirect_uri=CALLBACK&
     response_type=code&
     code_challenge=CHALLENGE&
     code_challenge_method=S256&
     scope=read write&
     state=RANDOM_STATE

4. User authenticates

5. Receive authorization code
   CALLBACK?code=AUTH_CODE&state=RANDOM_STATE

6. Exchange code for token (with verifier)
   POST /oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "CLIENT_ID",
     "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
     "redirect_uri": "CALLBACK"
   }
```

**Why PKCE?**:
- Prevents authorization code interception attacks
- No need for client_secret (safe for public clients)
- Required for mobile and SPA applications
- Recommended even for confidential clients

### Refresh Token Flow

**Use Case**: Obtaining new access tokens without re-authentication

**Flow**:
```
POST /oauth/token
{
  "grant_type": "refresh_token",
  "refresh_token": "def50200...",
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET"  // Only for confidential clients
}

Response:
{
  "access_token": "new_access_token",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token",  // Optionally rotate
  "scope": "read write"
}
```

**Best Practices**:
- Implement refresh token rotation (issue new refresh token each time)
- Set longer expiration for refresh tokens (days/weeks vs minutes for access tokens)
- Store refresh tokens securely (encrypted at rest)
- Invalidate old refresh token when new one is issued
- Implement refresh token revocation

## JWT Token Design

### Token Structure

JWT consists of three parts: Header.Payload.Signature

**Header**:
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-id-2025"
}
```

**Payload**:
```json
{
  "sub": "usr_1234567890",
  "iat": 1698336000,
  "exp": 1698339600,
  "nbf": 1698336000,
  "jti": "unique-token-id",
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "scope": ["read:posts", "write:posts"],
  "roles": ["user", "editor"]
}
```

**Standard Claims**:
- `sub` (subject): User identifier
- `iat` (issued at): Token creation timestamp
- `exp` (expiration): Token expiration timestamp
- `nbf` (not before): Token valid from timestamp
- `jti` (JWT ID): Unique token identifier
- `iss` (issuer): Token issuer
- `aud` (audience): Intended token recipient

**Custom Claims**:
- `scope`: Array of permission scopes
- `roles`: User roles
- `email`: User email (if needed)
- `name`: User display name

### Using JWT in Requests

**Authorization Header** (recommended):
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameter** (avoid for security reasons):
```http
GET /api/resource?access_token=eyJhbGc...
```

### JWT Validation

**Server-side validation steps**:
1. Verify signature using public key
2. Check expiration (`exp` claim)
3. Verify issuer (`iss` claim)
4. Verify audience (`aud` claim)
5. Check not-before (`nbf` claim)
6. Validate custom claims (scope, roles)

**Example validation code**:
```python
import jwt
from datetime import datetime

def validate_jwt(token, public_key):
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="https://api.example.com",
            issuer="https://auth.example.com"
        )

        # Additional custom validation
        if "read:posts" not in payload.get("scope", []):
            raise ValueError("Insufficient permissions")

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
```

### Token Rotation and Revocation

**Rotation Strategy**:
- Short-lived access tokens (15-60 minutes)
- Long-lived refresh tokens (days to weeks)
- Rotate refresh tokens on use
- Issue new access token before expiration

**Revocation**:
- Maintain token blacklist for revoked tokens
- Use Redis or similar for fast blacklist lookups
- Clear blacklist entries after token expiration
- Consider token versioning for mass revocation

## API Key Authentication

### Implementation Patterns

**Header-Based** (recommended):
```http
X-API-Key: sk_live_abc123def456
# Or
Authorization: ApiKey sk_live_abc123def456
```

**Query Parameter** (less secure, use only for public data):
```http
GET /api/data?api_key=sk_live_abc123def456
```

### API Key Design

**Key Format**:
```
sk_[environment]_[random_string]

Examples:
sk_live_abc123def456ghi789
sk_test_xyz987uvw654rst321
```

**Key Metadata**:
```json
{
  "keyId": "key_abc123",
  "key": "sk_live_abc123def456",
  "name": "Production API Key",
  "userId": "usr_1234567890",
  "scopes": ["read:posts", "write:posts"],
  "rateLimit": 1000,
  "createdAt": "2025-10-25T10:00:00Z",
  "expiresAt": "2026-10-25T10:00:00Z",
  "lastUsedAt": "2025-10-25T14:30:00Z"
}
```

### Best Practices

**Key Management**:
- Generate cryptographically random keys (minimum 32 bytes)
- Hash keys before storing in database
- Support multiple keys per account
- Allow key naming and description
- Implement key rotation workflow

**Security**:
- Different keys for different environments (dev, staging, prod)
- Implement key expiration dates
- Log all key usage with timestamps and IPs
- Rate limit per key
- Never expose keys in client-side code
- Provide key rolling/rotation mechanism

**Key Rotation**:
```
1. Generate new API key
2. Provide transition period (both keys work)
3. Notify user of deprecation timeline
4. Revoke old key after transition period
```

## Session-Based Authentication

### Traditional Session Flow

```
1. User submits credentials
   POST /auth/login
   { "email": "user@example.com", "password": "..." }

2. Server validates and creates session
   Session ID: sess_abc123
   Stores: { userId: "usr_123", loginTime: "...", ... }

3. Server sets session cookie
   Set-Cookie: sessionId=sess_abc123; HttpOnly; Secure; SameSite=Strict

4. Client includes cookie in subsequent requests
   Cookie: sessionId=sess_abc123

5. Server validates session on each request
```

### Session Security

**Cookie Attributes**:
```http
Set-Cookie: sessionId=sess_abc123;
  HttpOnly;           # Prevents JavaScript access
  Secure;             # HTTPS only
  SameSite=Strict;    # CSRF protection
  Path=/;             # Cookie scope
  Max-Age=3600;       # Expiration in seconds
  Domain=.example.com # Cookie domain
```

**Session Storage**:
- Store sessions in Redis or similar for performance
- Implement session expiration
- Clean up expired sessions regularly
- Use secure session ID generation
- Implement session fixation protection

## Security Best Practices

### General Security

**HTTPS Everywhere**:
- Enforce HTTPS for all endpoints
- Use HSTS header
- Implement certificate pinning for mobile apps

**Token Security**:
- Never log tokens or credentials
- Rotate secrets regularly
- Use environment variables for secrets
- Implement token binding (bind token to client)

### Rate Limiting

**Implementation**:
```http
# Request headers
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1698340800

# When exceeded
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

**Strategies**:
- Per user/API key
- Per IP address
- Per endpoint
- Sliding window vs fixed window
- Distributed rate limiting (Redis)

### Defense Against Common Attacks

**CSRF Protection**:
- Use SameSite cookie attribute
- Implement CSRF tokens
- Validate Origin/Referer headers

**XSS Protection**:
- Sanitize user input
- Set Content-Security-Policy headers
- Use HttpOnly cookies

**Brute Force Protection**:
- Implement account lockout
- Use CAPTCHA after failed attempts
- Exponential backoff
- Monitor suspicious patterns

**Injection Attacks**:
- Validate and sanitize all input
- Use parameterized queries
- Implement input length limits
- Reject unexpected characters

### Monitoring and Logging

**What to Log**:
- Authentication attempts (success and failure)
- Token generation and refresh
- API key usage
- Rate limit violations
- Permission denials
- Suspicious patterns

**What NOT to Log**:
- Passwords or credentials
- Full tokens (log only last 4 characters)
- API keys (log key ID only)
- Sensitive user data

### Multi-Factor Authentication (MFA)

**Implementation Flow**:
```
1. User provides username/password
2. Server validates primary credentials
3. Server generates MFA challenge (TOTP, SMS, etc.)
4. User provides MFA code
5. Server validates MFA code
6. Server issues access token
```

**MFA Methods**:
- TOTP (Time-based One-Time Password) - Google Authenticator
- SMS codes (less secure, but convenient)
- Email codes
- Hardware tokens (YubiKey)
- Biometric authentication
- Backup codes

**Best Practices**:
- Store recovery codes for account recovery
- Allow multiple MFA methods
- Implement MFA remember device
- Provide clear setup instructions
- Support MFA reset process
