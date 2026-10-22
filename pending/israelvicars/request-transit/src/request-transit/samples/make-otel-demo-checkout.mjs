// samples/make-otel-demo-checkout.mjs
// Writes samples/otel-demo-checkout.otlp.json: a SYNTHETIC, hand-built trace in OTLP JSON shape.
//
// Nothing here was exported from a running system. It mirrors the call graph of the public
// OpenTelemetry Demo ("Astronomy Shop") checkout flow, using the demo's real service names and
// span names, taken from its public source:
//   - src/checkout/main.go PlaceOrder: prepareOrderItemsAndShippingQuoteFromCart (GetCart,
//     per-item GetProduct + Convert, POST /get-quote, Convert), then Charge, POST /ship-order,
//     EmptyCart, POST /send_order_confirmation, then "orders publish" to Kafka
//   - src/frontend/pages/api/checkout.ts: after PlaceOrder, Promise.all(GetProduct) per item
//     (the parallel fan-out)
//   - test/tracetesting/checkout/place-order.yaml and frontend/06-checking-out-cart.yaml
//     (span names such as "oteldemo.PaymentService/Charge", "/ship-order", "orders publish")
//   - accounting and fraud-detection consume the "orders" topic
// Timings are invented but plausible. Two deliberate anomalies so the highlights show:
//   - SLOW: payment "charge" takes 413 ms (the demo can inject this kind of thing with flags)
//   - ERROR: email "POST /send_order_confirmation" returns 500 (checkout logs a warning and the
//     order still succeeds, which is what the real checkout code does on email failure)
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const T0 = 1791720000000000000n;            // 2026-10-11T12:00:00Z in ns; arbitrary fixed epoch
const traceId = '4bf92f3577b34da6a3ce929d0e0e4736';
let n = 0;
const sid = () => (0xa1b2c3d400000000n + BigInt(++n) * 0x1111n).toString(16).padStart(16, '0');
const KIND = { internal: 1, server: 2, client: 3, producer: 4, consumer: 5 };
const bySvc = new Map();
const attr = (o) => Object.entries(o).map(([key, v]) => ({ key,
  value: typeof v === 'number' ? (Number.isInteger(v) ? { intValue: String(v) } : { doubleValue: v }) : typeof v === 'boolean' ? { boolValue: v } : { stringValue: String(v) } }));

function span(service, name, kind, startMs, endMs, parent, attrs = {}, status) {
  const s = {
    traceId, spanId: sid(), parentSpanId: parent ? parent.spanId : '', name, kind: KIND[kind],
    startTimeUnixNano: String(T0 + BigInt(Math.round(startMs * 1e6))),
    endTimeUnixNano: String(T0 + BigInt(Math.round(endMs * 1e6))),
    attributes: attr(attrs), status: status || { code: 0 },
  };
  if (!bySvc.has(service)) bySvc.set(service, []);
  bySvc.get(service).push(s);
  return s;
}
const grpc = (svc, method) => ({ 'rpc.system': 'grpc', 'rpc.service': `oteldemo.${svc}`, 'rpc.method': method });
// A gRPC call: client span in the caller, server span in the callee (1 to 2 ms of network each way).
function rpc(caller, callee, svc, method, s, e, parent, extra = {}) {
  const c = span(caller, `oteldemo.${svc}/${method}`, 'client', s, e, parent, { ...grpc(svc, method), 'server.address': callee });
  const sv = span(callee, `oteldemo.${svc}/${method}`, 'server', s + 1.2, e - 1.1, c, { ...grpc(svc, method), 'rpc.grpc.status_code': 0, ...extra });
  return [c, sv];
}
function http(caller, callee, route, s, e, parent, status = 200, err) {
  const c = span(caller, 'HTTP POST', 'client', s, e, parent, { 'http.request.method': 'POST', 'url.full': `http://${callee}${route}`, 'http.response.status_code': status },
    status >= 500 ? { code: 2, message: `HTTP ${status}` } : undefined);
  const sv = span(callee, `POST ${route}`, 'server', s + 1.4, e - 1.2, c, { 'http.request.method': 'POST', 'http.route': route, 'http.response.status_code': status },
    status >= 500 ? { code: 2, message: err } : undefined);
  return [c, sv];
}

// ---- the request ----
const ingress = span('frontend-proxy', 'ingress', 'server', 0, 792, null, { 'http.request.method': 'POST', 'url.path': '/api/checkout', 'upstream_cluster': 'frontend' });
const fe = span('frontend', 'POST /api/checkout', 'server', 3, 788, ingress, { 'http.request.method': 'POST', 'http.route': '/api/checkout', 'http.response.status_code': 200 });
const [, co] = rpc('frontend', 'checkout', 'CheckoutService', 'PlaceOrder', 6, 711, fe, { 'app.user.id': '1997', 'app.user.currency': 'USD' });
const prep = span('checkout', 'prepareOrderItemsAndShippingQuoteFromCart', 'internal', 10, 196, co, { 'app.cart.items.count': 3 });
const [, cartGet] = rpc('checkout', 'cart', 'CartService', 'GetCart', 12, 38, prep);
span('cart', 'HGET', 'client', 17, 30, cartGet, { 'db.system': 'redis', 'peer.service': 'valkey-cart', 'server.address': 'valkey-cart' });
let t = 41;
for (const id of ['OLJCESPC7Z', '66VCHSJNUP', '9SIQT8TOJO']) {   // product ids from the demo catalog
  rpc('checkout', 'product-catalog', 'ProductCatalogService', 'GetProduct', t, t + 17, prep, { 'app.product.id': id }); t += 19;
  rpc('checkout', 'currency', 'CurrencyService', 'Convert', t, t + 13, prep, { 'app.currency.conversion.from': 'USD', 'app.currency.conversion.to': 'USD' }); t += 15;
}
// t is now 143
const [, quoteHttp] = http('checkout', 'shipping', '/get-quote', 144, 180, prep);
const qc = span('shipping', 'POST', 'client', 148, 174, quoteHttp, { 'http.request.method': 'POST', 'url.full': 'http://quote:8090/getquote' });
const qs = span('quote', 'POST /getquote', 'server', 150, 172, qc, { 'http.route': '/getquote', 'app.quote.items.count': 3 });
span('quote', 'calculate-quote', 'internal', 153, 169, qs, { 'app.quote.cost.total': 19.45 });
rpc('checkout', 'currency', 'CurrencyService', 'Convert', 182, 194, prep);
const [, pay] = rpc('checkout', 'payment', 'PaymentService', 'Charge', 199, 622, co);
span('payment', 'charge', 'internal', 203, 616, pay, { 'app.payment.card_type': 'visa', 'app.payment.card_valid': true, 'app.payment.charged': true });
http('checkout', 'shipping', '/ship-order', 625, 651, co);
rpc('checkout', 'cart', 'CartService', 'EmptyCart', 653, 668, co);
http('checkout', 'email', '/send_order_confirmation', 670, 697, co, 500, 'Internal Server Error: failed to send order confirmation (SMTP timeout)');
const pub = span('checkout', 'orders publish', 'producer', 699, 707, co, { 'messaging.system': 'kafka', 'messaging.destination.name': 'orders', 'messaging.operation': 'publish', 'peer.service': 'kafka' });
span('accounting', 'orders receive', 'consumer', 716, 742, pub, { 'messaging.system': 'kafka', 'messaging.destination.name': 'orders', 'messaging.operation': 'receive' });
span('fraud-detection', 'orders consume', 'consumer', 720, 760, pub, { 'messaging.system': 'kafka', 'messaging.destination.name': 'orders', 'messaging.operation': 'process' });
// frontend fan-out after PlaceOrder returns: Promise.all(getProduct) for the 3 items, in parallel
for (const [i, id] of ['OLJCESPC7Z', '66VCHSJNUP', '9SIQT8TOJO'].entries())
  rpc('frontend', 'product-catalog', 'ProductCatalogService', 'GetProduct', 714 + i * 0.6, 714 + i * 0.6 + [52, 58, 47][i], fe, { 'app.product.id': id });

const doc = {
  // Not part of OTLP; ignored by OTLP tooling, read by normalize.mjs.
  _comment: 'SYNTHETIC trace, hand-built to match the public OpenTelemetry Demo (Astronomy Shop) checkout call graph and service names. Not exported from any running system.',
  resourceSpans: [...bySvc].map(([service, spans]) => ({
    resource: { attributes: attr({ 'service.name': service, 'service.namespace': 'opentelemetry-demo' }) },
    scopeSpans: [{ scope: { name: 'synthetic-sample' }, spans }],
  })),
};
const out = join(dirname(fileURLToPath(import.meta.url)), 'otel-demo-checkout.otlp.json');
writeFileSync(out, JSON.stringify(doc, null, 1));
console.log(`wrote ${out}: ${[...bySvc.values()].flat().length} spans across ${bySvc.size} services`);
