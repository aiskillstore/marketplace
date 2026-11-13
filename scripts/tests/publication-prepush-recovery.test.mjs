import test from 'node:test';
import assert from 'node:assert/strict';
import { verifyPrepushFailure, reconcilePrepushReservations } from '../publication-prepush-recovery.mjs';
import { chooseAttempt, main, publicationIdentity } from '../continue-merged-publications.mjs';
import { readFileSync } from 'node:fs';

// Frozen historical run data, independent of the current workflow's Action pins.
const { before: beforeSteps, after: afterSteps } = JSON.parse(readFileSync(new URL('./fixtures/publication-prepush-job-steps.json', import.meta.url), 'utf8'));
const fixture = () => ({
  run: { id: 12, run_attempt: 1, event: 'workflow_dispatch', status: 'completed', conclusion: 'failure',
    path: '.github/workflows/publish-approved-batch.yml', head_branch: 'main', head_sha: '70175e06306db8eab43d3f63538b9553d73b8caa',
    head_repository: { full_name: 'aiskillstore/marketplace' }, display_title: `Publication batch ${'b'.repeat(64)}` },
  jobs: { total_count: 1, jobs: [{ id: 34, name: 'publish', conclusion: 'failure', steps: [
    ...beforeSteps.map(name => ({ name, conclusion: 'success' })),
    { name: 'Verify every approval and publish one atomic batch', conclusion: 'failure' },
    ...afterSteps.map(name => ({ name, conclusion: 'success' })),
  ] }] },
  receiverBlob: '409eab1ea2f03cc79bbc8a125a266a21055d6eb4',
  log: [
    '2026-11-06T17:27:38.105Z   PR_NUMBERS: 11,13',
    `2026-11-06T17:27:38.105Z   BATCH_ID: ${'b'.repeat(64)}`,
    '2026-11-06T17:28:35.189Z Main advanced; re-preflight required',
    '2026-11-06T17:28:35.199Z ##[error]Process completed with exit code 1.',
  ].join('\n'),
  prNumber: 11,
});

const digest = 'd'.repeat(64), merge = 'e'.repeat(40), attempt = '1793986072706-1';
const reservation = () => {
  const owner = 'https://github.com/aiskillstore/marketplace/actions/runs/12';
  const context = `agentcrew/publication/${digest}`;
  return {
    digest, merge, prNumber: 11,
    refs: [{ ref: `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${attempt}`, object: { type: 'commit', sha: merge } }],
    statuses: [context, `agentcrew/publication-attempt/${digest}/${attempt}`].flatMap(context => ['failure', 'pending'].map(state => ({
      id: `${context}-${state}`, context, state, target_url: owner,
      creator: { id: 254047988, login: 'ai-skill-store[bot]' },
    }))),
  };
};
function readers(value = fixture()) {
  return {
    request(path) {
      if (path === 'actions/runs/12') return structuredClone(value.run);
      if (path === 'actions/runs/12/attempts/1/jobs?per_page=100') return structuredClone(value.jobs);
      if (path === `contents/scripts/publish-approved-batch.mjs?ref=${value.run.head_sha}`) return { sha: value.receiverBlob };
      throw new Error(`Unexpected query ${path}`);
    },
    readJobLog: id => { assert.equal(id, 34); return value.log; },
  };
}

test('only proved pre-push reservations allow one fresh attempt; history is unmodified', () => {
  const input = reservation(), before = structuredClone(input);
  const result = reconcilePrepushReservations(input, readers());
  assert.deepEqual(input, before);
  assert.deepEqual(result.statuses, []);
  assert.deepEqual(result.prepushSafeRefs, input.refs.map(r => r.ref));
  assert.deepEqual(result.proofs, [{ runId: 12, jobId: 34, batchId: 'b'.repeat(64) }]);
  assert.ok(chooseAttempt({ ...input, ...result, now: 1793986072800 }).attempt);
  assert.ok(chooseAttempt({ ...input, now: 1793986072800 }).wait);
});

test('planner can dispatch only a verified no-push retry through the existing receiver', () => {
  const pr = { number: 11, changed_files: 1, created_at: '2026-11-05T00:00:00Z', merged_at: '2026-11-06T00:00:00Z',
    base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' },
    head: { ref: 'submission/test', sha: 'a'.repeat(40), repo: { full_name: 'aiskillstore/marketplace' } }, merge_commit_sha: merge };
  const actual = publicationIdentity(pr).digest;
  const value = reservation();
  for (const status of value.statuses) status.context = status.context.replace(digest, actual);
  value.refs[0].ref = value.refs[0].ref.replace(digest, actual);
  const io = readers(), writes = [];
  const request = (path, data) => {
    path = path.replace('repos/aiskillstore/marketplace/', '');
    if (data) { writes.push({ path, data }); return; }
    if (path === 'git/trees/main') return { tree: [{ path: 'pending', sha: 'tree' }] };
    if (path === 'git/trees/tree?recursive=1') return { tree: [{ path: 'owner/skill/skill-report.json', sha: 'report' }] };
    if (path.includes('actions/workflows/')) return { workflow_runs: [] };
    if (path.startsWith('pulls?')) return [pr];
    if (path === 'pulls/11') return pr;
    if (path.startsWith('pulls/11/files?')) return [{ filename: 'pending/owner/skill/skill-report.json', sha: 'report' }];
    if (path.startsWith('git/matching-refs/')) return value.refs;
    if (path.startsWith('commits/')) return value.statuses;
    return io.request(path);
  };
  process.argv.push('--apply');
  try {
    assert.equal(main(request, io.readJobLog).outcome, 'dispatched');
    assert.equal(writes.length, 1);
    assert.equal(writes[0].path, 'actions/workflows/publish-approved-batch.yml/dispatches');
    assert.equal(writes[0].data.inputs.pr_numbers, '11');
    value.statuses[0].state = 'success'; writes.length = 0;
    assert.equal(main(request, io.readJobLog).outcome, 'blocked');
    assert.equal(writes.length, 0);
  } finally { process.argv.pop(); }
});

test('receiver reconciles both before choosing attempt and after claiming its outbox', () => {
  const source = readFileSync(new URL('../publish-approved-batch.mjs', import.meta.url), 'utf8');
  assert.equal((source.match(/reconcilePrepushReservations\(/g) ?? []).length, 2);
});

test('never hides successful/unknown, foreign-writer, unbound or concurrent reservation evidence', () => {
  const mutations = [
    v => { v.statuses[0].state = 'success'; },
    v => { v.statuses[0].state = 'error'; },
    v => { v.statuses[0].creator.id = 123; },
    v => { v.statuses[0].target_url += '/attempts/1'; },
    v => { v.refs[0].object.sha = 'f'.repeat(40); },
    v => { v.refs = []; },
    v => { v.statuses = v.statuses.filter(s => !s.context.includes('/publication-attempt/')); },
    v => { v.statuses.unshift({ ...v.statuses[0], state: 'pending' }); },
    v => { v.statuses.push({ ...v.statuses[0], target_url: 'https://github.com/aiskillstore/marketplace/actions/runs/99' }); },
  ];
  for (const mutate of mutations) {
    const value = reservation(); mutate(value);
    assert.throws(() => reconcilePrepushReservations(value, readers()));
  }
});

test('recognizes only the pinned receiver failure before its sole push/callback path', () => {
  assert.deepEqual(verifyPrepushFailure(fixture()), { runId: 12, jobId: 34, batchId: 'b'.repeat(64) });
});

test('recognizes the separately audited recovery-enabled execution revision without changing history', () => {
  const value = fixture();
  value.run.head_sha = '9898ee93fc8e1da796c7b3ea7e9c582bae316f25';
  value.receiverBlob = '99e203b5bf8a47478db755e2845f2653bdbf6805';
  assert.deepEqual(verifyPrepushFailure(value), { runId: 12, jobId: 34, batchId: 'b'.repeat(64) });
  const input = reservation(), before = structuredClone(input);
  const result = reconcilePrepushReservations(input, readers(value));
  assert.deepEqual(input, before);
  assert.deepEqual(result.statuses, []);
  assert.deepEqual(result.prepushSafeRefs, input.refs.map(r => r.ref));
});

test('recognizes the separately audited 2026-11-12 pre-push execution without relaxing its proof', () => {
  const value = fixture();
  value.run.head_sha = '51965b79d69e82e99d7adf2602fca28be16788d5';
  value.receiverBlob = '99e203b5bf8a47478db755e2845f2653bdbf6805';
  assert.deepEqual(verifyPrepushFailure(value), { runId: 12, jobId: 34, batchId: 'b'.repeat(64) });
  const input = reservation(), before = structuredClone(input);
  const result = reconcilePrepushReservations(input, readers(value));
  assert.deepEqual(input, before);
  assert.deepEqual(result.statuses, []);
  assert.deepEqual(result.prepushSafeRefs, input.refs.map(r => r.ref));
  for (const mutate of [
    v => { v.run.head_sha = 'a'.repeat(40); },
    v => { v.receiverBlob = 'c'.repeat(40); },
    v => { v.run.run_attempt = 2; },
    v => { v.jobs.jobs[0].steps.unshift({ name: 'Unreviewed write', conclusion: 'success' }); },
    v => { v.log = v.log.replace('Main advanced; re-preflight required', 'Publication push outcome requires inspection'); },
  ]) {
    const invalid = structuredClone(value); mutate(invalid);
    assert.throws(() => verifyPrepushFailure(invalid));
  }
});

test('the newly audited receiver still rejects an unreviewed execution revision or invalid proof', () => {
  const mutations = [
    v => { v.run.head_sha = 'a'.repeat(40); },
    v => { v.receiverBlob = 'c'.repeat(40); },
    v => { v.run.run_attempt = 2; },
    v => { v.jobs.jobs[0].steps.unshift({ name: 'Unreviewed write', conclusion: 'success' }); },
    v => { v.log = v.log.replace('Main advanced; re-preflight required', 'Publication push outcome requires inspection'); },
  ];
  for (const mutate of mutations) {
    const value = fixture();
    value.run.head_sha = '9898ee93fc8e1da796c7b3ea7e9c582bae316f25';
    value.receiverBlob = '99e203b5bf8a47478db755e2845f2653bdbf6805';
    mutate(value);
    assert.throws(() => verifyPrepushFailure(value));
  }
});

test('rejects partial/unknown push outcomes and absent exact terminal failure', () => {
  for (const message of ['Publication push outcome requires inspection', 'socket closed', 'Main advanced; re-preflight required (untrusted)']) {
    const value = fixture(); value.log = value.log.replace('Main advanced; re-preflight required', message);
    assert.throws(() => verifyPrepushFailure(value));
  }
});

test('does not infer safe recovery from a rerun, missing jobs, untrusted source or another PR', () => {
  const mutations = [
    v => { v.run.run_attempt = 2; },
    v => { v.run.head_sha = 'a'.repeat(40); },
    v => { v.jobs.jobs[0].steps.unshift({ name: 'Unreviewed business write', conclusion: 'success' }); },
    v => { v.run.event = 'pull_request'; },
    v => { v.run.head_branch = 'submission/other'; },
    v => { v.run.head_repository.full_name = 'outsider/marketplace'; },
    v => { v.run.path = '.github/workflows/other.yml'; },
    v => { v.run.status = 'in_progress'; },
    v => { v.receiverBlob = 'c'.repeat(40); },
    v => { v.prNumber = 99; },
    v => { v.jobs.total_count = 2; },
    v => { v.jobs.jobs[0].steps[4].conclusion = 'success'; },
    v => { v.jobs.jobs[0].steps.shift(); },
    v => { v.log = v.log.replace('b'.repeat(64), 'c'.repeat(64)); },
  ];
  for (const mutate of mutations) { const value = fixture(); mutate(value); assert.throws(() => verifyPrepushFailure(value)); }
});
