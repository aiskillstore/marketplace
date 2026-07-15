import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import test from 'node:test';
import { buildLegacyAuditBindingPlan } from '../build-legacy-audit-binding-plan.mjs';
import { planLegacyAuditBindingCohorts } from '../plan-legacy-audit-binding-cohorts.mjs';
import {
  buildLegacyAuditBindingCandidateScope,
  selectLegacyAuditBindingSourceCohort,
} from '../build-legacy-audit-binding-source-cohort.mjs';

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

test('merges only the frozen 61/24 raw32 cohort from three immutable source boundaries', () => {
  const directory = mkdtempSync(resolve(tmpdir(), 'legacy-binding-sources-'));
  try {
    const distributions = [[0, 12], [1, 0], [60, 12]];
    const sources = [];
    const sourceEvidence = {
      schemaVersion: 1, status: 'source_evidence_fetched', skillIds: [],
      skills: [], audits: [], bindings: [],
    };
    let index = 0;
    for (let sourceIndex = 0; sourceIndex < distributions.length; sourceIndex += 1) {
      const runId = String(1000 + sourceIndex);
      const root = resolve(directory, runId); mkdirSync(root, { recursive: true });
      const [legacyCount, driftCount] = distributions[sourceIndex];
      const makeRows = (count, prefix) => Array.from({ length: count }, () => {
        const current = index++;
        const item = {
          id: `skill-${current}`, slug: `${prefix}-${current}`,
          publicEligibilityAuditId: `audit-${current}`,
        };
        sourceEvidence.skillIds.push(item.id);
        sourceEvidence.skills.push({
          id: item.id, slug: item.slug,
          public_eligibility_audit_id: item.publicEligibilityAuditId,
        });
        sourceEvidence.audits.push({
          id: item.publicEligibilityAuditId, skill_id: item.id, content_hash: 'a'.repeat(32),
        });
        return item;
      });
      const classification = {
        schemaVersion: 1, status: 'classified', cohorts: {
          exact: [], legacy_algorithm_equivalent: makeRows(legacyCount, 'legacy'),
          actual_or_unproven_drift: makeRows(driftCount, 'drift'),
        },
      };
      const headSha = String(sourceIndex + 1).repeat(40);
      writeFileSync(resolve(root, 'classification.json'), JSON.stringify(classification));
      writeFileSync(resolve(root, 'boundary.json'), JSON.stringify({ runId, workflowCommit: headSha }));
      writeFileSync(resolve(root, 'SHA256SUMS'), 'fixture sums\n');
      const digest = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
      sources.push({
        runId, headSha, artifactName: `legacy-equivalent-boundary-${runId}`,
        sha256sumsSha256: digest(resolve(root, 'SHA256SUMS')),
        classificationSha256: digest(resolve(root, 'classification.json')),
        expectedLegacy: legacyCount, expectedDrift: driftCount,
      });
    }
    sourceEvidence.skillIds.sort();
    const manifest = {
      schemaVersion: 1, status: 'frozen',
      expected: { legacy_algorithm_equivalent: 61, actual_or_unproven_drift: 24, total: 85 },
      sources,
    };
    const candidate = buildLegacyAuditBindingCandidateScope({ manifest, sourcesRoot: directory });
    assert.equal(candidate.counts.legacy_algorithm_equivalent, 85);
    const selected = selectLegacyAuditBindingSourceCohort({ manifest, sourcesRoot: directory, sourceEvidence });
    assert.deepEqual(selected.classification.counts, {
      exact: 0, legacy_algorithm_equivalent: 61, actual_or_unproven_drift: 24,
    });
    assert.equal(selected.plan.selectedCount, 85);

    const changed = structuredClone(sourceEvidence);
    changed.audits[0].content_hash = `v2:${'1'.repeat(40)}:${'2'.repeat(64)}:${'3'.repeat(64)}:${'4'.repeat(32)}`;
    assert.throws(
      () => selectLegacyAuditBindingSourceCohort({ manifest, sourcesRoot: directory, sourceEvidence: changed }),
      /raw32 cohort count changed/
    );
    const pointerDrift = structuredClone(sourceEvidence);
    pointerDrift.skills[0].public_eligibility_audit_id = 'new-audit-pointer';
    assert.throws(
      () => selectLegacyAuditBindingSourceCohort({ manifest, sourcesRoot: directory, sourceEvidence: pointerDrift }),
      /current raw32 audit pointer changed/
    );
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('binding workflow is two-phase, pinned, score/artifact preserving, and cache inert', () => {
  const workflow = readFileSync(resolve(
    import.meta.dirname,
    '../../.github/workflows/bind-legacy-audit-subjects.yml'
  ), 'utf8');
  assert.match(workflow, /options: \[dry-run, execute\]/);
  assert.match(workflow, /version: '2\.7\.0'/);
  assert.match(workflow, /cc987bdb22b3c19b7f7dec60b707032979823579167c0b911e408771ed9e13d7/);
  assert.match(workflow, /skill bind-legacy-audit/);
  assert.match(workflow, /--dry-run --concurrency 1/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/binding-inventory\.json" "\$RUNNER_TEMP\/post-binding-inventory\.json"/);
  assert.doesNotMatch(workflow, /cache\/invalidate|warm-cache|invalidateApi/);
  assert.doesNotMatch(workflow, /expected_targeted:|expected_drift:/);
  assert.match(workflow, /--expected-targeted 61 --expected-drift 24/);
  assert.match(workflow, /\.expectedTargeted == 61/);
  assert.match(workflow, /\.expectedDrift == 24/);
  assert.match(workflow, /boundary\/classification\.json/);
  assert.doesNotMatch(workflow, /boundary\/hash-classification\.json/);
  assert.match(workflow, /\.counts\.legacy_algorithm_equivalent == 61/);
  assert.match(workflow, /\.counts\.actual_or_unproven_drift == 24/);
  assert.match(workflow, /legacy-audit-binding-boundary-/);
});

test('binding workflow authenticates and byte-freezes governance and binding run boundaries', () => {
  const workflow = readFileSync(resolve(
    import.meta.dirname,
    '../../.github/workflows/bind-legacy-audit-subjects.yml'
  ), 'utf8');
  assert.match(workflow, /--json databaseId,conclusion,event,headBranch,headSha,workflowName,url/);
  assert.match(workflow, /\.conclusion == "success"/);
  assert.match(workflow, /\.event == "workflow_dispatch"/);
  assert.match(workflow, /\.headBranch == "main"/);
  assert.match(workflow, /\.workflowName == "Govern Legacy-Equivalent Artifacts"/);
  assert.match(workflow, /\.workflowName == "Bind Legacy Audit Subjects"/);
  assert.match(workflow, /--name "\$artifact" --dir "\$target"/);
  assert.match(workflow, /--name "legacy-audit-binding-boundary-\$DRY_RUN"/);
  assert.ok((workflow.match(/sha256sum --check SHA256SUMS/g) || []).length >= 2);
  assert.match(workflow, /\.headSha == \$headSha/);
  assert.match(workflow, /git merge-base --is-ancestor "\$head_sha" "\$GITHUB_SHA"/);
  assert.match(workflow, /source-governance-boundaries/);
  assert.match(workflow, /legacy-audit-binding-source-boundaries-v1\.json/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/binding-dry-run\.json" "\$RUNNER_TEMP\/boundary\/binding-dry-run\.json"/);
  assert.match(workflow, /status:"binding_dry_run_frozen"/);
  assert.match(workflow, /name: legacy-audit-binding-boundary-\$\{\{ github\.run_id \}\}/);
  const downloads = workflow.match(/gh run download[\s\S]{0,180}/g) || [];
  assert.equal(downloads.length, 2);
  assert.match(downloads[0], /--name "\$artifact"/);
  assert.match(downloads[1], /--name "legacy-audit-binding-boundary-\$DRY_RUN"/);

  const manifest = JSON.parse(readFileSync(resolve(
    import.meta.dirname,
    '../data/legacy-audit-binding-source-boundaries-v1.json'
  ), 'utf8'));
  assert.deepEqual(manifest.sources.map((source) => source.runId), [
    '29391353646', '29394223576', '29402463151',
  ]);
  assert.deepEqual(manifest.sources.map((source) => [source.expectedLegacy, source.expectedDrift]), [
    [0, 12], [1, 0], [60, 12],
  ]);
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
