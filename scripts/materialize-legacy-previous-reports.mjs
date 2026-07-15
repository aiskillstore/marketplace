#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const COMMIT_RE = /^[0-9a-f]{40}$/;
const MAX_GIT_OUTPUT = 64 * 1024 * 1024;

function fail(message) {
  throw new Error(message);
}

function git(repositoryRoot, args, encoding = 'utf8') {
  try {
    return execFileSync('git', ['-C', repositoryRoot, ...args], {
      encoding,
      maxBuffer: MAX_GIT_OUTPUT,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (error) {
    const detail = error.stderr?.toString().trim() || error.message;
    fail(`Git evidence read failed (${args.join(' ')}): ${detail}`);
  }
}

function safeSkillPath(value) {
  if (typeof value !== 'string' || value !== value.trim()) {
    fail('plan contains a non-canonical Skill path');
  }
  const segments = value.split('/');
  if (
    !value.startsWith('skills/')
    || value.startsWith('/')
    || value.includes('\\')
    || /[\u0000-\u001f\u007f,?#]/.test(value)
    || segments.some((segment) => !segment || segment === '.' || segment === '..')
  ) {
    fail(`plan contains an unsafe Skill path: ${value || '<empty>'}`);
  }
  return value;
}

function exactCommit(repositoryRoot, value) {
  if (typeof value !== 'string' || !COMMIT_RE.test(value)) {
    fail(`plan contains an invalid exact commit: ${value ?? '<missing>'}`);
  }
  const resolved = git(repositoryRoot, ['rev-parse', '--verify', `${value}^{commit}`]).trim();
  if (resolved !== value) fail(`commit did not resolve exactly: ${value}`);
  return value;
}

function firstParent(repositoryRoot, commit) {
  const fields = git(repositoryRoot, ['rev-list', '--parents', '-n', '1', commit]).trim().split(' ');
  if (fields[0] !== commit || fields.length < 2 || fields.some((field) => !COMMIT_RE.test(field))) {
    fail(`commit has no valid first parent: ${commit}`);
  }
  return fields[1];
}

function readPreviousReport(repositoryRoot, parentCommit, skillPath) {
  const reportPath = `${skillPath}/skill-report.json`;
  const output = git(repositoryRoot, [
    'ls-tree',
    '-z',
    '--full-tree',
    parentCommit,
    '--',
    reportPath,
  ], 'buffer');
  if (output.length === 0) return null;

  const records = output.toString('utf8').split('\0').filter(Boolean);
  if (records.length !== 1) fail(`ambiguous previous report tree entry: ${parentCommit}:${reportPath}`);
  const tab = records[0].indexOf('\t');
  const metadata = tab === -1 ? [] : records[0].slice(0, tab).split(' ');
  const treePath = tab === -1 ? '' : records[0].slice(tab + 1);
  const [mode, type, objectId] = metadata;
  if (
    treePath !== reportPath
    || type !== 'blob'
    || !/^100[0-7]{3}$/.test(mode || '')
    || !/^[0-9a-f]{40,64}$/.test(objectId || '')
  ) {
    fail(`previous report is not an ordinary Git file: ${parentCommit}:${reportPath}`);
  }
  return git(repositoryRoot, ['cat-file', 'blob', objectId], 'buffer');
}

function assertUnusedOutput(outputRoot, manifestPath) {
  if (existsSync(manifestPath)) fail(`manifest output already exists: ${manifestPath}`);
  if (existsSync(outputRoot) && readdirSync(outputRoot).length > 0) {
    fail(`previous-report output root is not empty: ${outputRoot}`);
  }
}

function safeOutputPath(outputRoot, batchIndex, commit, skillPath) {
  const relative = `batch-${batchIndex}/${commit}/${skillPath}/skill-report.json`;
  const target = resolve(outputRoot, ...relative.split('/'));
  if (!target.startsWith(`${outputRoot}${sep}`)) fail(`refusing output path outside root: ${relative}`);
  return target;
}

function validatePlan(plan, repositoryRoot) {
  if (
    !plan
    || !Array.isArray(plan.selected)
    || !Array.isArray(plan.batches)
    || !Number.isSafeInteger(plan.selectedCount)
    || plan.selectedCount < 0
    || plan.selectedCount !== plan.selected.length
  ) {
    fail('plan does not contain one complete selected cohort');
  }

  const selectedByPath = new Map();
  const selectedSlugs = new Set();
  for (const row of plan.selected) {
    const path = safeSkillPath(row?.path);
    const commit = exactCommit(repositoryRoot, row?.marketplaceCommit);
    if (
      typeof row?.slug !== 'string'
      || !row.slug
      || row.slug !== row.slug.trim()
      || /[\u0000-\u001f\u007f,\s]/.test(row.slug)
      || selectedSlugs.has(row.slug)
    ) {
      fail(`plan contains an invalid or duplicate slug: ${row?.slug ?? '<missing>'}`);
    }
    if (selectedByPath.has(path)) fail(`plan contains duplicate Skill path: ${path}`);
    selectedSlugs.add(row.slug);
    selectedByPath.set(path, { path, slug: row.slug, currentCommit: commit });
  }

  const coveredPaths = new Set();
  const groups = [];
  const batchIndexes = new Set();
  const groupKeys = new Set();
  for (const batch of plan.batches) {
    if (!Number.isSafeInteger(batch?.index) || batch.index < 1 || batchIndexes.has(batch.index)) {
      fail(`plan contains an invalid or duplicate batch index: ${batch?.index ?? '<missing>'}`);
    }
    batchIndexes.add(batch.index);
    if (!Array.isArray(batch.groups)) fail(`plan batch ${batch.index} has no groups`);
    let batchCount = 0;
    for (const group of batch.groups) {
      const commit = exactCommit(repositoryRoot, group?.marketplaceCommit);
      const groupKey = `${batch.index}:${commit}`;
      if (groupKeys.has(groupKey)) fail(`plan contains duplicate group: ${groupKey}`);
      groupKeys.add(groupKey);
      if (!Number.isSafeInteger(group.count) || group.count < 1
          || !Array.isArray(group.paths) || !Array.isArray(group.slugs) || group.count !== group.paths.length
          || group.count !== group.slugs.length) {
        fail(`plan group ${batch.index}/${commit} is incomplete`);
      }
      const paths = group.paths.map(safeSkillPath);
      for (let index = 0; index < paths.length; index++) {
        const path = paths[index];
        const selected = selectedByPath.get(path);
        if (
          !selected
          || selected.currentCommit !== commit
          || selected.slug !== group.slugs[index]
          || coveredPaths.has(path)
        ) {
          fail(`plan group coverage mismatch for ${path}`);
        }
        coveredPaths.add(path);
      }
      batchCount += group.count;
      groups.push({ batchIndex: batch.index, currentCommit: commit, paths });
    }
    if (batch.count !== batchCount) fail(`plan batch ${batch.index} count does not match its groups`);
  }
  if (coveredPaths.size !== selectedByPath.size) fail('plan groups do not cover selected paths exactly once');
  return groups;
}

export function materializeLegacyPreviousReports({
  repositoryRoot,
  plan,
  outputRoot,
  manifestPath,
}) {
  const root = resolve(repositoryRoot);
  const destination = resolve(outputRoot);
  const manifest = resolve(manifestPath);
  if (destination === resolve('/') || manifest === destination || manifest.startsWith(`${destination}${sep}`)) {
    fail('previous-report root and manifest outputs must be separate safe paths');
  }
  assertUnusedOutput(destination, manifest);
  const groups = validatePlan(plan, root);

  // Read and hash the complete cohort before creating any output.
  const pending = [];
  for (const group of groups) {
    const parentCommit = firstParent(root, group.currentCommit);
    for (const path of group.paths) {
      const contents = readPreviousReport(root, parentCommit, path);
      pending.push({
        batchIndex: group.batchIndex,
        path,
        currentCommit: group.currentCommit,
        parentCommit,
        present: contents !== null,
        sha256: contents === null ? null : createHash('sha256').update(contents).digest('hex'),
        contents,
      });
    }
  }
  pending.sort((left, right) => left.path < right.path ? -1 : left.path > right.path ? 1 : 0);

  mkdirSync(destination, { recursive: true });
  for (const group of groups) {
    const groupRoot = resolve(destination, `batch-${group.batchIndex}`, group.currentCommit);
    if (!groupRoot.startsWith(`${destination}${sep}`)) fail('refusing group output outside root');
    mkdirSync(groupRoot, { recursive: true });
  }
  for (const entry of pending) {
    if (entry.contents === null) continue;
    const target = safeOutputPath(
      destination,
      entry.batchIndex,
      entry.currentCommit,
      entry.path,
    );
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, entry.contents, { flag: 'wx', mode: 0o600 });
  }
  const output = {
    schemaVersion: 1,
    status: 'legacy_previous_reports_materialized',
    selectedCount: pending.length,
    entries: pending.map(({ contents: _contents, batchIndex: _batchIndex, ...entry }) => entry),
  };
  mkdirSync(dirname(manifest), { recursive: true });
  writeFileSync(manifest, `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx', mode: 0o600 });
  return output;
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null || value.startsWith('--')) {
      fail(`invalid argument: ${key || '<missing>'}`);
    }
    const name = key.slice(2);
    if (Object.hasOwn(values, name)) fail(`duplicate argument: ${key}`);
    values[name] = value;
  }
  return values;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  for (const name of ['plan', 'output-root', 'manifest']) {
    if (!args[name]) fail(`--${name} is required`);
  }
  const output = materializeLegacyPreviousReports({
    repositoryRoot: args['repository-root'] || process.cwd(),
    plan: JSON.parse(readFileSync(resolve(args.plan), 'utf8')),
    outputRoot: args['output-root'],
    manifestPath: args.manifest,
  });
  process.stdout.write(`${JSON.stringify({ status: output.status, selectedCount: output.selectedCount })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`legacy previous-report materialization failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
