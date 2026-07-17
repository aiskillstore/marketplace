import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  fetchApprovedCatalog,
  fetchScoreEvidence,
  finalizeClosure,
  parseRecoveryResult,
  parseScoreRunLog,
  verifyCacheReadback,
  verifyScoreTransitions,
} from '../score-cache-closure.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const RECOVERY = readFileSync(resolve(ROOT, '.github/workflows/recover-score-cache-closure.yml'), 'utf8');
const RECALCULATE = readFileSync(resolve(ROOT, '.github/workflows/recalculate-scores.yml'), 'utf8');
const INVALIDATE_ACTION = readFileSync(resolve(ROOT, '.github/actions/invalidate-cache/action.yml'), 'utf8');

test('strictly extracts unique terminal failures and reconciles the aggregate summary', () => {
  const parsed = parseScoreRunLog(`
::error::score ultimately failed for slug=beta after 1 attempts
::error::score ultimately failed for slug=alpha after 3 attempts
Processed: 5
Updated: 3
Errors: 2
`);
  assert.deepEqual(parsed, {
    errors: 2,
    failedSlugs: ['alpha', 'beta'],
    processed: 5,
    updated: 3,
  });
  assert.throws(() => parseScoreRunLog(`
::error::score ultimately failed for slug=alpha after 1 attempts
Processed: 5
Updated: 3
Errors: 2
`), /failure count mismatch/);
  assert.throws(() => parseScoreRunLog(`
::error::score ultimately failed for slug=alpha after 1 attempts
::error::score ultimately failed for slug=alpha after 1 attempts
Processed: 2
Updated: 0
Errors: 2
`), /repeats terminal failures/);
});

test('extracts only checksum-verified residual failures from a prior recovery result', () => {
  const metadata = {
    schemaVersion: 1,
    requestedCount: 5,
    successfulCount: 3,
    failedCount: 2,
    causallyProvenCount: 3,
  };
  assert.deepEqual(parseRecoveryResult({
    metadata,
    successfulText: 'charlie\nalpha\nbravo\n',
    failedText: 'echo\ndelta\n',
  }), {
    failedCount: 2,
    failedSlugs: ['delta', 'echo'],
    requestedCount: 5,
    successfulCount: 3,
  });
  assert.throws(() => parseRecoveryResult({
    metadata: { ...metadata, causallyProvenCount: 2 },
    successfulText: 'alpha\nbravo\ncharlie\n',
    failedText: 'delta\necho\n',
  }), /does not causally prove every success/);
  assert.throws(() => parseRecoveryResult({
    metadata,
    successfulText: 'alpha\nbravo\ndelta\n',
    failedText: 'delta\necho\n',
  }), /success\/failure overlap/);
});

test('approved catalog pagination selects only public eligible canonical slugs', async () => {
  const requests = [];
  const slugs = await fetchApprovedCatalog({
    supabaseUrl: 'https://db.example.test',
    serviceRoleKey: 'secret',
    fetchImpl: async (url, init) => {
      requests.push({ url: String(url), init });
      return new Response(JSON.stringify([{ slug: 'beta' }, { slug: 'alpha' }]), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });
    },
  });
  assert.deepEqual(slugs, ['alpha', 'beta']);
  assert.match(requests[0].url, /public_eligible=eq\.true/);
  assert.equal(requests[0].init.headers['Accept-Profile'], 'skillstore');
});

test('freezes exact current DB score and snapshot identity for every requested slug', async () => {
  const evidence = await fetchScoreEvidence({
    supabaseUrl: 'https://db.example.test',
    serviceRoleKey: 'secret',
    slugs: ['alpha'],
    requireSnapshot: true,
    fetchImpl: async () => new Response(JSON.stringify([{
      slug: 'alpha',
      quality_score: 88,
      quality_tier: 'silver',
      quality_score_calculated_at: '2026-07-15T12:00:00+00:00',
      current_quality_score_snapshot_id: '11111111-1111-4111-8111-111111111111',
    }]), { status: 200, headers: { 'content-type': 'application/json' } }),
  });
  assert.deepEqual(evidence, [{
    calculatedAt: '2026-07-15T12:00:00+00:00',
    qualityScore: 88,
    qualityTier: 'silver',
    slug: 'alpha',
    snapshotId: '11111111-1111-4111-8111-111111111111',
  }]);
});

test('rejects a claimed update that preserves an old snapshot and predates the trusted run boundary', () => {
  const unchanged = {
    calculatedAt: '2026-07-15T11:59:00+00:00',
    qualityScore: 88,
    qualityTier: 'silver',
    slug: 'alpha',
    snapshotId: '11111111-1111-4111-8111-111111111111',
  };
  assert.throws(() => verifyScoreTransitions({
    beforeScores: [unchanged],
    afterScores: [unchanged],
    runBoundary: '2026-07-15T12:00:00.000Z',
  }), /did not prove a causal score write/);
});

test('proves a score write by changed snapshot identity or an advanced post-boundary calculatedAt', () => {
  const before = {
    calculatedAt: '2026-07-15T11:59:00+00:00',
    qualityScore: 80,
    qualityTier: 'bronze',
    slug: 'alpha',
    snapshotId: '11111111-1111-4111-8111-111111111111',
  };
  const changedSnapshot = verifyScoreTransitions({
    beforeScores: [before],
    afterScores: [{ ...before, snapshotId: '22222222-2222-4222-8222-222222222222' }],
    runBoundary: '2026-07-15T12:00:00.000Z',
  });
  assert.equal(changedSnapshot.provenCount, 1);
  assert.equal(changedSnapshot.transitions[0].snapshotChanged, true);

  const refreshedInPlace = verifyScoreTransitions({
    beforeScores: [before],
    afterScores: [{ ...before, calculatedAt: '2026-07-15T12:00:00.000Z' }],
    runBoundary: '2026-07-15T12:00:00.000Z',
  });
  assert.equal(refreshedInPlace.transitions[0].calculatedAtAdvanced, true);
});

test('rejects an unchanged future timestamp caused by runner and database clock skew', () => {
  const unchangedFuture = {
    calculatedAt: '2026-07-15T12:00:05.000Z',
    qualityScore: 88,
    qualityTier: 'silver',
    slug: 'alpha',
    snapshotId: '11111111-1111-4111-8111-111111111111',
  };
  assert.throws(() => verifyScoreTransitions({
    beforeScores: [unchangedFuture],
    afterScores: [unchangedFuture],
    runBoundary: '2026-07-15T12:00:00.000Z',
  }), /did not prove a causal score write/);
});

function cachedResponse(slug, {
  build = 'build-a', cache, calculatedAt = '2026-07-15T12:00:00+00:00', key = `key-${slug}`,
  qualityScore = 88, qualityTier = 'silver', version = 'v5', write,
}) {
  return new Response(JSON.stringify({
    data: { slug, qualityScore, qualityTier, qualityBreakdown: { calculatedAt } },
  }), {
    status: 200,
    headers: {
      'content-type': 'application/json',
      'x-kv-cache': cache,
      'x-kv-key': key,
      'x-kv-version': version,
      'x-kv-write': write,
      'x-skillstore-build': build,
    },
  });
}

test('production readback requires a closed first read and a stable HIT+SKIPPED second read', async () => {
  const calls = new Map();
  const evidence = await verifyCacheReadback({
    expectedScores: ['alpha', 'beta'].map((slug) => ({
      slug,
      qualityScore: 88,
      qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00',
      snapshotId: '11111111-1111-4111-8111-111111111111',
    })),
    attempts: 1,
    concurrency: 2,
    expectedCacheVersion: 'v6',
    fetchImpl: async (url) => {
      const slug = String(url).split('/').at(-1);
      const count = (calls.get(slug) || 0) + 1;
      calls.set(slug, count);
      return cachedResponse(slug, count === 1
        ? { cache: 'MISS', version: 'v6', write: 'STORED' }
        : { cache: 'HIT', version: 'v6', write: 'SKIPPED' });
    },
  });
  assert.equal(evidence.failures.length, 0);
  assert.equal(evidence.slugCount, 2);
  assert.deepEqual(evidence.builds, ['build-a']);
  assert.deepEqual(Object.fromEntries(calls), { alpha: 2, beta: 2 });
});

test('readback retries a whole idempotent GET pass after a production build transition without mixing evidence', async () => {
  const builds = ['build-a', 'build-a', 'build-b', 'build-b', 'build-b', 'build-b', 'build-b', 'build-b'];
  let call = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: ['alpha', 'beta'].map((slug) => ({
      slug,
      qualityScore: 88,
      qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00',
      snapshotId: '11111111-1111-4111-8111-111111111111',
    })),
    attempts: 1,
    buildAttempts: 2,
    buildRetryDelayMs: 1,
    concurrency: 1,
    fetchImpl: async (url) => {
      const slug = String(url).split('/').at(-1);
      return cachedResponse(slug, {
        build: builds[call++],
        cache: 'HIT',
        version: 'v6',
        write: 'SKIPPED',
      });
    },
    sleepImpl: async () => {},
  });
  assert.equal(evidence.status, 'complete');
  assert.equal(evidence.acceptedBuild, 'build-b');
  assert.equal(evidence.buildAttemptCount, 2);
  assert.deepEqual(evidence.builds, ['build-b']);
  assert.ok(evidence.results.every((result) => (
    result.first.build === 'build-b' && result.second.build === 'build-b'
  )));
});

test('readback retries a single-slug pair on build change before comparing build-specific data', async () => {
  const reads = [
    { build: 'build-a', key: 'key-old', qualityScore: 87, version: 'v5' },
    { build: 'build-b', key: 'key-new', qualityScore: 88, version: 'v6' },
    { build: 'build-b', key: 'key-new', qualityScore: 88, version: 'v6' },
    { build: 'build-b', key: 'key-new', qualityScore: 88, version: 'v6' },
  ];
  let call = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    buildAttempts: 2,
    buildRetryDelayMs: 1,
    concurrency: 1,
    fetchImpl: async () => cachedResponse('alpha', {
      ...reads[call++], cache: 'HIT', write: 'SKIPPED',
    }),
    sleepImpl: async () => {},
  });
  assert.equal(evidence.status, 'complete');
  assert.equal(evidence.acceptedBuild, 'build-b');
  assert.equal(evidence.buildAttemptCount, 2);
  assert.equal(evidence.results.length, 1);
});

test('readback retries a deployment-invalid pass even when it also contains HTTP 500', async () => {
  const responses = [
    new Response('temporary', { status: 500 }),
    cachedResponse('beta', { build: 'build-a', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
    cachedResponse('beta', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
    cachedResponse('alpha', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
    cachedResponse('alpha', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
    cachedResponse('beta', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
    cachedResponse('beta', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' }),
  ];
  let call = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: ['alpha', 'beta'].map((slug) => ({
      slug,
      qualityScore: 88,
      qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00',
      snapshotId: '11111111-1111-4111-8111-111111111111',
    })),
    attempts: 1,
    buildAttempts: 2,
    buildRetryDelayMs: 1,
    concurrency: 1,
    fetchImpl: async () => responses[call++],
    sleepImpl: async () => {},
  });
  assert.equal(evidence.status, 'complete');
  assert.equal(evidence.acceptedBuild, 'build-b');
  assert.equal(evidence.buildAttemptCount, 2);
  assert.equal(evidence.results.length, 2);
  assert.equal(evidence.retryableReadFailures, 1);
});

test('readback returns an actionable non-destructive blocker when deployment never stabilizes', async () => {
  const builds = ['build-a', 'build-b', 'build-a', 'build-b'];
  let call = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    buildAttempts: 2,
    buildRetryDelayMs: 1,
    concurrency: 1,
    fetchImpl: async () => cachedResponse('alpha', {
      build: builds[call++], cache: 'HIT', version: 'v6', write: 'SKIPPED',
    }),
    sleepImpl: async () => {},
  });
  assert.equal(evidence.status, 'blocked_deployment_change');
  assert.equal(evidence.acceptedBuild, null);
  assert.equal(evidence.results.length, 0);
  assert.equal(evidence.buildAttemptCount, 2);
  assert.deepEqual(evidence.buildPasses.map((pass) => pass.failureCodes), [
    ['build_transition'],
    ['build_transition'],
  ]);
});

test('readback bounds transient HTTP 500 retries to idempotent GETs and keeps persistent 500 red', async () => {
  let transientCalls = 0;
  const recovered = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 2,
    buildAttempts: 1,
    concurrency: 1,
    fetchImpl: async (_url, init) => {
      assert.equal(init.method, 'GET');
      transientCalls += 1;
      if (transientCalls === 1) return new Response('temporary', { status: 500 });
      return cachedResponse('alpha', { build: 'build-b', cache: 'HIT', version: 'v6', write: 'SKIPPED' });
    },
    sleepImpl: async () => {},
  });
  assert.equal(recovered.status, 'complete');
  assert.equal(recovered.retryableReadFailures, 1);
  assert.equal(transientCalls, 3);

  let persistentCalls = 0;
  const failed = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 2,
    buildAttempts: 1,
    concurrency: 1,
    fetchImpl: async (_url, init) => {
      assert.equal(init.method, 'GET');
      persistentCalls += 1;
      return new Response('still broken', { status: 500 });
    },
    sleepImpl: async () => {},
  });
  assert.equal(failed.status, 'failed');
  assert.equal(failed.acceptedBuild, null);
  assert.equal(failed.results.length, 0);
  assert.equal(failed.failures[0].code, 'http_5xx');
  assert.equal(persistentCalls, 2);
});

test('readback rejects a stable cache generation that is not the required version', async () => {
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    concurrency: 1,
    expectedCacheVersion: 'v6',
    fetchImpl: async () => cachedResponse('alpha', {
      cache: 'HIT', version: 'v5', write: 'SKIPPED',
    }),
  });
  assert.equal(evidence.failures.length, 1);
  assert.match(evidence.failures[0].error, /cache version was v5\/v5; expected v6/);
});

test('readback records unstable cache identity as a failure', async () => {
  let count = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    concurrency: 1,
    fetchImpl: async () => {
      count += 1;
      return cachedResponse('alpha', count === 1
        ? { cache: 'MISS', write: 'STORED', version: 'v5' }
        : { cache: 'HIT', write: 'SKIPPED', version: 'v6' });
    },
  });
  assert.equal(evidence.failures.length, 1);
  assert.match(evidence.failures[0].error, /changed version/);
});

test('readback accepts a correct cache entry warmed after invalidation but before verification', async () => {
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    concurrency: 1,
    fetchImpl: async () => cachedResponse('alpha', { cache: 'HIT', write: 'SKIPPED' }),
  });
  assert.equal(evidence.failures.length, 0);
  assert.equal(evidence.results[0].first.cache, 'HIT');
});

test('readback rejects a stale HIT that disagrees with frozen DB score evidence', async () => {
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    concurrency: 1,
    fetchImpl: async () => cachedResponse('alpha', {
      cache: 'HIT', qualityScore: 87, write: 'SKIPPED',
    }),
  });
  assert.equal(evidence.failures.length, 1);
  assert.match(evidence.failures[0].error, /API score identity does not match frozen DB evidence/);
});

test('readback rejects a freshly stored cache body that disagrees with frozen DB score evidence', async () => {
  let count = 0;
  const evidence = await verifyCacheReadback({
    expectedScores: [{
      slug: 'alpha', qualityScore: 88, qualityTier: 'silver',
      calculatedAt: '2026-07-15T12:00:00+00:00', snapshotId: '11111111-1111-4111-8111-111111111111',
    }],
    attempts: 1,
    concurrency: 1,
    fetchImpl: async () => {
      count += 1;
      return cachedResponse('alpha', {
        cache: count === 1 ? 'MISS' : 'HIT',
        qualityScore: 87,
        write: count === 1 ? 'STORED' : 'SKIPPED',
      });
    },
  });
  assert.equal(evidence.failures.length, 1);
  assert.match(evidence.failures[0].error, /API score identity does not match frozen DB evidence/);
});

function completedReadback(slugCount = 2) {
  const slugs = Array.from({ length: slugCount }, (_, index) => `slug-${index + 1}`);
  return {
    acceptedBuild: 'build-b',
    buildAttemptCount: 1,
    buildPasses: [{ attempt: 1, builds: ['build-b'], failureCodes: [] }],
    builds: ['build-b'],
    failures: [],
    results: slugs.map((slug) => ({
      slug,
      first: { build: 'build-b' },
      second: { build: 'build-b' },
    })),
    retryableReadFailures: 0,
    schemaVersion: 1,
    slugCount,
    slugSha256: createHash('sha256').update(`${slugs.join('\n')}\n`).digest('hex'),
    status: 'complete',
  };
}

function completedClosureInput() {
  return {
    scope: 'source-run-failures',
    plannedSlugCount: 2,
    selectedSlugCount: 2,
    score: {
      schemaVersion: 1,
      requestedCount: 2,
      successfulCount: 2,
      failedCount: 0,
      causallyProvenCount: 2,
    },
    invalidation: {
      expectedCount: 2,
      totalCount: 2,
      successCount: 2,
      failedCount: 0,
      listVersionBumped: true,
    },
    readback: completedReadback(),
  };
}

test('finalizer closes score, invalidation, and one-build readback deterministically and reentrantly', () => {
  const input = completedClosureInput();
  const first = finalizeClosure(input);
  const second = finalizeClosure(structuredClone(input));
  assert.deepEqual(second, first);
  assert.equal(first.status, 'complete');
  assert.equal(first.score.status, 'complete');
  assert.equal(first.invalidation.status, 'complete');
  assert.equal(first.readback.status, 'complete');
  assert.equal(first.readback.acceptedBuild, 'build-b');
  assert.equal(first.finalizerStatus, 'complete');

  const approvedCatalog = finalizeClosure({
    ...input,
    scope: 'approved-catalog-cache',
    score: null,
    invalidation: {
      expectedCount: 1,
      totalCount: 1,
      successCount: 1,
      failedCount: 0,
      listVersionBumped: true,
    },
  });
  assert.equal(approvedCatalog.status, 'complete');
  assert.equal(approvedCatalog.score.status, 'not_required');
});

test('finalizer CLI can replay the same local evidence without production writes', () => {
  const directory = mkdtempSync(join(tmpdir(), 'score-cache-finalizer-'));
  try {
    const readbackPath = join(directory, 'readback.json');
    const scorePath = join(directory, 'score.json');
    const outputPath = join(directory, 'final.json');
    const replayPath = join(directory, 'final-replay.json');
    writeFileSync(readbackPath, JSON.stringify(completedReadback()));
    writeFileSync(scorePath, JSON.stringify(completedClosureInput().score));
    const args = [
      resolve(ROOT, 'scripts/score-cache-closure.mjs'),
      'finalize-closure',
      '--scope', 'source-run-failures',
      '--planned-slug-count', '2',
      '--selected-slug-count', '2',
      '--invalidation-expected-count', '2',
      '--invalidation-total-count', '2',
      '--invalidation-success-count', '2',
      '--invalidation-failed-count', '0',
      '--list-version-bumped', 'true',
      '--readback', readbackPath,
      '--score-metadata', scorePath,
    ];
    const first = spawnSync(process.execPath, [...args, '--output', outputPath], { encoding: 'utf8' });
    assert.equal(first.status, 0, first.stderr);
    const replay = spawnSync(process.execPath, [...args, '--output', replayPath], { encoding: 'utf8' });
    assert.equal(replay.status, 0, replay.stderr);
    assert.deepEqual(
      JSON.parse(readFileSync(replayPath, 'utf8')),
      JSON.parse(readFileSync(outputPath, 'utf8')),
    );
    assert.equal(JSON.parse(readFileSync(outputPath, 'utf8')).status, 'complete');
  } finally {
    rmSync(directory, { force: true, recursive: true });
  }
});

test('finalizer keeps score, invalidation, HTTP failure, and deployment transition distinct and fail-closed', () => {
  const scoreFailed = finalizeClosure({
    ...completedClosureInput(),
    selectedSlugCount: 1,
    score: {
      schemaVersion: 1,
      requestedCount: 2,
      successfulCount: 1,
      failedCount: 1,
      causallyProvenCount: 1,
    },
    readback: completedReadback(1),
  });
  assert.equal(scoreFailed.status, 'failed');
  assert.equal(scoreFailed.score.status, 'failed');

  const invalidationFailed = finalizeClosure({
    ...completedClosureInput(),
    invalidation: {
      expectedCount: 2,
      totalCount: 2,
      successCount: 1,
      failedCount: 1,
      listVersionBumped: true,
    },
  });
  assert.equal(invalidationFailed.status, 'failed');
  assert.equal(invalidationFailed.invalidation.status, 'failed');

  const httpFailed = finalizeClosure({
    ...completedClosureInput(),
    readback: {
      ...completedReadback(),
      acceptedBuild: null,
      builds: [],
      failures: [{ slug: 'slug-1', code: 'http_5xx', error: 'HTTP 500' }],
      results: [],
      status: 'failed',
    },
  });
  assert.equal(httpFailed.status, 'failed');
  assert.equal(httpFailed.readback.status, 'failed');

  const deploymentBlocked = finalizeClosure({
    ...completedClosureInput(),
    readback: {
      ...completedReadback(),
      acceptedBuild: null,
      buildPasses: [{ attempt: 1, builds: [], failureCodes: ['build_transition'] }],
      builds: [],
      failures: [{ slug: '*', code: 'build_transition', error: 'deployment changed' }],
      results: [],
      status: 'blocked_deployment_change',
    },
  });
  assert.equal(deploymentBlocked.status, 'blocked_deployment_change');
  assert.equal(deploymentBlocked.score.status, 'complete');
  assert.equal(deploymentBlocked.invalidation.status, 'complete');
  assert.equal(deploymentBlocked.readback.status, 'blocked_deployment_change');

  const mixedBuildClaim = finalizeClosure({
    ...completedClosureInput(),
    readback: {
      ...completedReadback(),
      acceptedBuild: 'build-b',
      builds: ['build-a', 'build-b'],
    },
  });
  assert.equal(mixedBuildClaim.status, 'failed');
  assert.equal(mixedBuildClaim.readback.status, 'failed');
});

test('daily workflow moves score cache closure to a fail-closed hosted job', () => {
  assert.match(RECALCULATE, /cache-closure:[\s\S]*runs-on: ubuntu-latest/);
  assert.match(RECALCULATE, /actions\/upload-artifact@v4[\s\S]*score-closure-\$\{\{ github\.run_id \}\}/);
  assert.match(RECALCULATE, /actions\/download-artifact@v5[\s\S]*score-closure-\$\{\{ github\.run_id \}\}/);
  assert.match(RECALCULATE, /Verify every production API cache readback/);
  assert.match(RECALCULATE, /freeze-score-evidence/);
  assert.match(RECALCULATE, /--expected-score-evidence/);
  assert.match(RECALCULATE, /^concurrency:\n(?:.*\n){0,5}\s+group: production-skill-score-writes/m);
  assert.doesNotMatch(RECALCULATE, /\|\| echo "::warning::Batch cache invalidation failed/);
});

test('manual recovery is file-backed, fixed-CLI, bounded, and red on any remaining failure', () => {
  assert.match(RECOVERY, /source_run_id:/);
  assert.match(RECOVERY, /gh run view "\$SOURCE_RUN_ID"[\s\S]*--log > "\$plan\/source-run\.log"/);
  assert.match(RECOVERY, /extract-run-log/);
  assert.match(RECOVERY, /recovery-run-failures/);
  assert.match(RECOVERY, /\.conclusion == "failure" or \.conclusion == "cancelled"/);
  assert.match(RECOVERY, /score-cache-recovery-result-\$SOURCE_RUN_ID/);
  assert.match(RECOVERY, /sha256sum --check SHA256SUMS/);
  assert.match(RECOVERY, /extract-recovery-result/);
  assert.match(RECOVERY, /source-result-metadata\.json/);
  assert.match(RECOVERY, /compare\/\$source_sha\.\.\.\$GITHUB_SHA/);
  assert.match(RECOVERY, /source run commit is not an ancestor/);
  assert.match(RECOVERY, /approved-catalog/);
  assert.match(RECOVERY, /name: score-cache-recovery-plan-\$\{\{ github\.run_id \}\}/);
  assert.match(RECOVERY, /RECOVERY_CLI_VERSION: '2\.8\.1'/);
  assert.match(RECOVERY, /RECOVERY_CLI_SHA256: '0c53207352b1fe1c5bc73c9d544ee7d97067ed55ab6b72f00e5624b7ee0c7c5c'/);
  assert.match(RECOVERY, /RECOVERY_CLI_SHA256: '[0-9a-f]{64}'/);
  assert.match(RECOVERY, /runs-on: ubuntu-latest/);
  assert.match(RECOVERY, /group: production-skill-score-writes/);
  assert.match(RECOVERY, /--concurrency "\$\{\{ inputs\.score_concurrency \}\}"/);
  assert.match(RECOVERY, /Invalidate selected score API entries/);
  assert.match(RECOVERY, /awk 'NF \{ print; exit \}' "\$target" > "\$invalidation_target"/);
  assert.match(RECOVERY, /slugs-file: \$\{\{ runner\.temp \}\}\/cache-invalidation-slugs\.txt/);
  assert.match(RECOVERY, /EXPECTED: \$\{\{ steps\.selected\.outputs\.invalidation_count \}\}/);
  assert.match(RECOVERY, /test "\$LIST_VERSION_BUMPED" = true/);
  assert.match(RECOVERY, /invalidationCount: \(\.invalidation\.expectedCount \| tostring\)/);
  assert.match(RECOVERY, /listVersionBumped: \(\.invalidation\.listVersionBumped \| tostring\)/);
  assert.match(RECOVERY, /List-generation invalidation slugs:/);
  assert.match(RECOVERY, /batch-size: '30'\n\s+concurrency: \$\{\{ needs\.plan\.outputs\.scope == 'approved-catalog-cache' && '4' \|\| '1' \}\}/);
  assert.match(RECOVERY, /--expected-cache-version v6/);
  assert.match(RECOVERY, /--concurrency 16/);
  assert.match(RECOVERY, /--build-attempts 3/);
  assert.match(RECOVERY, /--build-retry-delay-ms 15000/);
  assert.match(RECOVERY, /name: Finalize score and cache closure state\n\s+id: finalizer\n\s+if: always\(\)/);
  assert.match(RECOVERY, /score-cache-closure\.mjs finalize-closure/);
  assert.match(RECOVERY, /--readback "\$RUNNER_TEMP\/cache-readback\.json"/);
  assert.match(RECOVERY, /--output "\$evidence\/final-summary\.json"/);
  assert.match(RECOVERY, /blocked_deployment_change/);
  assert.match(RECOVERY, /\.finalizerStatus == "complete"/);
  assert.match(RECOVERY, /Require complete score and cache recovery/);
  assert.match(RECOVERY, /freeze-score-evidence/);
  assert.match(RECOVERY, /before-score-evidence\.json/);
  assert.match(RECOVERY, /verify-score-transitions/);
  assert.match(RECOVERY, /causallyProvenCount/);
  assert.match(RECOVERY, /test "\$proven_count" -eq "\$successful_count"/);
  assert.match(RECOVERY, /--expected-score-evidence/);
  assert.match(RECOVERY, /score_args\+=\(--score-metadata "\$score_metadata"\)/);
  assert.match(RECOVERY, /remainingScoreFailures: \(\(\.score\.failedCount \/\/ 0\) \| tostring\)/);
  assert.doesNotMatch(RECOVERY, /workflow run|repository_dispatch/);
});

test('every single-file score closure sparse checkout disables cone mode', () => {
  for (const [name, workflow] of [
    ['recalculate', RECALCULATE],
    ['recovery', RECOVERY],
  ]) {
    const checkoutBlocks = [...workflow.matchAll(
      /uses: actions\/checkout@v5\n\s{8}with:\n((?:\s{10,}[^\n]*\n)*)/g,
    )]
      .map((match) => match[1])
      .filter((block) => block.includes('scripts/score-cache-closure.mjs'));
    assert.ok(checkoutBlocks.length > 0, `${name} must checkout the score closure runtime`);
    for (const block of checkoutBlocks) {
      assert.match(block, /sparse-checkout-cone-mode:\s*false/,
        `${name} single-file sparse checkout must disable cone mode`);
    }
  }
});

test('shared invalidation action preserves score-only closure flags and validates response identity', () => {
  assert.match(INVALIDATE_ACTION, /invalidate-artifacts:/);
  assert.match(INVALIDATE_ACTION, /invalidate-dependent-packs:/);
  assert.match(INVALIDATE_ACTION, /invalidateArtifacts: \$invalidateArtifacts/);
  assert.match(INVALIDATE_ACTION, /invalidateDependentPacks: \$invalidateDependentPacks/);
  assert.match(INVALIDATE_ACTION, /Cache invalidation response violated the requested closure contract/);
  assert.match(INVALIDATE_ACTION, /\.invalidated\.listVersionBumped == true/);
  assert.match(INVALIDATE_ACTION, /list_version_bumped=true/);
  assert.match(INVALIDATE_ACTION, /--max-time 90/);
  assert.match(INVALIDATE_ACTION, /local max_attempts=4/);
  assert.match(INVALIDATE_ACTION, /concurrency:[\s\S]*default: '1'/);
  assert.match(INVALIDATE_ACTION, /concurrency must be an integer between 1 and 4/);
  assert.match(INVALIDATE_ACTION, /wave_start\+=BATCH_CONCURRENCY/);
  assert.match(INVALIDATE_ACTION, /worker exited without complete evidence/);
  assert.match(INVALIDATE_ACTION, /produced inconsistent completion evidence/);
  assert.match(INVALIDATE_ACTION, /for \(\(BATCH_NUM=1; BATCH_NUM<=BATCHES; BATCH_NUM\+\+\)\)/);
  assert.match(INVALIDATE_ACTION, /workers did not produce trustworthy completion evidence/);

  const runBlock = INVALIDATE_ACTION.match(/\n      run: \|\n([\s\S]+)$/);
  assert.ok(runBlock, 'composite action must contain its Bash run block');
  const shell = runBlock[1]
    .split('\n')
    .map((line) => line.startsWith('        ') ? line.slice(8) : line)
    .join('\n');
  const syntax = spawnSync('bash', ['-n'], { encoding: 'utf8', input: shell });
  assert.equal(syntax.status, 0, syntax.stderr);
});
