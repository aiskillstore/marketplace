// contracts/match.mjs: attach index entries to the spans of one normalized trace.
//   server span with rpc.service/rpc.method -> rpc entry "Service/Method" (package prefix like oteldemo. dropped)
//   server span with http method + route/path -> http entry; path params normalized (:id, {id}, numbers,
//     uuids, long hex -> {}); a leading /api/vN and any configured prefix is optional on both sides
//   consumer span -> topic consumer entry of that service, else the topic's producer shape (medium confidence)
//   client/producer span to a config.infra name, or to an uninstrumented db/cache/broker -> infrastructure
// Result: { bySpan: { spanId: {state:'matched'|'fallback'|'infra'|'unmatched', key, entryId, reason} }, entries }
export function normPath(p, prefixes = []) {
  let s = String(p || '').split('?')[0].replace(/^[a-z]+:\/\/[^/]+/i, '').replace(/\/+$/, '') || '/';
  s = s.split('/').map((seg) => /^(:\w+|\{\w+\}|\d+|[0-9a-f]{8}-[0-9a-f-]{27,}|[0-9a-f]{16,})$/i.test(seg) ? '{}' : seg).join('/');
  const out = new Set([s]);
  for (const pre of ['/api/v\\d+', ...prefixes.map((x) => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\/$/, ''))]) {
    const m = s.match(new RegExp('^' + pre + '(?=/|$)'));
    if (m) out.add(s.slice(m[0].length) || '/');
  }
  return [...out];
}
const rpcKey = (svc, method, pkgPrefix) => `${String(svc).replace(pkgPrefix ? new RegExp('^' + pkgPrefix) : /^.*\./, '')}/${method}`;
export function spanKey(s, kids = []) {
  const a = s.attrs || {};
  if (a['rpc.service'] && a['rpc.method']) return { kind: 'rpc', rpc: rpcKey(a['rpc.service'], a['rpc.method']), label: `${a['rpc.service']}/${a['rpc.method']}` };
  if (s.kind === 'consumer' || (a['messaging.destination.name'] && s.kind !== 'producer' && s.kind !== 'client')) return { kind: 'topic', topic: a['messaging.destination.name'] || s.name.split(' ')[0], label: `topic ${a['messaging.destination.name'] || s.name}` };
  const nm = String(s.name).match(/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\S+)/);
  const method = a['http.request.method'] || a['http.method'] || (nm && nm[1]) || null;
  const path = a['http.route'] || a['url.path'] || (nm && nm[2]) || (a['url.full'] ? new URL(a['url.full']).pathname : null);
  if (path) return { kind: 'http', method, path, label: `${method || '*'} ${path}` };
  return { kind: 'unknown', label: s.name };
}
export function matchTrace(trace, index) {
  const infra = new Set(index.config.infra || []), prefixes = index.config.prefixes || [];
  const byId = new Map(trace.spans.map((s) => [s.spanId, s]));
  const kids = new Map(trace.spans.map((s) => [s.spanId, []]));
  for (const s of trace.spans) if (s.parentId && kids.has(s.parentId)) kids.get(s.parentId).push(s);
  const svcs = index.services || {};
  const bySpan = {};
  for (const s of trace.spans) {
    const cross = kids.get(s.spanId).filter((c) => c.service !== s.service);
    if (s.peer && (s.kind === 'producer' || (s.kind === 'client' && cross.length === 0))) {
      bySpan[s.spanId] = { state: 'infra', key: s.peer, reason: infra.has(s.peer) ? 'listed as infrastructure in the config' : 'uninstrumented dependency (database, cache or broker)' };
      continue;
    }
    if (!(s.kind === 'server' || s.kind === 'consumer')) continue;
    const p = s.parentId && byId.get(s.parentId);
    if (!p) continue;   // the root/ingress span is where the request boards, not a hop
    const k = spanKey(s);
    const mine = index.entries.filter((e) => e.service === s.service);
    let hit = null, state = 'matched';
    if (k.kind === 'rpc') hit = mine.find((e) => e.kind === 'rpc' && e.rpc === k.rpc);
    else if (k.kind === 'http') {
      const want = normPath(k.path, prefixes);
      hit = mine.find((e) => e.kind === 'http' && (!k.method || !e.method || e.method === '*' || e.method === k.method) && normPath(e.path, prefixes).some((x) => want.includes(x)));
    } else if (k.kind === 'topic') {
      hit = mine.find((e) => e.kind === 'topic' && e.topic === k.topic && e.role === 'consumer');
      if (!hit) { hit = index.entries.find((e) => e.kind === 'topic' && e.topic === k.topic && e.role === 'producer'); if (hit) state = 'fallback'; }
    }
    if (hit) bySpan[s.spanId] = { state, key: k.label, entryId: hit.id, ...(state === 'fallback' ? { reason: `no consumer schema in ${s.service}; using the shape ${hit.service} publishes (medium confidence)` } : {}) };
    else bySpan[s.spanId] = { state: 'unmatched', key: k.label, reason: !svcs[s.service] ? `service ${s.service} is not in the config` : mine.length ? `no entry for ${k.label} among ${mine.length} in ${s.service}` : `no contracts extracted from ${s.service}${svcs[s.service].notRead ? ` (not read: ${svcs[s.service].notRead.join(', ')})` : ''}` };
  }
  const used = new Set(Object.values(bySpan).map((m) => m.entryId).filter(Boolean));
  return { indexKey: index.key, bySpan, entries: index.entries.filter((e) => used.has(e.id)) };
}
