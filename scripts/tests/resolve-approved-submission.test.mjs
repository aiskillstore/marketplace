import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';

import {
  calculateCanonicalTreeHash,
  calculateCanonicalTreeHashAtCommit,
  resolveApprovedSubmission,
} from '../resolve-approved-submission.mjs';

function write(root, path, contents) {
  const fullPath = join(root, path);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function addSkill(root, pendingDir, {
  blocked = false,
  content = '# Skill\n',
  hash = null,
  slug = 'owner-skill',
  sourceType = 'community',
  sourceRef = '1'.repeat(40),
  sourceUrl = null,
  previousSourceRef = null,
  previousTreeHash = null,
  treeHash = null,
  withReference = false,
} = {}) {
  write(root, `${pendingDir}/SKILL.md`, content);
  if (withReference) write(root, `${pendingDir}/references/note.md`, '# Note\n');
  write(root, `${pendingDir}/skill-report.json`, `${JSON.stringify({
    meta: {
      content_hash: hash ?? createHash('sha256').update(content).digest('hex'),
      slug,
      source_type: sourceType,
      source_ref: sourceRef,
      source_url: sourceUrl ?? `https://github.com/owner/repo/tree/${sourceRef}/skills/skill`,
      tree_hash: treeHash ?? calculateCanonicalTreeHash(root, pendingDir),
      ...(previousSourceRef ? { previous_source_ref: previousSourceRef } : {}),
      ...(previousTreeHash ? { previous_tree_hash: previousTreeHash } : {}),
    },
    security_audit: { is_blocked: blocked, safe_to_publish: false },
  })}\n`);
}

function withRepository(run) {
  const root = mkdtempSync(join(tmpdir(), 'approved-submission-'));
  try {
    return run(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function git(root, ...args) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim();
}

function commitReportOnlyHistory(root, pendingDir, { oldRef = '1'.repeat(40), newRef = '2'.repeat(40) } = {}) {
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'report-only-reaudit');
  const reportPath = join(root, pendingDir, 'skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.source_ref = newRef;
  report.meta.source_url = report.meta.source_url.replace(oldRef, newRef);
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  git(root, 'add', reportPath);
  git(root, 'commit', '-qm', 're-audit report');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge re-audit report', 'report-only-reaudit');
  return { baseCommit, mergeCommit: git(root, 'rev-parse', 'HEAD'), report, reportPath };
}

function commitPartialReauditHistory(root, pendingDir) {
  const oldRef = '1'.repeat(40);
  const newRef = '2'.repeat(40);
  write(root, `${pendingDir}/unchanged.md`, '# Unchanged\n');
  write(root, `${pendingDir}/deleted.md`, '# Delete me\n');
  write(root, `${pendingDir}/script.sh`, '#!/bin/sh\nexit 0\n');
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: oldRef, withReference: true });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'partial-reaudit');
  write(root, `${pendingDir}/SKILL.md`, '# Updated Skill\n');
  write(root, `${pendingDir}/references/note.md`, '# Updated reference\n');
  write(root, `${pendingDir}/added.md`, '# Added\n');
  rmSync(join(root, pendingDir, 'deleted.md'));
  chmodSync(join(root, pendingDir, 'script.sh'), 0o755);
  const reportPath = join(root, pendingDir, 'skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.source_ref = newRef;
  report.meta.source_url = report.meta.source_url.replace(oldRef, newRef);
  report.meta.content_hash = createHash('sha256').update('# Updated Skill\n').digest('hex');
  report.meta.tree_hash = calculateCanonicalTreeHash(root, pendingDir);
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', 'partial re-audit');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge partial re-audit', 'partial-reaudit');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  const changedFiles = git(root, 'diff', '--name-only', '--no-renames', baseCommit, mergeCommit, '--', 'pending')
    .split('\n').filter(Boolean).sort();
  return { baseCommit, mergeCommit, changedFiles };
}

test('calculates a canonical skill hash from immutable Git blobs', () => withRepository((root) => {
  addSkill(root, 'skills/owner/skill', { slug: 'owner-skill', withReference: true });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'fixture');
  assert.equal(
    calculateCanonicalTreeHashAtCommit(root, 'HEAD', 'skills/owner/skill'),
    calculateCanonicalTreeHash(root, 'skills/owner/skill'),
  );
  write(root, 'skills/owner/skill/references/note.md', '# Changed\n');
  assert.notEqual(
    calculateCanonicalTreeHashAtCommit(root, 'HEAD', 'skills/owner/skill'),
    calculateCanonicalTreeHash(root, 'skills/owner/skill'),
  );
}));

test('resolves only frozen PR files and ignores unrelated pending submissions', () => withRepository((root) => {
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill', withReference: true });
  addSkill(root, 'pending/other/unrelated', { slug: 'other-unrelated' });

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [
      'pending/owner/skill/SKILL.md',
      'pending/owner/skill/skill-report.json',
      'pending/owner/skill/references/note.md',
    ],
  });

  assert.deepEqual(plan.skills.map(({ pendingDir, targetDir }) => ({ pendingDir, targetDir })), [
    { pendingDir: 'pending/owner/skill', targetDir: 'skills/owner/skill' },
  ]);
}));

test('supports an official flat pending skill', () => withRepository((root) => {
  addSkill(root, 'pending/official-skill', { slug: 'official-skill', sourceType: 'official' });
  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: ['pending/official-skill/SKILL.md', 'pending/official-skill/skill-report.json'],
  });
  assert.equal(plan.skills[0].targetDir, 'skills/official-skill');
}));

test('exact-history initial submission still requires and resolves the complete artifact', () => withRepository((root) => {
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  write(root, 'README.md', '# Base\n');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'base');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'initial-submission');
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill', withReference: true });
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'initial pending submission');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge initial submission', 'initial-submission');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  const changedFiles = git(root, 'diff', '--name-only', '--no-renames', baseCommit, mergeCommit, '--', 'pending')
    .split('\n').filter(Boolean).sort();
  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles,
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].publicationMode, 'full');
}));

test('resolves a report-only community re-audit without scanning unrelated pending roots', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: '1'.repeat(40), withReference: true });
  addSkill(root, 'pending/other/unrelated', { slug: 'other-unrelated' });
  const { baseCommit, mergeCommit } = commitReportOnlyHistory(root, pendingDir);

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [`${pendingDir}/skill-report.json`],
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });

  assert.deepEqual(plan.skills.map(({ pendingDir, targetDir, publicationMode }) => ({
    pendingDir,
    targetDir,
    publicationMode,
  })), [{
    pendingDir: 'pending/owner/skill',
    targetDir: 'skills/owner/skill',
    publicationMode: 'report-only',
  }]);
}));

test('resolves a report-only official re-audit', () => withRepository((root) => {
  const pendingDir = 'pending/official-skill';
  addSkill(root, pendingDir, { slug: 'official-skill', sourceType: 'official', sourceRef: '1'.repeat(40) });
  const { baseCommit, mergeCommit } = commitReportOnlyHistory(root, pendingDir);
  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [`${pendingDir}/skill-report.json`],
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].targetDir, 'skills/official-skill');
  assert.equal(plan.skills[0].publicationMode, 'report-only');
}));

test('exact history parses only merge parent headers, never commit-message text', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const oldRef = '1'.repeat(40);
  const newRef = '2'.repeat(40);
  const spoofedParent = 'a'.repeat(40);
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: oldRef });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  const updateReport = () => {
    const reportPath = join(root, pendingDir, 'skill-report.json');
    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    report.meta.source_ref = newRef;
    report.meta.source_url = report.meta.source_url.replace(oldRef, newRef);
    writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  };

  updateReport();
  git(root, 'add', '.');
  git(root, 'commit', '-m', 'not a merge', '-m', `parent ${spoofedParent}`);
  const nonMergeCommit = git(root, 'rev-parse', 'HEAD');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [`${pendingDir}/skill-report.json`],
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: nonMergeCommit,
    }),
    /publication base is not the exact first parent of the merge commit/,
  );

  git(root, 'checkout', '-q', '--force', baseCommit);
  git(root, 'branch', '-f', baseBranch, baseCommit);
  git(root, 'checkout', '-qb', 'reaudit');
  updateReport();
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 're-audit report');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-m', `merge re-audit\n\nparent ${spoofedParent}`, 'reaudit');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [`${pendingDir}/skill-report.json`],
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].publicationMode, 'report-only');
}));

test('partial re-audit admits omitted unchanged files, mode changes, additions, and legal deletions', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  assert.ok(!changedFiles.includes(`${pendingDir}/unchanged.md`));
  assert.ok(changedFiles.includes(`${pendingDir}/deleted.md`));
  assert.equal(readFileSync(join(root, `${pendingDir}/unchanged.md`), 'utf8'), '# Unchanged\n');
  assert.throws(() => readFileSync(join(root, `${pendingDir}/deleted.md`)));

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles,
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].publicationMode, 'partial-reaudit');
  assert.equal(plan.skills[0].targetDir, 'skills/owner/skill');
}));

test('partial re-audit rejects incomplete PR evidence and current omitted-file drift', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: changedFiles.filter((path) => path !== `${pendingDir}/added.md`),
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /changed-file evidence does not match/,
  );

  write(root, `${pendingDir}/unchanged.md`, '# Drifted after merge\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles,
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /blob or mode drifted/,
  );
}));

test('partial re-audit rejects an undeclared current file', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  write(root, `${pendingDir}/undeclared.md`, '# Not reviewed\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles,
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /path set drifted/,
  );
}));

test('partial re-audit rejects current mode drift on an omitted file', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  chmodSync(join(root, pendingDir, 'unchanged.md'), 0o755);
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles,
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /blob or mode drifted/,
  );
}));

test('partial re-audit requires both SKILL.md and skill-report.json in the exact changed set', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const oldRef = '1'.repeat(40);
  const newRef = '2'.repeat(40);
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: oldRef, withReference: true });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'payload-without-skill');
  write(root, `${pendingDir}/references/note.md`, '# Updated reference\n');
  const reportPath = join(root, pendingDir, 'skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.source_ref = newRef;
  report.meta.source_url = report.meta.source_url.replace(oldRef, newRef);
  report.meta.tree_hash = calculateCanonicalTreeHash(root, pendingDir);
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'change payload without SKILL.md');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge payload without SKILL.md', 'payload-without-skill');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  const changedFiles = git(root, 'diff', '--name-only', '--no-renames', baseCommit, mergeCommit, '--', 'pending')
    .split('\n').filter(Boolean).sort();

  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles,
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /partial re-audit must change both SKILL\.md and skill-report\.json/,
  );
}));

test('an exact-history re-audit with every current file changed remains full mode', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const oldRef = '1'.repeat(40);
  const newRef = '2'.repeat(40);
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: oldRef });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'complete-reaudit');
  write(root, `${pendingDir}/SKILL.md`, '# Updated Skill\n');
  const reportPath = join(root, pendingDir, 'skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.source_ref = newRef;
  report.meta.source_url = report.meta.source_url.replace(oldRef, newRef);
  report.meta.content_hash = createHash('sha256').update('# Updated Skill\n').digest('hex');
  report.meta.tree_hash = calculateCanonicalTreeHash(root, pendingDir);
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'complete re-audit');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge complete re-audit', 'complete-reaudit');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  const changedFiles = git(root, 'diff', '--name-only', '--no-renames', baseCommit, mergeCommit, '--', 'pending')
    .split('\n').filter(Boolean).sort();

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles,
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].publicationMode, 'full');
}));

test('partial re-audit rejects committed current-main drift even if the worktree is restored to merge bytes', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  write(root, `${pendingDir}/unchanged.md`, '# Drifted in current main\n');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'drift pending after reviewed merge');
  write(root, `${pendingDir}/unchanged.md`, '# Unchanged\n');

  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles,
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /current main pending subtree blob or mode drifted/,
  );
}));

test('report-only CLI accepts the exact workflow commit arguments', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: '1'.repeat(40) });
  const { baseCommit, mergeCommit } = commitReportOnlyHistory(root, pendingDir);
  const filesPath = join(root, 'pr-files.txt');
  const outputPath = join(root, 'approval-plan.json');
  writeFileSync(filesPath, `${pendingDir}/skill-report.json\n`);
  const result = spawnSync(process.execPath, [
    join(process.cwd(), 'scripts/resolve-approved-submission.mjs'),
    '--repo-root', root,
    '--files', filesPath,
    '--output', outputPath,
    '--report-only-base-commit', baseCommit,
    '--report-only-merge-commit', mergeCommit,
  ], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(readFileSync(outputPath, 'utf8')).skills[0].publicationMode, 'report-only');
}));

test('report-only CLI verifies merge parents after workflow-shaped depth-1 fetches', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: '1'.repeat(40) });
  const { baseCommit, mergeCommit } = commitReportOnlyHistory(root, pendingDir);
  write(root, 'README.md', '# Current main\n');
  git(root, 'add', 'README.md');
  git(root, 'commit', '-qm', 'advance main after merge');

  const shallowRoot = mkdtempSync(join(tmpdir(), 'approved-submission-shallow-'));
  try {
    const clone = join(shallowRoot, 'clone');
    const cloneResult = spawnSync('git', ['clone', '--depth=1', `file://${root}`, clone], { encoding: 'utf8' });
    assert.equal(cloneResult.status, 0, cloneResult.stderr);
    git(clone, 'fetch', '--no-tags', '--depth=1', 'origin', baseCommit, mergeCommit);
    assert.equal(git(clone, 'rev-list', '--parents', '-n', '1', mergeCommit), mergeCommit);

    const filesPath = join(shallowRoot, 'pr-files.txt');
    const outputPath = join(shallowRoot, 'approval-plan.json');
    writeFileSync(filesPath, `${pendingDir}/skill-report.json\n`);
    const result = spawnSync(process.execPath, [
      join(process.cwd(), 'scripts/resolve-approved-submission.mjs'),
      '--repo-root', clone,
      '--files', filesPath,
      '--output', outputPath,
      '--report-only-base-commit', baseCommit,
      '--report-only-merge-commit', mergeCommit,
    ], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(readFileSync(outputPath, 'utf8')).skills[0].publicationMode, 'report-only');
  } finally {
    rmSync(shallowRoot, { recursive: true, force: true });
  }
}));

test('partial re-audit CLI passes after workflow-shaped depth-1 fetches', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const { baseCommit, mergeCommit, changedFiles } = commitPartialReauditHistory(root, pendingDir);
  write(root, 'README.md', '# Current main\n');
  git(root, 'add', 'README.md');
  git(root, 'commit', '-qm', 'advance main after partial merge');
  const shallowRoot = mkdtempSync(join(tmpdir(), 'approved-partial-shallow-'));
  try {
    const clone = join(shallowRoot, 'clone');
    const cloneResult = spawnSync('git', ['clone', '--depth=1', `file://${root}`, clone], { encoding: 'utf8' });
    assert.equal(cloneResult.status, 0, cloneResult.stderr);
    git(clone, 'fetch', '--no-tags', '--depth=1', 'origin', baseCommit, mergeCommit);
    const filesPath = join(shallowRoot, 'pr-files.txt');
    const outputPath = join(shallowRoot, 'approval-plan.json');
    writeFileSync(filesPath, `${changedFiles.join('\n')}\n`);
    const result = spawnSync(process.execPath, [
      join(process.cwd(), 'scripts/resolve-approved-submission.mjs'),
      '--repo-root', clone,
      '--files', filesPath,
      '--output', outputPath,
      '--report-only-base-commit', baseCommit,
      '--report-only-merge-commit', mergeCommit,
    ], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(readFileSync(outputPath, 'utf8')).skills[0].publicationMode, 'partial-reaudit');
  } finally {
    rmSync(shallowRoot, { recursive: true, force: true });
  }
}));

test('report-only re-audit is admitted only when the exact prior pending content and provenance are unchanged', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  const oldRef = '1'.repeat(40);
  const newRef = '2'.repeat(40);
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: oldRef, withReference: true });
  const { baseCommit, mergeCommit, reportPath } = commitReportOnlyHistory(root, pendingDir, { oldRef, newRef });

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [`${pendingDir}/skill-report.json`],
    reportOnlyBaseCommit: baseCommit,
    reportOnlyMergeCommit: mergeCommit,
  });
  assert.equal(plan.skills[0].publicationMode, 'report-only');

  git(root, 'checkout', '-q', '--detach', baseCommit);
  git(root, 'checkout', '-qb', 'untrusted-reaudit');
  const untrustedReport = JSON.parse(readFileSync(reportPath, 'utf8'));
  untrustedReport.meta.source_ref = newRef;
  untrustedReport.meta.source_url = `https://github.com/other/repo/tree/${newRef}/skills/skill`;
  writeFileSync(reportPath, `${JSON.stringify(untrustedReport)}\n`);
  git(root, 'add', reportPath);
  git(root, 'commit', '-qm', 'untrusted provenance change');
  git(root, 'checkout', '-q', '--detach', baseCommit);
  git(root, 'merge', '--no-ff', '-qm', 'merge untrusted re-audit', 'untrusted-reaudit');
  const untrustedMergeCommit = git(root, 'rev-parse', 'HEAD');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [`${pendingDir}/skill-report.json`],
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: untrustedMergeCommit,
    }),
    /source provenance does not match the trusted prior pending report/,
  );
}));

test('report-only re-audit rejects a changed pending payload even when the report is valid', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  addSkill(root, pendingDir, { slug: 'owner-skill' });
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'prior pending submission');
  const baseBranch = git(root, 'branch', '--show-current');
  const baseCommit = git(root, 'rev-parse', 'HEAD');
  git(root, 'checkout', '-qb', 'payload-drift');
  writeFileSync(join(root, pendingDir, 'SKILL.md'), '# Drifted\n');
  git(root, 'add', '.');
  git(root, 'commit', '-qm', 'unexpected payload change');
  git(root, 'checkout', '-q', baseBranch);
  git(root, 'merge', '--no-ff', '-qm', 'merge payload drift', 'payload-drift');
  const mergeCommit = git(root, 'rev-parse', 'HEAD');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [`${pendingDir}/skill-report.json`],
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /changed-file evidence does not match/,
  );
}));

test('report-only re-audit rejects additional changed payload files', () => withRepository((root) => {
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill', withReference: true });
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [
        'pending/owner/skill/skill-report.json',
        'pending/owner/skill/references/note.md',
      ],
    }),
    /report-only.*only.*skill-report\.json/,
  );
  write(root, 'README.md', '# Unrelated\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/skill/skill-report.json', 'README.md'],
    }),
    /outside pending/,
  );
}));

test('report-only re-audit requires a regular SKILL.md bound by exact merged history', () => withRepository((root) => {
  const pendingDir = 'pending/owner/skill';
  addSkill(root, pendingDir, { slug: 'owner-skill', sourceRef: '1'.repeat(40), withReference: true });
  const { baseCommit, mergeCommit } = commitReportOnlyHistory(root, pendingDir);
  rmSync(join(root, pendingDir, 'SKILL.md'));
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [`${pendingDir}/skill-report.json`],
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /current pending subtree path set drifted/,
  );

  git(root, 'checkout', '--force', mergeCommit);
  write(root, `${pendingDir}/SKILL.md`, '# Drifted\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [`${pendingDir}/skill-report.json`],
      reportOnlyBaseCommit: baseCommit,
      reportOnlyMergeCommit: mergeCommit,
    }),
    /current pending subtree blob or mode drifted/,
  );
}));

test('authorizes a reviewed same-repository update when the source path moves', () => withRepository((root) => {
  const oldCommit = '1'.repeat(40);
  const newCommit = '2'.repeat(40);
  addSkill(root, 'skills/owner/skill', {
    slug: 'owner-skill',
    sourceRef: oldCommit,
    sourceUrl: `https://github.com/owner/repo/tree/${oldCommit}/legacy/skill`,
  });
  const previousTreeHash = calculateCanonicalTreeHash(root, 'skills/owner/skill');
  const publishedReportPath = join(root, 'skills/owner/skill/skill-report.json');
  const publishedReport = JSON.parse(readFileSync(publishedReportPath, 'utf8'));
  publishedReport.meta.tree_hash = '0'.repeat(64);
  writeFileSync(publishedReportPath, `${JSON.stringify(publishedReport)}\n`);
  addSkill(root, 'pending/owner/skill', {
    slug: 'owner-skill',
    content: '# Updated\n',
    sourceRef: newCommit,
    sourceUrl: `https://github.com/owner/repo/tree/${newCommit}/skills/new-skill`,
    previousSourceRef: oldCommit,
    previousTreeHash,
  });

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: ['pending/owner/skill/SKILL.md', 'pending/owner/skill/skill-report.json'],
  });
  assert.equal(plan.skills[0].update, true);
  assert.equal(plan.skills[0].previousSourceRef, oldCommit);

  const reportPath = join(root, 'pending/owner/skill/skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.previous_tree_hash = '0'.repeat(64);
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/skill/SKILL.md', 'pending/owner/skill/skill-report.json'],
    }),
    /reviewed update snapshot does not match/,
  );

  report.meta.previous_tree_hash = previousTreeHash;
  report.meta.source_url = `https://github.com/owner/other/tree/${newCommit}/skills/new-skill`;
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/skill/SKILL.md', 'pending/owner/skill/skill-report.json'],
    }),
    /source identity does not match the published target/,
  );
}));

test('resolves an exact concurrent duplicate without weakening update snapshots', () => withRepository((root) => {
  const sourceRef = '1'.repeat(40);
  addSkill(root, 'skills/owner/skill', { slug: 'owner-skill', sourceRef });
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill', sourceRef });

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: ['pending/owner/skill/SKILL.md', 'pending/owner/skill/skill-report.json'],
  });
  assert.equal(plan.skills[0].duplicate, true);
  assert.equal(plan.skills[0].update, false);

  write(root, 'pending/owner/skill/SKILL.md', '# Changed\n');
  const reportPath = join(root, 'pending/owner/skill/skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.content_hash = createHash('sha256').update('# Changed\n').digest('hex');
  report.meta.tree_hash = calculateCanonicalTreeHash(root, 'pending/owner/skill');
  writeFileSync(reportPath, `${JSON.stringify(report)}\n`);
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/skill/SKILL.md', 'pending/owner/skill/skill-report.json'],
    }),
    /reviewed update snapshot does not match/,
  );
}));

test('rejects root-level and over-nested pending SKILL.md paths', () => withRepository((root) => {
  write(root, 'pending/SKILL.md', '# Broken\n');
  assert.throws(
    () => resolveApprovedSubmission({ repositoryRoot: root, changedFiles: ['pending/SKILL.md'] }),
    /must be pending/,
  );
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/pending/owner/skill/SKILL.md'],
    }),
    /must be pending/,
  );
}));

test('rejects absolute, traversal, and backslash frozen paths', () => withRepository((root) => {
  for (const path of ['/pending/owner/skill/SKILL.md', 'pending/../skill/SKILL.md', 'pending\\owner\\skill\\SKILL.md']) {
    assert.throws(
      () => resolveApprovedSubmission({ repositoryRoot: root, changedFiles: [path] }),
      /invalid frozen path/,
    );
  }
}));

test('rejects stale report hashes without using audit verdicts as a publication gate', () => withRepository((root) => {
  addSkill(root, 'pending/owner/stale', { hash: '0'.repeat(64), slug: 'owner-stale' });
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/stale/SKILL.md', 'pending/owner/stale/skill-report.json'],
    }),
    /content_hash does not match/,
  );

  addSkill(root, 'pending/owner/blocked', { blocked: true, slug: 'owner-blocked' });
  assert.equal(resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: ['pending/owner/blocked/SKILL.md', 'pending/owner/blocked/skill-report.json'],
  }).skills.length, 1);
}));

test('rejects reference drift and report slugs that do not match the publication path', () => withRepository((root) => {
  addSkill(root, 'pending/owner/tree-drift', { slug: 'owner-tree-drift', withReference: true });
  write(root, 'pending/owner/tree-drift/references/note.md', '# Changed after audit\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [
        'pending/owner/tree-drift/SKILL.md',
        'pending/owner/tree-drift/skill-report.json',
        'pending/owner/tree-drift/references/note.md',
      ],
    }),
    /tree_hash does not match/,
  );

  addSkill(root, 'pending/owner/name', { slug: 'victim' });
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: ['pending/owner/name/SKILL.md', 'pending/owner/name/skill-report.json'],
    }),
    /slug does not match its publication path/,
  );
}));

test('rejects pending files outside the frozen skill roots', () => withRepository((root) => {
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill' });
  write(root, 'pending/other/report.json', '{}\n');
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [
        'pending/owner/skill/SKILL.md',
        'pending/owner/skill/skill-report.json',
        'pending/other/report.json',
      ],
    }),
    /outside the frozen skill set/,
  );
}));

test('rejects pre-existing files inside a frozen skill directory', () => withRepository((root) => {
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill', withReference: true });
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [
        'pending/owner/skill/SKILL.md',
        'pending/owner/skill/skill-report.json',
      ],
    }),
    /outside the frozen PR\/artifact set/,
  );
}));

test('rejects symlinked resources from the frozen file set', () => withRepository((root) => {
  addSkill(root, 'pending/owner/skill', { slug: 'owner-skill' });
  mkdirSync(join(root, 'pending/owner/skill/references'), { recursive: true });
  symlinkSync('/etc/hosts', join(root, 'pending/owner/skill/references/linked.md'));
  assert.throws(
    () => resolveApprovedSubmission({
      repositoryRoot: root,
      changedFiles: [
        'pending/owner/skill/SKILL.md',
        'pending/owner/skill/skill-report.json',
        'pending/owner/skill/references/linked.md',
      ],
    }),
    /not a regular file/,
  );
}));
