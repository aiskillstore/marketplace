---
name: lovable
description: |
  Integration skill for Lovable.dev projects. Activates when working with:
  - Lovable.dev projects with GitHub sync
  - Supabase Edge Functions that need deployment
  - Database migrations for Lovable Cloud
  - Projects with supabase/ directory structure
  - Any mention of "Lovable", "deploy edge function", "apply migration"
  
  Provides exact Lovable prompts for backend operations that can't be done via GitHub alone.
---

# Lovable Integration Skill

This skill enables Claude Code to work effectively with Lovable.dev projects while respecting Lovable's deployment requirements.

## When to Use This Skill

Activate when:
- User mentions "Lovable" or "lovable.dev"
- Project has `supabase/` directory with Edge Functions
- User asks to deploy edge functions
- User creates database migrations
- User asks about Lovable Cloud or backend deployment
- Project appears to be a Lovable project (React + Supabase structure)

## Project Architecture Types

Lovable supports two architectures. **Always detect which one you're working with** before giving advice.

### Detecting Architecture

Check the root directory of the user's project:
- `app.config.ts` present → **TanStack Start** (new, SSR — post-April 2026)
- `vite.config.ts` present → **Vite SPA** (legacy, CSR — pre-April 2026)

Both are fully supported. Old projects remain on Vite and receive no forced migration.

---

## Vite SPA Architecture (Legacy)

Projects created before April 2026. Client-side rendering only.

### What Syncs Automatically (Vite SPA)

✅ Edit freely and push to `main`:
- `src/` - All React components, pages, hooks, utils
- `public/` - Static assets
- Config files - `vite.config.ts`, `tailwind.config.js`, `tsconfig.json`
- `package.json` - Dependencies
- `supabase/functions/*/index.ts` - Edge Function **code** (not deployment)
- `supabase/migrations/*.sql` - Migration **files** (not application)

### What Requires Lovable Deployment (Vite SPA)

⚠️ After editing, provide Lovable prompt:

| Change Type | Lovable Prompt |
|-------------|----------------|
| Edge Function code | `"Deploy the [name] edge function"` |
| All Edge Functions | `"Deploy all edge functions"` |
| New migration file | `"Apply pending Supabase migrations"` |
| New table needed | `"Create a [name] table with columns: [list]"` |
| RLS policy | `"Enable RLS on [table] allowing [who] to [what]"` |
| Storage bucket | `"Create a [public/private] bucket called [name]"` |
| Secret/env var | Manual: Cloud → Secrets → Add |

---

## TanStack Start Architecture (New Projects)

Projects created after April 2026. Full server-side rendering (SSR) via TanStack Start.

### Key Differences from Vite SPA

- Routes are **file-based** in `app/routes/` (not React Router in `src/App.tsx`)
- Config file is `app.config.ts` (not `vite.config.ts`)
- **Server functions** (`createServerFn`) let server-side logic live directly in component files — no edge function needed for simple server logic
- Files named `*.server.ts` are server-only and never sent to the browser
- Pages are rendered as complete HTML on the server before reaching the browser

### What Syncs Automatically (TanStack Start)

✅ Edit freely and push to `main`:
- `app/` - All routes, components, server functions, layouts
- `app/routes/` - File-based route pages
- `public/` - Static assets
- `app.config.ts`, `tailwind.config.js`, `tsconfig.json` - Config files
- `package.json` - Dependencies
- `app/**/*.server.ts` - TanStack server functions (**auto-deploys, no Lovable prompt needed**)
- `supabase/functions/*/index.ts` - Supabase Edge Function **code** (not deployment)
- `supabase/migrations/*.sql` - Migration **files** (not application)

### What Requires Lovable Deployment (TanStack Start)

⚠️ After editing, provide Lovable prompt:

| Change Type | Lovable Prompt |
|-------------|----------------|
| Supabase Edge Function code | `"Deploy the [name] edge function"` |
| All Supabase Edge Functions | `"Deploy all edge functions"` |
| New migration file | `"Apply pending Supabase migrations"` |
| New table needed | `"Create a [name] table with columns: [list]"` |
| RLS policy | `"Enable RLS on [table] allowing [who] to [what]"` |
| Storage bucket | `"Create a [public/private] bucket called [name]"` |
| Secret/env var | Manual: Cloud → Secrets → Add |

> **Note:** TanStack server functions (`createServerFn`) are **not** Supabase Edge Functions. They live in `app/` and deploy automatically via GitHub sync — no Lovable prompt needed. Only `supabase/functions/` requires manual deployment.

### TanStack Start File Structure

```
project/
├── app/                          # ✅ Safe - auto-syncs
│   ├── routes/                   # File-based routing
│   │   ├── __root.tsx            # Root layout
│   │   ├── index.tsx             # Home page (/)
│   │   └── [route].tsx           # Other pages
│   ├── components/               # Shared UI components
│   ├── lib/                      # Utilities and helpers
│   └── *.server.ts               # ✅ Server functions (auto-deploy)
├── app.config.ts                 # TanStack Start config
├── public/                       # Static assets
├── supabase/
│   ├── functions/                # ✅ Edit code, ⚠️ needs deploy
│   └── migrations/               # ✅ Create files, ⚠️ needs apply
└── CLAUDE.md                     # Project context
```

---

## Core Concept (Both Architectures)

Lovable uses **two-way GitHub sync** on the `main` branch only:
- Frontend and server-side code (including TanStack server functions) sync automatically
- Supabase Edge Functions and database migrations require Lovable prompts after code changes

## Response Format

When backend deployment is needed, always output:

```
📋 **LOVABLE PROMPT:**
> "[exact prompt to copy-paste]"
```

For destructive operations, add:
```
⚠️ **Warning**: [explanation of risk]
```

## File Structure Reference

### Vite SPA (Legacy — `vite.config.ts` present)

```
project/
├── src/                          # ✅ Safe - auto-syncs
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── lib/
│   └── integrations/supabase/
│       ├── client.ts             # ⚠️ Has Supabase URLs
│       └── types.ts
├── supabase/
│   ├── functions/                # ✅ Edit code, ⚠️ needs deploy
│   │   └── [function-name]/
│   │       └── index.ts
│   ├── migrations/               # ✅ Create files, ⚠️ needs apply
│   │   └── YYYYMMDDHHMMSS_*.sql
│   └── config.toml               # ⚠️ Lovable Cloud manages
├── .env                          # Local only - Lovable ignores
└── CLAUDE.md                     # Project context
```

### TanStack Start (New — `app.config.ts` present)

```
project/
├── app/                          # ✅ Safe - auto-syncs
│   ├── routes/                   # File-based routing
│   │   ├── __root.tsx            # Root layout
│   │   ├── index.tsx             # Home route (/)
│   │   └── [name].tsx            # Named routes
│   ├── components/               # Shared components
│   ├── lib/                      # Utilities
│   ├── integrations/supabase/    # Supabase client + types
│   └── *.server.ts               # ✅ Server functions (auto-deploy, no prompt needed)
├── app.config.ts                 # TanStack Start config
├── public/                       # Static assets
├── supabase/
│   ├── functions/                # ✅ Edit code, ⚠️ needs deploy via Lovable
│   │   └── [function-name]/
│   │       └── index.ts
│   ├── migrations/               # ✅ Create files, ⚠️ needs apply via Lovable
│   │   └── YYYYMMDDHHMMSS_*.sql
│   └── config.toml               # ⚠️ Lovable Cloud manages
├── .env                          # Local only - Lovable ignores
└── CLAUDE.md                     # Project context
```

## Backend Types

### Lovable Cloud
- Backend managed entirely by Lovable
- No Supabase dashboard access
- All operations via Lovable prompts
- Secrets in Cloud → Secrets UI

### Own Supabase
- Direct Supabase dashboard access
- Can use Supabase CLI: `supabase functions deploy`
- More flexibility but manual setup

## Quick Prompts Reference

### Edge Functions
```
"Deploy all edge functions"
"Deploy the send-email edge function"
"Create an edge function called [name] that [description]"
"Show logs for [name] edge function"
"The [name] edge function returns [error]. Fix it"
```

### Database
```
"Create a [name] table with columns: id (uuid), name (text), created_at (timestamp)"
"Add a [column] column of type [type] to [table]"
"Add foreign key from [table1].[col] to [table2].id"
"Apply pending Supabase migrations"
```

### RLS Policies
```
"Enable RLS on [table]"
"Add RLS policy on [table] allowing authenticated users to read all rows"
"Add RLS policy on [table] allowing users to only access their own rows"
```

### Storage
```
"Create a public storage bucket called [name]"
"Create a private storage bucket called [name]"
"Allow authenticated users to upload to [bucket]"
```

### Auth
```
"Enable Google authentication"
"Enable GitHub authentication"
"When user signs up, create row in profiles table"
```

## Branch Rules

- **Only `main` syncs** with Lovable
- Feature branches don't deploy until merged
- Lovable syncs within 1-2 minutes of push

## Yolo Mode - Automated Deployments (Beta)

When `yolo_mode: on` in CLAUDE.md, deployments are automated via browser automation:

### How It Works

Instead of showing manual prompts, the **yolo skill** (`/skills/yolo/SKILL.md`) takes over:
1. Automatically navigates to Lovable.dev
2. Submits deployment prompts
3. Monitors for success/failure
4. Runs verification tests (if enabled)
5. Reports deployment summary

### When Yolo Mode Activates

- During `/lovable:deploy-edge` command
- During `/lovable:apply-migration` command
- When `yolo_mode: on` in CLAUDE.md

### Configure Yolo Mode

```
/lovable:yolo on               # Enable with testing
/lovable:yolo on --no-testing  # Enable without testing
/lovable:yolo on --debug       # Enable with verbose logs
/lovable:yolo off              # Disable
```

### Beta Status

⚠️ Yolo mode is in beta:
- Requires Claude in Chrome extension
- May have bugs or UI compatibility issues
- Always has manual fallback
- See `/skills/yolo/SKILL.md` for details

## Debugging Checklist

1. **Frontend not updating?**
   - On `main` branch?
   - Changes pushed?
   - Wait 1-2 min

2. **Edge Function not working?**
   - Deployed via Lovable (or yolo mode)?
   - Secrets set in Cloud UI?
   - Check logs in Lovable

3. **Database query failing?**
   - Migration applied (via Lovable or yolo mode)?
   - RLS policies correct?
   - Table exists?

4. **Yolo mode not working?**
   - Check `yolo_mode: on` in CLAUDE.md
   - Chrome extension installed?
   - Logged into Lovable?
   - See yolo skill for troubleshooting
