import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import {
  createLegacyGovernanceBoundary,
  verifyLegacyGovernanceBoundary,
  verifyLegacyGovernanceExecution,
} from '../verify-legacy-equivalent-governance.mjs';
import {
  fetchLegacyGovernanceReadback,
  fetchLegacyGovernanceSourceEvidence,
} from '../fetch-legacy-equivalent-governance-readback.mjs';

const SKILL_ID = '00000000-0000-4000-8000-000000000001';
const SOURCE_AUDIT_ID = '10000000-0000-4000-8000-000000000001';
const DERIVED_AUDIT_ID = '20000000-0000-4000-8000-000000000001';
const ARTIFACT_ID = '30000000-0000-4000-8000-000000000001';
const SNAPSHOT_ID = '40000000-0000-4000-8000-000000000001';
const COMMIT = 'a'.repeat(40);
const LEGACY_CONTENT = 'b'.repeat(64);
const LEGACY_TREE = 'c'.repeat(64);
const CONTENT = 'd'.repeat(64);
const TREE = 'e'.repeat(64);

function frozenRow() {
  return {
    id: SKILL_ID,
    slug: 'owner-image',
    path: 'skills/owner/image',
    marketplaceCommit: COMMIT,
    contentHash: LEGACY_CONTENT,
    treeHash: LEGACY_TREE,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publicEligibilityAuditId: SOURCE_AUDIT_ID,
    publishedAt: '2026-01-01T00:00:00.000Z',
    updatedAt: '2026-01-02T00:00:00.000Z',
    evidence: {
      artifact: {
        contentHash: CONTENT,
        treeHash: TREE,
        hashRepair: {
          reportContentHash: LEGACY_CONTENT,
          reportTreeHash: LEGACY_TREE,
          packagedContentHash: CONTENT,
          packagedTreeHash: TREE,
        },
      },
    },
  };
}

function fixtures() {
  const row = frozenRow();
  const plan = {
    schemaVersion: 3,
    selectedCount: 1,
    selected: [row],
    lastSelected: row.slug,
    batches: [{
      index: 1,
      groups: [{
        marketplaceCommit: COMMIT,
        count: 1,
        slugs: [row.slug],
        paths: [row.path],
      }],
    }],
  };
  const classification = {
    schemaVersion: 1,
    status: 'classified',
    counts: { exact: 0, legacy_algorithm_equivalent: 1, actual_or_unproven_drift: 0 },
    cohorts: { exact: [], legacy_algorithm_equivalent: [row], actual_or_unproven_drift: [] },
  };
  const rawSkill = {
    id: SKILL_ID,
    slug: row.slug,
    plugin_path: row.path,
    marketplace_commit_sha: COMMIT,
    content_hash: LEGACY_CONTENT,
    tree_hash: LEGACY_TREE,
    artifact_revision: 0,
    current_artifact_version_id: null,
    status: 'approved',
    public_eligible: true,
    public_eligibility_audit_id: SOURCE_AUDIT_ID,
    published_at: row.publishedAt,
    updated_at: row.updatedAt,
  };
  const preInventory = {
    scopedSkillIds: [SKILL_ID],
    rows: [rawSkill],
    packMemberships: [{ skill_id: SKILL_ID, pack_id: '50000000-0000-4000-8000-000000000001' }],
    packs: [{
      id: '50000000-0000-4000-8000-000000000001',
      slug: 'image-pack',
      published_at: '2026-01-03T00:00:00.000Z',
      updated_at: '2026-01-04T00:00:00.000Z',
    }],
    artifacts: [],
    observations: [],
  };
  const dryRunResults = [{
    batchIndex: 1,
    marketplaceCommit: COMMIT,
    selectedCount: 1,
    slugs: [row.slug],
    exitCode: 0,
    result: {
      success: true,
      mode: 'dry-run',
      governed: 0,
      validated: 1,
      results: [{
        slug: row.slug,
        mode: 'dry-run',
        skillId: SKILL_ID,
        sourceAuditId: SOURCE_AUDIT_ID,
        derivedAuditId: null,
        artifactVersionId: null,
        artifactRevision: null,
        artifactCreated: null,
        scoreSnapshotId: null,
      }],
    },
  }];
  const sourceEvidence = {
    schemaVersion: 1,
    status: 'source_evidence_fetched',
    skillIds: [SKILL_ID],
    skills: [{
      id: SKILL_ID,
      slug: row.slug,
      name: 'Image',
      description: 'Legacy image skill',
      author_name: 'owner',
      supported_tools: ['claude', 'codex'],
      file_structure: [{ name: 'SKILL.md', type: 'file' }],
    }],
    audits: [{ id: SOURCE_AUDIT_ID, skill_id: SKILL_ID, version: 7, audit_payload_hash: 'f'.repeat(32) }],
  };
  return { row, plan, classification, rawSkill, preInventory, dryRunResults, sourceEvidence };
}

function createBoundaryFixture() {
  const values = fixtures();
  const directory = mkdtempSync(join(tmpdir(), 'legacy-governance-test-'));
  const files = {
    plan: join(directory, 'plan.json'),
    classification: join(directory, 'classification.json'),
    preInventory: join(directory, 'pre-inventory.json'),
    dryRunResults: join(directory, 'dry-run.json'),
    sourceEvidence: join(directory, 'source-evidence.json'),
  };
  writeFileSync(files.plan, JSON.stringify(values.plan));
  writeFileSync(files.classification, JSON.stringify(values.classification));
  writeFileSync(files.preInventory, JSON.stringify(values.preInventory));
  writeFileSync(files.dryRunResults, JSON.stringify(values.dryRunResults));
  writeFileSync(files.sourceEvidence, JSON.stringify(values.sourceEvidence));
  const boundary = createLegacyGovernanceBoundary({
    plan: values.plan,
    classification: values.classification,
    dryRunResults: values.dryRunResults,
    paths: files,
    metadata: {
      runId: '12345',
      repository: 'aiskillstore/marketplace',
      workflowCommit: 'f'.repeat(40),
      cliVersion: '2.4.0',
      cliSha256: '9'.repeat(64),
    },
  });
  return { ...values, directory, files, boundary };
}

test('freezes and verifies one exact dry-run boundary', () => {
  const fixture = createBoundaryFixture();
  try {
    assert.equal(fixture.boundary.status, 'frozen');
    assert.equal(fixture.boundary.legacyCount, 1);
    const verified = verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: structuredClone(fixture.preInventory),
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: structuredClone(fixture.sourceEvidence),
      paths: fixture.files,
      expectedRunId: '12345',
    });
    assert.equal(verified.status, 'execution_preflight_verified');
    const drift = structuredClone(fixture.preInventory);
    drift.rows[0].updated_at = '2026-07-15T00:00:00.000Z';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: drift,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /production state changed/);
    const resumable = structuredClone(fixture.preInventory);
    resumable.rows[0] = {
      ...resumable.rows[0],
      content_hash: CONTENT,
      tree_hash: TREE,
      artifact_revision: 1,
      current_artifact_version_id: ARTIFACT_ID,
      public_eligibility_audit_id: DERIVED_AUDIT_ID,
    };
    resumable.artifacts = [{
      id: ARTIFACT_ID,
      skill_id: SKILL_ID,
      artifact_revision: 1,
      content_hash: CONTENT,
      tree_hash: TREE,
      marketplace_commit_sha: COMMIT,
      source_path: fixture.row.path,
      hash_provenance: {
        classification: 'legacy_algorithm_equivalent',
        report: { contentHash: LEGACY_CONTENT, treeHash: LEGACY_TREE },
      },
    }];
    resumable.observations = [{
      skill_id: SKILL_ID,
      artifact_version_id: ARTIFACT_ID,
      marketplace_commit_sha: COMMIT,
      source_path: fixture.row.path,
    }];
    const resumed = verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: resumable,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    });
    assert.equal(resumed.resumableCount, 1);
    const changedAudit = structuredClone(fixture.sourceEvidence);
    changedAudit.audits[0].summary = 'changed after dry-run';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: fixture.preInventory,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: changedAudit,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /source audit changed/);
  } finally {
    rmSync(fixture.directory, { recursive: true, force: true });
  }
});

test('verifies artifact, derived audit, score, Pack, and attestation execution evidence', () => {
  const fixture = createBoundaryFixture();
  try {
    const result = {
      slug: fixture.row.slug,
      mode: 'execute',
      skillId: SKILL_ID,
      sourceAuditId: SOURCE_AUDIT_ID,
      derivedAuditId: DERIVED_AUDIT_ID,
      artifactVersionId: ARTIFACT_ID,
      artifactRevision: 1,
      artifactCreated: true,
      scoreSnapshotId: SNAPSHOT_ID,
    };
    const executionResults = [{
      batchIndex: 1,
      marketplaceCommit: COMMIT,
      selectedCount: 1,
      slugs: [fixture.row.slug],
      exitCode: 0,
      result: { success: true, mode: 'execute', governed: 1, validated: 1, results: [result] },
    }];
    const postInventory = {
      ...structuredClone(fixture.preInventory),
      rows: [{
        ...fixture.rawSkill,
        content_hash: CONTENT,
        tree_hash: TREE,
        artifact_revision: 1,
        current_artifact_version_id: ARTIFACT_ID,
        public_eligibility_audit_id: DERIVED_AUDIT_ID,
      }],
      artifacts: [{
        id: ARTIFACT_ID,
        skill_id: SKILL_ID,
        artifact_revision: 1,
        content_hash: CONTENT,
        tree_hash: TREE,
        marketplace_commit_sha: COMMIT,
        source_path: fixture.row.path,
        hash_provenance: {
          classification: 'legacy_algorithm_equivalent',
          report: { contentHash: LEGACY_CONTENT, treeHash: LEGACY_TREE },
          packaged: { contentHash: CONTENT, treeHash: TREE },
        },
      }],
      observations: [{
        skill_id: SKILL_ID,
        artifact_version_id: ARTIFACT_ID,
        marketplace_commit_sha: COMMIT,
        source_path: fixture.row.path,
      }],
    };
    const readback = {
      skills: [{
        ...fixture.sourceEvidence.skills[0],
        current_quality_score_snapshot_id: SNAPSHOT_ID,
        quality_score: 88,
      }],
      audits: [
        { ...fixture.sourceEvidence.audits[0] },
        {
          id: DERIVED_AUDIT_ID,
          skill_id: SKILL_ID,
          version: 8,
          derived_from_audit_id: SOURCE_AUDIT_ID,
          derivation_kind: 'legacy_algorithm_equivalent_hash_rebind',
          subject_content_hash: CONTENT,
          subject_tree_hash: TREE,
        },
      ],
      scoreSnapshots: [{
        id: SNAPSHOT_ID,
        skill_id: SKILL_ID,
        score_subject: {
          auditId: DERIVED_AUDIT_ID,
          auditVersion: 8,
          contentHash: CONTENT,
          treeHash: TREE,
        },
      }],
      scoreBreakdowns: [{ skill_id: SKILL_ID, score_snapshot_id: SNAPSHOT_ID, stale_at: null, stale_reason: null }],
      attestations: [],
    };
    const verified = verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
    });
    assert.equal(verified.executedCount, 1);
    readback.scoreSnapshots[0].score_subject.auditId = SOURCE_AUDIT_ID;
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
    }), /production readback mismatch/);
    readback.scoreSnapshots[0].score_subject.auditId = DERIVED_AUDIT_ID;
    readback.audits[0].summary = 'changed during execution';
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
    }), /production readback mismatch/);
  } finally {
    rmSync(fixture.directory, { recursive: true, force: true });
  }
});

test('fetches bounded independent governance readback tables', async () => {
  const executionResults = [{ result: { results: [{
    skillId: SKILL_ID,
    sourceAuditId: SOURCE_AUDIT_ID,
    derivedAuditId: DERIVED_AUDIT_ID,
    scoreSnapshotId: SNAPSHOT_ID,
  }] } }];
  const requested = [];
  const fetchImpl = async (url, options) => {
    requested.push({ table: url.pathname.split('/').at(-1), auth: options.headers.Authorization });
    return { ok: true, json: async () => [] };
  };
  const output = await fetchLegacyGovernanceReadback({
    supabaseUrl: 'https://db.example.test',
    serviceKey: 'service-key',
    executionResults,
    fetchImpl,
  });
  assert.equal(output.schemaVersion, 1);
  assert.deepEqual(requested.map((entry) => entry.table).sort(), [
    'security_audit_attestations',
    'skill_quality_breakdown',
    'skill_quality_score_snapshots',
    'skill_security_audit',
    'skills',
  ]);
  assert.ok(requested.every((entry) => entry.auth === 'Bearer service-key'));
});

test('freezes the complete source audit row and unhashed Skill install metadata', async () => {
  const classification = fixtures().classification;
  const fetchImpl = async (url) => {
    const table = url.pathname.split('/').at(-1);
    if (table === 'skills') {
      return { ok: true, json: async () => [{ id: SKILL_ID, name: 'Image', file_structure: [] }] };
    }
    assert.equal(url.searchParams.get('select'), '*');
    return { ok: true, json: async () => [{ id: SOURCE_AUDIT_ID, skill_id: SKILL_ID, version: 7 }] };
  };
  const output = await fetchLegacyGovernanceSourceEvidence({
    supabaseUrl: 'https://db.example.test',
    serviceKey: 'service-key',
    classification,
    fetchImpl,
  });
  assert.equal(output.skills.length, 1);
  assert.equal(output.audits[0].id, SOURCE_AUDIT_ID);
});

test('workflow is two-phase, exactly pinned, bounded, and never executes ordinary sync', () => {
  const workflow = readFileSync(
    resolve(import.meta.dirname, '../../.github/workflows/govern-legacy-equivalent-artifacts.yml'),
    'utf8'
  );
  const ordinaryWorkflow = readFileSync(
    resolve(import.meta.dirname, '../../.github/workflows/backfill-artifact-versions.yml'),
    'utf8'
  );
  assert.match(workflow, /default: '2\.4\.0'/);
  assert.match(workflow, /test "\$CLI_VERSION" = '2\.4\.0'/);
  assert.doesNotMatch(workflow, /version:\s*(latest|'latest'|"latest")/);
  assert.match(workflow, /batch_size must be between 1 and 500/);
  assert.match(workflow, /dry_run_id/);
  assert.match(workflow, /gh run download "\$DRY_RUN_ID"/);
  assert.match(workflow, /headBranch == "main"/);
  assert.match(workflow, /git merge-base --is-ancestor/);
  assert.match(workflow, /boundaries may only be created from main/);
  assert.match(workflow, /execute may only run from main/);
  assert.match(workflow, /sha256sum --check SHA256SUMS/);
  assert.match(workflow, /CLI 2\.4\.0 binary differs from the frozen dry-run boundary/);
  assert.ok((workflow.match(/eec024fd85af15a50103b80bfca2e00dcc30f62f94f1dbb32c7a5eba0061b461/g) || []).length >= 2);
  assert.match(workflow, /--phase execute-preflight/);
  assert.match(workflow, /skill govern-legacy-equivalent/);
  assert.match(workflow, /cache batches of at most ten/);
  assert.match(workflow, /--concurrency 1/);
  assert.match(workflow, /legacy-equivalent-boundary-/);
  assert.match(workflow, /legacy-equivalent-execution-/);
  assert.match(workflow, /legacy-equivalent-failed-dry-run-/);
  assert.match(workflow, /Preserve execution status evidence/);
  const syncCalls = workflow.match(/skill sync[\s\S]{0,250}/g) || [];
  assert.equal(syncCalls.length, 1);
  assert.match(syncCalls[0], /--dry-run/);
  assert.match(syncCalls[0], /--repair-stale-report-hashes/);
  assert.match(ordinaryWorkflow, /\.exactBatches\[\]/);
  assert.match(ordinaryWorkflow, /CLI_VERSION" != "2\.3\.1"/);
});
