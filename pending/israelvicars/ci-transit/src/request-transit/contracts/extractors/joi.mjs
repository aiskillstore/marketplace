// Joi schemas: const X = Joi.object({...}); fields are optional unless .required()
import { chain, splitTop, exprEnd, lineOf, unquote } from '../text.mjs';
export function joiNode(expr) {
  const parts = chain(expr);
  let node, i, required = false;
  if (parts[0].name === 'Joi' && parts[1]) {
    const b = parts[1]; i = 2;
    switch (b.name) {
      case 'object': node = { t: 'object', props: props(b.args.replace(/^\{|\}$/g, '')) }; break;
      case 'string': node = { t: 'string' }; break;
      case 'number': node = { t: 'number' }; break;
      case 'boolean': case 'bool': node = { t: 'boolean' }; break;
      case 'date': node = { t: 'string', c: ['date'] }; break;
      case 'array': node = { t: 'array', items: { t: 'unknown' } }; break;
      case 'alternatives': node = { t: 'union', of: [] }; break;
      default: node = { t: 'unknown' };
    }
  } else if (/^[A-Za-z_$][\w$]*$/.test(parts[0].name) && parts[0].args === undefined) { node = { t: 'ref', name: parts[0].name }; i = 1; }
  else return { t: 'unknown' };
  for (; i < parts.length; i++) {
    const { name, args } = parts[i];
    if (name === 'required') required = true;
    else if (name === 'optional') required = false;
    else if (name === 'integer') node.t = 'integer';
    else if (name === 'items' && node.t === 'array') node.items = joiNode(args);
    else if (name === 'valid' || name === 'allow' && false) node = { t: 'enum', values: splitTop(args, ',').map(unquote) };
    else if (['email', 'uuid', 'guid', 'uri', 'isoDate'].includes(name)) (node.c = node.c || []).push(name);
    else if (['min', 'max', 'length', 'pattern'].includes(name)) (node.c = node.c || []).push(`${name}(${args})`);
  }
  node.required = required;
  return node;
}
function props(body) {
  return splitTop(body, ',').map((kv) => {
    const k = kv.indexOf(':'); if (k < 0) return null;
    const node = joiNode(kv.slice(k + 1)); const optional = !node.required; delete node.required;
    return { name: unquote(kv.slice(0, k).trim()), optional, node };
  }).filter(Boolean);
}
export default {
  name: 'joi', kind: 'validator',
  test: (src) => /\bJoi\.\w+\(/.test(src),
  symbols(src) {
    const out = [];
    for (const m of src.matchAll(/\b(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(Joi\.[\s\S])/g)) {
      const start = m.index + m[0].length - m[2].length;
      const node = joiNode(src.slice(start, exprEnd(src, start))); delete node.required;
      out.push({ name: m[1], kind: 'joi', line: lineOf(src, m.index), node });
    }
    return out;
  },
};
