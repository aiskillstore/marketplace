// NestJS-style DTO classes. With class-validator decorators the shape is validated at runtime (kind
// class-validator, high confidence); a plain class is just a type (kind ts-types).
import { closeOf, splitTop, lineOf } from '../text.mjs';
import { parseTsType } from '../schema.mjs';
const CV = /^(Is\w+|Min|Max|Length|MinLength|MaxLength|Matches|ValidateNested|ArrayMinSize|ArrayMaxSize|Equals|Contains|IsOptional)$/;
const CONSTRAINT = { IsEmail: 'email', IsUUID: 'uuid', IsUrl: 'url', IsISO8601: 'datetime', IsPositive: 'positive' };
export function classMembers(body) {
  const props = []; let validated = false;
  const parts = [];
  for (const p of splitTop(body, ';\n')) {   // a decorator alone on its line belongs to the next member
    if (parts.length && /^(@[\w$]+\s*(\([^]*\))?\s*)+$/.test(parts[parts.length - 1]) ) parts[parts.length - 1] += ' ' + p; else parts.push(p);
  }
  for (let m of parts) {
    const decos = [];
    for (;;) {
      const d = m.match(/^@([\w$]+)\s*/); if (!d) break;
      let rest = m.slice(d[0].length), args = '';
      if (rest[0] === '(') { const j = closeOf(rest, 0); args = rest.slice(1, j); rest = rest.slice(j + 1); }
      decos.push({ name: d[1], args }); m = rest.trim();
    }
    const f = m.match(/^(?:public\s+|readonly\s+|private\s+|protected\s+)*([\w$]+)\s*(\?|!)?\s*:\s*([^=]+?)(?:=.*)?$/s);
    if (!f || /\(/.test(f[1])) continue;
    const node = parseTsType(f[3]);
    const c = [];
    for (const d of decos) {
      if (CV.test(d.name)) validated = true;
      if (CONSTRAINT[d.name]) c.push(CONSTRAINT[d.name]);
      if (['Min', 'Max', 'Length', 'MinLength', 'MaxLength'].includes(d.name)) c.push(`${d.name.toLowerCase()}(${d.args})`);
      if (d.name === 'IsInt' && node.t === 'number') node.t = 'integer';
    }
    if (c.length) node.c = c;
    props.push({ name: f[1], optional: f[2] === '?' || decos.some((d) => d.name === 'IsOptional'), node });
  }
  return { props, validated };
}
export default {
  name: 'class-validator', kind: 'validator',
  test: (src) => /\bclass\s+\w+/.test(src),
  symbols(src) {
    const out = [];
    for (const m of src.matchAll(/\b(?:export\s+)?class\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+[\w$.<>]+)?(?:\s+implements\s+[\w$.<>, ]+)?\s*\{/g)) {
      const open = m.index + m[0].length - 1, close = closeOf(src, open);
      const body = src.slice(open + 1, close);
      if (/@(Controller|Injectable|Module)\b/.test(src.slice(Math.max(0, m.index - 200), m.index))) continue;   // services, not DTOs
      const { props, validated } = classMembers(body);
      if (!props.length) continue;
      out.push({ name: m[1], kind: validated ? 'class-validator' : 'ts-types', line: lineOf(src, m.index), node: { t: 'object', props } });
    }
    return out;
  },
};
