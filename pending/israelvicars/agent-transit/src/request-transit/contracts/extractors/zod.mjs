// Zod schemas: const X = z.object({...}) and type T = z.infer<typeof X>
import { chain, splitTop, exprEnd, lineOf, unquote } from '../text.mjs';
const C = { email: 'email', uuid: 'uuid', url: 'url', datetime: 'datetime', int: null, positive: 'positive', nonnegative: '>= 0' };
export function zodNode(expr) {
  const parts = chain(expr);
  let node, i;
  if (parts[0].name === 'z' && parts[1]) {
    const b = parts[1]; i = 2;
    switch (b.name) {
      case 'object': node = { t: 'object', props: objectProps(b.args.replace(/^\{|\}$/g, '')) }; break;
      case 'string': node = { t: 'string' }; break;
      case 'number': node = { t: 'number' }; break;
      case 'bigint': node = { t: 'integer' }; break;
      case 'boolean': node = { t: 'boolean' }; break;
      case 'date': node = { t: 'string', c: ['date'] }; break;
      case 'array': node = { t: 'array', items: zodNode(b.args) }; break;
      case 'enum': node = { t: 'enum', values: splitTop(b.args.replace(/^\[|\]$/g, ''), ',').map(unquote) }; break;
      case 'literal': node = { t: 'enum', values: [unquote(b.args)] }; break;
      case 'union': node = { t: 'union', of: splitTop(b.args.replace(/^\[|\]$/g, ''), ',').map(zodNode) }; break;
      case 'optional': node = { ...zodNode(b.args), optional: true }; break;
      case 'record': node = { t: 'object', props: [], additional: zodNode(splitTop(b.args, ',').pop()) }; break;
      default: node = { t: 'unknown' };
    }
  } else if (/^[A-Za-z_$][\w$]*$/.test(parts[0].name) && parts[0].args === undefined) { node = { t: 'ref', name: parts[0].name }; i = 1; }
  else return { t: 'unknown' };
  for (; i < parts.length; i++) {
    const { name, args } = parts[i];
    if (name === 'optional' || name === 'nullish' || name === 'default') node.optional = true;
    else if (name === 'nullable') node.nullable = true;
    else if (name === 'int') node.t = node.t === 'number' ? 'integer' : node.t;
    else if (name === 'array') node = { t: 'array', items: node };
    else if (name in C) { if (C[name]) (node.c = node.c || []).push(C[name]); }
    else if (['min', 'max', 'length', 'regex', 'gt', 'lt', 'gte', 'lte'].includes(name)) (node.c = node.c || []).push(`${name}(${args})`);
  }
  return node;
}
function objectProps(body) {
  return splitTop(body, ',').map((kv) => {
    const k = kv.indexOf(':'); if (k < 0) return null;   // shorthand { Address } not supported
    const node = zodNode(kv.slice(k + 1));
    const optional = !!node.optional; delete node.optional;
    return { name: unquote(kv.slice(0, k).trim()), optional, node };
  }).filter(Boolean);
}
export default {
  name: 'zod', kind: 'validator',
  test: (src) => /\bz\.(object|string|number|array|enum)\(/.test(src),
  symbols(src) {
    const out = [];
    for (const m of src.matchAll(/\b(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(z\.[\s\S])/g)) {
      const start = m.index + m[0].length - m[2].length;
      out.push({ name: m[1], kind: 'zod', line: lineOf(src, m.index), node: zodNode(src.slice(start, exprEnd(src, start))) });
    }
    for (const m of src.matchAll(/\b(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=\s*z\.(?:infer|input|output)<\s*typeof\s+([\w$]+)\s*>/g))
      out.push({ name: m[1], kind: 'alias', line: lineOf(src, m.index), target: m[2] });
    return out;
  },
};
