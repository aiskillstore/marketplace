// contracts/indexer.mjs: build the contract index for the services in transit.config.json.
// Runs only when asked (scripts/transit.mjs index); nothing else in Transit calls it.
//   per file:  extractors -> {symbols, imports, reexports, routes}, cached by content hash
//   per entry: request/response symbols resolved through local declarations, relative imports and
//              workspace packages (config.packages globs, package.json name -> main), then inlined
//   output:    deterministic JSON (sorted, no timestamps) in .transit-cache/contracts/, never committed
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve, relative, extname, sep } from 'node:path';
import { execFileSync } from 'node:child_process';
import { EXTRACTORS, EXTRACTOR_VERSION } from './extractors/index.mjs';
import { blankComments } from './text.mjs';

const SRC_EXT = ['.ts', '.tsx', '.mts', '.js', '.mjs', '.jsx', '.proto'];
const SKIP_DIR = /^(node_modules|dist|build|\.git|coverage|\.next|\.transit-cache)$/;
const sha = (s) => createHash('sha256').update(s).digest('hex');
const posix = (p) => p.split(sep).join('/');

export function loadConfig(file) {
  const cfg = JSON.parse(readFileSync(file, 'utf8'));
  const base = dirname(resolve(file));
  return {
    file: resolve(file), base,
    services: cfg.services || {}, packages: cfg.packages || [], infra: cfg.infra || [],
    prefixes: cfg.prefixes || [], protoPaths: (cfg.protoPaths || []).map((p) => resolve(base, p)), rpcPackagePrefix: cfg.rpcPackagePrefix,
  };
}
function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir).sort()) {
    const p = join(dir, name), st = statSync(p);
    if (st.isDirectory()) { if (!SKIP_DIR.test(name)) walk(p, out); }
    else out.push(p);
  }
  return out;
}
function expandGlob(base, g) {
  if (!g.endsWith('/*')) return [resolve(base, g)];
  const d = resolve(base, g.slice(0, -2));
  return existsSync(d) ? readdirSync(d).sort().map((n) => join(d, n)).filter((p) => statSync(p).isDirectory()) : [];
}
function parseImports(src) {
  const imports = {}, reexports = [];
  for (const m of src.matchAll(/import\s+(?:type\s+)?(?:([\w$]+)\s*,?\s*)?(?:\{([^}]*)\})?\s*from\s*['"]([^'"]+)['"]/g)) {
    if (m[1]) imports[m[1]] = { spec: m[3], name: 'default' };
    for (const part of (m[2] || '').split(',').map((x) => x.trim()).filter(Boolean)) {
      const [orig, local] = part.replace(/^type\s+/, '').split(/\s+as\s+/).map((x) => x.trim());
      imports[local || orig] = { spec: m[3], name: orig };
    }
  }
  for (const m of src.matchAll(/export\s+\*\s+from\s*['"]([^'"]+)['"]/g)) reexports.push({ spec: m[1], all: true });
  for (const m of src.matchAll(/export\s+(?:type\s+)?\{([^}]*)\}\s*from\s*['"]([^'"]+)['"]/g))
    for (const part of m[1].split(',').map((x) => x.trim()).filter(Boolean)) {
      const [orig, as] = part.replace(/^type\s+/, '').split(/\s+as\s+/).map((x) => x.trim());
      reexports.push({ spec: m[2], name: orig, as: as || orig });
    }
  return { imports, reexports };
}

export function buildIndex(configFile, { cacheDir = '.transit-cache/contracts', log = () => {} } = {}) {
  const cfg = loadConfig(configFile);
  mkdirSync(join(cacheDir, 'files'), { recursive: true });
  const pkgs = new Map();
  for (const g of cfg.packages) for (const d of expandGlob(cfg.base, g)) {
    const pj = join(d, 'package.json'); if (!existsSync(pj)) continue;
    const j = JSON.parse(readFileSync(pj, 'utf8'));
    pkgs.set(j.name, resolve(d, j.types || j.main || 'src/index.ts'));
  }
  const files = new Map();   // abs path -> parsed
  let hits = 0, misses = 0;
  function parseFile(abs) {
    if (files.has(abs)) return files.get(abs);
    const src = readFileSync(abs, 'utf8');
    const rel = posix(relative(cfg.base, abs));
    const key = sha(EXTRACTOR_VERSION + '\0' + rel + '\0' + src);
    const cf = join(cacheDir, 'files', key + '.json');
    let parsed;
    if (existsSync(cf)) { parsed = JSON.parse(readFileSync(cf, 'utf8')); hits++; }
    else {
      const text = extname(abs) === '.json' ? src : blankComments(src);
      const proto = extname(abs) === '.proto';
      parsed = { rel, hash: key, symbols: {}, routes: [], ...(extname(abs) === '.json' || proto ? { imports: {}, reexports: [] } : parseImports(text)) };
      for (const ex of EXTRACTORS) {
        if (!ex.test(text, abs)) continue;
        if (proto !== (ex.name === 'protobuf')) continue;   // .proto files belong to the protobuf extractor only
        if (proto && ex.imports) parsed.reexports = ex.imports(text).map((spec) => ({ spec, all: true, proto: true }));
        if (ex.symbols && extname(abs) !== '.json') for (const s of ex.symbols(text)) if (!parsed.symbols[s.name] || rank(s.kind) > rank(parsed.symbols[s.name].kind)) parsed.symbols[s.name] = { ...s, extractor: ex.name };
        if (ex.routes) for (const r of ex.routes(text, abs)) parsed.routes.push({ ...r, extractor: ex.name });
      }
      writeFileSync(cf, JSON.stringify(parsed));
      misses++;
    }
    files.set(abs, parsed);
    return parsed;
  }
  function resolveModule(fromAbs, spec) {
    let base;
    if (extname(fromAbs) === '.proto') {   // proto imports: relative to the file, then each protoPath
      return [dirname(fromAbs), ...cfg.protoPaths, cfg.base].map((d) => resolve(d, spec)).find((c) => existsSync(c)) || null;
    }
    if (spec.startsWith('.')) base = resolve(dirname(fromAbs), spec);
    else {
      const name = spec.startsWith('@') ? spec.split('/').slice(0, 2).join('/') : spec.split('/')[0];
      if (!pkgs.has(name)) return null;
      const sub = spec.slice(name.length);
      base = sub ? resolve(dirname(pkgs.get(name)), '.' + sub) : pkgs.get(name);
    }
    const cands = [base, ...SRC_EXT.map((e) => base.replace(/\.(js|mjs)$/, '') + e), ...SRC_EXT.map((e) => join(base, 'index' + e))];
    return cands.find((c) => existsSync(c) && statSync(c).isFile()) || null;
  }
  // find a named symbol as seen from a file: local, imported, or re-exported (cycles guarded)
  function lookup(abs, name, seen = new Set()) {
    const k = abs + '#' + name; if (seen.has(k)) return null; seen.add(k);
    const f = parseFile(abs);
    if (f.symbols[name]) return { ...f.symbols[name], file: f.rel, abs };
    if (name.includes('.')) {   // protobuf: shop.Money, Outer.Inner -> try shorter suffixes
      const parts = name.split('.');
      for (let i = 1; i < parts.length; i++) { const short = parts.slice(i).join('.'); if (f.symbols[short]) return { ...f.symbols[short], file: f.rel, abs }; }
    }
    const imp = f.imports[name];
    if (imp) { const m = resolveModule(abs, imp.spec); if (m) return lookup(m, imp.name, seen); return { unresolved: `${name} from '${imp.spec}' (module not found)` }; }
    for (const r of f.reexports) {
      if (!r.all && r.as !== name) continue;
      const m = resolveModule(abs, r.spec); if (!m) continue;
      const hit = lookup(m, r.all ? name : r.name, seen); if (hit && !hit.unresolved) return hit;
    }
    return null;
  }
  // inline every ref so the panel needs no symbol table; keep the ref name and its source
  function inline(node, abs, depth, notes, kinds) {
    if (!node) return node;
    if (node.t === 'ref') {
      if (depth > 6) return { t: 'ref', name: node.name };
      const hit = lookup(abs, node.name);
      if (!hit || hit.unresolved) { notes.push(`unresolved type ${node.name}${hit ? ': ' + hit.unresolved : ''}`); return { t: 'unknown', ref: node.name, unresolved: true }; }
      const sym = hit.kind === 'alias' ? lookup(hit.abs, hit.target) : hit;
      if (!sym || sym.unresolved) { notes.push(`unresolved ${node.name}`); return { t: 'unknown', ref: node.name, unresolved: true }; }
      kinds.add(sym.kind);
      const out = { ...inline(sym.node, sym.abs, depth + 1, notes, kinds), ref: node.name, from: `${sym.file}:${sym.line}` };
      for (const k of ['optional', 'nullable', 'c']) if (node[k]) out[k] = node[k];
      return out;
    }
    const n = { ...node };
    if (n.props) n.props = n.props.map((p) => ({ ...p, node: inline(p.node, abs, depth + 1, notes, kinds) }));
    if (n.items) n.items = inline(n.items, abs, depth + 1, notes, kinds);
    if (n.of) n.of = n.of.map((x) => inline(x, abs, depth + 1, notes, kinds));
    if (n.extends) {
      for (const e of n.extends) { const b = inline({ t: 'ref', name: e }, abs, depth + 1, notes, kinds); if (b.props) n.props = [...b.props, ...n.props]; }
      delete n.extends;
    }
    return n;
  }
  function side(ref, abs, framework) {
    if (!ref) return null;
    if (ref.void) return { schema: { t: 'void' }, kind: 'none', confidence: 'high', via: ref.via || 'declared', notes: [] };
    if (ref.inline) return { schema: ref.inline, name: ref.name, kind: 'openapi', confidence: 'high', via: 'openapi', notes: [] };
    const notes = [], kinds = new Set();
    const hit = lookup(abs, ref.symbol);
    if (!hit || hit.unresolved) return { schema: { t: 'unknown', ref: ref.symbol, unresolved: true }, name: ref.symbol, kind: 'unresolved', confidence: 'low', via: ref.via, notes: [hit ? hit.unresolved : `could not find ${ref.symbol}`] };
    const sym = hit.kind === 'alias' ? lookup(hit.abs, hit.target) : hit;
    if (!sym || sym.unresolved) return { schema: { t: 'unknown', ref: ref.symbol, unresolved: true }, name: ref.symbol, kind: 'unresolved', confidence: 'low', via: ref.via, notes: [`could not follow ${ref.symbol} -> ${hit.target}`] };
    let schema = inline(sym.node, sym.abs, 0, notes, kinds);
    if (ref.array) schema = { t: 'array', items: schema };
    const validator = ['zod', 'joi', 'class-validator', 'protobuf'].includes(sym.kind);
    const confidence = notes.length ? 'low' : validator && !ref.typeOnly ? 'high' : 'medium';
    return { schema, name: ref.symbol, kind: sym.kind, source: `${sym.file}:${sym.line}`, crossPackage: posix(relative(cfg.base, sym.abs)).split('/')[0] !== posix(relative(cfg.base, abs)).split('/')[0] || undefined, confidence, via: ref.via, notes };
  }

  const entries = [], services = {};
  for (const [svc, sc] of Object.entries(cfg.services).sort(([a], [b]) => (a < b ? -1 : 1))) {
    const repo = resolve(cfg.base, sc.repo || '.');
    const list = sc.openapi ? [resolve(repo, sc.openapi)] : [];
    for (const f of walk(repo)) if (SRC_EXT.includes(extname(f)) && !list.includes(f)) list.push(f);
    const skipped = walk(repo).filter((f) => !SRC_EXT.includes(extname(f)) && !list.includes(f)).map((f) => posix(relative(cfg.base, f)));
    let n = 0;
    for (const abs of list) {
      const f = parseFile(abs);
      for (const r of f.routes) {
        const request = side(r.request, abs, r.framework), response = side(r.response, abs, r.framework);
        const conf = [request, response].filter(Boolean).map((s) => s.confidence);
        const e = {
          service: svc, kind: r.kind, method: r.method, path: r.path, rpc: r.rpc, topic: r.topic, role: r.role,
          source: `${f.rel}:${r.line}`, extractor: [r.extractor, request && request.kind, response && response.kind !== request?.kind ? response?.kind : null].filter((x) => x && x !== 'none' && x !== 'unresolved').filter((x, i, a) => a.indexOf(x) === i).join('+'),
          confidence: conf.includes('low') ? 'low' : conf.includes('medium') || !request || !response ? 'medium' : 'high',
          request, response,
        };
        if (!request) e.gaps = [...(e.gaps || []), 'no request schema found'];
        if (!response && r.role !== 'consumer' && r.role !== 'producer') e.gaps = [...(e.gaps || []), 'no response type found'];
        entries.push(JSON.parse(JSON.stringify(e)));   // drops undefined keys
        n++;
      }
    }
    services[svc] = { repo: posix(relative(cfg.base, repo)), files: list.length, entries: n, notRead: skipped.length ? skipped : undefined };
  }
  const keyOf = (e) => [e.service, e.kind, e.rpc || e.topic || '', e.role || '', e.method || '', e.path || '', e.source].join('|');
  entries.sort((a, b) => (keyOf(a) < keyOf(b) ? -1 : keyOf(a) > keyOf(b) ? 1 : 0));
  entries.forEach((e, i) => { e.id = `c${String(i + 1).padStart(3, '0')}`; });
  let commit = null;
  try { commit = execFileSync('git', ['-C', cfg.base, 'rev-parse', 'HEAD'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); } catch {}
  const fileHashes = [...files.values()].map((f) => f.rel + ':' + f.hash.slice(0, 16)).sort();
  const index = {
    version: EXTRACTOR_VERSION,
    key: sha(EXTRACTOR_VERSION + JSON.stringify(cfg.services) + fileHashes.join('\n')).slice(0, 16),
    commit,
    config: { file: posix(relative(process.cwd(), cfg.file)), protoPaths: cfg.protoPaths.map((p) => posix(relative(cfg.base, p))), infra: cfg.infra, prefixes: cfg.prefixes, rpcPackagePrefix: cfg.rpcPackagePrefix },
    services: JSON.parse(JSON.stringify(services)),
    files: fileHashes,
    entries,
  };
  const text = stable(index);
  const out = join(cacheDir, `index-${index.key}.json`);
  writeFileSync(out, text);
  writeFileSync(join(cacheDir, 'index.json'), text);
  log(`indexed ${entries.length} contract entries from ${files.size} files (${hits} cached, ${misses} parsed) -> ${out}`);
  return { index, out, latest: join(cacheDir, 'index.json'), hits, misses };
}
const rank = (k) => ({ protobuf: 3, 'class-validator': 3, zod: 3, joi: 3, alias: 2, 'ts-types': 1 }[k] || 0);
// JSON with sorted object keys (arrays keep their order) so the same inputs give the same bytes
export function stable(v) {
  const norm = (x) => Array.isArray(x) ? x.map(norm) : x && typeof x === 'object' ? Object.fromEntries(Object.keys(x).sort().map((k) => [k, norm(x[k])])) : x;
  return JSON.stringify(norm(v), null, 1) + '\n';
}
