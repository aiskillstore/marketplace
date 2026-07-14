import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import {
  materializeChangedSkills,
  parseChangedSkillPaths,
} from '../materialize-changed-skills.mjs';

function git(repositoryRoot, args) {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding: 'utf8' }).trim();
}

function write(repositoryRoot, relativePath, contents) {
  const fullPath = join(repositoryRoot, relativePath);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function makeRepository() {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'materialize-skills-'));
  git(repositoryRoot, ['init', '--initial-branch=main']);
  git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
  git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);

  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v1\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":1}\n');
  write(repositoryRoot, 'skills/owner/untouched/SKILL.md', '# Untouched\n');
  write(repositoryRoot, 'skills/owner/untouched/skill-report.json', '{"revision":1}\n');
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', 'base']);

  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v2\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":2}\n');
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', 'updated report']);

  return { repositoryRoot, commit: git(repositoryRoot, ['rev-parse', 'HEAD']) };
}

test('parses unique repository-relative skill paths and rejects unsafe inputs', () => {
  assert.deepEqual(
    parseChangedSkillPaths('owner/zeta,owner/alpha owner/zeta'),
    ['owner/alpha', 'owner/zeta'],
  );

  for (const invalid of [
    '',
    '/owner/demo',
    'skills/owner/demo',
    '../owner/demo',
    'owner/../demo',
    'owner\\demo',
  ]) {
    assert.throws(() => parseChangedSkillPaths(invalid), /no changed|invalid changed/);
  }
});

test('restores only selected paths from an exact commit through skip-worktree state', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v3 at mutable HEAD\n');
    write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":3}\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'newer mutable head']);

    const demoFiles = [
      'skills/owner/demo/SKILL.md',
      'skills/owner/demo/skill-report.json',
    ];
    git(repositoryRoot, ['update-index', '--skip-worktree', ...demoFiles]);
    rmSync(join(repositoryRoot, 'skills/owner/demo'), { recursive: true });

    write(repositoryRoot, 'skills/owner/untouched/local-only.txt', 'keep me\n');
    write(repositoryRoot, 'skills/owner/demo/stale-untracked.txt', 'remove me\n');

    assert.deepEqual(
      materializeChangedSkills({ repositoryRoot, commit, skills: ['owner/demo'] }),
      ['skills/owner/demo'],
    );
    assert.equal(readFileSync(join(repositoryRoot, 'skills/owner/demo/SKILL.md'), 'utf8'), '# Demo v2\n');
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/demo/skill-report.json'), 'utf8'),
      '{"revision":2}\n',
    );
    assert.equal(existsSync(join(repositoryRoot, 'skills/owner/demo/stale-untracked.txt')), false);
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/untouched/local-only.txt'), 'utf8'),
      'keep me\n',
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('fails before mutation when a selected path has no published report at the pinned commit', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    write(repositoryRoot, 'skills/owner/not-published/local-only.txt', 'preserve on preflight failure\n');

    assert.throws(
      () => materializeChangedSkills({
        repositoryRoot,
        commit,
        skills: ['owner/demo', 'owner/not-published'],
      }),
      /published report is missing/,
    );
    assert.equal(
      readFileSync(join(repositoryRoot, 'skills/owner/not-published/local-only.txt'), 'utf8'),
      'preserve on preflight failure\n',
    );
    assert.equal(readFileSync(join(repositoryRoot, 'skills/owner/demo/SKILL.md'), 'utf8'), '# Demo v2\n');
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('rejects symbolic commit names instead of materializing mutable HEAD', () => {
  const { repositoryRoot } = makeRepository();
  try {
    assert.throws(
      () => materializeChangedSkills({ repositoryRoot, commit: 'HEAD', skills: ['owner/demo'] }),
      /exact 40-character SHA/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});
