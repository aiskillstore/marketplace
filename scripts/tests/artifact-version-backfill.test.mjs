import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

import { fetchArtifactVersionInventory } from '../fetch-artifact-version-inventory.mjs';
import { buildArtifactBackfillPlan, main } from '../plan-artifact-version-backfill.mjs';
import { verifyArtifactVersionReadback } from '../verify-artifact-version-backfill.mjs';

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
    current_artifact_version_id: revision > 0 ? '123e4567-e89b-42d3-a456-426614174000' : null,
    status: 'approved',
    public_eligible: true,
    published_at: '2026-01-02T03:04:05.000Z',
    updated_at: '2026-07-14T16:50:53.000Z',
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
    assert.equal(plan.selected[0].status, 'approved');
    assert.equal(plan.selected[0].publicEligible, true);
    assert.equal(plan.selected[0].currentArtifactVersionId, null);
    assert.equal(plan.selected[0].publishedAt, '2026-01-02T03:04:05.000Z');
    assert.equal(plan.selected[0].updatedAt, '2026-07-14T16:50:53.000Z');
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

test('readback proves dry-run immutability and execute initialization', () => {
  const commit = 'a'.repeat(40);
  const before = {
    slug: 'legacy-skill',
    path: 'skills/owner/legacy',
    marketplaceCommit: commit,
    contentHash: HASH_A,
    treeHash: HASH_B,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publishedAt: '2026-01-02T03:04:05.000Z',
    updatedAt: '2026-07-14T16:50:53.000Z',
  };
  const unchanged = inventoryRow({ slug: before.slug, path: 'owner/legacy', commit });
  const dryRun = verifyArtifactVersionReadback({
    mode: 'dry-run',
    plan: { selected: [before] },
    postInventory: { rows: [unchanged] },
  });
  assert.equal(dryRun.verifiedCount, 1);

  const initialized = {
    ...unchanged,
    artifact_revision: 1,
    current_artifact_version_id: '123e4567-e89b-42d3-a456-426614174000',
  };
  const execute = verifyArtifactVersionReadback({
    mode: 'execute',
    plan: { selected: [before] },
    postInventory: { rows: [initialized] },
  });
  assert.equal(execute.evidence[0].after.artifactRevision, 1);
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan: { selected: [before] },
    postInventory: { rows: [{ ...initialized, artifact_revision: 2 }] },
  }), /unexpected artifact_revision/);
});

test('readback fails closed on visibility or immutable identity drift', () => {
  const commit = 'a'.repeat(40);
  const before = {
    slug: 'legacy-skill',
    path: 'skills/owner/legacy',
    marketplaceCommit: commit,
    contentHash: HASH_A,
    treeHash: HASH_B,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publishedAt: '2026-01-02T03:04:05.000Z',
    updatedAt: '2026-07-14T16:50:53.000Z',
  };
  const changed = {
    ...inventoryRow({ slug: before.slug, path: 'owner/legacy', commit }),
    artifact_revision: 1,
    current_artifact_version_id: '123e4567-e89b-42d3-a456-426614174000',
    public_eligible: false,
  };
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan: { selected: [before] },
    postInventory: { rows: [changed] },
  }), /publicEligible changed/);
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'dry-run',
    plan: { selected: [before] },
    postInventory: { rows: [{ ...changed, public_eligible: true }] },
  }), /Dry-run changed artifact_revision/);
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan: { selected: [before] },
    postInventory: { rows: [{ ...changed, public_eligible: true, published_at: '2026-07-15T00:00:00.000Z' }] },
  }), /publishedAt changed/);
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'dry-run',
    plan: { selected: [before] },
    postInventory: { rows: [{ ...inventoryRow({ slug: before.slug, path: 'owner/legacy', commit }), published_at: '2026-07-15T00:00:00.000Z' }] },
  }), /publishedAt changed/);
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan: { selected: [before] },
    postInventory: { rows: [{ ...changed, public_eligible: true, updated_at: '2026-07-15T00:00:00.000Z' }] },
  }), /updatedAt changed/);
});

test('workflow is pinned, evidence-producing, and isolated from normal fan-out', () => {
  const workflow = readFileSync(
    resolve(import.meta.dirname, '../../.github/workflows/backfill-artifact-versions.yml'),
    'utf8'
  );
  const inventoryFetcher = readFileSync(
    resolve(import.meta.dirname, '../fetch-artifact-version-inventory.mjs'),
    'utf8'
  );
  assert.match(workflow, /cli_version:/);
  assert.match(workflow, /default: '2\.2\.1'/);
  assert.match(workflow, /CLI_VERSION" != "2\.2\.1"/);
  assert.match(workflow, /fetch-artifact-version-inventory\.mjs/);
  assert.match(workflow, /fetch-depth: 0/);
  assert.match(workflow, /git archive/);
  assert.match(workflow, /--artifact-only/);
  assert.match(workflow, /--legacy-only/);
  assert.match(workflow, /actions\/upload-artifact@v6/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET: \$\{\{ secrets\.CACHE_INVALIDATE_SECRET \}\}/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET:\?CACHE_INVALIDATE_SECRET is required for execute mode/);
  assert.match(workflow, /jq -r '\.selected\[\]\.slug'/);
  assert.match(workflow, /https:\/\/skillstore\.io\/api\/cache\/invalidate/);
  assert.match(workflow, /--fail-with-body/);
  assert.match(workflow, /artifact-backfill-cache-invalidation\.json/);
  assert.match(workflow, /artifact-backfill-inventory-post\.json/);
  assert.match(workflow, /verify-artifact-version-backfill\.mjs/);
  assert.match(inventoryFetcher, /current_artifact_version_id/);
  assert.match(inventoryFetcher, /public_eligible/);
  assert.match(inventoryFetcher, /published_at/);
  assert.match(inventoryFetcher, /updated_at/);
  assert.match(workflow, /OFFSET \+= 10/);
  assert.match(workflow, /OFFSET \/ 10 \+ 1/);
  assert.doesNotMatch(workflow, /OFFSET \+= 50|OFFSET \/ 50|OFFSET:50/);
  assert.match(workflow, /steps\.inputs\.outputs\.mode == 'execute'/);
  assert.match(workflow, /id: cache-invalidate/);
  assert.match(workflow, /steps\.readback\.outcome == 'success'/);
  assert.ok(
    workflow.indexOf('id: readback') < workflow.indexOf('id: cache-invalidate'),
    'production readback must pass before cache invalidation publishes the new projection'
  );
  assert.match(workflow, /CACHE_OUTCOME: \$\{\{ steps\.cache-invalidate\.outcome \}\}/);
  assert.doesNotMatch(workflow, /calculate-scores|trigger-translate|warm-cache/);
});
