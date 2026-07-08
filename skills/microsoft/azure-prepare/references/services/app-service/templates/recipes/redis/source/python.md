# Redis Recipe — Python — REFERENCE ONLY

## Redis Client with Token Refresh

### Requirements

Add to `requirements.txt`:

```
redis>=5.0
azure-identity
```

### Cache Module

Create `cache.py`:

```python
import os
import time
import threading
import redis
from azure.identity import DefaultAzureCredential

# Redis ACL auth requires both username and token as password
_REDIS_USERNAME = "default"
_TOKEN_SCOPE = "https://redis.azure.com/.default"
_TOKEN_REFRESH_MARGIN = 300  # Refresh 5 minutes before expiry

_credential = DefaultAzureCredential()
_lock = threading.RLock()  # reentrant — get_cache() calls _get_token() while holding the lock
_token_cache: dict = {}


def _get_token():
    """Return a valid Entra ID token, refreshing if within expiry margin."""
    with _lock:
        now = time.time()
        if not _token_cache or now >= _token_cache["expires_on"] - _TOKEN_REFRESH_MARGIN:
            tok = _credential.get_token(_TOKEN_SCOPE)
            _token_cache["token"] = tok.token
            _token_cache["expires_on"] = tok.expires_on
        return _token_cache["token"]


def create_redis_client() -> redis.Redis:
    """Create a Redis client. Token is refreshed on each call via _get_token()."""
    return redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ.get("REDIS_PORT", 6380)),
        ssl=True,
        username=_REDIS_USERNAME,
        password=_get_token(),
        decode_responses=True,
    )


def get_cache() -> redis.Redis:
    """Lazy/refreshing accessor — call this from request handlers instead of holding a module-level client.
    Recreates the client when the cached token is within the refresh margin and closes the prior one."""
    global _client
    with _lock:
        now = time.time()
        if _client is None or now >= _token_cache.get("expires_on", 0) - _TOKEN_REFRESH_MARGIN:
            old = _client
            _client = create_redis_client()
            if old is not None:
                try:
                    old.close()
                except Exception:
                    pass
        return _client


_client: redis.Redis | None = None
```

> ⚠️ Entra ID tokens expire in ~1 hour. The `_get_token()` helper refreshes proactively 5 minutes before expiry, and `get_cache()` recreates the underlying client so in-flight pool connections pick up the new token. Always call `get_cache()` from request handlers — never cache the client at module scope across the token lifetime.

### Usage

```python
from cache import get_cache

def get_cached(key: str):
    cache = get_cache()
    value = cache.get(key)
    if value is None:
        value = "computed-value"
        cache.setex(key, 300, value)  # TTL 5 minutes
    return value
```

## Files to Modify

| File | Action |
|------|--------|
| `cache.py` | Create — Redis client with token refresh |
| `main.py` | Modify — use cache client |
| `requirements.txt` | Modify — add redis, azure-identity |
