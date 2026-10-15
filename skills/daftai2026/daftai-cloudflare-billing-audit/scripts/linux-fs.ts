/**
 * [INPUT]: 依赖 node:fs、node:path 与 fs-common 身份原语
 * [OUTPUT]: 提供 Linux 描述符锚定读取与独占输出能力
 * [POS]: Linux 文件适配器；能力缺失时拒绝而不降级
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { digest, statIdentity, sameDirectory, identityOf, isMissing, statFingerprint } from './fs-common.ts';
import { MAX_INVENTORY_BYTES } from './audit-types.ts';
import type { DirectoryIdentity, OpenDirectory, StableStat } from './fs-common.ts';
function descriptorPrefix(): string {
  // 只读探测描述符路径语义；此适配器仅接收 Linux 宿主。
  if (process.platform !== 'linux') throw new Error('secure-path-access-unsupported');
  const base = '/proc/self/fd';
  const required = fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW;
  if (!required || fs.constants.O_NOFOLLOW === undefined || fs.constants.O_DIRECTORY === undefined) throw new Error('secure-path-access-unsupported');
  let rootFd: number | undefined;
  let probeFd: number | undefined;
  try {
    rootFd = fs.openSync('/', fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
    const root = fs.fstatSync(rootFd, { bigint: true });
    const descriptor = fs.statSync(`${base}/${rootFd}`, { bigint: true });
    if (descriptor.dev !== root.dev || descriptor.ino !== root.ino) throw new Error('secure-path-access-unsupported');
    probeFd = fs.openSync(`${base}/${rootFd}/.`, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
    const traversed = fs.fstatSync(probeFd, { bigint: true });
    if (traversed.dev !== root.dev || traversed.ino !== root.ino) throw new Error('secure-path-access-unsupported');
    fs.closeSync(probeFd); probeFd = undefined;
    let rejectedSymlink = false;
    try { probeFd = fs.openSync(`${base}/${rootFd}`, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW); }
    catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code !== 'ELOOP' && code !== 'EMLINK' && code !== 'ENOTDIR') throw new Error('secure-path-access-unsupported');
      rejectedSymlink = true;
    }
    if (!rejectedSymlink || probeFd !== undefined) throw new Error('secure-path-access-unsupported');
    return base;
  } catch {
    throw new Error('secure-path-access-unsupported');
  } finally {
    if (probeFd !== undefined) try { fs.closeSync(probeFd); } catch { /* already closed */ }
    if (rootFd !== undefined) try { fs.closeSync(rootFd); } catch { /* already closed */ }
  }
}

export class AnchoredFs {
  readonly mode = 'descriptor-anchored' as const;
  readonly rootPath: string;
  readonly prefix: string;
  readonly rootFd: number;
  readonly rootIdentities: DirectoryIdentity[];
  private readonly baseFd: number;
  private readonly rootStat: StableStat;
  private closed = false;

  private constructor(rootPath: string, prefix: string, rootFd: number, baseFd: number, identities: DirectoryIdentity[]) {
    this.rootPath = rootPath;
    this.prefix = prefix;
    this.rootFd = rootFd;
    this.baseFd = baseFd;
    this.rootIdentities = identities;
    this.rootStat = fs.fstatSync(rootFd, { bigint: true });
  }

  static openDirectory(absolutePath: string, createMissing = false): AnchoredFs {
    const absolute = path.resolve(absolutePath);
    const prefix = descriptorPrefix();
    const rootPart = path.parse(absolute).root;
    const components = absolute.slice(rootPart.length).split(path.sep).filter(Boolean);
    const baseFd = fs.openSync(rootPart, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
    let parentFd = baseFd;
    const identities: DirectoryIdentity[] = [];
    try {
      let cursor = rootPart;
      for (const component of components) {
        const entryPath = `${prefix}/${parentFd}/${component}`;
        let entry: StableStat;
        try { entry = fs.lstatSync(entryPath, { bigint: true }); }
        catch (error) {
          if (!createMissing || !isMissing(error)) throw error;
          fs.mkdirSync(entryPath, { mode: 0o700 });
          entry = fs.lstatSync(entryPath, { bigint: true });
        }
        if (entry.isSymbolicLink() || !entry.isDirectory()) throw new Error('path-component-rejected');
        const nextFd = fs.openSync(entryPath, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
        const opened = fs.fstatSync(nextFd, { bigint: true });
        if (!opened.isDirectory() || opened.dev !== entry.dev || opened.ino !== entry.ino) {
          fs.closeSync(nextFd);
          throw new Error('path-changed-during-open');
        }
        identities.push(identityOf(component, opened));
        cursor = path.join(cursor, component);
        let after: StableStat;
        try { after = fs.lstatSync(`${prefix}/${parentFd}/${component}`, { bigint: true }); }
        catch { fs.closeSync(nextFd); throw new Error('path-changed-during-open'); }
        if (!sameDirectory(after, identities.at(-1)!)) { fs.closeSync(nextFd); throw new Error('path-changed-during-open'); }
        if (parentFd !== baseFd) fs.closeSync(parentFd);
        parentFd = nextFd;
      }
      if (!fs.fstatSync(parentFd).isDirectory()) throw new Error('project-path-not-directory');
      const tree = new AnchoredFs(absolute, prefix, parentFd, baseFd, identities);
      tree.assertRootStable();
      return tree;
    } catch (error) {
      if (parentFd !== baseFd) try { fs.closeSync(parentFd); } catch { /* closed */ }
      try { fs.closeSync(baseFd); } catch { /* closed */ }
      if (error instanceof Error && error.message === 'path-component-rejected') throw new Error('project-path-through-symlink');
      if (error instanceof Error && error.message === 'path-changed-during-open') throw new Error('project-path-changed-during-scan');
      if (isMissing(error)) throw new Error('project-path-not-found');
      throw error;
    }
  }

  descriptorPath(fd: number): string { return `${this.prefix}/${fd}`; }

  rootFingerprint(): string {
    this.assertRootStable();
    return digest(this.rootIdentities.map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|'));
  }

  private openAt(parentFd: number, name: string, flags: number, mode?: number): number {
    if (!name || name === '.' || name === '..' || name.includes('/') || name.includes('\\')) throw new Error('unsafe-path-component');
    return fs.openSync(`${this.descriptorPath(parentFd)}/${name}`, flags | fs.constants.O_NOFOLLOW, mode);
  }

  private lstatAt(parentFd: number, name: string): StableStat {
    if (!name || name === '.' || name === '..' || name.includes('/') || name.includes('\\')) throw new Error('unsafe-path-component');
    return fs.lstatSync(`${this.descriptorPath(parentFd)}/${name}`, { bigint: true });
  }

  assertRootStable(): void {
    if (this.closed) throw new Error('secure-tree-closed');
    let parentFd = this.baseFd;
    try {
      for (const identity of this.rootIdentities) {
        let stat: StableStat;
        try { stat = this.lstatAt(parentFd, identity.name); }
        catch { throw new Error('project-path-changed-during-scan'); }
        if (!sameDirectory(stat, identity)) throw new Error('project-path-changed-during-scan');
        let child: number;
        try { child = this.openAt(parentFd, identity.name, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY); }
        catch { throw new Error('project-path-changed-during-scan'); }
        const openedStat = fs.fstatSync(child, { bigint: true });
        if (!sameDirectory(openedStat, identity)) { fs.closeSync(child); throw new Error('project-path-changed-during-scan'); }
        if (parentFd !== this.baseFd) fs.closeSync(parentFd);
        parentFd = child;
      }
      const current = fs.fstatSync(parentFd, { bigint: true });
      if (current.dev !== this.rootStat.dev || current.ino !== this.rootStat.ino) throw new Error('project-path-changed-during-scan');
    } finally {
      if (parentFd !== this.baseFd) fs.closeSync(parentFd);
    }
  }

  openDirectory(relative: string, expected?: StableStat): OpenDirectory {
    this.assertRootStable();
    const parts = relative === '.' || relative === '' ? [] : relative.split('/');
    let parentFd = this.rootFd;
    const identities: DirectoryIdentity[] = [];
    try {
      for (const [index, part] of parts.entries()) {
        if (!part || part === '.' || part === '..' || part.includes('\\')) throw new Error('unsafe-project-relative-path');
        let stat: StableStat;
        try { stat = this.lstatAt(parentFd, part); }
        catch { throw new Error('project-path-changed-during-scan'); }
        if (stat.isSymbolicLink()) throw new Error('symlink-path-not-followed');
        if (!stat.isDirectory()) throw new Error('project-path-not-directory');
        if (index === parts.length - 1 && expected && (stat.dev !== expected.dev || stat.ino !== expected.ino)) throw new Error('project-path-changed-during-scan');
        let child: number;
        try { child = this.openAt(parentFd, part, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY); }
        catch { throw new Error('project-path-changed-during-scan'); }
        const openedStat = fs.fstatSync(child, { bigint: true });
        if (!sameDirectory(openedStat, identityOf(part, stat))) { fs.closeSync(child); throw new Error('project-path-changed-during-scan'); }
        if (index === parts.length - 1 && expected && (openedStat.dev !== expected.dev || openedStat.ino !== expected.ino)) { fs.closeSync(child); throw new Error('project-path-changed-during-scan'); }
        if (parentFd !== this.rootFd) fs.closeSync(parentFd);
        parentFd = child;
        identities.push(identityOf(part, openedStat));
      }
      this.assertRootStable();
      return { fd: parentFd, identities };
    } catch (error) {
      if (parentFd !== this.rootFd) try { fs.closeSync(parentFd); } catch { /* close failed */ }
      throw error;
    }
  }

  closeDirectory(opened: OpenDirectory): void {
    if (opened.fd !== this.rootFd) try { fs.closeSync(opened.fd); } catch { /* closed */ }
  }

  directoryFingerprint(relative: string, expected?: StableStat): string {
    const opened = this.openDirectory(relative, expected);
    try {
      const identities = [...this.rootIdentities, ...opened.identities].map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|');
      this.assertRootStable();
      return digest(identities);
    } finally { this.closeDirectory(opened); }
  }

  listDirectory(relative: string, maxItems: number, expected?: StableStat): { entries: fs.Dirent[]; capped: boolean; stat: StableStat; directoryFingerprint: string } {
    const opened = this.openDirectory(relative, expected);
    let handle: fs.Dir | undefined;
    const entries: fs.Dirent[] = [];
    let capped = false;
    try {
      const stat = fs.fstatSync(opened.fd, { bigint: true });
      handle = fs.opendirSync(this.descriptorPath(opened.fd));
      while (true) {
        const entry = handle.readSync();
        if (!entry) break;
        if (entries.length >= maxItems) { capped = true; break; }
        entries.push(entry);
      }
      try { handle.closeSync(); } catch { /* closed */ }
      handle = undefined;
      this.assertRootStable();
      const rechecked = this.openDirectory(relative, expected);
      try {
        const after = fs.fstatSync(rechecked.fd, { bigint: true });
        if (after.dev !== stat.dev || after.ino !== stat.ino) throw new Error('project-path-changed-during-scan');
      } finally { this.closeDirectory(rechecked); }
      const identityText = [...this.rootIdentities, ...opened.identities].map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|');
      return { entries, capped, stat, directoryFingerprint: digest(identityText) };
    } catch (error) {
      if (error instanceof Error && /path-changed|symlink-path/.test(error.message)) throw error;
      throw new Error('directory-read-failed');
    } finally {
      try { handle?.closeSync(); } catch { /* closed */ }
      this.closeDirectory(opened);
    }
  }

  inspectFile(relative: string): { status: 'file' | 'directory' | 'missing' | 'symlink' | 'other'; stat?: StableStat; parentFingerprint?: string } {
    const parts = relative.split('/');
    const name = parts.pop();
    if (!name || name === '.' || name === '..') return { status: 'other' };
    let parent: OpenDirectory;
    try { parent = this.openDirectory(parts.join('/') || '.'); }
    catch (error) {
      if (error instanceof Error && error.message === 'symlink-path-not-followed') return { status: 'symlink' };
      if (isMissing(error)) return { status: 'missing' };
      return { status: 'other' };
    }
    try {
      let stat: StableStat;
      try { stat = this.lstatAt(parent.fd, name); }
      catch (error) { return { status: isMissing(error) ? 'missing' : 'other' }; }
      if (stat.isSymbolicLink()) return { status: 'symlink', stat };
      if (stat.isFile()) return { status: 'file', stat, parentFingerprint: digest([...this.rootIdentities, ...parent.identities].map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|')) };
      if (stat.isDirectory()) return { status: 'directory', stat };
      return { status: 'other', stat };
    } finally { this.closeDirectory(parent); }
  }

  readFile(relative: string, maxBytes: number, expected?: { stat: StableStat; statFingerprint?: string }): { text?: string; bytes?: number; sha256?: string; statFingerprint?: string; error?: string } {
    if (!Number.isSafeInteger(maxBytes) || maxBytes < 0 || maxBytes > MAX_INVENTORY_BYTES) return { error: 'invalid-byte-limit' };
    const parts = relative.split('/');
    const name = parts.pop();
    if (!name || name === '.' || name === '..') return { error: 'unsafe-project-relative-path' };
    let parent: OpenDirectory;
    try { parent = this.openDirectory(parts.join('/') || '.'); }
    catch (error) { return { error: error instanceof Error ? error.message : 'path-changed' }; }
    let fd: number | undefined;
    try {
      const before = this.lstatAt(parent.fd, name);
      if (before.isSymbolicLink()) return { error: 'symlink' };
      if (!before.isFile()) return { error: 'not-regular-file' };
      if (before.size > BigInt(maxBytes)) return { error: 'file-too-large' };
      const parentToken = digest([...this.rootIdentities, ...parent.identities].map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|'));
      const currentFingerprint = statFingerprint(before, parentToken);
      if (expected && (before.dev !== expected.stat.dev || before.ino !== expected.stat.ino || (expected.statFingerprint && currentFingerprint !== expected.statFingerprint))) return { error: 'path-changed' };
      fd = this.openAt(parent.fd, name, fs.constants.O_RDONLY | fs.constants.O_NONBLOCK);
      const openedStat = fs.fstatSync(fd, { bigint: true });
      if (!openedStat.isFile() || openedStat.dev !== before.dev || openedStat.ino !== before.ino || openedStat.size !== before.size) return { error: 'path-changed' };
      const buffer = Buffer.alloc(maxBytes + 1);
      let count = 0;
      while (count < buffer.length) {
        const read = fs.readSync(fd, buffer, count, buffer.length - count, count);
        if (read === 0) break;
        count += read;
      }
      if (count > maxBytes) return { error: 'file-too-large' };
      const after = fs.fstatSync(fd, { bigint: true });
      this.assertRootStable();
      const parentAfter = this.openDirectory(parts.join('/') || '.');
      try {
        const entryAfter = this.lstatAt(parentAfter.fd, name);
        if (entryAfter.isSymbolicLink() || !entryAfter.isFile() || entryAfter.dev !== before.dev || entryAfter.ino !== before.ino || statIdentity(after) !== statIdentity(openedStat)) return { error: 'path-changed' };
        const afterChain = digest([...this.rootIdentities, ...parentAfter.identities].map((item) => `${item.name}:${item.dev}:${item.ino}:${item.mode}`).join('|'));
        if (afterChain !== parentToken) return { error: 'path-changed' };
        const fileStatFingerprint = statFingerprint(after, afterChain);
        if (expected?.statFingerprint && fileStatFingerprint !== expected.statFingerprint) return { error: 'path-changed' };
        const content = buffer.subarray(0, count);
        return { text: content.toString('utf8'), bytes: count, sha256: digest(content), statFingerprint: fileStatFingerprint };
      } finally { this.closeDirectory(parentAfter); }
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'unreadable' };
    } finally {
      if (fd !== undefined) try { fs.closeSync(fd); } catch { /* closed */ }
      this.closeDirectory(parent);
    }
  }

  writeNewFile(name: string, contents: string): void {
    if (name.includes('/') || name.includes('\\') || name === '.' || name === '..') throw new Error('unsafe-output-name');
    const fd = this.openAt(this.rootFd, name, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL, 0o600);
    try {
      const data = Buffer.from(contents, 'utf8');
      let written = 0;
      while (written < data.length) written += fs.writeSync(fd, data, written, data.length - written, written);
      fs.fsyncSync(fd);
      const stat = fs.fstatSync(fd, { bigint: true });
      if (!stat.isFile() || stat.size !== BigInt(data.length)) throw new Error('output-write-incomplete');
      this.assertRootStable();
    } finally { fs.closeSync(fd); }
  }

  createChildDirectory(name: string): AnchoredFs {
    if (name.includes('/') || name.includes('\\') || name === '.' || name === '..') throw new Error('unsafe-output-name');
    this.assertRootStable();
    try { fs.mkdirSync(`${this.prefix}/${this.rootFd}/${name}`, { mode: 0o700 }); }
    catch (error) { if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error; throw new Error('output-collision'); }
    const relativePath = path.join(this.rootPath, name);
    return AnchoredFs.openDirectory(relativePath, false);
  }

  close(): void {
    if (this.closed) return;
    this.closed = true;
    if (this.rootFd !== this.baseFd) try { fs.closeSync(this.rootFd); } catch { /* closed */ }
    try { fs.closeSync(this.baseFd); } catch { /* closed */ }
  }
}
