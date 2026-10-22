// adapters/fetch-xray.mjs: pull one trace from AWS X-Ray with the AWS CLI and save the BatchGetTraces
// response as a file normalize.mjs auto-detects (format "xray").
// UNTESTED against a live AWS account. Uses your normal AWS CLI credentials (AWS_PROFILE / AWS_REGION /
// SSO); nothing is stored. Needs xray:BatchGetTraces (and xray:GetTraceSummaries for --find).
// X-Ray samples about 5% of requests by default unless CloudWatch Transaction Search is on.
//
// usage: node adapters/fetch-xray.mjs <trace id> [--out traces/<id>.xray.json] [--region R] [--profile P]
//        node adapters/fetch-xray.mjs --find [--minutes 60] [--filter 'fault = true'] [--region R]
//   trace id: X-Ray form 1-5f84c7a5-2b0c... or the 32-hex OTel form (converted)
import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const argv = process.argv.slice(2); const opt = {}; const pos = [];
for (let i = 0; i < argv.length; i++) {
  if (!argv[i].startsWith('--')) { pos.push(argv[i]); continue; }
  const k = argv[i].slice(2);
  if (k === 'find') opt.find = true; else opt[k] = argv[++i];
}
const common = [...(opt.region ? ['--region', opt.region] : []), ...(opt.profile ? ['--profile', opt.profile] : []), '--output', 'json'];
function aws(args) {
  try { return JSON.parse(execFileSync('aws', ['xray', ...args, ...common], { encoding: 'utf8', maxBuffer: 256 << 20, stdio: ['ignore', 'pipe', 'inherit'] })); }
  catch (e) { if (e.code === 'ENOENT') console.error('aws CLI not found: install AWS CLI v2 (brew install awscli) and sign in (aws sso login)'); process.exit(e.status || 1); }
}
const toXray = (id) => /^[0-9a-f]{32}$/i.test(id) ? `1-${id.slice(0, 8)}-${id.slice(8)}`.toLowerCase() : id;

if (opt.find) {
  const end = Math.floor(Date.now() / 1000), start = end - 60 * Number(opt.minutes || 60);
  const r = aws(['get-trace-summaries', '--start-time', String(start), '--end-time', String(end), ...(opt.filter ? ['--filter-expression', opt.filter] : []), '--sampling']);
  const rows = (r.TraceSummaries || []).slice(0, 20);
  if (!rows.length) { console.error('no traces in that window'); process.exit(1); }
  for (const t of rows) console.log(`${t.Id}  ${(t.Duration * 1000).toFixed(0)} ms  ${t.HasFault ? 'fault' : t.HasError ? 'error' : t.HasThrottle ? 'throttle' : 'ok'}  ${t.Http && t.Http.HttpURL || ''}`);
  process.exit(0);
}
const id = pos[0] && toXray(pos[0]);
if (!id || !/^1-[0-9a-f]{8}-[0-9a-f]{24}$/i.test(id)) { console.error('usage: node adapters/fetch-xray.mjs <1-xxxxxxxx-24hex | 32-hex trace id> [--out file] | --find'); process.exit(1); }
// the CLI follows NextToken pages itself; merge in case several Traces entries come back
const r = aws(['batch-get-traces', '--trace-ids', id]);
if (!r.Traces || !r.Traces.length) { console.error(`X-Ray returned no trace for ${id}${r.UnprocessedTraceIds && r.UnprocessedTraceIds.length ? ' (unprocessed)' : ''}. Traces are kept 30 days and only sampled requests exist.`); process.exit(1); }
const out = opt.out || `traces/${id}.xray.json`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify(r, null, 1) + '\n');
console.log(`wrote ${out} (${r.Traces.reduce((n, t) => n + t.Segments.length, 0)} segment documents)`);
