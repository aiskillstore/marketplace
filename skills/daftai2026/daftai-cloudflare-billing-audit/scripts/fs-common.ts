/**
 * [INPUT]: 依赖 node:fs、node:path 和 node:crypto
 * [OUTPUT]: 提供 路径包含判断、对象守卫与身份指纹
 * [POS]: 平台适配器共用的无状态原语
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
export function isWithin(parent: string, candidate: string): boolean {
  // macOS 的路径别名不能绕过目标内输出禁令；大小写敏感卷也保守拒绝。
  const relative = process.platform === 'darwin' ? path.relative(parent.toLowerCase(), candidate.toLowerCase()) : path.relative(parent, candidate);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

export function displayPath(root: string, absolute: string): string {
  const relative = path.relative(root, absolute).split(path.sep).join('/');
  return relative || '.';
}

export type DirectoryIdentity = { name: string; dev: string; ino: string; mode: string };
export type OpenDirectory = { fd: number; identities: DirectoryIdentity[] };
export type StableStat = fs.BigIntStats;

export function digest(value: string | Buffer): string {
  return createHash('sha256').update(value).digest('hex');
}

export function statIdentity(stat: StableStat): string {
  return [stat.dev, stat.ino, stat.mode, stat.size, stat.mtimeNs, stat.ctimeNs].join(':');
}

export function sameDirectory(stat: StableStat, identity: DirectoryIdentity): boolean {
  return stat.isDirectory() && !stat.isSymbolicLink() && String(stat.dev) === identity.dev && String(stat.ino) === identity.ino && String(stat.mode) === String(identity.mode);
}

export function identityOf(name: string, stat: StableStat): DirectoryIdentity {
  return { name, dev: String(stat.dev), ino: String(stat.ino), mode: String(stat.mode) };
}

export function isMissing(error: unknown): boolean {
  return (error as NodeJS.ErrnoException).code === 'ENOENT';
}

export function statFingerprint(stat: StableStat, parentFingerprint: string): string {
  return digest(`${statIdentity(stat)}|${parentFingerprint}`);
}

export function object(value: unknown): Record<string, unknown> | undefined {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : undefined;
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return object(value) !== undefined;
}
