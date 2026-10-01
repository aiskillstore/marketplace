import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const repo = 'aiskillstore/marketplace';
const prefix = `repos/${repo}`;
const successfulStep = (jobs, name) => {
  const steps = jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
  return steps.length === 1 && steps[0].conclusion === 'success';
};
function jobsFor(run, request) {
  const result = request(`${prefix}/actions/runs/${run.id}/attempts/${run.run_attempt}/jobs?per_page=100`);
  if (result.total_count !== result.jobs?.length) throw new Error('Incomplete sync jobs evidence');
  return result.jobs;
}

// A failed provider write is never replayed automatically. An inspected,
// outbox-owned source-monitor recovery can close exactly its original push.
export function recoveredPushSync(push, runs, request) {
  const sourceMonitor = recoveredSourceMonitorPushSync(push, runs, request);
  if (sourceMonitor) return sourceMonitor;
  // A separate verifier performs provider GETs, exact pinned-tree/artifact checks,
  // then records a NEW context. Never turn an arbitrary green manual run or the
  // old failed publication status into success.
  if (!push || push.event !== 'push' || push.status !== 'completed'
    || push.conclusion !== 'failure' || !/^[a-f0-9]{40}$/.test(push.head_sha ?? '')
    || !Number.isSafeInteger(push.id) || push.id < 1) return null;
  const context = `agentcrew/provider-reconciliation/${push.id}`;
  const status = request(`${prefix}/commits/${push.head_sha}/status`).statuses.find(s => s.context === context);
  if (status?.state !== 'success' || status.creator?.id !== 41898282
    || status.creator.login !== 'github-actions[bot]') return null;
  const match = status.target_url?.match(/^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/([1-9][0-9]*)$/);
  if (!match) return null;
  const proof = request(`${prefix}/actions/runs/${match[1]}`);
  if (String(proof.id) !== match[1] || proof.event !== 'workflow_dispatch'
    || proof.status !== 'completed' || proof.conclusion !== 'success'
    || proof.path !== '.github/workflows/reconcile-submission-sync.yml'
    || proof.head_branch !== 'main' || proof.head_repository?.full_name !== repo
    || !Number.isSafeInteger(proof.run_attempt) || proof.run_attempt < 1
    || !(Date.parse(proof.created_at) > Date.parse(push.created_at))
    || !new RegExp(`^Reconcile submission push ${push.id} using recovery [1-9][0-9]*$`).test(proof.display_title ?? '')) return null;
  const jobs = jobsFor(proof, request);
  if (!['Verify exact recovery and provider state', 'Record separate reconciliation result']
    .every(name => successfulStep(jobs, name))) return null;
  return proof;
}

function recoveredSourceMonitorPushSync(push, runs, request) {
  if (!push || push.event !== 'push' || push.status !== 'completed'
    || !['failure', 'cancelled'].includes(push.conclusion)
    || !/^[a-f0-9]{40}$/.test(push.head_sha ?? '')) return null;
  const candidates = runs.filter(r => r.event === 'workflow_dispatch'
    && r.status === 'completed' && r.conclusion === 'success'
    && r.head_branch === 'main' && r.head_repository?.full_name === repo
    && r.path === '.github/workflows/sync-to-supabase.yml'
    && r.created_at > push.created_at
    && /^Provider sync source-monitor-pr-[1-9][0-9]*-[a-f0-9]{40}-[a-f0-9]{40}-[a-f0-9]{64}$/.test(r.display_title ?? '')
    && r.display_title.split('-').at(-2) === push.head_sha);
  if (!candidates.length) return null;
  const baseline = runs.filter(r => r.event === 'push' && r.status === 'completed'
    && r.created_at < push.created_at).sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
  if (!baseline || baseline.conclusion !== 'success') return null;
  const originalJobs = jobsFor(push, request);
  if (!successfulStep(originalJobs, 'Wait for authoritative publication completion')) return null;
  const provider = originalJobs.flatMap(j => j.steps ?? []).filter(s => s.name === 'Sync skills to Supabase');
  if (provider.length !== 1 || !['failure', 'cancelled'].includes(provider[0].conclusion)) return null;
  const commit = request(`${prefix}/git/commits/${push.head_sha}`);
  // ponytail: recover a single merge immediately after a complete push baseline;
  // accumulated ranges require separate inspection rather than guessing coverage.
  if (commit.parents?.length !== 2 || commit.parents[0].sha !== baseline.head_sha) return null;
  for (const recovery of candidates) {
    const correlation = recovery.display_title.slice('Provider sync '.length);
    const head = correlation.match(/^source-monitor-pr-[1-9][0-9]*-([a-f0-9]{40})-/)[1];
    if (commit.parents[1].sha !== head) continue;
    const jobs = jobsFor(recovery, request);
    if (!['Validate trusted sync correlation', 'Verify durable provider sync dispatch outbox',
      'Sync skills to Supabase', 'Upload provider-complete synced slugs artifact',
      'Record durable correlated manual sync result'].every(name => successfulStep(jobs, name))) continue;
    const context = `agentcrew/provider-sync/${createHash('sha256').update(correlation).digest('hex')}`;
    const status = request(`${prefix}/commits/${push.head_sha}/status`).statuses.find(s => s.context === context);
    if (status?.state === 'success'
      && status.target_url === `https://github.com/${repo}/actions/runs/${recovery.id}`) return recovery;
  }
  return null;
}

function api(endpoint) {
  return JSON.parse(execFileSync('gh', ['api', endpoint], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  const runId = process.argv[2];
  if (!/^[1-9][0-9]*$/.test(runId ?? '')) throw new Error('An exact failed push run ID is required');
  const runs = api(`${prefix}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`).workflow_runs;
  const recovery = recoveredPushSync(runs.find(r => String(r.id) === runId), runs, api);
  if (recovery) console.log(`Push sync ${runId} reconciled by verified recovery ${recovery.id}`);
  else process.exitCode = 1;
}
