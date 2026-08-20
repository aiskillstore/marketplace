import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const scripts = new URL('.', import.meta.url);

function run(script, ...args) {
  return spawnSync(process.execPath, [fileURLToPath(new URL(script, scripts)), ...args], { encoding: 'utf8' });
}

test('rejects unknown and duplicate options before doing work', () => {
  const unknown = run('daily-upcoming.mjs', '--bogus', 'value');
  assert.equal(unknown.status, 1);
  assert.match(unknown.stderr, /Unknown option: --bogus/);

  const duplicate = run('poll-new-events.mjs', '--limit', '20', '--limit', '30');
  assert.equal(duplicate.status, 1);
  assert.match(duplicate.stderr, /Duplicate option: --limit/);
});

test('validates numeric ranges before loading state or calling the API', () => {
  for (const [script, args, error] of [
    ['daily-upcoming.mjs', ['--limit', '0'], /--limit must be between 1 and 100/],
    ['daily-upcoming.mjs', ['--hours', '8785'], /--hours must be between 1 and 8784/],
    ['poll-new-events.mjs', ['--limit', 'many'], /--limit must be an integer/],
  ]) {
    const result = run(script, ...args);
    assert.equal(result.status, 1);
    assert.match(result.stderr, error);
  }
});

test('validates calendar dates and date-range combinations', () => {
  for (const [args, error] of [
    [['--start-date', '2026-02-30', '--end-date', '2026-03-01'], /valid calendar date/],
    [['--start-date', '2026-08-01'], /must be provided together/],
    [['--start-date', '2026-08-02', '--end-date', '2026-08-01'], /must not be earlier/],
    [['--start-date', '2026-01-01', '--end-date', '2027-01-02'], /must not exceed 366 days/],
    [['--hours', '24', '--start-date', '2026-08-01', '--end-date', '2026-08-02'], /cannot be combined/],
  ]) {
    const result = run('daily-upcoming.mjs', ...args);
    assert.equal(result.status, 1);
    assert.match(result.stderr, error);
  }
});

test('validates IANA time zones before calling the API', () => {
  const result = run('init-subscription.mjs', '--timezone', 'Shanghai time');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /valid IANA time zone/);
});
