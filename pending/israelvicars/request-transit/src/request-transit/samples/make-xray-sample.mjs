// samples/make-xray-sample.mjs: writes samples/xray-checkout.json, a SYNTHETIC trace in the shape of the
// AWS X-Ray BatchGetTraces response (`aws xray batch-get-traces`), built from the synthetic OTel demo
// checkout so the two renders can be compared. Not exported from a real AWS account.
//   server/consumer spans -> one segment per service hop, with parent_id = the calling subsegment
//   client spans          -> subsegments, namespace "remote" (the kafka publish becomes an SQS SendMessage,
//                            namespace "aws", plus the inferred SQS segment X-Ray would add)
//   internal spans        -> subsegments without a namespace
//   error spans           -> fault: true + cause.exceptions (one throttled DynamoDB-style call is not added:
//                            the sample keeps the same trip as the OTLP original)
// Format: docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html
import { readFileSync, writeFileSync } from 'node:fs';
const otlp = JSON.parse(readFileSync(new URL('./otel-demo-checkout.otlp.json', import.meta.url), 'utf8'));
const val = (v) => v.stringValue ?? (v.intValue != null ? Number(v.intValue) : v.doubleValue ?? v.boolValue);
const kv = (l) => Object.fromEntries((l || []).map((a) => [a.key, val(a.value)]));
const K = (k) => typeof k === 'string' ? k.replace('SPAN_KIND_', '').toLowerCase() : ['internal', 'internal', 'server', 'client', 'producer', 'consumer'][k];
const spans = [];
for (const rs of otlp.resourceSpans) {
  const svc = kv(rs.resource.attributes)['service.name'];
  for (const ss of rs.scopeSpans) for (const s of ss.spans) spans.push({ ...s, svc, kind: K(s.kind), a: kv(s.attributes) });
}
const tid = spans[0].traceId;
const xid = `1-${tid.slice(0, 8)}-${tid.slice(8)}`;
const sec = (ns) => Number(BigInt(ns) / 1000n) / 1e6;
const byId = new Map(spans.map((s) => [s.spanId, s]));
const kids = (id) => spans.filter((s) => s.parentSpanId === id);
const isSeg = (s) => !s.parentSpanId || s.kind === 'server' || s.kind === 'consumer' || byId.get(s.parentSpanId).svc !== s.svc;
function body(s) {
  const d = { id: s.spanId, name: s.svc, start_time: sec(s.startTimeUnixNano), end_time: sec(s.endTimeUnixNano) };
  const code = s.a['http.response.status_code'] || s.a['http.status_code'];
  const failed = s.status && (s.status.code === 2 || s.status.code === 'STATUS_CODE_ERROR');
  if (s.a['http.request.method'] || s.a['http.method']) d.http = { request: { method: s.a['http.request.method'] || s.a['http.method'], url: s.a['url.full'] || 'https://shop.example/' + (s.a['http.route'] || s.name.split(' ').pop()).replace(/^\//, '') }, response: code ? { status: code } : undefined };
  if (failed) { d.fault = true; d.cause = { exceptions: [{ id: s.spanId.slice(0, 16), type: 'ServiceError', message: s.status.message || 'error' }] }; }
  return d;
}
function sub(s) {
  const d = body(s);
  if (!s.parentSpanId || s.kind === 'server' || s.kind === 'consumer') throw new Error('not a subsegment');
  d.name = s.kind === 'client' || s.kind === 'producer' ? (s.a['peer.service'] || s.a['server.address'] || s.a['messaging.system'] || s.name) : s.name;
  if (s.kind === 'producer') { d.name = 'SQS'; d.namespace = 'aws'; d.aws = { operation: 'SendMessage', queue_url: 'https://sqs.us-east-1.amazonaws.com/000000000000/' + (s.a['messaging.destination.name'] || 'orders') }; }
  else if (s.kind === 'client') { d.namespace = 'remote'; if (s.a['db.system']) { d.sql = { database_type: s.a['db.system'], sanitized_query: s.name }; d.name = s.a['server.address'] || s.a['db.system']; } }
  const ch = kids(s.spanId).filter((k) => !isSeg(k));
  if (ch.length) d.subsegments = ch.map(sub);
  return d;
}
const docs = [];
for (const s of spans.filter(isSeg)) {
  const d = body(s);
  d.trace_id = xid;
  if (s.parentSpanId) d.parent_id = s.parentSpanId;
  d.origin = 'AWS::ECS::Container';
  const ch = kids(s.spanId).filter((k) => !isSeg(k));
  if (ch.length) d.subsegments = ch.map(sub);
  docs.push(d);
}
// the inferred SQS segment X-Ray adds below a SendMessage subsegment
const prod = spans.find((s) => s.kind === 'producer');
if (prod) docs.push({ id: 'f0f0f0f0f0f0f0f0', name: 'SQS', trace_id: xid, parent_id: prod.spanId, inferred: true, origin: 'AWS::SQS::Queue', start_time: sec(prod.startTimeUnixNano), end_time: sec(prod.endTimeUnixNano), aws: { operation: 'SendMessage' } });
const doc = {
  _comment: 'SYNTHETIC sample in AWS X-Ray BatchGetTraces response shape, derived from samples/otel-demo-checkout.otlp.json. Not real data.',
  Traces: [{ Id: xid, Duration: sec(spans.reduce((m, s) => (BigInt(s.endTimeUnixNano) > m ? BigInt(s.endTimeUnixNano) : m), 0n)) - sec(spans.reduce((m, s) => (BigInt(s.startTimeUnixNano) < m ? BigInt(s.startTimeUnixNano) : m), BigInt(spans[0].startTimeUnixNano))), LimitExceeded: false,
    Segments: docs.map((d) => ({ Id: d.id, Document: JSON.stringify(d) })) }],
  UnprocessedTraceIds: [],
};
writeFileSync(new URL('./xray-checkout.json', import.meta.url), JSON.stringify(doc, null, 1) + '\n');
console.log(`wrote samples/xray-checkout.json (${docs.length} segment documents, ${spans.length} spans)`);
