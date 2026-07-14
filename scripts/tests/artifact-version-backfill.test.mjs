import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

import { fetchArtifactVersionInventory } from '../fetch-artifact-version-inventory.mjs';
import { buildArtifactBackfillPlan } from '../plan-artifact-version-backfill.mjs';
import {
  classifyArtifactVersionResults,
  verifyArtifactVersionExecution,
} from '../verify-artifact-version-classification.mjs';
import { verifyArtifactVersionReadback } from '../verify-artifact-version-backfill.mjs';

const HASH_A = 'a'.repeat(64);
const HASH_B = 'b'.repeat(64);
const HASH_C = 'c'.repeat(64);
const HASH_D = 'd'.repeat(64);
const SKILL_ID = '00000000-0000-4000-8000-000000000001';
const AUDIT_ID = '00000000-0000-4000-8000-000000000002';
const ARTIFACT_ID = '00000000-0000-4000-8000-000000000003';
const OBSERVATION_ID = '00000000-0000-4000-8000-000000000004';
const PACK_ID = '00000000-0000-4000-8000-000000000005';

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

function uuidFor(index) {
  return `00000000-0000-4000-8000-${String(index).padStart(12, '0')}`;
}

function inventoryRow({
  slug,
  path,
  commit,
  id = SKILL_ID,
  revision = 0,
  contentHash = HASH_A,
  treeHash = HASH_B,
}) {
  return {
    id,
    slug,
    plugin_path: `skills/${path}`,
    marketplace_commit_sha: commit,
    content_hash: contentHash,
    tree_hash: treeHash,
    artifact_revision: revision,
    current_artifact_version_id: revision > 0 ? ARTIFACT_ID : null,
    status: 'approved',
    public_eligible: true,
    public_eligibility_audit_id: AUDIT_ID,
    published_at: '2026-01-02T03:04:05.000Z',
    updated_at: '2026-07-14T16:50:53.000Z',
  };
}

function hashRepair(before, classification) {
  const exact = classification === 'exact';
  const legacyEquivalent = classification === 'legacy_algorithm_equivalent';
  return {
    requested: true,
    applied: false,
    classification,
    eligibleForExecution: exact,
    reason: exact
      ? 'report_matches_canonical_packaged_hashes'
      : legacyEquivalent
        ? 'report_matches_complete_legacy_scheme_but_audit_rebinding_is_required'
        : 'report_hashes_do_not_match_one_complete_known_scheme',
    contentHashMismatch: !exact,
    treeHashMismatch: !exact,
    reportContentHash: before.contentHash,
    reportContentHashScheme: exact
      ? 'skill_md_raw_bytes_v1'
      : legacyEquivalent
        ? 'skill_md_strip_version_trim_v1'
        : 'unproven',
    packagedContentHash: exact ? before.contentHash : HASH_C,
    packagedContentHashScheme: 'skill_md_raw_bytes_v1',
    reportTreeHash: before.treeHash,
    reportTreeHashScheme: exact
      ? 'canonical_entries_v1'
      : legacyEquivalent
        ? 'legacy_path_sha256_merkle_v1'
        : 'unproven',
    packagedTreeHash: exact ? before.treeHash : HASH_D,
    packagedTreeHashScheme: 'canonical_entries_v1',
    legacyCalculatedContentHash: legacyEquivalent ? before.contentHash : HASH_D,
    legacyCalculatedContentHashScheme: 'skill_md_strip_version_trim_v1',
    legacyCalculatedTreeHash: legacyEquivalent ? before.treeHash : HASH_C,
    legacyCalculatedTreeHashScheme: 'legacy_path_sha256_merkle_v1',
    observationTimeSource: exact ? 'report_generated_at' : 'backfill_execution_time',
    observedAt: exact ? '2026-01-01T00:00:00.000Z' : '2026-07-15T00:00:00.000Z',
  };
}

function dryRunResult(before, classification) {
  const repair = hashRepair(before, classification);
  return {
    slug: before.slug,
    skillId: before.id,
    success: true,
    blocked: classification !== 'exact',
    mode: 'dry-run',
    writeOccurred: false,
    artifact: {
      candidateAuthorVersion: '1.0.0',
      versionStatus: 'valid',
      contentHash: repair.packagedContentHash,
      treeHash: repair.packagedTreeHash,
      marketplaceCommit: before.marketplaceCommit,
      sourcePath: before.path,
      upstreamCommit: null,
      observedAt: repair.observedAt,
      observationTimeSource: repair.observationTimeSource,
      currentArtifactVersionId: null,
      currentRevision: 0,
      artifactVersionId: null,
      revision: null,
      created: null,
      changeKind: null,
      skillPublishedAt: before.publishedAt,
      skillUpdatedAt: before.updatedAt,
      publicEligible: before.publicEligible,
      publicEligibilityAuditId: before.publicEligibilityAuditId,
      hashRepair: repair,
    },
  };
}

function groupWrappers(plan, classificationBySlug) {
  return plan.batches.flatMap((batch) => batch.groups.map((group) => {
    const results = group.slugs.map((slug) => {
      const before = plan.selected.find((row) => row.slug === slug);
      return dryRunResult(before, classificationBySlug[slug]);
    });
    return {
      batchIndex: batch.index,
      marketplaceCommit: group.marketplaceCommit,
      selectedCount: group.count,
      exitCode: 0,
      result: {
        success: true,
        mode: 'dry-run',
        dryRun: true,
        artifactOnly: true,
        repairStaleReportHashes: true,
        synced: results.length,
        skipped: 0,
        blocked: results.filter((row) => row.blocked).length,
        errors: 0,
        slugs: results.map((row) => row.slug),
        results,
      },
    };
  }));
}

function executionResult(before) {
  const row = dryRunResult(before, 'exact');
  return {
    ...row,
    blocked: false,
    mode: 'artifact-only',
    writeOccurred: true,
    artifact: {
      ...row.artifact,
      artifactVersionId: ARTIFACT_ID,
      revision: 1,
      created: true,
      changeKind: 'initial',
    },
  };
}

function executionWrappers(plan, classification) {
  return classification.exactBatches.map((group) => {
    const results = group.slugs.map((slug) => executionResult(
      plan.selected.find((row) => row.slug === slug)
    ));
    return {
      batchIndex: group.batchIndex,
      marketplaceCommit: group.marketplaceCommit,
      selectedCount: group.count,
      exitCode: 0,
      result: {
        success: true,
        mode: 'artifact-only',
        dryRun: false,
        artifactOnly: true,
        repairStaleReportHashes: true,
        synced: results.length,
        skipped: 0,
        blocked: 0,
        errors: 0,
        slugs: results.map((row) => row.slug),
        results,
      },
    };
  });
}

test('plans a bounded legacy batch from pinned historical commits and paths', () => {
  const repository = createRepository();
  try {
    repository.addSkill('a/one', 'alpha');
    repository.addSkill('b/two', 'beta');
    repository.addSkill('c/three', 'charlie');
    const commit = repository.commit('snapshots');
    const rows = [
      inventoryRow({ slug: 'alpha', path: 'a/one', commit, id: uuidFor(10) }),
      inventoryRow({ slug: 'beta', path: 'b/two', commit, id: uuidFor(11) }),
      inventoryRow({ slug: 'charlie', path: 'c/three', commit, id: uuidFor(12) }),
    ];
    const plan = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: [rows[2], rows[0], rows[1]] },
      batchSize: 2,
    });
    assert.equal(plan.totalLegacy, 3);
    assert.deepEqual(plan.selected.map((row) => row.slug), ['alpha', 'beta']);
    assert.equal(plan.lastSelected, 'beta');
    assert.equal(plan.unclassifiedLegacyAfterBatch, 1);
    assert.equal(plan.batches.length, 1);
    assert.equal(plan.batches[0].count, 2);
  } finally {
    repository.cleanup();
  }
});

test('frozen execute ranges cannot slide forward after exact rows become versioned', () => {
  const repository = createRepository();
  try {
    repository.addSkill('a/one', 'alpha');
    repository.addSkill('b/two', 'beta');
    repository.addSkill('c/three', 'charlie');
    const commit = repository.commit('snapshots');
    const rows = [
      inventoryRow({ slug: 'alpha', path: 'a/one', commit, id: uuidFor(20), revision: 1 }),
      inventoryRow({ slug: 'beta', path: 'b/two', commit, id: uuidFor(21) }),
      inventoryRow({ slug: 'charlie', path: 'c/three', commit, id: uuidFor(22) }),
    ];
    const dryRun = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows },
      batchSize: 1,
      startAfter: 'alpha',
    });
    assert.deepEqual(dryRun.selected.map((row) => row.slug), ['beta']);

    const afterPartialExecute = rows.map((row) => row.slug === 'beta'
      ? { ...row, artifact_revision: 1, current_artifact_version_id: ARTIFACT_ID }
      : row);
    const replay = buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: afterPartialExecute },
      batchSize: 1,
      startAfter: 'alpha',
      endAt: 'beta',
    });
    assert.deepEqual(replay.selected, []);
    assert.equal(replay.selected.some((row) => row.slug === 'charlie'), false);
  } finally {
    repository.cleanup();
  }
});

test('fails closed on an oversized frozen range or unreproducible report identity', () => {
  const repository = createRepository();
  try {
    repository.addSkill('a/one', 'alpha');
    repository.addSkill('b/two', 'beta');
    const commit = repository.commit('snapshots');
    const rows = [
      inventoryRow({ slug: 'alpha', path: 'a/one', commit, id: uuidFor(30) }),
      inventoryRow({ slug: 'beta', path: 'b/two', commit, id: uuidFor(31) }),
    ];
    assert.throws(() => buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows },
      batchSize: 1,
      endAt: 'beta',
    }), /maximum is 1/);
    assert.throws(() => buildArtifactBackfillPlan({
      repositoryRoot: repository.root,
      inventory: { rows: [{ ...rows[0], tree_hash: HASH_C }] },
      batchSize: 1,
    }), /tree_hash mismatch/);
  } finally {
    repository.cleanup();
  }
});

test('fetches exact Skills then bounded Pack and artifact evidence', async () => {
  const skill = inventoryRow({
    slug: 'alpha',
    path: 'a/one',
    commit: 'a'.repeat(40),
  });
  const requestedTables = [];
  const inventory = await fetchArtifactVersionInventory({
    supabaseUrl: 'https://database.example',
    serviceKey: 'secret',
    scopeInventory: { selected: [{ id: skill.id }] },
    fetchImpl: async (input) => {
      const url = new URL(input);
      const table = url.pathname.split('/').at(-1);
      requestedTables.push(table);
      if (table === 'skills') {
        return new Response(JSON.stringify([skill]), {
          status: 206,
          headers: { 'content-range': '0-0/1' },
        });
      }
      return new Response('[]', { status: 200 });
    },
  });
  assert.equal(inventory.count, 1);
  assert.deepEqual(inventory.scopedSkillIds, [SKILL_ID]);
  assert.deepEqual(requestedTables, [
    'skills',
    'pack_skills',
    'skill_artifact_versions',
    'skill_artifact_observations',
  ]);
});

test('classifies every planned row and derives an exact-only execution cohort', () => {
  const commit = 'a'.repeat(40);
  const selected = ['alpha', 'beta', 'charlie'].map((slug, index) => ({
    id: uuidFor(40 + index),
    slug,
    path: `skills/owner/${slug}`,
    marketplaceCommit: commit,
    contentHash: HASH_A,
    treeHash: HASH_B,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publicEligibilityAuditId: AUDIT_ID,
    publishedAt: '2026-01-02T03:04:05.000Z',
    updatedAt: '2026-07-14T16:50:53.000Z',
  }));
  const plan = {
    selected,
    batches: [{
      index: 1,
      groups: [{
        marketplaceCommit: commit,
        count: 3,
        slugs: selected.map((row) => row.slug),
        paths: selected.map((row) => row.path),
      }],
    }],
  };
  const classification = classifyArtifactVersionResults({
    plan,
    groupResults: groupWrappers(plan, {
      alpha: 'exact',
      beta: 'legacy_algorithm_equivalent',
      charlie: 'actual_or_unproven_drift',
    }),
  });
  assert.deepEqual(classification.counts, {
    exact: 1,
    legacy_algorithm_equivalent: 1,
    actual_or_unproven_drift: 1,
  });
  assert.deepEqual(classification.exactBatches[0].slugs, ['alpha']);
  assert.equal(classification.remainingCohorts.total, 2);
});

test('classification rejects operational failures or incomplete evidence', () => {
  const before = {
    id: SKILL_ID,
    slug: 'alpha',
    path: 'skills/a/one',
    marketplaceCommit: 'a'.repeat(40),
    contentHash: HASH_A,
    treeHash: HASH_B,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publicEligibilityAuditId: AUDIT_ID,
    publishedAt: '2026-01-02T03:04:05.000Z',
    updatedAt: '2026-07-14T16:50:53.000Z',
  };
  const plan = {
    selected: [before],
    batches: [{ index: 1, groups: [{
      marketplaceCommit: before.marketplaceCommit,
      count: 1,
      slugs: [before.slug],
      paths: [before.path],
    }] }],
  };
  const wrappers = groupWrappers(plan, { alpha: 'exact' });
  wrappers[0].exitCode = 1;
  assert.throws(() => classifyArtifactVersionResults({ plan, groupResults: wrappers }), /summary\/exit/);
  assert.throws(() => classifyArtifactVersionResults({ plan, groupResults: [] }), /group count mismatch/);
  const wrongSlugs = groupWrappers(plan, { alpha: 'exact' });
  wrongSlugs[0].result.slugs = ['different'];
  assert.throws(
    () => classifyArtifactVersionResults({ plan, groupResults: wrongSlugs }),
    /top-level slugs/
  );
});

test('execution verifier accepts only the exact cohort', () => {
  const before = {
    id: SKILL_ID,
    slug: 'alpha',
    path: 'skills/a/one',
    marketplaceCommit: 'a'.repeat(40),
    contentHash: HASH_A,
    treeHash: HASH_B,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publicEligibilityAuditId: AUDIT_ID,
    publishedAt: '2026-01-02T03:04:05.000Z',
    updatedAt: '2026-07-14T16:50:53.000Z',
  };
  const plan = {
    selected: [before],
    batches: [{ index: 1, groups: [{
      marketplaceCommit: before.marketplaceCommit,
      count: 1,
      slugs: [before.slug],
      paths: [before.path],
    }] }],
  };
  const classification = classifyArtifactVersionResults({
    plan,
    groupResults: groupWrappers(plan, { alpha: 'exact' }),
  });
  const execution = verifyArtifactVersionExecution({
    plan,
    classification,
    groupResults: executionWrappers(plan, classification),
  });
  assert.equal(execution.executedCount, 1);
  const invalid = executionWrappers(plan, classification);
  invalid[0].result.results[0].artifact.hashRepair.classification = 'legacy_algorithm_equivalent';
  assert.throws(() => verifyArtifactVersionExecution({
    plan,
    classification,
    groupResults: invalid,
  }), /hash classification/);
});

function readbackFixture() {
  const raw = inventoryRow({
    slug: 'alpha',
    path: 'a/one',
    commit: 'a'.repeat(40),
  });
  const planned = {
    id: raw.id,
    slug: raw.slug,
    path: raw.plugin_path,
    marketplaceCommit: raw.marketplace_commit_sha,
    contentHash: raw.content_hash,
    treeHash: raw.tree_hash,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: raw.status,
    publicEligible: raw.public_eligible,
    publicEligibilityAuditId: raw.public_eligibility_audit_id,
    publishedAt: raw.published_at,
    updatedAt: raw.updated_at,
  };
  const plan = { selected: [planned] };
  const packMemberships = [{ skill_id: SKILL_ID, pack_id: PACK_ID }];
  const packs = [{
    id: PACK_ID,
    slug: 'demo-pack',
    published_at: '2026-01-01T00:00:00.000Z',
    updated_at: '2026-02-01T00:00:00.000Z',
  }];
  const preInventory = {
    scopedSkillIds: [SKILL_ID],
    rows: [raw],
    packMemberships,
    packs,
    artifacts: [],
    observations: [],
  };
  return { raw, planned, plan, preInventory };
}

test('dry-run readback proves Skill, Pack, artifact, and observation immutability', () => {
  const { planned, plan, preInventory } = readbackFixture();
  const classification = {
    classifiedCount: 1,
    cohorts: {
      exact: [{ ...planned }],
      legacy_algorithm_equivalent: [],
      actual_or_unproven_drift: [],
    },
    remainingCohorts: { legacyAlgorithmEquivalent: 0, actualOrUnprovenDrift: 0, total: 0 },
  };
  const readback = verifyArtifactVersionReadback({
    mode: 'dry-run',
    plan,
    classification,
    execution: { evidence: [] },
    preInventory,
    postInventory: structuredClone(preInventory),
  });
  assert.equal(readback.verifiedCount, 1);
  const drift = structuredClone(preInventory);
  drift.packs[0].updated_at = '2026-07-15T00:00:00.000Z';
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'dry-run', plan, classification, execution: { evidence: [] }, preInventory, postInventory: drift,
  }), /Dependent Pack timestamps changed/);
});

test('execute readback proves exact artifact hash provenance and observation identity', () => {
  const { raw, planned, plan, preInventory } = readbackFixture();
  const result = executionResult(planned);
  const classification = {
    classifiedCount: 1,
    cohorts: {
      exact: [{ ...planned }],
      legacy_algorithm_equivalent: [],
      actual_or_unproven_drift: [],
    },
    remainingCohorts: { legacyAlgorithmEquivalent: 0, actualOrUnprovenDrift: 0, total: 0 },
  };
  const repair = result.artifact.hashRepair;
  const postInventory = {
    ...structuredClone(preInventory),
    rows: [{ ...raw, artifact_revision: 1, current_artifact_version_id: ARTIFACT_ID }],
    artifacts: [{
      id: ARTIFACT_ID,
      skill_id: SKILL_ID,
      artifact_revision: 1,
      upstream_version_raw: '1.0.0',
      upstream_version_normalized: '1.0.0',
      upstream_version_source: 'version',
      upstream_version_status: 'valid',
      content_hash: HASH_A,
      tree_hash: HASH_B,
      upstream_commit_sha: null,
      marketplace_commit_sha: planned.marketplaceCommit,
      source_path: planned.path,
      previous_version_id: null,
      change_kind: 'initial',
      observed_at: result.artifact.observedAt,
      created_at: '2026-07-15T00:00:01.000Z',
      install_snapshot_hash: HASH_C,
      snapshot_status: 'exact',
      readme_template_version: 3,
      artifact_builder_version: 1,
      hash_provenance: {
        schemaVersion: 1,
        classification: 'exact',
        report: {
          contentHash: repair.reportContentHash,
          contentHashScheme: repair.reportContentHashScheme,
          treeHash: repair.reportTreeHash,
          treeHashScheme: repair.reportTreeHashScheme,
        },
        packaged: {
          contentHash: repair.packagedContentHash,
          contentHashScheme: repair.packagedContentHashScheme,
          treeHash: repair.packagedTreeHash,
          treeHashScheme: repair.packagedTreeHashScheme,
        },
        legacyCalculated: {
          contentHash: repair.legacyCalculatedContentHash,
          contentHashScheme: repair.legacyCalculatedContentHashScheme,
          treeHash: repair.legacyCalculatedTreeHash,
          treeHashScheme: repair.legacyCalculatedTreeHashScheme,
        },
        observationTimeSource: repair.observationTimeSource,
      },
    }],
    observations: [{
      id: OBSERVATION_ID,
      skill_id: SKILL_ID,
      artifact_version_id: ARTIFACT_ID,
      marketplace_commit_sha: planned.marketplaceCommit,
      source_path: planned.path,
      upstream_commit_sha: null,
      observed_at: result.artifact.observedAt,
      created_at: '2026-07-15T00:00:01.000Z',
    }],
  };
  const readback = verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory,
  });
  assert.equal(readback.executedCount, 1);

  const equivalentUtcOffset = structuredClone(postInventory);
  equivalentUtcOffset.artifacts[0].observed_at = '2026-01-01T00:00:00.000+00:00';
  equivalentUtcOffset.observations[0].observed_at = '2026-01-01T00:00:00.000+00:00';
  const offsetReadback = verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory: equivalentUtcOffset,
  });
  assert.equal(offsetReadback.executedCount, 1);

  const invalidObservedAt = structuredClone(postInventory);
  invalidObservedAt.artifacts[0].observed_at = '2026-02-31T00:00:00.000Z';
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory: invalidObservedAt,
  }), /install identity\/hash provenance readback mismatch/);

  const microsecondDrift = structuredClone(postInventory);
  microsecondDrift.observations[0].observed_at = '2026-01-01T00:00:00.000001+00:00';
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory: microsecondDrift,
  }), /Artifact observation readback mismatch/);

  const installIdentityDrift = structuredClone(postInventory);
  installIdentityDrift.artifacts[0].upstream_version_status = 'missing';
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory: installIdentityDrift,
  }), /install identity\/hash provenance readback mismatch/);
  postInventory.artifacts[0].hash_provenance.packaged.treeHash = HASH_D;
  assert.throws(() => verifyArtifactVersionReadback({
    mode: 'execute',
    plan,
    classification,
    execution: { evidence: [{ slug: planned.slug, result }] },
    preInventory,
    postInventory,
  }), /install identity\/hash provenance readback mismatch/);
});

test('workflow is bounded, exact-only, cursor-safe, and evidence-producing', () => {
  const workflow = readFileSync(
    resolve(import.meta.dirname, '../../.github/workflows/backfill-artifact-versions.yml'),
    'utf8'
  );
  const inventoryFetcher = readFileSync(
    resolve(import.meta.dirname, '../fetch-artifact-version-inventory.mjs'),
    'utf8'
  );
  assert.match(workflow, /default: '2\.2\.2'/);
  assert.match(workflow, /CLI_VERSION" != "2\.2\.2"/);
  assert.match(workflow, /sparse-checkout: ''/);
  assert.match(workflow, /sparse-checkout-cone-mode: false/);
  const checkoutGuard = workflow.indexOf('name: Normalize full checkout and verify backfill runtime');
  const firstProductionRead = workflow.indexOf('name: Fetch exact production Skill catalog');
  assert.ok(checkoutGuard > workflow.indexOf('uses: actions/checkout@v5'));
  assert.ok(checkoutGuard < firstProductionRead);
  const checkoutGuardBlock = workflow.slice(checkoutGuard, firstProductionRead);
  assert.match(checkoutGuardBlock, /checked_out_sha=\$\(git rev-parse HEAD\)/);
  assert.match(checkoutGuardBlock, /"\$checked_out_sha" != "\$GITHUB_SHA"/);
  assert.match(checkoutGuardBlock, /git sparse-checkout disable[\s\S]*git reset --hard HEAD/);
  assert.match(checkoutGuardBlock, /if \[ ! -f "\$required_path" \]/);
  for (const requiredPath of [
    '.github/actions/download-skillstore-cli/action.yml',
    'scripts/fetch-artifact-version-inventory.mjs',
    'scripts/plan-artifact-version-backfill.mjs',
    'scripts/verify-artifact-version-classification.mjs',
    'scripts/verify-artifact-version-backfill.mjs',
  ]) {
    assert.ok(checkoutGuardBlock.includes(requiredPath), `${requiredPath} must be verified before production reads`);
  }
  assert.match(workflow, /batch_size must be an integer between 1 and 500/);
  assert.match(workflow, /execute requires the frozen end_at slug/);
  assert.match(workflow, /--repair-stale-report-hashes/);
  assert.match(workflow, /--dry-run/);
  assert.match(workflow, /\.exactBatches\[\]/);
  assert.match(workflow, /No completion cursor is published/);
  assert.doesNotMatch(workflow, /legacyAtOrBeforeCursor.*exit|Verified resume cursor|status: "complete"/);
  assert.match(workflow, /verify-artifact-version-classification\.mjs/);
  assert.match(workflow, /verify-artifact-version-backfill\.mjs/);
  assert.match(workflow, /OFFSET \+= 10/);
  assert.match(workflow, /\.slugs == \$requested/);
  assert.doesNotMatch(workflow, /OFFSET \+= 50|OFFSET \/ 50|OFFSET:50/);
  assert.match(workflow, /\.evidence\[\]\.slug/);
  assert.match(inventoryFetcher, /hash_provenance/);
  assert.match(inventoryFetcher, /packMemberships/);
  assert.match(workflow, /actions\/upload-artifact@v6/);
  assert.doesNotMatch(workflow, /calculate-scores|trigger-translate|warm-cache/);
});
