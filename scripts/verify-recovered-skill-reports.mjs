#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { basename, join, relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
// Keep these contracts byte-for-byte compatible with Skillstore CLI v2.14.2
// src/cli/lib/content-hash.ts. The recovery was also cross-checked by invoking
// calculateCanonicalSkillHashes() from that release against all ten directories.
export const CANONICAL_CONTENT_HASH_SCHEME = 'skill_md_raw_bytes_v1';
export const CANONICAL_TREE_HASH_SCHEME = 'canonical_entries_v1';

export const RECOVERED_SKILL_REPORTS = Object.freeze([
  {
    path: 'skills/atomic-mail/atomicmail',
    slug: 'atomic-mail-atomicmail',
    sourceUrl: 'https://github.com/atomic-mail/atomic-mail-agentic/tree/main/integrations/skill/atomicmail',
  },
  {
    path: 'skills/skills-collective/ai-image-generation',
    slug: 'skills-collective-ai-image-generation',
    sourceUrl: 'https://github.com/skills-collective/skills/tree/main/ai-image-generation/',
  },
  {
    path: 'skills/skills-collective/ai-music',
    slug: 'skills-collective-ai-music',
    sourceUrl: 'https://github.com/skills-collective/skills/tree/main/ai-music/',
  },
  {
    path: 'skills/skills-collective/ai-video-generation',
    slug: 'skills-collective-ai-video-generation',
    sourceUrl: 'https://github.com/skills-collective/skills/tree/main/ai-video-generation/',
  },
  {
    path: 'skills/zx029w/laofang-gaizao-bucailei',
    slug: 'zx029w-laofang-gaizao-bucailei',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E8%80%81%E6%88%BF%E6%94%B9%E9%80%A0%E4%B8%8D%E8%B8%A9%E9%9B%B7/',
  },
  {
    path: 'skills/zx029w/quanwu-dingzhi-bucailei',
    slug: 'zx029w-quanwu-dingzhi-bucailei',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E5%85%A8%E5%B1%8B%E5%AE%9A%E5%88%B6%E4%B8%8D%E8%B8%A9%E9%9B%B7/',
  },
  {
    path: 'skills/zx029w/zhuangxiu-baojia-shenhe',
    slug: 'zx029w-zhuangxiu-baojia-shenhe',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E8%A3%85%E4%BF%AE%E6%8A%A5%E4%BB%B7%E5%AE%A1%E6%A0%B8/',
  },
  {
    path: 'skills/zx029w/zhuangxiu-hetong-shenhe',
    slug: 'zx029w-zhuangxiu-hetong-shenhe',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E8%A3%85%E4%BF%AE%E5%90%88%E5%90%8C%E5%AE%A1%E6%A0%B8/',
  },
  {
    path: 'skills/zx029w/zhuangxiu-yusuan-jisuanqi',
    slug: 'zx029w-zhuangxiu-yusuan-jisuanqi',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E8%A3%85%E4%BF%AE%E9%A2%84%E7%AE%97%E8%AE%A1%E7%AE%97%E5%99%A8/',
  },
  {
    path: 'skills/zx029w/zhuangxiu-zengxiang-bilei',
    slug: 'zx029w-zhuangxiu-zengxiang-bilei',
    sourceUrl: 'https://github.com/zx029w/zhuangxiu-skills/tree/main/%E8%A3%85%E4%BF%AE%E5%A2%9E%E9%A1%B9%E9%81%BF%E9%9B%B7/',
  },
]);

function fail(message) {
  throw new Error(message);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function toPosixPath(path) {
  return path.split(/[\\/]+/).filter(Boolean).join('/');
}

function isSystemTempFile(name) {
  return name === '.DS_Store' || name.endsWith('~') || name.endsWith('.tmp') || name.endsWith('.temp');
}

function gitMode(mode) {
  return (mode & 0o111) ? '100755' : '100644';
}

function countLines(bytes) {
  if (bytes.length === 0) return 0;
  let lines = 1;
  for (const byte of bytes) {
    if (byte === 10) lines += 1;
  }
  return lines;
}

function collectCanonicalEntries(directory, baseDirectory = directory) {
  const dirents = readdirSync(directory, { withFileTypes: true })
    .filter((entry) => !isSystemTempFile(entry.name) && entry.name !== '.git')
    .sort((left, right) => left.name.localeCompare(right.name, 'en', { sensitivity: 'variant' }));
  const entries = [];

  for (const dirent of dirents) {
    const fullPath = join(directory, dirent.name);
    const relativePath = toPosixPath(relative(baseDirectory, fullPath));
    const stat = lstatSync(fullPath);
    if (dirent.isSymbolicLink() || (!dirent.isDirectory() && !dirent.isFile())) {
      fail(`unsupported file type in canonical tree: ${relativePath}`);
    }
    if (dirent.isDirectory()) {
      entries.push(...collectCanonicalEntries(fullPath, baseDirectory));
      continue;
    }
    if (relativePath === 'skill-report.json') continue;
    const bytes = readFileSync(fullPath);
    entries.push({
      path: relativePath,
      mode: gitMode(stat.mode),
      sha256: sha256(bytes),
      size: bytes.byteLength,
    });
  }
  return entries;
}

export function calculateCanonicalSkillHashes(skillDirectory) {
  const skillBytes = readFileSync(join(skillDirectory, 'SKILL.md'));
  const entries = collectCanonicalEntries(skillDirectory)
    .sort((left, right) => left.path.localeCompare(right.path, 'en', { sensitivity: 'variant' }));
  const serialized = entries.map((entry) => JSON.stringify(entry)).join('\n');
  return {
    contentHash: sha256(skillBytes),
    treeHash: sha256(serialized),
    entries,
  };
}

function frontmatterName(skillBytes, label) {
  const skill = skillBytes.toString('utf8');
  const frontmatter = skill.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
  const rawName = frontmatter?.match(/^name:\s*(.+?)\s*$/m)?.[1];
  const name = rawName?.replace(/^(['"])(.*)\1$/, '$2');
  if (!name || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) {
    fail(`${label} has no canonical frontmatter name`);
  }
  return name;
}

function validateReportedFileStructure(skillDirectory, nodes, label, seen = new Set()) {
  if (!Array.isArray(nodes)) fail(`${label} file_structure is not an array`);
  for (const node of nodes) {
    const path = toPosixPath(String(node?.path || ''));
    if (!path || path.startsWith('../') || path === 'skill-report.json' || seen.has(path)) {
      fail(`${label} has an invalid or duplicate file_structure path: ${path || '<missing>'}`);
    }
    seen.add(path);
    if (node.name !== basename(path)) fail(`${label} file_structure name/path mismatch: ${path}`);
    const fullPath = resolve(skillDirectory, path);
    if (!fullPath.startsWith(`${resolve(skillDirectory)}/`)) fail(`${label} file_structure escapes its Skill: ${path}`);
    const stat = lstatSync(fullPath);
    if (stat.isSymbolicLink()) fail(`${label} file_structure contains a symlink: ${path}`);
    if (node.type === 'dir') {
      if (!stat.isDirectory()) fail(`${label} expected directory: ${path}`);
      if (node.children !== undefined) {
        validateReportedFileStructure(skillDirectory, node.children, label, seen);
      }
    } else if (node.type === 'file') {
      if (!stat.isFile()) fail(`${label} expected file: ${path}`);
      if (node.lines !== countLines(readFileSync(fullPath))) {
        fail(`${label} line count does not match bytes: ${path}`);
      }
    } else {
      fail(`${label} has an invalid file_structure type: ${path}`);
    }
  }
  return seen;
}

export function verifyRecoveredSkillReport(repositoryRoot, target) {
  const skillDirectory = resolve(repositoryRoot, target.path);
  const skillBytes = readFileSync(join(skillDirectory, 'SKILL.md'));
  const report = JSON.parse(readFileSync(join(skillDirectory, 'skill-report.json'), 'utf8'));
  const owner = target.path.split('/')[1];
  const directoryName = basename(skillDirectory);
  const name = frontmatterName(skillBytes, target.path);
  const expectedSlug = `${owner}-${name}`;
  const source = new URL(String(report.meta?.source_url || ''));
  const canonical = calculateCanonicalSkillHashes(skillDirectory);

  if (directoryName !== name) fail(`${target.path} directory does not match SKILL.md name`);
  if (target.slug !== expectedSlug || report.meta?.slug !== expectedSlug) {
    fail(`${target.path} does not use canonical community slug ${expectedSlug}`);
  }
  if (report.meta?.source_url !== target.sourceUrl) fail(`${target.path} source_url mismatch`);
  if (source.hostname !== 'github.com' || decodeURIComponent(source.pathname).split('/')[1] !== owner) {
    fail(`${target.path} source owner mismatch`);
  }
  if (report.meta?.source_ref !== 'main' || report.meta?.source_type !== 'community') {
    fail(`${target.path} source metadata mismatch`);
  }
  if (!SHA256_RE.test(String(report.meta?.content_hash || ''))
    || report.meta.content_hash !== canonical.contentHash) {
    fail(`${target.path} content_hash does not match exact SKILL.md bytes`);
  }
  if (!SHA256_RE.test(String(report.meta?.tree_hash || ''))
    || report.meta.tree_hash !== canonical.treeHash) {
    fail(`${target.path} tree_hash does not match canonical source paths and bytes`);
  }
  if (report.security_audit?.analysis_status !== 'ok') {
    fail(`${target.path} lacks a successful audit report`);
  }
  validateReportedFileStructure(skillDirectory, report.file_structure, target.path);

  return {
    path: target.path,
    slug: expectedSlug,
    sourceUrl: target.sourceUrl,
    contentHash: canonical.contentHash,
    contentHashScheme: CANONICAL_CONTENT_HASH_SCHEME,
    treeHash: canonical.treeHash,
    treeHashScheme: CANONICAL_TREE_HASH_SCHEME,
    entryCount: canonical.entries.length,
  };
}

function collectReportSlugPaths(directory, results = new Map()) {
  for (const dirent of readdirSync(directory, { withFileTypes: true })) {
    if (!dirent.isDirectory()) continue;
    const child = join(directory, dirent.name);
    const reportPath = join(child, 'skill-report.json');
    try {
      const report = JSON.parse(readFileSync(reportPath, 'utf8'));
      const slug = report.meta?.slug;
      if (typeof slug === 'string' && slug) {
        const paths = results.get(slug) || [];
        paths.push(reportPath);
        results.set(slug, paths);
      }
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
      collectReportSlugPaths(child, results);
    }
  }
  return results;
}

export function verifyRecoveredSkillReports(repositoryRoot) {
  const results = RECOVERED_SKILL_REPORTS.map((target) =>
    verifyRecoveredSkillReport(repositoryRoot, target));
  const uniqueSlugs = new Set(results.map((row) => row.slug));
  if (uniqueSlugs.size !== RECOVERED_SKILL_REPORTS.length) {
    fail('recovered reports do not have ten unique canonical slugs');
  }
  const repositorySlugs = collectReportSlugPaths(resolve(repositoryRoot, 'skills'));
  for (const row of results) {
    const matches = repositorySlugs.get(row.slug) || [];
    if (matches.length !== 1 || !matches[0].endsWith(`${row.path}/skill-report.json`)) {
      fail(`${row.slug} is not unique at its canonical repository path`);
    }
  }
  return results;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const repositoryRoot = resolve(process.argv[2] || '.');
  console.log(JSON.stringify({
    schemaVersion: 1,
    verifiedCount: RECOVERED_SKILL_REPORTS.length,
    results: verifyRecoveredSkillReports(repositoryRoot),
  }, null, 2));
}
