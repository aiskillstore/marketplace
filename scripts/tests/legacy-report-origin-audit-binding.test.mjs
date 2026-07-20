import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import test from 'node:test';
import { buildLegacyReportOriginAuditBindingPlan } from '../build-legacy-report-origin-audit-binding-plan.mjs';

function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function uuid(prefix, index) {
  return `${prefix}0000000-0000-4000-8000-${String(index + 1).padStart(12, '0')}`;
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'report-origin-binding-'));
  execFileSync('git', ['init', '-q', root]);
  execFileSync('git', ['-C', root, 'config', 'user.email', 'test@example.com']);
  execFileSync('git', ['-C', root, 'config', 'user.name', 'Test']);
  const baseRows = Array.from({ length: 70 }, (_, index) => {
    const slug = `owner-skill-${String(index).padStart(2, '0')}`;
    const path = `skills/owner/skill-${String(index).padStart(2, '0')}`;
    const contentHash = index.toString(16).padStart(64, '0');
    const treeHash = (index + 100).toString(16).padStart(64, '0');
    const canonicalContent = (index + 200).toString(16).padStart(64, '0');
    const canonicalTree = (index + 300).toString(16).padStart(64, '0');
    if (index < 11) {
      const reportPath = join(root, path, 'skill-report.json');
      mkdirSync(dirname(reportPath), { recursive: true });
      writeFileSync(reportPath, `${JSON.stringify({
        meta: { slug, content_hash: contentHash, tree_hash: treeHash },
        security_audit: { summary: `audit-${index}` },
      }, null, 2)}\n`);
    }
    return { index, slug, path, contentHash, treeHash, canonicalContent, canonicalTree };
  });
  execFileSync('git', ['-C', root, 'add', '.']);
  execFileSync('git', ['-C', root, 'commit', '-qm', 'fixture']);
  const commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  const rows = baseRows.map((row) => ({
    id: uuid('0', row.index),
    slug: row.slug,
    path: row.path,
    marketplaceCommit: commit,
    contentHash: row.contentHash,
    treeHash: row.treeHash,
    artifactRevision: 0,
    currentArtifactVersionId: null,
    status: 'approved',
    publicEligible: true,
    publicEligibilityAuditId: uuid('1', row.index),
    publishedAt: '2026-01-01T00:00:00.000Z',
    updatedAt: '2026-01-02T00:00:00.000Z',
    evidence: { artifact: { contentHash: row.canonicalContent, treeHash: row.canonicalTree } },
  }));
  const classification = {
    schemaVersion: 1,
    status: 'classified',
    classifiedCount: 70,
    counts: { exact: 0, legacy_algorithm_equivalent: 0, actual_or_unproven_drift: 70 },
    cohorts: { exact: [], legacy_algorithm_equivalent: [], actual_or_unproven_drift: rows },
  };
  const originLineage = {
    status: 'legacy_report_origin_evidence_materialized',
    selectedCount: 70,
    entries: rows.map((row, index) => {
      const reportPath = `${row.path}/skill-report.json`;
      const bytes = index < 11 ? execFileSync('git', ['-C', root, 'show', `${commit}:${reportPath}`]) : Buffer.from('');
      const gitBlob = index < 11
        ? execFileSync('git', ['-C', root, 'rev-parse', `${commit}:${reportPath}`], { encoding: 'utf8' }).trim()
        : '0'.repeat(40);
      return {
        slug: row.slug,
        skillId: row.id,
        path: row.path,
        currentMarketplaceCommit: commit,
        currentReport: {
          contentHash: row.contentHash,
          treeHash: row.treeHash,
          sha256: sha256(bytes),
          gitBlob,
        },
      };
    }),
  };
  const sourceEvidence = {
    schemaVersion: 1,
    status: 'source_evidence_fetched',
    bindings: [],
    skills: rows.map((row, index) => ({
      id: row.id,
      slug: row.slug,
      content_hash: index >= 65 ? row.evidence.artifact.contentHash : row.contentHash,
      tree_hash: index >= 65 ? row.evidence.artifact.treeHash : row.treeHash,
      marketplace_commit_sha: index >= 65 ? 'b'.repeat(40) : commit,
      plugin_path: row.path,
      public_eligible: true,
      public_eligibility_audit_id: index >= 65 ? uuid('2', index) : row.publicEligibilityAuditId,
      artifact_revision: index >= 65 ? 1 : 0,
      current_artifact_version_id: index >= 65 ? uuid('3', index) : null,
      repository: 'https://github.com/owner/repo',
      source_ref: 'main',
    })),
    audits: rows.map((row, index) => ({
      id: row.publicEligibilityAuditId,
      skill_id: row.id,
      version: 1,
      content_hash: index < 11
        ? (index + 1).toString(16).padStart(32, '0')
        : `v2:${commit}:${row.contentHash}:${row.treeHash}:${'f'.repeat(32)}`,
      audit_payload_hash: null,
      subject_marketplace_commit_sha: null,
      subject_content_hash: null,
      subject_tree_hash: null,
      subject_plugin_path: null,
      derived_from_audit_id: null,
      derivation_kind: null,
    })),
  };
  const inventory = {
    scopedSkillIds: rows.map((row) => row.id),
    rows: sourceEvidence.skills,
    artifacts: rows.slice(65).map((row, offset) => {
      const index = offset + 65;
      const skill = sourceEvidence.skills[index];
      return {
        id: skill.current_artifact_version_id,
        skill_id: row.id,
        artifact_revision: 1,
        content_hash: skill.content_hash,
        tree_hash: skill.tree_hash,
        marketplace_commit_sha: skill.marketplace_commit_sha,
        source_path: skill.plugin_path,
        snapshot_status: 'complete',
      };
    }),
  };
  return { root, classification, originLineage, sourceEvidence, inventory };
}

test('builds exactly 11 append-only bindings from the authenticated 70-row Report-Origin split', () => {
  const item = fixture();
  try {
    const plan = buildLegacyReportOriginAuditBindingPlan({
      ...item,
      repositoryRoot: item.root,
      expectedSelected: 11,
      expectedV2Revision0: 54,
      expectedGoverned: 5,
    });
    assert.deepEqual(plan.counts, {
      selected: 11,
      v2Revision0: 54,
      governed: 5,
      existingBindings: 0,
    });
    assert.equal(plan.entries.length, 11);
    assert.match(plan.planSha256, /^[0-9a-f]{64}$/);

    const tampered = structuredClone(item.sourceEvidence);
    tampered.audits[0].subject_tree_hash = '0'.repeat(64);
    assert.throws(() => buildLegacyReportOriginAuditBindingPlan({
      classification: item.classification,
      originLineage: item.originLineage,
      sourceEvidence: tampered,
      inventory: item.inventory,
      repositoryRoot: item.root,
      expectedSelected: 11,
      expectedV2Revision0: 54,
      expectedGoverned: 5,
    }), /raw32 audit columns changed/);

    const alreadyBound = structuredClone(item.sourceEvidence);
    alreadyBound.bindings.push({ source_audit_id: alreadyBound.audits[0].id });
    assert.throws(() => buildLegacyReportOriginAuditBindingPlan({
      classification: item.classification,
      originLineage: item.originLineage,
      sourceEvidence: alreadyBound,
      inventory: item.inventory,
      repositoryRoot: item.root,
      expectedSelected: 11,
      expectedV2Revision0: 54,
      expectedGoverned: 5,
    }), /already bound/);

    const brokenPointer = structuredClone(item.inventory);
    brokenPointer.artifacts[0].tree_hash = '0'.repeat(64);
    assert.throws(() => buildLegacyReportOriginAuditBindingPlan({
      classification: item.classification,
      originLineage: item.originLineage,
      sourceEvidence: item.sourceEvidence,
      inventory: brokenPointer,
      repositoryRoot: item.root,
      expectedSelected: 11,
      expectedV2Revision0: 54,
      expectedGoverned: 5,
    }), /governed projection changed/);
  } finally {
    rmSync(item.root, { recursive: true, force: true });
  }
});

test('workflow freezes one dry-run before binding and forbids governance side effects', () => {
  const workflow = readFileSync(resolve(
    import.meta.dirname,
    '../../.github/workflows/bind-legacy-report-origin-audits.yml'
  ), 'utf8');
  assert.match(workflow, /name: Bind Legacy Report-Origin Audits 11/);
  assert.match(workflow, /BINDING_CLI_VERSION: '2\.15\.2'/);
  assert.match(workflow, /fceaa46ab5e8cb2b68398a49f1e6c041bfa4cc83abc00221ba7d1e2bf83a73e4/);
  assert.match(workflow, /--expected-selected 11 --expected-v2 54 --expected-governed 5/);
  assert.match(workflow, /skill bind-legacy-audit/);
  assert.match(workflow, /Prove only 11 append-only bindings changed/);
  assert.match(workflow, /inventory-scope\.json/);
  assert.doesNotMatch(workflow, /--scope-inventory "\$ORIGIN_COHORT"/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/current\/inventory\.json" "\$RUNNER_TEMP\/post-inventory\.json"/);
  assert.doesNotMatch(workflow, /govern-legacy-equivalent|skill score|CACHE_INVALIDATE/);
});
