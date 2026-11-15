import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const repo = 'aiskillstore/marketplace';
const prefix = `repos/${repo}`;
const unavailable = 'The job was not acquired by Runner of type self-hosted even after multiple attempts';
const validId = id => Number.isSafeInteger(id) && id > 0;

// This is evidence for a NEW inspected initial-sync recovery, not permission to
// rerun the old workflow. Empty steps without GitHub's runner annotation fail closed.
export function verifyUnstartedProviderRecovery({run, commit, attempts, statuses, publisher}) {
  assert.ok(validId(run.id) && Number.isSafeInteger(run.run_attempt) && run.run_attempt >= 1 && run.run_attempt <= 8);
  assert.ok(run.event === 'push' && run.status === 'completed' && run.conclusion === 'failure'
    && run.path === '.github/workflows/sync-to-supabase.yml' && run.head_branch === 'main'
    && run.head_repository?.full_name === repo && /^[a-f0-9]{40}$/.test(run.head_sha));
  assert.equal(commit.sha, run.head_sha, 'Publication source mismatch');
  const correlations = [...commit.message.matchAll(/^AgentCrew-Publication: (submission-pr-[1-9][0-9]*-[a-f0-9]{40}-[a-f0-9]{40})$/gm)];
  assert.equal(correlations.length, 1, 'One exact original publication required');
  const correlation = correlations[0][1];
  const digest = createHash('sha256').update(correlation).digest('hex');
  const owner = statuses.find(s => s.context === `agentcrew/publication/${digest}`);
  assert.ok(owner?.creator?.id === 254047988 && owner.creator.login === 'ai-skill-store[bot]'
    && ['pending','success'].includes(owner.state) && validId(publisher.id) && owner?.target_url === `https://github.com/${repo}/actions/runs/${publisher.id}`
    && publisher.event === 'workflow_dispatch' && publisher.status === 'completed' && publisher.conclusion === 'success'
    && publisher.head_branch === 'main' && publisher.head_repository?.full_name === repo
    && ((publisher.path === '.github/workflows/publish-approved-batch.yml' && publisher.display_title === `Publication batch ${digest}`)
      || (publisher.path === '.github/workflows/on-pr-merge.yml' && publisher.display_title === `Publication ${correlation}`)), 'Unverified publication reservation owner');
  assert.equal(attempts?.length, run.run_attempt, 'Every historical attempt is required');
  let unacquired = 0;
  for (let index = 0; index < attempts.length; index++) {
    const {number, jobs, annotations} = attempts[index];
    assert.equal(number, index + 1, 'Missing or repeated historical attempt');
    assert.ok(jobs.jobs?.length > 0 && jobs.jobs.length < 100 && jobs.total_count === jobs.jobs.length, 'Incomplete attempt jobs');
    const matches = jobs.jobs.filter(j => j.name === 'sync');
    assert.equal(matches.length, 1, 'One original sync job required');
    const job = matches[0];
    assert.ok(validId(job.id) && job.run_id === run.id && job.head_sha === run.head_sha && job.run_attempt === number
      && job.status === 'completed' && job.check_run_url === `https://api.github.com/${prefix}/check-runs/${job.id}`, 'Unbound historical job');
    assert.ok(jobs.jobs.every(j => j === job || (j.status === 'completed' && j.conclusion === 'skipped')), 'A descendant executed; inspect its effects');
    assert.ok(Array.isArray(job.steps), 'Missing execution evidence');
    if (job.steps.length === 0) {
      assert.ok(job.conclusion === 'cancelled' && job.runner_id === 0 && job.runner_name === ''
        && job.labels?.includes('self-hosted') && annotations?.length > 0 && annotations.length < 100
        && annotations.some(a => a.annotation_level === 'failure' && a.message === unavailable), 'Unproven unacquired job');
      unacquired++;
    } else {
      assert.equal(job.conclusion, 'failure', 'Unknown historical execution');
      for (const [name, conclusion] of [['Guard provider write against workflow reruns','failure'],
        ['Wait for authoritative publication completion','skipped'], ['Sync skills to Supabase','skipped']]) {
        const steps = job.steps.filter(s => s.name === name);
        assert.ok(steps.length === 1 && steps[0].conclusion === conclusion, `Unproven missing provider stage: ${name}`);
      }
      for (const name of ['Upload provider-complete synced slugs artifact', 'Notify skillstore - Published submissions']) {
        assert.ok(job.steps.filter(s => s.name === name).every(s => s.conclusion === 'skipped'), 'A provider descendant executed');
      }
    }
  }
  assert.ok(unacquired > 0, 'This recovery requires an explicitly unacquired original attempt');
  return {publisherId:publisher.id, correlation};
}

// A new dispatch is a separate execution, not another attempt of the old run.
// Empty projections must never conceal an earlier recovery's unknown effects.
export function verifyNoOtherRecovery(run, currentId, read) {
  assert.ok(validId(currentId) && typeof run.created_at === 'string'
    && Number.isFinite(Date.parse(run.created_at)), 'Missing recovery identity/time');
  const runs = [];
  let total;
  for (let page = 1; ; page++) {
    assert.ok(page <= 10, 'Recovery inventory exceeds bounded proof');
    const inventory = read(`${prefix}/actions/workflows/sync-to-supabase.yml/runs?event=workflow_dispatch&created=${encodeURIComponent(`>=${run.created_at}`)}&per_page=100&page=${page}`);
    assert.ok(Number.isSafeInteger(inventory.total_count) && inventory.total_count >= 0
      && inventory.total_count <= 1000 && Array.isArray(inventory.workflow_runs) && inventory.workflow_runs.length <= 100);
    if (total === undefined) total = inventory.total_count;
    assert.equal(inventory.total_count, total, 'Recovery inventory changed during read');
    runs.push(...inventory.workflow_runs);
    if (inventory.workflow_runs.length < 100 || runs.length === total) break;
  }
  assert.equal(runs.length, total, 'Incomplete recovery inventory');
  assert.equal(new Set(runs.map(r => r.id)).size, total, 'Repeated recovery inventory entries');
  assert.ok(!runs.some(r => r.id !== currentId && r.display_title === `Recover provider sync ${run.id}`), 'Another recovery exists; inspect its effects before starting provider');
}

// The caller supplies its authenticated, bounded GitHub GET adapter. No writes.
export function loadUnstartedProviderRecovery(run, commit, read) {
  assert.ok(Number.isSafeInteger(run.run_attempt) && run.run_attempt >= 1 && run.run_attempt <= 8);
  const attempts = [];
  for (let number = 1; number <= run.run_attempt; number++) {
    const jobs = read(`${prefix}/actions/runs/${run.id}/attempts/${number}/jobs?per_page=100`);
    const sync = jobs.jobs?.filter(j => j.name === 'sync');
    assert.equal(sync?.length, 1);
    const annotations = sync[0].steps?.length === 0
      ? read(`${prefix}/check-runs/${sync[0].id}/annotations?per_page=100`) : undefined;
    attempts.push({number, jobs, ...(annotations ? {annotations} : {})});
  }
  const correlations = [...commit.message.matchAll(/^AgentCrew-Publication: (submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40}))$/gm)];
  assert.equal(correlations.length, 1);
  const digest = createHash('sha256').update(correlations[0][1]).digest('hex');
  const statuses = [];
  for (let page = 1; ; page++) {
    assert.ok(page <= 10, 'Publication status inventory exceeds bounded proof');
    const batch = read(`${prefix}/commits/${correlations[0][4]}/statuses?per_page=100&page=${page}`);
    assert.ok(Array.isArray(batch) && batch.length <= 100);
    statuses.push(...batch);
    if (batch.length < 100) break;
  }
  const owner = statuses.find(s => s.context === `agentcrew/publication/${digest}`);
  const match = owner?.target_url?.match(/^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/([1-9][0-9]*)$/);
  assert.ok(match, 'No exact publication reservation owner');
  const publisher = read(`${prefix}/actions/runs/${match[1]}`);
  const evidence = {run, commit, attempts, statuses, publisher};
  verifyUnstartedProviderRecovery(evidence);
  return evidence;
}
