import { test } from 'node:test';
import assert from 'node:assert/strict';
import { evaluateProviderRerun } from '../guard-provider-rerun.mjs';

function attempts(...conclusions) {
  return conclusions.map((conclusion, index) => ({
    attempt: index + 1,
    jobs: [{
      name: 'sync',
      steps: [{ name: 'Sync skills to Supabase', conclusion }],
    }],
  }));
}

test('first attempt may enter the provider step', () => {
  assert.deepEqual(evaluateProviderRerun({ currentAttempt: 1, previousAttempts: [] }), {
    allowed: true,
    reason: 'first-attempt',
  });
});

test('provider success followed by downstream failure blocks full-rerun provider replay', () => {
  assert.deepEqual(evaluateProviderRerun({
    currentAttempt: 2,
    previousAttempts: attempts('success'),
  }), {
    allowed: false,
    reason: 'attempt-1-provider-success',
  });
});

test('cancelled or failed provider evidence remains unknown and blocks replay', () => {
  for (const conclusion of ['cancelled', 'failure']) {
    assert.deepEqual(evaluateProviderRerun({
      currentAttempt: 2,
      previousAttempts: attempts(conclusion),
    }), {
      allowed: false,
      reason: `attempt-1-provider-${conclusion}`,
    });
  }
});

test('rerun may proceed only when every prior provider step was authoritatively skipped', () => {
  assert.deepEqual(evaluateProviderRerun({
    currentAttempt: 3,
    previousAttempts: attempts('skipped', 'skipped'),
  }), {
    allowed: true,
    reason: 'all-prior-provider-steps-skipped',
  });
});

test('missing or malformed prior-attempt evidence fails closed', () => {
  for (const previousAttempts of [
    [],
    [{ attempt: 1, jobs: [] }],
    [{ attempt: 1, jobs: [{ name: 'sync', steps: [] }] }],
    [{ attempt: 1, jobs: [{ name: 'sync', steps: [{ name: 'Sync skills to Supabase', conclusion: null }] }] }],
  ]) {
    assert.equal(evaluateProviderRerun({ currentAttempt: 2, previousAttempts }).allowed, false);
  }
});
