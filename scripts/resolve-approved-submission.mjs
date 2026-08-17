#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { posix, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

function fail(message) {
  throw new Error(message);
}

function readOption(args, name, { required = true } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) fail(`missing required option ${name}`);
    return null;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) {
    fail(`missing value for ${name}`);
  }
  return args[index + 1];
}

function normalizeFrozenPath(path) {
  const normalized = String(path ?? '').trim();
  if (!normalized) return null;
  if (
    normalized.startsWith('/')
    || normalized.includes('\\')
    || posix.normalize(normalized) !== normalized
    || normalized.split('/').some((segment) => !segment || segment === '.' || segment === '..')
  ) {
    fail(`invalid frozen path ${JSON.stringify(normalized)}`);
  }
  return normalized;
}

function ensureInsideRoot(repositoryRoot, absolutePath, label) {
  const relativePath = relative(repositoryRoot, absolutePath);
  if (relativePath === '' || relativePath.startsWith(`..${sep}`) || relativePath === '..') {
    fail(`${label} escapes repository root`);
  }
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`${label} is not valid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function sourceIdentity(report, label) {
  const sourceUrl = report?.meta?.source_url;
  const sourceRef = report?.meta?.source_ref;
  if (typeof sourceUrl !== 'string' || typeof sourceRef !== 'string' || sourceRef === '') {
    fail(`${label} is missing source_url or source_ref`);
  }
  let url;
  try {
    url = new URL(sourceUrl);
  } catch {
    fail(`${label} has an invalid source_url`);
  }
  if (url.protocol !== 'https:' || url.hostname !== 'github.com' || url.search || url.hash
    || url.username || url.password || url.port) {
    fail(`${label} source_url must be a plain HTTPS GitHub URL`);
  }
  let segments;
  try {
    segments = url.pathname.split('/').filter(Boolean).map(decodeURIComponent);
  } catch {
    fail(`${label} source_url contains invalid percent encoding`);
  }
  const [owner, repo, kind, encodedRef, ...skillPath] = segments;
  if (!owner || !repo || kind !== 'tree' || encodedRef !== sourceRef
    || skillPath.some((segment) => segment.includes('/'))
    || segments.some((segment) => segment === '.' || segment === '..' || segment.includes('\\') || /[\u0000-\u001f\u007f]/u.test(segment))) {
    fail(`${label} source_url does not match source_ref`);
  }
  const canonicalPath = `/${owner}/${repo}/tree/${encodeURIComponent(sourceRef)}${skillPath.length > 0
    ? `/${skillPath.map(encodeURIComponent).join('/')}`
    : ''}`;
  if (url.pathname !== canonicalPath && url.pathname !== `${canonicalPath}/`) {
    fail(`${label} source_url is not canonical`);
  }
  return {
    repository: `${owner}/${repo}`.toLowerCase(),
    path: skillPath.join('/'),
    ref: sourceRef,
  };
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function isSystemTempFile(name) {
  return name === '.DS_Store' || name.endsWith('~') || name.endsWith('.tmp') || name.endsWith('.temp');
}

function collectCanonicalEntries(repositoryRoot, directory, baseDirectory) {
  const absoluteDirectory = resolve(repositoryRoot, ...directory.split('/'));
  const entries = [];
  const dirents = readdirSync(absoluteDirectory, { withFileTypes: true })
    .filter((entry) => !isSystemTempFile(entry.name) && entry.name !== '.git')
    .sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'variant' }));
  for (const dirent of dirents) {
    const relativePath = `${directory}/${dirent.name}`;
    const treePath = relative(baseDirectory, relativePath).split(sep).join('/');
    const absolutePath = resolve(repositoryRoot, ...relativePath.split('/'));
    const fileStat = lstatSync(absolutePath);
    if (fileStat.isSymbolicLink() || (!fileStat.isDirectory() && !fileStat.isFile())) {
      fail(`pending tree contains an unsupported file type: ${relativePath}`);
    }
    if (fileStat.isDirectory()) {
      entries.push(...collectCanonicalEntries(repositoryRoot, relativePath, baseDirectory));
      continue;
    }
    if (treePath === 'skill-report.json') continue;
    const bytes = readFileSync(absolutePath);
    entries.push({
      path: treePath,
      mode: (fileStat.mode & 0o111) ? '100755' : '100644',
      sha256: createHash('sha256').update(bytes).digest('hex'),
      size: bytes.byteLength,
    });
  }
  return entries;
}

export function calculateCanonicalTreeHash(repositoryRoot, skillDirectory) {
  const entries = collectCanonicalEntries(repositoryRoot, skillDirectory, skillDirectory)
    .sort((a, b) => a.path.localeCompare(b.path, 'en', { sensitivity: 'variant' }));
  return createHash('sha256').update(entries.map((entry) => JSON.stringify(entry)).join('\n')).digest('hex');
}

function gitBuffer(repositoryRoot, args) {
  const result = spawnSync('git', ['-C', repositoryRoot, ...args], {
    encoding: 'buffer',
    maxBuffer: 100 * 1024 * 1024,
  });
  if (result.status !== 0) {
    fail(`git ${args.join(' ')} failed: ${result.stderr.toString('utf8').trim()}`);
  }
  return result.stdout;
}

export function calculateCanonicalTreeHashAtCommit(repositoryRoot, commit, skillDirectory) {
  const normalizedDirectory = normalizeFrozenPath(skillDirectory);
  if (!normalizedDirectory?.startsWith('skills/')) fail('committed skill directory must be under skills/');
  const resolvedCommit = gitBuffer(repositoryRoot, ['rev-parse', '--verify', `${commit}^{commit}`])
    .toString('utf8').trim();
  if (!/^[0-9a-f]{40}$/.test(resolvedCommit)) fail(`invalid resolved commit: ${resolvedCommit}`);
  const listing = gitBuffer(repositoryRoot, [
    'ls-tree', '-rz', '--full-tree', resolvedCommit, '--', normalizedDirectory,
  ]);
  let listingText;
  try {
    listingText = new TextDecoder('utf-8', { fatal: true }).decode(listing);
  } catch {
    fail(`committed skill tree contains a non-UTF-8 path: ${normalizedDirectory}`);
  }
  const entries = [];
  for (const record of listingText.split('\0').filter(Boolean)) {
    const tab = record.indexOf('\t');
    const header = record.slice(0, tab).split(' ');
    const path = record.slice(tab + 1);
    if (tab < 0 || header.length !== 3 || !path.startsWith(`${normalizedDirectory}/`)) {
      fail(`invalid committed tree entry for ${normalizedDirectory}`);
    }
    const [mode, type, object] = header;
    const treePath = path.slice(normalizedDirectory.length + 1);
    if (treePath === 'skill-report.json' || treePath.split('/').some(isSystemTempFile)
      || treePath.split('/').includes('.git')) continue;
    if (type !== 'blob' || !['100644', '100755'].includes(mode) || !/^[0-9a-f]{40,64}$/.test(object)) {
      fail(`committed skill tree contains an unsupported entry: ${path}`);
    }
    const bytes = gitBuffer(repositoryRoot, ['cat-file', 'blob', object]);
    entries.push({
      path: treePath,
      mode,
      sha256: createHash('sha256').update(bytes).digest('hex'),
      size: bytes.byteLength,
    });
  }
  entries.sort((a, b) => a.path.localeCompare(b.path, 'en', { sensitivity: 'variant' }));
  return createHash('sha256').update(entries.map((entry) => JSON.stringify(entry)).join('\n')).digest('hex');
}

function validateSegment(segment, label) {
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(segment) || segment === 'pending') {
    fail(`${label} contains invalid or reserved segment ${JSON.stringify(segment)}`);
  }
}

function listRegularFiles(repositoryRoot, directory) {
  const absoluteDirectory = resolve(repositoryRoot, ...directory.split('/'));
  const files = [];
  for (const entry of readdirSync(absoluteDirectory, { withFileTypes: true })) {
    const relativePath = `${directory}/${entry.name}`;
    const absolutePath = resolve(repositoryRoot, ...relativePath.split('/'));
    ensureInsideRoot(repositoryRoot, absolutePath, relativePath);
    const fileStat = lstatSync(absolutePath);
    if (fileStat.isSymbolicLink() || (!fileStat.isDirectory() && !fileStat.isFile())) {
      fail(`pending tree contains an unsupported file type: ${relativePath}`);
    }
    if (fileStat.isDirectory()) files.push(...listRegularFiles(repositoryRoot, relativePath));
    else files.push(relativePath);
  }
  return files.sort();
}

function rootFromSkillFile(path) {
  const segments = path.split('/');
  if (segments.at(-1) !== 'SKILL.md' || segments[0] !== 'pending') return null;
  if (segments.length !== 3 && segments.length !== 4) {
    fail(`pending SKILL.md must be pending/<skill>/SKILL.md or pending/<owner>/<skill>/SKILL.md: ${path}`);
  }
  for (const [index, segment] of segments.slice(1, -1).entries()) {
    validateSegment(segment, `pending path segment ${index + 1}`);
  }
  return segments.slice(0, -1).join('/');
}

export function resolveApprovedSubmission({ repositoryRoot, changedFiles }) {
  const root = realpathSync(repositoryRoot);
  const normalizedFiles = [...new Set(changedFiles.map(normalizeFrozenPath).filter(Boolean))].sort();
  const pendingFiles = normalizedFiles.filter((path) => path === 'pending' || path.startsWith('pending/'));
  if (pendingFiles.length === 0) fail('submission contains no pending files');

  const pendingRoots = [...new Set(pendingFiles.map(rootFromSkillFile).filter(Boolean))].sort();
  if (pendingRoots.length === 0) fail('submission contains no canonical pending SKILL.md');

  for (const path of pendingFiles) {
    const absolutePath = resolve(root, ...path.split('/'));
    ensureInsideRoot(root, absolutePath, path);
    if (!existsSync(absolutePath)) fail(`frozen pending file is missing after merge: ${path}`);
    const fileStat = lstatSync(absolutePath);
    if (!fileStat.isFile() || fileStat.isSymbolicLink()) {
      fail(`frozen pending path is not a regular file: ${path}`);
    }
  }

  for (const path of pendingFiles) {
    if (!pendingRoots.some((pendingRoot) => path === pendingRoot || path.startsWith(`${pendingRoot}/`))) {
      fail(`pending file is outside the frozen skill set: ${path}`);
    }
  }

  const frozenFileSet = new Set(pendingFiles);
  for (const pendingRoot of pendingRoots) {
    const unfrozen = listRegularFiles(root, pendingRoot).filter((path) => !frozenFileSet.has(path));
    if (unfrozen.length > 0) {
      fail(`${pendingRoot} contains file(s) outside the frozen PR/artifact set: ${unfrozen.slice(0, 5).join(', ')}`);
    }
  }

  const skills = pendingRoots.map((pendingDir) => {
    const segments = pendingDir.split('/');
    const sourceType = segments.length === 2 ? 'official' : 'community';
    const skillPath = resolve(root, pendingDir, 'SKILL.md');
    const reportPath = resolve(root, pendingDir, 'skill-report.json');
    ensureInsideRoot(root, skillPath, `${pendingDir}/SKILL.md`);
    ensureInsideRoot(root, reportPath, `${pendingDir}/skill-report.json`);
    if (!existsSync(skillPath) || !lstatSync(skillPath).isFile()) fail(`${pendingDir}/SKILL.md is missing`);
    if (!existsSync(reportPath) || !lstatSync(reportPath).isFile()) fail(`${pendingDir}/skill-report.json is missing`);
    if (lstatSync(skillPath).isSymbolicLink() || lstatSync(reportPath).isSymbolicLink()) {
      fail(`${pendingDir} contains a symlinked publication identity file`);
    }

    const report = readJson(reportPath, `${pendingDir}/skill-report.json`);
    if (report?.meta?.source_type !== sourceType) {
      fail(`${pendingDir} source_type does not match its pending path shape`);
    }
    if (typeof report?.meta?.slug !== 'string' || !/^[a-z0-9][a-z0-9-]*$/.test(report.meta.slug)) {
      fail(`${pendingDir} has an invalid report slug`);
    }
    const expectedSlug = sourceType === 'official'
      ? segments[1]
      : `${segments[1]}-${segments[2]}`;
    if (report.meta.slug !== expectedSlug) {
      fail(`${pendingDir} report slug does not match its publication path`);
    }
    const expectedContentHash = report?.meta?.content_hash;
    const actualContentHash = sha256(skillPath);
    if (!/^[0-9a-f]{64}$/.test(expectedContentHash ?? '') || expectedContentHash !== actualContentHash) {
      fail(`${pendingDir} report content_hash does not match SKILL.md raw bytes`);
    }
    const expectedTreeHash = report?.meta?.tree_hash;
    const actualTreeHash = calculateCanonicalTreeHash(root, pendingDir);
    if (!/^[0-9a-f]{64}$/.test(expectedTreeHash ?? '') || expectedTreeHash !== actualTreeHash) {
      fail(`${pendingDir} report tree_hash does not match the canonical skill tree`);
    }

    const targetDir = `skills/${segments.slice(1).join('/')}`;
    const targetPath = resolve(root, targetDir);
    let update = existsSync(targetPath);
    let duplicate = false;
    let previousSourceRef = null;
    if (update) {
      const targetStat = lstatSync(targetPath);
      if (targetStat.isSymbolicLink() || !targetStat.isDirectory()) {
        fail(`${targetDir} must be a non-symlink directory`);
      }
      const publishedReportPath = resolve(targetPath, 'skill-report.json');
      if (!existsSync(publishedReportPath) || lstatSync(publishedReportPath).isSymbolicLink()
        || !lstatSync(publishedReportPath).isFile()) {
        fail(`${targetDir}/skill-report.json is missing or unsafe`);
      }
      const publishedReport = readJson(publishedReportPath, `${targetDir}/skill-report.json`);
      const publishedTreeHash = calculateCanonicalTreeHash(root, targetDir);
      if (publishedReport?.meta?.tree_hash !== publishedTreeHash) {
        fail(`${targetDir} published tree_hash does not match the canonical skill tree`);
      }
      const nextIdentity = sourceIdentity(report, `${pendingDir}/skill-report.json`);
      const previousIdentity = sourceIdentity(publishedReport, `${targetDir}/skill-report.json`);
      duplicate = publishedTreeHash === actualTreeHash
        && report.meta.source_type === publishedReport?.meta?.source_type
        && report.meta.slug === publishedReport?.meta?.slug
        && nextIdentity.repository === previousIdentity.repository
        && nextIdentity.path === previousIdentity.path
        && /^[0-9a-f]{40}$/.test(nextIdentity.ref)
        && nextIdentity.ref === previousIdentity.ref;
      if (duplicate) {
        update = false;
      } else {
        const expectedPreviousTreeHash = report?.meta?.previous_tree_hash;
        const expectedPreviousSourceRef = report?.meta?.previous_source_ref;
        if (!/^[0-9a-f]{64}$/.test(expectedPreviousTreeHash ?? '')
          || typeof expectedPreviousSourceRef !== 'string' || expectedPreviousSourceRef === ''
          || publishedTreeHash !== expectedPreviousTreeHash
          || previousIdentity.ref !== expectedPreviousSourceRef) {
          fail(`${pendingDir} reviewed update snapshot does not match the published target`);
        }
        if (report.meta.source_type !== publishedReport?.meta?.source_type
          || report.meta.slug !== publishedReport?.meta?.slug
          || nextIdentity.repository !== previousIdentity.repository
          || nextIdentity.path !== previousIdentity.path) {
          fail(`${pendingDir} source identity does not match the published target`);
        }
        if (!/^[0-9a-f]{40}$/.test(nextIdentity.ref) || nextIdentity.ref === previousIdentity.ref) {
          fail(`${pendingDir} update must use a new immutable source commit`);
        }
        previousSourceRef = expectedPreviousSourceRef;
      }
    }
    return {
      contentHash: actualContentHash,
      duplicate,
      treeHash: actualTreeHash,
      pendingDir,
      reportSlug: report.meta.slug,
      sourceType,
      targetDir,
      update,
      previousSourceRef,
    };
  });

  const targets = new Set();
  const slugs = new Set();
  for (const skill of skills) {
    if (targets.has(skill.targetDir)) fail(`duplicate publication target ${skill.targetDir}`);
    if (slugs.has(skill.reportSlug)) fail(`duplicate report slug ${skill.reportSlug}`);
    targets.add(skill.targetDir);
    slugs.add(skill.reportSlug);
  }

  return { schemaVersion: 1, skills };
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes('--tree-hash-at-commit')) {
    process.stdout.write(`${calculateCanonicalTreeHashAtCommit(
      readOption(args, '--repo-root'),
      readOption(args, '--commit'),
      readOption(args, '--skill-dir'),
    )}\n`);
    return;
  }
  const repositoryRoot = readOption(args, '--repo-root');
  const filesPath = readOption(args, '--files');
  const outputPath = readOption(args, '--output');
  const changedFiles = readFileSync(filesPath, 'utf8').split(/\r?\n/).filter(Boolean);
  const plan = resolveApprovedSubmission({ repositoryRoot, changedFiles });
  writeFileSync(outputPath, `${JSON.stringify(plan, null, 2)}\n`, { mode: 0o600 });
  process.stdout.write(`Resolved ${plan.skills.length} frozen pending skill(s)\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Pending publication plan failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
