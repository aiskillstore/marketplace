import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
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

function exactRecoveryBoundary(row, cohortSha256) {
  return {
    metadata: {
      status: 'fresh_canonical_audit_frozen', runId: '29646612265', lastSelected: row.slug,
      cohortSha256,
    },
    selection: { status: 'lineage_unproven', lastSelected: row.slug },
    executionProof: {
      schemaVersion: 2,
      producerKind: 'fresh_canonical_audit_recovery',
      status: 'fresh_canonical_audit_execution_complete',
      executeRunId: '29668478921',
      dryRunId: '29646612265',
      failedExecuteRunId: '29666546406',
      failedExecuteHeadSha: '3e7baf520a4d078047b53b95352156e3a3f74260',
      workflowCommit: '7e58b46f1a1478773d6d1f5ef5eb4ae5d56d439c',
      lastSelected: row.slug,
      cohortSha256,
      executedCount: 1,
      originalCli: {
        version: '2.8.0',
        sha256: 'ecfaa49aa72d24b8ea6322c7dae24d4bbe9df174a5d009cc56d7d2a89e7ae05a',
      },
      failedExecutionCli: {
        version: '2.8.2',
        sha256: '9b885943950c15555e8fbae522adf2cf9514ae74f63050a905c8e97694d52fcb',
      },
      recoveryRuntime: {
        cacheVersion: 'v7',
        smokeCommit: 'e368da730951aceca17a7e5d9d5a9adc0e3efc2a',
      },
      executionResultsSha256: '1'.repeat(64),
      postInventorySha256: '2'.repeat(64),
      boundaryManifestSha256: '3'.repeat(64),
      recoveryEvidenceManifestSha256: '4'.repeat(64),
      scoreTimestampEvidenceSha256: '5'.repeat(64),
      cacheClosureEvidenceSha256: '6'.repeat(64),
      cacheReadbackSha256: '7'.repeat(64),
      smokeResultSha256: '8'.repeat(64),
      scoreFinalized: true,
      timestampFinalized: true,
      cacheClosureCompleted: true,
      packClosureCompleted: true,
      productionSmokeCompleted: true,
    },
  };
}

function exactCacheRecoveryBoundary(row, cohortSha256) {
  const boundary = exactRecoveryBoundary(row, cohortSha256);
  boundary.metadata.runId = '29682699325';
  Object.assign(boundary.executionProof, {
    executeRunId: '29691166740',
    dryRunId: '29682699325',
    failedExecuteRunId: '29684825610',
    failedExecuteHeadSha: '2bfe0fd5cf25a967c5481dd83207b0de24997273',
    workflowCommit: '15eac13abcacce4146ebfc3069898fe24fbc178d',
    originalCli: {
      version: '2.8.4',
      sha256: '282cfb6103f580c1758674f6d407493b3039a2ca788c986297684180ae6f0dbb',
    },
    failedExecutionCli: {
      version: '2.8.4',
      sha256: '282cfb6103f580c1758674f6d407493b3039a2ca788c986297684180ae6f0dbb',
    },
    recoveryRuntime: {
      cacheVersion: 'v7',
      smokeCommit: '0f78b2d983b0e233f6b7071e38ddf6b4f29c9168',
    },
  });
  return boundary;
}

function exactSmokeRecoveryBoundary(row, cohortSha256) {
  return {
    metadata: {
      status: 'fresh_canonical_audit_frozen', runId: '29669706395', lastSelected: row.slug,
      cohortSha256,
    },
    selection: { status: 'lineage_unproven', lastSelected: row.slug },
    executionProof: {
      schemaVersion: 2,
      producerKind: 'fresh_canonical_audit_smoke_recovery',
      status: 'fresh_canonical_audit_execution_complete',
      executeRunId: 'future-smoke-recovery-run',
      dryRunId: '29669706395',
      failedExecuteRunId: '29671150631',
      failedExecuteHeadSha: '88d62f4c32ec837ef30075b202b81a580b723259',
      workflowCommit: 'f'.repeat(40),
      lastSelected: row.slug,
      cohortSha256,
      executedCount: 1,
      executionResultsSha256: '1'.repeat(64),
      postInventorySha256: '2'.repeat(64),
      boundaryManifestSha256: '3'.repeat(64),
      recoveryEvidenceManifestSha256: '4'.repeat(64),
      smokeResultSha256: '5'.repeat(64),
      failedExecutionCli: {
        version: '2.8.3',
        sha256: '296cab05576adec2c6613255b26663fab58e8f3fa585e2c085cd0367d8c7274f',
      },
      failedSmokeExpectedPublicCliVersion: '0.1.9',
      recoveryRuntime: {
        smokeCommit: 'e368da730951aceca17a7e5d9d5a9adc0e3efc2a',
        publicCliVersion: '0.1.10',
        publicCliIntegrity: 'sha512-HKxQJadsobOSJFrf43w9kPHjwlzel0KC9G0R2tIfHVwIbypj2r0eQE2mZkj07wZKQOtYLbQRBcLi2eZpLftzJw==',
      },
      scoreFinalized: true,
      timestampFinalized: true,
      cacheClosureCompleted: true,
      packClosureCompleted: true,
      productionSmokeCompleted: true,
    },
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

  const recoveryBoundary = exactRecoveryBoundary(row, cohortSha256);
  const recovered = prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1), previousBoundary: recoveryBoundary, cohortSha256,
  });
  assert.equal(recovered.count, 0);
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1),
    previousBoundary: {
      ...recoveryBoundary,
      executionProof: {
        ...recoveryBoundary.executionProof,
        failedExecuteRunId: '29623717000',
      },
    },
    cohortSha256,
  }), /successfully closed previous execution/);

  const cacheRecoveryBoundary = exactCacheRecoveryBoundary(row, cohortSha256);
  const cacheRecovered = prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1), previousBoundary: cacheRecoveryBoundary, cohortSha256,
  });
  assert.equal(cacheRecovered.count, 0);
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1),
    previousBoundary: {
      ...cacheRecoveryBoundary,
      executionProof: {
        ...cacheRecoveryBoundary.executionProof,
        workflowCommit: 'f'.repeat(40),
      },
    },
    cohortSha256,
  }), /successfully closed previous execution/);

  const smokeRecoveryBoundary = exactSmokeRecoveryBoundary(row, cohortSha256);
  const smokeRecovered = prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1), previousBoundary: smokeRecoveryBoundary, cohortSha256,
  });
  assert.equal(smokeRecovered.count, 0);
  assert.throws(() => prepareFreshCanonicalAuditBatch({
    repositoryRoot: root, cohort, startAfter: row.slug, batchSize: 1,
    productionInventory: inventory(row, 1),
    previousBoundary: {
      ...smokeRecoveryBoundary,
      executionProof: {
        ...smokeRecoveryBoundary.executionProof,
        failedSmokeExpectedPublicCliVersion: '0.1.10',
      },
    },
    cohortSha256,
  }), /successfully closed previous execution/);
});

test('workflow is two-phase, CLI-pinned, resumable, and closes P0 channels', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/govern-fresh-canonical-audits.yml', import.meta.url), 'utf8');
  assert.match(workflow, /options: \[dry-run, execute, recover, recover-cache, recover-smoke\]/);
  assert.doesNotMatch(workflow, /options: \[[^\]]*recover-rpc-timeout/);
  assert.match(workflow, /execute-boundary:\n    if: inputs\.mode == 'execute'/);
  assert.match(workflow, /default: '2\.15\.10'/);
  assert.equal((workflow.match(/2ea8ef90fcb890b83b1cf1bd772bd02da3fff98bc8f5162c481287552518bdd8/g) || []).length, 1);
  assert.match(workflow, /DRY_RUN_ID" = '29646612265'/);
  assert.match(workflow, /11101c85a06aaec0d8f0deda0a4aac82cf24899b/);
  assert.match(workflow, /sha256:4d5b40e20e59cd830125e572ed2ba888dcc2ce5309a62001793a87dd8464035b/);
  assert.match(workflow, /git show "11101c85a06aaec0d8f0deda0a4aac82cf24899b:\$path"/);
  assert.ok((workflow.match(/282cfb6103f580c1758674f6d407493b3039a2ca788c986297684180ae6f0dbb/g) || []).length >= 4);
  assert.doesNotMatch(workflow, /3fe1650ff585db24a2708ea26819c22bc9f5fa0702fe703885c41537a08c8de5/);
  assert.equal((workflow.match(/296cab05576adec2c6613255b26663fab58e8f3fa585e2c085cd0367d8c7274f/g) || []).length, 2);
  assert.equal((workflow.match(/9b885943950c15555e8fbae522adf2cf9514ae74f63050a905c8e97694d52fcb/g) || []).length, 2);
  assert.equal((workflow.match(/ecfaa49aa72d24b8ea6322c7dae24d4bbe9df174a5d009cc56d7d2a89e7ae05a/g) || []).length, 4);
  assert.match(workflow, /\[\[ "\$FRESH_GOVERNANCE_CLI_SHA256" =~ \^\[0-9a-f\]\{64\}\$ \]\]/);
  assert.match(workflow, /REPORT_ORIGIN_FRESH_COHORT: 'governance\/fresh-canonical-audit\/raw32-exact62-v1\.json'/);
  assert.match(workflow, /REPORT_ORIGIN_FRESH_COHORT_SHA256: 'c8a2f173067a9064a693669db12db398de1324a044e8ae54176ab368aa3038c3'/);
  assert.match(workflow, /Prove Report-Origin raw32 audits are replacement pointers only/);
  assert.match(workflow, /auditReplacementMode == "commit_addressed"/);
  assert.match(workflow, /invalid Report-Origin replacement proof/);
  assert.match(workflow, /fresh_audit_binding_v3/);
  assert.match(workflow, /\^v3:\[0-9a-f\]\{40\}:\[0-9a-f\]\{64\}:\[0-9a-f\]\{64\}:\[0-9a-f\]\+:\[0-9a-f\]\{32\}\$/);
  assert.match(workflow, /subject_marketplace_commit_sha == \$candidate\.row\.marketplaceCommit/);
  assert.match(workflow, /subject_content_hash == \$candidate\.row\.canonicalArtifact\.contentHash/);
  assert.match(workflow, /subject_tree_hash == \$candidate\.row\.canonicalArtifact\.treeHash/);
  assert.match(workflow, /subject_plugin_path == \$candidate\.row\.path/);
  assert.match(workflow, /commit_addressed_raw32_pointer_replacement/);
  assert.match(workflow, /p_expected_latest_audit_content_hash/);
  assert.match(workflow, /p_expected_source_ref == \$candidate\.row\.marketplaceCommit/);
  assert.match(workflow, /p_expected_skill_report_url == \("https:\/\/github\.com\/aiskillstore\/marketplace\/blob\/"/);
  assert.match(workflow, /skill audit/);
  assert.match(workflow, /target="\$RUNNER_TEMP\/materialized\/\$commit"/);
  assert.match(workflow, /skill audit skills --slugs "\$slugs"/);
  assert.match(workflow, /if \[ "\$audit_status" -eq 132 \]/);
  assert.match(workflow, /rematerializing this local-only audit group for one bounded retry/);
  assert.match(workflow, /rm -rf "\$target"/);
  assert.match(workflow, /rm -f "\$checkpoint" "\$manifest"/);
  assert.match(workflow, /elif \[ "\$audit_status" -ne 0 \]/);
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
  assert.equal((workflow.match(/test "\$\(git rev-parse HEAD\)" = "\$GITHUB_SHA"/g) || []).length, 4);
  assert.match(workflow, /fresh_canonical_audit_execution_complete/);
  assert.equal((workflow.match(/include-hidden-files: true/g) || []).length, 4);
  assert.match(workflow, /name: fresh-canonical-audit-boundary-\$\{\{ github\.run_id \}\}[\s\S]*?include-hidden-files: true/);
  assert.match(workflow, /name: fresh-canonical-audit-execution-\$\{\{ github\.run_id \}\}[\s\S]*?include-hidden-files: true/);
  assert.match(workflow, /productionSmokeCompleted:true/);
  assert.match(workflow, /pre-inventory\.json/);
  assert.match(workflow, /ZERO_WRITE_DRY_RUN_ID: '29743150038'/);
  assert.match(workflow, /ZERO_WRITE_FAILED_RUN_ID: '29744338076'/);
  assert.match(workflow, /ZERO_WRITE_FAILED_ARTIFACT_ID: '8461872394'/);
  assert.match(workflow, /test "\$DRY_RUN_ID" != "\$ZERO_WRITE_DRY_RUN_ID" \|\| \{ echo '::error::sealed zero-write boundary cannot be executed'; exit 1; \}/);
  assert.match(workflow, /verify-fresh-canonical-zero-write-recovery\.mjs/);
  assert.match(workflow, /fresh_canonical_zero_write_recovery/);
  assert.match(workflow, /skill govern-fresh-canonical-audit/);
  assert.match(workflow, /production-skill-score-writes/);
  assert.match(workflow, /CACHE_INVALIDATE_SECRET/);
  assert.match(workflow, /expected.*Pack|post-execution artifact and Pack evidence/i);
  assert.doesNotMatch(workflow, /SMOKE_PUBLIC_CLI_PACKAGES: skillstore@0\.1\.9,skillstore@latest/);
  assert.match(workflow, /SMOKE_PUBLIC_CLI_PACKAGES: skillstore@0\.1\.10,skillstore@latest/);
  assert.match(workflow, /production-smoke\.mjs/);
  assert.match(workflow, /MCP channel/);
  assert.match(workflow, /recover-boundary:/);
  assert.match(workflow, /INCIDENT_DRY_RUN_ID: \$\{\{ inputs\.mode == 'recover-cache' && '29682699325' \|\| '29646612265' \}\}/);
  assert.match(workflow, /INCIDENT_DRY_RUN_SHA: \$\{\{ inputs\.mode == 'recover-cache' && 'e8ce3fcb20197aefea54f9fb43ccce4716e3209c' \|\| '11101c85a06aaec0d8f0deda0a4aac82cf24899b' \}\}/);
  assert.match(workflow, /INCIDENT_FAILED_EXECUTE_RUN_ID: \$\{\{ inputs\.mode == 'recover-cache' && '29684825610' \|\| '29666546406' \}\}/);
  assert.match(workflow, /INCIDENT_FAILED_EXECUTE_SHA: \$\{\{ inputs\.mode == 'recover-cache' && '2bfe0fd5cf25a967c5481dd83207b0de24997273' \|\| '3e7baf520a4d078047b53b95352156e3a3f74260' \}\}/);
  assert.match(workflow, /RECOVERY_INPUT_CLI_VERSION: \$\{\{ inputs\.mode == 'recover-cache' && '2\.8\.4' \|\| '2\.8\.3' \}\}/);
  assert.match(workflow, /RECOVERY_SMOKE_SHA: \$\{\{ inputs\.mode == 'recover-cache' && '0f78b2d983b0e233f6b7071e38ddf6b4f29c9168' \|\| 'e368da730951aceca17a7e5d9d5a9adc0e3efc2a' \}\}/);
  assert.match(workflow, /2\.8\.0/);
  assert.match(workflow, /2\.8\.2/);
  assert.match(workflow, /--expected-failed-run-id/);
  assert.match(workflow, /--expected-failed-run-sha/);
  assert.match(workflow, /failedExecutionCli:\{version:\$failedExecutionCliVersion,sha256:\$failedExecutionCliSha256\}/);
  assert.match(workflow, /RECOVERY_EXPECTED_CACHE_VERSION: 'v7'/);
  assert.match(workflow, /producerKind:"fresh_canonical_audit_recovery"/);
  assert.match(workflow, /scripts\/verify-fresh-canonical-audit-recovery\.mjs/);
  assert.match(workflow, /recover-smoke-boundary:/);
  assert.match(workflow, /INCIDENT_DRY_RUN_ID: '29669706395'/);
  assert.match(workflow, /INCIDENT_FAILED_EXECUTE_RUN_ID: '29671150631'/);
  assert.match(workflow, /fresh_canonical_audit_smoke_recovery/);
  assert.match(workflow, /Recovery ran no governance RPC, score recalculation, or cache invalidation/);
  assert.match(workflow, /scripts\/close-fresh-canonical-audit-cache\.mjs/);
  assert.match(workflow, /def job_rows:/);
  assert.match(workflow, /elif type=="array" and all\(\.\[\]; type=="object" and \(\.jobs\|type\)=="array"\)/);
  const recovery = workflow.slice(workflow.indexOf('  recover-boundary:'));
  assert.doesNotMatch(recovery, /skill govern-fresh-canonical-audit|recalculate-scores|record_fresh_canonical_audit/);
});

test('Report-Origin Fresh-11 cohort is exact, immutable, and source-addressed', () => {
  const bytes = readFileSync(new URL(
    '../../governance/fresh-canonical-audit/report-origin-raw32-v1.json', import.meta.url
  ));
  const cohort = JSON.parse(bytes.toString('utf8'));
  const expectedSlugs = [
    '270aldo-ngx-hybrid-sales',
    '5minfutures-architecture-reference',
    '5minfutures-coding-standards',
    '5minfutures-migration-tracker',
    '5minfutures-portfolio-context',
    '92bilal26-assessment-builder',
    '92bilal26-code-example-generator',
    '92bilal26-concept-scaffolding',
    '92bilal26-exercise-designer',
    '92bilal26-technical-clarity',
    '92bilal26-visual-asset-workflow',
  ];
  assert.equal(createHash('sha256').update(bytes).digest('hex'),
    '261604847b20ede3b31264c4500433692ba38269b32c48e84c78d4609d4568e6');
  assert.equal(cohort.schemaVersion, 1);
  assert.equal(cohort.status, 'lineage_unproven');
  assert.equal(cohort.count, 11);
  assert.deepEqual(cohort.rows.map((row) => row.slug), expectedSlugs);
  assert.equal(new Set(cohort.rows.map((row) => row.skillId)).size, 11);
  assert.equal(new Set(cohort.rows.map((row) => row.path)).size, 11);
  for (const row of cohort.rows) {
    assert.equal(row.marketplaceCommit, '820ccb93d2e2fe828678ed05433bafd1054e5000');
    assert.equal(row.remainingReason, 'same_source_tree_unproven');
    assert.equal(row.governanceEligibleByLineage, false);
    assert.match(row.reportContentHash, /^[0-9a-f]{64}$/);
    assert.match(row.reportTreeHash, /^[0-9a-f]{64}$/);
    assert.match(row.canonicalArtifact.contentHash, /^[0-9a-f]{64}$/);
    assert.match(row.canonicalArtifact.treeHash, /^[0-9a-f]{64}$/);
    assert.notEqual(row.reportTreeHash, row.canonicalArtifact.treeHash);
    assert.deepEqual(row.legacyReference, {
      kind: 'frozen_mutable_main',
      sourceRef: 'main',
      skillReportUrl: `https://github.com/aiskillstore/marketplace/blob/main/${row.path}/skill-report.json`,
    });
  }
});

test('residual raw32 Fresh cohort is exact, commit-pinned, and replacement-only', () => {
  const bytes = readFileSync(new URL(
    '../../governance/fresh-canonical-audit/raw32-exact62-v1.json', import.meta.url
  ));
  const cohort = JSON.parse(bytes.toString('utf8'));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),
    'c8a2f173067a9064a693669db12db398de1324a044e8ae54176ab368aa3038c3');
  assert.equal(cohort.schemaVersion, 1);
  assert.equal(cohort.status, 'lineage_unproven');
  assert.equal(cohort.count, 62);
  assert.equal(cohort.rows.length, 62);
  assert.equal(new Set(cohort.rows.map((row) => row.slug)).size, 62);
  assert.equal(new Set(cohort.rows.map((row) => row.skillId)).size, 62);
  assert.equal(new Set(cohort.rows.map((row) => row.path)).size, 62);
  assert.deepEqual([...new Set(cohort.rows.map((row) => row.marketplaceCommit))].sort(), [
    '14dc8f201a64f8d30fd131d7f036cd5e788be523',
    '3f6e026a3363e0954ede7bef0cfe88d4475de137',
    'd1c4c60b80afc545d96b5e8a51c19b2fdc81df70',
  ]);
  for (const row of cohort.rows) {
    assert.equal(row.remainingReason, 'same_source_tree_unproven');
    assert.equal(row.governanceEligibleByLineage, false);
    assert.match(row.reportContentHash, /^[0-9a-f]{64}$/);
    assert.match(row.reportTreeHash, /^[0-9a-f]{64}$/);
    assert.equal(row.reportContentHash, row.canonicalArtifact.contentHash);
    assert.equal(row.reportTreeHash, row.canonicalArtifact.treeHash);
    assert.equal(row.legacyReference, undefined);
  }
});
