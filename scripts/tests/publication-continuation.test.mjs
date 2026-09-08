import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { parse } from 'yaml';
import { trustedMerged, publicationIdentity, chooseAttempt } from '../continue-merged-publications.mjs';

test('only authoritative merged submissions continue; unknown effects never auto-replay', () => {
  const pr = { number: 12, merged_at: '2026-09-08T00:00:00Z', base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' }, head: { repo: { full_name: 'aiskillstore/marketplace' }, ref: 'submission/test', sha: 'a'.repeat(40) }, merge_commit_sha: 'b'.repeat(40) };
  assert.ok(trustedMerged(pr));
  assert.equal(Boolean(trustedMerged({ ...pr, merged_at: null })), false);
  assert.equal(Boolean(trustedMerged({ ...pr, user: { id: 1 } })), false);
  const { digest, correlation } = publicationIdentity(pr);
  assert.equal(correlation, `submission-pr-12-${'a'.repeat(40)}-${'b'.repeat(40)}`);
  const input = { refs: [], statuses: [], digest, merge: pr.merge_commit_sha, now: 1788800000000 };
  assert.equal(chooseAttempt(input).attempt, '1788800000000-1');
  for (const state of ['pending', 'success', 'failure', 'error']) {
    assert.ok(chooseAttempt({ ...input, statuses: [{ context: `agentcrew/publication/${digest}`, state }] }).wait);
  }
  assert.ok(chooseAttempt({ ...input, statuses: [{ context: `agentcrew/publication-attempt/${digest}/1`, state: 'pending' }] }).wait);
  const ref = { ref: `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${input.now}-1`, object: { type: 'commit', sha: input.merge } };
  assert.ok(chooseAttempt({ ...input, refs: [ref] }).wait);
  assert.ok(chooseAttempt({ ...input, refs: [ref], now: input.now + 900001 }).attempt);
  assert.throws(() => chooseAttempt({ ...input, refs: [{ ...ref, object: { type: 'commit', sha: 'c'.repeat(40) } }] }));
  assert.ok(chooseAttempt({ ...input, refs: Array(8).fill(ref) }).wait);
});

test('merged-only continuation runs trusted main code and reuses the existing receiver', () => {
  const source = readFileSync('.github/workflows/continue-merged-publications.yml', 'utf8');
  const workflow = parse(source);
  assert.deepEqual(workflow.on.push.branches, ['main']);
  assert.ok(workflow.on.schedule.length);
  assert.equal(workflow.jobs.continue.steps[0].with.ref, 'main');
  assert.equal(workflow.jobs.continue.steps[0].with['persist-credentials'], false);
  const script = readFileSync('scripts/continue-merged-publications.mjs', 'utf8');
  assert.match(script, /on-pr-merge.yml\/dispatches/);
  assert.match(script, /syncRuns.some\(r => r.status !== 'completed'\)/);
  assert.doesNotMatch(script, /\/merge['`"]|update-branch|safe_to_publish|is_blocked|risk_level/);
});

test('sync baseline selection sorts workflow runs newest first', () => {
  const source = readFileSync('.github/workflows/sync-to-supabase.yml', 'utf8');
  assert.match(source, /sort_by\(\.created_at\) \| reverse\[\]/);
});

test('current pending inventory stops after its exact owners; fresh A prevents dispatching B', async () => {
  const { main } = await import('../continue-merged-publications.mjs');
  const makePr = (number, date, sha) => ({ number, merged_at: date, base: { ref: 'main' }, user: { id: 254047988, login: 'ai-skill-store[bot]' }, head: { repo: { full_name: 'aiskillstore/marketplace' }, ref: 'submission/test', sha: 'a'.repeat(40) }, merge_commit_sha: sha.repeat(40) });
  const a = makePr(1, '2026-09-01T00:00:00Z', 'b');
  const b = makePr(2, '2026-09-02T00:00:00Z', 'c');
  const { digest } = publicationIdentity(a);
  const calls = [];
  let syncRuns = [];
  const request = (endpoint, data) => {
    calls.push(endpoint);
    assert.equal(data, undefined, 'fresh earlier outbox must prevent every write');
    if (endpoint.endsWith('/git/trees/main')) return { tree: [{ path: 'pending', sha: 'tree' }] };
    if (endpoint.includes('/git/trees/tree?')) return { tree: [{ path: 'owner/a/skill-report.json', sha: 'ra' }, { path: 'owner/b/skill-report.json', sha: 'rb' }] };
    if (endpoint.includes('/pulls?')) {
      assert.ok(endpoint.endsWith('page=1'), 'do not scan 1000 old PRs after finding all current owners');
      return [b, a, ...Array(98).fill({ merged_at: null })];
    }
    if (endpoint.includes('/pulls/1/files')) return [{ filename: 'pending/owner/a/skill-report.json', sha: 'ra' }];
    if (endpoint.includes('/pulls/2/files')) return [{ filename: 'pending/owner/b/skill-report.json', sha: 'rb' }];
    if (endpoint.includes('/actions/workflows/')) return { workflow_runs: endpoint.includes('sync-to-supabase') ? syncRuns : [] };
    if (endpoint.endsWith('/pulls/1')) return a;
    if (endpoint.includes('/git/matching-refs/')) return [{ ref: `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${Date.now()}-1`, object: { type: 'commit', sha: a.merge_commit_sha } }];
    if (endpoint.includes('/statuses?')) return [];
    throw new Error(`Unexpected request: ${endpoint}`);
  };
  main(request);
  assert.ok(!calls.some(p => p.endsWith('/pulls/2')));
  syncRuns = [{ id: 12, event: 'push', status: 'completed', conclusion: 'failure', created_at: '2026-09-08T00:00:00Z' }];
  assert.throws(() => main(request), /Previous push sync 12 is failure/);
});
