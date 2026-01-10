# aiohttp Patterns

HTTP client and server patterns with aiohttp.

## Client Session Best Practices

```python
import aiohttp

# WRONG - creates session per request
async def bad_fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# CORRECT - reuse session
async def fetch_all(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_one(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()
```

## Connection Pooling

```python
import aiohttp

# Configure connection pool
connector = aiohttp.TCPConnector(
    limit=100,           # Max connections
    limit_per_host=10,   # Max per host
    ttl_dns_cache=300,   # DNS cache TTL
)

async with aiohttp.ClientSession(connector=connector) as session:
    # Use session
    pass
```

## Timeout Configuration

```python
import aiohttp

timeout = aiohttp.ClientTimeout(
    total=30,        # Total timeout
    connect=10,      # Connection timeout
    sock_read=10,    # Read timeout
    sock_connect=10, # Socket connect timeout
)

async with aiohttp.ClientSession(timeout=timeout) as session:
    async with session.get(url) as response:
        return await response.text()
```

## Request Methods

```python
async with aiohttp.ClientSession() as session:
    # GET
    async with session.get(url, params={'key': 'value'}) as r:
        data = await r.json()

    # POST JSON
    async with session.post(url, json={'key': 'value'}) as r:
        data = await r.json()

    # POST form data
    async with session.post(url, data={'key': 'value'}) as r:
        data = await r.text()

    # PUT
    async with session.put(url, json={'key': 'value'}) as r:
        pass

    # DELETE
    async with session.delete(url) as r:
        pass

    # With headers
    headers = {'Authorization': 'Bearer token'}
    async with session.get(url, headers=headers) as r:
        pass
```

## Response Handling

```python
async with session.get(url) as response:
    # Status
    print(response.status)  # 200
    print(response.reason)  # OK

    # Headers
    print(response.headers['Content-Type'])

    # Body
    text = await response.text()
    json_data = await response.json()
    bytes_data = await response.read()

    # Streaming
    async for chunk in response.content.iter_chunked(1024):
        process(chunk)
```

## Error Handling

```python
import aiohttp

async def safe_fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        print(f"HTTP error: {e.status}")
    except aiohttp.ClientConnectionError:
        print("Connection error")
    except aiohttp.ClientTimeout:
        print("Request timed out")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None
```

## Retry with Backoff

```python
async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    max_retries: int = 3
) -> dict | None:
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return None
```

## File Upload

```python
async def upload_file(session, url, file_path):
    with open(file_path, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename='upload.txt')
        async with session.post(url, data=data) as response:
            return await response.json()
```

## File Download

```python
async def download_file(session, url, dest_path):
    async with session.get(url) as response:
        with open(dest_path, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                f.write(chunk)
```

## WebSocket Client

```python
async def websocket_client(url):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            # Send message
            await ws.send_str("Hello")

            # Receive messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(f"Received: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
```

## Simple aiohttp Server

```python
from aiohttp import web

async def handle_get(request):
    name = request.match_info.get('name', 'World')
    return web.json_response({'message': f'Hello, {name}'})

async def handle_post(request):
    data = await request.json()
    return web.json_response({'received': data})

app = web.Application()
app.router.add_get('/', handle_get)
app.router.add_get('/{name}', handle_get)
app.router.add_post('/data', handle_post)

if __name__ == '__main__':
    web.run_app(app, port=8080)
```

## Server Middleware

```python
from aiohttp import web

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException:
        raise
    except Exception as e:
        return web.json_response(
            {'error': str(e)},
            status=500
        )

@web.middleware
async def logging_middleware(request, handler):
    print(f"{request.method} {request.path}")
    response = await handler(request)
    print(f"Response: {response.status}")
    return response

app = web.Application(middlewares=[logging_middleware, error_middleware])
```

## Session State

```python
from aiohttp import web

async def init_db(app):
    app['db'] = await create_db_pool()

async def cleanup_db(app):
    await app['db'].close()

app = web.Application()
app.on_startup.append(init_db)
app.on_cleanup.append(cleanup_db)

async def handler(request):
    db = request.app['db']
    # Use db connection
```
