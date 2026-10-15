/**
 * [INPUT]: 依赖 node:test、合成夹具与平台适配器
 * [OUTPUT]: 提供 宿主和便携适配器契约测试
 * [POS]: 平台回归测试；不伪造宿主平台
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test from 'node:test';
import type { AuditOptions } from './audit-types.ts';

const modulePath = process.env.AUDIT_MODULE;
const api: typeof import('./audit.ts') = await import(modulePath ? pathToFileURL(path.resolve(modulePath)).href : './audit.ts');
const { auditProject, readReviewEvidenceFile, runCli } = api;
type BunTomlRuntime = typeof globalThis & { Bun?: { TOML?: { parse?: unknown } } };
const hasToml = typeof (globalThis as BunTomlRuntime).Bun?.TOML?.parse === 'function';
const modes: ReadonlyArray<{ label: string; options: AuditOptions }> = [
  { label: 'native', options: {} },
  { label: 'portable-explicit', options: { accessMode: 'portable-stable-tree' } },
];
function write(root: string, relative: string, value: string): void {
  const file = path.join(root, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
}
function fixture(body: (root: string, area: string) => void): void {
  // realpath removes the standard /var -> /private/var macOS system alias.
  const base = fs.realpathSync(os.tmpdir());
  const area = fs.mkdtempSync(path.join(base, 'cfba-portable-'));
  const root = path.join(area, '工程 project');
  fs.mkdirSync(root);
  write(root, 'wrangler.jsonc', '{ // safe fixture\n "main":"src/入口 worker.ts", }');
  write(root, 'src/入口 worker.ts', 'export class DO { async alarm(){ this.ctx.storage.setAlarm(1); } }');
  try { body(root, area); } finally { fs.rmSync(area, { recursive: true, force: true }); }
}
function capture(args: string[]): { exit: number; out: string; error: string } {
  const original = { log: console.log, error: console.error, write: process.stdout.write };
  const out: string[] = [], errors: string[] = [];
  console.log = (...items: unknown[]) => { out.push(items.join(' ')); };
  console.error = (...items: unknown[]) => { errors.push(items.join(' ')); };
  process.stdout.write = ((value: unknown) => { out.push(String(value)); return true; }) as typeof process.stdout.write;
  try { return { exit: runCli(args), out: out.join('\n'), error: errors.join('\n') }; }
  finally { console.log = original.log; console.error = original.error; process.stdout.write = original.write; }
}

for (const mode of modes) {
  const audit = (root: string, options: AuditOptions = {}): ReturnType<typeof auditProject> => auditProject(root, { ...mode.options, ...options });
  test(`${mode.label}: JSONC, TOML, multiple environments, Unicode/spaces and truthful adapter`, () => fixture(root => {
    write(root, 'apps/toml/wrangler.toml', 'main = "index.js"\n[vars]\nPRIVATE = "DO_NOT_DISCLOSE_4387"\n[env.preview]\nmain = "preview.js"\n');
    write(root, 'apps/toml/index.js', 'export default {};');
    write(root, 'apps/toml/preview.js', 'export default {};');
    const report = audit(root, { writeReports: false }).report;
    assert.equal(report.runtimePlatform, process.platform);
    assert.equal(report.secureReadMode, mode.label === 'portable-explicit' || process.platform !== 'linux' ? 'portable-stable-tree' : 'descriptor-anchored');
    assert.ok(report.readSourceFiles.includes('src/入口 worker.ts'));
    assert.ok(report.findings.some(f => f.matchesRuleId === 'CF-DO-ALARM-LOOP'));
    const toml = report.configs.find(c => c.path === 'apps/toml/wrangler.toml');
    assert.equal(toml?.parserStatus, hasToml ? 'supported-bun-toml' : 'unsupported-no-bun-toml-parser');
    if (hasToml) assert.ok(toml.environments.some(e => e.name === 'preview'));
    else assert.ok(report.unknowns.some(u => u.code === 'toml-coverage-unsupported'));
    assert.ok(!JSON.stringify(report).includes('DO_NOT_DISCLOSE_4387'));
  }));
  test(`${mode.label}: invalid configs fail visibly and secret-like paths stay excluded`, () => fixture(root => {
    write(root, 'broken/wrangler.json', '{"main":"a.js","main":"b.js"}');
    write(root, 'bad/wrangler.toml', 'main = [');
    for (const file of ['.env', '.dev.vars', '.npmrc', 'secret.ts', 'secrets/data.ts', 'src/credentials.ts', 'private.pem', 'node_modules/unsafe.js']) write(root, file, 'DO_NOT_DISCLOSE_4387');
    const report = audit(root, { writeReports: false }).report;
    assert.ok(report.configs.some(c => c.parserStatus === 'invalid-json-or-jsonc'));
    assert.ok(report.configs.some(c => c.parserStatus === (hasToml ? 'invalid-toml' : 'unsupported-no-bun-toml-parser')));
    assert.ok(report.skipped.excludedPaths > 0);
    assert.ok(!report.reviewEvidenceFiles.some(f => /secret|credential|node_modules|\.env|\.pem/.test(f.path)));
    assert.ok(!JSON.stringify(report).includes('DO_NOT_DISCLOSE_4387'));
  }));
  test(`${mode.label}: byte, file and entry caps preserve incomplete coverage`, () => fixture(root => {
    write(root, 'src/large.js', 'x'.repeat(300_000));
    for (let i = 0; i < 15; i++) write(root, `extra/${i}.js`, 'export default {};');
    const large = audit(root, { writeReports: false }).report;
    assert.ok(!large.readSourceFiles.includes('src/large.js'));
    assert.ok(large.skipped.unreadableOrOversize > 0);
    for (const [limit, value, code] of [['maxFiles', 4, 'scan-limit-max-files'], ['maxEntries', 4, 'scan-limit-max-entries']] as const) {
      const report = audit(root, { writeReports: false, limits: { [limit]: value } }).report;
      assert.ok(report.unknowns.some(u => u.code === code));
    }
    const capped = audit(root, { writeReports: false, limits: { maxTotalBytes: 80, maxFileBytes: 80 } }).report;
    assert.ok(capped.unknowns.length > 0);
    assert.ok(!capped.readSourceFiles.includes('src/large.js'));
  }));
  test(`${mode.label}: progressive evidence round-trip, traversal rejection and stale inventory`, () => fixture((root, area) => {
    write(root, 'wrangler.jsonc', JSON.stringify({ main: 'src/入口 worker.ts', d1_databases: [{ binding: 'DB', database_name: 'fixture' }] }));
    write(root, 'migrations/0001.sql', 'CREATE TABLE items (id INTEGER);');
    write(root, '.github/workflows/deploy.yml', 'name: fixture\non: workflow_dispatch\njobs: {}');
    const result = audit(root, { outputDir: path.join(area, 'reports') });
    assert.ok(result.outputDirectory);
    const inventory = path.join(result.outputDirectory, 'inventory.json');
    for (const relative of ['src/入口 worker.ts', 'migrations/0001.sql', '.github/workflows/deploy.yml']) {
      assert.ok(result.report.reviewEvidenceFiles.some(f => f.path === relative));
      assert.equal(readReviewEvidenceFile(root, inventory, relative, mode.options), fs.readFileSync(path.join(root, relative), 'utf8'));
    }
    for (const relative of ['../outside.js', '/outside.js', 'src/../outside.js', 'src\\outside.js', 'secrets/key.ts', 'unlisted.js']) {
      assert.throws(() => readReviewEvidenceFile(root, inventory, relative, mode.options));
    }
    write(root, 'src/入口 worker.ts', 'export default { changed: true };');
    assert.throws(() => readReviewEvidenceFile(root, inventory, 'src/入口 worker.ts', mode.options), /stale/);
  }));
  test(`${mode.label}: output is external and source tree is unmodified`, () => fixture((root, area) => {
    assert.throws(() => audit(root, { outputDir: path.join(root, 'reports') }), /output-inside-project/);
    const before = fs.readFileSync(path.join(root, 'src/入口 worker.ts'), 'utf8');
    const result = audit(root, { outputDir: path.join(area, 'outside reports') });
    assert.ok(result.outputDirectory);
    assert.ok(fs.existsSync(path.join(result.outputDirectory, 'inventory.json')));
    assert.ok(fs.existsSync(path.join(result.outputDirectory, 'inventory.md')));
    assert.equal(fs.readFileSync(path.join(root, 'src/入口 worker.ts'), 'utf8'), before);
    assert.ok(!fs.existsSync(path.join(root, 'reports')));
  }));
  test(`${mode.label}: native symlink or Windows directory junction is excluded`, () => fixture((root, area) => {
    const external = path.join(area, 'external');
    fs.mkdirSync(external);
    write(external, 'outside.ts', 'DO_NOT_DISCLOSE_4387');
    const link = path.join(root, 'linked');
    // Junction creation needs no symlink privilege on ordinary Windows installations.
    fs.symlinkSync(external, link, process.platform === 'win32' ? 'junction' : 'dir');
    const report = audit(root, { writeReports: false }).report;
    assert.ok(report.skipped.symlinks > 0);
    assert.ok(!report.readSourceFiles.some((f: string) => f.startsWith('linked/')));
    assert.throws(() => audit(link, { writeReports: false }));
    assert.throws(() => audit(root, { outputDir: path.join(link, 'reports') }));
    assert.ok(!JSON.stringify(report).includes('DO_NOT_DISCLOSE_4387'));
  }));
}
test('native CLI and public exports retain controlled reader contract', () => fixture((root, area) => {
  for (const name of ['auditProject', 'readReviewEvidenceFile', 'runCli', 'parseJsoncStrict', 'stripJsoncComments', 'scanSource', 'maskJavaScript'] as const) assert.equal(typeof api[name], 'function');
  assert.equal(capture(['--help']).exit, 0);
  assert.notEqual(capture([]).exit, 0);
  assert.notEqual(capture(['--unknown']).exit, 0);
  const result = capture(['--project', root, '--output-dir', path.join(area, 'cli reports')]);
  assert.equal(result.exit, 0, result.error);
  const inventory = path.join(JSON.parse(result.out).outputDirectory, 'inventory.json');
  const read = capture(['--project', root, '--inventory', inventory, '--read-file', 'src/入口 worker.ts']);
  assert.equal(read.exit, 0, read.error);
  assert.match(read.out, /setAlarm/);
  const denied = capture(['--project', root, '--inventory', inventory, '--read-file', '../outside.js']);
  assert.notEqual(denied.exit, 0);
  assert.equal(denied.out, '');
}));

test('installed architecture: bounded Chinese L3 modules, compatible public types and one-way dependency DAG', () => {
  const dir = modulePath ? path.dirname(path.resolve(modulePath)) : path.dirname(fileURLToPath(import.meta.url));
  const files = fs.readdirSync(dir).filter(name => name.endsWith('.ts') && !name.endsWith('.test.ts') && name !== 'installed-smoke.ts');
  const graph = new Map<string, string[]>();
  for (const name of files) {
    const text = fs.readFileSync(path.join(dir, name), 'utf8');
    assert.ok(text.split(/\r?\n/).length <= 800, `${name} exceeds 800 lines`);
    const header = text.match(/^\/\*\*\r?\n(?:\s*\*.*\r?\n)*\s*\*\//)?.[0];
    assert.ok(header, `${name} needs a leading L3 contract block`);
    assert.match(header, /^\s*\* \[INPUT\]:\s+\S+/m, `${name} needs an INPUT contract`);
    assert.match(header, /^\s*\* \[OUTPUT\]:\s+\S+/m, `${name} needs an OUTPUT contract`);
    assert.match(header, /^\s*\* \[POS\]:\s+\S+/m, `${name} needs a POS contract`);
    assert.match(header, /^\s*\* \[PROTOCOL\]: 变更时更新此头部，然后检查 CLAUDE\.md\s*$/m, `${name} needs the fixed protocol line`);
    assert.match(header, /[\u3400-\u9fff]/, `${name} needs a Chinese L3 description`);
    const imports = [...text.matchAll(/(?:from\s*|import\s*\()\s*['"]\.\/([^'"]+\.ts)['"]/g)].map(match => match[1]!);
    if (name !== 'audit.ts') assert.ok(!imports.includes('audit.ts'), `${name} imports public facade backwards`);
    graph.set(name, imports);
  }
  const visiting = new Set<string>(), visited = new Set<string>();
  function visit(name: string): void {
    assert.ok(!visiting.has(name), `module dependency cycle at ${name}`);
    if (visited.has(name)) return;
    assert.ok(graph.has(name), `missing module ${name}`);
    visiting.add(name);
    for (const dep of graph.get(name)!) visit(dep);
    visiting.delete(name); visited.add(name);
  }
  for (const name of files) visit(name);
  const facade = fs.readFileSync(path.join(dir, 'audit.ts'), 'utf8');
  for (const type of ['UnknownItem', 'Binding', 'MainStatus', 'EnvironmentInventory', 'ConfigInventory', 'CandidateFinding', 'AuditReport', 'ReviewEvidenceFile', 'AuditOptions', 'SourceScanResult']) assert.match(facade, new RegExp(`\\b${type}\\b`));
});

test('inventories with unknown or mismatched adapter mode cannot authorize evidence', () => fixture((root, area) => {
  assert.throws(() => auditProject(root, {
    writeReports: false,
    // @ts-expect-error 运行时防御测试故意传入未识别的访问模式。
    accessMode: 'unrecognized',
  }), /unsupported-access-mode/);
  const result = auditProject(root, { outputDir: path.join(area, 'reports') });
  assert.ok(result.outputDirectory);
  const inventory = path.join(result.outputDirectory, 'inventory.json');
  const original = fs.readFileSync(inventory, 'utf8');
  for (const secureReadMode of ['unknown-adapter', result.report.secureReadMode === 'descriptor-anchored' ? 'portable-stable-tree' : 'descriptor-anchored']) {
    fs.writeFileSync(inventory, JSON.stringify({ ...JSON.parse(original), secureReadMode }));
    assert.throws(() => readReviewEvidenceFile(root, inventory, 'src/入口 worker.ts'), /stale-inventory/);
  }
}));

test('Windows lexical rejection is platform-neutral unit evidence, not native Windows execution', async () => {
  const dir = modulePath ? path.dirname(path.resolve(modulePath)) : path.dirname(fileURLToPath(import.meta.url));
  const portableApi: typeof import('./portable-fs.ts') = await import(pathToFileURL(path.join(dir, 'portable-fs.ts')).href);
  const { validateWindowsPath, validateWindowsUserPath } = portableApi;
  for (const candidate of ['NUL', 'CON.ts', 'aux/file.ts', 'COM1.js', 'LPT1.txt', 'src/file.ts:stream', 'src/trailing.', 'src/trailing ', 'src/../file.ts']) assert.throws(() => validateWindowsPath(candidate));
  assert.doesNotThrow(() => validateWindowsPath('src/入口 worker.ts'));
  for (const candidate of ['./project', '../project/', 'project/', 'C:/', 'C:/工程 project/', '.']) assert.doesNotThrow(() => validateWindowsUserPath(candidate));
  for (const candidate of ['C:project', 'C:/NUL', 'C:/file:stream', '//?/C:/project']) assert.throws(() => validateWindowsUserPath(candidate));
});
