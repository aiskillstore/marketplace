// normalize.mjs: turn a trace file into the one internal schema the viz understands.
//
//   { traceId, meta: {format, source, synthetic, startUnixNs, warnings[]},
//     spans: [{ spanId, parentId, service, name, start, duration, status, kind,
//               statusMessage?, peer?, operation?, attrs? }] }
//
//   start, duration  milliseconds (floats); start is relative to the earliest span in the trace
//   status           'ok' | 'error' | 'unset'
//   kind             'server' | 'client' | 'producer' | 'consumer' | 'internal'
//   peer             optional name of the thing a client/producer span talks to when that thing
//                    is not instrumented (a database, a broker); becomes an inferred node
//   attrs            a small whitelist of attributes (peer, db, messaging, http, rpc keys)
//
// Supported inputs (auto-detected, or force with --format):
//   posthog    PostHog Distributed Tracing spans (REST trace endpoint / MCP apm-trace-get)
//   otlp       OTLP JSON ({resourceSpans:[...]}), hex or base64 ids, numeric or string enums
//   datadog    Datadog tracer/agent span JSON: [[span,...]] or [span,...] or {spans:[...]} or
//              {traces:[[...]]} where span = {trace_id, span_id, parent_id, service, resource,
//              name, start (ns), duration (ns), error (0/1), meta {}, metrics {}, type}
//   datadog-v2 Datadog Spans API (GET /api/v2/spans/events, POST .../events/search) response:
//              {data:[{type:'spans', attributes:{trace_id, span_id, parent_id, service,
//              resource_name, start_timestamp, end_timestamp, custom:{...}, tags:[...]}}]}
//   tempo      Grafana Tempo trace-by-id: v1 /api/traces/<id> ({batches:[ResourceSpans]}) or
//              v2 /api/v2/traces/<id> ({trace:{resourceSpans|batches}, status?}); OTLP inside, ids base64
//              (protobuf-JSON) or hex, enums as strings or numbers, scopeSpans or instrumentationLibrarySpans
//   jaeger     Jaeger v2 query API /api/v3/traces[/<id>] ({result:{resourceSpans:[...]}}): OTLP inside
//   xray       AWS X-Ray BatchGetTraces response or segment documents (segments + nested subsegments)
//   internal   already-normalized JSON (passed through and re-validated)
//
// CLI: node normalize.mjs <trace.json> [--format otlp|jaeger|tempo|posthog|xray|datadog|datadog-v2|internal] [--trace-id ID]
//      prints the normalized JSON to stdout
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const KEEP_ATTRS = /^(peer\.service|server\.address|net\.peer\.name|db\.(system|type|name|instance)|messaging\.(system|destination\.name|operation)|kafka\.topic|http\.(request\.method|method|route|status_code|response\.status_code|url)|url\.(full|path)|rpc\.(system|service|method|grpc\.status_code)|out\.host|span\.kind|component|error\.(message|msg|type)|app\.[\w.]+)$/;

// JSON.parse turns 64-bit ids like 9876543210987654321 (and ns timestamps) into lossy doubles.
// Quote any bare integer with 16+ digits that is the value of an id or ns-time key before parsing.
export function parseJsonSafe(text) {
  return JSON.parse(text.replace(/("(?:trace_id|span_id|parent_id|traceId|spanId|parentId|parentSpanId|start|duration|startTimeUnixNano|endTimeUnixNano)"\s*:\s*)(\d{16,})/g, '$1"$2"'));
}

export function detectFormat(doc) {
  if (doc && Array.isArray(doc.resourceSpans)) return 'otlp';
  if (doc && doc.result && Array.isArray(doc.result.resourceSpans)) return 'jaeger';
  if (tempoResourceSpans(doc)) return 'tempo';
  const xr = isXray(doc);
  if (xr === 'summaries') throw new Error('this is GetTraceSummaries output (trace ids only, no segments): fetch the segments with `aws xray batch-get-traces --trace-ids <Id>` or scripts/fetch.mjs xray <Id>');
  if (xr) return 'xray';
  const ph = posthogSpans(doc);
  if (ph && ph[0] && 'span_id' in ph[0] && ('duration_nano' in ph[0] || 'service_name' in ph[0])) return 'posthog';
  if (doc && Array.isArray(doc.data) && doc.data[0] && doc.data[0].attributes && 'span_id' in doc.data[0].attributes) return 'datadog-v2';
  const first = Array.isArray(doc) ? (Array.isArray(doc[0]) ? doc[0][0] : doc[0])
    : doc && Array.isArray(doc.traces) ? doc.traces[0]?.[0]
    : doc && Array.isArray(doc.spans) ? doc.spans[0] : null;
  if (first && 'span_id' in first && 'trace_id' in first) return 'datadog';
  if (first && 'spanId' in first && 'start' in first && 'duration' in first) return 'internal';
  throw new Error('unrecognized trace format: expected OTLP JSON (resourceSpans), Jaeger /api/v3 (result.resourceSpans), Grafana Tempo (batches / trace.resourceSpans), PostHog tracing spans (span_id/service_name/duration_nano), Datadog spans (trace_id/span_id), AWS X-Ray (BatchGetTraces / segment documents) or the internal schema');
}

// ---------------------------------------------------------------- Grafana Tempo
// Tempo wraps OTLP. v1: {batches:[...]}. v2: {trace:{resourceSpans:[...]}} (older builds: trace.batches),
// with status "PARTIAL"/"COMPLETE" and an optional message when the trace was cut (size limit, q filter).
function tempoResourceSpans(doc) {
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return null;
  if (Array.isArray(doc.batches)) return doc.batches;
  const t = doc.trace;
  if (t && typeof t === 'object') {
    if (Array.isArray(t.resourceSpans)) return t.resourceSpans;
    if (Array.isArray(t.batches)) return t.batches;
    if (!Object.keys(t).length) return [];
  }
  return null;
}
function fromTempo(doc) {
  const rs = tempoResourceSpans(doc) || [];
  const r = fromOtlp({ resourceSpans: rs });
  const warnings = [...(r.raw.warnings || [])];
  const st = String(doc.status || '').toUpperCase();
  if (st.includes('PARTIAL')) warnings.push(`Tempo returned a PARTIAL trace${doc.message ? `: ${doc.message}` : ''}; some spans may be missing`);
  r.raw.warnings = warnings;
  r.source = r.source || (doc._comment ? String(doc._comment) : null);
  return r;
}

// ---------------------------------------------------------------- OTLP
const OTLP_KIND = { 0: 'internal', 1: 'internal', 2: 'server', 3: 'client', 4: 'producer', 5: 'consumer' };
const otlpKind = (k) => typeof k === 'string'
  ? (k.replace(/^SPAN_KIND_/, '').toLowerCase().replace('unspecified', 'internal'))
  : OTLP_KIND[k] || 'internal';
const otlpStatus = (s) => {
  const c = s && s.code;
  if (c === 2 || c === 'STATUS_CODE_ERROR') return 'error';
  if (c === 1 || c === 'STATUS_CODE_OK') return 'ok';
  return 'unset';
};
// OTLP/JSON says hex; some exporters emit protobuf-default base64. 16/32 hex chars stay as-is.
const otlpId = (id) => {
  if (!id) return null;
  if (/^[0-9a-f]+$/i.test(id) && (id.length === 16 || id.length === 32)) return id.toLowerCase();
  try { const hex = Buffer.from(id, 'base64').toString('hex'); if (hex.length === 16 || hex.length === 32) return hex; } catch {}
  return id;
};
const anyValue = (v) => v == null ? null : 'stringValue' in v ? v.stringValue : 'intValue' in v ? Number(v.intValue)
  : 'doubleValue' in v ? v.doubleValue : 'boolValue' in v ? v.boolValue
  : 'arrayValue' in v ? (v.arrayValue.values || []).map(anyValue) : JSON.stringify(v);
const kvs = (list) => Object.fromEntries((list || []).map((a) => [a.key, anyValue(a.value)]));

function fromOtlp(doc) {
  const raw = [];
  for (const rs of doc.resourceSpans) {
    const res = kvs(rs.resource && rs.resource.attributes);
    const service = res['service.name'] || 'unknown_service';
    for (const ss of rs.scopeSpans || rs.instrumentationLibrarySpans || []) {
      for (const s of ss.spans || []) {
        const a = kvs(s.attributes);
        const kind = otlpKind(s.kind);
        raw.push({
          traceId: otlpId(s.traceId), spanId: otlpId(s.spanId), parentId: otlpId(s.parentSpanId),
          service, name: s.name, kind,
          startNs: BigInt(s.startTimeUnixNano), endNs: BigInt(s.endTimeUnixNano),
          status: otlpStatus(s.status), statusMessage: s.status && s.status.message || undefined,
          peer: (kind === 'client' || kind === 'producer') ? (a['peer.service'] || a['db.system'] && (a['server.address'] || a['db.system']) || a['messaging.system'] || undefined) : undefined,
          attrs: pick(a),
        });
      }
    }
  }
  return { raw, format: 'otlp', source: doc._comment };
}

// ---------------------------------------------------------------- Datadog (tracer / agent JSON)
// Field mapping (documented in README.md):
//   trace_id (uint64, decimal)  -> traceId; if any span of that trace carries meta['_dd.p.tid']
//                                  (upper 64 bits, hex) the traceId becomes the full 128-bit
//                                  W3C/OTel hex id, so it matches the OTel trace id
//   span_id                     -> spanId (decimal string)
//   parent_id (0 = root)        -> parentId (null for 0 / missing)
//   service                     -> service
//   resource                    -> name  (e.g. "GET /api/checkout"); falls back to name
//   name                        -> operation (e.g. "grpc.client", "http.request")
//   start (ns since epoch)      -> start (ms, relative to the earliest span)
//   duration (ns)               -> duration (ms)
//   error (0/1)                 -> status 'error' | 'ok'; message from meta error.message|error.msg
//   meta['span.kind']           -> kind; if absent, inferred from type (web=server,
//                                  http/grpc/db/sql/cache/redis=client, queue=producer|consumer)
//   meta peer.service | out.host | db.system/db.type | messaging.system -> peer (client spans)
const DD_TYPE_KIND = { web: 'server', http: 'client', grpc: 'client', db: 'client', sql: 'client', cache: 'client',
  redis: 'client', memcached: 'client', cassandra: 'client', elasticsearch: 'client', mongodb: 'client' };
function ddKind(meta, type, name) {
  const k = meta['span.kind'];
  if (k) return k === 'broker' ? 'producer' : k;
  if (type === 'queue' || /kafka|rabbitmq|sqs|queue/.test(name || '')) return /consume|receive|process/.test(name || '') ? 'consumer' : 'producer';
  return DD_TYPE_KIND[type] || 'internal';
}
const ddParent = (p) => (p === undefined || p === null || String(p) === '0' || p === '') ? null : String(p);
// Tracers only put _dd.p.tid on the first span of each chunk, so look it up per 64-bit trace id.
function ddTraceId(tid, hiByTid) {
  const hi = hiByTid.get(String(tid));
  return hi ? hi.toLowerCase().padStart(16, '0') + BigInt(tid).toString(16).padStart(16, '0') : String(tid);
}
function ddPeer(meta, kind) {
  if (!(kind === 'client' || kind === 'producer')) return undefined;
  return meta['peer.service'] || meta['messaging.system'] || meta['db.system'] || meta['db.type'] || meta['out.host'] || undefined;
}
function fromDatadog(doc) {
  const spans = Array.isArray(doc) ? (Array.isArray(doc[0]) ? doc.flat() : doc)
    : Array.isArray(doc.traces) ? doc.traces.flat() : doc.spans;
  const hiByTid = new Map();
  for (const s of spans) if (s.meta && s.meta['_dd.p.tid']) hiByTid.set(String(s.trace_id), s.meta['_dd.p.tid']);
  const raw = spans.map((s) => {
    const meta = s.meta || {};
    const kind = ddKind(meta, s.type, s.name);
    const start = BigInt(s.start), dur = BigInt(s.duration);
    const err = Number(s.error) === 1;
    return {
      traceId: ddTraceId(s.trace_id, hiByTid), spanId: String(s.span_id), parentId: ddParent(s.parent_id),
      service: s.service || 'unknown_service', name: s.resource || s.name, operation: s.name, kind,
      startNs: start, endNs: start + dur,
      status: err ? 'error' : 'ok', statusMessage: err ? (meta['error.message'] || meta['error.msg'] || meta['error.type']) : undefined,
      peer: ddPeer(meta, kind), attrs: pick({ ...meta, ...(s.metrics || {}) }),
    };
  });
  return { raw, format: 'datadog', source: doc._comment };
}

// ---------------------------------------------------------------- PostHog Distributed Tracing
// Shape of POST /api/projects/:id/tracing/spans/trace/:trace_id/ and the MCP tool apm-trace-get:
// {results:[span], hasMore, nextOffset} (also accepted: a bare array, {spans:[...]}, {data:[...]}).
//   trace_id / span_id        hex (HogQL returns base64: decoded like OTLP ids)
//   parent_span_id            hex; all zeros or empty = root
//   service_name              -> service (fallback resource_attributes['service.name'])
//   name                      -> name
//   kind 0-5 (OTel enum)      -> kind
//   status_code 0/1/2         -> unset/ok/error; message from attributes otel.status_description / exception.message
//   timestamp (ISO start)     -> start; duration_nano -> duration (end_time used if duration missing)
// Sources: posthog.com/docs/api/tracing-2, PostHog products/tracing/skills/.../spans-and-fields.md
function posthogSpans(doc) {
  if (Array.isArray(doc)) return doc;
  if (!doc || typeof doc !== 'object') return null;
  for (const k of ['results', 'spans', 'data']) if (Array.isArray(doc[k])) return doc[k];
  return null;
}
// ISO 8601 with up to 9 fractional digits -> BigInt ns since epoch (Date.parse keeps only ms)
function isoToNs(iso) {
  const m = String(iso).match(/^(.*T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:?\d{2})?$/);
  if (!m) return BigInt(Date.parse(iso)) * 1000000n;
  const sec = BigInt(Date.parse(m[1] + (m[3] || 'Z'))) * 1000000n;
  return sec + BigInt((m[2] || '').padEnd(9, '0').slice(0, 9) || '0');
}
const phParent = (p) => (!p || /^0+$/.test(p) || p === 'AAAAAAAAAAA=') ? null : otlpId(p);
// PostHog's tracing API returns no OTel status message and no span events (checked live on US Cloud, 2026-10-18),
// so the error text falls back to attributes the instrumentation sets: gRPC error message, exception message,
// gRPC status name, HTTP status, error.type.
function phStatusMessage(s, a) {
  const direct = a['otel.status_description'] || s.status_message || a['exception.message'] || a['grpc.error_message'] || a['error.message'];
  if (direct) return String(direct);
  const rpc = a['rpc.response.status_code'] ?? a['rpc.grpc.status_code'], http = a['http.response.status_code'] ?? a['http.status_code'];
  const parts = [rpc != null && rpc !== 'OK' && Number(rpc) !== 0 ? `gRPC ${rpc}` : '', http != null && Number(http) >= 400 ? `HTTP ${http}` : '', a['error.type'] || ''].filter(Boolean);
  return parts.length ? parts.join(' · ') : undefined;
}
function fromPosthog(doc) {
  const raw = posthogSpans(doc).map((s) => {
    const a = s.attributes || {}, res = s.resource_attributes || {};
    const kind = OTLP_KIND[Number(s.kind)] || 'internal';
    const startNs = isoToNs(s.timestamp);
    const endNs = s.duration_nano != null ? startNs + BigInt(Math.round(Number(s.duration_nano))) : isoToNs(s.end_time);
    const code = Number(s.status_code);
    const status = code === 2 ? 'error' : code === 1 ? 'ok' : 'unset';
    return {
      traceId: otlpId(s.trace_id), spanId: otlpId(s.span_id), parentId: phParent(s.parent_span_id),
      service: s.service_name || res['service.name'] || 'unknown_service', name: s.name || 'span', kind,
      startNs, endNs, status,
      statusMessage: status === 'error' ? phStatusMessage(s, a) : undefined,
      peer: (kind === 'client' || kind === 'producer') ? (a['peer.service'] || a['db.system'] && (a['server.address'] || a['db.system']) || a['messaging.system'] || undefined) : undefined,
      attrs: pick(a),
    };
  });
  // the innermost failing span often carries only error.type while its server span in the same service has the
  // text (e.g. payment "charge" vs "PaymentService/Charge"); the alert lands on the innermost one, so it borrows it
  const byId = new Map(raw.map((s) => [s.spanId, s])), weak = (s) => !s.statusMessage || s.statusMessage === (s.attrs && s.attrs['error.type']) || !/\s/.test(s.statusMessage);
  for (const s of raw) {
    if (s.status !== 'error' || !weak(s)) continue;
    for (let p = byId.get(s.parentId); p && p.service === s.service; p = byId.get(p.parentId)) if (p.status === 'error' && !weak(p)) { s.statusMessage = p.statusMessage; break; }
  }
  if (doc && doc.hasMore) raw.warnings = ['input says hasMore=true: this is only the first page of spans; fetch every page'];
  return { raw, format: 'posthog', source: doc && doc._comment };
}

// ---------------------------------------------------------------- AWS X-Ray
// Input: the `aws xray batch-get-traces` / BatchGetTraces response {Traces:[{Id, Segments:[{Id, Document}]}]}
// (Document is a JSON string), or {Segments:[...]}, or an array of segment documents, or one segment document.
// GetTraceSummaries output has no segments; it is only for finding trace ids (scripts/fetch.mjs xray --find).
// Segment document fields (docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html):
//   segment                -> span, kind server (consumer when its parent is a producer subsegment)
//     name -> service; id -> spanId; parent_id (upstream subsegment) -> parentId; trace_id 1-xxxxxxxx-24hex -> 32-hex
//     start_time / end_time (epoch seconds, float) -> ns; in_progress without end_time -> end of its children
//   subsegment (nested in subsegments[]) -> span in the same service, parent = enclosing (sub)segment
//     no namespace           -> in-process work: kind internal
//     namespace remote | aws -> downstream call: kind client (producer for SQS/SNS/Kinesis/EventBridge sends),
//                               peer = name; becomes a line to the callee's segment if one has it as parent_id,
//                               else an infrastructure node
//   fault (5xx) / error (4xx) / throttle (429) -> status error; message from cause.exceptions[0] or the flag + HTTP status
//     (errors on internal subsegments inside an aws/remote call are folded into that call)
//   inferred segments (inferred: true, made by X-Ray for AWS services) are dropped: the aws subsegment already draws them
//   http.request.method/url, http.response.status, aws.operation/table_name/queue_url, sql.database_type -> attrs
const XRAY_PRODUCE = /^(SendMessage|SendMessageBatch|Publish|PublishBatch|PutRecord|PutRecords|PutEvents)$/;
function xraySegments(doc) {
  const docs = [];
  const add = (d) => docs.push(typeof d === 'string' ? JSON.parse(d) : d);
  if (doc && Array.isArray(doc.Traces)) { for (const t of doc.Traces) for (const s of t.Segments || []) add(s.Document); }
  else if (doc && Array.isArray(doc.Segments)) { for (const s of doc.Segments) add(s.Document || s); }
  else if (Array.isArray(doc)) { for (const s of doc) add(s.Document || s); }
  else if (doc && doc.trace_id && doc.start_time != null) add(doc);
  return docs;
}
const isXray = (doc) => {
  if (doc && Array.isArray(doc.TraceSummaries)) return 'summaries';
  if (doc && Array.isArray(doc.Traces) && doc.Traces[0] && Array.isArray(doc.Traces[0].Segments)) return 'xray';
  const first = doc && Array.isArray(doc.Segments) ? doc.Segments[0] : Array.isArray(doc) ? doc[0] : doc;
  if (!first || typeof first !== 'object') return null;
  if (first.Document && /"start_time"/.test(first.Document)) return 'xray';
  if (first.trace_id && first.start_time != null && first.id) return 'xray';
  return null;
};
// the awsxray exporter names remote subsegments by span name: a bare HTTP method is replaced by the URL host,
// a gRPC "pkg.Service/Method" by its service, so one remote service is one station
const xrayPeer = (name, url) => {
  const grpc = /^([\w.]+\.\w+)\/\w+$/.exec(name || ''); if (grpc) return grpc[1];
  if (!/^(GET|HEAD|POST|PUT|PATCH|DELETE|OPTIONS)$/i.test(name || '') || !url) return name;
  try { return new URL(url).hostname || name; } catch { return name; }
};
const xrayTraceId = (id) => { const m = /^1-([0-9a-f]{8})-([0-9a-f]{24})$/i.exec(id || ''); return m ? (m[1] + m[2]).toLowerCase() : id; };
const secNs = (x) => BigInt(Math.round(Number(x) * 1e6)) * 1000n;   // X-Ray times carry microseconds
function fromXray(doc) {
  const raw = [], warnings = [];
  let dropped = 0, open = 0;
  const all = xraySegments(doc);
  function walk(s, ctx) {
    // PutTraceSegments also takes standalone subsegment documents (type "subsegment", with trace_id and
    // parent_id); the collector's awsxray exporter sends every non-server span that way. Their service is
    // the enclosing segment's, resolved below once every document is in.
    if (!ctx && s.type === 'subsegment') ctx = { service: null, parent: s.parent_id, traceId: s.trace_id };
    const isSeg = !ctx;
    const svc = isSeg ? s.name : ctx.service;
    const ns = s.namespace;
    const aws = s.aws || {}, http = s.http || {}, req = http.request || {}, res = http.response || {};
    let kind = isSeg ? 'server' : (ns === 'remote' || ns === 'aws') ? 'client' : 'internal';
    if (kind === 'client' && XRAY_PRODUCE.test(aws.operation || '')) kind = 'producer';
    const failed = !!(s.fault || s.error || s.throttle);
    const ex = s.cause && Array.isArray(s.cause.exceptions) && s.cause.exceptions[0];
    const flag = s.throttle ? 'throttled' : s.fault ? 'fault' : 'error';
    const startNs = secNs(s.start_time);
    const kids = (s.subsegments || []).map((c) => walk(c, { service: svc, parent: s.id, traceId: ctx ? ctx.traceId : s.trace_id }));
    let endNs;
    if (s.end_time != null) endNs = secNs(s.end_time);
    else { open++; endNs = kids.reduce((m, k) => (k.endNs > m ? k.endNs : m), startNs); }
    const attrs = pick({
      'http.request.method': req.method, 'url.full': req.url, 'http.response.status_code': res.status,
      'rpc.system': ns === 'aws' ? 'aws-api' : undefined, 'rpc.service': ns === 'aws' ? s.name : undefined, 'rpc.method': aws.operation,
      'db.system': (s.sql && s.sql.database_type) || (aws.table_name ? 'dynamodb' : undefined), 'db.name': aws.table_name,
      'messaging.system': aws.queue_url ? 'aws_sqs' : undefined,
      'messaging.destination.name': aws.queue_url ? String(aws.queue_url).split('/').pop() : aws.topic_arn ? String(aws.topic_arn).split(':').pop() : undefined,
      'component': s.origin,
    });
    const span = {
      traceId: xrayTraceId(isSeg ? s.trace_id : ctx.traceId), spanId: s.id, parentId: isSeg ? (s.parent_id || null) : ctx.parent,
      service: svc || 'unknown_service',
      name: isSeg ? (req.method && req.url ? `${req.method} ${new URL(req.url, 'http://x').pathname}` : s.name)
        : aws.operation ? `${s.name} ${aws.operation}` : (s.sql && s.sql.sanitized_query) || (req.method && req.url ? `${req.method} ${new URL(req.url, 'http://x').pathname}` : s.name),
      kind, startNs, endNs, status: failed ? 'error' : 'ok',
      statusMessage: failed ? (ex && (ex.message || ex.type) ? `${ex.type ? ex.type + ': ' : ''}${ex.message || ''}`.replace(/: $/, '') : `${flag}${res.status ? ' (HTTP ' + res.status + ')' : ''}`) : undefined,
      peer: kind === 'client' || kind === 'producer' ? xrayPeer(s.name, req.url) : undefined,
      operation: aws.operation, attrs,
    };
    if (!svc) span.inheritService = true;
    raw.push(span);
    return span;
  }
  for (const s of all) { if (s.inferred) { dropped++; continue; } walk(s, null); }
  // a segment whose parent is a producer subsegment was delivered through a queue
  const byId = new Map(raw.map((s) => [s.spanId, s]));
  for (const s of raw) {
    if (!s.inheritService) continue;
    let p = byId.get(s.parentId); while (p && p.inheritService) p = byId.get(p.parentId);
    s.service = (p && p.service) || 'unknown_service';
  }
  for (const s of raw) delete s.inheritService;
  // SDK plumbing inside an aws/remote call (attempt, wait, response... in aws-xray-sdk-go) repeats the call's
  // error flag. The call is the error origin, so the alert lands on the AWS service's station, not the caller's.
  const callOf = (s) => { for (let p = byId.get(s.parentId); p; p = byId.get(p.parentId)) { if (p.kind === 'client' || p.kind === 'producer') return p; if (p.kind !== 'internal') return null; } return null; };
  for (const s of raw) {
    if (s.kind !== 'internal' || s.status !== 'error') continue;
    const call = callOf(s); if (!call) continue;
    if (call.status !== 'error') { call.status = 'error'; call.statusMessage = s.statusMessage; }
    s.status = 'ok'; delete s.statusMessage;
  }
  for (const s of raw) { const p = s.parentId && byId.get(s.parentId); if (s.kind === 'server' && p && p.kind === 'producer') s.kind = 'consumer'; }
  if (dropped) warnings.push(`dropped ${dropped} inferred segment(s) (AWS services X-Ray drew from client subsegments)`);
  if (open) warnings.push(`${open} segment(s) still in progress; end set to their last child`);
  if (doc && Array.isArray(doc.UnprocessedTraceIds) && doc.UnprocessedTraceIds.length) warnings.push(`X-Ray could not return: ${doc.UnprocessedTraceIds.join(', ')}`);
  raw.warnings = warnings;
  return { raw, format: 'xray', source: doc && doc._comment };
}

// ---------------------------------------------------------------- Datadog Spans API v2
// attributes.start_timestamp / end_timestamp are ISO-8601 (millisecond precision); durations in
// custom.duration (ns) are preferred when present. error from custom.error, custom.status or a
// "status:error" tag. kind from custom.span.kind / custom['span.kind'].
function fromDatadogV2(doc) {
  const raw = doc.data.map(({ attributes: a }) => {
    const custom = a.custom || {};
    const flat = { ...flatten(custom), ...flatten(a.attributes || {}) };
    const tags = Object.fromEntries((a.tags || []).map((t) => { const i = t.indexOf(':'); return i < 0 ? [t, true] : [t.slice(0, i), t.slice(i + 1)]; }));
    const kind = ddKind(flat, a.type, flat['operation_name'] || '');
    const startNs = BigInt(Date.parse(a.start_timestamp)) * 1000000n;
    const endNs = flat.duration != null ? startNs + BigInt(Math.round(Number(flat.duration))) : BigInt(Date.parse(a.end_timestamp)) * 1000000n;
    const err = Number(flat.error) === 1 || flat.status === 'error' || tags.status === 'error';
    return {
      traceId: String(a.trace_id), spanId: String(a.span_id), parentId: ddParent(a.parent_id),
      service: a.service || 'unknown_service', name: a.resource_name || flat['operation_name'] || 'span', operation: flat['operation_name'], kind,
      startNs, endNs, status: err ? 'error' : 'ok',
      statusMessage: err ? (flat['error.message'] || flat['error.msg']) : undefined,
      peer: ddPeer(flat, kind), attrs: pick(flat),
    };
  });
  return { raw, format: 'datadog-v2', source: doc._comment };
}

function flatten(o, pre = '', out = {}) {
  for (const [k, v] of Object.entries(o)) {
    if (v && typeof v === 'object' && !Array.isArray(v)) flatten(v, pre + k + '.', out); else out[pre + k] = v;
  }
  return out;
}
function pick(a) {
  const o = {};
  for (const [k, v] of Object.entries(a)) if (KEEP_ATTRS.test(k) && v !== undefined && v !== '') o[k] = v;
  return Object.keys(o).length ? o : undefined;
}

// ---------------------------------------------------------------- common
export function normalize(doc, { format, traceId } = {}) {
  if (typeof doc === 'string') doc = parseJsonSafe(doc);
  format = format || detectFormat(doc);
  if (format === 'internal') return validate(doc);
  const { raw, source } = format === 'otlp' ? fromOtlp(doc) : format === 'jaeger' ? fromOtlp(doc.result || doc) : format === 'tempo' ? fromTempo(doc) : format === 'posthog' ? fromPosthog(doc) : format === 'xray' ? fromXray(doc) : format === 'datadog' ? fromDatadog(doc) : fromDatadogV2(doc);
  if (!raw.length) throw new Error('no spans found');
  const warnings = [...(raw.warnings || [])];
  // One trace per viz. Pick the requested one, else the trace with the most spans.
  const counts = new Map();
  for (const s of raw) counts.set(s.traceId, (counts.get(s.traceId) || 0) + 1);
  const tid = traceId || [...counts].sort((a, b) => b[1] - a[1])[0][0];
  if (counts.size > 1) warnings.push(`input has ${counts.size} traces; using ${tid}`);
  const spans = raw.filter((s) => s.traceId === tid);
  if (!spans.length) throw new Error(`trace ${traceId} not found`);
  const t0 = spans.reduce((m, s) => (s.startNs < m ? s.startNs : m), spans[0].startNs);
  const ids = new Set(spans.map((s) => s.spanId));
  const out = spans.map((s) => {
    const o = {
      spanId: s.spanId, parentId: s.parentId && ids.has(s.parentId) ? s.parentId : null,
      service: s.service, name: s.name,
      start: Number(s.startNs - t0) / 1e6, duration: Math.max(0, Number(s.endNs - s.startNs) / 1e6),
      status: s.status, kind: s.kind,
    };
    if (s.parentId && !ids.has(s.parentId)) warnings.push(`span ${s.spanId} (${s.service} ${s.name}) has parent ${s.parentId} that is not in the file; treated as a root`);
    if (s.statusMessage) o.statusMessage = s.statusMessage;
    if (s.peer) o.peer = String(s.peer);
    if (s.operation) o.operation = s.operation;
    if (s.attrs) o.attrs = s.attrs;
    return o;
  }).sort((a, b) => a.start - b.start || (a.parentId ? 1 : -1));
  const synthetic = /synthetic/i.test(source || '');
  return validate({ traceId: tid, meta: { format, source: source || null, synthetic, startUnixNs: String(t0), warnings }, spans: out });
}

export function validate(t) {
  if (!t || !Array.isArray(t.spans) || !t.spans.length) throw new Error('internal schema: spans[] required');
  const KINDS = new Set(['server', 'client', 'producer', 'consumer', 'internal']);
  for (const s of t.spans) {
    for (const k of ['spanId', 'service', 'name']) if (typeof s[k] !== 'string' || !s[k]) throw new Error(`span missing ${k}: ${JSON.stringify(s)}`);
    if (!(s.start >= 0) || !(s.duration >= 0)) throw new Error(`span ${s.spanId}: start/duration must be >= 0 ms`);
    if (!KINDS.has(s.kind)) throw new Error(`span ${s.spanId}: bad kind ${s.kind}`);
    if (!['ok', 'error', 'unset'].includes(s.status)) throw new Error(`span ${s.spanId}: bad status ${s.status}`);
  }
  t.meta = t.meta || { format: 'internal', warnings: [] };
  return t;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const argv = process.argv.slice(2); const opt = {}; const pos = [];
  for (let i = 0; i < argv.length; i++) argv[i].startsWith('--') ? (opt[argv[i].slice(2)] = argv[++i]) : pos.push(argv[i]);
  if (!pos[0]) { console.error('usage: node normalize.mjs <trace.json> [--format otlp|posthog|xray|datadog|datadog-v2|internal] [--trace-id ID]'); process.exit(1); }
  const t = normalize(readFileSync(pos[0], 'utf8'), { format: opt.format, traceId: opt['trace-id'] });
  for (const w of t.meta.warnings) console.error('warning:', w);
  process.stdout.write(JSON.stringify(t, null, 1) + '\n');
}
