// TypeScript interfaces and type aliases: shapes without runtime checks (medium confidence as a request,
// usually the only source for a response).
import { closeOf, exprEnd, lineOf } from '../text.mjs';
import { parseMembers, parseTsType } from '../schema.mjs';
export default {
  name: 'ts-types', kind: 'type',
  test: (src) => /\b(interface|type)\s+\w+/.test(src),
  symbols(src) {
    const out = [];
    for (const m of src.matchAll(/\b(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)(?:<[^>{]*>)?(?:\s+extends\s+([\w$.,\s<>]+?))?\s*\{/g)) {
      const open = m.index + m[0].length - 1;
      const node = { t: 'object', props: parseMembers(src.slice(open + 1, closeOf(src, open))) };
      if (m[2]) node.extends = m[2].split(',').map((x) => x.trim());
      out.push({ name: m[1], kind: 'ts-types', line: lineOf(src, m.index), node });
    }
    for (const m of src.matchAll(/\b(?:export\s+)?type\s+([A-Za-z_$][\w$]*)(?:<[^>=]*>)?\s*=\s*/g)) {
      const start = m.index + m[0].length, text = src.slice(start, exprEnd(src, start));
      if (/^z\.(infer|input|output)</.test(text)) continue;   // zod alias, handled by the zod extractor
      out.push({ name: m[1], kind: 'ts-types', line: lineOf(src, m.index), node: parseTsType(text) });
    }
    return out;
  },
};
