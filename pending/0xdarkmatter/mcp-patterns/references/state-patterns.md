# MCP State Management Patterns

Patterns for persisting and caching state in MCP servers.

## SQLite for Persistence

```python
import aiosqlite

DB_PATH = Path.home() / ".my-mcp-server" / "state.db"

async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TEXT
            )
        """)
        await db.commit()

async def get_cached(key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT value FROM cache WHERE key = ? AND expires_at > datetime('now')",
            (key,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

async def set_cached(key: str, value: str, ttl_seconds: int = 3600):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, datetime('now', '+' || ? || ' seconds'))",
            (key, value, ttl_seconds)
        )
        await db.commit()
```

## In-Memory Cache

```python
from functools import lru_cache
from cachetools import TTLCache

# Simple TTL cache
cache = TTLCache(maxsize=100, ttl=300)  # 5 minute TTL

async def get_data(key: str):
    if key in cache:
        return cache[key]
    data = await fetch_from_api(key)
    cache[key] = data
    return data
```
