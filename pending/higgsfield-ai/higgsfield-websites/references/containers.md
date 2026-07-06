# Containers — heavy & long-running work

Use a **container** when the work can't run in a Worker: ffmpeg/video, a headless
browser, image processing, a long (minutes-to-hours) job, or any CPU/memory-heavy
task. A container is a **Docker image** that runs alongside your Worker, fronted
by a **Durable Object**. It's **off by default** — opt in only when you need it.

Don't reach for a container for ordinary backend logic — use server functions /
server routes (see `references/runtime-and-infra.md`). Containers cost compute while
running; they sleep when idle.

## The shape (what the platform fixes vs what you write)

The platform **fixes** the names so you can't mis-wire them:
- Durable Object class **`AppContainer`**, binding **`env.CONTAINER`**, one
  instance type, **`max_instances: 1`**.

> **`max_instances: 1` means there is exactly ONE container instance for the
> whole website.** Design for a **single shared container that serves every job**
> (route to it by a STABLE name, track per-job state inside the container) — NOT
> one container per job, and NOT a pool. `getByName(jobId)` is wrong here: each
> distinct name wants its own instance, and only one is allowed.

**You write** these:
0. add the dep (not in the base template): `cd app && bun add @cloudflare/containers`.
1. `app/app.manifest.json` → opt in.
2. `app/container/Dockerfile` (+ its server) → the image, listening on a port.
3. `export class AppContainer extends Container` in `app/src/server.ts`.

## 1. Opt in — `app/app.manifest.json`

```jsonc
{
  "container": { "instanceType": "standard-2", "port": 8080, "sleepAfter": "5m" }
}
// or just  "container": true  for the defaults above
```
`port` must match the port your container server listens on. `sleepAfter` is the
**idle** shutdown — active jobs keep themselves alive (see §4).

## 2. The image — `app/container/Dockerfile`

Keep it in its own folder (`app/container/`) so it's clearly the container's
image, not the website. It must run an HTTP server on the `port` from the manifest:

```dockerfile
# app/container/Dockerfile  (example: ffmpeg + a tiny Node server)
FROM node:20-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY server.mjs .
EXPOSE 8080
CMD ["node", "server.mjs"]
```

`app/container/server.mjs` accepts a job, does the heavy work in the **background**
(returns `202` immediately), and exposes a **per-job** `GET /status?jobId=…`.
Because ONE container serves all jobs, state is keyed per job — never a single
global:

```js
import http from "node:http";

// ONE shared container serves ALL jobs → state MUST be per-job, not global.
const jobs = new Map(); // jobId -> { status, progress, outputKey, error }

http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://c");

  if (req.method === "POST" && url.pathname === "/start") {
    const job = await readJson(req);                 // { jobId, containerToken, appBaseUrl, ... }
    // Idempotent: the DO may re-send /start while the container is booting.
    if (jobs.get(job.jobId)?.status === "running") { res.writeHead(202).end("running"); return; }
    jobs.set(job.jobId, { status: "running", progress: 0, outputKey: null, error: null });
    res.writeHead(202).end("started");               // return FAST — work runs detached
    runJob(job).catch((e) =>
      jobs.set(job.jobId, { ...jobs.get(job.jobId), status: "error", error: String(e) }));
    return;
  }

  if (url.pathname === "/status") {
    const jobId = url.searchParams.get("jobId");
    // Unknown jobId → "unknown" so the DO knows to (re)send /start (it may have
    // booted fresh, or slept and lost this job from the Map).
    const state = jobs.get(jobId) ?? { status: "unknown" };
    res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify(state));
    return;
  }
  res.writeHead(404).end();
}).listen(8080, () => console.log("[CTR] listening on 8080"));

async function runJob(job) {
  // ... run ffmpeg, etc. (can take many minutes) ...
  // If you need Higgsfield data, call YOUR app (NOT fnf directly) with the token:
  //   await fetch(`${job.appBaseUrl}/api/whatever`,
  //     { headers: { Authorization: `Bearer ${job.containerToken}` } });
  jobs.set(job.jobId, { ...jobs.get(job.jobId), status: "done", progress: 100,
                        outputKey: `jobs/${job.jobId}/out.mp4` });
}
```

> The container disk is **ephemeral** (gone on restart). Durable state lives in
> D1/R2 via the Worker — never rely on files in the container.

## 3. The Durable Object — `app/src/server.ts` (the boot is the tricky part)

Export a class named **exactly `AppContainer`**. Before the code, the two lessons
that decide whether a container website works at all:

- **The cold boot takes far longer than a few seconds** (image pull + process
  start — easily 20–60s for a heavy image). **Never abort it.** A short
  `AbortController`/timeout on the first `containerFetch` cancels the cold start
  → the runtime returns `Failed to start container: Container request aborted`
  → the job sticks at **"starting" forever**.
- **Never block a DO alarm on the boot either.** An alarm (`schedule`/`tick`) has
  a tight wall-time budget; a `containerFetch` that blocks on a cold boot gets the
  invocation killed (`exceededWallTime`) before it can re-arm.

So: **boot patiently in the background** (`ctx.waitUntil`, generous timeout) from
the kickoff REQUEST, and make `tick` a pure **monitor** that touches the container
only once it's actually running.

```ts
import { Container } from "@cloudflare/containers";
import { bindings } from "./lib/bindings.server";

const MAX_JOB_MS = 3 * 60 * 60 * 1000; // 3h hard deadline (crash/hang backstop)
const BOOT_TIMEOUT_MS = 120_000;       // PATIENT cold-boot budget (background)
const POLL_TIMEOUT_MS = 6_000;         // fast health-check ONCE the container is up

export class AppContainer extends Container {
  defaultPort = 8080;  // must match the manifest port + the container server
  sleepAfter = "5m";   // idle shutdown; an ACTIVE job renews this (below)

  private booting = false; // one boot in flight at a time (shared across jobs)

  // ctx.waitUntil — the Container base doesn't surface ctx, so cast.
  private bg(p: Promise<unknown>) { (this as any).ctx.waitUntil(p); }

  // Is the container process up? A PURE read of the raw flag — it never triggers
  // a start (unlike containerFetch, which auto-starts and, if aborted mid-boot,
  // yields "Failed to start container: request aborted").
  private running(): boolean { return Boolean((this as any).ctx?.container?.running); }

  // Boot PATIENTLY and deliver POST /start. MUST run via this.bg(...) — never
  // awaited in an alarm — so the long cold boot blocks nothing AND is never
  // aborted. A SHORT timeout here is the #1 way to get stuck at "starting".
  private async bootAndStart(job: any) {
    try {
      await this.containerFetch("http://c/start", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(job),
        signal: AbortSignal.timeout(BOOT_TIMEOUT_MS), // generous, NOT 6s
      });
    } catch (e) { console.log(`[DO] bootAndStart ${job.jobId} THREW ${e}`); }
  }

  // Kickoff hands the full job here. Boot in the background; start the monitor.
  override async fetch(req: Request): Promise<Response> {
    const url = new URL(req.url);
    if (req.method === "POST" && url.pathname === "/__keepalive/start") {
      const job = await req.json();
      this.booting = true;
      this.bg(this.bootAndStart(job).finally(() => (this.booting = false)));
      this.schedule(1, "tick", { job, startedAt: Date.now() }); // monitor loop
      return Response.json({ ok: true });
    }
    return super.fetch(req); // your normal SSR / routes
  }

  // Monitor + recovery — one loop per job. Talks to the container ONLY when it's
  // running, so it never aborts the in-flight boot.
  async tick(p: { job: any; startedAt: number }) {
    const env = bindings();
    const { jobId } = p.job;

    if (Date.now() - p.startedAt > MAX_JOB_MS) {       // crash/hang backstop
      await env.DB?.prepare("UPDATE jobs SET status='timed_out' WHERE id=? AND status!='done'").bind(jobId).run();
      await this.stopIfIdle();                         // do NOT destroy() — siblings share this container
      return;
    }
    // Already finished? stop looping (a stale tick must not pin the container).
    const row = await env.DB?.prepare("SELECT status FROM jobs WHERE id=?").bind(jobId).first<{ status: string }>();
    if (!row || ["done", "error", "timed_out"].includes(row.status)) { await this.stopIfIdle(); return; }

    this.renewActivityTimeout();                       // an active job keeps it alive

    // Not up yet → kick ONE patient background boot + re-arm. NEVER poll a
    // not-running container: containerFetch would auto-start it and this poll's
    // timeout would abort the cold boot.
    if (!this.running()) {
      if (!this.booting) { this.booting = true; this.bg(this.bootAndStart(p.job).finally(() => (this.booting = false))); }
      this.schedule(3, "tick", p);
      return;
    }

    // Up → poll THIS job's status (fast; the port is open).
    let s: any = null;
    try {
      const r = await this.containerFetch(`http://c/status?jobId=${jobId}`, { signal: AbortSignal.timeout(POLL_TIMEOUT_MS) });
      const body = await r.text();
      if (r.ok && body.trimStart().startsWith("{")) s = JSON.parse(body);
      else console.log(`[DO] status non-json http=${r.status} ${body.slice(0, 200)}`); // surfaces runtime errors verbatim
    } catch (e) { console.log(`[DO] status unreachable ${e}`); }

    if (!s) { this.schedule(3, "tick", p); return; }   // booting/race → retry soon

    if (s.status === "unknown") {                      // up but lost this job → re-send /start
      this.bg(this.bootAndStart(p.job));
      this.schedule(3, "tick", p);
      return;
    }

    // Mirror progress to D1; finish on done/error.
    await env.DB?.prepare("UPDATE jobs SET status=?, output=COALESCE(?, output) WHERE id=? AND status!='done'")
      .bind(s.status, s.outputKey ?? null, jobId).run();
    if (s.status === "done" || s.status === "error") { await this.stopIfIdle(); return; }
    this.schedule(5, "tick", p);                       // re-arm (~5s)
  }

  // Stop the SHARED container ONLY when no job is still active (stopping it
  // mid-job would kill siblings). D1 is the source of truth.
  private async stopIfIdle() {
    const env = bindings();
    const row = await env.DB?.prepare("SELECT COUNT(*) AS n FROM jobs WHERE status IN ('queued','running')").first<{ n: number }>();
    if (!row || row.n === 0) await this.stop().catch(() => {});
  }
}

// ... your normal default `export default { fetch }` SSR handler stays below ...
```

Don't override the Durable Object `alarm()` — `Container` uses it internally; use
`schedule()` for periodic work.

## 4. Long jobs — never block a request; keep it alive; have a deadline

- **Kickoff returns fast.** The browser hits your website; you write the job row, hand
  it to the DO, and return a `jobId` in milliseconds — you do NOT hold the request
  for the boot or the job.
- **One shared container.** Route to the DO by a **stable name** so every job
  lands on the single allowed instance; the DO boots it once and monitors per job.
- **Persist + poll.** Write a `jobs` row to D1 (`status=running`); the browser
  polls a cheap `GET /api/jobs/:id` every few seconds (not one long connection).
- **Keep-alive.** While any job runs, `tick` calls `renewActivityTimeout()`.
  `sleepAfter` only kills a TRULY idle container.
- **Deadline.** The 3h cap stops renewing a hung/crashed container so it can't
  bill forever.

Kickoff + status routes (TanStack server routes):

```ts
// POST /api/jobs — start a job (returns immediately)
const jobId = crypto.randomUUID();
await env.DB.prepare("INSERT INTO jobs (id, status) VALUES (?, 'running')").bind(jobId).run();

// ONE shared container for the whole app → route by a STABLE name, not jobId.
const stub = env.CONTAINER.getByName("app");
await stub.fetch(new Request("https://do/__keepalive/start", {   // the DO route, not the container
  method: "POST",
  body: JSON.stringify({
    jobId,
    containerToken,                                  // from x-hf-container-token (see §5)
    appBaseUrl: new URL(request.url).origin,
    /* ...your job spec... */
  }),
}));
return Response.json({ jobId });

// GET /api/jobs/:id — cheap status the browser polls
const row = await env.DB.prepare("SELECT status, output FROM jobs WHERE id=?").bind(id).first();
return Response.json(row);
```

## 5. Calling Higgsfield (fnf) from the container — the container token

A background container has no signed-in viewer, so it can't call fnf directly.
Instead it calls **your website's own API** as the viewer, using a short-lived
**container token**. The flow:

1. **Browser, at kickoff** — mint a token (same-origin; the platform handles it):
   ```js
   const { token } = await fetch("/__auth/container-token", { method: "POST" }).then(r => r.json());
   await fetch("/api/jobs", { method: "POST", body: form, headers: { "x-hf-container-token": token } });
   ```
2. **Your website** reads `x-hf-container-token` and passes it to the container at
   `/start` (as `containerToken` above).
3. **The container**, when it needs fnf, calls **your website** (not fnf):
   ```js
   await fetch(`${appBaseUrl}/api/generate`, {
     method: "POST",
     headers: { Authorization: `Bearer ${containerToken}` },
     body: JSON.stringify({ ... }),
   });
   ```
4. **Your `/api/generate` route** calls fnf the normal way (server-side, via the
   fnf SDK / `https://fnf.internal/*`) — the platform injects the viewer's
   credentials automatically. You write nothing special; it works because the
   platform resolved the viewer from the container token.

> **Do NOT forward the container token to fnf.** Your website calls `fnf.internal`
> with **no** auth header — the platform stamps in the viewer's real creds. The
> container token is ONLY for the container→your-website hop.

The token is scoped to **one user + one website** and expires in **3h**. The
container never holds a real Higgsfield/Cloudflare credential.

## 6. Results & big files

- Small results / status → the DO writes **D1** (it has `env.DB`).
- Big outputs (a video) → write to **R2** (declare `"r2": true`); the container
  reports only the **key**, and your website/DO records it in D1. Don't pass big blobs
  through HTTP bodies.

## Gotchas (read before shipping)

- **Cold-boot abort (#1 cause of "stuck at starting")** — the first
  `containerFetch` triggers the cold boot and waits for the port; a short
  timeout/abort cancels the boot → `Failed to start container: Container request
  aborted`. Boot **patiently in the background** (`ctx.waitUntil`, generous
  timeout); only the *monitor* polls (with a short timeout) once the container is
  `running`.
- **Don't block the alarm on the boot** — a `tick` that awaits a cold boot is
  killed (`exceededWallTime`). Kick the boot via `ctx.waitUntil` and re-arm.
- **Idle-kill** — a busy-but-no-requests container sleeps unless you
  `renewActivityTimeout()` (the `tick` loop). Easy to forget.
- **Ephemeral disk** — container files vanish on restart; persist via D1/R2.
- **ONE shared instance** — `max_instances` is 1. Route by a **stable name** and
  track **per-job state in the container** (a `Map`); never `getByName(jobId)` or
  a pool, and never `destroy()`/`stop()` the container while a sibling job runs.
- **Cold start** — the first request after idle takes tens of seconds to boot;
  show a "starting…" state and let the monitor converge.
- **`port` must match** the manifest, the Dockerfile `EXPOSE`/listen, and
  `defaultPort` in `AppContainer`.
- **Don't call fnf from the container directly** — always go through your website's
  API with the container token (§5), and your website calls `fnf.internal` with no
  token.
