# Production Deployment Guide

## Environment Configuration

### Production Checklist
- [ ] Use environment variables for all secrets
- [ ] Configure logging to files with rotation
- [ ] Set appropriate log levels (INFO or WARNING)
- [ ] Enable monitoring and health checks
- [ ] Configure rate limiting
- [ ] Set up error alerting
- [ ] Document deployment process
- [ ] Implement graceful shutdown
- [ ] Configure connection pooling
- [ ] Set up backup and recovery

### Production Server Template
```python
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = ENVIRONMENT == "development"

# Logging
log_level = logging.DEBUG if DEBUG else logging.INFO
log_handler = RotatingFileHandler(
    "mcp_server.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
logger.addHandler(log_handler)

# Secrets (from environment)
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY or not DATABASE_URL:
    raise ValueError("Missing required environment variables")

# Rate limiting
MAX_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT", "100"))

# Initialize server
app = Server(
    name="production-server",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# Request tracking
request_count = 0

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    global request_count
    request_count += 1
    request_id = f"req_{request_count}"

    logger.info(f"[{request_id}] Tool call: {name}")
    logger.debug(f"[{request_id}] Arguments: {arguments}")

    start_time = datetime.now()

    try:
        result = await execute_tool(name, arguments)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{request_id}] Success in {duration:.2f}s")
        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"[{request_id}] Failed in {duration:.2f}s: {str(e)}",
            exc_info=True
        )
        raise

async def main():
    logger.info(f"Starting MCP server in {ENVIRONMENT} mode")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Monitoring

### Health Check Implementation
```python
from datetime import datetime

health_stats = {
    "start_time": datetime.now(),
    "request_count": 0,
    "error_count": 0
}

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    health_stats["request_count"] += 1

    if name == "health_check":
        uptime = (datetime.now() - health_stats["start_time"]).total_seconds()
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "healthy",
                "uptime_seconds": uptime,
                "total_requests": health_stats["request_count"],
                "error_count": health_stats["error_count"],
                "error_rate": health_stats["error_count"] / health_stats["request_count"] if health_stats["request_count"] > 0 else 0
            })
        )]

    try:
        return await execute_tool(name, arguments)
    except Exception as e:
        health_stats["error_count"] += 1
        raise
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
request_counter = Counter('mcp_requests_total', 'Total requests', ['tool_name'])
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration', ['tool_name'])
error_counter = Counter('mcp_errors_total', 'Total errors', ['tool_name', 'error_type'])

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    request_counter.labels(tool_name=name).inc()

    with request_duration.labels(tool_name=name).time():
        try:
            return await execute_tool(name, arguments)
        except Exception as e:
            error_counter.labels(
                tool_name=name,
                error_type=type(e).__name__
            ).inc()
            raise

# Start metrics server
start_http_server(9090)
```

## Scaling Considerations

### Horizontal Scaling with Redis
```python
import aioredis

class ScalableMCPServer:
    def __init__(self):
        self.redis = None

    async def initialize(self):
        """Initialize shared resources"""
        self.redis = await aioredis.create_redis_pool(
            os.getenv("REDIS_URL", "redis://localhost")
        )

    async def get_cached(self, key: str):
        """Get from shared cache"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set_cached(self, key: str, value, ttl: int = 300):
        """Set in shared cache with TTL"""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
```

### Connection Pooling
```python
import aiohttp

class APIClient:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def fetch(self, url: str):
        async with self.session.get(url) as response:
            return await response.json()

# Usage
client = APIClient()

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with client:
        data = await client.fetch(arguments["url"])
        return [TextContent(type="text", text=json.dumps(data))]
```

### Caching Strategy
```python
from functools import lru_cache
from datetime import datetime, timedelta
import asyncio

class AsyncLRUCache:
    def __init__(self, maxsize: int, ttl: timedelta):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl

    async def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    async def set(self, key: str, value):
        if len(self.cache) >= self.maxsize:
            # Remove oldest entry
            oldest = min(self.cache.items(), key=lambda x: x[1][1])
            del self.cache[oldest[0]]

        self.cache[key] = (value, datetime.now())

# Usage
cache = AsyncLRUCache(maxsize=1000, ttl=timedelta(minutes=5))

async def fetch_user_data(user_id: str):
    # Check cache
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return cached

    # Fetch from database
    data = await database.get_user(user_id)

    # Cache result
    await cache.set(f"user:{user_id}", data)

    return data
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run as non-root user
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# Set environment
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Run server
CMD ["python", "server.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    environment:
      - ENVIRONMENT=production
      - API_KEY=${API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

## Graceful Shutdown

```python
import signal
import asyncio

shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    logger.info("Starting MCP server")

    try:
        async with stdio_server() as (read_stream, write_stream):
            # Run server with shutdown monitoring
            server_task = asyncio.create_task(
                app.run(read_stream, write_stream, app.create_initialization_options())
            )
            shutdown_task = asyncio.create_task(shutdown_event.wait())

            # Wait for either server completion or shutdown signal
            done, pending = await asyncio.wait(
                [server_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()

    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Alerting

### Sentry Integration
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "production"),
    traces_sample_rate=1.0
)

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        return await execute_tool(name, arguments)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.exception(f"Tool {name} failed")
        raise
```

## Backup and Recovery

### State Backup
```python
import json
from pathlib import Path

async def backup_state():
    """Backup server state"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "metrics": health_stats,
        "cache_keys": list(cache.cache.keys())
    }

    backup_path = Path("backups") / f"state_{datetime.now():%Y%m%d_%H%M%S}.json"
    backup_path.parent.mkdir(exist_ok=True)

    with open(backup_path, 'w') as f:
        json.dump(state, f, indent=2)

    logger.info(f"State backed up to {backup_path}")

# Schedule periodic backups
async def backup_scheduler():
    while True:
        await asyncio.sleep(3600)  # Backup every hour
        await backup_state()
```
