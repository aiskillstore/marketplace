import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';

import {
  parseRequestedSlugs,
  parseResultSlugs,
  verifyExactSelection,
  verifyLocalActionSummary,
  verifyLocalMutations,
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

test('requires exact applied-or-failed local action accounting for every requested update', () => {
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
  assert.deepEqual(verifyLocalActionSummary([
    '| Observed updated skills | 2 |',
    '| Selected updated skills for this run | 2 |',
    '| Applied updated skills | 1 |',
    '| Failed selected updates | 1 |',
    '| Deferred updated skills | 0 |',
  ].join('\n'), 2), {
    observed: 2,
    selected: 2,
    applied: 1,
    failed: 1,
    deferred: 0,
  });
});

test('accepts a fully accounted invalid candidate with no marketplace mutations', () => {
  const root = mkdtempSync(join(tmpdir(), 'source-monitor-selection-'));
  try {
    const directory = join(root, 'skills', 'owner', 'broken');
    mkdirSync(directory, { recursive: true });
    writeFileSync(join(directory, 'SKILL.md'), '---\nname: broken\ndescription: old\n---\n');
    writeFileSync(join(directory, 'skill-report.json'), JSON.stringify({
      meta: { slug: 'broken', upstream_commit_sha: null },
    }));
    execFileSync('git', ['init', '-q'], { cwd: root });
    execFileSync('git', ['config', 'user.name', 'Fixture'], { cwd: root });
    execFileSync('git', ['config', 'user.email', 'fixture@example.com'], { cwd: root });
    execFileSync('git', ['add', '.'], { cwd: root });
    execFileSync('git', ['commit', '-qm', 'fixture'], { cwd: root });

    const summary = [
      '| Observed updated skills | 1 |',
      '| Selected updated skills for this run | 1 |',
      '| Applied updated skills | 0 |',
      '| Failed selected updates | 1 |',
      '| Deferred updated skills | 0 |',
      '',
      '### Local Action Failures',
      '',
      '- broken: invalid upstream SKILL.md',
    ].join('\n');
    assert.deepEqual(verifyLocalMutations({
      repositoryRoot: root,
      requested: 'broken',
      expectedUpstreamCommit: EXPECTED_COMMIT,
      summaryText: summary,
    }), {
      observed: 1,
      selected: 1,
      applied: 0,
      failed: 1,
      deferred: 0,
      changedPaths: 0,
      authorizedDirectories: 0,
    });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
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
