import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';

import {
  calculateCanonicalTreeHash,
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
      tree_hash: treeHash ?? calculateCanonicalTreeHash(root, pendingDir),
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
