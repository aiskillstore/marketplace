import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import {
  calculateCanonicalTreeHash,
  resolveApprovedSubmission,
} from '../resolve-approved-submission.mjs';

const SCRIPT = 'scripts/rebind-skill-report-hashes.mjs';

function withFixture(fn, { sourceUrl = 'https://github.com/example/source/tree/main/skill' } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'rebind-report-hashes-'));
  const skillDir = 'pending/example/fixture';
  const absoluteDir = join(root, skillDir);
  mkdirSync(join(absoluteDir, 'references'), { recursive: true });
  writeFileSync(join(absoluteDir, 'SKILL.md'), '---\nname: fixture\ndescription: final artifact\n---\n');
  writeFileSync(join(absoluteDir, 'references', '中文.md'), 'reference\n');
  writeFileSync(join(absoluteDir, 'skill-report.json'), `${JSON.stringify({
    meta: {
      slug: 'example-fixture',
      source_type: 'community',
      source_url: sourceUrl,
      source_ref: 'main',
      content_hash: '0'.repeat(64),
      tree_hash: '1'.repeat(64),
    },
    security_audit: { is_blocked: false, safe_to_publish: true },
  }, null, 2)}\n`);
  try {
    return fn({ root, skillDir, absoluteDir });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function run(root, paths) {
  const pathsFile = join(root, 'changed-skills.bin');
  writeFileSync(pathsFile, Buffer.from(`${paths.join('\0')}\0`));
  return spawnSync(process.execPath, [
    SCRIPT,
    '--repo-root', root,
    '--skill-paths-file', pathsFile,
  ], { cwd: process.cwd(), encoding: 'utf8' });
}

test('rebinds hashes to the final artifact while preserving source lineage', () => withFixture(({ root, skillDir, absoluteDir }) => {
  const result = run(root, [`${skillDir}/SKILL.md`]);
  assert.equal(result.status, 0, result.stderr);
  const report = JSON.parse(readFileSync(join(absoluteDir, 'skill-report.json'), 'utf8'));
  const expectedContent = createHash('sha256').update(readFileSync(join(absoluteDir, 'SKILL.md'))).digest('hex');
  const expectedTree = calculateCanonicalTreeHash(root, skillDir);
  assert.equal(report.meta.content_hash, expectedContent);
  assert.equal(report.meta.tree_hash, expectedTree);
  assert.equal(report.meta.source_url, 'https://github.com/example/source/tree/main/skill');
  assert.equal(report.meta.source_ref, 'main');

  const plan = resolveApprovedSubmission({
    repositoryRoot: root,
    changedFiles: [
      `${skillDir}/SKILL.md`,
      `${skillDir}/skill-report.json`,
      `${skillDir}/references/中文.md`,
    ],
  });
  assert.equal(plan.skills[0].contentHash, expectedContent);
  assert.equal(plan.skills[0].treeHash, expectedTree);
}));

test('rejects missing source lineage before changing hashes', () => withFixture(({ root, absoluteDir, skillDir }) => {
  const reportPath = join(absoluteDir, 'skill-report.json');
  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  report.meta.source_ref = '';
  writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  const result = run(root, [`${skillDir}/SKILL.md`]);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /invalid source_ref lineage/);
  assert.equal(JSON.parse(readFileSync(reportPath, 'utf8')).meta.content_hash, '0'.repeat(64));
}));

test('rejects traversal and control characters in changed path input', () => withFixture(({ root }) => {
  for (const path of ['../SKILL.md', 'pending/example/bad\npath/SKILL.md']) {
    const result = run(root, [path]);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /unsafe SKILL\.md path|noncanonical SKILL\.md path/);
  }
}));
