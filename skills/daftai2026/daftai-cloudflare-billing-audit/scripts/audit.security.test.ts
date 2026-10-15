/**
 * [INPUT]: 依赖 node:test、Linux 文件接口与审计公开接口
 * [OUTPUT]: 提供 描述符和确定性竞态回归测试
 * [POS]: Linux 专属安全测试；其他平台明确跳过
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import nodeTest, { after } from 'node:test';
import { MAX_INVENTORY_BYTES } from './audit-types.ts';
import type { AuditOptions, AuditReport } from './audit-types.ts';

const api: typeof import('./audit.ts') = await import(process.env.AUDIT_MODULE ?? './audit.ts');
const { auditProject, scanSource, runCli } = api;
const linux = process.platform === 'linux';
const fixtureBase = linux ? fs.mkdtempSync(path.join(os.tmpdir(), 'cfba-security-')) : '';
after(() => { if (fixtureBase) fs.rmSync(fixtureBase, { recursive: true, force: true }); });
const test = (name: string, body: () => void): void => {
  nodeTest(name, { skip: linux ? false : 'Linux descriptor and deterministic I/O race suite' }, body);
};

function fixture(body: (root: string, area: string) => void): void {
  const area = fs.mkdtempSync(path.join(fixtureBase, 'case-'));
  const root = path.join(area, 'project');
  fs.mkdirSync(root);
  write(root, 'wrangler.json', '{"main":"main.js"}');
  write(root, 'main.js', 'export default { marker: "SAFE_SOURCE" };');
  try { body(root, area); }
  finally { fs.rmSync(area, { recursive: true, force: true }); }
}
function write(root: string, relative: string, contents: string): void {
  const file = path.join(root, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, contents);
}
function identity(stat: fs.Stats): string { return `${stat.dev}:${stat.ino}`; }
function real(file: unknown): string {
  try { return fs.realpathSync(String(file)); } catch { return ''; }
}
function audited(root: string, options: AuditOptions = {}): AuditReport {
  return auditProject(root, { ...options, writeReports: false }).report;
}
function invoke(root: string, inventory: string, relative = 'main.js'): { exit: number; stdout: string; stderr: string } {
  const oldLog = console.log, oldError = console.error, oldWrite = process.stdout.write;
  const stdout: string[] = [], stderr: string[] = [];
  console.log = (...items: unknown[]) => { stdout.push(items.join(' ')); };
  console.error = (...items: unknown[]) => { stderr.push(items.join(' ')); };
  process.stdout.write = ((chunk: unknown) => { stdout.push(String(chunk)); return true; }) as typeof process.stdout.write;
  let exit: number;
  try { exit = runCli(['--project', root, '--inventory', inventory, '--read-file', relative]); }
  finally { console.log = oldLog; console.error = oldError; process.stdout.write = oldWrite; }
  return { exit, stdout: stdout.join('\n'), stderr: stderr.join('\n') };
}
function rejected(result: ReturnType<typeof invoke>): void {
  assert.notEqual(result.exit, 0);
  assert.equal(result.stdout, '');
  assert.ok(!result.stderr.includes('FAKE_INVENTORY_VALUE') && !result.stderr.includes('EVIL_SOURCE'));
}
function inventoryFor(root: string, area: string): string {
  const result = auditProject(root, { outputDir: path.join(area, 'reports') });
  assert.ok(result.outputDirectory);
  return path.join(result.outputDirectory, 'inventory.json');
}

// Positive controls rule out a hollow green caused by all scans failing closed.
test('security: ordinary project produces a nonempty supported candidate', () => fixture(root => {
  write(root, 'main.js', 'export class DO { async alarm(){ this.ctx.storage.setAlarm(1); } }');
  const report = audited(root);
  assert.ok(report.readSourceFiles.includes('main.js'));
  assert.ok(report.findings.some(finding => finding.matchesRuleId === 'CF-DO-ALARM-LOOP'));
}));
test('security: recursive exact maxFiles cap reports incomplete coverage', () => fixture(root => {
  fs.unlinkSync(path.join(root, 'main.js'));
  write(root, 'wrangler.json', '{"main":"a/000.js"}');
  for (let i = 0; i < 499; i++) write(root, `a/${String(i).padStart(3, '0')}.js`, 'export default {};');
  write(root, 'z.js', 'for(;;) q.send(1);');
  const report = audited(root);
  assert.equal(report.status, 'partial');
  assert.ok(report.unknowns.some(item => item.code.includes('max-files')));
  assert.ok(!report.readSourceFiles.includes('z.js'));
}));
test('security: recursive exact maxEntries cap never silently skips a sibling', () => fixture(root => {
  fs.unlinkSync(path.join(root, 'main.js'));
  write(root, 'wrangler.json', '{"main":"z.js"}');
  fs.mkdirSync(path.join(root, 'a'));
  write(root, 'z.js', 'for(;;) q.send(1);');
  const report = audited(root, { limits: { maxEntries: 3 } });
  if (!report.readSourceFiles.includes('z.js')) {
    assert.equal(report.status, 'partial');
    assert.ok(report.unknowns.some(item => item.code.includes('max-entries')));
  }
}));
for (const [name, source] of [
  ['alarm', 'class DO { alarm = async () => { this.ctx.storage.setAlarm(1); }; }'],
  ['queue', 'class Worker { queue = async (batch) => { batch.messages[0].retry(); env.Q.send(1); }; }'],
]) test(`security: ${name} arrow field has a candidate or explicit syntax unknown`, () => {
  const result = scanSource(source, 'main.js');
  assert.ok(result.findings.length > 0 || result.unsupported.length > 0);
});
test('security: full .env prefix family is never source-review allowlisted', () => fixture(root => {
  for (const name of ['.env-prod.ts', '.envrc.ts', '.envsecret.ts', '.ENV-PROD.ts', '.env-prod/main.js', '.envrc/main.js', '.env.prod.ts']) {
    write(root, name, 'for(;;) q.send("FAKE_VALUE");');
  }
  const report = audited(root);
  assert.deepEqual(report.readSourceFiles, ['main.js']);
  assert.equal(report.findings.length, 0);
}));

// Real rename/symlink mutations are injected immediately before actual I/O calls.
// A renamed, previously pinned inode stays authorized; a fresh external inode does not.
// Either way, detected path changes must not create a reusable review allowlist.
for (const event of ['root-enumeration', 'child-enumeration', 'root-file-open', 'child-file-open']) {
  for (const sameInode of [false, true]) test(`security: ${event} rejects ${sameInode ? 'moved pinned inode' : 'external inode'} redirection`, () => fixture((root, area) => {
    fs.unlinkSync(path.join(root, 'main.js'));
    write(root, 'wrangler.json', '{"main":"src/main.js"}');
    write(root, 'src/main.js', 'export default {};');
    const outside = path.join(area, 'outside');
    write(outside, 'wrangler.json', '{"main":"src/main.js"}');
    write(outside, 'src/main.js', 'for(;;) q.send("FAKE_OUTSIDE");');
    write(outside, 'main.js', 'for(;;) q.send("FAKE_OUTSIDE");');
    const rootEvent = event.startsWith('root'), enumeration = event.endsWith('enumeration');
    const directory = rootEvent ? root : path.join(root, 'src');
    const trigger = enumeration ? directory : path.join(root, rootEvent ? 'wrangler.json' : 'src/main.js');
    const originalIdentity = identity(fs.statSync(trigger));
    const oldOpen = fs.openSync, oldDir = fs.opendirSync;
    let injected = false, unauthorizedIo = false, result: AuditReport | undefined, failure: unknown;
    const matches = (file: unknown): boolean => String(file) === trigger || real(file) === trigger;
    const replace = (): void => {
      if (injected) return;
      injected = true;
      const moved = path.join(area, 'moved');
      fs.renameSync(directory, moved);
      fs.symlinkSync(sameInode ? moved : outside, directory);
    };
    if (enumeration) fs.opendirSync = (file: fs.PathLike, options?: fs.OpenDirOptions) => {
      const intended = matches(file);
      if (intended) replace();
      const handle = oldDir(file, options);
      if (intended && identity(fs.statSync(file)) !== originalIdentity) unauthorizedIo = true;
      return handle;
    };
    else fs.openSync = (file: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
      const intended = matches(file);
      if (intended) replace();
      const fd = oldOpen(file, flags, mode);
      if (intended && identity(fs.fstatSync(fd)) !== originalIdentity) unauthorizedIo = true;
      return fd;
    };
    try { try { result = audited(root); } catch (error) { failure = error; } }
    finally { fs.openSync = oldOpen; fs.opendirSync = oldDir; }
    assert.ok(injected, 'race must hit the actual descriptor-backed I/O path');
    assert.equal(unauthorizedIo, false, 'fresh external inodes must not be opened or enumerated');
    if (failure) return;
    assert.ok(result);
    assert.equal(result.status, 'partial');
    assert.equal(result.findings.length, 0);
    assert.ok(!result.readSourceFiles.includes('src/main.js'));
    assert.ok(result.unknowns.some(item => item.code !== 'static-analysis-scope'));
  }));
}

test('security: unknown access adapter fails closed without spoofing platform', () => fixture(root => {
  assert.throws(() => auditProject(root, {
    writeReports: false,
    // @ts-expect-error 运行时防御测试故意传入未支持的访问模式。
    accessMode: 'unsupported',
  }), /unsupported-access-mode/);
}));

test('security: unavailable descriptor paths fail closed', () => fixture(root => {
  const previous = fs.statSync;
  const mutableFs = fs as unknown as { statSync: typeof fs.statSync };
  const spyStatSync = (file: fs.PathLike, options?: Parameters<typeof fs.statSync>[1]): ReturnType<typeof fs.statSync> => {
    if (/^\/(?:proc\/self|dev)\/fd\//.test(String(file))) throw Object.assign(new Error('fake unavailable descriptor path'), { code: 'ENOENT' });
    return previous(file, options);
  };
  mutableFs.statSync = spyStatSync as typeof fs.statSync;
  try { assert.throws(() => auditProject(root, { writeReports: false }), /secure-path-access-unsupported/); }
  finally { mutableFs.statSync = previous; }
}));
test('security: a capability probe must reject a runtime that follows its real symlink', () => fixture(root => {
  const previous = fs.openSync;
  let injected = false;
  fs.openSync = (file: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
    const name = String(file);
    let isLink = false;
    try { isLink = fs.lstatSync(name).isSymbolicLink(); } catch { /* not the probe */ }
    if (isLink && (name.endsWith('/linked.txt') || /^\/(?:proc\/self|dev)\/fd\/\d+$/.test(name))) {
      injected = true;
      const flagsWithoutNoFollow = typeof flags === 'number' ? flags & ~fs.constants.O_NOFOLLOW : flags;
      return previous(file, flagsWithoutNoFollow, mode);
    }
    return previous(file, flags, mode);
  };
  try {
    assert.throws(() => auditProject(root, { writeReports: false }), /secure-path-access-unsupported/);
    assert.ok(injected, 'probe must reach an existing real symlink');
  } finally { fs.openSync = previous; }
}));

function withTargetTmpdir(root: string, area: string, alias: boolean, body: () => void): void {
  const previousEnv = process.env.TMPDIR, previousMkdtemp = fs.mkdtempSync;
  const temporary = alias ? path.join(area, 'tmp-alias') : root;
  if (alias) fs.symlinkSync(root, temporary);
  process.env.TMPDIR = temporary;
  let targetWrites = 0;
  const spyMkdtempSync = (prefix: string, options?: Parameters<typeof fs.mkdtempSync>[1]): ReturnType<typeof fs.mkdtempSync> => {
    const parent = real(path.dirname(String(prefix)));
    if (parent === root || parent.startsWith(root + path.sep)) targetWrites++;
    return previousMkdtemp(prefix, options);
  };
  fs.mkdtempSync = spyMkdtempSync as typeof fs.mkdtempSync;
  try { body(); assert.equal(targetWrites, 0, 'a temporary write still changes the project even when later cleaned up'); }
  finally {
    fs.mkdtempSync = previousMkdtemp;
    if (previousEnv === undefined) delete process.env.TMPDIR; else process.env.TMPDIR = previousEnv;
  }
}
for (const alias of [false, true]) test(`security: TMPDIR ${alias ? 'symlink' : 'path'} into target never permits probe writes`, () => fixture((root, area) => {
  withTargetTmpdir(root, area, alias, () => { try { audited(root); } catch { /* a conservative refusal is allowed */ } });
}));

// Observe actual open/read attempts, not merely empty error output after a forbidden read.
function watchForbiddenFile(file: string, body: () => void): void {
  const forbidden = fs.statSync(file), wanted = identity(forbidden);
  const oldOpen = fs.openSync, oldRead = fs.readFileSync;
  let opened = 0, read = 0, nonregularAttempts = 0;
  fs.openSync = (target: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
    if (!forbidden.isFile()) {
      let matches = false;
      try { matches = identity(fs.statSync(target)) === wanted; } catch { /* unrelated probe */ }
      if (matches) { nonregularAttempts++; throw new Error('test-blocks-nonregular-open'); }
    }
    const fd = oldOpen(target, flags, mode);
    if (identity(fs.fstatSync(fd)) === wanted) opened++;
    return fd;
  };
  fs.readFileSync = ((target: fs.PathOrFileDescriptor, options?: Parameters<typeof fs.readFileSync>[1]): ReturnType<typeof fs.readFileSync> => {
    try { if (identity(typeof target === 'number' ? fs.fstatSync(target) : fs.statSync(target)) === wanted) read++; }
    catch { /* unrelated probe */ }
    return oldRead(target, options);
  }) as typeof fs.readFileSync;
  try { body(); assert.equal(nonregularAttempts, 0); assert.equal(opened, 0); assert.equal(read, 0); }
  finally { fs.openSync = oldOpen; fs.readFileSync = oldRead; }
}
test('security: emitted inventory supports a nonempty ordinary controlled reread', () => fixture((root, area) => {
  const result = invoke(root, inventoryFor(root, area));
  assert.equal(result.exit, 0);
  assert.ok(result.stdout.includes('SAFE_SOURCE'));
}));
for (const variant of ['sensitive-file', 'sensitive-ancestor', 'symlink-file', 'symlink-ancestor', 'oversize', 'directory', 'fifo']) {
  test(`security: inventory ${variant} is rejected before forbidden I/O`, () => fixture((root, area) => {
    let inventory: string, target: string;
    if (variant === 'sensitive-file') { inventory = target = path.join(area, '.env-prod.ts'); fs.writeFileSync(target, 'FAKE_INVENTORY_VALUE'); }
    else if (variant === 'sensitive-ancestor') { inventory = target = path.join(area, 'credentials/inventory.json'); write(area, 'credentials/inventory.json', 'FAKE_INVENTORY_VALUE'); }
    else if (variant === 'symlink-file') { target = path.join(area, 'ordinary.json'); fs.writeFileSync(target, 'FAKE_INVENTORY_VALUE'); inventory = path.join(area, 'inventory.json'); fs.symlinkSync(target, inventory); }
    else if (variant === 'symlink-ancestor') { target = path.join(area, 'actual/inventory.json'); write(area, 'actual/inventory.json', 'FAKE_INVENTORY_VALUE'); fs.symlinkSync(path.join(area, 'actual'), path.join(area, 'linked')); inventory = path.join(area, 'linked/inventory.json'); }
    else {
      inventory = target = path.join(area, 'inventory.json');
      if (variant === 'oversize') { const fd = fs.openSync(target, 'w'); fs.ftruncateSync(fd, MAX_INVENTORY_BYTES + 1); fs.closeSync(fd); }
      else if (variant === 'directory') fs.mkdirSync(target);
      else execFileSync('mkfifo', [target]);
    }
    watchForbiddenFile(target, () => rejected(invoke(root, inventory)));
  }));
}
for (const sameInode of [false, true]) test(`security: inventory ancestor race rejects ${sameInode ? 'moved inode' : 'external inode'}`, () => fixture((root, area) => {
  const inventory = inventoryFor(root, area), directory = path.dirname(inventory);
  const outside = path.join(area, 'outside');
  write(outside, 'inventory.json', 'FAKE_INVENTORY_VALUE');
  const forbidden = identity(fs.statSync(path.join(outside, 'inventory.json')));
  const previous = fs.openSync;
  let injected = false, outsideOpened = false;
  fs.openSync = (file: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
    if (!injected && real(file) === inventory) {
      injected = true;
      const moved = path.join(area, 'moved');
      fs.renameSync(directory, moved);
      fs.symlinkSync(sameInode ? moved : outside, directory);
    }
    const fd = previous(file, flags, mode);
    if (identity(fs.fstatSync(fd)) === forbidden) outsideOpened = true;
    return fd;
  };
  try { rejected(invoke(root, inventory)); assert.ok(injected); assert.equal(outsideOpened, false); }
  finally { fs.openSync = previous; }
}));
for (const scope of ['root', 'ancestor']) for (const sameInode of [false, true]) {
  test(`security: final reread rejects ${scope} ${sameInode ? 'moved inode' : 'external inode'} after fresh scan`, () => fixture((root, area) => {
    write(root, 'wrangler.json', '{"main":"src/main.js"}');
    write(root, 'src/main.js', 'export default { marker: "SAFE_SOURCE" };');
    const inventory = inventoryFor(root, area), file = path.join(root, 'src/main.js');
    const directory = scope === 'root' ? root : path.join(root, 'src');
    const outside = path.join(area, 'outside');
    write(outside, 'main.js', 'for(;;) q.send("EVIL_SOURCE");');
    write(outside, 'src/main.js', 'for(;;) q.send("EVIL_SOURCE");');
    const forbidden = identity(fs.statSync(path.join(outside, scope === 'root' ? 'src/main.js' : 'main.js')));
    const previous = fs.openSync;
    let seen = 0, injected = false, outsideOpened = false;
    fs.openSync = (candidate: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
      if (real(candidate) === file && ++seen === 2) {
        injected = true;
        const moved = path.join(area, 'moved');
        fs.renameSync(directory, moved);
        fs.symlinkSync(sameInode ? moved : outside, directory);
      }
      const fd = previous(candidate, flags, mode);
      if (identity(fs.fstatSync(fd)) === forbidden) outsideOpened = true;
      return fd;
    };
    try {
      rejected(invoke(root, inventory, 'src/main.js'));
      assert.ok(injected, 'mutation must occur at final reread, after the fresh scan');
      assert.equal(outsideOpened, false);
    } finally { fs.openSync = previous; }
  }));
}
test('security: final reread rejects same-inode equal-length content overwrite', () => fixture((root, area) => {
  const inventory = inventoryFor(root, area), file = path.join(root, 'main.js');
  const contents = fs.readFileSync(file, 'utf8'), previous = fs.openSync;
  let seen = 0, injected = false;
  fs.openSync = (candidate: fs.PathLike, flags: fs.OpenMode, mode?: fs.Mode | null) => {
    if (real(candidate) === file && ++seen === 2) { injected = true; fs.writeFileSync(file, contents.replace('SAFE_SOURCE', 'EVIL_SOURCE')); }
    return previous(candidate, flags, mode);
  };
  try { rejected(invoke(root, inventory)); assert.ok(injected); }
  finally { fs.openSync = previous; }
}));
test('security: controlled reader never probes by writing into target TMPDIR', () => fixture((root, area) => {
  const inventory = inventoryFor(root, area);
  withTargetTmpdir(root, area, false, () => { invoke(root, inventory); });
}));
