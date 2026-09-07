#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  cpSync,
  lstatSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
} from 'node:fs';
import { basename, dirname, join, posix, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import { calculateCanonicalTreeHash } from './resolve-approved-submission.mjs';

function fail(message) {
  throw new Error(message);
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index === -1) fail(`missing required option ${name}`);
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

function normalizePendingDir(value) {
  if (typeof value !== 'string' || value === '' || value.includes('\\')
    || posix.normalize(value) !== value) {
    fail(`invalid pending directory: ${JSON.stringify(value)}`);
  }
  const segments = value.split('/');
  if (segments.length !== 3 || segments[0] !== 'pending'
    || segments.some((segment) => segment === '' || segment === '.' || segment === '..'
      || /[\u0000-\u001f\u007f]/u.test(segment))) {
    fail(`pending directory must be a canonical community path: ${value}`);
  }
  return value;
}

function git(repositoryRoot, args) {
  const result = spawnSync('git', ['-C', repositoryRoot, ...args], {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
  });
  if (result.status !== 0) {
    fail(`git ${args.join(' ')} failed: ${result.stderr.trim()}`);
  }
  return result.stdout.trim();
}

export function calculatePendingGitTreeOidAtCommit(repositoryRoot, commit, pendingDir) {
  const normalizedPendingDir = normalizePendingDir(pendingDir);
  const resolvedCommit = git(repositoryRoot, ['rev-parse', '--verify', `${commit}^{commit}`]);
  if (!/^[a-f0-9]{40,64}$/.test(resolvedCommit)) fail(`invalid resolved commit: ${resolvedCommit}`);
  const treeOid = git(repositoryRoot, [
    'rev-parse', '--verify', `${resolvedCommit}:${normalizedPendingDir}`,
  ]);
  if (!/^[a-f0-9]{40,64}$/.test(treeOid)
    || git(repositoryRoot, ['cat-file', '-t', treeOid]) !== 'tree') {
    fail(`committed pending path is not a Git tree: ${normalizedPendingDir}`);
  }
  return treeOid;
}

function assertDirectory(path, label) {
  let stat;
  try {
    stat = lstatSync(path);
  } catch (error) {
    if (error?.code === 'ENOENT') fail(`${label} is missing: ${path}`);
    throw error;
  }
  if (stat.isSymbolicLink() || !stat.isDirectory()) {
    fail(`${label} must be a non-symlink directory: ${path}`);
  }
}

function assertRegularFile(path, label) {
  let stat;
  try {
    stat = lstatSync(path);
  } catch (error) {
    if (error?.code === 'ENOENT') fail(`${label} is missing: ${path}`);
    throw error;
  }
  if (stat.isSymbolicLink() || !stat.isFile()) {
    fail(`${label} must be a non-symlink regular file: ${path}`);
  }
}

function resolveSafeDirectory(rootPath, relativePath, label) {
  const root = resolve(rootPath);
  assertDirectory(root, `${label} root`);
  let current = root;
  for (const segment of relativePath.split('/')) {
    current = join(current, segment);
    assertDirectory(current, label);
  }
  return current;
}

function assertSafeTree(directory, label) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    const stat = lstatSync(path);
    if (stat.isSymbolicLink() || (!stat.isDirectory() && !stat.isFile())) {
      fail(`${label} contains an unsupported file type: ${path}`);
    }
    if (stat.isDirectory()) assertSafeTree(path, label);
  }
}

function fileSha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function readSourceRef(reportPath, label) {
  let report;
  try {
    report = JSON.parse(readFileSync(reportPath, 'utf8'));
  } catch (error) {
    fail(`${label} is malformed JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (typeof report?.meta?.source_ref !== 'string' || report.meta.source_ref === '') {
    fail(`${label} is missing meta.source_ref`);
  }
  return report.meta.source_ref;
}

export function replacePendingSubmission({
  repositoryRoot,
  mergedResults,
  pendingDir,
  expectedTreeHash,
  expectedReportHash,
  expectedGitTreeOid,
  expectedSourceRef,
}) {
  const normalizedPendingDir = normalizePendingDir(pendingDir);
  for (const [value, label] of [
    [expectedTreeHash, 'expected tree hash'],
    [expectedReportHash, 'expected report hash'],
  ]) {
    if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail(`${label} is invalid`);
  }
  if (typeof expectedGitTreeOid !== 'string' || !/^[a-f0-9]{40,64}$/.test(expectedGitTreeOid)) {
    fail('expected Git tree OID is invalid');
  }
  if (typeof expectedSourceRef !== 'string' || expectedSourceRef === '') {
    fail('expected source ref must be a non-empty string');
  }

  const destination = resolveSafeDirectory(repositoryRoot, normalizedPendingDir, 'pending update target');
  const destinationReport = join(destination, 'skill-report.json');
  assertRegularFile(destinationReport, 'pending update report');
  assertSafeTree(destination, 'pending update target');

  if (calculatePendingGitTreeOidAtCommit(repositoryRoot, 'HEAD', normalizedPendingDir) !== expectedGitTreeOid) {
    fail(`pending update Git tree changed after classification: ${normalizedPendingDir}`);
  }
  if (calculateCanonicalTreeHash(repositoryRoot, normalizedPendingDir) !== expectedTreeHash) {
    fail(`pending update target changed after classification: ${normalizedPendingDir}`);
  }
  if (fileSha256(destinationReport) !== expectedReportHash) {
    fail(`pending update report changed after classification: ${normalizedPendingDir}`);
  }
  if (readSourceRef(destinationReport, 'pending update report') !== expectedSourceRef) {
    fail(`pending update source ref changed after classification: ${normalizedPendingDir}`);
  }

  const replacementSource = resolveSafeDirectory(mergedResults, normalizedPendingDir, 'replacement pending target');
  const replacementReport = join(replacementSource, 'skill-report.json');
  assertRegularFile(replacementReport, 'replacement pending report');
  assertSafeTree(replacementSource, 'replacement pending target');

  const destinationParent = dirname(destination);
  const temporaryRoot = mkdtempSync(join(destinationParent, `.${basename(destination)}-replacement-`));
  const replacement = join(temporaryRoot, 'replacement');
  const previous = join(temporaryRoot, 'previous');
  let previousMoved = false;
  let replacementMoved = false;
  try {
    // The artifact directory is runner-private, but still revalidate the copied root
    // so a source-root symlink can never become the canonical pending directory.
    cpSync(replacementSource, replacement, { recursive: true, errorOnExist: true });
    assertDirectory(replacement, 'copied replacement pending target');
    assertRegularFile(join(replacement, 'skill-report.json'), 'copied replacement pending report');
    assertSafeTree(replacement, 'copied replacement pending target');
    assertDirectory(replacement, 'copied replacement pending target');
    renameSync(destination, previous);
    previousMoved = true;
    try {
      renameSync(replacement, destination);
      replacementMoved = true;
    } catch (error) {
      renameSync(previous, destination);
      previousMoved = false;
      throw error;
    }
  } finally {
    if (previousMoved && !replacementMoved) {
      renameSync(previous, destination);
      previousMoved = false;
    }
    rmSync(temporaryRoot, { recursive: true, force: true });
  }
}

function main() {
  const args = process.argv.slice(2);
  replacePendingSubmission({
    repositoryRoot: option(args, '--repository-root'),
    mergedResults: option(args, '--merged-results'),
    pendingDir: option(args, '--pending-dir'),
    expectedTreeHash: option(args, '--expected-tree-hash'),
    expectedReportHash: option(args, '--expected-report-hash'),
    expectedGitTreeOid: option(args, '--expected-git-tree-oid'),
    expectedSourceRef: option(args, '--expected-source-ref'),
  });
  process.stdout.write('Replaced frozen pending submission\n');
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Pending replacement failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
