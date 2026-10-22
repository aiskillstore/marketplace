// samples/make-tempo-sample.mjs: writes samples/tempo-checkout.json, a SYNTHETIC trace in the shape of the
// Grafana Tempo v2 trace-by-id response (GET /api/v2/traces/<id>, JSON), built from the synthetic OTel demo
// checkout. Tempo serializes OTLP with protobuf-JSON conventions: base64 trace/span ids, string enums
// (SPAN_KIND_SERVER, STATUS_CODE_ERROR), int64 as strings. Not exported from a real Tempo.
import { readFileSync, writeFileSync } from 'node:fs';
const otlp = JSON.parse(readFileSync(new URL('./otel-demo-checkout.otlp.json', import.meta.url), 'utf8'));
const b64 = (hex) => hex ? Buffer.from(hex, 'hex').toString('base64') : undefined;
const KIND = ['SPAN_KIND_UNSPECIFIED', 'SPAN_KIND_INTERNAL', 'SPAN_KIND_SERVER', 'SPAN_KIND_CLIENT', 'SPAN_KIND_PRODUCER', 'SPAN_KIND_CONSUMER'];
const CODE = ['STATUS_CODE_UNSET', 'STATUS_CODE_OK', 'STATUS_CODE_ERROR'];
const span = (s) => {
  const o = { traceId: b64(s.traceId), spanId: b64(s.spanId), name: s.name,
    kind: typeof s.kind === 'number' ? KIND[s.kind] : s.kind,
    startTimeUnixNano: String(s.startTimeUnixNano), endTimeUnixNano: String(s.endTimeUnixNano),
    attributes: s.attributes, status: {} };
  if (s.parentSpanId) o.parentSpanId = b64(s.parentSpanId);
  const c = s.status && s.status.code;
  if (c) o.status.code = typeof c === 'number' ? CODE[c] : c;
  if (s.status && s.status.message) o.status.message = s.status.message;
  return o;
};
const doc = {
  _comment: 'SYNTHETIC trace in the Grafana Tempo /api/v2/traces/<id> JSON shape, converted from samples/otel-demo-checkout.otlp.json. Not exported from a running Tempo.',
  trace: { resourceSpans: otlp.resourceSpans.map((rs) => ({ resource: rs.resource,
    scopeSpans: rs.scopeSpans.map((ss) => ({ scope: ss.scope, spans: ss.spans.map(span) })) })) },
  status: 'COMPLETE',
};
writeFileSync(new URL('./tempo-checkout.json', import.meta.url), JSON.stringify(doc, null, 1) + '\n');
console.log('wrote samples/tempo-checkout.json');
