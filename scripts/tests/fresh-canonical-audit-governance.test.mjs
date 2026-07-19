import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { prepareFreshCanonicalAuditBatch } from '../prepare-fresh-canonical-audit-batch.mjs';

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'fresh-audit-plan-'));
  execFileSync('git', ['init', '-q', root]);
  execFileSync('git', ['-C', root, 'config', 'user.email', 'test@example.com']);
  execFileSync('git', ['-C', root, 'config', 'user.name', 'Test']);
  mkdirSync(join(root, 'skills', 'owner', 'skill'), { recursive: true });
  mkdirSync(join(root, 'schemas'), { recursive: true });
  writeFileSync(join(root, 'skills', 'owner', 'skill', 'SKILL.md'), '---\nname: skill\n---\n');
  writeFileSync(join(root, 'skills', 'owner', 'skill', 'skill-report.json'), '{}\n');
  writeFileSync(join(root, 'schemas', 'skill-report.schema.json'), '{}\n');
  execFileSync('git', ['-C', root, 'add', '.']);
  execFileSync('git', ['-C', root, 'commit', '-qm', 'fixture']);
  const commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  const row = {
    slug: 'owner-skill', skillId: '11111111-1111-4111-8111-111111111111',
    path: 'skills/owner/skill', marketplaceCommit: commit,
    reportContentHash: 'a'.repeat(64), reportTreeHash: 'b'.repeat(64),
    canonicalArtifact: { contentHash: 'c'.repeat(64), treeHash: 'd'.repeat(64) },
    remainingReason: 'source_changed_after_report_subject', governanceEligibleByLineage: false,
  };
  return { root, row };
}

function inventory(row, revision = 0) {
  return {
    rows: [{
      id: row.skillId,
      slug: row.slug,
      artifact_revision: revision,
      current_artifact_version_id: revision > 0 ? 'artifact-version-id' : null,
    }],
  };
}

test('prepares a bounded commit-addressed fresh audit batch', () => {
  const { root, row } = fixture();
  const result = prepareFreshCanonicalAuditBatch({
    repositoryRoot: root,
    cohort: { schemaVersion: 1, status: 'lineage_unproven', count: 1, rows: [row] },
    batchSize: 1,
    productionInventory: inventory(row),
  });
  assert.equal(result.count, 1);
  assert.equal(result.groups[0].marketplaceCommit, row.marketplaceCommit);
  assert.deepEqual(result.groups[0].paths, ['schemas/skill-report.schema.json', row.path]);
  assert.equal(result.remaining, 0);
});

test('rejects a lineage-governable row from the fresh audit lane', () => {
  const { root, row } = fixture();
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root,
    cohort: { schemaVersion: 1, status: 'lineage_unproven', count: 1, rows: [{ ...row, governanceEligibleByLineage: true }] },
    batchSize: 1,
    productionInventory: inventory(row),
  }), /Invalid fresh-audit cohort row/);
});

test('cursor requires both the immediately preceding boundary and a fully governed production prefix', () => {
  const { root, row } = fixture();
  const cohortSha256 = 'f'.repeat(64);
  const cohort = { schemaVersion: 1, status: 'lineage_unproven', count: 1, rows: [row] };
  const previousBoundary = {
    metadata: {
      status: 'fresh_canonical_audit_frozen', runId: '123', lastSelected: row.slug,
      cohortSha256,
    },
    selection: { status: 'lineage_unproven', lastSelected: row.slug },
    executionProof: {
      schemaVersion: 1, status: 'fresh_canonical_audit_execution_complete', executeRunId: '456',
      dryRunId: '123', lastSelected: row.slug, cohortSha256,
      scoreFinalized: true, timestampFinalized: true, cacheClosureCompleted: true,
      packClosureCompleted: true, productionSmokeCompleted: true,
    },
  };
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 0), previousBoundary, cohortSha256,
  }), /Cursor prefix is not fully governed/);
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1), previousBoundary: null, cohortSha256,
  }), /successfully closed previous execution/);
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1),
    previousBoundary: {
      ...previousBoundary,
      executionProof: { ...previousBoundary.executionProof, productionSmokeCompleted: false },
    },
    cohortSha256,
  }), /successfully closed previous execution/);
});

test('workflow is two-phase, CLI-pinned, resumable, and closes P0 channels', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/govern-fresh-canonical-audits.yml', import.meta.url), 'utf8');
  assert.match(workflow, /options: \[dry-run, execute, recover\]/);
  assert.match(workflow, /default: '2\.8\.3'/);
  assert.match(workflow, /DRY_RUN_ID" = '29646612265'/);
  assert.match(workflow, /11101c85a06aaec0d8f0deda0a4aac82cf24899b/);
  assert.match(workflow, /sha256:4d5b40e20e59cd830125e572ed2ba888dcc2ce5309a62001793a87dd8464035b/);
  assert.match(workflow, /git show "11101c85a06aaec0d8f0deda0a4aac82cf24899b:\$path"/);
  assert.equal((workflow.match(/296cab05576adec2c6613255b26663fab58e8f3fa585e2c085cd0367d8c7274f/g) || []).length, 2);
  assert.equal((workflow.match(/9b885943950c15555e8fbae522adf2cf9514ae74f63050a905c8e97694d52fcb/g) || []).length, 2);
  assert.equal((workflow.match(/ecfaa49aa72d24b8ea6322c7dae24d4bbe9df174a5d009cc56d7d2a89e7ae05a/g) || []).length, 4);
  assert.match(workflow, /\[\[ "\$audited" =~ \^\[0-9a-f\]\{64\}\$ \]\]/);
  assert.match(workflow, /skill audit/);
  assert.match(workflow, /cd "\$RUNNER_TEMP\/materialized\/\$commit"/);
  assert.match(workflow, /skill audit skills --slugs "\$slugs"/);
  assert.doesNotMatch(workflow, /skill audit \\\n\s+"\$RUNNER_TEMP\/materialized\/\$commit\/skills"/);
  assert.match(workflow, /fresh-run-manifest-file/);
  assert.match(workflow, /fresh-audit-run\.json/);
  assert.match(workflow, /previous_boundary_run_id/);
  assert.match(workflow, /previous_execute_run_id/);
  assert.match(workflow, /PREVIOUS_EXECUTE_RUN_ID" = '29619841184'/);
  assert.match(workflow, /execute_head_sha" = '09cce5e8dac464d8e5f1d0a10446110bd95a9e3f'/);
  assert.match(workflow, /grep -Ec "\$legacy_hidden_pattern"/);
  assert.match(workflow, /grep -Ev "\$legacy_hidden_pattern" SHA256SUMS \| sha256sum --check -/);
  assert.equal((workflow.match(/sparse-checkout: ''/g) || []).length, 2);
  assert.equal((workflow.match(/sparse-checkout-cone-mode: false/g) || []).length, 2);
  assert.equal((workflow.match(/git sparse-checkout disable/g) || []).length, 2);
  assert.equal((workflow.match(/git reset --hard HEAD/g) || []).length, 2);
  assert.equal((workflow.match(/test "\$\(git rev-parse HEAD\)" = "\$GITHUB_SHA"/g) || []).length, 3);
  assert.match(workflow, /fresh_canonical_audit_execution_complete/);
  assert.equal((workflow.match(/include-hidden-files: true/g) || []).length, 3);
  assert.match(workflow, /name: fresh-canonical-audit-boundary-\$\{\{ github\.run_id \}\}[\s\S]*?include-hidden-files: true/);
  assert.match(workflow, /name: fresh-canonical-audit-execution-\$\{\{ github\.run_id \}\}[\s\S]*?include-hidden-files: true/);
  assert.match(workflow, /productionSmokeCompleted:true/);
  assert.match(workflow, /pre-inventory\.json/);
  assert.match(workflow, /skill govern-fresh-canonical-audit/);
  assert.match(workflow, /production-skill-score-writes/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET/);
  assert.match(workflow, /expected.*Pack|post-execution artifact and Pack evidence/i);
  assert.match(workflow, /SMOKE_PUBLIC_CLI_PACKAGES: skillstore@0\.1\.9,skillstore@latest/);
  assert.match(workflow, /production-smoke\.mjs/);
  assert.match(workflow, /MCP channel/);
  assert.match(workflow, /recover-boundary:/);
  assert.match(workflow, /INCIDENT_DRY_RUN_ID: '29646612265'/);
  assert.match(workflow, /INCIDENT_FAILED_EXECUTE_RUN_ID: '29666546406'/);
  assert.match(workflow, /INCIDENT_BOUNDARY_CLI_VERSION: '2\.8\.0'/);
  assert.match(workflow, /INCIDENT_EXECUTE_CLI_VERSION: '2\.8\.2'/);
  assert.match(workflow, /failedExecutionCli:\{version:\$failedExecutionCliVersion,sha256:\$failedExecutionCliSha256\}/);
  assert.match(workflow, /RECOVERY_EXPECTED_CACHE_VERSION: 'v7'/);
  assert.match(workflow, /producerKind:"fresh_canonical_audit_recovery"/);
  assert.match(workflow, /scripts\/verify-fresh-canonical-audit-recovery\.mjs/);
  assert.match(workflow, /scripts\/close-fresh-canonical-audit-cache\.mjs/);
  const recovery = workflow.slice(workflow.indexOf('  recover-boundary:'));
  assert.doesNotMatch(recovery, /skill govern-fresh-canonical-audit|recalculate-scores|record_fresh_canonical_audit/);
});
