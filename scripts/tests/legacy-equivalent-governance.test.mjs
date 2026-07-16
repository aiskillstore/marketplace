import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import {
  canonicalSourceEvidence,
  createLegacyGovernanceBoundary,
  qualifyLegacyGovernanceClassification,
  validateLegacyPreviousReportManifest,
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

test('canonicalizes source evidence row order without hiding value drift', () => {
  const left = {
    schemaVersion: 1,
    skills: [{ id: '2', name: 'Second' }, { id: '1', name: 'First' }],
    audits: [{ id: 'a', version: 1 }, { id: 'b', version: 2 }],
  };
  const reordered = structuredClone(left);
  reordered.skills.reverse();
  reordered.audits.reverse();
  assert.equal(canonicalSourceEvidence(left), canonicalSourceEvidence(reordered));
  reordered.audits[0].version = 3;
  assert.notEqual(canonicalSourceEvidence(left), canonicalSourceEvidence(reordered));
});

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
  const { evidence: _classificationOnlyEvidence, ...plannedRow } = row;
  const plan = {
    schemaVersion: 3,
    selectedCount: 1,
    selected: [plannedRow],
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
  const hashClassification = {
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
    audits: [{
      id: SOURCE_AUDIT_ID,
      skill_id: SKILL_ID,
      version: 7,
      content_hash: `v2:${COMMIT}:${LEGACY_CONTENT}:${LEGACY_TREE}:${'f'.repeat(32)}`,
      audit_payload_hash: null,
      subject_marketplace_commit_sha: null,
      subject_content_hash: null,
      subject_tree_hash: null,
      subject_plugin_path: null,
      derived_from_audit_id: null,
      derivation_kind: null,
    }],
  };
  const classification = qualifyLegacyGovernanceClassification({
    classification: hashClassification,
    sourceEvidence,
  });
  const previousReportManifest = {
    schemaVersion: 1,
    status: 'legacy_previous_reports_materialized',
    selectedCount: 1,
    entries: [{
      path: row.path,
      currentCommit: COMMIT,
      parentCommit: '8'.repeat(40),
      present: true,
      sha256: '7'.repeat(64),
    }],
  };
  return {
    row,
    plan,
    hashClassification,
    classification,
    rawSkill,
    preInventory,
    dryRunResults,
    sourceEvidence,
    previousReportManifest,
  };
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
    previousReportManifest: join(directory, 'legacy-previous-report-manifest.json'),
  };
  writeFileSync(files.plan, JSON.stringify(values.plan));
  writeFileSync(files.classification, JSON.stringify(values.classification));
  writeFileSync(files.preInventory, JSON.stringify(values.preInventory));
  writeFileSync(files.dryRunResults, JSON.stringify(values.dryRunResults));
  writeFileSync(files.sourceEvidence, JSON.stringify(values.sourceEvidence));
  writeFileSync(files.previousReportManifest, JSON.stringify(values.previousReportManifest));
  const boundary = createLegacyGovernanceBoundary({
    plan: values.plan,
    classification: values.classification,
    dryRunResults: values.dryRunResults,
    paths: files,
    metadata: {
      runId: '12345',
      repository: 'aiskillstore/marketplace',
      workflowCommit: 'f'.repeat(40),
      cliVersion: '2.11.4',
      cliSha256: '236c0d3f5091d6cf15d3fa90a247706ab2419f7cfb672554fc5336f0f4212394',
    },
  });
  return { ...values, directory, files, boundary };
}

test('qualifies only exact v2/v3 source bindings and preserves hash classification', () => {
  const base = fixtures();
  assert.equal(base.classification.governance.eligibleCount, 1);
  assert.equal(base.classification.governance.unprovenCount, 0);
  assert.equal(base.classification.governance.eligible[0].reason, 'eligible_v2');
  assert.deepEqual(base.classification.cohorts, base.hashClassification.cohorts);

  const v3Evidence = structuredClone(base.sourceEvidence);
  const v3Audit = v3Evidence.audits[0];
  const payloadHash = 'f'.repeat(32);
  v3Audit.content_hash = `v3:${COMMIT}:${LEGACY_CONTENT}:${LEGACY_TREE}:${Buffer.from(base.row.path).toString('hex')}:${payloadHash}`;
  v3Audit.audit_payload_hash = payloadHash;
  v3Audit.subject_marketplace_commit_sha = COMMIT;
  v3Audit.subject_content_hash = LEGACY_CONTENT;
  v3Audit.subject_tree_hash = LEGACY_TREE;
  v3Audit.subject_plugin_path = base.row.path;
  const v3Qualified = qualifyLegacyGovernanceClassification({
    classification: base.hashClassification,
    sourceEvidence: v3Evidence,
  });
  assert.equal(v3Qualified.governance.eligible[0].reason, 'eligible_v3');

  const legacyEvidence = structuredClone(base.sourceEvidence);
  legacyEvidence.audits[0].content_hash = payloadHash;
  legacyEvidence.bindings = [{
    id: 'binding-1',
    skill_id: base.row.id,
    source_audit_id: SOURCE_AUDIT_ID,
    source_audit_version: legacyEvidence.audits[0].version,
    source_audit_payload_hash: payloadHash,
    subject_marketplace_commit_sha: COMMIT,
    subject_content_hash: LEGACY_CONTENT,
    subject_tree_hash: LEGACY_TREE,
    subject_plugin_path: base.row.path,
    report_object_spec: `${COMMIT}:${base.row.path}/skill-report.json`,
  }];
  const legacyQualified = qualifyLegacyGovernanceClassification({
    classification: base.hashClassification,
    sourceEvidence: legacyEvidence,
  });
  assert.equal(legacyQualified.governance.eligible[0].reason, 'eligible_legacy_binding_v1');

  const cases = [
    {
      name: 'plain legacy digest',
      mutate: (audit) => { audit.content_hash = 'f'.repeat(32); },
      reason: 'source_audit_binding_unproven_legacy_digest',
    },
    {
      name: 'malformed binding',
      mutate: (audit) => { audit.content_hash = 'v2:broken'; },
      reason: 'source_audit_binding_malformed_or_unsupported',
    },
    {
      name: 'subject mismatch',
      mutate: (audit) => {
        audit.content_hash = `v2:${'9'.repeat(40)}:${LEGACY_CONTENT}:${LEGACY_TREE}:${'f'.repeat(32)}`;
      },
      reason: 'source_audit_binding_subject_mismatch',
    },
    {
      name: 'projection mismatch',
      mutate: (audit) => { audit.audit_payload_hash = 'f'.repeat(32); },
      reason: 'source_audit_projection_mismatch',
    },
    {
      name: 'derived audit',
      mutate: (audit) => { audit.derived_from_audit_id = DERIVED_AUDIT_ID; },
      reason: 'source_audit_identity_unproven',
    },
    {
      name: 'invalid audit version',
      mutate: (audit) => { audit.version = 0; },
      reason: 'source_audit_identity_unproven',
    },
  ];
  for (const item of cases) {
    const sourceEvidence = structuredClone(base.sourceEvidence);
    item.mutate(sourceEvidence.audits[0]);
    const qualified = qualifyLegacyGovernanceClassification({
      classification: base.hashClassification,
      sourceEvidence,
    });
    assert.equal(qualified.governance.eligibleCount, 0, item.name);
    assert.equal(qualified.governance.unprovenCount, 1, item.name);
    assert.equal(qualified.governance.unproven[0].reason, item.reason, item.name);
    assert.deepEqual(qualified.cohorts, base.hashClassification.cohorts, item.name);
  }
});

test('aborts instead of classifying incomplete source evidence', () => {
  const fixture = fixtures();
  const incomplete = structuredClone(fixture.sourceEvidence);
  incomplete.audits = [];
  assert.throws(() => qualifyLegacyGovernanceClassification({
    classification: fixture.hashClassification,
    sourceEvidence: incomplete,
  }), /cover.*exactly once/);
});

test('validates exact present and absent previous-report manifest evidence', () => {
  const fixture = fixtures();
  const absent = structuredClone(fixture.previousReportManifest);
  absent.entries[0].present = false;
  absent.entries[0].sha256 = null;
  assert.doesNotThrow(() => validateLegacyPreviousReportManifest(absent, fixture.plan));

  const cases = [
    {
      mutate(manifest) { manifest.entries[0].unexpected = true; },
      error: /unexpected fields/,
    },
    {
      mutate(manifest) { manifest.entries[0].sha256 = 'bad'; },
      error: /manifest mismatch/,
    },
    {
      mutate(manifest) { manifest.entries[0].parentCommit = COMMIT; },
      error: /manifest mismatch/,
    },
    {
      mutate(manifest) { manifest.entries[0] = null; },
      error: /not an object/,
    },
  ];
  for (const item of cases) {
    const manifest = structuredClone(fixture.previousReportManifest);
    item.mutate(manifest);
    assert.throws(() => validateLegacyPreviousReportManifest(manifest, fixture.plan), item.error);
  }
});

test('freezes and verifies one exact dry-run boundary', () => {
  const fixture = createBoundaryFixture();
  try {
    assert.equal(fixture.boundary.status, 'frozen');
    assert.equal(fixture.boundary.legacyCount, 1);
    assert.match(fixture.boundary.hashes.previousReportManifest, /^[0-9a-f]{64}$/);
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
    const priorCliBoundaries = [
      ['2.11.1', '9aa6a6e15d249e52bed690049974d8312f3257c205025823a68d249cc5cc8367'],
      ['2.11.2', 'c596ca3b6d27875fdcd231bfb889899f08ea8ae95217def7bf46de2aa3722b81'],
      ['2.11.3', 'af5d2718c527d5228ce356182e1a80b9efba065b0a794888a79215666344b201'],
    ];
    for (const [cliVersion, cliSha256] of priorCliBoundaries) {
      assert.equal(verifyLegacyGovernanceBoundary({
        boundary: { ...fixture.boundary, cliVersion, cliSha256 },
        plan: fixture.plan,
        classification: fixture.classification,
        frozenInventory: fixture.preInventory,
        currentInventory: structuredClone(fixture.preInventory),
        frozenSourceEvidence: fixture.sourceEvidence,
        currentSourceEvidence: structuredClone(fixture.sourceEvidence),
        paths: fixture.files,
        expectedRunId: '12345',
      }).status, 'execution_preflight_verified');
    }
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: { ...fixture.boundary, cliVersion: '2.11.0' },
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: structuredClone(fixture.preInventory),
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: structuredClone(fixture.sourceEvidence),
      paths: fixture.files,
      expectedRunId: '12345',
    }), /downloaded boundary metadata is invalid/);
    const reorderedSourceEvidence = structuredClone(fixture.sourceEvidence);
    reorderedSourceEvidence.skills.reverse();
    reorderedSourceEvidence.audits.reverse();
    assert.equal(verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: structuredClone(fixture.preInventory),
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: reorderedSourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }).status, 'execution_preflight_verified');
    const packTimestampAdvance = structuredClone(fixture.preInventory);
    packTimestampAdvance.packs[0].updated_at = '2026-07-15T00:00:00.000Z';
    const advancedPreflight = verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: packTimestampAdvance,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    });
    assert.equal(advancedPreflight.status, 'execution_preflight_verified');
    assert.deepEqual(advancedPreflight.packUpdatedAtAdvances, [{
      packId: fixture.preInventory.packs[0].id,
      frozenUpdatedAt: fixture.preInventory.packs[0].updated_at,
      currentUpdatedAt: packTimestampAdvance.packs[0].updated_at,
    }]);
    const packTimestampRegression = structuredClone(fixture.preInventory);
    packTimestampRegression.packs[0].updated_at = '2025-07-15T00:00:00.000Z';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: packTimestampRegression,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /Pack updated_at regressed/);
    const packTopologyDrift = structuredClone(fixture.preInventory);
    packTopologyDrift.packs[0].slug = 'changed-pack';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: packTopologyDrift,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /production state changed/);
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
      updated_at: '2026-07-16T01:34:36.244Z',
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
    const resumableSourceEvidence = structuredClone(fixture.sourceEvidence);
    resumableSourceEvidence.skills[0].public_eligibility_audit_id = DERIVED_AUDIT_ID;
    const resumed = verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: resumable,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: resumableSourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    });
    assert.equal(resumed.resumableCount, 1);
    const resumableTimestampRegression = structuredClone(resumable);
    resumableTimestampRegression.rows[0].updated_at = '2025-12-31T00:00:00.000Z';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: resumableTimestampRegression,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: resumableSourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /production state changed incompatibly/);
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: resumable,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /Skill metadata or source audit changed/);
    const resumableMetadataDrift = structuredClone(resumableSourceEvidence);
    resumableMetadataDrift.skills[0].description = 'changed after governance';
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: resumable,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: resumableMetadataDrift,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /Skill metadata or source audit changed/);
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

    writeFileSync(fixture.files.previousReportManifest, JSON.stringify({
      ...fixture.previousReportManifest,
      entries: [{ ...fixture.previousReportManifest.entries[0], sha256: '6'.repeat(64) }],
    }));
    assert.throws(() => verifyLegacyGovernanceBoundary({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      frozenInventory: fixture.preInventory,
      currentInventory: fixture.preInventory,
      frozenSourceEvidence: fixture.sourceEvidence,
      currentSourceEvidence: fixture.sourceEvidence,
      paths: fixture.files,
      expectedRunId: '12345',
    }), /previousReportManifest hash mismatch/);
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
    postInventory.packs[0].updated_at = '2026-07-15T00:00:00.000Z';
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
    const currentInventory = structuredClone(fixture.preInventory);
    currentInventory.packs[0].updated_at = postInventory.packs[0].updated_at;
    const verified = verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      currentInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
      postSourceEvidence: structuredClone(fixture.sourceEvidence),
    });
    assert.equal(verified.executedCount, 1);
    postInventory.packs[0].updated_at = '2026-07-15T00:00:01.000Z';
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      currentInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
      postSourceEvidence: structuredClone(fixture.sourceEvidence),
    }), /Pack state changed during governance execution/);
    postInventory.packs[0].updated_at = '2026-07-15T00:00:00.000Z';
    readback.scoreSnapshots[0].score_subject.auditId = SOURCE_AUDIT_ID;
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      currentInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
      postSourceEvidence: structuredClone(fixture.sourceEvidence),
    }), /production readback mismatch/);
    readback.scoreSnapshots[0].score_subject.auditId = DERIVED_AUDIT_ID;
    readback.audits[0].summary = 'changed during execution';
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      currentInventory,
      postInventory,
      readback,
      frozenSourceEvidence: fixture.sourceEvidence,
      postSourceEvidence: structuredClone(fixture.sourceEvidence),
    }), /production readback mismatch/);

    const changedPostEvidence = structuredClone(fixture.sourceEvidence);
    changedPostEvidence.audits[0].summary = 'changed during execution';
    assert.throws(() => verifyLegacyGovernanceExecution({
      boundary: fixture.boundary,
      plan: fixture.plan,
      classification: fixture.classification,
      executionResults,
      frozenInventory: fixture.preInventory,
      currentInventory,
      postInventory,
      readback: {
        ...readback,
        audits: [{ ...fixture.sourceEvidence.audits[0] }, readback.audits[1]],
      },
      frozenSourceEvidence: fixture.sourceEvidence,
      postSourceEvidence: changedPostEvidence,
    }), /source audit changed during governance execution/);
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
  const classification = structuredClone(fixtures().hashClassification);
  const secondSkillId = '00000000-0000-4000-8000-000000000002';
  const secondAuditId = '10000000-0000-4000-8000-000000000002';
  classification.cohorts.legacy_algorithm_equivalent.push({
    ...classification.cohorts.legacy_algorithm_equivalent[0],
    id: secondSkillId,
    slug: 'owner-second',
    publicEligibilityAuditId: secondAuditId,
  });
  classification.counts.legacy_algorithm_equivalent = 2;
  const fetchImpl = async (url) => {
    const table = url.pathname.split('/').at(-1);
    if (table === 'skills') {
      return { ok: true, json: async () => [
        { id: secondSkillId, name: 'Second', file_structure: [] },
        { id: SKILL_ID, name: 'Image', file_structure: [] },
      ] };
    }
    assert.equal(url.searchParams.get('select'), '*');
    return { ok: true, json: async () => [
      { id: secondAuditId, skill_id: secondSkillId, version: 8 },
      { id: SOURCE_AUDIT_ID, skill_id: SKILL_ID, version: 7 },
    ] };
  };
  const output = await fetchLegacyGovernanceSourceEvidence({
    supabaseUrl: 'https://db.example.test',
    serviceKey: 'service-key',
    classification,
    fetchImpl,
  });
  assert.deepEqual(output.skills.map((row) => row.id), [SKILL_ID, secondSkillId]);
  assert.deepEqual(output.audits.map((row) => row.id), [SOURCE_AUDIT_ID, secondAuditId]);
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
  assert.match(workflow, /default: '2\.11\.4'/);
  assert.match(workflow, /test "\$CLI_VERSION" = '2\.11\.4'/);
  assert.doesNotMatch(workflow, /version:\s*(latest|'latest'|"latest")/);
  assert.match(workflow, /batch_size must be between 1 and 500/);
  assert.match(workflow, /dry_run_id/);
  assert.match(workflow, /gh run download "\$DRY_RUN_ID"/);
  assert.match(workflow, /headBranch == "main"/);
  assert.match(workflow, /git merge-base --is-ancestor/);
  assert.match(workflow, /boundaries may only be created from main/);
  assert.match(workflow, /execute may only run from main/);
  assert.match(workflow, /sha256sum --check SHA256SUMS/);
  assert.match(workflow, /boundary or execution CLI binary differs from its audited release/);
  assert.match(workflow, /2\.11\.1\) boundary_audited='9aa6a6e15d249e52bed690049974d8312f3257c205025823a68d249cc5cc8367'/);
  assert.match(workflow, /2\.11\.2\) boundary_audited='c596ca3b6d27875fdcd231bfb889899f08ea8ae95217def7bf46de2aa3722b81'/);
  assert.match(workflow, /2\.11\.3\) boundary_audited='af5d2718c527d5228ce356182e1a80b9efba065b0a794888a79215666344b201'/);
  assert.match(workflow, /test "\$boundary_actual" = "\$boundary_audited" && test "\$actual" = "\$execution_audited"/);
  assert.ok((workflow.match(/236c0d3f5091d6cf15d3fa90a247706ab2419f7cfb672554fc5336f0f4212394/g) || []).length >= 2);
  assert.equal((workflow.match(/require-checksum: 'true'/g) || []).length, 2);
  assert.match(workflow, /--phase execute-preflight/);
  assert.match(workflow, /--current-inventory "\$RUNNER_TEMP\/current-inventory\.json"/);
  assert.match(workflow, /\$\{\{ runner\.temp \}\}\/current-inventory\.json/);
  assert.match(workflow, /--phase qualify/);
  assert.match(workflow, /skill govern-legacy-equivalent/);
  assert.match(workflow, /four bounded workers/);
  assert.equal((workflow.match(/--concurrency 4/g) || []).length, 2);
  assert.match(workflow, /Prepare audited CLI TLS trust/);
  assert.match(workflow, /status=\$\(curl -sS -o \/dev\/null -w '%\{http_code\}' https:\/\/skillstore\.io\/api\/cache\/invalidate\)/);
  assert.match(workflow, /NODE_EXTRA_CA_CERTS: \/etc\/ssl\/certs\/ca-certificates\.crt/);
  assert.match(workflow, /SSL_CERT_FILE: \/etc\/ssl\/certs\/ca-certificates\.crt/);
  assert.match(workflow, /NODE_OPTIONS: --use-openssl-ca/);
  assert.match(workflow, /execute-boundary:[\s\S]{0,160}group: production-skill-score-writes/);
  assert.match(workflow, /legacy-equivalent-boundary-/);
  assert.match(workflow, /legacy-equivalent-execution-/);
  assert.match(workflow, /legacy-equivalent-failed-dry-run-/);
  assert.match(workflow, /Preserve execution status evidence/);
  assert.match(workflow, /scripts\/materialize-legacy-previous-reports\.mjs/);
  assert.match(workflow, /--manifest "\$RUNNER_TEMP\/legacy-previous-report-manifest\.json"/);
  assert.match(workflow, /--manifest "\$RUNNER_TEMP\/current-legacy-previous-report-manifest\.json"/);
  assert.match(workflow, /cmp \\\n+\s+"\$RUNNER_TEMP\/boundary\/legacy-previous-report-manifest\.json" \\\n+\s+"\$RUNNER_TEMP\/current-legacy-previous-report-manifest\.json"/);
  assert.match(workflow, /--previous-report-manifest "\$RUNNER_TEMP\/boundary\/legacy-previous-report-manifest\.json"/);
  assert.match(workflow, /sha256sum plan\.json classification\.json pre-inventory\.json governance-dry-run\.json source-evidence\.json legacy-previous-report-manifest\.json boundary\.json/);
  assert.match(workflow, /\$\{\{ runner\.temp \}\}\/current-legacy-previous-report-manifest\.json/);
  const sourceEvidenceIndex = workflow.indexOf('Fetch complete source audit evidence before governance planning');
  const qualificationIndex = workflow.indexOf('Qualify source-audit bindings and plan only governable groups');
  const governanceDryRunIndex = workflow.indexOf('Run administrator governance dry-run');
  assert(sourceEvidenceIndex > 0 && sourceEvidenceIndex < qualificationIndex);
  assert(qualificationIndex < governanceDryRunIndex);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/source-evidence\.json" "\$RUNNER_TEMP\/source-evidence-after\.json"/);
  assert.match(workflow, /--post-source-evidence "\$RUNNER_TEMP\/post-source-evidence\.json"/);
  assert.match(workflow, /\$\{\{ runner\.temp \}\}\/post-source-evidence\.json/);
  const syncCalls = workflow.match(/skill sync[\s\S]{0,250}/g) || [];
  assert.equal(syncCalls.length, 1);
  assert.match(syncCalls[0], /--dry-run/);
  assert.match(syncCalls[0], /--repair-stale-report-hashes/);
  assert.match(syncCalls[0], /--legacy-previous-report-root "\$RUNNER_TEMP\/legacy-previous-reports\/batch-\$index\/\$commit"/);
  const governanceCalls = workflow.match(/skill govern-legacy-equivalent[\s\S]{0,420}/g) || [];
  assert.equal(governanceCalls.length, 2);
  assert.match(governanceCalls[0], /--legacy-previous-report-root "\$RUNNER_TEMP\/legacy-previous-reports\/batch-\$index\/\$commit"/);
  assert.match(governanceCalls[1], /--legacy-previous-report-root "\$RUNNER_TEMP\/current-legacy-previous-reports\/batch-\$index\/\$commit"/);
  const recomputeIndex = workflow.indexOf('Recompute and match frozen first-parent report evidence');
  const executeIndex = workflow.indexOf('Execute frozen legacy cohort with four bounded workers');
  assert(recomputeIndex > 0 && recomputeIndex < executeIndex);
  assert.match(ordinaryWorkflow, /\.exactBatches\[\]/);
  assert.match(ordinaryWorkflow, /CLI_VERSION" != "2\.3\.1"/);
});
