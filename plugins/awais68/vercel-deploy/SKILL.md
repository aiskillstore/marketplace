---
name: vercel-deploy
description: |
  Use when deploying Next.js applications to Vercel.
  Triggers for: vercel.json configuration, build optimization, environment variable setup,
  custom domain configuration, API proxy setup, or deployment troubleshooting.
  NOT for: backend-only deployments, non-Vercel hosting, or local development setup.
---

# Vercel Deployment Skill

Expert deployment of Next.js applications to Vercel with optimal build settings, environment configuration, and custom domain setup.

## Quick Reference

| Task | File/Command |
|------|--------------|
| Configure build | `vercel.json` |
| Set env vars | Vercel Dashboard or CLI |
| Deploy | `vercel --prod` |
| Check status | `vercel inspect` |
| Custom domain | Vercel Dashboard > Settings > Domains |

## Project Structure

```
project/
├── vercel.json              # Vercel configuration
├── next.config.js           # Next.js configuration
├── .env.local               # Local development (not committed)
├── .env.example             # Template (committed)
├── docs/
│   └── deployment.md        # Deployment documentation
└── frontend/                # Next.js app
    ├── app/
    ├── public/
    └── src/
```

## vercel.json Configuration

### Basic Configuration

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  }
}
```

### Advanced Configuration with Rewrites

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],

  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.yourdomain.com/:path*"
    }
  ],

  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    },
    {
      "source": "/static/:path*",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/api/:path*",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    }
  ],

  "redirects": [
    {
      "source": "/old-path/:path*",
      "destination": "/new-path/:path*",
      "permanent": true
    },
    {
      "source": "/www/:path*",
      "destination": "/:path*",
      "permanent": true
    }
  ]
}
```

### Next.js Config Integration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output configuration for Vercel
  output: 'standalone',

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.yourdomain.com',
        pathname: '/uploads/**',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/legacy/:path*',
        destination: '/:path*',
        permanent: true,
      },
    ];
  },

  // Experimental features
  experimental: {
    serverActions: {
      allowedOrigins: ['yourdomain.com'],
    },
  },
};

module.exports = nextConfig;
```

## Environment Variables

### Variable Naming Convention

| Prefix | Access | Description |
|--------|--------|-------------|
| `NEXT_PUBLIC_` | Client + Server | Exposed to browser |
| No prefix | Server only | Backend/API use only |

### Required Variables

```bash
# .env.example - Copy to .env.local for local dev

# API Configuration
# Backend API URL (development)
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"

# Authentication
NEXT_PUBLIC_AUTH_ENABLED="true"

# Feature Flags
NEXT_PUBLIC_ENABLE_DARK_MODE="true"
NEXT_PUBLIC_SHOW_BETA_FEATURES="false"
```

### Production Variables (Set in Vercel Dashboard)

```bash
# Environment variables for Production

# API Configuration
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"

# Optional: Analytics
NEXT_PUBLIC_GA_ID="G-XXXXXXXXXX"
NEXT_PUBLIC_POSTHOG_KEY="phc_xxx"

# Optional: Error tracking
NEXT_PUBLIC_SENTRY_DSN="https://xxx@sentry.io/xxx"
```

### Sensitive Variables (Server-Only)

These should NOT have `NEXT_PUBLIC_` prefix:

```bash
# Server-only (never exposed to client)
API_SECRET_KEY="vercel-secret-key"
DATABASE_URL="postgresql://..."
REDIS_URL="redis://..."
```

## Vercel CLI Deployment

### Installation and Login

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Link to project
cd frontend
vercel link
```

### Deployment Commands

```bash
# Deploy to preview (staging)
vercel

# Deploy to production
vercel --prod

# Deploy with environment
vercel --env=NODE_ENV=production

# Pull environment variables from Vercel
vercel env pull .env.local
```

### CI/CD Deployment

```bash
# In CI pipeline
npm i -g vercel
vercel --token=$VERCEL_TOKEN --yes
```

## Custom Domain Setup

### Adding Domain in Vercel

1. Go to Vercel Dashboard > Project > Settings > Domains
2. Add your domain (e.g., `yourdomain.com`)
3. Configure DNS records

### DNS Configuration

```dns
# For root domain (yourdomain.com)
Type: A
Name: @
Value: 76.76.21.21

# For www subdomain
Type: CNAME
Name: www
Value: cname.vercel-dns.com.

# For API subdomain (optional)
Type: CNAME
Name: api
Value: cname.vercel-dns.com.
```

### www to Root Redirect

```json
{
  "redirects": [
    {
      "source": "/:path*",
      "destination": "https://yourdomain.com/:path*",
      "permanent": true
    }
  ]
}
```

## API Proxy Setup

### Option 1: Vercel Rewrites (Recommended)

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.yourdomain.com/:path*"
    }
  ]
}
```

### Option 2: Next.js Rewrite

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
    },
  ];
}
```

### Edge Function for API (Advanced)

```typescript
// frontend/app/api/[...route]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/endpoint`,
    {
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Content-Type': 'application/json',
      },
    }
  );

  const data = await response.json();
  return NextResponse.json(data);
}
```

## Build Optimization

### Build Command

```bash
# Standard build
npm run build

# With TypeScript check only
npm run build -- --no-lint

# Custom build
next build
```

### Performance Settings

```javascript
// next.config.js
const nextConfig = {
  // Enable SWC minifier (faster builds)
  swcMinify: true,

  // Compiler options
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Image optimization
  images: {
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Enable react strict mode
  reactStrictMode: true,

  // Generate Etag
  generateEtags: true,
};
```

### Bundle Analysis

```bash
# Install bundle analyzer
npm install -D @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // your config
});
```

## Error Pages

### Custom 404 Page

```typescript
// frontend/app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">404 - Page Not Found</h1>
      <p className="mt-2 text-gray-600">
        The page you're looking for doesn't exist.
      </p>
      <Link
        href="/"
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Go Home
      </Link>
    </div>
  );
}
```

### Custom 500 Page

```typescript
// frontend/app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">Something went wrong!</h1>
      <p className="mt-2 text-gray-600">
        An unexpected error occurred.
      </p>
      <button
        onClick={() => reset()}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Try Again
      </button>
    </div>
  );
}
```

### Global Error Boundary

```typescript
// frontend/app/global-error.tsx
'use client';

export default function GlobalError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center">
          <h1 className="text-2xl">Application Error</h1>
        </div>
      </body>
    </html>
  );
}
```

## Deployment Checklist

- [ ] **Build succeeds locally**: `npm run build` completes without errors
- [ ] **Build succeeds on Vercel**: Deploy preview builds correctly
- [ ] **Correct API URLs**: NEXT_PUBLIC_API_URL points to correct environment
- [ ] **No sensitive vars exposed**: No `NEXT_PUBLIC_` prefix on secrets
- [ ] **404 page configured**: Custom not-found.tsx exists
- [ ] **500 page configured**: Custom error.tsx exists
- [ ] **Custom domain set up**: DNS records configured correctly
- [ ] **HTTPS enforced**: Automatic SSL certificate
- [ ] **Redirects configured**: www to root or vice versa
- [ ] **Cache headers set**: Static assets properly cached

## Deployment Documentation Template

```markdown
# Deployment Guide

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

## Environment Variables

### Development
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Production
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## Custom Domain

1. Add `yourdomain.com` in Vercel Dashboard > Settings > Domains
2. Configure DNS:
   - A record: `@` -> `76.76.21.21`
   - CNAME: `www` -> `cname.vercel-dns.com`

## Troubleshooting

### Build Fails
```bash
# Run locally to see error
npm run build
```

### Environment Variables Not Working
- Check variable name starts with `NEXT_PUBLIC_` for client access
- Redeploy after adding new variables

### 404 on Production
- Verify `vercel.json` outputDirectory matches build output
- Check page files are in `app/` directory (App Router)
```

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@frontend-nextjs-app-router` | Next.js App Router configuration |
| `@env-config` | Environment variable management |
| `@tailwind-css` | CSS build optimization |
| `@api-route-design` | API routes and rewrites |
| `@error-handling` | Custom error pages |
