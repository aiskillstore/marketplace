# npx -y @insforge/cli deployments deploy — frontend hosting (Vercel)

Deploy a frontend project (static site / SPA / Next.js / etc.) to InsForge
hosting (via Vercel) from its source directory.

> Looking to deploy a **backend** Docker container (API, worker)? Use
> `npx -y @insforge/cli compute deploy` instead — see
> [compute-deploy.md](../compute-deploy.md).

## Syntax

```bash
npx -y @insforge/cli deployments deploy [source-directory] [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--env <vars>` | Environment variables as JSON: `'{"KEY":"value"}'` |
| `--meta <meta>` | Metadata as JSON |

## Default Directory

Current directory (`.`) if not specified. In most projects, this should be the app root, not `dist/`, `build/`, or `.next/`.

## What It Does

1. Creates a deployment record (gets presigned upload URL)
2. Zips the source directory (max compression)
3. Uploads the zip to the presigned URL
4. Starts the deployment with env vars and metadata
5. Polls status every 5 seconds for up to 2 minutes
6. Returns the live URL and deployment ID

## Excluded Files

The following are automatically excluded from the upload:
- `node_modules/`, `.git/`, `.next/`, `dist/`, `build/`
- `.env*`, `.DS_Store`, `.insforge/`, `*.log`

Because build output is excluded automatically, deploy the project source tree/root directory instead of pointing the command at `dist/`, `build/`, or `.next/`.

### Custom excludes with `.vercelignore`

To exclude additional files, add a `.vercelignore` file to the deploy source directory. It uses `.gitignore` syntax, including `!` negation:

```gitignore
# .vercelignore
*.md
drafts/
!IMPORTANT.md
```

Notes:
- Patterns apply on top of the built-in excludes above; the built-ins always stay excluded and cannot be re-included with `!`.
- The `.vercelignore` file itself is never uploaded.
- If the project was previously deployed directly with the Vercel CLI, an existing `.vercelignore` is honored as-is.

## Environment Variables Are Required

Frontend apps need env vars (API URL, anon key, etc.) to connect to InsForge. Deploying without them produces a broken app. There are two ways to provide them:

**Option A — Persistent env vars (recommended for repeated deploys):**

```bash
# Check what's already configured
npx -y @insforge/cli deployments env list

# Set env vars — these persist across all future deployments
npx -y @insforge/cli deployments env set VITE_INSFORGE_URL https://my-app.us-east.insforge.app
npx -y @insforge/cli deployments env set VITE_INSFORGE_ANON_KEY ik_xxx

# Deploy the project source — persistent vars are applied automatically
npx -y @insforge/cli deployments deploy .
```

**Option B — Inline `--env` flag (one-off or override):**

```bash
npx -y @insforge/cli deployments deploy . --env '{"VITE_INSFORGE_URL": "https://my-app.us-east.insforge.app", "VITE_INSFORGE_ANON_KEY": "ik_xxx"}'
```

Before deploying, always confirm env vars are in place: either check `deployments env list` shows the required vars, or pass `--env` on the command.

## Examples

```bash
# Deploy with persistent env vars already set
npx -y @insforge/cli deployments deploy .

# Deploy with inline env vars
npx -y @insforge/cli deployments deploy . --env '{"VITE_API_URL": "https://my-app.us-east.insforge.app", "VITE_ANON_KEY": "ik_xxx"}'

# JSON output
npx -y @insforge/cli deployments deploy . --json
```

## Typical Workflow

### Pre-Deployment: Local Build Verification

**CRITICAL: Always verify local build succeeds before deploying to InsForge.**

Local builds are faster to debug and don't waste server resources on avoidable errors.

After the build passes locally, deploy the project source directory (usually `.`). Do not deploy the generated output folder; the CLI excludes it automatically.

Local Build Checklist:

```bash
# 1. Install dependencies
npm install

# 2. Create production environment file
# Use the correct prefix for your framework:
# - Vite: VITE_INSFORGE_URL
# - Next.js: NEXT_PUBLIC_INSFORGE_URL
# - CRA: REACT_APP_INSFORGE_URL
# - Astro: PUBLIC_INSFORGE_URL
cat > .env.production << 'EOF'
INSFORGE_URL=https://your-project.insforge.app
INSFORGE_ANON_KEY=your-anon-key
EOF

# 3. Run production build
npm run build
```

### Common Build Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Missing env var errors | Build-time env vars not set | Create `.env.production` with framework-specific prefix |
| Module resolution errors | Edge functions scanned by compiler | Exclude edge function directories from build config |
| Static export conflicts | Dynamic routes with static export | Use SSR or configure static params per framework docs |
| `module_not_found` | Missing dependency | Run `npm install` and verify package.json |

### Framework-Specific Notes

**Environment Variables by Framework:**

| Framework | Prefix | Example |
|-----------|--------|---------|
| Vite | `VITE_` | `VITE_INSFORGE_URL` |
| Next.js | `NEXT_PUBLIC_` | `NEXT_PUBLIC_INSFORGE_URL` |
| Create React App | `REACT_APP_` | `REACT_APP_INSFORGE_URL` |
| Astro | `PUBLIC_` | `PUBLIC_INSFORGE_URL` |
| SvelteKit | `PUBLIC_` | `PUBLIC_INSFORGE_URL` |

**Edge Functions:**
If your project has edge functions in a separate directory (commonly `functions/` for Deno-based functions), exclude them from your frontend build to prevent module resolution errors. Add the directory to your TypeScript or bundler exclude configuration.

### Start to Deploy

```bash
# 4. Ensure env vars are set (check existing, add any missing)
npx -y @insforge/cli deployments env list
npx -y @insforge/cli deployments env set VITE_INSFORGE_URL https://my-app.us-east.insforge.app
npx -y @insforge/cli deployments env set VITE_INSFORGE_ANON_KEY ik_xxx

# 5. Deploy the project source (persistent env vars are applied automatically)
npx -y @insforge/cli deployments deploy .
```

Alternatively, pass env vars inline: `npx -y @insforge/cli deployments deploy . --env '{"VITE_INSFORGE_URL": "...", "VITE_INSFORGE_ANON_KEY": "..."}'`

### Check Deployment Status

Wait 30 seconds to 1 minute, then check status with `npx -y @insforge/cli deployments status <id>`.

#### Status Values

| Status | Description |
|--------|-------------|
| `WAITING` | Waiting for source upload |
| `UPLOADING` | Uploading to build server |
| `QUEUED` | Queued for build |
| `BUILDING` | Building (typically ~1 min) |
| `READY` | Complete - URL available |
| `ERROR` | Build or deployment failed |
| `CANCELED` | Deployment cancelled |

## SPA Routing

For React single-page apps, ensure a `vercel.json` exists in the project root:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## Best Practices

1. **Deploy the project source directory**
   - Run the command from your app root, or pass that directory explicitly
   - Do not deploy `dist/`, `build/`, or `.next/` directly; the CLI excludes them automatically
   - Never include `node_modules`, `.git`, `.env`, or `.insforge` in the upload
   - Large assets should go to InsForge Storage, not the deployment

2. **Always set env vars before deploying**
   - Use `deployments env set` for persistent vars, or `--env` for one-off deploys
   - Run `deployments env list` to verify vars are in place before deploying
   - Never commit `.env` files to source or include in zip
   - Use the correct env var prefix for your framework: `VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`, etc.

3. **Always build locally first** to catch errors before deploying.

4. **Include vercel.json for SPAs**
   - Required for client-side routing to work properly


## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Including node_modules in zip | Exclude it - will be installed during build |
| Including .env files | Use `deployments env set` or `--env` flag instead |
| Deploying `dist/`, `build/`, or `.next/` directly | Deploy the project source/root directory instead; the CLI excludes build output automatically |
| Deploying without env vars | Run `deployments env list` first — if empty, set vars with `deployments env set` or `--env` |
| Missing VITE_* env vars | Add all required build-time variables with correct framework prefix |
| Checking status too early | Wait 30sec-1min before checking status |
| Missing vercel.json for SPA | Add rewrites config for client-side routing |
