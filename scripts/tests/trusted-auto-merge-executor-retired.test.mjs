import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import test from 'node:test';

const retiredPaths = [
  'scripts/auto-merge-trusted-skill-pr.mjs',
  '.github/workflows/auto-merge-trusted-skill-pr.yml',
  'scripts/tests/auto-merge-trusted-skill-pr.test.mjs',
  'scripts/tests/auto-merge-trusted-skill-pr-workflow.test.mjs',
];

const forbiddenReferences = [
  'node scripts/auto-merge-trusted-skill-pr.mjs',
  'Auto Merge Trusted Skill PR',
  'auto-merge-trusted-skill-pr.yml',
];

test('the repository-owned trusted Skill PR auto-merge executor stays retired', () => {
  for (const path of retiredPaths) {
    assert.equal(existsSync(path), false, `${path} must remain retired; Cody handles the Skill workflow`);
  }

  for (const name of readdirSync('.github/workflows')) {
    if (!/\.ya?ml$/u.test(name)) continue;
    const source = readFileSync(`.github/workflows/${name}`, 'utf8');
    for (const reference of forbiddenReferences) {
      assert.doesNotMatch(source, new RegExp(reference.replaceAll('.', '\\.')),
        `.github/workflows/${name} must not restore the retired executor`);
    }
  }

  for (const manifest of ['package.json', 'package-lock.json']) {
    const source = readFileSync(manifest, 'utf8');
    for (const reference of forbiddenReferences) {
      assert.doesNotMatch(source, new RegExp(reference.replaceAll('.', '\\.')),
        `${manifest} must not restore the retired executor`);
    }
  }
});
