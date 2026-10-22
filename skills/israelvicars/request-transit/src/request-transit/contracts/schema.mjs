// contracts/schema.mjs: the small schema tree every extractor emits, plus a TypeScript type parser.
//   {t:'object', props:[{name, optional, node}]} | {t:'array', items} | {t:'enum', values} | {t:'union', of}
//   {t:'string'|'number'|'integer'|'boolean'|'null'|'void'|'unknown'} | {t:'ref', name}
//   any node may carry c: ['email', 'min(1)', ...] (validator constraints)
import { splitTop, closeOf, unquote } from './text.mjs';
const PRIM = { string: 'string', number: 'number', boolean: 'boolean', bigint: 'integer', null: 'null', undefined: 'void', void: 'void', any: 'unknown', unknown: 'unknown', object: 'unknown', Date: 'string' };

export function parseTsType(src) {
  let s = String(src || '').trim();
  if (!s) return { t: 'unknown' };
  const parts = splitTop(s, '|');
  if (parts.length > 1) {
    const lits = parts.filter((p) => /^['"`].*['"`]$/.test(p) || /^-?\d+(\.\d+)?$/.test(p));
    const rest = parts.filter((p) => !lits.includes(p) && p !== 'null' && p !== 'undefined');
    if (!rest.length && lits.length) return { t: 'enum', values: lits.map((v) => (/^['"`]/.test(v) ? unquote(v) : Number(v))) };
    const of = rest.map(parseTsType);
    const node = of.length === 1 ? of[0] : { t: 'union', of };
    if (parts.length !== rest.length + lits.length) node.nullable = true;
    return node;
  }
  if (s.endsWith('[]')) return { t: 'array', items: parseTsType(s.slice(0, -2)) };
  if (s.startsWith('(') && closeOf(s, 0) === s.length - 1) return parseTsType(s.slice(1, -1));
  if (s.startsWith('{')) return { t: 'object', props: parseMembers(s.slice(1, closeOf(s, 0))) };
  if (/^['"`]/.test(s)) return { t: 'enum', values: [unquote(s)] };
  const g = s.match(/^([\w.]+)\s*<([\s\S]*)>$/);
  if (g) {
    const [, name, inner] = g;
    if (name === 'Array' || name === 'ReadonlyArray') return { t: 'array', items: parseTsType(inner) };
    if (name === 'Promise' || name === 'Observable' || name === 'Readonly' || name === 'Partial' && false) return parseTsType(inner);
    if (name === 'Record') return { t: 'object', props: [], additional: parseTsType(splitTop(inner, ',')[1]) };
    return { t: 'ref', name, generic: inner };
  }
  if (PRIM[s]) return { t: PRIM[s] };
  if (/^[A-Za-z_$][\w$.]*$/.test(s)) return { t: 'ref', name: s };
  return { t: 'unknown', text: s.slice(0, 60) };
}
// "a: string; b?: number" (also newline or comma separated) -> props
export function parseMembers(body) {
  const props = [];
  for (const m of splitTop(body, ';,\n')) {
    const mm = m.match(/^(?:readonly\s+)?(['"]?[\w$-]+['"]?)\s*(\?|!)?\s*:\s*([\s\S]+)$/);
    if (!mm || /^\w+\s*\(/.test(m)) continue;
    props.push({ name: unquote(mm[1]), optional: mm[2] === '?', node: parseTsType(mm[3]) });
  }
  return props;
}
// field-by-field text used in the panel and in tests: { a: string; b?: number[] }
export function show(n, depth = 0) {
  if (!n) return '—';
  const c = n.c && n.c.length ? ` /* ${n.c.join(', ')} */` : '';
  switch (n.t) {
    case 'object': return n.props.length ? `{ ${n.props.map((p) => `${p.name}${p.optional ? '?' : ''}: ${show(p.node, depth + 1)}`).join('; ')} }` : '{}';
    case 'array': return `${show(n.items, depth + 1)}[]`;
    case 'enum': return n.values.map((v) => JSON.stringify(v)).join(' | ');
    case 'union': return n.of.map((x) => show(x, depth + 1)).join(' | ');
    case 'ref': return n.name + c;
    default: return n.t + c;
  }
}
