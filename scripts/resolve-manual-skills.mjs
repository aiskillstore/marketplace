#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { posix } from 'node:path';
import { pathToFileURL } from 'node:url';
import { publishedSkillDirectory } from './detect-changed-skills.mjs';

const MAX_GIT_OUTPUT = 64 * 1024 * 1024;

function readOption(args, name) {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
    throw new Error(`missing required option ${name}`);
  }
  return args[index + 1];
}

function git(repositoryRoot, args, options = {}) {
  return execFileSync('git', args, {
    cwd: repositoryRoot,
    encoding: options.encoding ?? 'buffer',
    maxBuffer: MAX_GIT_OUTPUT,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

function resolveExactCommit(repositoryRoot, commit) {
  if (!/^[0-9a-f]{40}$/i.test(commit)) {
    throw new Error(`commit must be an exact 40-character SHA: ${commit}`);
  }

  const resolved = git(
    repositoryRoot,
    ['rev-parse', '--verify', `${commit}^{commit}`],
    { encoding: 'utf8' },
  ).trim();
  if (resolved.toLowerCase() !== commit.toLowerCase()) {
    throw new Error(`commit did not resolve exactly: ${commit}`);
  }
  return resolved;
}

export function parseManualSkillIdentifiers(rawSkills) {
  const identifiers = [...new Set(
    String(rawSkills ?? '')
      .split(/[\s,]+/)
      .map((value) => value.trim().replace(/^skills\//, '').replace(/\/skill-report\.json$/, ''))
      .filter(Boolean),
  )];
  if (identifiers.length === 0) throw new Error('no manual skill identifiers were provided');

  for (const identifier of identifiers) {
    const segments = identifier.split('/');
    if (
      identifier.startsWith('/')
      || identifier.includes('\\')
      || posix.normalize(identifier) !== identifier
      || segments.some((segment) => !segment || segment === '.' || segment === '..')
    ) {
      throw new Error(`invalid manual skill identifier: ${identifier}`);
    }
  }
  return identifiers;
}

function reportBlobsAtCommit(repositoryRoot, commit) {
  const output = git(repositoryRoot, [
    'ls-tree',
    '-r',
    '-z',
    '--full-tree',
    commit,
    '--',
    'skills',
  ]).toString('utf8');
  const reports = [];

  for (const record of output.split('\0')) {
    if (!record) continue;
    const tabIndex = record.indexOf('\t');
    if (tabIndex === -1) continue;
    const [mode, type, oid] = record.slice(0, tabIndex).split(' ');
    const treePath = record.slice(tabIndex + 1);
    if (
      type !== 'blob'
      || !mode.startsWith('100')
      || !treePath.startsWith('skills/')
      || posix.basename(treePath) !== 'skill-report.json'
    ) {
      continue;
    }
    publishedSkillDirectory(treePath);
    reports.push({ oid, treePath });
  }
  return reports;
}

function addMapping(index, key, relativePath) {
  if (!key) return;
  const existing = index.get(key);
  if (existing && existing !== relativePath) {
    index.set(key, null);
    return;
  }
  if (existing !== null) index.set(key, relativePath);
}

export function resolveManualSkillPaths({ repositoryRoot = '.', commit, skills }) {
  const exactCommit = resolveExactCommit(repositoryRoot, commit);
  const requested = Array.isArray(skills)
    ? parseManualSkillIdentifiers(skills.join(' '))
    : parseManualSkillIdentifiers(skills);
  const byPath = new Map();
  const bySlug = new Map();
  const reports = reportBlobsAtCommit(repositoryRoot, exactCommit);

  for (const report of reports) {
    const relativePath = posix.dirname(report.treePath).slice('skills/'.length);
    if (!relativePath || relativePath === '.') continue;
    addMapping(byPath, relativePath, relativePath);
    addMapping(bySlug, relativePath.replaceAll('/', '-'), relativePath);
  }

  if (requested.some((identifier) => !byPath.has(identifier) && !bySlug.has(identifier))) {
    for (const report of reports) {
      const relativePath = posix.dirname(report.treePath).slice('skills/'.length);
      try {
        const document = JSON.parse(
          git(repositoryRoot, ['cat-file', 'blob', report.oid], { encoding: 'utf8' }),
        );
        if (typeof document?.meta?.slug === 'string' && document.meta.slug.trim()) {
          addMapping(bySlug, document.meta.slug.trim(), relativePath);
        }
      } catch {
        // Path-derived lookup remains available for malformed legacy reports.
      }
    }
  }

  const resolved = [];
  const missing = [];
  const ambiguous = [];
  for (const identifier of requested) {
    const pathMatch = byPath.get(identifier);
    const slugMatch = bySlug.get(identifier);
    const match = pathMatch ?? slugMatch;
    if (pathMatch === null || slugMatch === null) {
      ambiguous.push(identifier);
    } else if (match) {
      resolved.push(match);
    } else {
      missing.push(identifier);
    }
  }

  if (ambiguous.length > 0) {
    throw new Error(`ambiguous skill identifier(s): ${ambiguous.join(', ')}`);
  }
  if (missing.length > 0) {
    throw new Error(`could not resolve skill identifier(s) at ${exactCommit}: ${missing.join(', ')}`);
  }
  return [...new Set(resolved)].sort();
}

function main() {
  const args = process.argv.slice(2);
  const commit = readOption(args, '--commit');
  const skills = readOption(args, '--skills');
  process.stdout.write(`${resolveManualSkillPaths({ commit, skills }).join(' ')}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`::error::Manual skill resolution failed: ${message}`);
    process.exitCode = 1;
  }
}
