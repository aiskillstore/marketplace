// NestJS controllers: @Controller('prefix') + @Get/@Post/... ('path'), @GrpcMethod('Service', 'Method'),
// @EventPattern('topic') / @MessagePattern('topic'). Request = @Body()/@Payload() parameter type, or the first
// typed parameter for gRPC/events, or X.parse(param) inside the method. Response = return type
// (Promise<T> / Observable<T> unwrapped).
import { closeOf, splitTop, lineOf } from '../text.mjs';
const HTTP = /^(Get|Post|Put|Patch|Delete|Head|Options|All)$/;
const PRIM = /^(string|number|boolean|any|unknown|object|void|undefined|null|Record<.*>)$/;
export default {
  name: 'nest', kind: 'route',
  test: (src) => /@(Controller|GrpcMethod|EventPattern|MessagePattern)\b/.test(src),
  routes(src) {
    const out = [];
    for (const cm of src.matchAll(/@Controller\(\s*(?:['"`]([^'"`]*)['"`])?[^)]*\)\s*(?:export\s+)?class\s+[\w$]+[^{]*\{/g)) {
      const prefix = cm[1] || '';
      const open = cm.index + cm[0].length - 1, close = closeOf(src, open);
      const body = src.slice(open + 1, close), base = open + 1;
      const re = /((?:@[\w$]+\s*\([^)]*\)\s*)+)(?:public\s+|private\s+|protected\s+)?(?:async\s+)?([\w$]+)\s*\(/g;
      for (const m of body.matchAll(re)) {
        const decos = [...m[1].matchAll(/@([\w$]+)\s*\(([^)]*)\)/g)].map((d) => ({ name: d[1], args: splitTop(d[2], ',').map((a) => a.replace(/^['"`]|['"`]$/g, '')) }));
        const pOpen = m.index + m[0].length - 1, pClose = closeOf(body, pOpen);
        const params = splitTop(body.slice(pOpen + 1, pClose), ',');
        const after = body.slice(pClose + 1, pClose + 200);
        const ret = (after.match(/^\s*:\s*([^{]+?)\s*\{/) || [])[1];
        const bOpen = pClose + 1 + after.indexOf('{'), mBody = body.slice(bOpen, closeOf(body, bOpen));
        let route = null;
        const h = decos.find((d) => HTTP.test(d.name)), g = decos.find((d) => d.name === 'GrpcMethod'), e = decos.find((d) => /^(EventPattern|MessagePattern)$/.test(d.name));
        if (h) route = { kind: 'http', method: h.name === 'All' ? '*' : h.name.toUpperCase(), path: '/' + [prefix, h.args[0] || ''].map((x) => x.replace(/^\/|\/$/g, '')).filter(Boolean).join('/') };
        else if (g) route = { kind: 'rpc', rpc: `${g.args[0]}/${g.args[1] || m[2][0].toUpperCase() + m[2].slice(1)}` };
        else if (e) route = { kind: 'topic', topic: e.args[0], role: 'consumer' };
        if (!route) continue;
        let request = null;
        const typed = params.map((p) => p.match(/^((?:@[\w$]+\([^)]*\)\s*)*)([\w$]+)\??\s*:\s*(.+)$/)).filter(Boolean);
        const pick = typed.find((t) => /@(Body|Payload)\(/.test(t[1])) || (route.kind !== 'http' ? typed.find((t) => !/@(Metadata|Ctx|Headers?|Req|Res|Param|Query)\(/.test(t[1])) : null);
        if (pick) {
          const type = pick[3].trim();
          const parsed = mBody.match(new RegExp(`([\\w$]+)\\.(?:parse|safeParse|validate)\\(\\s*${pick[2]}\\b`));
          if (parsed) request = { symbol: parsed[1], via: 'handler' };
          else if (!PRIM.test(type)) request = { symbol: type.replace(/\[\]$/, ''), array: type.endsWith('[]'), via: 'parameter type' };
        }
        let response = null;
        if (route.role !== 'consumer' && ret) {
          const r = ret.replace(/^(Promise|Observable)\s*<([\s\S]*)>$/, '$2').trim();
          response = r === 'void' ? { void: true, via: 'return type' } : PRIM.test(r) ? null : { symbol: r.replace(/\[\]$/, ''), array: r.endsWith('[]'), via: 'return type' };
        }
        out.push({ ...route, line: lineOf(src, base + m.index + m[1].length), request, response, framework: 'nest' });
      }
    }
    return out;
  },
};
