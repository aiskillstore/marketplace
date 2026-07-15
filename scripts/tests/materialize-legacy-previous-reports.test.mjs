import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
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
import test from 'node:test';
import { materializeLegacyPreviousReports } from '../materialize-legacy-previous-reports.mjs';

function git(repositoryRoot, args) {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding: 'utf8' }).trim();
}

function write(repositoryRoot, relativePath, contents) {
  const path = join(repositoryRoot, relativePath);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, contents);
}

function commit(repositoryRoot, message) {
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', message]);
  return git(repositoryRoot, ['rev-parse', 'HEAD']);
}

function makeRepository() {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'legacy-previous-reports-'));
  git(repositoryRoot, ['init', '--initial-branch=main']);
  git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
  git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);
  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v1\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":1}\n');
  write(repositoryRoot, 'skills/owner/new/SKILL.md', '# New placeholder\n');
  const parentCommit = commit(repositoryRoot, 'parent');

  write(repositoryRoot, 'skills/owner/demo/SKILL.md', '# Demo v2\n');
  write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":2}\n');
  write(repositoryRoot, 'skills/owner/new/skill-report.json', '{"revision":1}\n');
  const currentCommit = commit(repositoryRoot, 'current');
  return { repositoryRoot, parentCommit, currentCommit };
}

function planFor(currentCommit) {
  const selected = [
    { slug: 'owner-demo', path: 'skills/owner/demo', marketplaceCommit: currentCommit },
    { slug: 'owner-new', path: 'skills/owner/new', marketplaceCommit: currentCommit },
  ];
  return {
    schemaVersion: 3,
    selectedCount: selected.length,
    selected,
    batches: [{
      index: 1,
      count: selected.length,
      groups: [{
        marketplaceCommit: currentCommit,
        count: selected.length,
        paths: selected.map((row) => row.path),
        slugs: selected.map((row) => row.slug),
      }],
    }],
  };
}

test('materializes first-parent reports and records an exact deterministic absence manifest', () => {
  const { repositoryRoot, parentCommit, currentCommit } = makeRepository();
  const outputRoot = join(repositoryRoot, 'output');
  const manifestPath = join(repositoryRoot, 'manifest.json');
  try {
    const manifest = materializeLegacyPreviousReports({
      repositoryRoot,
      plan: planFor(currentCommit),
      outputRoot,
      manifestPath,
    });
    assert.equal(manifest.selectedCount, 2);
    assert.deepEqual(manifest.entries, [
      {
        path: 'skills/owner/demo',
        currentCommit,
        parentCommit,
        present: true,
        sha256: createHash('sha256').update('{"revision":1}\n').digest('hex'),
      },
      {
        path: 'skills/owner/new',
        currentCommit,
        parentCommit,
        present: false,
        sha256: null,
      },
    ]);
    assert.equal(
      readFileSync(join(outputRoot, `batch-1/${currentCommit}/skills/owner/demo/skill-report.json`), 'utf8'),
      '{"revision":1}\n',
    );
    assert.equal(
      existsSync(join(outputRoot, `batch-1/${currentCommit}/skills/owner/new/skill-report.json`)),
      false,
    );
    assert.deepEqual(JSON.parse(readFileSync(manifestPath, 'utf8')), manifest);
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('uses a merge commit first parent rather than another parent', () => {
  const { repositoryRoot } = makeRepository();
  const outputRoot = join(repositoryRoot, 'output');
  const manifestPath = join(repositoryRoot, 'manifest.json');
  try {
    git(repositoryRoot, ['checkout', '-b', 'side']);
    write(repositoryRoot, 'side.txt', 'side\n');
    commit(repositoryRoot, 'side');
    git(repositoryRoot, ['checkout', 'main']);
    write(repositoryRoot, 'skills/owner/demo/skill-report.json', '{"revision":3}\n');
    const firstParent = commit(repositoryRoot, 'main parent');
    git(repositoryRoot, ['merge', '--no-ff', 'side', '-m', 'merge']);
    const mergeCommit = git(repositoryRoot, ['rev-parse', 'HEAD']);
    const plan = planFor(mergeCommit);
    plan.selected = [plan.selected[0]];
    plan.selectedCount = 1;
    plan.batches[0].count = 1;
    plan.batches[0].groups[0].paths = [plan.selected[0].path];
    plan.batches[0].groups[0].slugs = [plan.selected[0].slug];
    plan.batches[0].groups[0].count = 1;
    const manifest = materializeLegacyPreviousReports({ repositoryRoot, plan, outputRoot, manifestPath });
    assert.equal(manifest.entries[0].parentCommit, firstParent);
    assert.equal(
      readFileSync(join(outputRoot, `batch-1/${mergeCommit}/skills/owner/demo/skill-report.json`), 'utf8'),
      '{"revision":3}\n',
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('rejects unsafe, duplicate, symbolic, uncovered, and root-commit evidence before output', () => {
  const { repositoryRoot, currentCommit } = makeRepository();
  try {
    const cases = [
      {
        mutate(plan) { plan.selected[0].path = 'skills/owner/../demo'; plan.batches[0].groups[0].paths[0] = plan.selected[0].path; },
        error: /unsafe Skill path/,
      },
      {
        mutate(plan) { plan.selected[1].path = plan.selected[0].path; plan.batches[0].groups[0].paths[1] = plan.selected[0].path; },
        error: /duplicate Skill path/,
      },
      {
        mutate(plan) { plan.selected[0].marketplaceCommit = 'HEAD'; },
        error: /invalid exact commit/,
      },
      {
        mutate(plan) {
          plan.batches[0].groups[0].paths.pop();
          plan.batches[0].groups[0].slugs.pop();
          plan.batches[0].groups[0].count = 1;
          plan.batches[0].count = 1;
        },
        error: /do not cover selected paths/,
      },
    ];
    for (const [index, item] of cases.entries()) {
      const plan = planFor(currentCommit);
      item.mutate(plan);
      const outputRoot = join(repositoryRoot, `output-${index}`);
      const manifestPath = join(repositoryRoot, `manifest-${index}.json`);
      assert.throws(() => materializeLegacyPreviousReports({
        repositoryRoot, plan, outputRoot, manifestPath,
      }), item.error);
      assert.equal(existsSync(outputRoot), false);
      assert.equal(existsSync(manifestPath), false);
    }

    const rootCommit = git(repositoryRoot, ['rev-list', '--max-parents=0', 'HEAD']);
    const rootPlan = planFor(rootCommit);
    assert.throws(() => materializeLegacyPreviousReports({
      repositoryRoot,
      plan: rootPlan,
      outputRoot: join(repositoryRoot, 'root-output'),
      manifestPath: join(repositoryRoot, 'root-manifest.json'),
    }), /no valid first parent/);
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});

test('refuses to overwrite either evidence output', () => {
  const { repositoryRoot, currentCommit } = makeRepository();
  try {
    const plan = planFor(currentCommit);
    const outputRoot = join(repositoryRoot, 'output');
    const manifestPath = join(repositoryRoot, 'manifest.json');
    mkdirSync(outputRoot);
    write(outputRoot, 'sentinel', 'keep\n');
    assert.throws(() => materializeLegacyPreviousReports({
      repositoryRoot, plan, outputRoot, manifestPath,
    }), /output root is not empty/);
    rmSync(outputRoot, { recursive: true });
    writeFileSync(manifestPath, 'keep\n');
    assert.throws(() => materializeLegacyPreviousReports({
      repositoryRoot, plan, outputRoot, manifestPath,
    }), /manifest output already exists/);
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});
