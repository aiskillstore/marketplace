import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';

export const readPublicationJobLog = id => execFileSync('gh', ['api', `repos/aiskillstore/marketplace/actions/jobs/${id}/logs`],
  { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024, timeout: 60000 });

// Pin the WHOLE audited execution revision (workflow, checkout, imports and
// receiver), not just an error string or one script. At this revision the
// exact terminal error below precedes the sole push/callback/provider path.
// Other revisions/outcomes stay blocked, even with an unchanged receiver blob.
const auditedReceiverRevisions = new Map([
  ['70175e06306db8eab43d3f63538b9553d73b8caa', '409eab1ea2f03cc79bbc8a125a266a21055d6eb4'],
]);
const repo = 'aiskillstore/marketplace';
export function verifyPrepushFailure({ run, jobs, receiverBlob, log, prNumber }) {
  assert.ok(Number.isSafeInteger(run.id) && run.id > 0 && run.run_attempt === 1, 'Unverified prior attempts');
  assert.ok(run.event === 'workflow_dispatch' && run.status === 'completed' && run.conclusion === 'failure'
    && run.path === '.github/workflows/publish-approved-batch.yml' && run.head_branch === 'main'
    && run.head_repository?.full_name === repo && /^[a-f0-9]{40}$/.test(run.head_sha), 'Untrusted receiver run');
  assert.equal(auditedReceiverRevisions.get(run.head_sha), receiverBlob, 'Unaudited execution revision');
  assert.ok(auditedReceiverRevisions.has(run.head_sha), 'Unaudited execution revision');
  const batchId = /^Publication batch ([a-f0-9]{64})$/.exec(run.display_title ?? '')?.[1];
  assert.ok(batchId, 'Unbound publication batch');
  assert.ok(jobs.total_count === 1 && jobs.jobs?.length === 1, 'Incomplete receiver job inventory');
  const job = jobs.jobs[0];
  assert.ok(job.name === 'publish' && job.conclusion === 'failure' && Number.isSafeInteger(job.id), 'Untrusted receiver job');
  const before = ['Set up job', 'Run actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510',
    'Run actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09', 'Run actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444'];
  const after = ['Post Run actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444',
    'Post Run actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09',
    'Post Run actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510', 'Complete job'];
  assert.deepEqual(job.steps.map(s => s.name), [...before, 'Verify every approval and publish one atomic batch', ...after], 'Unreviewed execution steps');
  assert.ok(job.steps.slice(0, before.length).every(s => s.conclusion === 'success'), 'Unverified checkout/setup');
  const step = job.steps.filter(s => s.name === 'Verify every approval and publish one atomic batch');
  assert.ok(step.length === 1 && step[0].conclusion === 'failure', 'Unverified failed publication step');
  const lines = log.split(/\r?\n/).map(line => line.replace(/^\d{4}-\d\d-\d\dT[\d:.]+Z /, ''));
  const numbers = lines.filter(line => /^  PR_NUMBERS: /.test(line));
  assert.equal(numbers.length, 1, 'Ambiguous publication inputs');
  const input = numbers[0].slice('  PR_NUMBERS: '.length).split(',');
  assert.ok(input.length > 0 && input.length <= 25 && input.every(n => /^[1-9][0-9]*$/.test(n))
    && new Set(input).size === input.length && input.includes(String(prNumber)), 'Unbound PR input');
  assert.deepEqual(lines.filter(line => /^  BATCH_ID: /.test(line)), [`  BATCH_ID: ${batchId}`], 'Batch input mismatch');
  const failure = lines.indexOf('Main advanced; re-preflight required');
  assert.ok(failure >= 0 && lines.lastIndexOf('Main advanced; re-preflight required') === failure
    && lines[failure + 1] === '##[error]Process completed with exit code 1.', 'No exact terminal pre-push failure');
  return { runId: run.id, jobId: job.id, batchId };
}

// Read-only reconciliation: keep the durable history, but exclude only the
// exact reservations independently proved to have aborted before push. Both
// the planner and receiver use this function, including the post-claim check.
export function reconcilePrepushReservations({ statuses, refs, digest, merge, prNumber }, { request, readJobLog }) {
  const context = `agentcrew/publication/${digest}`;
  const attemptPrefix = `agentcrew/publication-attempt/${digest}/`;
  const relevant = statuses.filter(s => s.context === context || s.context.startsWith(attemptPrefix));
  if (!relevant.length) return { statuses, prepushSafeRefs: [], proofs: [] };
  const runs = new Map();
  for (const status of relevant) {
    assert.ok(['pending', 'failure'].includes(status.state) && status.creator?.id === 254047988
      && status.creator.login === 'ai-skill-store[bot]', 'Reservation is not a trusted no-push failure');
    const id = /^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/([1-9][0-9]*)$/.exec(status.target_url ?? '')?.[1];
    assert.ok(id, 'Unbound receiver reservation');
    if (!runs.has(id)) runs.set(id, []);
    runs.get(id).push(status);
  }
  const prepushSafeRefs = [], proofs = [];
  for (const [id, history] of runs) {
    const contexts = [...new Set(history.map(s => s.context))];
    const attemptContexts = contexts.filter(c => c.startsWith(attemptPrefix));
    assert.ok(contexts.includes(context) && attemptContexts.length === 1 && contexts.length === 2, 'Incomplete attempt reservation history');
    for (const c of contexts) assert.equal(history.find(s => s.context === c).state, 'failure', 'Receiver still active');
    const attempt = attemptContexts[0].slice(attemptPrefix.length);
    assert.match(attempt, /^\d{13}-[1-9]\d*$/);
    const refName = `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${attempt}`;
    const matched = refs.filter(r => r.ref === refName);
    assert.ok(matched.length === 1 && matched[0].object.type === 'commit' && matched[0].object.sha === merge, 'Missing exact failed outbox');
    const run = request(`actions/runs/${id}`);
    assert.equal(String(run.id), id, 'Run identity mismatch');
    const jobs = request(`actions/runs/${id}/attempts/1/jobs?per_page=100`);
    assert.ok(jobs.jobs?.length === 1, 'Unbound job logs');
    const receiver = request(`contents/scripts/publish-approved-batch.mjs?ref=${run.head_sha}`);
    const log = readJobLog(jobs.jobs[0].id);
    proofs.push(verifyPrepushFailure({ run, jobs, receiverBlob: receiver.sha, log, prNumber }));
    prepushSafeRefs.push(refName);
  }
  return { statuses: statuses.filter(s => !relevant.includes(s)), prepushSafeRefs, proofs };
}
