import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { normalizeSlugs, runWarm, WarmError } from '../warm-skill-cache.mjs';

const BUILD_A = `${'a'.repeat(40)}.deploy-a`;
const BUILD_B = `${'b'.repeat(40)}.deploy-b`;
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');

function response({
  status = 200,
  build = BUILD_A,
  apiCache,
  pageCache,
  zipCache,
  body = 'ok',
  ray = 'abc123-SJC',
  contentLength,
  responseBytes,
  omitLength = false,
} = {}) {
  const headers = new Headers({
    'x-skillstore-build': build,
    'cf-ray': ray,
  });
  if (apiCache) headers.set('x-api-kv-cache', apiCache);
  if (pageCache) headers.set('x-page-kv-cache', pageCache);
  if (zipCache) headers.set('x-cache', zipCache);
  const actualBytes = new TextEncoder().encode(body).byteLength;
  if (!omitLength) headers.set('content-length', String(contentLength ?? actualBytes));
  if (responseBytes !== undefined) {
    headers.set('x-skillstore-response-bytes', String(responseBytes));
  }
  return new Response(body, { status, headers });
}

function versionResponse(build = BUILD_A) {
  return response({ build, body: JSON.stringify({ version: build }) });
}

function streamingResponse({
  build = BUILD_A,
  apiCache,
  pageCache,
  chunks = [],
  contentLength,
  responseBytes,
  pending = false,
  onCancel = () => {},
} = {}) {
  const headers = new Headers({
    'x-skillstore-build': build,
    'cf-ray': 'stream-SJC',
  });
  if (apiCache) headers.set('x-api-kv-cache', apiCache);
  if (pageCache) headers.set('x-page-kv-cache', pageCache);
  if (contentLength !== undefined) headers.set('content-length', String(contentLength));
  if (responseBytes !== undefined) {
    headers.set('x-skillstore-response-bytes', String(responseBytes));
  }
  const encoded = chunks.map((chunk) => new TextEncoder().encode(chunk));
  let cursor = 0;
  const body = new ReadableStream({
    pull(controller) {
      if (pending) return;
      if (cursor < encoded.length) controller.enqueue(encoded[cursor++]);
      else controller.close();
    },
    cancel: onCancel,
  }, { highWaterMark: 0 });
  return new Response(body, { headers });
}

function versionBodyBytes(build = BUILD_A) {
  return new TextEncoder().encode(JSON.stringify({ version: build })).byteLength;
}

function sequencedFetch(steps, calls) {
  let cursor = 0;
  return async (url, init) => {
    calls.push({ url, init });
    const step = steps[cursor++];
    assert(step, `unexpected request ${cursor}: ${url}`);
    if (step.assert) step.assert(url, init);
    return typeof step.response === 'function' ? step.response(url, init) : step.response;
  };
}

function baseOptions(fetchImpl, records = [], overrides = {}) {
  return {
    slugs: ['alpha'],
    siteUrl: 'https://skillstore.test',
    locales: ['en'],
    concurrency: 2,
    maxAttempts: 3,
    retryWindowMinMs: 120_000,
    retryWindowMaxMs: 120_000,
    timeoutMs: 1_000,
    requestBudget: 100,
    byteBudget: 1_000_000,
    fetchImpl,
    sleep: async () => {},
    report: (record) => records.push(record),
    ...overrides,
  };
}

test('normalizes and rejects empty warm scopes', async () => {
  assert.deepEqual(normalizeSlugs(' beta,alpha\nalpha '), ['alpha', 'beta']);
  await assert.rejects(
    runWarm(baseOptions(async () => versionResponse(), [], { slugs: [] })),
    (error) => error instanceof WarmError && /scope is empty/i.test(error.message)
  );
});

test('enforces request and byte budgets before unbounded warming can continue', async () => {
  await assert.rejects(
    runWarm(baseOptions(async () => versionResponse(), [], { requestBudget: 7 })),
    /below the minimum 8/i
  );

  const summary = await runWarm(baseOptions(async () => versionResponse(), [], { byteBudget: 10 }));
  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /byte budget.*exceed/i);
  assert.equal(summary.budget.requests, 1);
});

test('rejects an oversized Content-Length before reading and cancels the body', async () => {
  let cancelled = false;
  let calls = 0;
  const summary = await runWarm(baseOptions(async (url) => {
    calls++;
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return streamingResponse({
      apiCache: 'HIT',
      contentLength: 10,
      pending: true,
      onCancel: () => { cancelled = true; },
    });
  }, [], {
    byteBudget: versionBodyBytes() + 5,
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /before reading/i);
  assert.equal(summary.budget.bytes, versionBodyBytes());
  assert.equal(summary.budget.reservedBytes, 0);
  assert.equal(cancelled, true);
  assert.equal(calls, 2);
});

test('enforces the hard byte limit while streaming one chunked response', async () => {
  let cancelled = false;
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return streamingResponse({
      apiCache: 'HIT',
      chunks: ['1234', '5678'],
      contentLength: 4,
      onCancel: () => { cancelled = true; },
    });
  }, [], {
    byteBudget: versionBodyBytes() + 6,
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /exceeded its declared/i);
  assert.equal(summary.budget.bytes, versionBodyBytes() + 4);
  assert.ok(summary.budget.bytes <= summary.budget.byteLimit);
  assert.equal(summary.budget.reservedBytes, 0);
  assert.equal(cancelled, true);
});

test('atomically reserves Content-Length across concurrent responses', async () => {
  const cancelled = [];
  let apiCalls = 0;
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    const index = apiCalls++;
    return streamingResponse({
      apiCache: 'HIT',
      contentLength: 60,
      pending: true,
      onCancel: () => { cancelled[index] = true; },
    });
  }, [], {
    slugs: ['alpha', 'beta'],
    concurrency: 2,
    byteBudget: versionBodyBytes() + 100,
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /byte budget/i);
  assert.ok(summary.budget.bytes <= summary.budget.byteLimit);
  assert.equal(summary.budget.reservedBytes, 0);
  assert.deepEqual(cancelled, [true, true]);
  assert.equal(apiCalls, 2);
});

test('fails closed when both response-size headers are missing', async () => {
  let cancelled = false;
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return streamingResponse({
      apiCache: 'HIT',
      chunks: ['ok'],
      onCancel: () => { cancelled = true; },
    });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /missing Content-Length/i);
  assert.equal(cancelled, true);
});

test('fails closed on an invalid Skillstore response-size header', async () => {
  let cancelled = false;
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return streamingResponse({
      apiCache: 'HIT',
      chunks: ['ok'],
      responseBytes: 'invalid',
      onCancel: () => { cancelled = true; },
    });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /x-skillstore-response-bytes must be/i);
  assert.equal(cancelled, true);
});

test('fails closed when Content-Length conflicts with the Skillstore size header', async () => {
  let cancelled = false;
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return streamingResponse({
      apiCache: 'HIT',
      chunks: ['ok'],
      contentLength: 2,
      responseBytes: 3,
      onCancel: () => { cancelled = true; },
    });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /Conflicting response sizes/i);
  assert.equal(cancelled, true);
});

test('accepts the trusted Skillstore response-size header for dynamic pages', async () => {
  const calls = [];
  const html = '<html>cached</html>';
  const htmlBytes = new TextEncoder().encode(html).byteLength;
  const pageHit = () => response({
    pageCache: 'HIT',
    body: html,
    omitLength: true,
    responseBytes: htmlBytes,
  });
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: pageHit() },
    { response: pageHit() },
    { response: pageHit() },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, true);
  assert.equal(summary.completedEndpoints.page, 1);
  assert.equal(summary.budget.requests, 8);
  assert.equal(new Headers(calls[4].init.headers).get('accept-encoding'), 'identity');
});

test('warms API before HTML, accepts MISS then HIT, and verifies two ordinary HITs', async () => {
  const calls = [];
  const records = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS', body: '{"data":{}}' }) },
    { response: response({ apiCache: 'HIT', body: '{"data":{}}' }) },
    {
      assert: (url, init) => {
        assert.match(url, /__skillstore_build=/);
        assert.equal(new Headers(init.headers).has('cache-control'), false);
      },
      response: response({ apiCache: 'HIT', body: '{"data":{}}' }),
    },
    {
      assert: (url, init) => {
        assert.match(url, /__skillstore_build=/);
        assert.equal(new Headers(init.headers).has('cache-control'), false);
      },
      response: response({ apiCache: 'HIT', body: '{"data":{}}' }),
    },
    { response: response({ pageCache: 'MISS', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    {
      assert: (url, init) => {
        assert.match(url, /__skillstore_build=/);
        assert.equal(new Headers(init.headers).has('cache-control'), false);
      },
      response: response({ pageCache: 'HIT', body: '<html></html>' }),
    },
    {
      assert: (url, init) => {
        assert.match(url, /__skillstore_build=/);
        assert.equal(new Headers(init.headers).has('cache-control'), false);
      },
      response: response({ pageCache: 'HIT', body: '<html></html>' }),
    },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, records));

  assert.equal(summary.success, true);
  assert.deepEqual(summary.completedEndpoints, { api: 1, page: 1, zip: 0 });
  assert.equal(summary.failedEndpoints, 0);
  assert.equal(summary.skippedEndpoints, 0);
  assert.equal(summary.budget.requests, 10);
  assert.match(calls[1].url, /\/api\/skills\/alpha/);
  assert.match(calls[5].url, /\/skills\/alpha/);
  assert.equal(new Headers(calls[1].init.headers).get('cache-control'), 'no-cache');
  const innerRecord = records.find((record) => record.phase === 'inner-cache');
  assert.equal(innerRecord?.colo, 'SJC');
  for (const field of ['url', 'attempt', 'status', 'cache', 'bytes', 'cfRay', 'colo']) {
    assert.equal(Object.hasOwn(innerRecord, field), true, `JSONL evidence must include ${field}`);
  }
  assert.deepEqual(
    records
      .filter((record) => record.kind === 'api' && record.phase === 'ordinary-verification')
      .map((record) => record.attempt),
    [1, 2]
  );
  assert.deepEqual(
    records
      .filter((record) => record.kind === 'page' && record.phase === 'ordinary-verification')
      .map((record) => record.attempt),
    [1, 2]
  );
});

test('fails a persistent MISS and does not start HTML warming', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'MISS' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, false);
  assert.equal(summary.completedEndpoints.api, 0);
  assert.equal(summary.completedEndpoints.page, 0);
  assert.equal(summary.failedEndpoints, 1);
  assert.equal(summary.skippedEndpoints, 1);
  assert.match(summary.failures.join('\n'), /never reached.*HIT/i);
  assert.equal(calls.some((call) => new URL(call.url).pathname === '/skills/alpha'), false);
});

test('retries 429 and 5xx responses before accepting HIT', async () => {
  const calls = [];
  const records = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ status: 429 }) },
    { response: response({ status: 503 }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, records, { maxAttempts: 4 }));

  assert.equal(summary.success, true);
  assert.deepEqual(
    records.filter((record) => record.kind === 'api').map((record) => record.status),
    [429, 503, 200, 200, 200]
  );
  assert.equal(summary.budget.requests, 10);
});

test('never exceeds the hard 120 second deadline for one endpoint', async () => {
  let clock = 0;
  const fetchImpl = async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return response({ apiCache: 'MISS' });
  };

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    maxAttempts: 100,
    retryWindowMinMs: 120_000,
    retryWindowMaxMs: 120_000,
    requestBudget: 500,
    now: () => clock,
    sleep: async (milliseconds) => {
      clock += milliseconds;
    },
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /endpoint deadline/i);
  assert.ok(clock <= 120_000, `endpoint elapsed ${clock}ms exceeded 120000ms`);
});

test('aborts immediately when a response build differs from the pinned deployment', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse(BUILD_A) },
    { response: response({ build: BUILD_B, apiCache: 'HIT' }) },
    { response: versionResponse(BUILD_A) },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, [], { maxAttempts: 5 }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /deployment changed/i);
  assert.equal(calls.length, 2, 'fatal deployment mismatch must skip retries and the final probe');
});

test('a fatal deployment mismatch aborts another in-flight fetch', async () => {
  let apiCalls = 0;
  let inFlightAborted = false;
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url, init });
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    apiCalls++;
    if (apiCalls === 1) return response({ build: BUILD_B, apiCache: 'HIT' });
    return new Promise((_, reject) => {
      const abort = () => {
        inFlightAborted = true;
        reject(init.signal.reason || new Error('aborted'));
      };
      if (init.signal.aborted) abort();
      else init.signal.addEventListener('abort', abort, { once: true });
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    slugs: ['alpha', 'beta'],
    concurrency: 2,
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /deployment changed/i);
  assert.equal(inFlightAborted, true);
  assert.equal(apiCalls, 2);
  assert.equal(
    calls.some((call) => new URL(call.url).pathname === '/skills/alpha'),
    false,
    'fatal abort must prevent the page phase'
  );
});

test('rejects a version document that does not exactly match its build header', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    {
      response: response({
        build: BUILD_A,
        body: JSON.stringify({ version: BUILD_B }),
      }),
    },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /build probe mismatch/i);
  assert.equal(calls.length, 1);
});

test('fails if the active deployment changes at the final build probe', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse(BUILD_A) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse(BUILD_B) },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /changed before completion/i);
});

test('reports exact counts for multiple slugs and locales', async () => {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url, init });
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({ pageCache: 'HIT', body: '<html></html>' });
  };

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    slugs: ['alpha', 'beta'],
    locales: ['en', 'zh-hans'],
    concurrency: 3,
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(summary.plannedEndpoints, { api: 2, page: 4, zip: 0 });
  assert.deepEqual(summary.completedEndpoints, { api: 2, page: 4, zip: 0 });
  assert.equal(summary.budget.requests, 20);
  assert.equal(summary.failedEndpoints, 0);
  assert.equal(summary.skippedEndpoints, 0);
  assert.equal(calls.length, 20);
});

test('workflow checks out scripts, requires bounded skill scope, and has no retired content branches', () => {
  const workflow = readFileSync(resolve(REPO_ROOT, '.github/workflows/warm-cache.yml'), 'utf8');
  const invalidateAction = readFileSync(resolve(REPO_ROOT, '.github/actions/invalidate-cache/action.yml'), 'utf8');

  assert.match(workflow, /sparse-checkout: \|\n\s+\.github\/actions\n\s+scripts/);
  assert.match(workflow, /approve_full_catalog/);
  assert.match(workflow, /request_budget/);
  assert.match(workflow, /byte_budget/);
  assert.match(workflow, /Warm scope is empty/);
  assert.match(workflow, /node scripts\/warm-skill-cache\.mjs/);
  assert.match(workflow, /status=eq\.approved&public_eligible=eq\.true/);
  assert.doesNotMatch(workflow, /Warm workflows cache|Warm releases cache|type=skills/);
  assert.doesNotMatch(invalidateAction, /packs\/workflows/);
  assert.match(invalidateAction, /skills\|packs\|plugins\|releases/);
});

test('sync propagates invalidation failures and cannot warm stale 365-day detail entries', () => {
  const workflow = readFileSync(resolve(REPO_ROOT, '.github/workflows/sync-to-supabase.yml'), 'utf8');
  const invalidationSection = workflow.slice(
    workflow.indexOf('cache-invalidate:'),
    workflow.indexOf('# TRIGGER TRANSLATION')
  );

  assert.doesNotMatch(invalidationSection, /continue-on-error:\s*true/);
  assert.match(invalidationSection, /cache warming is blocked/);
  assert.match(invalidationSection, /365 days/);
  assert.match(invalidationSection, /needs\.cache-invalidate\.result == 'success'/);
  assert.match(invalidationSection, /-f scope=changed/);
  assert.match(invalidationSection, /-f request_budget=/);
  assert.match(invalidationSection, /-f byte_budget=/);
});
