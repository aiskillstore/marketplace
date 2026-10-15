/**
 * [INPUT]: 依赖 node:fs、node:path 与 fs-common 指纹
 * [OUTPUT]: 提供 稳定目录树读取及独占输出能力
 * [POS]: macOS 和 Windows 的文件适配器；不提供恶意并发隔离
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import fs from 'node:fs';
import path from 'node:path';
import { digest, statIdentity, statFingerprint, isMissing } from './fs-common.ts';
import { MAX_INVENTORY_BYTES } from './audit-types.ts';
import type { StableStat } from './fs-common.ts';

type ChainEntry = { path: string; real: string; stat: StableStat };
const windows = process.platform === 'win32';

export function validateWindowsPath(input: string, absolute = false): void {
  if (!input || input.includes('\0') || /[\x00-\x1f]/.test(input)) throw new Error('unsafe-windows-path');
  let rest = input;
  if (absolute) {
    if (!/^[A-Za-z]:[\\/]/.test(input)) throw new Error('unsafe-windows-path');
    rest = input.slice(3);
    if (!rest) return;
  }
  if (/[:<>"|?*]/.test(rest) || rest.startsWith('\\') || rest.startsWith('/')) throw new Error('unsafe-windows-path');
  for (const part of rest.split(/[\\/]/)) {
    if (!part || part === '.' || part === '..' || /[. ]$/.test(part) || /^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\.|$)/i.test(part)) throw new Error('unsafe-windows-path');
  }
}
// 用户根路径可带点段和尾部分隔符；命名空间/驱动器相对路径必须在 resolve 前拒绝。
export function validateWindowsUserPath(input: string): void {
  if (!input || input.includes('\0') || /^[\\/]/.test(input)) throw new Error('unsafe-windows-path');
  const absolute = /^[A-Za-z]:[\\/]/.test(input);
  const rest = absolute ? input.slice(3) : input;
  if (rest.includes(':')) throw new Error('unsafe-windows-path');
  for (const part of rest.split(/[\\/]/)) {
    if (part === '' || part === '.' || part === '..') continue;
    validateWindowsPath(part);
  }
}
function component(name: string): void {
  if (!name || name === '.' || name === '..' || /[\\/\0]/.test(name)) throw new Error('unsafe-project-relative-path');
  if (windows) validateWindowsPath(name);
}
// lstat 已逐级拒绝链接；macOS 卷的大小写别名不属于重定向。
function samePath(a: string, b: string): boolean {
  return windows || process.platform === 'darwin' ? a.toLowerCase() === b.toLowerCase() : a === b;
}
function directorySame(a: StableStat, b: StableStat): boolean {
  return a.isDirectory() && !a.isSymbolicLink() && a.dev === b.dev && a.ino === b.ino && a.mode === b.mode;
}
function fingerprint(chain: ChainEntry[]): string {
  return digest(chain.map(e => `${e.path}:${e.real}:${e.stat.dev}:${e.stat.ino}:${e.stat.mode}`).join('|'));
}
function chainTo(absolute: string, createMissing = false): ChainEntry[] {
  if (windows) validateWindowsPath(absolute, true);
  const root = path.parse(absolute).root;
  const parts = absolute.slice(root.length).split(path.sep).filter(Boolean);
  const chain: ChainEntry[] = [];
  let cursor = root;
  for (const part of ['', ...parts]) {
    if (part) { component(part); cursor = path.join(cursor, part); }
    let stat: StableStat;
    try { stat = fs.lstatSync(cursor, { bigint: true }); }
    catch (error) {
      if (!part || !createMissing || !isMissing(error)) throw error;
      checkChain(chain);
      fs.mkdirSync(cursor, { mode: 0o700 });
      stat = fs.lstatSync(cursor, { bigint: true });
    }
    if (stat.isSymbolicLink()) throw new Error('project-path-through-symlink');
    if (!stat.isDirectory()) throw new Error('project-path-not-directory');
    const real = fs.realpathSync(cursor);
    if (!samePath(real, cursor)) throw new Error('project-path-through-symlink');
    chain.push({ path: cursor, real, stat });
  }
  checkChain(chain);
  return chain;
}
function checkChain(chain: ChainEntry[]): void {
  for (const entry of chain) {
    let stat: StableStat;
    try { stat = fs.lstatSync(entry.path, { bigint: true }); }
    catch { throw new Error('project-path-changed-during-scan'); }
    if (!directorySame(stat, entry.stat) || !samePath(fs.realpathSync(entry.path), entry.real)) throw new Error('project-path-changed-during-scan');
  }
}

export class PortableFs {
  readonly mode = 'portable-stable-tree' as const;
  private closed = false;
  readonly rootPath: string;
  private readonly rootChain: ChainEntry[];
  private constructor(rootPath: string, rootChain: ChainEntry[]) { this.rootPath = rootPath; this.rootChain = rootChain; }
  static openDirectory(input: string, createMissing = false): PortableFs {
    // Validate before resolve: Windows drive-relative and special namespace syntax must not normalize away.
    if (windows) validateWindowsUserPath(input);
    const absolute = path.resolve(input);
    try { return new PortableFs(absolute, chainTo(absolute, createMissing)); }
    catch (error) { if (isMissing(error)) throw new Error('project-path-not-found'); throw error; }
  }
  assertRootStable(): void {
    if (this.closed) throw new Error('secure-tree-closed');
    checkChain(this.rootChain);
  }
  rootFingerprint(): string { this.assertRootStable(); return fingerprint(this.rootChain); }
  private directory(relative: string, expected?: StableStat): ChainEntry[] {
    this.assertRootStable();
    const parts = relative === '.' || relative === '' ? [] : relative.split('/');
    parts.forEach(component);
    const chain = chainTo(path.join(this.rootPath, ...parts));
    this.assertRootStable();
    if (expected && !directorySame(chain.at(-1)!.stat, expected)) throw new Error('project-path-changed-during-scan');
    return chain;
  }
  private parent(relative: string): { chain: ChainEntry[]; file: string } {
    const parts = relative.split('/');
    parts.forEach(component);
    const name = parts.pop()!;
    const chain = this.directory(parts.join('/') || '.');
    return { chain, file: path.join(chain.at(-1)!.path, name) };
  }
  directoryFingerprint(relative: string, expected?: StableStat): string { return fingerprint(this.directory(relative, expected)); }
  listDirectory(relative: string, maxItems: number, expected?: StableStat): { entries: fs.Dirent[]; capped: boolean; stat: StableStat; directoryFingerprint: string } {
    const chain = this.directory(relative, expected);
    const stat = chain.at(-1)!.stat;
    const handle = fs.opendirSync(chain.at(-1)!.path);
    const entries: fs.Dirent[] = [];
    let capped = false;
    try {
      checkChain(chain);
      while (true) {
        const entry = handle.readSync();
        if (!entry) break;
        if (entries.length >= maxItems) { capped = true; break; }
        entries.push(entry);
      }
      checkChain(chain); this.assertRootStable();
      return { entries, capped, stat, directoryFingerprint: fingerprint(chain) };
    } finally { handle.closeSync(); }
  }
  inspectFile(relative: string): { status: 'file' | 'directory' | 'missing' | 'symlink' | 'other'; stat?: StableStat; parentFingerprint?: string } {
    try {
      const { chain, file } = this.parent(relative);
      const stat = fs.lstatSync(file, { bigint: true });
      if (stat.isSymbolicLink()) return { status: 'symlink', stat };
      if (!samePath(fs.realpathSync(file), file)) return { status: 'symlink', stat };
      checkChain(chain); this.assertRootStable();
      if (stat.isFile()) return { status: 'file', stat, parentFingerprint: fingerprint(chain) };
      return { status: stat.isDirectory() ? 'directory' : 'other', stat };
    } catch (error) {
      if (error instanceof Error && /symlink/.test(error.message)) return { status: 'symlink' };
      return { status: isMissing(error) ? 'missing' : 'other' };
    }
  }
  readFile(relative: string, maxBytes: number, expected?: { stat: StableStat; statFingerprint?: string }): { text?: string; bytes?: number; sha256?: string; statFingerprint?: string; error?: string } {
    let fd: number | undefined;
    try {
      if (!Number.isSafeInteger(maxBytes) || maxBytes < 0 || maxBytes > MAX_INVENTORY_BYTES) return { error: 'invalid-byte-limit' };
      const { chain, file } = this.parent(relative);
      const before = fs.lstatSync(file, { bigint: true });
      if (before.isSymbolicLink() || !samePath(fs.realpathSync(file), file)) return { error: 'symlink' };
      if (!before.isFile()) return { error: 'not-regular-file' };
      if (before.size > BigInt(maxBytes)) return { error: 'file-too-large' };
      const token = fingerprint(chain);
      const beforeFingerprint = statFingerprint(before, token);
      if (expected && (statIdentity(expected.stat) !== statIdentity(before) || (expected.statFingerprint && expected.statFingerprint !== beforeFingerprint))) return { error: 'path-changed' };
      checkChain(chain);
      const flags = fs.constants.O_RDONLY | (windows ? 0 : (fs.constants.O_NOFOLLOW ?? 0) | (fs.constants.O_NONBLOCK ?? 0));
      fd = fs.openSync(file, flags);
      const opened = fs.fstatSync(fd, { bigint: true });
      if (!opened.isFile() || statIdentity(opened) !== statIdentity(before)) return { error: 'path-changed' };
      checkChain(chain); this.assertRootStable();
      if (!samePath(fs.realpathSync(file), file) || statIdentity(fs.lstatSync(file, { bigint: true })) !== statIdentity(opened)) return { error: 'path-changed' };
      const buffer = Buffer.alloc(maxBytes + 1);
      let count = 0;
      while (count < buffer.length) {
        const n = fs.readSync(fd, buffer, count, buffer.length - count, count);
        if (!n) break;
        count += n;
      }
      if (count > maxBytes) return { error: 'file-too-large' };
      const after = fs.fstatSync(fd, { bigint: true });
      checkChain(chain); this.assertRootStable();
      const entry = fs.lstatSync(file, { bigint: true });
      if (!entry.isFile() || statIdentity(after) !== statIdentity(opened) || statIdentity(entry) !== statIdentity(opened) || !samePath(fs.realpathSync(file), file)) return { error: 'path-changed' };
      const content = buffer.subarray(0, count);
      return { text: content.toString('utf8'), bytes: count, sha256: digest(content), statFingerprint: statFingerprint(after, token) };
    } catch (error) { return { error: error instanceof Error ? error.message : 'unreadable' }; }
    finally { if (fd !== undefined) fs.closeSync(fd); }
  }
  writeNewFile(name: string, contents: string): void {
    component(name); this.assertRootStable();
    const file = path.join(this.rootPath, name);
    const fd = fs.openSync(file, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | (windows ? 0 : (fs.constants.O_NOFOLLOW ?? 0)), 0o600);
    try {
      const before = fs.fstatSync(fd, { bigint: true });
      if (!before.isFile() || before.nlink !== 1n) throw new Error('unsafe-output-file');
      this.assertRootStable();
      const entry = fs.lstatSync(file, { bigint: true });
      if (!entry.isFile() || entry.dev !== before.dev || entry.ino !== before.ino || !samePath(fs.realpathSync(file), file)) throw new Error('output-path-changed');
      const data = Buffer.from(contents);
      let count = 0;
      while (count < data.length) count += fs.writeSync(fd, data, count, data.length - count, count);
      fs.fsyncSync(fd);
      const after = fs.fstatSync(fd, { bigint: true });
      this.assertRootStable();
      const final = fs.lstatSync(file, { bigint: true });
      if (!final.isFile() || final.dev !== after.dev || final.ino !== after.ino || after.size !== BigInt(data.length) || !samePath(fs.realpathSync(file), file)) throw new Error('output-write-incomplete');
    } finally { fs.closeSync(fd); }
  }
  createChildDirectory(name: string): PortableFs {
    component(name); this.assertRootStable();
    const child = path.join(this.rootPath, name);
    try { fs.mkdirSync(child, { mode: 0o700 }); }
    catch (error) { if ((error as NodeJS.ErrnoException).code === 'EEXIST') throw new Error('output-collision'); throw error; }
    this.assertRootStable();
    return PortableFs.openDirectory(child);
  }
  close(): void { this.closed = true; }
}
