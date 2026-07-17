import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { test } from 'node:test';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import * as closure from '../score-cache-closure.mjs';

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

const BUILD_A = `${'a'.repeat(40)}.deploy-a`;
const BUILD_B = `${'b'.repeat(40)}.deploy-b`;

function cachedResponse(slug, {
  build = BUILD_A, cache, calculatedAt = '2026-07-15T12:00:00+00:00', key = `key-${slug}`,
  qualityScore = 88, qualityTier = 'silver', version = 'v6', write,
} = {}) {
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

function versionResponse(build = BUILD_A, bodyBuild = build, headers = {}) {
  return new Response(JSON.stringify({ version: bodyBuild }), {
    status: 200,
    headers: {
      'content-type': 'application/json',
      'x-skillstore-build': build,
      ...headers,
    },
  });
}

function expectedScores(slugs = ['alpha']) {
  return slugs.map((slug) => ({
    slug,
    qualityScore: 88,
    qualityTier: 'silver',
    calculatedAt: '2026-07-15T12:00:00+00:00',
    snapshotId: '11111111-1111-4111-8111-111111111111',
  }));
}

function scriptedFetch(responses, calls = []) {
  return async (url, init) => {
    calls.push({ url: String(url), init });
    assert.ok(responses.length > 0, `unexpected request ${url}`);
    const next = responses.shift();
    return typeof next === 'function' ? next(url, init) : next;
  };
}

function stableReadPair(slug = 'alpha', build = BUILD_A) {
  return [
    cachedResponse(slug, { build, cache: 'MISS', write: 'STORED' }),
    cachedResponse(slug, { build, cache: 'HIT', write: 'SKIPPED' }),
  ];
}

test('production readback brackets pinned detail GETs with exact no-cache build probes', async () => {
  const calls = [];
  const evidence = await verifyCacheReadback({
    expectedScores: expectedScores(),
    attempts: 1,
    buildAttempts: 1,
    concurrency: 1,
    fetchImpl: scriptedFetch([
      versionResponse(),
      ...stableReadPair(),
      versionResponse(),
    ], calls),
  });
  assert.equal(evidence.status, 'complete');
  assert.equal(evidence.acceptedBuild, BUILD_A);
  assert.deepEqual(calls.map((call) => new URL(call.url).pathname), [
    '/_app/version.json', '/api/skills/alpha', '/api/skills/alpha', '/_app/version.json',
  ]);
  assert.equal(calls[0].init.headers['Cache-Control'], 'no-cache');
  assert.equal(calls[3].init.headers['Cache-Control'], 'no-cache');
  for (const detail of calls.slice(1, 3)) {
    assert.equal(new URL(detail.url).searchParams.get('__skillstore_build'), BUILD_A);
  }
  assert.equal(evidence.results[0].first.score.qualityScore, 88);
  assert.equal(evidence.results[0].second.cache, 'HIT');
});

test('garbage, multi-value, missing, and body/header-mismatched build probes fail closed', async () => {
  for (const response of [
    versionResponse('garbage'),
    versionResponse(`${BUILD_A}, ${BUILD_B}`),
    new Response(JSON.stringify({ version: BUILD_A }), { status: 200 }),
    versionResponse(BUILD_A, BUILD_B),
  ]) {
    const evidence = await verifyCacheReadback({
      expectedScores: expectedScores(), attempts: 1, buildAttempts: 1, concurrency: 1,
      fetchImpl: scriptedFetch([response]),
    });
    assert.equal(evidence.status, 'failed');
    assert.equal(evidence.acceptedBuild, null);
    assert.equal(evidence.results.length, 0);
    assert.match(evidence.failures[0].code, /build_identity|build_probe/);
  }
});

test('A to B on HTTP 500 taints the pass and A recovery cannot wash it out', async () => {
  const responses = [
    versionResponse(BUILD_A),
    new Response('temporary', { status: 500, headers: { 'x-skillstore-build': BUILD_B } }),
    versionResponse(BUILD_A),
    ...stableReadPair('alpha', BUILD_A),
    versionResponse(BUILD_A),
  ];
  const evidence = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 2, buildAttempts: 2,
    buildRetryDelayMs: 0, concurrency: 1, sleepImpl: async () => {},
    fetchImpl: scriptedFetch(responses),
  });
  assert.equal(evidence.status, 'complete');
  assert.equal(evidence.acceptedBuild, BUILD_A);
  assert.equal(evidence.buildAttemptCount, 2);
  assert.deepEqual(evidence.buildPasses[0].failureCodes, ['build_transition']);
  assert.equal(evidence.buildPasses[0].builds.includes(BUILD_B), true);
  assert.equal(evidence.rejectedPassDiagnostics.length, 1);
  assert.equal(evidence.retryableReadFailures, 0);
});

test('429/503 retries honor bounded Retry-After with jitter inside the pinned build', async () => {
  const delays = [];
  const evidence = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 2, buildAttempts: 1, concurrency: 1,
    randomImpl: () => 0,
    sleepImpl: async (delay) => { delays.push(delay); },
    fetchImpl: scriptedFetch([
      versionResponse(BUILD_A),
      new Response('busy', {
        status: 503,
        headers: { 'retry-after': '120', 'x-skillstore-build': BUILD_A },
      }),
      ...stableReadPair('alpha', BUILD_A),
      versionResponse(BUILD_A),
    ]),
  });
  assert.equal(evidence.status, 'complete');
  assert.deepEqual(delays, [500]);
  assert.equal(evidence.retryableReadFailures, 1);
  assert.equal(evidence.requestBudget.retriesUsed, 1);
});

test('a single-slug retry crossing builds taints the entire pass', async () => {
  const evidence = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 2, buildAttempts: 1, concurrency: 1,
    sleepImpl: async () => {},
    fetchImpl: scriptedFetch([
      versionResponse(BUILD_A),
      new Response('temporary', { status: 503, headers: { 'x-skillstore-build': BUILD_A } }),
      cachedResponse('alpha', { build: BUILD_B, cache: 'HIT', write: 'SKIPPED' }),
    ]),
  });
  assert.equal(evidence.status, 'blocked_deployment_change');
  assert.equal(evidence.acceptedBuild, null);
  assert.equal(evidence.results.length, 0);
  assert.deepEqual(evidence.buildPasses[0].failureCodes, ['build_transition']);
});

test('a transition aborts concurrent workers instead of scanning the remaining scope', async () => {
  let calls = 0;
  let cancelled = 0;
  const hanging = () => new Response(new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode('{"data":'));
    },
    cancel() { cancelled += 1; },
  }), { status: 200, headers: { 'x-skillstore-build': BUILD_A } });
  const evidence = await Promise.race([
    verifyCacheReadback({
      expectedScores: expectedScores(['alpha', 'beta', 'charlie', 'delta']),
      attempts: 1, buildAttempts: 1, concurrency: 2, timeoutMs: 100,
      fetchImpl: async (url) => {
        calls += 1;
        const pathname = new URL(url).pathname;
        if (pathname === '/_app/version.json') return versionResponse(BUILD_A);
        if (pathname.endsWith('/alpha')) {
          return new Response('transition', { status: 500, headers: { 'x-skillstore-build': BUILD_B } });
        }
        return hanging();
      },
    }),
    new Promise((resolve) => setTimeout(() => resolve('external-timeout'), 250)),
  ]);
  assert.notEqual(evidence, 'external-timeout');
  assert.equal(evidence.status, 'blocked_deployment_change');
  assert.ok(calls < 1 + (4 * 2), `transition did not bound calls: ${calls}`);
  assert.ok(cancelled >= 1, 'in-flight body must be cancelled on transition');
});

test('whole-response timeout remains active after headers and cancels a hanging body', async () => {
  let cancelled = 0;
  const hanging = new Response(new ReadableStream({
    start(controller) { controller.enqueue(new TextEncoder().encode('{"data":')); },
    cancel() { cancelled += 1; },
  }), {
    status: 200,
    headers: { 'content-type': 'application/json', 'x-skillstore-build': BUILD_A },
  });
  const outcome = await Promise.race([
    verifyCacheReadback({
      expectedScores: expectedScores(), attempts: 1, buildAttempts: 1,
      concurrency: 1, timeoutMs: 20,
      fetchImpl: scriptedFetch([versionResponse(), hanging]),
    }),
    new Promise((resolve) => setTimeout(() => resolve('external-timeout'), 200)),
  ]);
  assert.notEqual(outcome, 'external-timeout');
  assert.equal(outcome.status, 'failed');
  assert.equal(outcome.failures[0].code, 'read_timeout');
  assert.ok(cancelled >= 1);
});

test('detail and non-2xx bodies have hard byte bounds and are cancelled when exceeded', async () => {
  let cancelled = 0;
  const oversized = new Response(new ReadableStream({
    start(controller) { controller.enqueue(new Uint8Array(2048)); },
    cancel() { cancelled += 1; },
  }), {
    status: 200,
    headers: { 'content-type': 'application/json', 'x-skillstore-build': BUILD_A },
  });
  const evidence = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 1, buildAttempts: 1,
    concurrency: 1, maxBodyBytes: 1024,
    fetchImpl: scriptedFetch([versionResponse(), oversized]),
  });
  assert.equal(evidence.status, 'failed');
  assert.equal(evidence.failures[0].code, 'response_too_large');
  assert.ok(cancelled >= 1);

  let errorCancelled = 0;
  const oversizedError = new Response(new ReadableStream({
    start(controller) { controller.enqueue(new Uint8Array(70 * 1024)); },
    cancel() { errorCancelled += 1; },
  }), { status: 503, headers: { 'x-skillstore-build': BUILD_A } });
  const non2xx = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 1, buildAttempts: 1, concurrency: 1,
    fetchImpl: scriptedFetch([versionResponse(), oversizedError]),
  });
  assert.equal(non2xx.status, 'failed');
  assert.equal(non2xx.failures[0].code, 'response_too_large');
  assert.ok(errorCancelled >= 1, 'oversized non-2xx body must be cancelled');
});

test('list generation probe is bounded, build-pinned, and records exact cache generation identity', async () => {
  const calls = [];
  const list = new Response(JSON.stringify({ data: [{ slug: 'alpha' }] }), {
    status: 200,
    headers: {
      'x-skillstore-build': BUILD_A,
      'x-kv-cache': 'MISS',
      'x-kv-key': 'skills-list',
      'x-kv-version': 'generation-1',
      'x-kv-write': 'STORED',
    },
  });
  const identity = await closure.probeListGeneration({
    fetchImpl: scriptedFetch([versionResponse(), list, versionResponse()], calls),
    siteUrl: 'https://skillstore.io',
    timeoutMs: 100,
  });
  assert.deepEqual(identity, {
    schemaVersion: 1,
    build: BUILD_A,
    cache: 'MISS',
    key: 'skills-list',
    version: 'generation-1',
    write: 'STORED',
    requestsUsed: 3,
  });
  assert.equal(new URL(calls[1].url).searchParams.get('__skillstore_build'), BUILD_A);
  assert.equal(calls[0].init.headers['Cache-Control'], 'no-cache');
  assert.equal(calls[2].init.headers['Cache-Control'], 'no-cache');
});

test('stable cache semantics remain strict inside one accepted build', async () => {
  const wrongVersion = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 1, buildAttempts: 1, concurrency: 1,
    expectedCacheVersion: 'v6',
    fetchImpl: scriptedFetch([
      versionResponse(),
      cachedResponse('alpha', { cache: 'HIT', version: 'v5', write: 'SKIPPED' }),
      cachedResponse('alpha', { cache: 'HIT', version: 'v5', write: 'SKIPPED' }),
      versionResponse(),
    ]),
  });
  assert.equal(wrongVersion.status, 'failed');
  assert.equal(wrongVersion.failures[0].code, 'cache_version_mismatch');

  const staleScore = await verifyCacheReadback({
    expectedScores: expectedScores(), attempts: 1, buildAttempts: 1, concurrency: 1,
    fetchImpl: scriptedFetch([
      versionResponse(),
      cachedResponse('alpha', { cache: 'HIT', qualityScore: 87, write: 'SKIPPED' }),
      cachedResponse('alpha', { cache: 'HIT', qualityScore: 87, write: 'SKIPPED' }),
      versionResponse(),
    ]),
  });
  assert.equal(staleScore.status, 'failed');
  assert.equal(staleScore.failures[0].code, 'score_mismatch');
});

test('5295-scope retry-amplified readback budget is deterministic and below the 360-minute job', async () => {
  const budget = closure.calculateReadbackBudget({
    slugCount: 5295,
    readsPerSlug: 2,
    attempts: 2,
    buildAttempts: 2,
    concurrency: 16,
    requestTimeoutMs: 5_000,
    retryDelayMaxMs: 1_000,
    buildRetryDelayMs: 15_000,
    qps: 8,
    probeRequestsPerPass: 2,
    invalidationCount: 1,
    invalidationBatchSize: 200,
    invalidationTimeoutMs: 60_000,
    workflowReserveMs: 20 * 60_000,
  });
  assert.equal(budget.requestLimit, 42_364);
  assert.equal(budget.retryLimit, 21_180);
  assert.equal(budget.invalidationBatches, 1);
  assert.equal(budget.invalidationWorstCaseMs, 60_000);
  assert.ok(budget.worstCaseReadbackMs < 340 * 60_000, JSON.stringify(budget));
  assert.ok(budget.worstCaseTotalMs < 360 * 60_000, JSON.stringify(budget));

  const fullInvalidation = closure.calculateReadbackBudget({
    ...budget.parameters,
    invalidationCount: 5295,
  });
  assert.ok(fullInvalidation.worstCaseTotalMs >= 360 * 60_000);

  const amplified = closure.calculateReadbackBudget({
    ...budget.parameters,
    attempts: 3,
    requestTimeoutMs: 30_000,
  });
  assert.ok(amplified.worstCaseTotalMs >= 360 * 60_000);
});

const TEST_HEAD = 'c'.repeat(40);
const SOURCE_HEAD = 'd'.repeat(40);
const WORKFLOW_IDENTITY = {
  repository: 'aiskillstore/marketplace',
  runId: '123456789',
  runAttempt: 1,
  headSha: TEST_HEAD,
  eventName: 'workflow_dispatch',
  workflowName: 'Recover Score and Cache Closure',
};

function slugDigest(slugs) {
  return createHash('sha256').update(`${[...slugs].sort().join('\n')}\n`).digest('hex');
}

function scoreRows(slugs) {
  return slugs.map((slug, index) => ({
    slug,
    qualityScore: 80 + index,
    qualityTier: 'silver',
    calculatedAt: `2026-07-15T12:00:0${index}.000Z`,
    snapshotId: `${index + 1}1111111-1111-4111-8111-111111111111`,
  }));
}

function completedReadback(slugCount = 2, invalidationCount = slugCount) {
  const slugs = Array.from({ length: slugCount }, (_, index) => `slug-${index + 1}`);
  const scores = scoreRows(slugs);
  return {
    acceptedBuild: BUILD_B,
    buildAttemptCount: 1,
    buildPasses: [{ attempt: 1, builds: [BUILD_B], failureCodes: [], status: 'accepted' }],
    builds: [BUILD_B],
    failures: [],
    rejectedPassDiagnostics: [],
    results: slugs.map((slug, index) => ({
      slug,
      first: {
        build: BUILD_B, cache: 'MISS', key: `skill:${slug}`, version: 'v6', write: 'STORED',
        score: {
          qualityScore: scores[index].qualityScore,
          qualityTier: scores[index].qualityTier,
          calculatedAt: scores[index].calculatedAt,
        },
      },
      second: {
        build: BUILD_B, cache: 'HIT', key: `skill:${slug}`, version: 'v6', write: 'SKIPPED',
        score: {
          qualityScore: scores[index].qualityScore,
          qualityTier: scores[index].qualityTier,
          calculatedAt: scores[index].calculatedAt,
        },
      },
    })),
    retryableReadFailures: 0,
    schemaVersion: 1,
    slugCount,
    slugSha256: slugDigest(slugs),
    expectedBuild: BUILD_B,
    expectedCacheVersion: 'v6',
    expectedScoreSha256: createHash('sha256').update(JSON.stringify(scores)).digest('hex'),
    workflowIdentity: { ...WORKFLOW_IDENTITY },
    budget: closure.calculateReadbackBudget({
      slugCount, readsPerSlug: 2, attempts: 2, buildAttempts: 2, concurrency: 16,
      requestTimeoutMs: 5_000, retryDelayMaxMs: 1_000, buildRetryDelayMs: 15_000,
      qps: 8, probeRequestsPerPass: 2, invalidationCount,
      invalidationBatchSize: 200, invalidationTimeoutMs: 60_000,
      workflowReserveMs: 20 * 60_000,
    }),
    requestBudget: { requestLimit: 20, requestsUsed: 6, retryLimit: 8, retriesUsed: 0, qps: 8 },
    status: 'complete',
  };
}

function completedClosureInput() {
  const slugs = ['slug-1', 'slug-2'];
  const scores = scoreRows(slugs);
  const before = scores.map((score, index) => ({
    ...score,
    calculatedAt: `2026-07-15T11:59:0${index}.000Z`,
    snapshotId: `${index + 5}1111111-1111-4111-8111-111111111111`,
  }));
  return {
    scope: 'source-run-failures',
    plannedSlugCount: 2,
    selectedSlugCount: 2,
    workflowIdentity: { ...WORKFLOW_IDENTITY },
    planManifestVerified: true,
    plan: {
      metadata: {
        schemaVersion: 2,
        scope: 'source-run-failures',
        sourceRunId: '987654321',
        slugCount: 2,
        slugSha256: slugDigest(slugs),
        workflowIdentity: { ...WORKFLOW_IDENTITY },
        sourceIdentity: {
          databaseId: 987654321,
          displayTitle: 'Recalculate Skill Scores',
          status: 'completed',
          conclusion: 'failure',
          headSha: SOURCE_HEAD,
          event: 'workflow_dispatch',
        },
      },
      plannedSlugs: slugs,
    },
    selectedSlugs: slugs,
    invalidationSlugs: slugs,
    expectedScoreEvidence: { schemaVersion: 1, scores },
    beforeScoreEvidence: { schemaVersion: 1, scores: before },
    scoreWriteEvidence: {
      schemaVersion: 1,
      provenCount: 2,
      runBoundary: '2026-07-15T12:00:00.000Z',
      transitions: slugs.map((slug, index) => ({
        slug,
        beforeSnapshotId: before[index].snapshotId,
        afterSnapshotId: scores[index].snapshotId,
        beforeCalculatedAt: before[index].calculatedAt,
        afterCalculatedAt: scores[index].calculatedAt,
        snapshotChanged: true,
        calculatedAtAdvanced: true,
      })),
    },
    score: {
      schemaVersion: 1,
      requestedCount: 2,
      successfulCount: 2,
      failedCount: 0,
      causallyProvenCount: 2,
      runBoundary: '2026-07-15T12:00:00.000Z',
      wrapperExit: 0,
    },
    invalidation: {
      schemaVersion: 2,
      type: 'skills',
      exactSlugs: slugs,
      slugSha256: slugDigest(slugs),
      expectedCount: 2,
      totalCount: 2,
      successCount: 2,
      failedCount: 0,
      listVersionBumped: true,
      contract: {
        invalidateArtifacts: false,
        invalidateDependentPacks: false,
        failOnError: true,
      },
      before: {
        build: BUILD_B, key: 'skills-list:generation-1', version: 'generation-1',
        workflowIdentity: { ...WORKFLOW_IDENTITY },
      },
      after: {
        build: BUILD_B, key: 'skills-list:generation-2', version: 'generation-2',
        workflowIdentity: { ...WORKFLOW_IDENTITY },
      },
      workflowIdentity: { ...WORKFLOW_IDENTITY },
    },
    readback: completedReadback(),
    preflightBudget: completedReadback().budget,
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
  assert.equal(first.readback.acceptedBuild, BUILD_B);
  assert.equal(first.finalizerStatus, 'complete');

  const approvedInput = completedClosureInput();
  approvedInput.scope = 'approved-catalog-cache';
  approvedInput.plan.metadata.scope = 'approved-catalog-cache';
  approvedInput.plan.metadata.sourceRunId = '';
  approvedInput.plan.metadata.sourceIdentity = null;
  approvedInput.score = null;
  approvedInput.beforeScoreEvidence = null;
  approvedInput.scoreWriteEvidence = null;
  approvedInput.invalidationSlugs = ['slug-1'];
  approvedInput.invalidation.exactSlugs = ['slug-1'];
  approvedInput.invalidation.slugSha256 = slugDigest(['slug-1']);
  approvedInput.invalidation.expectedCount = 1;
  approvedInput.invalidation.totalCount = 1;
  approvedInput.invalidation.successCount = 1;
  approvedInput.readback = completedReadback(2, 1);
  approvedInput.preflightBudget = approvedInput.readback.budget;
  const approvedCatalog = finalizeClosure(approvedInput);
  assert.equal(approvedCatalog.status, 'complete');
  assert.equal(approvedCatalog.score.status, 'not_required');
});

test('finalizer rejects old workflow artifacts, inconsistent slugs, forged build, and skeleton readback', () => {
  const oldArtifact = completedClosureInput();
  oldArtifact.readback.workflowIdentity.runId = '111111111';
  assert.notEqual(finalizeClosure(oldArtifact).status, 'complete');

  const inconsistentSlugs = completedClosureInput();
  inconsistentSlugs.invalidationSlugs = ['other-slug'];
  inconsistentSlugs.invalidation.exactSlugs = ['other-slug'];
  inconsistentSlugs.invalidation.slugSha256 = slugDigest(['other-slug']);
  assert.notEqual(finalizeClosure(inconsistentSlugs).status, 'complete');

  const forgedBuild = completedClosureInput();
  forgedBuild.readback.acceptedBuild = 'forged-build';
  forgedBuild.readback.builds = ['forged-build'];
  forgedBuild.readback.buildPasses[0].builds = ['forged-build'];
  for (const result of forgedBuild.readback.results) {
    result.first.build = 'forged-build';
    result.second.build = 'forged-build';
  }
  assert.notEqual(finalizeClosure(forgedBuild).status, 'complete');

  const skeleton = completedClosureInput();
  skeleton.readback.results = skeleton.readback.results.map(({ slug }) => ({
    slug, first: { build: BUILD_B }, second: { build: BUILD_B },
  }));
  assert.notEqual(finalizeClosure(skeleton).status, 'complete');
});

test('finalizer CLI verifies manifests and atomically replays the same complete local evidence', () => {
  const directory = mkdtempSync(join(tmpdir(), 'score-cache-finalizer-'));
  try {
    const input = completedClosureInput();
    const planDir = join(directory, 'plan');
    const resultDir = join(directory, 'result');
    mkdirSync(planDir);
    mkdirSync(resultDir);
    const writeJson = (path, value) => writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
    const writeManifest = (path, names) => writeFileSync(
      join(path, 'SHA256SUMS'),
      `${names.sort().map((name) => `${createHash('sha256').update(readFileSync(join(path, name))).digest('hex')}  ${name}`).join('\n')}\n`,
    );
    writeJson(join(planDir, 'metadata.json'), input.plan.metadata);
    writeFileSync(join(planDir, 'requested-slugs.txt'), `${input.plan.plannedSlugs.join('\n')}\n`);
    writeManifest(planDir, ['metadata.json', 'requested-slugs.txt']);
    writeJson(join(resultDir, 'metadata.json'), input.score);
    writeJson(join(resultDir, 'before-score-evidence.json'), input.beforeScoreEvidence);
    writeJson(join(resultDir, 'score-write-evidence.json'), input.scoreWriteEvidence);
    writeManifest(resultDir, ['metadata.json', 'before-score-evidence.json', 'score-write-evidence.json']);

    const selectedPath = join(directory, 'selected.txt');
    const invalidationSlugsPath = join(directory, 'invalidation.txt');
    const expectedPath = join(directory, 'expected.json');
    const invalidationPath = join(directory, 'invalidation.json');
    const budgetPath = join(directory, 'budget.json');
    const readbackPath = join(directory, 'readback.json');
    const outputPath = join(directory, 'final.json');
    const replayPath = join(directory, 'final-replay.json');
    writeFileSync(selectedPath, `${input.selectedSlugs.join('\n')}\n`);
    writeFileSync(invalidationSlugsPath, `${input.invalidationSlugs.join('\n')}\n`);
    writeJson(expectedPath, input.expectedScoreEvidence);
    writeJson(invalidationPath, input.invalidation);
    writeJson(budgetPath, input.preflightBudget);
    writeJson(readbackPath, input.readback);
    const identityArgs = [
      '--workflow-repository', WORKFLOW_IDENTITY.repository,
      '--workflow-run-id', WORKFLOW_IDENTITY.runId,
      '--workflow-run-attempt', String(WORKFLOW_IDENTITY.runAttempt),
      '--workflow-head-sha', WORKFLOW_IDENTITY.headSha,
      '--workflow-event-name', WORKFLOW_IDENTITY.eventName,
      '--workflow-name', WORKFLOW_IDENTITY.workflowName,
    ];
    const args = [
      resolve(ROOT, 'scripts/score-cache-closure.mjs'), 'finalize-closure',
      '--scope', 'source-run-failures', '--plan-dir', planDir, '--result-dir', resultDir,
      '--selected-slugs', selectedPath, '--invalidation-slugs', invalidationSlugsPath,
      '--expected-score-evidence', expectedPath, '--invalidation-evidence', invalidationPath,
      '--preflight-budget', budgetPath, '--readback', readbackPath, ...identityArgs,
    ];
    const first = spawnSync(process.execPath, [...args, '--output', outputPath], { encoding: 'utf8' });
    assert.equal(first.status, 0, first.stderr);
    const replay = spawnSync(process.execPath, [...args, '--output', replayPath], { encoding: 'utf8' });
    assert.equal(replay.status, 0, replay.stderr);
    assert.deepEqual(JSON.parse(readFileSync(replayPath, 'utf8')), JSON.parse(readFileSync(outputPath, 'utf8')));
    assert.equal(JSON.parse(readFileSync(outputPath, 'utf8')).status, 'complete');
    assert.equal([...resolve(directory).matchAll(/\.tmp/g)].length, 0);
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
      buildPasses: [{
        attempt: 1,
        builds: [BUILD_A, BUILD_B],
        failureCodes: ['build_transition'],
        status: 'rejected',
      }],
      builds: [],
      failures: [{ slug: '*', code: 'build_transition', error: 'deployment changed' }],
      rejectedPassDiagnostics: [{ attempt: 1, failures: [{ code: 'build_transition' }], retries: 0 }],
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
  assert.match(RECOVERY, /--attempts 2/);
  assert.match(RECOVERY, /--build-attempts 2/);
  assert.match(RECOVERY, /--build-retry-delay-ms 15000/);
  assert.match(RECOVERY, /--timeout-ms 5000/);
  assert.match(RECOVERY, /--max-body-bytes 1048576/);
  assert.match(RECOVERY, /--qps 8/);
  assert.match(RECOVERY, /Prove readback budget before any cache write/);
  assert.match(RECOVERY, /prove-readback-budget/);
  assert.match(RECOVERY, /--invalidation-count "\$\{\{ steps\.selected\.outputs\.invalidation_count \}\}"/);
  assert.ok(
    RECOVERY.indexOf('Prove readback budget before any cache write')
      < RECOVERY.indexOf('Invalidate selected score API entries'),
  );
  assert.match(RECOVERY, /Freeze list generation before invalidation/);
  assert.match(RECOVERY, /Freeze list generation after invalidation/);
  assert.match(RECOVERY, /probe-list-generation/);
  assert.match(RECOVERY, /--expected-build "\$pinned_build"/);
  assert.match(RECOVERY, /workflowIdentity:\{repository:\$repository,runId:\$runId/);
  assert.match(RECOVERY, /name: Finalize score and cache closure state\n\s+id: finalizer\n\s+if: always\(\)/);
  assert.match(RECOVERY, /score-cache-closure\.mjs finalize-closure/);
  assert.match(RECOVERY, /--plan-dir "\$RUNNER_TEMP\/score-cache-recovery-plan"/);
  assert.match(RECOVERY, /--selected-slugs "\$RUNNER_TEMP\/cache-closure-slugs\.txt"/);
  assert.match(RECOVERY, /--invalidation-slugs "\$RUNNER_TEMP\/cache-invalidation-slugs\.txt"/);
  assert.match(RECOVERY, /--invalidation-evidence "\$evidence\/invalidation-evidence\.json"/);
  assert.match(RECOVERY, /--preflight-budget "\$RUNNER_TEMP\/readback-budget\.json"/);
  assert.match(RECOVERY, /--readback "\$RUNNER_TEMP\/cache-readback\.json"/);
  assert.match(RECOVERY, /--workflow-run-id "\$GITHUB_RUN_ID"/);
  assert.match(RECOVERY, /--workflow-head-sha "\$GITHUB_SHA"/);
  assert.match(RECOVERY, /--output "\$evidence\/final-summary\.json"/);
  assert.match(RECOVERY, /find \. -type f ! -name SHA256SUMS/);
  assert.match(RECOVERY, /blocked_deployment_change/);
  assert.match(RECOVERY, /\.finalizerStatus == "complete"/);
  assert.match(RECOVERY, /Require complete score and cache recovery/);
  assert.match(RECOVERY, /freeze-score-evidence/);
  assert.match(RECOVERY, /before-score-evidence\.json/);
  assert.match(RECOVERY, /verify-score-transitions/);
  assert.match(RECOVERY, /causallyProvenCount/);
  assert.match(RECOVERY, /test "\$proven_count" -eq "\$successful_count"/);
  assert.match(RECOVERY, /--expected-score-evidence/);
  assert.match(RECOVERY, /score_args\+=\(--result-dir "\$score_result"\)/);
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
