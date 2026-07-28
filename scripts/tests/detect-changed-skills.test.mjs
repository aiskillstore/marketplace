import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import {
  detectChangedSkillPathsFromGit,
  filterRecoveredSkillPathsFromGit,
  resolveChangedSkillPaths,
} from '../detect-changed-skills.mjs';

function git(repositoryRoot, args) {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding: 'utf8' }).trim();
}

function write(repositoryRoot, relativePath, contents) {
  const fullPath = join(repositoryRoot, relativePath);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

test('resolves changed files to the closest published skill at arbitrary depth', () => {
  assert.deepEqual(
    resolveChangedSkillPaths(
      [
        'skills/flat/SKILL.md',
        'skills/owner/nested/reference.md',
        'skills/owner/nested/examples/demo/SKILL.md',
        'skills/owner/other/skill-report.json',
        'README.md',
      ],
      [
        'skills/flat/skill-report.json',
        'skills/owner/nested/skill-report.json',
        'skills/owner/other/skill-report.json',
      ],
    ),
    ['flat', 'owner/nested', 'owner/other'],
  );
});

test('uses pinned commit trees instead of the mutable runner working tree', () => {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'changed-skills-git-'));
  try {
    git(repositoryRoot, ['init', '--initial-branch=main']);
    git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
    git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);

    write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo\n');
    write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":1}\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'base']);
    const base = git(repositoryRoot, ['rev-parse', 'HEAD']);

    write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":2}\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'audit report']);
    const head = git(repositoryRoot, ['rev-parse', 'HEAD']);

    rmSync(join(repositoryRoot, 'skills/owner/demo/skill-report.json'));

    assert.deepEqual(
      detectChangedSkillPathsFromGit({ repositoryRoot, base, head }),
      ['owner/demo'],
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('subtracts only successful manual recovery slugs whose pinned skill tree is unchanged', () => {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'recovered-sync-git-'));
  try {
    git(repositoryRoot, ['init', '--initial-branch=main']);
    git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
    git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);

    write(repositoryRoot, 'skills/owner/recovered/SKILL.md', '# Recovered\n');
    write(repositoryRoot, 'skills/owner/recovered/skill-report.json', JSON.stringify({
      meta: { slug: 'owner-recovered' },
    }));
    write(repositoryRoot, 'skills/owner/changed/SKILL.md', '# Before\n');
    write(repositoryRoot, 'skills/owner/changed/skill-report.json', JSON.stringify({
      meta: { slug: 'owner-changed' },
    }));
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'manual recovery tree']);
    const recoveryHead = git(repositoryRoot, ['rev-parse', 'HEAD']);

    write(repositoryRoot, 'skills/owner/changed/SKILL.md', '# After\n');
    git(repositoryRoot, ['add', '.']);
    git(repositoryRoot, ['commit', '-m', 'later skill change']);
    const head = git(repositoryRoot, ['rev-parse', 'HEAD']);

    assert.deepEqual(
      filterRecoveredSkillPathsFromGit({
        repositoryRoot,
        head,
        skillPaths: ['owner/recovered', 'owner/changed'],
        recoveries: [{
          runId: 123,
          headSha: recoveryHead,
          artifactId: 456,
          digest: `sha256:${'a'.repeat(64)}`,
          slugs: ['owner-recovered', 'owner-changed'],
        }],
      }),
      ['owner/changed'],
    );

    assert.throws(
      () => filterRecoveredSkillPathsFromGit({
        repositoryRoot,
        head,
        skillPaths: ['owner/recovered'],
        recoveries: [{
          runId: 123,
          headSha: recoveryHead,
          artifactId: 456,
          digest: `sha256:${'a'.repeat(64)}`,
          slugs: ['owner-recovered', 'owner-recovered'],
        }],
      }),
      /duplicate recovery slug/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('fails closed on reserved or over-nested published report paths', () => {
  assert.throws(
    () => resolveChangedSkillPaths(
      ['skills/pending/pending/SKILL.md'],
      ['skills/pending/pending/skill-report.json'],
    ),
    /invalid or reserved path identity/,
  );
  assert.throws(
    () => resolveChangedSkillPaths(
      ['skills/owner/group/skill/SKILL.md'],
      ['skills/owner/group/skill/skill-report.json'],
    ),
    /invalid path depth/,
  );
});
