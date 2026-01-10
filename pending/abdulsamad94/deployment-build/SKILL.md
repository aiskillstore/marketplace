---
name: Deployment & Build
description: Knowledge of the Vercel deployment pipeline, hybrid build scripts, and environment configuration.
---

# Deployment & Build Pipeline

## Hybrid Build Process
Our project combines a Next.js root app with a Docusaurus documentation app.
- **Build Command**: `npm run build`
- **Logic**:
  1.  `cd textbook && npm install && npm run build` (Builds Docs)
  2.  `npx shx mkdir -p public/docs` (Creates output dir)
  3.  `npx shx cp -r textbook/build/* public/docs/` (Copies static docs to Next.js public folder)
  4.  `next build` (Builds the main Next.js app)

## Vercel Configuration
- **File**: `backend/vercel.json`
- **Python Runtime**: Used for the FastAPI backend (`backend/main.py`).
- **Routes**: Rewrites all `/api/*` requests to the Python function.

## Environment Variables
Ensure these are set in the Vercel Dashboard:
- `GEMINI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `BETTER_AUTH_SECRET`
- `NEXT_PUBLIC_APP_URL`
