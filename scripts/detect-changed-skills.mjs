#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { posix } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_DIGEST_RE = /^sha256:[0-9a-f]{64}$/;
const SHA_RE = /^[0-9a-f]{40}$/;
const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

function readOption(args, name) {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
    throw new Error(`missing required option ${name}`);
  }
  return args[index + 1];
}

function gitPaths(repositoryRoot, args) {
  const output = execFileSync('git', args, {
    cwd: repositoryRoot,
    encoding: 'buffer',
    maxBuffer: 64 * 1024 * 1024,
  });
  return output.toString('utf8').split('\0').filter(Boolean);
}

function gitText(repositoryRoot, args) {
  return execFileSync('git', args, {
    cwd: repositoryRoot,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}

function exactCommit(repositoryRoot, commit, label) {
  if (!SHA_RE.test(commit)) throw new Error(`${label} is not an exact commit SHA`);
  const resolved = gitText(repositoryRoot, ['rev-parse', '--verify', `${commit}^{commit}`]);
  if (resolved !== commit) throw new Error(`${label} did not resolve exactly`);
  return resolved;
}

function isAncestor(repositoryRoot, ancestor, head) {
  try {
    execFileSync('git', ['merge-base', '--is-ancestor', ancestor, head], {
      cwd: repositoryRoot,
      stdio: 'ignore',
    });
    return true;
  } catch {
    return false;
  }
}

function treeObject(repositoryRoot, commit, skillPath) {
  try {
    const oid = gitText(repositoryRoot, ['rev-parse', '--verify', `${commit}:skills/${skillPath}`]);
    return gitText(repositoryRoot, ['cat-file', '-t', oid]) === 'tree' ? oid : null;
  } catch {
    return null;
  }
}

function reportSlug(repositoryRoot, commit, skillPath) {
  try {
    const report = JSON.parse(gitText(repositoryRoot, [
      'show',
      `${commit}:skills/${skillPath}/skill-report.json`,
    ]));
    return typeof report?.meta?.slug === 'string' && SLUG_RE.test(report.meta.slug)
      ? report.meta.slug
      : null;
  } catch {
    return null;
  }
}

export function publishedSkillDirectory(reportPath) {
  if (!reportPath.startsWith('skills/') || posix.basename(reportPath) !== 'skill-report.json') {
    return null;
  }
  const segments = reportPath.split('/');
  if (segments.length !== 3 && segments.length !== 4) {
    throw new Error(`published skill report has invalid path depth: ${reportPath}`);
  }
  const identitySegments = segments.slice(1, -1);
  if (
    identitySegments.includes('pending')
    || identitySegments.some((segment) => !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(segment))
  ) {
    throw new Error(`published skill report has invalid or reserved path identity: ${reportPath}`);
  }
  return identitySegments.join('/');
}

export function resolveChangedSkillPaths(changedPaths, reportPaths) {
  const published = new Set(reportPaths.map(publishedSkillDirectory).filter(Boolean));
  const changedSkills = new Set();

  for (const changedPath of changedPaths) {
    if (!changedPath.startsWith('skills/')) continue;

    let directory = posix.dirname(changedPath.slice('skills/'.length));
    while (directory && directory !== '.') {
      if (published.has(directory)) {
        changedSkills.add(directory);
        break;
      }
      const parent = posix.dirname(directory);
      if (parent === directory) break;
      directory = parent;
    }
  }

  return [...changedSkills].sort();
}

export function detectChangedSkillPathsFromGit({ repositoryRoot = '.', base, head }) {
  const changedPaths = gitPaths(repositoryRoot, [
    'diff',
    '--name-only',
    '-z',
    base,
    head,
    '--',
    'skills',
  ]);
  const headPaths = gitPaths(repositoryRoot, [
    'ls-tree',
    '-r',
    '--name-only',
    '-z',
    head,
    '--',
    'skills',
  ]);

  return resolveChangedSkillPaths(changedPaths, headPaths);
}

export function filterRecoveredSkillPathsFromGit({
  repositoryRoot = '.',
  head,
  skillPaths,
  recoveries,
}) {
  const exactHead = exactCommit(repositoryRoot, head, 'head');
  if (!Array.isArray(skillPaths) || !Array.isArray(recoveries) || recoveries.length > 100) {
    throw new Error('recovery filter input is invalid or exceeds 100 runs');
  }

  const headsBySlug = new Map();
  for (const recovery of recoveries) {
    if (!Number.isSafeInteger(recovery?.runId) || recovery.runId <= 0
      || !Number.isSafeInteger(recovery?.artifactId) || recovery.artifactId <= 0
      || !SHA256_DIGEST_RE.test(recovery?.digest ?? '')
      || !Array.isArray(recovery?.slugs)
      || recovery.slugs.length === 0
      || recovery.slugs.length > 25) {
      throw new Error('recovery manifest contains invalid run or artifact evidence');
    }
    const recoveryHead = exactCommit(repositoryRoot, recovery.headSha, `recovery run ${recovery.runId} head`);
    if (!isAncestor(repositoryRoot, recoveryHead, exactHead)) continue;

    const uniqueSlugs = new Set();
    for (const slug of recovery.slugs) {
      if (typeof slug !== 'string' || !SLUG_RE.test(slug)) {
        throw new Error(`invalid recovery slug in run ${recovery.runId}`);
      }
      if (uniqueSlugs.has(slug)) throw new Error(`duplicate recovery slug in run ${recovery.runId}: ${slug}`);
      uniqueSlugs.add(slug);
      if (!headsBySlug.has(slug)) headsBySlug.set(slug, new Set());
      headsBySlug.get(slug).add(recoveryHead);
    }
  }

  return [...new Set(skillPaths)].filter((skillPath) => {
    if (publishedSkillDirectory(`skills/${skillPath}/skill-report.json`) !== skillPath) {
      throw new Error(`invalid changed skill path: ${skillPath}`);
    }
    const slug = reportSlug(repositoryRoot, exactHead, skillPath);
    const currentTree = treeObject(repositoryRoot, exactHead, skillPath);
    if (!slug || !currentTree) return true;
    return ![...(headsBySlug.get(slug) ?? [])]
      .some((recoveryHead) => treeObject(repositoryRoot, recoveryHead, skillPath) === currentTree);
  }).sort();
}

function main() {
  const args = process.argv.slice(2);
  const base = readOption(args, '--base');
  const head = readOption(args, '--head');
  const recoveriesIndex = args.indexOf('--recoveries');
  const recoveriesPath = recoveriesIndex >= 0 ? args[recoveriesIndex + 1] : null;
  if (recoveriesIndex >= 0 && (!recoveriesPath || recoveriesPath.startsWith('--'))) {
    throw new Error('missing required option --recoveries');
  }
  const detected = detectChangedSkillPathsFromGit({ base, head });
  const changedSkills = recoveriesPath
    ? filterRecoveredSkillPathsFromGit({
        head,
        skillPaths: detected,
        recoveries: JSON.parse(readFileSync(recoveriesPath, 'utf8')),
      })
    : detected;
  process.stdout.write(`${changedSkills.join(' ')}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`::error::Incremental skill detection failed: ${message}`);
    process.exitCode = 1;
  }
}
