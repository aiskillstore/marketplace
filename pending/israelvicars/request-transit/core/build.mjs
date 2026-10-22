// core/build.mjs: trace file (OTLP JSON, Datadog span JSON, Datadog Spans API v2, or normalized)
// -> one self-contained transit.html (trace, fonts and code inlined; no network at view time).
//
// usage: node core/build.mjs <trace.json> [--share] [--out transit-out/transit.html] [--format otlp|datadog|datadog-v2|internal]
//        [--trace-id ID] [--title "..."] [--subtitle "..."] [--slow-ms N] [--ms-per-sec N]
//        [--target-seconds 9] [--redact key1,key2] [--no-default-redact]
//        [--strict | --share] [--keep-uuids] [--keep-ci-titles] [--no-scrub]   (value scrubbing, see core/scrub.mjs)
//        --share: strict scrubbing, refuses --no-scrub, opens paused on the first SERVICE ALERT with a verdict headline.
//        Without --out the file is ./transit-out/<title>-<alert>-service-alert.html (see core/verdict.mjs), else
//        ./transit-out/transit.html; an existing file is never overwritten (-2, -3, ... is added). --out is used as given.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseJsonSafe } from '../src/request-transit/adapters/normalize.mjs';
import { pickAdapter } from './adapters.mjs';
import { existsSync } from 'node:fs';
import { matchTrace } from '../src/request-transit/contracts/match.mjs';
import { resolveVocab } from './vocab.mjs';
import { compressGaps, DEFAULT_MAX_GAP_MS } from './gaps.mjs';
import { scrubTrace, scrubLevel } from './scrub.mjs';
import { parseArgs, runCli, UserError } from './cli.mjs';
import { verdict, defaultName } from './verdict.mjs';
const DEFAULT_DIR = 'transit-out';
export const DEFAULT_INDEX = '.transit-cache/contracts/index.json';

const HERE = dirname(fileURLToPath(import.meta.url));
// attribute keys dropped before anything is rendered (span attributes can carry PII)
export const DEFAULT_REDACT = /(^|[._-])(user|email|phone|token|auth|authorization|password|passwd|secret|cookie|set-cookie|session|card|ssn|credentials?|jwt|bearer|api[_-]?key|apikey|private[_-]?key|access[_-]?key)([._-]|$)|^(client|user)\.(address|ip)$|^enduser\./i;

export function redact(trace, keys = [], useDefault = true) {
  const set = new Set(keys);
  let n = 0;
  for (const s of trace.spans) {
    if (!s.attrs) continue;
    for (const k of Object.keys(s.attrs)) if (set.has(k) || (useDefault && DEFAULT_REDACT.test(k))) { delete s.attrs[k]; n++; }
  }
  trace.meta.redacted = n;
  return trace;
}

// A request trace from one service (e.g. telemetrygen, a monolith) would draw one station and no hops.
// Then stations become operations: each non-root span's service is its span name, with a trailing
// counter or id dropped ("okey-dokey-7" -> "okey-dokey") so N numbered children share one station.
export function splitSingleService(trace) {
  const services = new Set(trace.spans.map((s) => s.service));
  if (services.size !== 1 || trace.spans.length < 2) return false;
  // calls to an uninstrumented peer (DB, AWS service, broker) already give the map a second station
  if (trace.spans.some((s) => s.peer && s.peer !== s.service)) return false;
  const svc = [...services][0];
  const op = (name) => String(name || 'span').replace(/[\s._:#/-]*(\d+|[0-9a-f]{8,})$/i, '').slice(0, 40) || String(name);
  const ops = new Set();
  for (const s of trace.spans) if (s.parentId) { s.attrs = Object.assign({}, s.attrs, { 'service.name': svc }); s.service = op(s.name); ops.add(s.service); }
  trace.meta.warnings.push(`single-service trace (${svc}): stations are operations (${ops.size} span name${ops.size === 1 ? '' : 's'})`);
  return true;
}

// JSON, or JSON Lines (agent sessions); anything else is a UserError with the reason, never a stack trace
export function readInput(file) {
  let input;
  try { input = readFileSync(file, 'utf8'); }
  catch (e) { throw new UserError(e.code === 'ENOENT' ? `no such file: ${file}` : e.code === 'EISDIR' ? `${file} is a directory, expected a trace file` : `cannot read ${file}: ${e.code || e.message}`); }
  if (!input.trim()) throw new UserError(`${file} is empty; expected a trace export (JSON) or an agent session (JSON Lines)`);
  try { return parseJsonSafe(input); }
  catch (jsonErr) {
    const lines = input.split(/\r?\n/).map((l, i) => [l, i + 1]).filter(([l]) => l.trim());
    if (lines.length < 2) throw new UserError(`${file} is not valid JSON (${jsonErr.message.replace(/\s+/g, ' ').slice(0, 160)})`);
    return lines.map(([l, n]) => { try { return parseJsonSafe(l); } catch (e) { throw new UserError(`${file} is neither JSON nor JSON Lines: line ${n} does not parse (${e.message.replace(/\s+/g, ' ').slice(0, 160)})`); } });
  }
}

export function build(file, opt = {}) {
  const doc = readInput(file);
  if (doc === null || typeof doc !== 'object') throw new UserError(`${file} holds a JSON ${doc === null ? 'null' : typeof doc}, not a trace; see the supported formats in src/request-transit/SKILL.md`);
  let adapter, trace;
  try {
    adapter = pickAdapter(doc, opt.format);
    trace = adapter.normalize(doc, { format: adapter.format, traceId: opt['trace-id'], showArgs: !!opt['show-args'], maxSteps: opt['max-steps'] != null ? Number(opt['max-steps']) : undefined });
  } catch (e) {
    if (e instanceof UserError) throw e;
    throw new UserError(`could not read ${file} as a trace: ${e.message}`);
  }
  if (opt.share && (opt['no-scrub'] || opt.scrub === 'off')) throw new UserError('--share pages are meant to be dropped into Slack, so value scrubbing cannot be turned off: remove --no-scrub (or build without --share for local debugging)');
  redact(trace, opt.redact ? String(opt.redact).split(',') : [], !opt['no-default-redact']);
  scrubTrace(trace, scrubLevel(opt), adapter.format);
  const vizOpts = {};
  if (!['gh-actions', 'claude-code', 'codex', 'cursor'].includes(adapter.format)) splitSingleService(trace);
  // the verdict's "after N" is wall time, so keep the start/end times from before gap shortening
  const wallSpans = new Map(trace.spans.map((s) => [s.spanId, { start: s.start, duration: s.duration }]));
  // agent sessions and CI runs: shorten idle gaps (--max-gap-ms N, 0 or --no-compress-gaps to keep wall time)
  const family = adapter.format === 'gh-actions' ? 'ci' : ['claude-code', 'codex', 'cursor'].includes(adapter.format) ? 'agent' : null;
  if (family && !opt['no-compress-gaps']) {
    const gaps = compressGaps(trace, opt['max-gap-ms'] != null ? Number(opt['max-gap-ms']) : DEFAULT_MAX_GAP_MS[family]);
    if (gaps) {
      trace.meta.gaps = gaps;
      trace.meta.warnings.push(`shortened ${gaps.count} idle gap(s) longer than ${gaps.maxGapMs / 1000} s (${Math.round(gaps.removedMs / 1000)} s of wall time cut); pass --max-gap-ms 0 for wall time`);
      vizOpts.gapNote = `${gaps.count} idle gap${gaps.count === 1 ? '' : 's'} shortened, not wall-clock`;
    }
  }
  // a large CI run keeps only failed/cancelled steps as stations: say so on the map, not just in the console
  if (adapter.format === 'gh-actions' && trace.meta.warnings.some((w) => w.startsWith('large run:'))) vizOpts.gapNote = [vizOpts.gapNote, 'failed steps only'].filter(Boolean).join('  ·  ');
  if (opt.title) vizOpts.title = opt.title;
  if (opt.subtitle) vizOpts.subtitle = opt.subtitle;
  if (opt['slow-ms']) vizOpts.slowMs = Number(opt['slow-ms']);
  if (opt['ms-per-sec']) vizOpts.msPerSec = Number(opt['ms-per-sec']);
  if (opt['target-seconds']) vizOpts.targetSeconds = Number(opt['target-seconds']);
  if (adapter.format === 'gh-actions') vizOpts.ciStepsAsStations = true;
  vizOpts.vocab = resolveVocab(opt.vocab || (adapter.format === 'gh-actions' ? 'ci' : adapter.format && ['claude-code', 'codex', 'cursor'].includes(adapter.format) ? 'agent' : undefined));
  const v = verdict(trace, vizOpts.vocab, wallSpans);
  if (opt.share) vizOpts.share = { verdict: v.text, origin: v.origin, message: v.message };
  // contracts are opt-in: only an explicit --contracts [index.json] reads an index, and it never builds one
  let contracts = null;
  if (opt.contracts) {
    const ix = opt.contracts === true ? DEFAULT_INDEX : opt.contracts;
    if (!existsSync(ix)) throw new Error(`--contracts: no index at ${ix}. Build one first (ask the user): node src/request-transit/scripts/transit.mjs index --config transit.config.json`);
    contracts = matchTrace(trace, JSON.parse(readFileSync(ix, 'utf8')));
  }
  const js = `window.TRACE = ${JSON.stringify(trace)};\nwindow.VIZ_OPTS = ${JSON.stringify(vizOpts)};\nwindow.CONTRACTS = ${JSON.stringify(contracts)};`.replace(/<\//g, '<\\/');
  const face = (w) => `@font-face { font-family: "Transit Sans"; font-weight: ${w}; font-style: normal; src: url(data:font/woff;base64,${readFileSync(join(HERE, `fonts/arimo-${w}.woff`)).toString('base64')}) format("woff"); }`;
  const tpl = readFileSync(join(HERE, 'transit.template.html'), 'utf8');
  if (!tpl.includes('/*__TRACE_DATA__*/') || !tpl.includes('/*__FONTS__*/')) throw new Error('template placeholder missing');
  const html = tpl.replace('/*__FONTS__*/', () => face(400) + '\n  ' + face(700)).replace('/*__TRACE_DATA__*/', () => js);
  // default: ./transit-out/ (the same folder the render teaser uses); never overwrite an earlier default file
  let out = resolve(opt.out || join(DEFAULT_DIR, defaultName(opt.title, v)));
  if (!opt.out) for (let i = 2; existsSync(out); i++) out = resolve(DEFAULT_DIR, defaultName(opt.title, v).replace(/\.html$/, `-${i}.html`));
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, html);
  return { out, trace, contracts, verdict: v.text };
}

if (process.argv[1] && process.argv[1].endsWith('/build.mjs')) await runCli(async () => {
  await (await import('./setup.mjs')).ensureSetup({ need: [] });   // node version only; the HTML needs no deps
  const { opt, pos } = parseArgs(process.argv.slice(2));
  if (!pos[0]) throw new UserError('usage: node core/build.mjs <trace.json> [--share] [--out transit-out/transit.html] [--title ...] [--strict]');
  const { out, trace, contracts, verdict: vt } = build(pos[0], opt);
  for (const w of trace.meta.warnings) console.error('warning:', w);
  const sc = trace.meta.scrub;
  console.log(`wrote ${out} (${trace.spans.length} spans, ${trace.meta.format}${trace.meta.synthetic ? ', synthetic' : ''}, ${trace.meta.redacted} attrs redacted, ${sc.level === 'off' ? 'value scrubbing OFF' : `${sc.values} values scrubbed (${sc.level})`}${contracts ? `, contracts: ${Object.values(contracts.bySpan).filter((m) => m.state === 'matched' || m.state === 'fallback').length} matched / ${Object.values(contracts.bySpan).filter((m) => m.state === 'unmatched').length} unmatched / ${Object.values(contracts.bySpan).filter((m) => m.state === 'infra').length} infra` : ''})`);
  if (opt.share) console.log(`share: drop ${out} into Slack. Suggested message: "${vt}"`);
});
