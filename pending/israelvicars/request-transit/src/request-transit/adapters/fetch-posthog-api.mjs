// adapters/fetch-posthog-api.mjs: pull every span of one trace from PostHog Distributed Tracing and
// save it as a file normalize.mjs auto-detects (format "posthog").
// Endpoint and fields from posthog.com/docs/api/tracing-2 (scope tracing:read). Read confirmed live on US Cloud
// (2026-10-18, OpenTelemetry Demo traces of 66 spans in one page); the pagination body ({offset}) follows the
// documented hasMore/nextOffset response and has not been exercised by a multi-page trace yet.
//
// Env only (never commit keys):
//   POSTHOG_API_KEY     personal API key (phx_...) with the tracing:read scope (POSTHOG_PERSONAL_API_KEY also read).
//                       NOT the phc_ project token, NOT a phs_ project secret key.
//   POSTHOG_HOST        https://us.posthog.com (default) or https://eu.posthog.com or your self-hosted URL
//   POSTHOG_PROJECT_ID  numeric project id; if unset, looked up via /api/projects/@current/ (needs project:read)
// usage: node adapters/fetch-posthog-api.mjs <trace_id_hex> [--out traces/<id>.posthog.json]
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const argv = process.argv.slice(2); const opt = {}; const pos = [];
for (let i = 0; i < argv.length; i++) argv[i].startsWith('--') ? (opt[argv[i].slice(2)] = argv[++i]) : pos.push(argv[i]);
const traceId = pos[0];
const key = process.env.POSTHOG_API_KEY || process.env.POSTHOG_PERSONAL_API_KEY;
let project = process.env.POSTHOG_PROJECT_ID;
const host = (process.env.POSTHOG_HOST || 'https://us.posthog.com').replace(/\/$/, '');
if (!traceId || !/^[0-9a-f]{32}$/i.test(traceId)) { console.error('usage: node adapters/fetch-posthog-api.mjs <32-hex trace id> [--out file]'); process.exit(1); }
if (!key) { console.error('set POSTHOG_API_KEY (personal key, phx_..., scope tracing:read); POSTHOG_HOST defaults to https://us.posthog.com'); process.exit(1); }
if (key.startsWith('phs_')) { console.error('POSTHOG_API_KEY is a project secret key (phs_); those only take feature_flag/endpoint/support_ticket scopes and PostHog rejects them on the tracing API (401). Create a personal API key (phx_) with the tracing:read scope.'); process.exit(1); }
if (key.startsWith('phc_')) { console.error('POSTHOG_API_KEY looks like a project token (phc_); the query API needs a personal API key (phx_)'); process.exit(1); }

if (!project) {
  const r = await fetch(`${host}/api/projects/@current/`, { headers: { Authorization: `Bearer ${key}` } });
  if (!r.ok) { console.error(`PostHog ${r.status} looking up the current project: set POSTHOG_PROJECT_ID, or give the key the project:read scope`); process.exit(1); }
  project = String((await r.json()).id);
}
const url = `${host}/api/projects/${encodeURIComponent(project)}/tracing/spans/trace/${traceId.toLowerCase()}/`;
const results = [];
let offset = 0;
for (let page = 0; page < 100; page++) {
  const r = await fetch(url, { method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: JSON.stringify(offset ? { offset } : {}) });
  if (!r.ok) {
    const hint = r.status === 403 ? ' (the key needs the tracing:read scope)' : r.status === 401 ? ' (not a valid personal API key for this host; US and EU are separate)' : '';
    console.error(`PostHog ${r.status}${hint}: ${(await r.text()).slice(0, 400)}`); process.exit(1);
  }
  const body = await r.json();
  const spans = Array.isArray(body) ? body : body.results || body.spans || [];
  results.push(...spans);
  if (!body.hasMore || body.nextOffset == null || !spans.length) break;
  offset = body.nextOffset;
}
if (!results.length) { console.error(`no spans for trace ${traceId} (check the id, project and time retention)`); process.exit(1); }
const out = opt.out || `traces/${traceId}.posthog.json`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify({ _comment: `PostHog trace ${traceId} from ${host}`, results, hasMore: false }, null, 1) + '\n');
console.log(`wrote ${out} (${results.length} spans)`);
