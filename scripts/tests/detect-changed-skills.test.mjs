import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import {
  detectChangedSkillPathsFromGit,
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
