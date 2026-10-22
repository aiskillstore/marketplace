// Protocol Buffers (.proto): services/rpcs become rpc entries ("Service/Method"), messages and enums become
// shapes. Handles nested messages (registered as Outer.Inner and Inner), repeated, optional/required,
// map<K,V>, oneof (fields optional), enums, and imports (followed by the indexer: relative to the file,
// then config.protoPaths). A .proto is the wire contract, so its shapes are high confidence.
import { closeOf, lineOf } from '../text.mjs';
const SCALAR = {
  string: 'string', bytes: 'string', bool: 'boolean', double: 'number', float: 'number',
  int32: 'integer', int64: 'integer', uint32: 'integer', uint64: 'integer', sint32: 'integer', sint64: 'integer',
  fixed32: 'integer', fixed64: 'integer', sfixed32: 'integer', sfixed64: 'integer',
};
const WKT = { 'google.protobuf.Timestamp': ['string', 'datetime'], 'google.protobuf.Duration': ['string', 'duration'], 'google.protobuf.Empty': ['void'], 'google.protobuf.Struct': ['unknown'], 'google.protobuf.Any': ['unknown'] };
export function protoType(t) {
  t = t.trim().replace(/^\./, '');
  if (SCALAR[t]) return t === 'bytes' ? { t: 'string', c: ['bytes'] } : { t: SCALAR[t] };
  if (WKT[t]) { const [ty, c] = WKT[t]; return c ? { t: ty, c: [c] } : { t: ty }; }
  const m = t.match(/^map\s*<\s*([\w.]+)\s*,\s*([\w.]+)\s*>$/);
  if (m) return { t: 'object', props: [], additional: protoType(m[2]) };
  return { t: 'ref', name: t };
}
// body of a message -> props; nested messages/enums pushed to out with qualified names
function message(body, prefix, base, src, out) {
  const props = [];
  let i = 0;
  while (i < body.length) {
    const rest = body.slice(i);
    const nest = rest.match(/^\s*(message|enum|oneof)\s+([\w]+)\s*\{/);
    if (nest) {
      const open = i + nest[0].length - 1, close = closeOf(body, open), inner = body.slice(open + 1, close);
      if (nest[1] === 'message') declare('message', nest[2], inner, prefix, base + open, src, out);
      else if (nest[1] === 'enum') declare('enum', nest[2], inner, prefix, base + open, src, out);
      else props.push(...message(inner, prefix, base + open + 1, src, out).map((p) => ({ ...p, optional: true })));   // oneof members
      i = close + 1; continue;
    }
    const semi = body.indexOf(';', i); if (semi < 0) break;
    const stmt = body.slice(i, semi).trim(); i = semi + 1;
    const f = stmt.match(/^(repeated\s+|optional\s+|required\s+)?(map\s*<[^>]+>|[\w.]+)\s+(\w+)\s*=\s*\d+/);
    if (!f || /^(option|reserved|extensions)\b/.test(stmt)) continue;
    let node = protoType(f[2]);
    if (f[1] && f[1].trim() === 'repeated') node = { t: 'array', items: node };
    props.push({ name: f[3], optional: !!f[1] && f[1].trim() === 'optional', node });
  }
  return props;
}
function declare(kind, name, inner, prefix, at, src, out) {
  const q = prefix ? `${prefix}.${name}` : name;
  const node = kind === 'enum'
    ? { t: 'enum', values: [...inner.matchAll(/(\w+)\s*=\s*-?\d+/g)].map((m) => m[1]) }
    : { t: 'object', props: message(inner, q, at + 1, src, out) };
  const sym = { name: q, kind: 'protobuf', line: lineOf(src, at), node };
  out.push(sym);
  if (prefix) out.push({ ...sym, name });   // also reachable by its short name
}
export default {
  name: 'protobuf', kind: 'schema',
  test: (src, file) => /\.proto$/.test(file || ''),
  symbols(src) {
    const out = [];
    const re = /^\s*(message|enum)\s+(\w+)\s*\{/gm;
    let m;
    while ((m = re.exec(src))) {
      const open = m.index + m[0].length - 1, close = closeOf(src, open);
      declare(m[1], m[2], src.slice(open + 1, close), '', open, src, out);
      re.lastIndex = close + 1;
    }
    return out;
  },
  imports: (src) => [...src.matchAll(/^\s*import\s+(?:public\s+|weak\s+)?"([^"]+)"\s*;/gm)].map((m) => m[1]),
  routes(src) {
    const out = [];
    for (const s of src.matchAll(/\bservice\s+(\w+)\s*\{/g)) {
      const open = s.index + s[0].length - 1, body = src.slice(open + 1, closeOf(src, open));
      for (const r of body.matchAll(/\brpc\s+(\w+)\s*\(\s*(stream\s+)?([\w.]+)\s*\)\s*returns\s*\(\s*(stream\s+)?([\w.]+)\s*\)/g)) {
        const sym = (t, stream) => protoType(t).t === 'ref' ? { symbol: t.replace(/^.*\.(?=[A-Z]\w*$)/, ''), qualified: t, array: !!stream, via: stream ? 'stream' : 'rpc' } : t === 'google.protobuf.Empty' ? { void: true, via: 'rpc' } : null;
        out.push({ kind: 'rpc', rpc: `${s[1]}/${r[1]}`, line: lineOf(src, open + 1 + r.index), framework: 'grpc', request: sym(r[3], r[2]), response: sym(r[5], r[4]) });
      }
    }
    return out;
  },
};
