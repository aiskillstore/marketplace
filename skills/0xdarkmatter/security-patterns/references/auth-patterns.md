# Authentication Patterns

Secure authentication implementation patterns.

## Password Hashing

### bcrypt (Recommended)

```python
import bcrypt

def hash_password(password: str) -> bytes:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)  # Cost factor 12
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Usage
hashed = hash_password("user_password")
is_valid = verify_password("user_password", hashed)
```

### Argon2 (Modern Alternative)

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,      # Iterations
    memory_cost=65536, # 64MB
    parallelism=4,     # Threads
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, password)
        return True
    except:
        return False
```

## Session Management

### Secure Session Configuration

```python
from flask import Flask
from datetime import timedelta

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],  # Strong random key
    SESSION_COOKIE_NAME='__session',
    SESSION_COOKIE_SECURE=True,           # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,         # No JavaScript access
    SESSION_COOKIE_SAMESITE='Strict',     # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)
```

### Session Token Generation

```python
import secrets

def generate_session_id() -> str:
    """Generate cryptographically secure session ID."""
    return secrets.token_urlsafe(32)  # 256 bits of entropy

def generate_csrf_token() -> str:
    """Generate CSRF token."""
    return secrets.token_hex(32)
```

## JWT Patterns

### JWT Generation

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ['JWT_SECRET']
ALGORITHM = "HS256"

def create_token(user_id: int, expires_delta: timedelta = timedelta(hours=1)) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16),  # Unique token ID
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")
```

### JWT Best Practices

```python
# DO
- Use strong secret (256+ bits)
- Set short expiration (15min - 1hr)
- Include jti for revocation
- Use HTTPS only
- Store in httpOnly cookie (not localStorage)

# DON'T
- Store sensitive data in payload (it's base64, not encrypted)
- Use long expiration times
- Send in URL parameters
- Use weak algorithms (none, HS256 with weak key)
```

### Refresh Token Pattern

```python
def create_tokens(user_id: int) -> tuple[str, str]:
    """Create access and refresh token pair."""
    access_token = create_token(
        user_id,
        expires_delta=timedelta(minutes=15),
        token_type="access"
    )
    refresh_token = create_token(
        user_id,
        expires_delta=timedelta(days=7),
        token_type="refresh"
    )
    return access_token, refresh_token

def refresh_access_token(refresh_token: str) -> str:
    """Generate new access token from refresh token."""
    payload = verify_token(refresh_token)

    if payload.get("token_type") != "refresh":
        raise AuthError("Not a refresh token")

    # Check if refresh token is revoked
    if is_token_revoked(payload["jti"]):
        raise AuthError("Token revoked")

    return create_token(payload["sub"], token_type="access")
```

## OAuth 2.0 Flow

### Authorization Code Flow

```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/callback/google')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('oauth2/v3/userinfo').json()

    # Find or create user
    user = find_or_create_user(
        email=user_info['email'],
        name=user_info['name'],
        oauth_provider='google',
        oauth_id=user_info['sub']
    )

    login_user(user)
    return redirect('/')
```

## Multi-Factor Authentication

### TOTP Implementation

```python
import pyotp

def generate_totp_secret() -> str:
    """Generate new TOTP secret for user."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str) -> str:
    """Generate URI for authenticator app."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="MyApp")

def verify_totp(secret: str, code: str) -> bool:
    """Verify TOTP code."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 30s drift
```

### Backup Codes

```python
def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate one-time backup codes."""
    return [secrets.token_hex(4) for _ in range(count)]

def use_backup_code(user_id: int, code: str) -> bool:
    """Verify and consume backup code."""
    user = get_user(user_id)
    if code in user.backup_codes:
        user.backup_codes.remove(code)
        user.save()
        return True
    return False
```

## Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # Rate limited to 5 attempts per minute per IP
    pass

@app.route("/api/sensitive")
@limiter.limit("10 per minute", key_func=lambda: current_user.id)
def sensitive_endpoint():
    # Rate limited per user, not IP
    pass
```

## Account Security

### Account Lockout

```python
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)

def record_failed_login(user_id: int) -> None:
    user = get_user(user_id)
    user.failed_login_attempts += 1
    user.last_failed_login = datetime.utcnow()

    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
        security_logger.warning(f"Account locked: {user.email}")

    user.save()

def check_account_locked(user_id: int) -> bool:
    user = get_user(user_id)
    if user.locked_until and user.locked_until > datetime.utcnow():
        return True
    return False

def reset_failed_attempts(user_id: int) -> None:
    user = get_user(user_id)
    user.failed_login_attempts = 0
    user.locked_until = None
    user.save()
```

### Password Reset

```python
def create_reset_token(user_id: int) -> str:
    """Create password reset token."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)

    # Store hash of token, not token itself
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    store_reset_token(user_id, token_hash, expires)

    return token

def verify_reset_token(token: str) -> int | None:
    """Verify reset token and return user_id."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = get_reset_token(token_hash)

    if not record or record.expires < datetime.utcnow():
        return None

    # Invalidate token after use
    delete_reset_token(token_hash)
    return record.user_id
```
