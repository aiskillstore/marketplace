// Express routes: app|router.<verb>('/path', ...middleware, handler)
//   request: validate(X) / validateBody(X) / celebrate({ body: X }) middleware, or X.parse|safeParse|validate(req.body)
//            in the handler; else the 3rd generic of Request<P, Res, Body> (type only)
//   response: Response<T> on the handler's res parameter, or the 2nd generic of Request<P, Res, Body>
import { closeOf, splitTop, lineOf } from '../text.mjs';
const VERBS = 'get|post|put|patch|delete|head|options';
export default {
  name: 'express', kind: 'route',
  test: (src) => new RegExp(`\\.(${VERBS})\\(\\s*['"\`]/`).test(src),
  routes(src) {
    const out = [];
    for (const m of src.matchAll(new RegExp(`\\b([\\w$]+)\\.(${VERBS})\\(\\s*(['"\`])([^'"\`]+)\\3`, 'g'))) {
      if (!/^(app|router|server|api|routes?|\w*Router)$/.test(m[1])) continue;
      const open = m.index + m[0].indexOf('('), close = closeOf(src, open);
      const args = splitTop(src.slice(open + 1, close), ',').slice(1);
      const handler = args[args.length - 1] || '';
      let request = null, response = null;
      for (const mw of args.slice(0, -1)) {
        const v = mw.match(/^(?:validate|validateBody|validateRequest|zValidator)\(\s*(?:['"]json['"]\s*,\s*)?([\w$]+)/) || mw.match(/^celebrate\(\s*\{[^}]*?(?:body|\[Segments\.BODY\])\s*:\s*([\w$]+)/);
        if (v) request = { symbol: v[1], via: 'middleware' };
      }
      if (!request) { const p = handler.match(/([\w$]+)\.(?:parse|safeParse|parseAsync|validate|validateAsync)\(\s*req\.body/); if (p) request = { symbol: p[1], via: 'handler' }; }
      const params = handler.match(/^(?:async\s+)?(?:function\s*\w*)?\(([^)]*)\)/);
      if (params) {
        const res = params[1].match(/\b\w+\s*:\s*Response\s*<\s*([\w$]+)/); if (res) response = { symbol: res[1], via: 'Response<T>' };
        const rq = params[1].match(/\b\w+\s*:\s*Request\s*<([^>]*)>/);
        if (rq) { const g = splitTop(rq[1], ','); if (!response && g[1] && !/^(any|unknown|\{\})$/.test(g[1])) response = { symbol: g[1], via: 'Request<_, Res>' }; if (!request && g[2] && !/^(any|unknown|\{\})$/.test(g[2])) request = { symbol: g[2], via: 'Request<_, _, Body>', typeOnly: true }; }
      }
      out.push({ kind: 'http', method: m[2].toUpperCase(), path: m[4], line: lineOf(src, m.index), request, response, framework: 'express' });
    }
    return out;
  },
};
