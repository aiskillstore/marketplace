// samples/make-posthog-sample.mjs: writes samples/posthog-checkout.json, a SYNTHETIC trace in the
// shape PostHog Distributed Tracing returns (POST /api/projects/:id/tracing/spans/trace/:trace_id/,
// MCP tool apm-trace-get). Built from the synthetic OTel demo checkout so both renders can be compared.
// Not exported from a real PostHog project. Field list: posthog.com/docs/api/tracing-2
import { readFileSync, writeFileSync } from 'node:fs';
const otlp = JSON.parse(readFileSync(new URL('./otel-demo-checkout.otlp.json', import.meta.url), 'utf8'));
const KIND = { SPAN_KIND_UNSPECIFIED: 0, SPAN_KIND_INTERNAL: 1, SPAN_KIND_SERVER: 2, SPAN_KIND_CLIENT: 3, SPAN_KIND_PRODUCER: 4, SPAN_KIND_CONSUMER: 5 };
const val = (v) => v.stringValue ?? (v.intValue != null ? Number(v.intValue) : v.doubleValue ?? v.boolValue);
const kv = (l) => Object.fromEntries((l || []).map((a) => [a.key, val(a.value)]));
const iso = (ns) => { ns = BigInt(ns); const ms = ns / 1000000n; return new Date(Number(ms)).toISOString().replace(/\.\d{3}Z$/, '.' + String(ns % 1000000000n).padStart(9, '0').slice(0, 6) + 'Z'); };
const results = [];
let t0 = null, tEnd = 0n;
for (const rs of otlp.resourceSpans) {
  const res = kv(rs.resource.attributes);
  for (const ss of rs.scopeSpans) for (const s of ss.spans) {
    const st = BigInt(s.startTimeUnixNano), en = BigInt(s.endTimeUnixNano);
    if (t0 === null || st < t0) t0 = st; if (en > tEnd) tEnd = en;
    const code = s.status && s.status.code;
    const attributes = kv(s.attributes);
    if (s.status && s.status.message) attributes['otel.status_description'] = s.status.message;
    results.push({
      uuid: `00000000-0000-4000-8000-${String(results.length).padStart(12, '0')}`,
      trace_id: s.traceId, span_id: s.spanId, parent_span_id: s.parentSpanId || '0000000000000000',
      name: s.name, kind: typeof s.kind === 'number' ? s.kind : KIND[s.kind] ?? 0,
      service_name: res['service.name'],
      status_code: code === 2 || code === 'STATUS_CODE_ERROR' ? 2 : code === 1 || code === 'STATUS_CODE_OK' ? 1 : 0,
      timestamp: iso(st), end_time: iso(en), duration_nano: Number(en - st),
      is_root_span: !s.parentSpanId, attributes, resource_attributes: res,
    });
  }
}
for (const r of results) { r.trace_start = iso(t0); r.trace_duration = Number(tEnd - t0); }
const doc = { _comment: 'SYNTHETIC sample in PostHog Distributed Tracing trace-endpoint shape, derived from samples/otel-demo-checkout.otlp.json. Not real data.', results, hasMore: false, nextOffset: null };
writeFileSync(new URL('./posthog-checkout.json', import.meta.url), JSON.stringify(doc, null, 1) + '\n');
console.log(`wrote samples/posthog-checkout.json (${results.length} spans)`);
