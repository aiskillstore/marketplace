/**
 * [INPUT]: 依赖 node:test、合成夹具与审计公开接口
 * [OUTPUT]: 提供 配置和候选回归测试
 * [POS]: 核心契约测试；不访问真实用户项目
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { auditProject, parseJsoncStrict, runCli, scanSource } from './audit.ts';

function fixture<T>(fn: (root: string, parent: string) => T): T {
  const parent = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'cfba-test-'));
  const root = path.join(parent, 'project');
  fs.mkdirSync(root);
  try { return fn(root, parent); }
  finally { fs.rmSync(parent, { recursive: true, force: true }); }
}

function write(root: string, relative: string, contents: string): void {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, contents);
}

function unknownCodes(report: ReturnType<typeof auditProject>['report']): string[] {
  return report.unknowns.map((item) => item.code);
}

test('JSONC comments preserve strings and duplicate keys or malformed commas are rejected', () => {
  const parsed = parseJsoncStrict(`{
    // line comment
    "url": "https://example.test/a//b",
    "description": "/* not a comment */",
    "nested": { "x": 1, },
  }`) as Record<string, unknown>;
  assert.equal(parsed.url, 'https://example.test/a//b');
  assert.equal(parsed.description, '/* not a comment */');
  assert.throws(() => parseJsoncStrict('{"x":1,"x":2}'));
  assert.throws(() => parseJsoncStrict('{"x":1,,}'));
  assert.throws(() => parseJsoncStrict('{,}'));
  assert.throws(() => parseJsoncStrict('[,]'));
  assert.throws(() => parseJsoncStrict('[ , ]'));
  assert.throws(() => parseJsoncStrict('{"x":1e999}'));
});

test('scanner reports narrow alarm, queue, and loop candidates but keeps trigger chains unknown', () => {
  const source = [
    'export class WorkerObject {',
    '  async alarm(opts = makeOptions()): Promise<void> {',
    '    await this.ctx.storage.setAlarm(1000);',
    '  }',
    '  async queue(batch: MessageBatch): Promise<void> {',
    '    batch.messages[0].retry();',
    '    await env.JOBS.send(batch.messages[0].body);',
    '  }',
    '}',
    'for (let i = 0; i < 3; i++) await env.JOBS.send(i);',
  ].join('\n');
  const result = scanSource(source, 'src/worker.ts');
  assert.equal(result.unsupported.length, 0);
  assert.deepEqual(result.findings.map((item) => item.matchesRuleId), [
    'CF-DO-ALARM-LOOP', 'CF-QUEUES-RETRY-FANOUT', 'CF-QUEUES-SELF-REENQUEUE-LOOP', 'CF-QUEUES-SELF-REENQUEUE-LOOP',
  ]);
  assert.ok(result.findings.every((item) => item.triggerChain === 'unknown'));
  assert.ok(result.findings.every((item) => item.line >= 1));
});

test('comments, quoted strings, regex literals, and JSX do not create confirmed candidates', () => {
  const ignored = [
    '// async alarm() { this.storage.setAlarm(1); }',
    '/* async queue(batch) { message.retry(); q.send(1); } */',
    'const text = "async alarm() { this.storage.setAlarm(1); }";',
    "const text2 = 'queue(batch) { message.retry(); q.send(1); }';",
  ].join('\n');
  assert.equal(scanSource(ignored, 'src/worker.js').findings.length, 0);
  const regex = scanSource('if (flag) /setAlarm() { queue(batch) { q.send(1); } }/.test(value);', 'src/worker.js');
  assert.equal(regex.findings.length, 0);
  assert.ok(regex.unsupported.includes('ambiguous-regex-or-division'));
  const jsx = scanSource('const View = <div>alarm() { storage.setAlarm(1); }</div>;', 'src/View.tsx');
  assert.equal(jsx.findings.length, 0);
  assert.ok(jsx.unsupported.includes('jsx-or-tsx'));
  const template = scanSource('const text = `prefix ${storage.setAlarm(1)}`;', 'src/template.js');
  assert.equal(template.findings.length, 0);
  assert.ok(template.unsupported.includes('template-interpolation-not-analyzed'));
});

test('nested parameter lists, return annotations, object queue handlers, and single-statement loops are covered', () => {
  const code = [
    'class DO { async alarm(arg = build(() => 1)): Promise<void> { this.ctx.storage.setAlarm(1); } }',
    'const handlers = { queue: async (batch: MessageBatch) => { batch.retry(); } };',
    'for (let i = 0; i < 10; i++) await env.Q.send(i);',
  ].join('\n');
  const result = scanSource(code, 'src/worker.ts');
  assert.deepEqual(result.unsupported, []);
  assert.deepEqual(result.findings.map((item) => item.matchesRuleId), ['CF-DO-ALARM-LOOP', 'CF-QUEUES-RETRY-FANOUT', 'CF-QUEUES-SELF-REENQUEUE-LOOP']);
});

test('wrangler workspace and environment inventory is separate, bounded, and redacts values', () => fixture((root) => {
  write(root, 'package.json', JSON.stringify({
    workspaces: ['apps/*'], scripts: { leakedScript: 'SHOULD_NOT_APPEAR' }, private: true,
  }));
  write(root, 'wrangler.jsonc', `{
    // config comment
    "main": "src/index.js",
    "kv_namespaces": [{"binding":"CACHE","id":"secret-resource-id"}],
    "vars": {"API_KEY":"DO_NOT_LEAK_THIS_VALUE"},
    "triggers": {"crons": ["0 * * * *", "30 2 * * *"]},
    "routes": ["private.example.test/*", "other.test/*"],
    "limits": {"cpu_ms": 30000},
    "env": {"preview": {"main":"src/preview.js", "d1_databases":[{"binding":"DB","database_id":"db-secret"}]}}
  }`);
  write(root, 'src/index.js', 'export default { fetch() { return new Response("ok"); } };');
  write(root, 'src/preview.js', 'export default { fetch() { return new Response("preview"); } };');
  write(root, 'apps/api/wrangler.json', JSON.stringify({ main: 'src/worker.ts', ai: { binding: 'AI' }, browser: { binding: 'BROWSER' }, containers: [{ class_name: 'JobContainer', image: 'secret-image-name' }], queues: { producers: [{ binding: 'JOBS', queue: 'private-queue-name' }], consumers: [{ queue: 'private-queue-name' }] } }));
  write(root, 'apps/api/src/worker.ts', 'export default { async fetch() { return new Response("ok"); } };');

  const { report } = auditProject(root, { writeReports: false });
  assert.equal(report.configs.length, 2);
  assert.deepEqual(report.workspaces.sort(), ['.', 'apps/api']);
  assert.equal(report.packageWorkspaces[0]?.patterns[0], 'apps/*');
  const base = report.configs.find((config) => config.path === 'wrangler.jsonc')!;
  const baseEnv = base.environments.find((env) => env.name === 'base')!;
  const preview = base.environments.find((env) => env.name === 'preview')!;
  assert.equal(baseEnv.main.status, 'exists');
  assert.equal(preview.main.path, 'src/preview.js');
  assert.deepEqual(preview.bindings.map((binding) => binding.type), ['d1_database']);
  assert.equal(baseEnv.varsCount, 1);
  assert.equal(baseEnv.triggers.cronCount, 2);
  assert.equal(baseEnv.routeCount, 2);
  assert.equal(baseEnv.limits.cpuMs, 30000);
  const apiBindings = report.configs.find((config) => config.path === 'apps/api/wrangler.json')!.environments[0]!.bindings;
  assert.deepEqual(apiBindings.map((binding) => binding.product), ['Workers AI', 'Browser Rendering', 'Cloudflare Containers', 'Cloudflare Queues', 'Cloudflare Queues']);
  assert.equal(report.findings.length, 0, 'binding declarations alone are not risk findings');
  const serialized = JSON.stringify(report);
  for (const marker of ['DO_NOT_LEAK_THIS_VALUE', 'secret-resource-id', 'db-secret', 'secret-image-name', 'private-queue-name', 'SHOULD_NOT_APPEAR', 'private.example.test']) assert.ok(!serialized.includes(marker));
}));

test('invalid, unsupported, and absent configs are explicit unknowns', () => fixture((root, parent) => {
  write(root, 'wrangler.json', '{"main":"x.js","main":"y.js"}');
  write(root, 'wrangler.toml', 'name = "sample"\nmain = "index.js"\n');
  const report = auditProject(root, { writeReports: false }).report;
  assert.ok(report.configs.some((config) => config.parserStatus === 'invalid-json-or-jsonc'));
  assert.ok(unknownCodes(report).includes('config-invalid-json-or-jsonc'));
  const bun = (globalThis as typeof globalThis & { Bun?: { TOML?: { parse?: unknown } } }).Bun;
  if (typeof bun?.TOML?.parse !== 'function') {
    assert.ok(report.configs.some((config) => config.parserStatus === 'unsupported-no-bun-toml-parser'));
    assert.ok(unknownCodes(report).includes('toml-coverage-unsupported'));
  }
  const empty = path.join(parent, 'empty'); fs.mkdirSync(empty);
  const noConfig = auditProject(empty, { writeReports: false }).report;
  assert.ok(unknownCodes(noConfig).includes('no-wrangler-config'));
}));

const bunTomlAvailable = typeof (globalThis as typeof globalThis & { Bun?: { TOML?: { parse?: unknown } } }).Bun?.TOML?.parse === 'function';

test('Bun TOML parser covers nested tables, arrays-of-tables, dotted keys, env, bindings, and rejects invalid TOML', { skip: !bunTomlAvailable }, () => fixture((root) => {
  write(root, 'wrangler.toml', `
name = "toml-worker"
main = "src/index.ts"
routes = ["private.example.test/*"]

[vars]
APP.MODE = "never-output-this"

[[kv_namespaces]]
binding = "CACHE"
id = "never-output-resource-id"

[[queues.producers]]
binding = "JOBS"
queue = "never-output-queue-name"

[[queues.consumers]]
queue = "never-output-queue-name"

[triggers]
crons = ["0 * * * *", "30 2 * * *"]

[limits]
cpu_ms = 30000

[env.preview]
main = "src/preview.ts"

[[env.preview.d1_databases]]
binding = "DB"
database_name = "never-output-db-name"
database_id = "never-output-db-id"
`);
  write(root, 'src/index.ts', 'export default {};');
  write(root, 'src/preview.ts', 'export default {};');
  const report = auditProject(root, { writeReports: false }).report;
  const config = report.configs.find((item) => item.path === 'wrangler.toml')!;
  assert.equal(config.parserStatus, 'supported-bun-toml');
  const base = config.environments.find((item) => item.name === 'base')!;
  const preview = config.environments.find((item) => item.name === 'preview')!;
  assert.equal(base.varsCount, 1);
  assert.deepEqual(base.bindings.map((binding) => binding.product), ['Workers KV', 'Cloudflare Queues', 'Cloudflare Queues']);
  assert.deepEqual(preview.bindings.map((binding) => binding.product), ['D1']);
  assert.equal(base.triggers.cronCount, 2);
  assert.equal(base.routeCount, 1);
  assert.equal(base.limits.cpuMs, 30000);
  const serialized = JSON.stringify(report);
  for (const secret of ['never-output-this', 'never-output-resource-id', 'never-output-queue-name', 'never-output-db-id', 'private.example.test']) assert.ok(!serialized.includes(secret));

  write(root, 'broken/wrangler.toml', 'name = [\n');
  const invalid = auditProject(root, { writeReports: false }).report.configs.find((item) => item.path === 'broken/wrangler.toml');
  assert.equal(invalid?.parserStatus, 'invalid-toml');
  assert.ok(unknownCodes(auditProject(root, { writeReports: false }).report).includes('config-invalid-toml'));
}));

test('wrong supported-product shapes become unknown and are not silently treated as absent', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'missing.js', kv_namespaces: { binding: 'CACHE' }, queues: { producers: 'not-an-array' }, unsafe: { bindings: [{ type: 'unknown' }] } }));
  const report = auditProject(root, { writeReports: false }).report;
  assert.ok(unknownCodes(report).includes('unclassified-binding'));
  assert.equal(report.configs[0]?.environments[0]?.main.status, 'missing');
  assert.equal(report.configs[0]?.environments[0]?.bindings.length, 0);
}));

test('secret-like files, generated directories, imports, and scripts are never executed or inventoried', () => fixture((root, parent) => {
  const marker = path.join(parent, 'executed.txt');
  write(root, 'package.json', JSON.stringify({ scripts: { preaudit: `touch ${marker}` } }));
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.ts' }));
  write(root, 'src/index.ts', `import './evil.js';\nexport default { fetch() { return new Response('ok'); } };`);
  write(root, 'src/evil.js', `import fs from 'node:fs'; fs.writeFileSync(${JSON.stringify(marker)}, 'executed');`);
  for (const file of ['.env', '.dev.vars', '.npmrc', 'private.pem', 'secrets.ts', 'credentials.ts']) write(root, file, 'NEVER_READ_VALUE');
  write(root, 'src/secrets.ts', 'NEVER_READ_VALUE');
  write(root, 'node_modules/pkg/index.js', 'NEVER_READ_VALUE');
  const report = auditProject(root, { writeReports: false }).report;
  assert.equal(fs.existsSync(marker), false);
  assert.ok(report.skipped.excludedPaths >= 5);
  assert.ok(!report.scannedSourceFiles.some((file) => /secret|credential/i.test(file)));
  assert.ok(!JSON.stringify(report).includes('NEVER_READ_VALUE'));
}));

test('symlinks are skipped, project and output symlink paths are rejected, and FIFOs are not read', { skip: process.platform === 'win32' }, () => fixture((root, parent) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.ts' }));
  write(root, 'src/index.ts', 'export default { fetch() {} };');
  const outside = path.join(parent, 'outside.ts'); fs.writeFileSync(outside, 'async alarm() { storage.setAlarm(1); }');
  fs.symlinkSync(outside, path.join(root, 'src', 'linked.ts'));
  const report = auditProject(root, { writeReports: false }).report;
  assert.equal(report.skipped.symlinks, 1);
  assert.ok(!report.scannedSourceFiles.includes('src/linked.ts'));

  const realParent = path.join(parent, 'real'); fs.mkdirSync(realParent);
  const aliasParent = path.join(parent, 'alias'); fs.symlinkSync(realParent, aliasParent, 'dir');
  const linkedRoot = path.join(aliasParent, 'project'); fs.mkdirSync(path.join(realParent, 'project'));
  assert.throws(() => auditProject(linkedRoot, { writeReports: false }), /project-path-through-symlink/);
  const outputAlias = path.join(parent, 'output-alias'); fs.symlinkSync(realParent, outputAlias, 'dir');
  assert.throws(() => auditProject(root, { outputDir: path.join(outputAlias, 'reports') }), /output-symlink-component/);
  assert.throws(() => auditProject(root, { outputDir: path.join(root, 'reports') }), /output-inside-project/);

  try {
    const fifo = path.join(root, 'src', 'not-a-file.ts');
    execFileSync('mkfifo', [fifo]);
    const fifoReport = auditProject(root, { writeReports: false }).report;
    assert.ok(!fifoReport.scannedSourceFiles.includes('src/not-a-file.ts'));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
  }
}));

test('file, byte, depth, global-entry, and finding caps produce explicit unknowns', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/main.js' }));
  write(root, 'src/main.js', 'export default {};');
  for (let i = 0; i < 25; i++) write(root, `src/file-${i}.js`, 'export const x = 1;');
  write(root, 'src/large.js', 'x'.repeat(300));
  const byFiles = auditProject(root, { writeReports: false, limits: { maxFiles: 8 } }).report;
  assert.ok(unknownCodes(byFiles).includes('scan-limit-max-files'));
  const byEntries = auditProject(root, { writeReports: false, limits: { maxEntries: 6 } }).report;
  assert.ok(unknownCodes(byEntries).includes('scan-limit-max-entries'));
  const byBytes = auditProject(root, { writeReports: false, limits: { maxFileBytes: 100 } }).report;
  assert.ok(unknownCodes(byBytes).includes('source-not-scanned'));
  const deepRoot = path.join(root, 'deep'); write(deepRoot, 'a/b/c/wrangler.json', JSON.stringify({ main: 'src/main.js' }));
  const deep = auditProject(deepRoot, { writeReports: false, limits: { maxDepth: 1 } }).report;
  assert.ok(unknownCodes(deep).includes('scan-limit-max-depth'));
  const manyFindings = Array.from({ length: 20 }, () => 'async alarm() {').join('\n') + '\n' + Array.from({ length: 20 }, () => 'this.ctx.storage.setAlarm(1);').join('\n') + '\n' + Array.from({ length: 20 }, () => '}').join('\n');
  const candidateCapped = scanSource(manyFindings, 'src/many.js', new Set(), 3);
  assert.equal(candidateCapped.findings.length, 3);
  assert.equal(candidateCapped.truncated, true);
}));

test('reports are written outside the project without overwriting prior results; CLI requires --project', () => fixture((root, parent) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/main.js', vars: { KEY: 'NEVER-PRINT' } }));
  write(root, 'src/main.js', 'export default {};');
  const outputDir = path.join(parent, 'audit-work');
  const options = { outputDir, now: new Date('2026-10-12T00:00:00.000Z') };
  const first = auditProject(root, options);
  const second = auditProject(root, options);
  assert.ok(first.outputDirectory && second.outputDirectory && first.outputDirectory !== second.outputDirectory);
  assert.ok(!first.outputDirectory.startsWith(root + path.sep));
  const json = fs.readFileSync(path.join(first.outputDirectory!, 'inventory.json'), 'utf8');
  const markdown = fs.readFileSync(path.join(first.outputDirectory!, 'inventory.md'), 'utf8');
  assert.ok(!json.includes('NEVER-PRINT'));
  assert.ok(!markdown.includes('NEVER-PRINT'));
  let stderr = '';
  const original = console.error;
  console.error = (message?: unknown) => { stderr += String(message); };
  try { assert.equal(runCli([]), 2); } finally { console.error = original; }
  assert.match(stderr, /explicit --project/);
  assert.ok(!fs.existsSync(path.join(root, 'cloudflare-billing-audit')));
}));

test('class-field arrow alarm and queue handlers produce candidates or explicit unknowns', () => {
  const code = [
    'class DO { alarm = async (opts = buildOptions()): Promise<void> => { this.ctx.storage.setAlarm(1); }; }',
    'class Consumer { queue = async (batch: MessageBatch): Promise<void> => { batch.messages[0].retry(); this.env.OUT.send(batch); }; }',
  ].join('\n');
  const result = scanSource(code, 'src/handlers.ts');
  assert.deepEqual(result.unsupported, []);
  assert.deepEqual(result.findings.map((item) => item.matchesRuleId), [
    'CF-DO-ALARM-LOOP', 'CF-QUEUES-RETRY-FANOUT', 'CF-QUEUES-SELF-REENQUEUE-LOOP',
  ]);
});

test('.env-prefixed files and directories are excluded consistently', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.ts' }));
  write(root, 'src/index.ts', 'export default {};');
  for (const file of ['.env-prod.ts', '.envrc.ts', '.envsecret.ts', '.ENV-LOCAL.js', '.envrc/worker.ts']) {
    write(root, file, 'SHOULD_NOT_BE_READ');
  }
  const report = auditProject(root, { writeReports: false }).report;
  assert.ok(report.readSourceFiles.includes('src/index.ts'));
  assert.ok(!report.readSourceFiles.some((item) => /(^|\/)\.env/i.test(item)));
  assert.ok(!JSON.stringify(report).includes('SHOULD_NOT_BE_READ'));
}));

test('recursive candidate cap keeps main in review scope or reports the omitted main explicitly', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'z.ts' }));
  for (let i = 0; i < 3; i++) write(root, `a/file-${i}.ts`, 'export const n = 1;');
  write(root, 'z.ts', 'async alarm() { this.ctx.storage.setAlarm(1); }');
  const report = auditProject(root, { writeReports: false, limits: { maxFiles: 4 } }).report;
  const main = report.configs[0]?.environments[0]?.main;
  assert.equal(main?.path, 'z.ts');
  assert.ok(report.readSourceFiles.includes('z.ts') || unknownCodes(report).some((code) => /main.*limit|scan-limit-max-files/.test(code)),
    'a configured entry point may not silently disappear at the recursive file cap');
  assert.ok(unknownCodes(report).includes('scan-limit-max-files'));
}));

test('recursive exact entry cap does not silently skip already-enumerated siblings', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'z.ts' }));
  for (let i = 0; i < 3; i++) write(root, `a/file-${i}.ts`, 'export const n = 1;');
  write(root, 'z.ts', 'export const main = true;');
  const report = auditProject(root, { writeReports: false, limits: { maxEntries: 6 } }).report;
  assert.ok(report.readSourceFiles.includes('z.ts'), 'entries enumerated before recursion must remain eligible for bounded processing');
}));

test('ancestor swap to an external symlink between check and open cannot create an outside finding', { skip: process.platform === 'win32' }, () => fixture((root, parent) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.js' }));
  write(root, 'src/index.js', 'export default {};');
  const outside = path.join(parent, 'outside');
  fs.mkdirSync(outside);
  fs.writeFileSync(path.join(outside, 'index.js'), 'async alarm() { this.ctx.storage.setAlarm(1); }');
  const originalOpen = fs.openSync;
  let swapped = false;
  const patchedOpen = ((file: fs.PathLike, flags: string | number, mode?: number): number => {
    const filename = String(file);
    if (!swapped && filename.endsWith('/index.js')) {
      swapped = true;
      fs.renameSync(path.join(root, 'src'), path.join(parent, 'moved-src'));
      fs.symlinkSync(outside, path.join(root, 'src'), 'dir');
    }
    return originalOpen(file, flags as number, mode);
  }) as typeof fs.openSync;
  (fs as unknown as { openSync: typeof fs.openSync }).openSync = patchedOpen;
  try {
    const report = auditProject(root, { writeReports: false }).report;
    assert.equal(swapped, true, 'the test must exercise the open boundary');
    assert.equal(report.findings.length, 0, 'outside candidate must never be analyzed as project source');
    assert.ok(unknownCodes(report).some((code) => /path.*changed|source-not-scanned|symlink-content-not-followed/.test(code)));
    assert.ok(!report.readSourceFiles.includes('src/index.js'));
  } finally {
    (fs as unknown as { openSync: typeof fs.openSync }).openSync = originalOpen;
  }
}));

test('D1 migrations and Worker workflow YAML become bounded, fingerprinted evidence only on product match', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.ts', d1_databases: [{ binding: 'DB', database_name: 'private', database_id: 'secret-id' }] }));
  write(root, 'src/index.ts', 'export default {};');
  write(root, 'migrations/0001.sql', 'CREATE TABLE records(id INTEGER);');
  write(root, '.github/workflows/deploy.yml', 'on: push\njobs:\n  deploy:\n    steps: []\n');
  write(root, 'db/notes.sql', 'not a configured migration');
  write(root, '.env-prod/workflow.yml', 'SHOULD_NOT_BE_READ');
  const report = auditProject(root, { writeReports: false }).report as typeof auditProject extends (...args: never[]) => infer R ? R extends { report: infer T } ? T & { readAuxiliaryFiles?: string[]; reviewEvidenceFiles?: Array<{ path: string; kind: string; bytes: number; sha256: string; statFingerprint: string }> } : never : never;
  assert.deepEqual(report.readAuxiliaryFiles?.sort(), ['.github/workflows/deploy.yml', 'migrations/0001.sql']);
  assert.ok(report.reviewEvidenceFiles?.some((item) => item.path === 'migrations/0001.sql' && item.kind === 'd1-migration-sql' && item.sha256.length === 64 && item.statFingerprint));
  assert.ok(report.reviewEvidenceFiles?.some((item) => item.path === '.github/workflows/deploy.yml' && item.kind === 'github-workflow-yaml'));
  assert.ok(!report.readAuxiliaryFiles?.includes('db/notes.sql'));
  assert.ok(!JSON.stringify(report).includes('secret-id'));
}));

test('controlled reread requires current inventory, exact allowlist and fingerprints; emits one file only', async () => {
  const parent = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'cfba-read-test-'));
  const root = path.join(parent, 'project');
  fs.mkdirSync(root);
  try {
    write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.ts' }));
    write(root, 'src/index.ts', 'export default { fetch() { return new Response("ok"); } };');
    const inventoryDir = path.join(parent, 'inventory');
    const created = auditProject(root, { outputDir: inventoryDir });
    const inventory = path.join(created.outputDirectory!, 'inventory.json');
    const module = await import('./audit.ts') as typeof import('./audit.ts') & { readReviewEvidenceFile?: (project: string, inventoryPath: string, relative: string) => string };
    assert.equal(typeof module.readReviewEvidenceFile, 'function');
    assert.equal(module.readReviewEvidenceFile!(root, inventory, 'src/index.ts'), 'export default { fetch() { return new Response("ok"); } };');
    assert.throws(() => module.readReviewEvidenceFile!(root, inventory, '../outside.ts'));
    write(root, 'src/index.ts', 'changed after inventory');
    assert.throws(() => module.readReviewEvidenceFile!(root, inventory, 'src/index.ts'), /stale|changed|fingerprint/i);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});

test('per-binding and per-environment D1 migration directories are selected, shared paths deduplicate, and top-level path is ignored', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({
    main: 'src/index.ts', migrations_dir: 'wrong-top-level',
    d1_databases: [
      { binding: 'DB_ONE', database_name: 'one', migrations_dir: 'database/changes' },
      { binding: 'DB_TWO', database_name: 'two', migrations_dir: 'database/changes' },
    ],
    env: { preview: { d1_databases: [{ binding: 'DB_PREVIEW', database_name: 'preview', migrations_dir: 'env/preview-migrations' }] } },
  }));
  write(root, 'src/index.ts', 'export default {};');
  write(root, 'database/changes/0001.sql', 'CREATE TABLE shared_one(id INTEGER);');
  write(root, 'env/preview-migrations/0001.sql', 'CREATE TABLE preview_one(id INTEGER);');
  write(root, 'migrations/ignored.sql', 'CREATE TABLE top_level_ignored(id INTEGER);');
  write(root, 'wrong-top-level/ignored.sql', 'CREATE TABLE wrong_top_level(id INTEGER);');
  write(root, 'packages/worker/wrangler.json', JSON.stringify({ main: 'index.ts', d1_databases: [{ binding: 'NESTED', database_name: 'nested', migrations_dir: 'schema' }] }));
  write(root, 'packages/worker/index.ts', 'export default {};');
  write(root, 'packages/worker/schema/001.sql', 'CREATE TABLE nested_one(id INTEGER);');
  const report = auditProject(root, { writeReports: false }).report;
  assert.deepEqual(report.readAuxiliaryFiles, [
    'database/changes/0001.sql', 'env/preview-migrations/0001.sql', 'packages/worker/schema/001.sql',
  ]);
  assert.ok(unknownCodes(report).includes('d1-migration-binding-attribution-unknown'));
  for (const pathName of ['migrations/ignored.sql', 'wrong-top-level/ignored.sql']) assert.ok(!report.readAuxiliaryFiles.includes(pathName));
}));

test('malformed Wrangler roots and non-object D1 entries do not authorize workflow or migration evidence', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/index.js' }));
  write(root, 'src/index.js', 'export default {};');
  write(root, '.github/workflows/deploy.yml', 'on: push\njobs: {}\n');
  const shapes: unknown[] = [null, [], 12, 'not-config', true,
    { main: 'index.ts', d1_databases: [null, 'not-a-binding', []] },
    { main: 'index.ts', d1_databases: [{ binding: 'BAD', migrations_dir: '/outside-project' }] }];
  shapes.forEach((shape, index) => {
    const directory = `case-${index}`;
    write(root, `${directory}/wrangler.json`, JSON.stringify(shape));
    write(root, `${directory}/.github/workflows/deploy.yml`, 'on: push\njobs: {}\n');
    write(root, `${directory}/migrations/0001.sql`, 'CREATE TABLE should_not_be_read(id INTEGER);');
  });
  const report = auditProject(root, { writeReports: false }).report;
  assert.deepEqual(report.readAuxiliaryFiles, ['.github/workflows/deploy.yml'], 'only the valid root config may enable its workflow review');
  assert.ok(!report.readAuxiliaryFiles.some((file) => file.endsWith('.sql')));
  assert.ok(unknownCodes(report).includes('config-shape-unsupported-for-auxiliary-review'));
  assert.ok(!JSON.stringify(report).includes('should_not_be_read'));
}));

test('lexical work budget makes adversarially nested source an explicit unknown while retaining safe-read path', () => fixture((root) => {
  write(root, 'wrangler.json', JSON.stringify({ main: 'src/worker.js' }));
  const source = 'while (ready) {'.repeat(16000) + 'this.ctx.storage.setAlarm(1);' + '}'.repeat(16000);
  write(root, 'src/worker.js', source);
  const started = Date.now();
  const report = auditProject(root, { writeReports: false }).report;
  assert.ok(Date.now() - started < 5000, 'the matcher must stop before repeated overlapping loop scans');
  assert.ok(report.readSourceFiles.includes('src/worker.js'));
  assert.ok(!report.scannedSourceFiles.includes('src/worker.js'));
  assert.ok(unknownCodes(report).includes('source-syntax-unsupported'));
  assert.ok(!report.findings.some((finding) => finding.file === 'src/worker.js'));
}));
