// OpenAPI 3 import (JSON). Each operation -> one http entry; $ref resolved inside the document.
// Request = requestBody application/json schema; response = first 2xx application/json schema.
import { lineOf } from '../text.mjs';
function fromJsonSchema(s, doc, seen = new Set()) {
  if (!s) return { t: 'unknown' };
  if (s.$ref) {
    const name = s.$ref.split('/').pop();
    if (seen.has(name)) return { t: 'ref', name };
    const target = s.$ref.startsWith('#/') ? s.$ref.slice(2).split('/').reduce((o, k) => o && o[k], doc) : null;
    return target ? { ...fromJsonSchema(target, doc, new Set([...seen, name])), ref: name } : { t: 'ref', name, unresolved: true };
  }
  const c = [];
  for (const k of ['format', 'minimum', 'maximum', 'minLength', 'maxLength', 'pattern']) if (s[k] !== undefined) c.push(k === 'format' ? s.format : `${k}(${s[k]})`);
  let n;
  if (s.enum) n = { t: 'enum', values: s.enum };
  else if (s.oneOf || s.anyOf) n = { t: 'union', of: (s.oneOf || s.anyOf).map((x) => fromJsonSchema(x, doc, seen)) };
  else if (s.type === 'object' || s.properties) {
    const req = new Set(s.required || []);
    n = { t: 'object', props: Object.keys(s.properties || {}).map((k) => ({ name: k, optional: !req.has(k), node: fromJsonSchema(s.properties[k], doc, seen) })) };
  } else if (s.type === 'array') n = { t: 'array', items: fromJsonSchema(s.items, doc, seen) };
  else n = { t: ['string', 'number', 'integer', 'boolean', 'null'].includes(s.type) ? s.type : 'unknown' };
  if (c.length) n.c = c;
  return n;
}
export default {
  name: 'openapi', kind: 'import',
  test: (src, file) => /\.json$/.test(file) && /"openapi"\s*:\s*"3/.test(src),
  routes(src) {
    const doc = JSON.parse(src), out = [];
    for (const [path, ops] of Object.entries(doc.paths || {})) {
      const at = src.indexOf(JSON.stringify(path));
      for (const [verb, op] of Object.entries(ops)) {
        if (!/^(get|post|put|patch|delete|head|options)$/.test(verb)) continue;
        const rb = op.requestBody && op.requestBody.content && op.requestBody.content['application/json'];
        const ok = Object.entries(op.responses || {}).find(([code]) => /^2/.test(code));
        const rs = ok && ok[1].content && ok[1].content['application/json'];
        out.push({
          kind: 'http', method: verb.toUpperCase(), path: path.replace(/\{(\w+)\}/g, ':$1'), line: lineOf(src, at), framework: 'openapi',
          request: rb ? { inline: fromJsonSchema(rb.schema, doc), source: 'openapi', name: rb.schema && rb.schema.$ref && rb.schema.$ref.split('/').pop() } : null,
          response: rs ? { inline: fromJsonSchema(rs.schema, doc), source: 'openapi', name: rs.schema && rs.schema.$ref && rs.schema.$ref.split('/').pop() } : ok ? { void: true } : null,
        });
      }
    }
    return out;
  },
};
