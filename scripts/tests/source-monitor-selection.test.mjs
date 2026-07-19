import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  parseRequestedSlugs,
  parseResultSlugs,
  verifyExactSelection,
  verifyLocalActionSummary,
} from '../verify-source-monitor-selection.mjs';

const EXPECTED_COMMIT = '458df4c41294655f76e551100a9b634114209bb9';

function jsonl(...slugs) {
  return `${slugs.map((slug) => JSON.stringify({
    slug,
    scan_status: 'updated',
    upstream_commit_sha: EXPECTED_COMMIT,
  })).join('\n')}\n`;
}

test('accepts an exact explicit source monitor result set independent of order', () => {
  assert.deepEqual(parseRequestedSlugs('owner-two, owner-one'), ['owner-one', 'owner-two']);
  assert.deepEqual(parseResultSlugs(jsonl('owner-two', 'owner-one')), ['owner-one', 'owner-two']);
  assert.deepEqual(verifyExactSelection('owner-two,owner-one', jsonl('owner-one', 'owner-two')), {
    requested: 2,
    results: 2,
    expectedUpstreamCommit: null,
  });
  assert.deepEqual(
    verifyExactSelection('owner-one', jsonl('owner-one'), EXPECTED_COMMIT),
    { requested: 1, results: 1, expectedUpstreamCommit: EXPECTED_COMMIT },
  );
});

test('requires every explicit result to match the expected immutable upstream commit', () => {
  const drifted = `${JSON.stringify({
    slug: 'owner-one',
    scan_status: 'updated',
    upstream_commit_sha: '1111111111111111111111111111111111111111',
  })}\n`;
  assert.throws(
    () => verifyExactSelection('owner-one', drifted, EXPECTED_COMMIT),
    /upstream commit mismatch/,
  );
  assert.throws(
    () => verifyExactSelection('owner-one', jsonl('owner-one'), 'main'),
    /invalid expected upstream commit/,
  );
  const wrongStatus = `${JSON.stringify({
    slug: 'owner-one',
    scan_status: 'error',
    upstream_commit_sha: EXPECTED_COMMIT,
  })}\n`;
  assert.throws(
    () => verifyExactSelection('owner-one', wrongStatus, EXPECTED_COMMIT),
    /update status mismatch/,
  );
});

test('requires exact successful local action accounting for every requested update', () => {
  const valid = [
    '| Observed updated skills | 2 |',
    '| Selected updated skills for this run | 2 |',
    '| Applied updated skills | 2 |',
    '| Failed selected updates | 0 |',
    '| Deferred updated skills | 0 |',
  ].join('\n');
  assert.deepEqual(verifyLocalActionSummary(valid, 2), {
    observed: 2,
    selected: 2,
    applied: 2,
    failed: 0,
    deferred: 0,
  });
  assert.throws(
    () => verifyLocalActionSummary(valid.replace('Applied updated skills | 2', 'Applied updated skills | 1'), 2),
    /local action mismatch/,
  );
});

test('rejects zero matches, partial matches, unexpected results, and duplicates', () => {
  assert.throws(() => verifyExactSelection('owner-one', ''), /missing=\[owner-one\]/);
  assert.throws(
    () => verifyExactSelection('owner-one,owner-two', jsonl('owner-one')),
    /missing=\[owner-two\]/,
  );
  assert.throws(
    () => verifyExactSelection('owner-one', jsonl('owner-one', 'owner-two')),
    /unexpected=\[owner-two\]/,
  );
  assert.throws(() => parseRequestedSlugs('owner-one owner-one'), /duplicate requested/);
  assert.throws(() => parseResultSlugs(jsonl('owner-one', 'owner-one')), /duplicate source monitor result/);
});

test('rejects malformed requested slugs and malformed JSONL records', () => {
  assert.throws(() => parseRequestedSlugs('owner/one'), /invalid requested/);
  assert.throws(() => parseResultSlugs('{not-json}\n'), /invalid source monitor JSONL/);
  assert.throws(() => parseResultSlugs('{"scan_status":"updated"}\n'), /invalid result skill slug/);
});
