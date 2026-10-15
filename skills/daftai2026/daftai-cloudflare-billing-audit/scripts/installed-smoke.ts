#!/usr/bin/env bun
/**
 * [INPUT]: 依赖 node 内置模块、Bun 和指定安装目录
 * [OUTPUT]: 提供 原生 CLI、受控读取、安装测试和哈希回执
 * [POS]: 安装验收入口；只创建并清理自身合成夹具
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ownDir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
let skillDir = path.resolve(ownDir, '..');
let output: string | undefined;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--skill-dir' && args[i + 1]) skillDir = path.resolve(args[++i]!);
  else if (args[i] === '--output' && args[i + 1]) output = path.resolve(args[++i]!);
  else throw new Error('Usage: bun installed-smoke.ts [--skill-dir <unpacked-skill>] [--output <result.json>]');
}
const bun = (globalThis as typeof globalThis & { Bun?: { version: string } }).Bun;
if (!bun) throw new Error('This acceptance runner requires Bun.');
const modulePath = path.join(skillDir, 'scripts', 'audit.ts');
const hashes: Record<string, string> = {};
function collect(dir: string): void {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
    const file = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) throw new Error('Installed skill must not contain symlinks.');
    if (entry.isDirectory()) { if (entry.name !== 'audit-results') collect(file); }
    else if (entry.isFile()) hashes[path.relative(skillDir, file).split(path.sep).join('/')] = createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  }
}
collect(skillDir);
const artifactHash = createHash('sha256').update(JSON.stringify(Object.entries(hashes).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0))).digest('hex');
const results: Array<{ name: string; status: string; detail?: string }> = [];
let adapter = 'UNKNOWN';
const area = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'cfba-installed-'));
try {
  const root = path.join(area, '工程 project');
  fs.mkdirSync(root);
  fs.writeFileSync(path.join(root, 'wrangler.jsonc'), '{"main":"worker.ts"}');
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({ scripts: { preinstall: 'exit 91', audit: 'exit 92' } }));
  const marker = path.join(area, 'TARGET_EXECUTED');
  fs.writeFileSync(path.join(root, 'must-not-run.js'), `require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'executed'); throw new Error('Target code must not execute');`);
  fs.writeFileSync(path.join(root, 'worker.ts'), 'export class DO { async alarm(){ this.ctx.storage.setAlarm(1); } }');
  const before = Object.fromEntries(fs.readdirSync(root).map(name => [name, createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex')]));
  try {
    const api = await import(pathToFileURL(modulePath).href);
    const report = api.auditProject(root, { writeReports: false }).report;
    adapter = report.secureReadMode;
    if (report.runtimePlatform !== process.platform || !report.findings.length) throw new Error('Missing positive control or inaccurate platform');
    results.push({ name: 'installed-module-native-positive-control', status: 'PASS' });
  } catch (error) { results.push({ name: 'installed-module-native-positive-control', status: 'FAIL', detail: String(error) }); }
  const cli = spawnSync(process.execPath, [modulePath, '--project', root, '--output-dir', path.join(area, 'reports')], { encoding: 'utf8' });
  try {
    if (cli.error || cli.status !== 0) throw new Error(String(cli.error ?? cli.stderr));
    const summary = JSON.parse(cli.stdout);
    const inventory = path.join(summary.outputDirectory, 'inventory.json');
    const read = spawnSync(process.execPath, [modulePath, '--project', root, '--inventory', inventory, '--read-file', 'worker.ts'], { encoding: 'utf8' });
    if (read.status !== 0 || !read.stdout.includes('setAlarm')) throw new Error(read.stderr || 'Controlled CLI read failed');
    results.push({ name: 'installed-cli-inventory-and-controlled-read', status: 'PASS' });
  } catch (error) { results.push({ name: 'installed-cli-inventory-and-controlled-read', status: 'FAIL', detail: String(error) }); }
  const after = Object.fromEntries(fs.readdirSync(root).map(name => [name, createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex')]));
  results.push({ name: 'target-not-executed-and-content-fingerprints-unchanged', status: JSON.stringify(before) === JSON.stringify(after) && !fs.existsSync(marker) ? 'PASS' : 'FAIL' });
  // Absolute installed paths avoid Bun's fuzzy filters and validate all installed suites.
  const testPaths = fs.readdirSync(path.join(skillDir, 'scripts')).filter(name => name.endsWith('.test.ts')).sort().map(name => path.join(skillDir, 'scripts', name));
  if (!testPaths.length) throw new Error('Installed skill has no test suites.');
  const tests = spawnSync(process.execPath, ['test', ...testPaths], {
    encoding: 'utf8', env: { ...process.env, AUDIT_MODULE: modulePath }, maxBuffer: 8 * 1024 * 1024,
  });
  results.push({ name: 'full-installed-test-suite', status: !tests.error && tests.status === 0 ? 'PASS' : 'FAIL', detail: `${tests.stdout ?? ''}${tests.stderr ?? ''}${tests.error ?? ''}` });
} finally { fs.rmSync(area, { recursive: true, force: true }); }
const passed = results.every(result => result.status === 'PASS');
const matrix = Object.fromEntries(['linux', 'darwin', 'win32'].map(platform => [platform, {
  status: platform === process.platform ? (passed ? 'PASS' : 'FAIL') : 'NOT_RUN',
  reason: platform === process.platform ? 'Executed on the real native host.' : 'Requires a real native host; Linux portable-adapter checks do not establish native compatibility.',
}]));
const report = {
  schemaVersion: '1.0', generatedAt: new Date().toISOString(), machine: { hostname: os.hostname(), platform: process.platform, arch: process.arch, release: os.release() },
  runtime: { bun: bun.version, nodeCompatibility: process.versions.node, executable: process.execPath },
  adapter, installedSkill: { directory: skillDir, artifactHash, files: hashes },
  harness: { path: fileURLToPath(import.meta.url), testHash: createHash('sha256').update(fs.readFileSync(path.join(skillDir, 'scripts', 'audit.portable.test.ts'))).digest('hex') },
  coverage: { executed: ['core-config-suite', 'portable-contract-suite', 'host-applicable-security-suite', 'native CLI', 'installed imports', 'target content immutability'], linkFixture: process.platform === 'win32' ? 'native-directory-junction' : 'native-directory-symlink', excluded: ['native hosts other than the current machine'], capabilitySkips: process.platform === 'linux' ? [] : ['Linux descriptor hostile-concurrency/FIFO regression suite: Linux-only tests skipped by the suite'] },
  results, nativeMatrix: matrix, status: passed ? 'PASS' : 'FAIL',
};
const json = `${JSON.stringify(report, null, 2)}\n`;
if (output) { fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, json); }
process.stdout.write(json);
process.exitCode = passed ? 0 : 1;
