import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import test from 'node:test';
import { buildLegacyAuditBindingPlan } from '../build-legacy-audit-binding-plan.mjs';
import { planLegacyAuditBindingCohorts } from '../plan-legacy-audit-binding-cohorts.mjs';

function row(prefix, index) {
  return {
    id: `${prefix}-skill-${index}`,
    slug: `${prefix}-${String(index).padStart(3, '0')}`,
    publicEligibilityAuditId: `${prefix}-audit-${index}`,
  };
}

function fixtures() {
  const legacy = Array.from({ length: 61 }, (_, index) => row('legacy', index));
  const drift = Array.from({ length: 24 }, (_, index) => row('drift', index));
  const entries = legacy.concat(drift).map((item) => ({
    slug: item.slug,
    skillId: item.id,
    sourceAuditId: item.publicEligibilityAuditId,
    decision: 'verified',
    reason: 'pinned_report_payload_matches',
    planEntry: {
      skillId: item.id,
      slug: item.slug,
      pluginPath: `skills/history/${item.slug}`,
      marketplaceCommit: 'a'.repeat(40),
      skillContentHash: 'b'.repeat(64),
      treeHash: 'c'.repeat(64),
      sourceAuditId: item.publicEligibilityAuditId,
      sourceAuditVersion: 1,
      sourceAuditPayloadHash: 'd'.repeat(32),
      reportBlobSha256: 'e'.repeat(64),
    },
  }));
  return {
    classification: {
      schemaVersion: 1,
      status: 'classified',
      cohorts: {
        legacy_algorithm_equivalent: legacy,
        actual_or_unproven_drift: drift,
      },
    },
    bindingEvidence: { schemaVersion: 1, status: 'verified', entries },
  };
}

test('targets 61 hash-equivalent rows and quarantines all 24 drift rows after binding proof', () => {
  const fixture = fixtures();
  const result = planLegacyAuditBindingCohorts({
    ...fixture,
    expectedTargetedCount: 61,
    expectedDriftCount: 24,
  });
  assert.deepEqual(result.plan.counts, {
    hashEquivalent: 61,
    targeted: 61,
    unprovenHashEquivalent: 0,
    driftQuarantined: 24,
  });
  assert.equal(result.plan.targeted.every((row) => row.artifactGovernanceAllowed), true);
  assert.equal(result.bindingPlan.entries.length, 61);
  assert.equal(result.plan.driftQuarantine.every((row) =>
    row.bindingVerified && !row.artifactGovernanceAllowed
  ), true);
  const targetedSlugs = new Set(result.plan.targeted.map((row) => row.slug));
  assert.equal(
    result.plan.driftQuarantine.some((row) => targetedSlugs.has(row.slug)),
    false
  );
});

test('fails closed on missing, duplicate, or cross-cohort evidence', () => {
  const fixture = fixtures();
  fixture.bindingEvidence.entries.pop();
  assert.throws(() => planLegacyAuditBindingCohorts(fixture), /cover.*exactly once/);

  const duplicate = fixtures();
  duplicate.bindingEvidence.entries[84] = duplicate.bindingEvidence.entries[0];
  assert.throws(() => planLegacyAuditBindingCohorts(duplicate), /unique non-empty slugs/);

  const mismatch = fixtures();
  mismatch.bindingEvidence.entries[0].sourceAuditId = 'latest-audit-not-frozen-pointer';
  assert.throws(() => planLegacyAuditBindingCohorts(mismatch), /frozen binding identity mismatch/);
});

test('binding workflow is two-phase, pinned, score/artifact preserving, and cache inert', () => {
  const workflow = readFileSync(resolve(
    import.meta.dirname,
    '../../.github/workflows/bind-legacy-audit-subjects.yml'
  ), 'utf8');
  assert.match(workflow, /options: \[dry-run, execute\]/);
  assert.match(workflow, /version: '2\.7\.0'/);
  assert.match(workflow, /__LEGACY_AUDIT_BINDING_LINUX_SHA256__/);
  assert.match(workflow, /skill bind-legacy-audit/);
  assert.match(workflow, /--dry-run --concurrency 1/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/binding-inventory\.json" "\$RUNNER_TEMP\/post-binding-inventory\.json"/);
  assert.doesNotMatch(workflow, /cache\/invalidate|warm-cache|invalidateApi/);
  assert.match(workflow, /expected_targeted:[\s\S]*default: 61/);
  assert.match(workflow, /expected_drift:[\s\S]*default: 24/);
});

test('builds the executable plan from the frozen pointer and exact Git blob', () => {
  const directory = mkdtempSync(resolve(tmpdir(), 'legacy-binding-plan-'));
  try {
    execFileSync('git', ['init', '-q'], { cwd: directory });
    execFileSync('git', ['config', 'user.email', 'test@example.com'], { cwd: directory });
    execFileSync('git', ['config', 'user.name', 'Test'], { cwd: directory });
    const path = 'skills/history/legacy-000';
    mkdirSync(resolve(directory, path), { recursive: true });
    const report = { meta: { slug: 'legacy-000', content_hash: 'b'.repeat(64), tree_hash: 'c'.repeat(64) }, security_audit: { risk_level: 'low' } };
    writeFileSync(resolve(directory, path, 'skill-report.json'), JSON.stringify(report));
    execFileSync('git', ['add', '.'], { cwd: directory });
    execFileSync('git', ['commit', '-qm', 'fixture'], { cwd: directory });
    const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: directory, encoding: 'utf8' }).trim();
    const classification = {
      schemaVersion: 1, status: 'classified',
      cohorts: {
        legacy_algorithm_equivalent: [{ id: 'skill-1', slug: 'legacy-000', path, marketplaceCommit: commit, contentHash: 'b'.repeat(64), treeHash: 'c'.repeat(64), publicEligibilityAuditId: 'audit-1' }],
        actual_or_unproven_drift: [{ id: 'skill-2', slug: 'drift-000', publicEligibilityAuditId: 'audit-2' }],
      },
    };
    const sourceEvidence = {
      skills: [{ id: 'skill-1', slug: 'legacy-000' }],
      audits: [{ id: 'audit-1', skill_id: 'skill-1', version: 3, content_hash: 'd'.repeat(32) }],
    };
    const plan = buildLegacyAuditBindingPlan({ classification, sourceEvidence, repositoryRoot: directory });
    assert.equal(plan.entries.length, 1);
    assert.equal(plan.entries[0].sourceAuditId, 'audit-1');
    assert.equal(plan.driftQuarantine[0].artifactGovernanceAllowed, false);
    assert.match(plan.planSha256, /^[0-9a-f]{64}$/);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
