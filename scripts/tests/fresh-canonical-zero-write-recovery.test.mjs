import assert from 'node:assert/strict';
import test from 'node:test';
import { INCIDENT, verifyZeroWriteRecovery } from '../verify-fresh-canonical-zero-write-recovery.mjs';

function fixture() {
  const successfulPrerequisites = [
    'Checkout complete Marketplace history',
    'Normalize full checkout and verify governance runtime',
    'Validate execute inputs',
    'Download and authenticate the successful frozen boundary',
    'Generate GitHub App token',
    'Download exact audited CLI 2.15.5',
    'Verify frozen CLI identity',
    'Rematerialize exact source and overlay only frozen fresh reports',
  ];
  const candidates = Array.from({ length: 10 }, (_, index) => {
    const n = String(index + 1).padStart(12, '0');
    const id = `11111111-1111-4111-8111-${n}`;
    return {
      row: { skillId: id, slug: `owner-skill-${index}` },
      rpcPayload: {
        p_expected_legacy_content_hash: 'a'.repeat(64),
        p_expected_legacy_tree_hash: 'b'.repeat(64),
        p_expected_latest_audit_id: `22222222-2222-4222-8222-${n}`,
      },
    };
  });
  const rows = candidates.map((candidate) => ({
    id: candidate.row.skillId, slug: candidate.row.slug, plugin_path: `skills/${candidate.row.slug}`,
    marketplace_commit_sha: INCIDENT.dryRun.sha, content_hash: 'a'.repeat(64), tree_hash: 'b'.repeat(64),
    artifact_revision: 0, current_artifact_version_id: null, status: 'approved', public_eligible: true,
    public_eligibility_audit_id: candidate.rpcPayload.p_expected_latest_audit_id,
    published_at: '2026-07-01T00:00:00Z', updated_at: '2026-07-20T12:30:00Z',
    quality_score: 82, quality_tier: 'good', quality_score_calculated_at: '2026-07-20T12:00:00Z',
    current_quality_score_snapshot_id: `33333333-3333-4333-8333-${candidate.row.skillId.slice(-12)}`,
  }));
  const run = (expected, conclusion) => ({ id: expected.id, head_sha: expected.sha,
    name: 'Govern Fresh Canonical Audits', event: 'workflow_dispatch', head_branch: 'main',
    run_attempt: 1, actor: { login: 'mylukin' }, triggering_actor: { login: 'mylukin' }, conclusion });
  const artifact = (expected, name) => ({ artifacts: [{ id: expected.artifactId, name,
    expired: false, digest: expected.artifactDigest }] });
  return {
    boundary: { schemaVersion: 1, status: 'fresh_canonical_audit_frozen', candidates },
    originalInventory: { rows, artifacts: [], observations: [] },
    currentInventory: { rows: structuredClone(rows), artifacts: [], observations: [] },
    dryRun: run(INCIDENT.dryRun, 'success'), failedRun: run(INCIDENT.failedRun, 'failure'),
    dryArtifacts: artifact(INCIDENT.dryRun, `fresh-canonical-audit-boundary-${INCIDENT.dryRun.id}`),
    failedArtifacts: artifact(INCIDENT.failedRun, `fresh-canonical-audit-execution-${INCIDENT.failedRun.id}`),
    failedJobs: { jobs: [{ id: INCIDENT.failedRun.jobId, name: 'execute-boundary',
      runner_id: INCIDENT.failedRun.runnerId, runner_name: INCIDENT.failedRun.runnerName,
      conclusion: 'failure', steps: [
        ...successfulPrerequisites.map((name) => ({ name, conclusion: 'success' })),
        { name: 'Execute resumable compound governance, score, and cache closure', conclusion: 'failure' },
        { name: 'Fetch exact post-execution artifact and Pack evidence', conclusion: 'skipped' },
        { name: 'Verify every P0/P1 download, install, NPX, Pack, and MCP channel', conclusion: 'skipped' },
        { name: 'Seal successful execute closure for the next cursor', conclusion: 'skipped' },
      ] }] },
  };
}

test('accepts only the exact zero-write incident and unchanged ten-row CAS boundary', () => {
  assert.deepEqual(verifyZeroWriteRecovery(fixture()), { count: 10 });
});

test('rejects tampered run, SHA, job, artifact, digest, boundary, and production state', () => {
  const mutations = [
    (x) => { x.failedRun.id += 1; },
    (x) => { x.failedRun.head_sha = 'f'.repeat(40); },
    (x) => { x.failedRun.actor.login = 'someone-else'; },
    (x) => { x.failedJobs.jobs[0].id += 1; },
    (x) => { x.failedArtifacts.artifacts[0].id += 1; },
    (x) => { x.failedArtifacts.artifacts[0].digest = `sha256:${'f'.repeat(64)}`; },
    (x) => { x.boundary.candidates.pop(); },
    (x) => { x.currentInventory.rows[0].content_hash = 'f'.repeat(64); },
    (x) => { x.currentInventory.rows[0].quality_score = 1; },
    (x) => { x.currentInventory.artifacts.push({ skill_id: x.currentInventory.rows[0].id }); },
    (x) => { x.failedJobs.jobs[0].steps = x.failedJobs.jobs[0].steps.filter((step) => step.name !== 'Verify frozen CLI identity'); },
    (x) => { x.failedJobs.jobs[0].steps.find((step) => step.name === 'Rematerialize exact source and overlay only frozen fresh reports').conclusion = 'failure'; },
  ];
  for (const mutate of mutations) {
    const input = fixture();
    mutate(input);
    assert.throws(() => verifyZeroWriteRecovery(input));
  }
});
