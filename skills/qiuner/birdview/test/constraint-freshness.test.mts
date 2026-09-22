import test from 'node:test';
import type { TestContext } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { architecture } from './fixtures.mjs';
import { inspectConstraintFreshness } from '../src/constraint-freshness.mjs';

function fixture(t: TestContext) {
  const repository = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-freshness-'));
  t.after(() => fs.rmSync(repository, { recursive: true, force: true }));
  const git = (...args: string[]): string => execFileSync('git', args, { cwd: repository, encoding: 'utf8', windowsHide: true }).trim();
  git('init', '-q');
  git('config', 'user.name', 'Birdview test');
  git('config', 'user.email', 'birdview@example.invalid');
  git('config', 'core.autocrlf', 'false');
  git('config', 'commit.gpgsign', 'false');
  git('config', 'core.hooksPath', path.join(repository, 'no-hooks'));
  fs.writeFileSync(path.join(repository, 'rules.md'), 'Wait for children.\n');
  fs.writeFileSync(path.join(repository, 'worker.ts'), 'export const worker = 1;\n');
  git('add', '.');
  git('commit', '-qm', 'Fixture baseline');
  const map = architecture(fs.readFileSync(new URL('../examples/architecture.json', import.meta.url), 'utf8'));
  map.constraints = [{ id: 'cleanup', name: 'Wait for cleanup', note: 'Applies to child work.', explanation: 'Cancellation must finish before returning.', origin: 'local', strength: 'required', applicability: 'applicable', scope: 'project', modules: [], relationships: [], evidence: [{ path: 'rules.md', note: 'Lifecycle rule.', quote: 'Wait for children.' }], code: [{ path: 'worker.ts', symbol: 'worker', note: 'Worker implementation.' }], baselineCommit: git('rev-parse', 'HEAD'), verification: 'Check cancellation.' }];
  const inspect = (root = repository) => inspectConstraintFreshness(map, root).rules.cleanup!;
  return { repository, git, map, inspect };
}

test('detects working, staged and committed linked-file changes without changing Git state', t => {
  const { repository, git, map, inspect } = fixture(t);
  const baseline = map.constraints![0]!.baselineCommit;
  const repositoryAlias = process.platform === 'win32' ? repository.replace(/^([A-Z]):/, (_, drive: string) => `${drive.toLowerCase()}:`) : repository;
  assert.equal(inspect(repositoryAlias).status, 'unchanged');
  fs.mkdirSync(path.join(repository, 'nested'));
  assert.throws(() => inspect(path.join(repository, 'nested')), /repository root/);
  assert.equal(inspect().status, 'unchanged');
  fs.writeFileSync(path.join(repository, 'worker.ts'), 'export const worker = 2;\n');
  const before = git('status', '--porcelain');
  assert.equal(inspect().status, 'changed');
  assert.equal(git('status', '--porcelain'), before);
  assert.equal(git('rev-parse', 'HEAD'), baseline);
  git('add', 'worker.ts');
  fs.writeFileSync(path.join(repository, 'worker.ts'), 'export const worker = 1;\n');
  assert.equal(inspect().status, 'changed');
  git('commit', '-qm', 'Fixture code change');
  git('restore', 'worker.ts');
  assert.equal(inspect().status, 'changed');
});

test('reports source changes, deleted code and unavailable baselines without compliance claims', t => {
  const { repository, map, inspect } = fixture(t);
  fs.writeFileSync(path.join(repository, 'unrelated.ts'), 'untracked\n');
  assert.equal(inspect().status, 'unchanged');
  fs.writeFileSync(path.join(repository, 'rules.md'), 'A different rule.\n');
  assert.equal(inspect().files.find(file => file.role === 'source')!.status, 'changed');
  fs.unlinkSync(path.join(repository, 'worker.ts'));
  assert.equal(inspect().files.find(file => file.role === 'code')!.status, 'missing');
  map.constraints![0]!.baselineCommit = '0'.repeat(40);
  assert.equal(inspect().reason, 'unavailable-baseline');
  delete map.constraints![0]!.baselineCommit;
  assert.equal(inspect().reason, 'no-baseline');
});
