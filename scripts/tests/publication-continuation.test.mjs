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
