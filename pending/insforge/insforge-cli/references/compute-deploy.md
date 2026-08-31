# npx -y @insforge/cli compute deploy — deploy a backend container

> 🔧 **DO NOT call `flyctl` directly to manage InsForge compute services.**
> InsForge runs containers on Fly.io under the hood, but the Fly account, org,
> IPs, and machine ownership all live on the InsForge cloud. Using `flyctl`
> with your own credentials will land in the wrong Fly org and fail with
> `unauthorized`. Use `npx -y @insforge/cli compute …` instead.

Deploy a backend service. Two modes:
1. **Source mode** (`compute deploy [dir]`): you have a Dockerfile. CLI shells out to `flyctl deploy --remote-only --build-only` using a short-lived per-app deploy token minted by InsForge cloud. Build runs on Fly's remote builder; image is pushed to `registry.fly.io`. Cloud then launches the machine. **No local Docker daemon needed** — only `flyctl` on PATH.
2. **Image mode** (`compute deploy --image <url>`): deploy a pre-built image from any registry. **Nothing needed locally** beyond the InsForge CLI.

> Looking to deploy a **frontend** (static site / SPA / Next.js to Vercel)? Use
> `npx -y @insforge/cli deployments deploy` instead — see
> [deployments/deploy.md](deployments/deploy.md).

## Two modes

| Mode | Command | When to use | Local tooling |
|---|---|---|---|
| **Source** | `compute deploy ./my-app --name my-api` | You have a Dockerfile and want one command. Build runs on Fly's remote builder via flyctl. | **`flyctl` on PATH** (no Docker needed) |
| **Image** | `compute deploy --image <url> --name my-api` | You already have a built image (CI pipeline, public image, custom registry). | None |

Both deploy to the same Fly.io infrastructure with the same options (`--port`, `--cpu`, `--memory`, `--region`, `--env`).

**Anti-pattern: `flyctl deploy` directly from your laptop with your own credentials.** Returns 401 — the Fly account is InsForge's, not yours. The CLI invokes flyctl for you with the *cloud-minted* per-app token, which is the only token that works.

## Syntax

```bash
# Source mode — flyctl remote build + push, then cloud launches the machine.
# Requires `flyctl` on PATH (curl -L https://fly.io/install.sh | sh). NO Docker daemon needed.
# Cloud mints a 20-min per-app token attenuated to one app + builder/wg with `else: deny`.
npx -y @insforge/cli compute deploy <dir> --name <name> [options]

# Image mode — deploy pre-built image (nothing needed locally).
npx -y @insforge/cli compute deploy --image <url> --name <name> [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name <name>` | Service name (DNS-safe: lowercase, numbers, dashes) | **required** |
| `[dir]` (positional) | Source directory containing a Dockerfile (source mode) | — |
| `--image <url>` | Docker image URL (image mode) | — |
| `--port <port>` | Container internal port | `8080` |
| `--cpu <tier>` | CPU tier in Fly.io standard format `<kind>-<N>x` (see [CPU tier section](#cpu-tier-flyio-standard-format)) | `shared-1x` |
| `--memory <mb>` | Memory in MB (any positive integer; Fly enforces per-tier bounds) | `512` |
| `--region <region>` | Fly.io region | `iad` |
| `--env <json>` | Env vars as JSON object. Mutually exclusive with `--env-file`. | none |
| `--env-file <path>` | Standard `.env` file (KEY=VALUE per line; `#` comments, blank lines, quoted values supported). Mutually exclusive with `--env`. | none |

Exactly one of `[dir]` or `--image` must be provided.

## Quick examples

```bash
# Source mode — your project, your Dockerfile, flyctl on PATH (no Docker needed)
npx -y @insforge/cli compute deploy . --name my-api --port 8000

# Off-the-shelf image
npx -y @insforge/cli compute deploy --image nginx:alpine --name proxy --port 80

# Pre-built image from GHCR
npx -y @insforge/cli compute deploy \
  --image ghcr.io/your-org/your-app:v1 \
  --name my-api \
  --port 8000 \
  --cpu performance-1x \
  --memory 2048 \
  --env '{"OPENAI_API_KEY": "sk-..."}'

# Bigger machine (8 cores + 4 GB RAM)
npx -y @insforge/cli compute deploy ./worker \
  --name batch \
  --port 8080 \
  --cpu performance-8x --memory 4096

# Env vars from a .env file (preferred for >1 secret)
npx -y @insforge/cli compute deploy \
  --image ghcr.io/your-org/your-app:v1 \
  --name my-api \
  --port 8000 \
  --env-file ./.env.production
```

### Rotating env vars after deploy

The `GET` path never returns env values (encrypted at rest, no decrypt endpoint). To rotate **one** secret without wiping the others, use partial-merge flags on `compute update` instead of `--env`:

```bash
# Partial merge — keeps untouched keys intact (repeatable flags)
npx -y @insforge/cli compute update <id> \
  --env-set DATABASE_URL=postgres://new-host \
  --env-set API_KEY=sk-... \
  --env-unset OLD_DEBUG_TOKEN

# Wholesale replace — clears anything not in the JSON. Mutually exclusive
# with --env-set / --env-unset.
npx -y @insforge/cli compute update <id> --env '{"NODE_ENV":"production","DATABASE_URL":"..."}'
```

## Source mode — worked example

```bash
# Project layout:
$ ls
Dockerfile  app.py  requirements.txt

# Deploy:
$ npx -y @insforge/cli compute deploy . --name my-bot --port 8080
✓ Detected Dockerfile at /path/to/Dockerfile
✓ Creating service "my-bot"...
✓ Created Fly app my-bot-projAbc
✓ Requesting deploy token...
✓ Building & pushing on Fly remote builder...
   [flyctl streams build logs here]
✓ Launching machine...
✓ Service "my-bot" deployed [running]
   Endpoint: https://my-bot-projAbc.fly.dev
   Image: registry.fly.io/my-bot-projAbc:cli-1714003200000 (built remotely; no local image to clean up)
```

What happens behind the scenes:
1. CLI looks up the service by `--name`. If missing, calls the cloud to provision a Fly app shell (no machine yet) and gets back the `flyAppId`.
2. CLI requests a per-app deploy token from the cloud — a Fly macaroon attenuated with `IfPresent { ifs: [Apps[<thisAppOnly>: rwcdC], FeatureSet[builder, wg]], else: deny }` and a 20-min ValidityWindow. The org-wide Fly token never leaves InsForge's servers.
3. CLI shells out to `flyctl deploy --remote-only --build-only --app <flyAppId> --image-label cli-<ts>` with the token exported as `FLY_API_TOKEN`. flyctl ships the build context to Fly's remote builder, the build runs there, and the resulting image is pushed straight to `registry.fly.io/<app>:cli-<ts>`. **Nothing built or pushed from your laptop** — and no Docker daemon needed.
4. CLI sends `PATCH /api/compute/services/<id>` with `imageUrl=registry.fly.io/<app>:cli-<ts>`. Cloud calls Fly Machines API to launch (or restart with the new image) and returns the public URL.

### When to use source mode vs image mode

- **Source mode**: rapid iteration on a single project, Dockerfile in repo, `flyctl` on PATH. No need for Docker Desktop or a local daemon.
- **Image mode**: no `flyctl` on the machine running the CLI (e.g. constrained CI runners), pipelines that push their own images, off-the-shelf images like `nginx:alpine`, or multiple deploy targets sharing one image.

### If you don't have a Dockerfile yet

Ask your AI agent to generate one for your stack:
- Node app → typically `FROM node:20-alpine`, `npm ci`, `CMD node index.js`
- Python app → `FROM python:3.12-alpine`, `pip install -r requirements.txt`, `CMD python app.py`
- Go binary → multi-stage build with `FROM golang:1.22 AS build` then `FROM alpine:3.20`

The InsForge skill knows these patterns; ask the agent and it'll write one.

## Producing an image yourself (for image mode)

If you want to build images in CI and deploy via `--image` instead:

```bash
docker build -t ghcr.io/<your-gh-username>/<app-name>:v1 .
echo $GITHUB_TOKEN | docker login ghcr.io -u <your-gh-username> --password-stdin
docker push ghcr.io/<your-gh-username>/<app-name>:v1

npx -y @insforge/cli compute deploy \
  --image ghcr.io/<your-gh-username>/<app-name>:v1 \
  --name <app-name> \
  --port <port>
```

Any OCI registry works (GHCR, Docker Hub, etc.) as long as the image is publicly pullable. Private registries require per-project credential setup — contact support.

## CPU Tier (Fly.io standard format)

`--cpu` accepts any well-formed Fly.io machine size in the format **`<kind>-<N>x`** where:
- `<kind>` is `shared` or `performance`
- `<N>` is the vCPU count

InsForge does **not** maintain a hardcoded allow-list — Fly.io is the source of truth for which sizes actually exist. If you pass an unsupported combination (e.g. `performance-32x`), Fly returns a clean validation error at machine-create time.

Common standard tiers (current as of writing):

| Tier | Kind | vCPU | Typical RAM range |
|------|------|------|-------------------|
| `shared-1x` (default) | shared | 1 | 256 MB – 2 GB |
| `shared-2x` | shared | 2 | 512 MB – 4 GB |
| `shared-4x` | shared | 4 | 1 GB – 8 GB |
| `shared-8x` | shared | 8 | 2 GB – 16 GB |
| `performance-1x` | dedicated | 1 | 2 GB – 8 GB |
| `performance-2x` | dedicated | 2 | 4 GB – 16 GB |
| `performance-4x` | dedicated | 4 | 8 GB – 32 GB |
| `performance-8x` | dedicated | 8 | 16 GB – 64 GB |
| `performance-16x` | dedicated | 16 | 32 GB – 128 GB |

Authoritative current list and pricing: <https://fly.io/docs/about/pricing/#started-machines>.

### Common picks

| Use case | Recommended `--cpu --memory` |
|----------|------------------------------|
| Static site / proxy | `shared-1x 256` |
| Small Node/Python API | `shared-1x 512` |
| Mid API with caching | `shared-2x 1024` |
| API needing 4 GB RAM | `shared-2x 4096` or `shared-4x 4096` |
| 8 cores + 4 GB (CPU-heavy short jobs) | `performance-8x 4096` |
| ML inference (CPU) | `performance-4x 8192` |
| Heavy data processing | `performance-8x 16384` |

## What happens internally

CLI → OSS instance → InsForge cloud backend → Fly.io. The cloud:
1. Records the service in its `compute_services` table
2. Creates a Fly.io app named `<name>-<projectId>`
3. Allocates IPv4 + IPv6 addresses
4. Launches a Fly machine pulling the image you specified
5. Returns the public endpoint URL

Total time: typically ~5 seconds (Fly pulls the image and boots the machine).

## Output

Text mode:
```
✓ Service "my-api" deployed [running]
  Endpoint: https://my-api-projID.fly.dev
```

JSON mode (`--json`):
```json
{
  "id": "uuid",
  "name": "my-api",
  "imageUrl": "ghcr.io/you/app:v1",
  "port": 80,
  "cpu": "shared-1x",
  "memory": 256,
  "region": "iad",
  "status": "running",
  "endpointUrl": "https://my-api-projID.fly.dev",
  "flyAppId": "my-api-projID",
  "flyMachineId": "abc123"
}
```

## Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| `COMPUTE_SERVICE_ALREADY_EXISTS` | Duplicate name in project | Choose a different name or delete the existing service |
| `COMPUTE_QUOTA_EXCEEDED` | At per-project quota (5 active services) | Delete unused services with `compute delete <id>`. If the dashboard shows fewer services than the error implies, contact support to clear orphans. |
| `COMPUTE_INVALID_CPU_TIER` | `--cpu` doesn't match `<kind>-<N>x` | Use the format above, e.g. `performance-2x` |
| `COMPUTE_IMAGE_NOT_AVAILABLE` | Fly registry alias propagation race exhausted retries (rare) | Re-run the deploy. The cloud silently retries this race 4 times with backoff `[2s, 4s, 8s]`; this error only surfaces if all retries failed. |
| `COMPUTE_FLY_API_ERROR` | Generic Fly 4xx (bad config, region mismatch, etc.) | Read the structured `error` message — it's the upstream Fly response and usually points at the specific field. |
| `flyctl is required for source-mode deploy` | flyctl isn't installed or not on PATH | Install: `curl -L https://fly.io/install.sh \| sh`, then reopen your shell. Or switch to `--image <pre-built-image>` |
| `flyctl deploy ... unauthorized` | Per-app deploy token expired (20-min TTL) | Re-run `compute deploy` — the CLI mints a fresh token per invocation |
| `flyctl deploy --build-only failed` | Build error in your Dockerfile | Check the build output above (streamed from Fly's remote builder); fix the Dockerfile and retry |
| `Image pull error` (image mode) | Registry private without InsForge having creds | Push to a public image, or contact support to configure private registry creds |
| `Unauthorized` from registry (image mode) | Image is private and InsForge cloud doesn't have credentials | Make the image public, or use a public registry |

## FAQ

**Q: Why does source mode need `flyctl` if it doesn't need Docker?**
A: The CLI shells out to `flyctl deploy --remote-only --build-only` for the build step — flyctl knows how to ship a build context to Fly's remote builder, stream logs back, and push the result. Image mode skips that entirely (it's just an HTTP call telling the cloud which image URL to pull), so it needs nothing locally.

**Q: Where does the deploy token come from? Can a stolen token attack other tenants?**
A: The cloud holds the org-wide Fly token; it never leaves InsForge servers. Per `compute deploy` invocation it mints a fresh app-scoped macaroon with `IfPresent { ifs: [Apps[<oneApp>: rwcdC], FeatureSet[builder, wg]], else: deny }` + 20-min ValidityWindow. If exfiltrated within those 20 minutes, the token can deploy to that one app and use the org's remote builder to do so — but cannot read or mutate any other app, list org-level inventory, mint new tokens, or persist beyond TTL. Verified by the live e2e suite which probes `/v1/orgs/<slug>/machines`, `/v1/apps?org_slug=`, and `/v1/orgs/<slug>/volumes` and asserts each returns 4xx.

**Q: Can I use a private image from my own registry?**
A: Public images (e.g. Docker Hub public, GHCR public) work out of the box. Private registry support requires per-project credential configuration; contact support to set this up.

**Q: How do I update a running service to a new image?**
A: Use `compute update <service-id> --image <new-image-url>`. The machine is restarted with the new image; ~5s downtime.

**Q: What happens to my service if Fly.io has an outage?**
A: It's down. InsForge runs your containers on Fly's infrastructure — Fly's uptime is your uptime. For HA, you'd typically deploy multiple services in different regions (future feature).

**Q: Do services scale to zero when idle, or stay always-on?**
A: Your choice, made at deploy time — the default is **always-on**. Image-mode machines are launched without autostop, and the CLI-generated source-mode config sets `auto_stop_machines = false`, so by default a service runs continuously until you run `compute stop` or the container process exits. To opt into **scale-to-zero**, deploy in source mode with your own `fly.toml` (the CLI leaves an existing `fly.toml` untouched) and set `auto_stop_machines = "stop"` with `min_machines_running = 0`; a stopped machine wakes on the next request. A slow first request on an always-on service is app-level cold work (cache warming, re-opening DB connections), not a platform cold start.

**Q: I see `MANIFEST_UNKNOWN` in a stack trace. What is it?**
A: After `flyctl` pushes your image, Fly asynchronously aliases the digest from the builder's namespace to your app's namespace. Until that propagates (usually < 8 s) the Machines API returns `400 MANIFEST_UNKNOWN` even though the digest is correct. The InsForge cloud silently retries 4 times with backoff `[2s, 4s, 8s]`, so you almost never see it. If retries exhaust, you get a structured `COMPUTE_IMAGE_NOT_AVAILABLE` 400 with `nextActions` telling you to re-run — re-runs are idempotent and typically succeed instantly because the alias has had time to propagate.

## Notes

- The user never needs to handle a Fly token. The InsForge cloud holds the org token; per deploy it mints an app-scoped, attenuated token (~20 min, `else: deny`) and the CLI exports it as `FLY_API_TOKEN` only for the duration of the flyctl subprocess.
- Source mode requires `flyctl` on PATH but **no local Docker daemon** (build runs on Fly's remote builder). Image mode requires neither.
- The machine starts immediately on first deploy. Subsequent deploys to the same `--name` update the existing machine in place. Use `compute stop` to pause without destroying.
- Env vars are encrypted at rest. See [Rotating env vars after deploy](#rotating-env-vars-after-deploy) for partial-merge usage on running services.
- `compute delete` is **permanent**: Fly app + image are destroyed and the registry GCs the image shortly after. The audit log captures the full config (encrypted env blob included) on delete for after-the-fact reconstruction. Dashboard adds a type-to-confirm gate; the CLI does not.
