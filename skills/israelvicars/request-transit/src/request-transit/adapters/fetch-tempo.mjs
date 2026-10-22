// adapters/fetch-tempo.mjs: fetch one trace from Grafana Tempo's HTTP API and save it as a file normalize.mjs
// auto-detects (format "tempo"). Tries GET /api/v2/traces/<id> first and falls back to /api/traces/<id>
// when the v2 route doesn't exist (older Tempo). Docs: grafana.com/docs/tempo/latest/api_docs/
//
// Env only (never commit credentials):
//   TEMPO_URL       base URL, e.g. http://localhost:3200 or your Grafana Cloud Tempo endpoint
//   TEMPO_TOKEN     optional bearer token
//   TEMPO_USER + TEMPO_PASSWORD   optional basic auth (Grafana Cloud: instance id + access-policy token)
//   TEMPO_TENANT    optional X-Scope-OrgID for multi-tenant Tempo
// usage: node adapters/fetch-tempo.mjs <trace id hex> [--out file] [--start unix_s --end unix_s] [--v1]
//        node adapters/fetch-tempo.mjs --find '{ status = error }' [--limit 20]
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const argv = process.argv.slice(2); const opt = {}; const pos = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--v1') opt.v1 = true;
  else if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[++i];
  else pos.push(argv[i]);
}
const base = (process.env.TEMPO_URL || '').replace(/\/$/, '');
if (!base) { console.error('set TEMPO_URL (e.g. http://localhost:3200); optional TEMPO_TOKEN or TEMPO_USER/TEMPO_PASSWORD, TEMPO_TENANT'); process.exit(1); }
// what may appear in output files and messages: scheme + host + port only (no user:password@, path or query)
const origin = (() => { try { const u = new URL(base); return `${u.protocol}//${u.host}`; } catch { console.error('TEMPO_URL is not a valid URL (expected e.g. http://localhost:3200)'); process.exit(1); } })();
const headers = { Accept: 'application/json' };
if (process.env.TEMPO_TOKEN) headers.Authorization = `Bearer ${process.env.TEMPO_TOKEN}`;
else if (process.env.TEMPO_USER) headers.Authorization = 'Basic ' + Buffer.from(`${process.env.TEMPO_USER}:${process.env.TEMPO_PASSWORD || ''}`).toString('base64');
// user:password@ in TEMPO_URL becomes Basic auth (fetch refuses URLs with credentials) and never reaches output
const fetchBase = (() => { const u = new URL(base); if (u.username && !headers.Authorization) headers.Authorization = 'Basic ' + Buffer.from(`${decodeURIComponent(u.username)}:${decodeURIComponent(u.password)}`).toString('base64'); u.username = ''; u.password = ''; return u.href.replace(/\/$/, ''); })();
if (process.env.TEMPO_TENANT) headers['X-Scope-OrgID'] = process.env.TEMPO_TENANT;
const range = new URLSearchParams();
if (opt.start) range.set('start', opt.start);
if (opt.end) range.set('end', opt.end);
const get = async (path) => {
  try { return await fetch(fetchBase + path, { headers }); }
  catch (e) { console.error(`cannot reach ${origin}: ${e.cause?.code || 'network error'}`); process.exit(1); }
};

if ('find' in opt) {
  const q = new URLSearchParams({ q: opt.find || '{}', limit: opt.limit || '20', ...Object.fromEntries(range) });
  const r = await get(`/api/search?${q}`);
  if (!r.ok) { console.error(`Tempo ${r.status}: ${(await r.text()).slice(0, 400)}`); process.exit(1); }
  const body = await r.json();
  for (const t of body.traces || []) console.log(`${String(t.traceID).padStart(32, '0')}  ${t.rootServiceName || '?'}  ${t.rootTraceName || ''}  ${t.durationMs ? t.durationMs + 'ms' : '<1ms'}`);   // search drops leading zeros and zero durations
  if (!(body.traces || []).length) console.error('no traces matched');
  process.exit(0);
}

const id = (pos[0] || '').toLowerCase();
if (!/^[0-9a-f]{1,32}$/.test(id)) { console.error('usage: node adapters/fetch-tempo.mjs <trace id hex> [--out file] [--start s --end s] [--v1] | --find "<TraceQL>"'); process.exit(1); }
const qs = range.toString() ? `?${range}` : '';
let r, version = 'v2';
if (!opt.v1) r = await get(`/api/v2/traces/${id}${qs}`);
// A missing v2 route answers Go's generic "404 page not found"; a missing trace has its own message.
if (opt.v1 || (r.status === 404 && /^\s*404 page not found/i.test(await r.clone().text()))) { version = 'v1'; r = await get(`/api/traces/${id}${qs}`); }
if (r.status === 404) { console.error(`trace ${id} not found in Tempo (check the id, tenant and retention; try --start/--end)`); process.exit(1); }
if (!r.ok) { console.error(`Tempo ${r.status}: ${(await r.text()).slice(0, 400)}`); process.exit(1); }
const body = await r.json();
const out = opt.out || `traces/${id}.tempo.json`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify({ _comment: `Tempo ${version} trace ${id} from ${origin}`, ...body }, null, 1) + '\n');
const n = JSON.stringify(body).match(/"spanId"/g)?.length || 0;
console.log(`wrote ${out} (${n} spans, Tempo ${version} API)${/partial/i.test(String(body.status || '')) ? ' - PARTIAL trace' : ''}`);
