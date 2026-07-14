import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import {
  parseManualSkillIdentifiers,
  resolveManualSkillPaths,
} from '../resolve-manual-skills.mjs';

function git(repositoryRoot, args) {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding: 'utf8' }).trim();
}

function write(repositoryRoot, relativePath, contents) {
  const fullPath = join(repositoryRoot, relativePath);
  mkdirSync(dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function makeRepository() {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'resolve-manual-skills-'));
  git(repositoryRoot, ['init', '--initial-branch=main']);
  git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
  git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);
  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', JSON.stringify({ meta: { slug: 'custom-demo' } }));
  write(repositoryRoot, 'skills/other/tool/SKILL.md', '# Tool\n');
  write(repositoryRoot, 'skills/other/tool/skill-report.json', JSON.stringify({ meta: { slug: 'other-tool' } }));
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', 'catalog']);
  return { repositoryRoot, commit: git(repositoryRoot, ['rev-parse', 'HEAD']) };
}

test('normalizes manual identifiers and rejects traversal', () => {
  assert.deepEqual(
    parseManualSkillIdentifiers('skills/owner/demo/skill-report.json,custom-demo custom-demo'),
    ['owner/demo', 'custom-demo'],
  );
  for (const invalid of ['', '../owner/demo', 'owner/../demo', '/owner/demo', 'owner\\demo']) {
    assert.throws(() => parseManualSkillIdentifiers(invalid), /no manual|invalid manual/);
  }
});

test('resolves paths and report slugs from the exact Git tree when skills is absent on disk', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    rmSync(join(repositoryRoot, 'skills'), { recursive: true, force: true });
    assert.deepEqual(
      resolveManualSkillPaths({
        repositoryRoot,
        commit,
        skills: 'custom-demo,other/tool owner/demo',
      }),
      ['other/tool', 'owner/demo'],
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('fails closed for missing identifiers and symbolic commits', () => {
  const { repositoryRoot, commit } = makeRepository();
  try {
    assert.throws(
      () => resolveManualSkillPaths({ repositoryRoot, commit, skills: 'missing-skill' }),
      /could not resolve skill identifier/,
    );
    assert.throws(
      () => resolveManualSkillPaths({ repositoryRoot, commit: 'HEAD', skills: 'custom-demo' }),
      /exact 40-character SHA/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});
