import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

import { fetchArtifactVersionInventory } from '../fetch-artifact-version-inventory.mjs';
import { buildArtifactBackfillPlan, main } from '../plan-artifact-version-backfill.mjs';

const HASH_A = 'a'.repeat(64);
const HASH_B = 'b'.repeat(64);

function git(root, ...args) {
  return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8' }).trim();
}

function createRepository() {
  const root = mkdtempSync(join(tmpdir(), 'artifact-backfill-plan-'));
  git(root, 'init', '-q');
  git(root, 'config', 'user.email', 'test@example.com');
  git(root, 'config', 'user.name', 'Test');
  const addSkill = (relativePath, slug, contentHash = HASH_A, treeHash = HASH_B) => {
    const directory = join(root, 'skills', relativePath);
    mkdirSync(directory, { recursive: true });
    writeFileSync(join(directory, 'SKILL.md'), `---\nname: ${slug}\nversion: 1.0.0\n---\n`);
    writeFileSync(join(directory, 'skill-report.json'), JSON.stringify({
      meta: { slug, content_hash: contentHash, tree_hash: treeHash },
    }));
  };
  const commit = (message) => {
    git(root, 'add', '.');
    git(root, 'commit', '-qm', message);
    return git(root, 'rev-parse', 'HEAD');
  };
  return { root, addSkill, commit, cleanup: () => rmSync(root, { recursive: true, force: true }) };
}

function inventoryRow({ slug, path, commit, revision = 0, contentHash = HASH_A, treeHash = HASH_B }) {
  return {
    slug,
    plugin_path: `skills/${path}`,
    marketplace_commit_sha: commit,
    content_hash: contentHash,
    tree_hash: treeHash,
    artifact_revision: revision,
  };
}

test('plans only production legacy rows from their exact historical commit and path', () => {
  const repository = createRepository();
  try {
    repository.addSkill('owner/legacy', 'legacy-skill');
    repository.addSkill('owner/versioned', 'already-versioned');
    const legacyCommit = repository.commit('legacy snapshot');
    repository.addSkill('owner/repo-only', 'repo-only');
    writeFileSync(join(repository.root, 'skills/owner/legacy/SKILL.md'), 'newer unapproved bytes\n');
    repository.commit('newer repository tree');

    const plan = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: [
        inventoryRow({ slug: 'legacy-skill', path: 'owner/legacy', commit: legacyCommit }),
        inventoryRow({ slug: 'already-versioned', path: 'owner/versioned', commit: legacyCommit, revision: 3 }),
      ] },
      batchSize: 100,
    });

    assert.equal(plan.inventoryCount, 2);
    assert.equal(plan.totalLegacy, 1);
    assert.deepEqual(plan.selected.map((row) => row.slug), ['legacy-skill']);
    assert.equal(plan.selected[0].marketplaceCommit, legacyCommit);
    assert.equal(plan.groups[0].marketplaceCommit, legacyCommit);
    assert.deepEqual(plan.groups[0].paths, ['skills/owner/legacy']);
    assert.equal(plan.selected.some((row) => row.slug === 'repo-only'), false);
  } finally {
    repository.cleanup();
  }
});

test('uses stable production slug cursors and groups selected rows by commit', () => {
  const repository = createRepository();
  try {
    repository.addSkill('a/one', 'alpha');
    const firstCommit = repository.commit('alpha');
    repository.addSkill('b/two', 'beta');
    repository.addSkill('c/three', 'charlie');
    const secondCommit = repository.commit('beta and charlie');
    const rows = [
      inventoryRow({ slug: 'charlie', path: 'c/three', commit: secondCommit }),
      inventoryRow({ slug: 'alpha', path: 'a/one', commit: firstCommit, revision: 1 }),
      inventoryRow({ slug: 'beta', path: 'b/two', commit: secondCommit }),
    ];

    const plan = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows },
      batchSize: 1,
      startAfter: 'alpha',
    });
    assert.deepEqual(plan.selected.map((row) => row.slug), ['beta']);
    assert.equal(plan.nextStartAfter, 'beta');
    assert.equal(plan.remainingAfterBatch, 1);

    const resumed = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows },
      batchSize: 10,
      startAfter: plan.nextStartAfter,
    });
    assert.deepEqual(resumed.selected.map((row) => row.slug), ['charlie']);
    assert.equal(resumed.hasMore, false);
  } finally {
    repository.cleanup();
  }
});

test('fails closed when production identity cannot be reproduced from Git', () => {
  const repository = createRepository();
  try {
    repository.addSkill('owner/legacy', 'legacy-skill');
    const commit = repository.commit('legacy snapshot');
    assert.throws(() => buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: [inventoryRow({
        slug: 'legacy-skill',
        path: 'owner/legacy',
        commit,
        treeHash: 'c'.repeat(64),
      })] },
      batchSize: 10,
    }), /tree_hash mismatch/);
    assert.throws(() => buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: [inventoryRow({ slug: 'legacy-skill', path: 'missing/path', commit })] },
      batchSize: 10,
    }), /Git evidence check failed/);
  } finally {
    repository.cleanup();
  }
});

test('writes plan evidence from a production inventory file', () => {
  const repository = createRepository();
  try {
    repository.addSkill('owner/legacy', 'legacy-skill');
    const commit = repository.commit('legacy snapshot');
    const inventory = join(repository.root, 'inventory.json');
    const output = join(repository.root, 'plan.json');
    const pathsOutput = join(repository.root, 'paths.txt');
    writeFileSync(inventory, JSON.stringify({ rows: [
      inventoryRow({ slug: 'legacy-skill', path: 'owner/legacy', commit }),
    ] }));
    main([
      '--repository-root', repository.root,
      '--inventory', inventory,
      '--batch-size', '100',
      '--output', output,
      '--paths-output', pathsOutput,
    ]);
    assert.equal(JSON.parse(readFileSync(output, 'utf8')).selectedCount, 1);
    assert.equal(readFileSync(pathsOutput, 'utf8'), 'skills/owner/legacy\n');
  } finally {
    repository.cleanup();
  }
});

test('fetches an exact paginated production inventory without count drift', async () => {
  const rows = Array.from({ length: 1001 }, (_, index) => ({ slug: `skill-${index}` }));
  const ranges = [];
  const inventory = await fetchArtifactVersionInventory({
    supabaseUrl: 'https://database.example',
    serviceKey: 'secret',
    fetchImpl: async (_url, options) => {
      const [startText, endText] = options.headers.Range.split('-');
      const start = Number(startText);
      const end = Math.min(Number(endText), rows.length - 1);
      ranges.push(options.headers.Range);
      return new Response(JSON.stringify(rows.slice(start, end + 1)), {
        status: 206,
        headers: { 'content-range': `${start}-${end}/${rows.length}` },
      });
    },
  });
  assert.equal(inventory.count, 1001);
  assert.deepEqual(ranges, ['0-999', '1000-1999']);
});

test('workflow is pinned, evidence-producing, and isolated from normal fan-out', () => {
  const workflow = readFileSync(
    resolve(import.meta.dirname, '../../.github/workflows/backfill-artifact-versions.yml'),
    'utf8'
  );
  assert.match(workflow, /cli_version:/);
  assert.match(workflow, /fetch-artifact-version-inventory\.mjs/);
  assert.match(workflow, /fetch-depth: 0/);
  assert.match(workflow, /git archive/);
  assert.match(workflow, /--artifact-only/);
  assert.match(workflow, /--legacy-only/);
  assert.match(workflow, /actions\/upload-artifact@v6/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET/);
  assert.match(workflow, /https:\/\/skillstore\.io\/api\/cache\/invalidate/);
  assert.match(workflow, /--fail-with-body/);
  assert.match(workflow, /artifact-backfill-cache-invalidation\.json/);
  assert.match(workflow, /steps\.inputs\.outputs\.mode == 'execute'/);
  assert.match(workflow, /id: cache-invalidate/);
  assert.match(workflow, /CACHE_OUTCOME: \$\{\{ steps\.cache-invalidate\.outcome \}\}/);
  assert.doesNotMatch(workflow, /calculate-scores|trigger-translate|warm-cache/);
});
