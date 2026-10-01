import assert from 'node:assert/strict';
import test from 'node:test';
import { createHash } from 'node:crypto';
import { recoveredPushSync } from '../recovered-push-sync.mjs';
import { admitMonitor } from '../source-monitor-admission.mjs';

const repo = 'aiskillstore/marketplace';
const baseline = { id: 1, event: 'push', status: 'completed', conclusion: 'success',
  head_sha: 'a'.repeat(40), created_at: '2026-09-21T00:00:00Z' };
const push = { id: 2, run_attempt: 1, event: 'push', status: 'completed', conclusion: 'failure',
  head_sha: 'b'.repeat(40), created_at: '2026-09-22T00:00:00Z' };
const correlation = `source-monitor-pr-12-${'c'.repeat(40)}-${push.head_sha}-${'d'.repeat(64)}`;
const recovery = { id: 3, run_attempt: 1, event: 'workflow_dispatch', status: 'completed', conclusion: 'success',
  head_branch: 'main', head_repository: { full_name: repo }, path: '.github/workflows/sync-to-supabase.yml',
  head_sha: 'e'.repeat(40), created_at: '2026-09-23T00:00:00Z', display_title: `Provider sync ${correlation}` };
const steps = ['Validate trusted sync correlation', 'Verify durable provider sync dispatch outbox',
  'Sync skills to Supabase', 'Upload provider-complete synced slugs artifact', 'Record durable correlated manual sync result']
  .map(name => ({ name, conclusion: 'success' }));
const context = `agentcrew/provider-sync/${createHash('sha256').update(correlation).digest('hex')}`;
function evidence({ parents = [baseline.head_sha, 'c'.repeat(40)], recoverySteps = steps,
  provider = 'failure', publication = 'success', totalCount = 1, status = {} } = {}) {
  return endpoint => {
    if (endpoint.includes('/runs/2/attempts/1/jobs')) return { total_count: 1, jobs: [{ steps: [
      { name: 'Wait for authoritative publication completion', conclusion: publication },
      { name: 'Sync skills to Supabase', conclusion: provider },
    ] }] };
    if (endpoint.includes('/runs/3/attempts/1/jobs')) return { total_count: totalCount, jobs: [{ steps: recoverySteps }] };
    if (endpoint.includes('/git/commits/')) return { parents: parents.map(sha => ({ sha })) };
    if (endpoint.includes('/statuses?')) return [];
    if (endpoint.endsWith('/status')) return { statuses: [{ context, state: 'success',
      target_url: `https://github.com/${repo}/actions/runs/3`, ...status }] };
    throw new Error(`Unexpected endpoint: ${endpoint}`);
  };
}

test('only exact, reserved and fully closed recovery reconciles a failed push', () => {
  const runs = [recovery, push, baseline];
  assert.equal(recoveredPushSync(push, runs, evidence()), recovery);
  for (const changes of [{ conclusion: 'failure' }, { status: 'in_progress' }, { head_branch: 'other' },
    { head_repository: { full_name: 'other/repo' } }, { path: 'other.yml' },
    { created_at: baseline.created_at }, { display_title: 'Provider sync unrelated' },
    { display_title: recovery.display_title.replace(push.head_sha, 'f'.repeat(40)) }]) {
    assert.equal(recoveredPushSync(push, [{ ...recovery, ...changes }, push, baseline], evidence()), null);
  }
  for (const name of steps.map(s => s.name)) {
    for (const conclusion of ['failure', 'skipped']) assert.equal(recoveredPushSync(push, runs,
      evidence({ recoverySteps: steps.map(s => s.name === name ? { ...s, conclusion } : s) })), null);
  }
  for (const overrides of [
    { parents: ['f'.repeat(40), 'c'.repeat(40)] }, { parents: [baseline.head_sha, 'f'.repeat(40)] },
    { provider: 'success' }, { publication: 'failure' }, { recoverySteps: steps.slice(1) },
    { recoverySteps: [...steps, steps[0]] }, { status: { state: 'pending' } },
    { status: { target_url: `https://github.com/${repo}/actions/runs/99` } },
  ]) assert.equal(recoveredPushSync(push, runs, evidence(overrides)), null);
  assert.throws(() => recoveredPushSync(push, runs, evidence({ totalCount: 101 })), /Incomplete/);
  assert.equal(recoveredPushSync(push, [recovery, push, { ...baseline, conclusion: 'failure' }], evidence()), null);
  assert.equal(recoveredPushSync(push, [push, baseline], endpoint => {
    assert.equal(endpoint, `repos/${repo}/commits/${push.head_sha}/statuses?per_page=100&page=1`);
    return []; // Separate reconciliation is discovered by exact status, not recent run lists.
  }), null);
});

test('monitor releases only the reconciled push; unrelated manual success still blocks', () => {
  const request = endpoint => endpoint.endsWith('git/trees/main') ? { tree: [] }
    : endpoint.includes('/workflows/') ? { workflow_runs: endpoint.includes('sync-to-supabase') ? [recovery, push, baseline] : [] }
      : evidence()(`repos/${repo}/${endpoint}`);
  assert.equal(admitMonitor(request), '');
  assert.match(admitMonitor(endpoint => endpoint.includes('/workflows/sync-to-supabase')
    ? { workflow_runs: [push, baseline, { ...recovery, display_title: 'Manual sync' }] } : request(endpoint)), /needs recovery/);
});
