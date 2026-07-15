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
  writeFileSync(join(root, 'skills', 'owner', 'skill', 'SKILL.md'), '---\nname: skill\n---\n');
  writeFileSync(join(root, 'skills', 'owner', 'skill', 'skill-report.json'), '{}\n');
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
      status: 'fresh_canonical_audit_execution_complete', executeRunId: '456',
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
  assert.match(workflow, /options: \[dry-run, execute\]/);
  assert.match(workflow, /default: '2\.8\.0'/);
  assert.equal((workflow.match(/ecfaa49aa72d24b8ea6322c7dae24d4bbe9df174a5d009cc56d7d2a89e7ae05a/g) || []).length, 2);
  assert.match(workflow, /\[\[ "\$audited" =~ \^\[0-9a-f\]\{64\}\$ \]\]/);
  assert.match(workflow, /skill audit/);
  assert.match(workflow, /fresh-run-manifest-file/);
  assert.match(workflow, /fresh-audit-run\.json/);
  assert.match(workflow, /previous_boundary_run_id/);
  assert.match(workflow, /previous_execute_run_id/);
  assert.match(workflow, /fresh_canonical_audit_execution_complete/);
  assert.match(workflow, /productionSmokeCompleted:true/);
  assert.match(workflow, /pre-inventory\.json/);
  assert.match(workflow, /skill govern-fresh-canonical-audit/);
  assert.match(workflow, /production-skill-score-writes/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET/);
  assert.match(workflow, /expected.*Pack|post-execution artifact and Pack evidence/i);
  assert.match(workflow, /SMOKE_PUBLIC_CLI_PACKAGES: skillstore@0\.1\.9,skillstore@latest/);
  assert.match(workflow, /production-smoke\.mjs/);
  assert.match(workflow, /MCP channel/);
});
