import assert from 'node:assert/strict';
import test from 'node:test';
import { closeFreshAuditCaches } from '../close-fresh-canonical-audit-cache.mjs';
import {
  assignFreshAuditLanes,
  buildCampaignManifest,
  createCampaignLedger,
  finalizeCampaign,
  immutableEvidenceKeys,
  immutableFreshAuditKey,
  transitionCampaignItem,
} from '../fresh-canonical-audit-campaign.mjs';
import { verifyRecoveryState } from '../verify-fresh-canonical-audit-recovery.mjs';

const ids = {
  skill: '11111111-1111-4111-8111-111111111111',
  oldAudit: '22222222-2222-4222-8222-222222222222',
  audit: '33333333-3333-4333-8333-333333333333',
  artifact: '44444444-4444-4444-8444-444444444444',
  snapshot: '55555555-5555-4555-8555-555555555555',
};
const commit = 'a'.repeat(40);
const content = 'b'.repeat(64);
const tree = 'c'.repeat(64);
const auditContent = `v3:${commit}:${content}:${tree}:path:payload`;
const failedRun = {
  id: 29666546406,
  head_sha: '3e7baf520a4d078047b53b95352156e3a3f74260',
  conclusion: 'failure', event: 'workflow_dispatch', head_branch: 'main', run_attempt: 1,
  run_started_at: '2026-07-19T00:11:42Z', updated_at: '2026-07-19T00:16:10Z',
};

function fixture() {
  const candidate = {
    row: { slug: 'owner-skill', skillId: ids.skill, marketplaceCommit: commit,
      path: 'skills/owner/skill', canonicalArtifact: { contentHash: content, treeHash: tree } },
    expectedSkill: { published_at: '2026-07-01T00:00:00Z', updated_at: '2026-07-02T00:00:00Z' },
    expectedLatestAudit: { id: ids.oldAudit, version: 4 },
    auditId: ids.audit,
    rpcPayload: { p_audit_payload: { content_hash: auditContent } },
  };
  const skill = {
    id: ids.skill, slug: 'owner-skill', status: 'approved', public_eligible: true,
    artifact_revision: 1, current_artifact_version_id: ids.artifact,
    content_hash: content, tree_hash: tree, marketplace_commit_sha: commit,
    plugin_path: 'skills/owner/skill', public_eligibility_audit_id: ids.audit,
    current_quality_score_snapshot_id: ids.snapshot, quality_score: 88, quality_tier: 'silver',
    quality_score_calculated_at: '2026-07-19T00:12:55Z',
    published_at: '2026-07-01T00:00:00Z', updated_at: '2026-07-02T00:00:00Z',
  };
  return {
    boundary: { schemaVersion: 1, status: 'fresh_canonical_audit_frozen', candidates: [candidate] },
    inventory: { schemaVersion: 2, rows: [skill], artifacts: [{
      id: ids.artifact, skill_id: ids.skill, artifact_revision: 1, change_kind: 'initial',
      previous_version_id: null, content_hash: content, tree_hash: tree,
      marketplace_commit_sha: commit, source_path: 'skills/owner/skill', created_at: '2026-07-19T00:12:45Z',
    }], observations: [{
      id: '66666666-6666-4666-8666-666666666666',
      skill_id: ids.skill,
      artifact_version_id: ids.artifact,
      marketplace_commit_sha: commit,
      source_path: 'skills/owner/skill',
      created_at: '2026-07-19T00:12:45Z',
    }] },
    audits: [{ id: ids.audit, skill_id: ids.skill, version: 5, content_hash: auditContent,
      analysis_status: 'ok', derived_from_audit_id: null, derivation_kind: null,
      subject_marketplace_commit_sha: commit, subject_content_hash: content,
      subject_tree_hash: tree, subject_plugin_path: 'skills/owner/skill',
      created_at: '2026-07-19T00:12:45Z' }],
    snapshots: [{ id: ids.snapshot, skill_id: ids.skill, scorer_version: '1.9.1',
      composite_score: 88, quality_tier: 'silver', calculated_at: '2026-07-19T00:12:55Z',
      created_at: '2026-07-19T00:12:55Z', score_inputs: {
        skill: { updatedAt: '2026-07-02T00:00:00Z' },
      }, score_subject: {
        auditId: ids.audit, auditVersion: 5, auditContentHash: auditContent,
        contentHash: content, treeHash: tree, marketplaceCommitSha: commit, pluginPath: 'skills/owner/skill',
      } }],
    breakdowns: [{
      skill_id: ids.skill, score_snapshot_id: ids.snapshot, stale_at: null, stale_reason: null,
      calculated_at: '2026-07-19T00:12:55Z', scorer_version: '1.9.1', composite_score: 88,
    }],
    failedRun,
  };
}

test('reconstructs deterministic execution results only from exact incident-bound durable state', () => {
  const result = verifyRecoveryState(fixture());
  assert.deepEqual(result.executionResults, [{
    slug: 'owner-skill', skillId: ids.skill, artifactVersionId: ids.artifact,
    artifactRevision: 1, artifactCreated: true, auditId: ids.audit,
    auditVersion: 5, scoreSnapshotId: ids.snapshot, scoreBreakdownVerified: true,
  }]);
  assert.equal(result.recoveryEvidence.verifiedCount, 1);
  assert.equal(result.expectedScoreEvidence.scores[0].qualityScore, 88);
});

test('rejects later mutation, wrong snapshot binding, or a different failed run', () => {
  const later = fixture();
  later.inventory.artifacts[0].created_at = '2026-07-19T00:17:00Z';
  assert.throws(() => verifyRecoveryState(later), /artifact evidence mismatch/);
  const snapshot = fixture();
  snapshot.snapshots[0].score_subject.auditId = ids.oldAudit;
  assert.throws(() => verifyRecoveryState(snapshot), /score subject mismatch/);
  const run = fixture();
  run.failedRun.run_attempt = 2;
  assert.throws(() => verifyRecoveryState(run), /failed run identity/);
});

function preflight(slug, packs = []) {
  const planHash = Buffer.from(`${slug}:${packs.join(',')}`)
    .toString('hex').padEnd(64, '0').slice(0, 64);
  return {
    preflight: true, type: 'skills', slugs: [slug],
    locales: ['en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'de', 'fr', 'es', 'pt', 'ru', 'ar'],
    catalogEpoch: 'epoch-test',
    planHash,
    closure: { dependentPacks: { all: packs, warmable: packs, overflow: false, cap: 100 } },
    plan: {
      primary: { resources: 1, api: 253, page: 231, artifactPrefixes: 2, artifacts: 0, artifactListOperations: 2 },
      dependentPacks: { resources: packs.length, api: packs.length * 33, page: packs.length * 66, artifactPrefixes: packs.length, artifacts: 0, artifactListOperations: packs.length },
      totals: {
        resources: 1 + packs.length,
        api: 253 + packs.length * 33,
        page: 231 + packs.length * 66,
        artifactPrefixes: 2 + packs.length,
        artifacts: 0,
        artifactListOperations: 2 + packs.length,
        listWrites: 2,
        kvOperations: packs.length ? 588 : 488,
      },
    },
    invalidated: {
      total: 0, api: 0, page: 0, artifacts: 0,
      listVersionBumped: false, listMaxStaleSeconds: 0,
    },
  };
}

function executed(plan) {
  return {
    preflight: false, type: 'skills', slugs: plan.slugs, locales: plan.locales,
    catalogEpoch: plan.catalogEpoch,
    planHash: plan.planHash,
    closure: plan.closure, plan: plan.plan,
    invalidated: {
      total: 484, api: 253, page: 231, artifacts: 0,
      listVersionBumped: true, listMaxStaleSeconds: 0,
    },
    ...(plan.closure.dependentPacks.all.length ? { dependentPacks: {
      slugs: plan.closure.dependentPacks.all,
      anonymousWarmableSlugs: plan.closure.dependentPacks.warmable,
      invalidated: {
        total: 99, api: 33, page: 66, artifacts: 0,
        listVersionBumped: true, listMaxStaleSeconds: 0,
      },
    } } : {}),
  };
}

test('closes cache one Skill at a time and binds execution to exact Pack closure', async () => {
  const requests = [];
  const plans = new Map();
  const result = await closeFreshAuditCaches({
    secret: 'secret', slugs: ['beta', 'alpha'], sleepImpl: async () => {},
    fetchImpl: async (_url, init) => {
      const body = JSON.parse(init.body);
      requests.push(body);
      if (body.preflight) {
        const plan = preflight(body.slugs[0], body.slugs[0] === 'alpha' ? ['pack-a'] : []);
        plans.set(body.slugs[0], plan);
        return new Response(JSON.stringify(plan), { status: 200 });
      }
      return new Response(JSON.stringify(executed(plans.get(body.slugs[0]))), { status: 200 });
    },
  });
  assert.equal(result.closedCount, 2);
  assert.deepEqual(result.slugs, ['alpha', 'beta']);
  assert(requests.every((request) => request.slugs.length === 1));
  assert.deepEqual(requests[1].expectedDependentPacks, ['pack-a']);
  assert.equal(requests[1].expectedPlanHash, plans.get('alpha').planHash);
});

test('accepts evolved cache-key counts only when the full bounded plan reconciles', async () => {
  const evolved = preflight('alpha');
  evolved.plan.primary.api = 260;
  evolved.plan.totals.api = 260;
  evolved.plan.totals.kvOperations = 495;
  const execution = executed(evolved);
  execution.invalidated.api = 260;
  execution.invalidated.total = 491;
  let calls = 0;
  const result = await closeFreshAuditCaches({
    secret: 'secret', slugs: ['alpha'], sleepImpl: async () => {},
    fetchImpl: async () => {
      calls += 1;
      return new Response(JSON.stringify(calls === 1 ? evolved : execution), { status: 200 });
    },
  });
  assert.equal(result.closedCount, 1);

  const malformed = preflight('alpha');
  malformed.plan.totals.kvOperations += 1;
  let malformedCalls = 0;
  await assert.rejects(closeFreshAuditCaches({
    secret: 'secret', slugs: ['alpha'], sleepImpl: async () => {},
    fetchImpl: async () => {
      malformedCalls += 1;
      return new Response(JSON.stringify(malformed), { status: 200 });
    },
  }), /invalid cache preflight contract/);
  assert.equal(malformedCalls, 1);
});

test('retries an aborted per-Skill execution and refreshes an explicit closure drift', async () => {
  let preflights = 0;
  let executes = 0;
  let activePlan;
  const result = await closeFreshAuditCaches({
    secret: 'secret', slugs: ['alpha'], sleepImpl: async () => {},
    fetchImpl: async (_url, init) => {
      const body = JSON.parse(init.body);
      if (body.preflight) {
        preflights += 1;
        activePlan = preflight('alpha', preflights === 1 ? ['pack-a'] : ['pack-b']);
        return new Response(JSON.stringify(activePlan), { status: 200 });
      }
      executes += 1;
      if (executes === 1) throw new Error('The operation was aborted.');
      if (executes === 2) return new Response(JSON.stringify({
        message: 'Dependent pack closure changed; run preflight again',
      }), { status: 409 });
      return new Response(JSON.stringify(executed(activePlan)), { status: 200 });
    },
  });
  assert.equal(result.closedCount, 1);
  assert.equal(preflights, 2);
  assert.equal(executes, 3);
  assert.deepEqual(result.results[0].preflight.closure.dependentPacks.all, ['pack-b']);
});

test('campaign manifest and finalizer are deterministic and reject partial ledgers', () => {
  const rows = [{ slug: 'beta' }, { slug: 'alpha' }, { slug: 'gamma' }];
  const manifest = buildCampaignManifest({ campaignId: 'fresh-2026', cohortSha256: 'f'.repeat(64), rows, shardSize: 2 });
  assert.deepEqual(manifest.shards.map((shard) => shard.slugs), [['alpha', 'beta'], ['gamma']]);
  const ledger = manifest.shards.map((shard) => ({
    shardId: shard.shardId, status: 'fresh_canonical_audit_execution_complete',
    count: shard.count, endInclusive: shard.endInclusive, proofSha256: 'e'.repeat(64),
  }));
  assert.equal(finalizeCampaign({ manifest, ledger }).completedCount, 3);
  assert.throws(() => finalizeCampaign({ manifest, ledger: ledger.slice(0, 1) }), /incomplete shard/);
});

test('campaign ledger enforces hashed state transitions and deterministic audit lanes', () => {
  const manifest = buildCampaignManifest({
    campaignId: 'fresh-2026',
    cohortSha256: 'f'.repeat(64),
    rows: [
      { slug: 'delta', requiresFreshAudit: false },
      { slug: 'charlie' },
      { slug: 'bravo' },
      { slug: 'alpha' },
    ],
    shardSize: 2,
  });
  assert.deepEqual(
    assignFreshAuditLanes(manifest, 2).map((lane) => lane.slugs),
    [['alpha', 'charlie'], ['bravo']]
  );
  const ledger = createCampaignLedger(manifest);
  const planned = ledger.find((entry) => entry.slug === 'alpha');
  const evidence = transitionCampaignItem(planned, {
    fromInputSha256: planned.inputSha256,
    outputSha256: 'a'.repeat(64),
    to: 'EVIDENCE_READY',
    attempt: 1,
  });
  assert.equal(evidence.state, 'EVIDENCE_READY');
  assert.throws(() => transitionCampaignItem(evidence, {
    fromInputSha256: planned.inputSha256,
    outputSha256: 'b'.repeat(64),
    to: 'COMMIT_READY',
    attempt: 2,
  }), /stale campaign input/);
});

test('immutable evidence and Fresh audit keys bind source and campaign identity', () => {
  const keys = immutableEvidenceKeys({
    commit: 'a'.repeat(40),
    path: 'skills/owner/skill',
    sourceDigest: 'b'.repeat(64),
    treeHash: 'c'.repeat(64),
  });
  assert.match(keys.source, /^source\/v1\/[0-9a-f]{40}\/[0-9a-f]{64}\/[0-9a-f]{64}\.tar\.zst$/);
  assert.equal(keys.evidence, `evidence/v1/${'b'.repeat(64)}.json`);
  assert.equal(immutableFreshAuditKey({
    campaignId: 'fresh-2026',
    model: 'sol-high',
    policyVersion: 'policy-v3',
    promptVersion: 'prompt-v2',
    scannerVersion: 'scanner-v1',
    subjectDigest: 'd'.repeat(64),
  }), `fresh-audit/fresh-2026/${'d'.repeat(64)}/scanner-v1/policy-v3/sol-high/prompt-v2.json`);
});
