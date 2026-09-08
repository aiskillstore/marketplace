import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import {
  chmodSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';

import { calculateCanonicalTreeHash } from '../resolve-approved-submission.mjs';
import {
  calculatePendingGitTreeOidAtCommit,
  replacePendingSubmission,
} from '../replace-pending-submission.mjs';

function write(root, path, contents) {
  const fullPath = join(root, path);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function writePending(root, content, sourceRef, risk = 'safe') {
  write(root, 'pending/example/alpha/SKILL.md', content);
  write(root, 'pending/example/alpha/skill-report.json', `${JSON.stringify({
    meta: { source_ref: sourceRef },
    security_audit: { risk_level: risk },
  })}\n`);
}

function git(root, ...args) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim();
}

function commitAll(root, message) {
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', message);
}

function initializeRepository(root) {
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  commitAll(root, 'initial pending');
}

function snapshot(root) {
  const report = readFileSync(join(root, 'pending/example/alpha/skill-report.json'));
  return {
    treeHash: calculateCanonicalTreeHash(root, 'pending/example/alpha'),
    reportHash: createHash('sha256').update(report).digest('hex'),
    gitTreeOid: calculatePendingGitTreeOidAtCommit(root, 'HEAD', 'pending/example/alpha'),
  };
}

function withFixture(run) {
  const root = mkdtempSync(join(tmpdir(), 'replace-pending-'));
  const repositoryRoot = join(root, 'repository');
  const mergedResults = join(root, 'merged');
  mkdirSync(repositoryRoot, { recursive: true });
  mkdirSync(mergedResults, { recursive: true });
  try {
    return run({ repositoryRoot, mergedResults });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test('replaces a canonical pending target only when the complete frozen snapshot matches', () => withFixture(({
  repositoryRoot,
  mergedResults,
}) => {
  const previousRef = '1'.repeat(40);
  writePending(repositoryRoot, '# Previous\n', previousRef);
  writePending(mergedResults, '# Replacement\n', '2'.repeat(40), 'medium');
  initializeRepository(repositoryRoot);
  const frozen = snapshot(repositoryRoot);

  replacePendingSubmission({
    repositoryRoot,
    mergedResults,
    pendingDir: 'pending/example/alpha',
    expectedTreeHash: frozen.treeHash,
    expectedReportHash: frozen.reportHash,
    expectedGitTreeOid: frozen.gitTreeOid,
    expectedSourceRef: previousRef,
  });

  assert.equal(
    readFileSync(join(repositoryRoot, 'pending/example/alpha/SKILL.md'), 'utf8'),
    '# Replacement\n',
  );
  assert.equal(
    JSON.parse(readFileSync(join(repositoryRoot, 'pending/example/alpha/skill-report.json'), 'utf8'))
      .security_audit.risk_level,
    'medium',
  );
}));

test('refuses a report-only concurrent change without replacing it', () => withFixture(({
  repositoryRoot,
  mergedResults,
}) => {
  const previousRef = '1'.repeat(40);
  writePending(repositoryRoot, '# Previous\n', previousRef);
  writePending(mergedResults, '# Replacement\n', '2'.repeat(40));
  initializeRepository(repositoryRoot);
  const frozen = snapshot(repositoryRoot);
  writePending(repositoryRoot, '# Previous\n', previousRef, 'critical');

  assert.throws(() => replacePendingSubmission({
    repositoryRoot,
    mergedResults,
    pendingDir: 'pending/example/alpha',
    expectedTreeHash: frozen.treeHash,
    expectedReportHash: frozen.reportHash,
    expectedGitTreeOid: frozen.gitTreeOid,
    expectedSourceRef: previousRef,
  }), /report changed after classification/);
  assert.equal(
    JSON.parse(readFileSync(join(repositoryRoot, 'pending/example/alpha/skill-report.json'), 'utf8'))
      .security_audit.risk_level,
    'critical',
  );
}));

test('refuses an unsafe report file type without replacing it', () => withFixture(({
  repositoryRoot,
  mergedResults,
}) => {
  const previousRef = '1'.repeat(40);
  writePending(repositoryRoot, '# Previous\n', previousRef);
  writePending(mergedResults, '# Replacement\n', '2'.repeat(40));
  initializeRepository(repositoryRoot);
  const frozen = snapshot(repositoryRoot);
  const reportPath = join(repositoryRoot, 'pending/example/alpha/skill-report.json');
  rmSync(reportPath);
  symlinkSync('SKILL.md', reportPath);

  assert.throws(() => replacePendingSubmission({
    repositoryRoot,
    mergedResults,
    pendingDir: 'pending/example/alpha',
    expectedTreeHash: frozen.treeHash,
    expectedReportHash: frozen.reportHash,
    expectedGitTreeOid: frozen.gitTreeOid,
    expectedSourceRef: previousRef,
  }), /report must be a non-symlink regular file/);
  assert.equal(readFileSync(reportPath, 'utf8'), '# Previous\n');
}));

test('refuses a tracked excluded-name change before whole-directory replacement', () => withFixture(({
  repositoryRoot,
  mergedResults,
}) => {
  const previousRef = '1'.repeat(40);
  writePending(repositoryRoot, '# Previous\n', previousRef);
  writePending(mergedResults, '# Replacement\n', '2'.repeat(40));
  initializeRepository(repositoryRoot);
  const frozen = snapshot(repositoryRoot);
  write(repositoryRoot, 'pending/example/alpha/concurrent.tmp', 'review state\n');
  commitAll(repositoryRoot, 'concurrent excluded-name state');
  assert.equal(calculateCanonicalTreeHash(repositoryRoot, 'pending/example/alpha'), frozen.treeHash);

  assert.throws(() => replacePendingSubmission({
    repositoryRoot,
    mergedResults,
    pendingDir: 'pending/example/alpha',
    expectedTreeHash: frozen.treeHash,
    expectedReportHash: frozen.reportHash,
    expectedGitTreeOid: frozen.gitTreeOid,
    expectedSourceRef: previousRef,
  }), /Git tree changed after classification/);
  assert.equal(
    readFileSync(join(repositoryRoot, 'pending/example/alpha/concurrent.tmp'), 'utf8'),
    'review state\n',
  );
}));

test('refuses a tracked report mode-only change before whole-directory replacement', () => withFixture(({
  repositoryRoot,
  mergedResults,
}) => {
  const previousRef = '1'.repeat(40);
  writePending(repositoryRoot, '# Previous\n', previousRef);
  writePending(mergedResults, '# Replacement\n', '2'.repeat(40));
  initializeRepository(repositoryRoot);
  const frozen = snapshot(repositoryRoot);
  const reportPath = join(repositoryRoot, 'pending/example/alpha/skill-report.json');
  chmodSync(reportPath, 0o755);
  commitAll(repositoryRoot, 'concurrent report mode');
  assert.equal(createHash('sha256').update(readFileSync(reportPath)).digest('hex'), frozen.reportHash);

  assert.throws(() => replacePendingSubmission({
    repositoryRoot,
    mergedResults,
    pendingDir: 'pending/example/alpha',
    expectedTreeHash: frozen.treeHash,
    expectedReportHash: frozen.reportHash,
    expectedGitTreeOid: frozen.gitTreeOid,
    expectedSourceRef: previousRef,
  }), /Git tree changed after classification/);
  assert.notEqual(lstatSync(reportPath).mode & 0o111, 0);
}));
