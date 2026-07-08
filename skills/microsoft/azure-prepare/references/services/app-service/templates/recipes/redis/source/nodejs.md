# Redis Recipe — Node.js — REFERENCE ONLY

## ioredis with Token Refresh

### npm Packages

```bash
npm install ioredis @azure/identity
```

### Cache Module

Create `src/cache.js`:

```javascript
const Redis = require("ioredis");
const { DefaultAzureCredential } = require("@azure/identity");

const credential = new DefaultAzureCredential();
const TOKEN_SCOPE = "https://redis.azure.com/.default";
// Redis ACL auth requires both username and token as password
const REDIS_USERNAME = "default";
const TOKEN_REFRESH_MARGIN = 5 * 60 * 1000; // 5 minutes in ms

let _client = null;
let _tokenExpiry = 0;

async function getToken() {
  const tok = await credential.getToken(TOKEN_SCOPE);
  _tokenExpiry = tok.expiresOnTimestamp;
  return tok.token;
}

async function getRedisClient() {
  const now = Date.now();
  if (_client && now < _tokenExpiry - TOKEN_REFRESH_MARGIN) {
    return _client;
  }

  // Token expired or about to expire — create a new client with a fresh token
  if (_client) {
    _client.disconnect();
    _client = null;
  }

  const token = await getToken();
  _client = new Redis({
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || "6380"),
    tls: { servername: process.env.REDIS_HOST },
    username: REDIS_USERNAME,
    password: token,
    lazyConnect: true,
  });
  await _client.connect();
  return _client;
}

module.exports = { getRedisClient };
```

> ⚠️ Entra ID tokens expire in ~1 hour. `getRedisClient()` recreates the connection with a fresh token when the current one is within 5 minutes of expiry. Always call `getRedisClient()` before each operation rather than caching the client reference long-term.

### Usage

```javascript
const { getRedisClient } = require("./cache");

app.get("/api/cached", async (req, res) => {
  const client = await getRedisClient();
  let value = await client.get("my-key");
  if (!value) {
    value = "computed-value";
    await client.setex("my-key", 300, value); // TTL 5 minutes
  }
  res.json({ value });
});
```

## Files to Modify

| File | Action |
|------|--------|
| `src/cache.js` | Create — Redis client with token refresh |
| `src/index.js` | Modify — use getRedisClient() |
| `package.json` | Modify — add ioredis, @azure/identity |
