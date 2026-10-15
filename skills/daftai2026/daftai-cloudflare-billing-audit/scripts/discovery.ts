/**
 * [INPUT]: 依赖 node:fs、node:path、文件适配器与静态集合
 * [OUTPUT]: 提供 有界发现、敏感路径排除和限量读取
 * [POS]: 配置与源码读取之前的范围选择层
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import fs from 'node:fs';
import path from 'node:path';
import type { AuditReport } from './audit-types.ts';
import { CONFIG_NAMES, SOURCE_EXTENSIONS, EXCLUDED_DIRS } from './audit-types.ts';
import type { AuditFs } from './audit-fs.ts';
import type { StableStat } from './fs-common.ts';
import { statFingerprint } from './fs-common.ts';
export function isSensitivePath(name: string): boolean {
  const lower = name.toLowerCase();
  const extension = path.extname(lower);
  return lower.startsWith('.env') || lower === '.dev.vars' || lower === '.npmrc' ||
    /^\.?(?:secrets?|credentials?)(?:[._-]|$)/.test(lower) ||
    /(?:^|[._-])(?:secret|secrets|credential|credentials)(?:[._-]|$)/.test(lower) ||
    ['.pem', '.key', '.p12', '.pfx'].includes(extension);
}

function candidateKind(name: string): 'config' | 'source' | 'metadata' | 'sql' | 'workflow' | undefined {
  if (CONFIG_NAMES.has(name.toLowerCase())) return 'config';
  if (name.toLowerCase() === 'package.json') return 'metadata';
  if (isSensitivePath(name)) return undefined;
  const extension = path.extname(name).toLowerCase();
  if (SOURCE_EXTENSIONS.has(extension)) return 'source';
  if (extension === '.sql') return 'sql';
  if (extension === '.yaml' || extension === '.yml') return 'workflow';
  return undefined;
}

export type Candidate = { relative: string; kind: 'config' | 'source' | 'metadata' | 'sql' | 'workflow'; stat: StableStat; parentFingerprint: string };
export type DiscoveryResult = { candidates: Candidate[]; symlinks: number; excludedPaths: number; nonRegularFiles: number; unreadableDirectories: number; changedEntries: number; limitsHit: string[] };

export function discoverProject(tree: AuditFs, limits: AuditReport['limits']): DiscoveryResult {
  const candidates: DiscoveryResult['candidates'] = [];
  const limitsHit = new Set<string>();
  let symlinks = 0;
  let excludedPaths = 0;
  let nonRegularFiles = 0;
  let unreadableDirectories = 0;
  let changedEntries = 0;
  let visitedEntries = 0;

  const walk = (directory: string, depth: number, expected?: StableStat): void => {
    if (depth > limits.maxDepth) { limitsHit.add('max-depth'); return; }
    let listing: ReturnType<AuditFs['listDirectory']>;
    try { listing = tree.listDirectory(directory, Math.max(0, limits.maxEntries - visitedEntries), expected); }
    catch (error) {
      if (error instanceof Error && /path-changed|symlink-path/.test(error.message)) throw error;
      unreadableDirectories++;
      return;
    }
    let entries = listing.entries;
    visitedEntries += entries.length;
    if (listing.capped) limitsHit.add('max-entries');
    entries.sort((a, b) => {
      const priority = (entry: fs.Dirent): number => candidateKind(entry.name) === 'config' ? 0 : candidateKind(entry.name) === 'metadata' ? 1 : 2;
      const ak = priority(a);
      const bk = priority(b);
      return ak - bk || a.name.localeCompare(b.name);
    });
    for (const entry of entries) {
      const relative = directory === '.' ? entry.name : `${directory}/${entry.name}`;
      if (relative.split('/').some(isSensitivePath)) { excludedPaths++; continue; }
      if (entry.isSymbolicLink()) { symlinks++; continue; }
      if (entry.isDirectory()) {
        if (EXCLUDED_DIRS.has(entry.name.toLowerCase()) || isSensitivePath(entry.name)) { excludedPaths++; continue; }
        if (visitedEntries >= limits.maxEntries) { limitsHit.add('max-entries'); continue; }
        if (depth >= limits.maxDepth) { limitsHit.add('max-depth'); continue; }
        const childStatus = tree.inspectFile(relative);
        if (childStatus.status === 'symlink') { symlinks++; continue; }
        if (childStatus.status === 'missing' || childStatus.status === 'other') { changedEntries++; continue; }
        if (childStatus.status !== 'directory' || !childStatus.stat) { unreadableDirectories++; continue; }
        walk(relative, depth + 1, childStatus.stat);
        continue;
      }
      if (!entry.isFile() || isSensitivePath(entry.name)) {
        if (isSensitivePath(entry.name)) excludedPaths++;
        else nonRegularFiles++;
        continue;
      }
      const kind = candidateKind(entry.name);
      if (!kind) continue;
      if (kind === 'workflow' && !relative.startsWith('.github/workflows/')) continue;
      const info = tree.inspectFile(relative);
      if (info.status === 'symlink') { symlinks++; continue; }
      if (info.status === 'missing' || info.status === 'other') { changedEntries++; continue; }
      if (info.status !== 'file' || !info.stat || !info.parentFingerprint) { nonRegularFiles++; continue; }
      candidates.push({ relative, kind, stat: info.stat, parentFingerprint: info.parentFingerprint });
    }
  };

  walk('.', 0);
  candidates.sort((a, b) => {
    const rank = (kind: Candidate['kind']): number => kind === 'config' ? 0 : kind === 'metadata' ? 1 : kind === 'source' ? 2 : 3;
    return rank(a.kind) - rank(b.kind) || a.relative.localeCompare(b.relative);
  });
  return { candidates, symlinks, excludedPaths, nonRegularFiles, unreadableDirectories, changedEntries, limitsHit: [...limitsHit] };
}

export function readBounded(tree: AuditFs, candidate: Candidate, perFileLimit: number, remainingTotal: number): { text?: string; bytes?: number; sha256?: string; statFingerprint?: string; error?: string } {
  const effectiveLimit = Math.min(perFileLimit, remainingTotal);
  if (candidate.stat.size > BigInt(perFileLimit)) return { error: 'file-too-large' };
  if (candidate.stat.size > BigInt(effectiveLimit)) return { error: 'total-byte-limit' };
  const expected = { stat: candidate.stat, statFingerprint: statFingerprint(candidate.stat, candidate.parentFingerprint) };
  return tree.readFile(candidate.relative, effectiveLimit, expected);
}
