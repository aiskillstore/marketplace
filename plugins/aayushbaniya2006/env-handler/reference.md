# Environment Variables Reference

## Files & Purpose

| File | Git Status | Purpose | Content Style |
|------|------------|---------|---------------|
| `.env` | Committed ✅ | **Template & Defaults** | `KEY=""` (Secrets)<br>`KEY="val"` (Defaults) |
| `.env.local` | Ignored 🚫 | **Secrets & Overrides** | `KEY="sk-123..."`<br>`KEY="override"` |
| `.env.example` | **FORBIDDEN** ❌ | Do not use | N/A |

## Best Practices

### 1. Variable Naming
-   **Server Secrets**: `UPPER_CASE` (e.g., `STRIPE_SECRET_KEY`)
-   **Public/Client**: Prefix with `NEXT_PUBLIC_` (e.g., `NEXT_PUBLIC_STRIPE_KEY`)

### 2. Security
-   Never commit real API keys to `.env`.
-   If you accidentally commit a key, rotate it immediately.

### 3. Deployment (Vercel)
-   In production (Vercel), variables from `.env.local` must be added to the **Project Settings > Environment Variables**.
-   Variables in `.env` are automatically picked up if the file is committed, but usually, it's better to define them in Vercel for consistency.

## Example

**Local Development:**

`.env`:
```bash
# Database
DATABASE_URL=""

# Auth
NEXTAUTH_SECRET=""
NEXTAUTH_URL="http://localhost:3000"

# Feature Flags
NEXT_PUBLIC_ENABLE_AI="true"
```

`.env.local`:
```bash
# Secrets
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
NEXTAUTH_SECRET="super-secret-hash"
```

