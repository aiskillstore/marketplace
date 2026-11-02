import test from 'node:test';
import assert from 'node:assert/strict';
import { verifyBoundedRecoveryCoverage } from '../reconcile-submission-sync.mjs';

const expected = Array.from({ length: 79 }, (_, i) => `skill-${i}`);
const batches = () => [
  { runId: 10, slugs: expected.slice(0, 40) },
  { runId: 11, slugs: expected.slice(40) },
];

test('bounded recovery covers 79 skills through disjoint <=64 batches', () => {
  assert.deepEqual(verifyBoundedRecoveryCoverage(expected, batches()), [...expected].sort());
  assert.deepEqual(verifyBoundedRecoveryCoverage(expected, [
    { runId: 10, slugs: expected.slice(0, 64) }, { runId: 11, slugs: expected.slice(64) },
  ]), [...expected].sort());
});

test('reject duplicate or missing/extra evidence instead of deduplicating it', () => {
  for (const rows of [
    [batches()[0], batches()[0]],
    [{ runId: 10, slugs: expected.slice(0, 40) }, { runId: 10, slugs: expected.slice(40) }],
    [{ runId: 10, slugs: [...expected.slice(0, 40), expected[0]] }, batches()[1]],
    [{ runId: 10, slugs: expected.slice(0, 41) }, batches()[1]],
    [batches()[0]],
    [batches()[0], { runId: 11, slugs: [...expected.slice(40), 'extra'] }],
    [{ runId: 10, slugs: expected.slice(0, 65) }, { runId: 11, slugs: expected.slice(65) }],
    [...batches(), { runId: 12, slugs: [] }],
    [{ runId: '10', slugs: expected.slice(0, 40) }, batches()[1]],
  ]) assert.throws(() => verifyBoundedRecoveryCoverage(expected, rows));
  assert.throws(() => verifyBoundedRecoveryCoverage([...expected, expected[0]], batches()));
  assert.throws(() => verifyBoundedRecoveryCoverage(['../escape'], [{ runId: 10, slugs: ['../escape'] }]));
});
