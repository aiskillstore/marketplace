# Auth Recipe — Node.js (Express) — REFERENCE ONLY

## JWT Validation with jsonwebtoken + jwks-rsa

### npm Packages

```bash
npm install jsonwebtoken jwks-rsa
```

### Auth Middleware

Add `middleware/auth.js`:

```javascript
const jwt = require("jsonwebtoken");
const jwksClient = require("jwks-rsa");

const client = jwksClient({
  jwksUri: `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}/discovery/v2.0/keys`,
  cache: true,
  rateLimit: true,
});

// Use APP_ID_URI if set (e.g., "api://<client-id>"); fall back to CLIENT_ID
const AUDIENCE = process.env.AZURE_APP_ID_URI || process.env.AZURE_CLIENT_ID;

function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "No token" });

  const decoded = jwt.decode(token, { complete: true });
  if (!decoded || !decoded.header || !decoded.header.kid) {
    return res.status(401).json({ error: "Invalid token" });
  }

  client.getSigningKey(decoded.header.kid, (err, key) => {
    if (err || !key) {
      return res.status(401).json({ error: "Invalid token" });
    }

    jwt.verify(
      token,
      key.getPublicKey(),
      {
        algorithms: ["RS256"],
        audience: AUDIENCE,
        issuer: `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}/v2.0`,
      },
      (err, payload) => {
        if (err) return res.status(401).json({ error: "Invalid token" });
        req.user = payload;
        next();
      }
    );
  });
}

module.exports = { authMiddleware };
```

> ⚠️ The `aud` claim in Entra ID tokens is often the Application ID URI (`api://<client-id>`), not the raw client ID. Set `AZURE_APP_ID_URI` in app settings to match your app registration's exposed API URI.

### Protected Endpoint

Add to `src/index.js`:

```javascript
const { authMiddleware } = require("./middleware/auth");

app.get("/api/me", authMiddleware, (req, res) => {
  res.json({ name: req.user?.name, oid: req.user?.oid });
});
```

## App Settings Required

| Setting | Value |
|---------|-------|
| `AZURE_TENANT_ID` | Entra tenant ID |
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_APP_ID_URI` | Application ID URI (e.g., `api://<client-id>`) — optional, defaults to CLIENT_ID |

## Files to Modify

| File | Action |
|------|--------|
| `middleware/auth.js` | Create — JWT validation middleware |
| `src/index.js` | Modify — add protected routes |
| `package.json` | Modify — add jsonwebtoken, jwks-rsa |
