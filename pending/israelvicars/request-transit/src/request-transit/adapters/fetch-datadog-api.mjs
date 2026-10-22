// adapters/fetch-datadog-api.mjs: pull every span of one trace from the Datadog Spans API and save
// it as a datadog-v2 file that build.mjs understands. UNTESTED against a live account (this
// playground has no Datadog keys); the response shape it writes is the one normalize.mjs parses.
//
// Keys come from the environment only. Never put them in this repo, a sample file, or a prompt.
//   export DD_API_KEY=...            # organization API key
//   export DD_APP_KEY=...            # application key with the apm_read scope
//   export DD_SITE=datadoghq.com     # or datadoghq.eu, us3.datadoghq.com, us5.datadoghq.com, ...
// usage: node adapters/fetch-datadog-api.mjs <trace_id> [--from now-1h] [--to now] [--out traces/<id>.json]
// Rate limit: 300 requests per hour on this endpoint. One call returns up to 1000 spans.
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const argv = process.argv.slice(2); const opt = {}; const pos = [];
for (let i = 0; i < argv.length; i++) argv[i].startsWith('--') ? (opt[argv[i].slice(2)] = argv[++i]) : pos.push(argv[i]);
const traceId = pos[0];
const { DD_API_KEY, DD_APP_KEY, DD_SITE = 'datadoghq.com' } = process.env;
if (!traceId || !DD_API_KEY || !DD_APP_KEY) {
  console.error('usage: DD_API_KEY=... DD_APP_KEY=... [DD_SITE=datadoghq.com] node adapters/fetch-datadog-api.mjs <trace_id> [--from now-1h] [--to now]');
  process.exit(1);
}
const url = `https://api.${DD_SITE}/api/v2/spans/events/search`;
const data = []; let cursor;
do {
  const body = { data: { type: 'search_request', attributes: {
    filter: { query: `trace_id:${traceId}`, from: opt.from || 'now-1h', to: opt.to || 'now' },
    sort: 'timestamp', page: { limit: 1000, ...(cursor ? { cursor } : {}) } } } };
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', 'DD-API-KEY': DD_API_KEY, 'DD-APPLICATION-KEY': DD_APP_KEY }, body: JSON.stringify(body) });
  if (!res.ok) { console.error(`Datadog API ${res.status}: ${await res.text()}`); process.exit(1); }
  const page = await res.json();
  data.push(...(page.data || []));
  cursor = page.meta && page.meta.page && page.meta.page.after;
} while (cursor);
if (!data.length) { console.error('no spans found: check the trace id, the time window (--from/--to) and that the spans are indexed (retention filters)'); process.exit(1); }
const out = opt.out || `traces/${traceId}.json`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify({ _comment: `Datadog Spans API export of trace ${traceId}`, data }, null, 1));
console.log(`wrote ${out}: ${data.length} spans. Next: node build.mjs ${out} --out out/${traceId}.html`);
