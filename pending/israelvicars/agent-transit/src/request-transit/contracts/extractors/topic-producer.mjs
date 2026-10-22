// Message producers: <client>.emit('topic', payload satisfies T) or publish<T>('topic', ...).
// Gives the topic's shape so consumers without their own schema can fall back to it.
import { closeOf, lineOf } from '../text.mjs';
export default {
  name: 'topic-producer', kind: 'route',
  test: (src) => /\.(emit|publish|send)\s*(<[^>]*>)?\(\s*['"`]/.test(src),
  routes(src) {
    const out = [];
    for (const m of src.matchAll(/\.(?:emit|publish|send)\s*(?:<\s*([\w$]+)\s*>)?\(\s*['"`]([\w.-]+)['"`]/g)) {
      const open = m.index + m[0].indexOf('('), args = src.slice(open, closeOf(src, open) + 1);
      const sat = args.match(/\bsatisfies\s+([\w$]+)/) || args.match(/\bas\s+([\w$]+)\s*\)/);
      const symbol = m[1] || (sat && sat[1]);
      if (!symbol) continue;
      out.push({ kind: 'topic', topic: m[2], role: 'producer', line: lineOf(src, m.index), request: { symbol, via: m[1] ? 'publish<T>' : 'satisfies' }, response: null, framework: 'producer' });
    }
    return out;
  },
};
