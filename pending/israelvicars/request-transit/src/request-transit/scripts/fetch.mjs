// skills/request-transit/scripts/fetch.mjs: get one trace into the normalized Transit shape. All backends write the same file.
//   file (default, no auth):  node src/request-transit/scripts/fetch.mjs file <trace.json> [--out trace.transit.json] [--trace-id ID]
//   datadog-api (headless/CI): node skills/request-transit/scripts/fetch.mjs datadog-api <trace_id>   (needs DD_API_KEY, DD_APP_KEY, DD_SITE; untested)
//   posthog-api (headless):  node skills/request-transit/scripts/fetch.mjs posthog-api <trace_id> (POSTHOG_API_KEY, POSTHOG_HOST, POSTHOG_PROJECT_ID; untested)
//   xray (headless, AWS CLI):  node skills/request-transit/scripts/fetch.mjs xray <trace id> | xray --find   (your AWS CLI credentials; untested live)
//   tempo (headless):  node skills/request-transit/scripts/fetch.mjs tempo <trace_id> | tempo --find '<TraceQL>'  (TEMPO_URL, optional TEMPO_TOKEN / TEMPO_USER+TEMPO_PASSWORD / TEMPO_TENANT)
//   grafana-mcp (interactive): agent fetches the trace via the Grafana MCP server (or Tempo's own /api/mcp), saves JSON, then `file`.
//   aws-mcp (interactive): agent calls get_xray_trace on the CloudWatch Application Signals MCP server, saves JSON, then `file`.
//   posthog-mcp (interactive): agent calls apm-trace-get, saves the JSON, then uses `file`.
//   datadog-mcp (interactive): not a script. The agent calls the Datadog MCP server, saves the span
//                              JSON it returns to a file, then runs the `file` backend. See references/adapters.md.
import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { normalize } from '../adapters/normalize.mjs';
import { readInput } from '../../../core/build.mjs';
import { ensureSetup } from '../../../core/setup.mjs';
await ensureSetup({ need: [] });
const runChild = (file, args) => { try { execFileSync(process.execPath, [fileURLToPath(new URL(file, import.meta.url)), ...args], { stdio: 'inherit' }); } catch (e) { process.exit(e.status || 1); } };
const [backend, arg, ...rest] = process.argv.slice(2); const opt = {};
for (let i = 0; i < rest.length; i++) if (rest[i].startsWith('--')) opt[rest[i].slice(2)] = rest[++i];
if (backend === 'file' && arg) {
  let t;
  try { t = normalize(readInput(arg), { traceId: opt['trace-id'], format: opt.format }); }
  catch (e) { console.error(`transit: ${e.message.replace(/\s+/g, ' ')}`); process.exit(1); }
  const out = opt.out || arg.replace(/\.json$/, '') + '.transit.json';
  writeFileSync(out, JSON.stringify(t, null, 1) + '\n');
  console.log(`wrote ${out} (${t.spans.length} spans, from ${t.meta.format})`);
} else if (backend === 'datadog-api' && arg) {
  runChild('../adapters/fetch-datadog-api.mjs', [arg, ...rest]);
} else if (backend === 'posthog-api' && arg) {
  runChild('../adapters/fetch-posthog-api.mjs', [arg, ...rest]);
} else if (backend === 'tempo' && arg) {
  runChild('../adapters/fetch-tempo.mjs', [arg, ...rest]);
} else if (backend === 'xray' && arg) {
  runChild('../adapters/fetch-xray.mjs', [arg, ...rest]);
} else {
  console.error('usage: node src/request-transit/scripts/fetch.mjs file <trace.json> | datadog-api <trace_id> | posthog-api <trace_id> | xray <trace_id>|--find | tempo <trace_id>|--find'); process.exit(1);
}
