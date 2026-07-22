import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  calculateWorstCaseRequests,
  MAX_ENDPOINT_ATTEMPTS,
  MAX_ERROR_RESPONSE_BYTES,
  MAX_EDGE_TRANSFORM_OVERHEAD,
  normalizeSlugs,
  normalizeWarmTargets,
  parseWarmTargets,
  runWarm,
  WarmError,
} from '../warm-skill-cache.mjs';

const BUILD_A = `${'a'.repeat(40)}.deploy-a`;
const BUILD_B = `${'b'.repeat(40)}.deploy-b`;
const CACHE_KEY_A = '00000000aaaa';
const CACHE_VERSION_A = 'cache-version-a';
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');

function response({
  status = 200,
  build = BUILD_A,
  apiCache,
  pageCache,
  zipCache,
  cacheWrite,
  cacheKey = CACHE_KEY_A,
  cacheVersion = CACHE_VERSION_A,
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
  const kvCache = apiCache || pageCache;
  if (kvCache) {
    if (cacheWrite !== null) {
      headers.set('x-kv-write', cacheWrite || (kvCache === 'MISS' ? 'STORED' : 'SKIPPED'));
    }
    if (cacheKey !== null) headers.set('x-kv-key', cacheKey);
    if (cacheVersion !== null) headers.set('x-kv-version', cacheVersion);
  }
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
  status = 200,
  build = BUILD_A,
  apiCache,
  pageCache,
  cacheWrite,
  cacheKey = CACHE_KEY_A,
  cacheVersion = CACHE_VERSION_A,
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
  const kvCache = apiCache || pageCache;
  if (kvCache) {
    if (cacheWrite !== null) {
      headers.set('x-kv-write', cacheWrite || (kvCache === 'MISS' ? 'STORED' : 'SKIPPED'));
    }
    if (cacheKey !== null) headers.set('x-kv-key', cacheKey);
    if (cacheVersion !== null) headers.set('x-kv-version', cacheVersion);
  }
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
  return new Response(body, { status, headers });
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

test('normalizes exact Skill and Pack locale targets and calculates a deterministic aggregate cap', () => {
  const raw = [
    { resource: 'packs', slug: 'beta-pack', locale: 'ja' },
    { resource: 'skills', slug: 'alpha-skill', locale: 'fr' },
    { resource: 'skills', slug: 'alpha-skill', locale: 'fr' },
  ];
  const targets = normalizeWarmTargets(raw);
  assert.deepEqual(targets, [
    { resource: 'packs', slug: 'beta-pack', locale: 'ja' },
    { resource: 'skills', slug: 'alpha-skill', locale: 'fr' },
  ]);
  assert.deepEqual(
    parseWarmTargets(targets.map((target) => JSON.stringify(target)).join('\n')),
    targets
  );
  assert.equal(MAX_ENDPOINT_ATTEMPTS, 16);
  assert.equal(calculateWorstCaseRequests(targets, { maxAttempts: 3 }), 14);
  assert.equal(calculateWorstCaseRequests(targets, { maxAttempts: 3, warmZip: true }), 19);
  assert.throws(
    () => normalizeWarmTargets([{ resource: 'workflows', slug: 'bad', locale: 'en' }]),
    /unsupported resource/i
  );
  assert.throws(
    () => normalizeWarmTargets([{ resource: 'skills', slug: 'bad', locale: 'xx' }]),
    /unsupported locale/i
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

test('accepts bounded HTML edge transforms and records declared, actual, and edgeDelta', async () => {
  const records = [];
  const originHtml = '<html>cached</html>';
  const edgeDelta = 1_157;
  const transformedHtml = `${originHtml}${'x'.repeat(edgeDelta)}`;
  const declared = new TextEncoder().encode(originHtml).byteLength;
  const fetchImpl = async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: transformedHtml,
      omitLength: true,
      responseBytes: declared,
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl, records));

  assert.equal(summary.success, true);
  assert.equal(summary.budget.reservedBytes, 0);
  const pageRecords = records.filter((record) => record.kind === 'page');
  assert.equal(pageRecords.length, 3);
  for (const record of pageRecords) {
    assert.equal(record.declared, declared);
    assert.equal(record.actual, declared + edgeDelta);
    assert.equal(record.edgeDelta, edgeDelta);
    assert.equal(record.bytes, record.actual);
  }
  assert.equal(
    summary.budget.bytes,
    records.reduce((total, record) => total + record.actual, 0),
    'unused edge reservations must be released instead of counted as downloaded bytes'
  );
});

test('accepts HTML at the exact edge transform ceiling', async () => {
  const fetchImpl = async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: `x${'y'.repeat(MAX_EDGE_TRANSFORM_OVERHEAD)}`,
      omitLength: true,
      responseBytes: 1,
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, true);
  assert.equal(summary.budget.reservedBytes, 0);
});

test('accepts transformed HTML when Content-Length is within the origin allowance and exact', async () => {
  const records = [];
  const edgeDelta = 1_157;
  const actual = 1 + edgeDelta;
  const fetchImpl = async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: `x${'y'.repeat(edgeDelta)}`,
      contentLength: actual,
      responseBytes: 1,
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl, records));

  assert.equal(summary.success, true);
  const page = records.find((record) => record.kind === 'page');
  assert.equal(page?.declared, 1);
  assert.equal(page?.actual, actual);
  assert.equal(page?.edgeDelta, edgeDelta);
});

test('rejects HTML Content-Length below the origin declaration', async () => {
  const summary = await runWarm(baseOptions(async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: 'x',
      contentLength: 0,
      responseBytes: 1,
    });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /must be between origin declared 1/i);
});

test('rejects HTML Content-Length above the edge transform allowance', async () => {
  const contentLength = 1 + MAX_EDGE_TRANSFORM_OVERHEAD + 1;
  const summary = await runWarm(baseOptions(async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: 'x'.repeat(contentLength),
      contentLength,
      responseBytes: 1,
    });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /must be between origin declared 1/i);
});

test('requires actual HTML bytes to exactly match an accepted Content-Length', async () => {
  const records = [];
  const summary = await runWarm(baseOptions(async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: 'abc',
      contentLength: 2,
      responseBytes: 1,
    });
  }, records));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /ended at 3 bytes; expected 2/i);
  const failure = records.find((record) => record.kind === 'page' && record.error);
  assert.equal(failure?.declared, 1);
  assert.equal(failure?.actual, 3);
  assert.equal(failure?.edgeDelta, 2);
  assert.equal(failure?.cache, 'HIT');
  assert.equal(failure?.cacheWrite, 'SKIPPED');
  assert.equal(failure?.cacheKey, CACHE_KEY_A);
  assert.equal(failure?.cacheVersion, CACHE_VERSION_A);
  assert.equal(failure?.buildToken, BUILD_A);
});

test('rejects HTML shorter than declared and records the negative edge delta', async () => {
  const records = [];
  const fetchImpl = async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: '',
      omitLength: true,
      responseBytes: 1,
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl, records));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /expected at least its declared 1 bytes/i);
  const failure = records.find((record) => record.kind === 'page' && record.error);
  assert.equal(failure?.declared, 1);
  assert.equal(failure?.actual, 0);
  assert.equal(failure?.edgeDelta, -1);
});

test('rejects HTML that exceeds the fixed edge transform allowance', async () => {
  const records = [];
  const actual = MAX_EDGE_TRANSFORM_OVERHEAD + 2;
  const fetchImpl = async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({
      pageCache: 'HIT',
      body: 'x'.repeat(actual),
      omitLength: true,
      responseBytes: 1,
    });
  };

  const summary = await runWarm(baseOptions(fetchImpl, records));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /edge transform allowance/i);
  const failure = records.find((record) => record.kind === 'page' && record.error);
  assert.equal(failure?.declared, 1);
  assert.equal(failure?.actual, actual);
  assert.equal(failure?.edgeDelta, MAX_EDGE_TRANSFORM_OVERHEAD + 1);
});

test('continues to require exact byte equality for API responses', async () => {
  const records = [];
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return response({ apiCache: 'HIT', body: 'abc', contentLength: 2 });
  }, records));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /exceeded its declared 2 bytes/i);
  const failure = records.find((record) => record.kind === 'api' && record.error);
  assert.equal(failure?.declared, 2);
  assert.equal(failure?.actual, 3);
  assert.equal(failure?.edgeDelta, 1);
});

test('continues to require exact byte equality for build probes', async () => {
  const records = [];
  const body = JSON.stringify({ version: BUILD_A });
  const summary = await runWarm(baseOptions(async () => response({
    build: BUILD_A,
    body,
    contentLength: new TextEncoder().encode(body).byteLength - 1,
  }), records));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /exceeded its declared/i);
  const failure = records.find((record) => record.kind === 'build' && record.error);
  assert.equal(failure?.actual, failure.declared + 1);
  assert.equal(failure?.edgeDelta, 1);
});

test('continues to require exact byte equality for ZIP responses', async () => {
  const records = [];
  const summary = await runWarm(baseOptions(async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.endsWith('/download')) {
      return response({ zipCache: 'HIT', body: 'abc', contentLength: 2 });
    }
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    return response({ pageCache: 'HIT', body: '<html></html>' });
  }, records, { warmZip: true }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /exceeded its declared 2 bytes/i);
  const failure = records.find((record) => record.kind === 'zip' && record.error);
  assert.equal(failure?.declared, 2);
  assert.equal(failure?.actual, 3);
  assert.equal(failure?.edgeDelta, 1);
});

test('atomically reserves the HTML declaration plus edge allowance', async () => {
  const cancelled = [];
  let pageCalls = 0;
  const versionBytes = versionBodyBytes();
  const apiBytes = 2 * 2 * 3;
  const summary = await runWarm(baseOptions(async (url) => {
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/skills/')) return response({ apiCache: 'HIT' });
    const index = pageCalls++;
    return streamingResponse({
      pageCache: 'HIT',
      responseBytes: 60,
      pending: true,
      onCancel: () => { cancelled[index] = true; },
    });
  }, [], {
    slugs: ['alpha', 'beta'],
    concurrency: 2,
    byteBudget: versionBytes + apiBytes + 60 + MAX_EDGE_TRANSFORM_OVERHEAD + 50,
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /byte budget/i);
  assert.equal(summary.budget.reservedBytes, 0);
  assert.deepEqual(cancelled, [true, true]);
  assert.equal(pageCalls, 2);
});

test('verifies invalidated API and HTML as MISS+STORED then two HIT+SKIPPED responses', async () => {
  const calls = [];
  const records = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS', body: '{"data":{}}' }) },
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

  const summary = await runWarm(baseOptions(fetchImpl, records, {
    mode: 'warm',
    scope: 'changed',
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(summary.completedEndpoints, { api: 1, page: 1, zip: 0 });
  assert.equal(summary.failedEndpoints, 0);
  assert.equal(summary.skippedEndpoints, 0);
  assert.equal(summary.budget.requests, 8);
  assert.match(calls[1].url, /\/api\/skills\/alpha/);
  assert.match(calls[4].url, /\/skills\/alpha/);
  assert.equal(new Headers(calls[1].init.headers).get('cache-control'), 'no-cache');
  const innerRecord = records.find((record) => record.phase === 'inner-cache');
  assert.equal(innerRecord?.colo, 'SJC');
  for (const field of [
    'url',
    'attempt',
    'status',
    'cache',
    'cacheWrite',
    'cacheKey',
    'cacheVersion',
    'bytes',
    'declared',
    'actual',
    'edgeDelta',
    'cfRay',
    'colo',
  ]) {
    assert.equal(Object.hasOwn(innerRecord, field), true, `JSONL evidence must include ${field}`);
  }
  assert.deepEqual(
    records
      .filter((record) => record.kind === 'api')
      .map((record) => [record.cache, record.cacheWrite]),
    [['MISS', 'STORED'], ['HIT', 'SKIPPED'], ['HIT', 'SKIPPED']]
  );
  assert.deepEqual(
    records
      .filter((record) => record.kind === 'page')
      .map((record) => [record.cache, record.cacheWrite]),
    [['MISS', 'STORED'], ['HIT', 'SKIPPED'], ['HIT', 'SKIPPED']]
  );
  for (const kind of ['api', 'page']) {
    const chain = records.filter((record) => record.kind === kind);
    assert.deepEqual([...new Set(chain.map((record) => record.cacheKey))], [CACHE_KEY_A]);
    assert.deepEqual([...new Set(chain.map((record) => record.cacheVersion))], [CACHE_VERSION_A]);
    assert.deepEqual([...new Set(chain.map((record) => record.buildToken))], [BUILD_A]);
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

test('changed cache retries old HIT/STALE without pinning identity before fresh MISS', async () => {
  const calls = [];
  const records = [];
  const oldKey = '00000000old0';
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'HIT', cacheKey: oldKey }) },
    { response: response({ apiCache: 'STALE', cacheKey: oldKey }) },
    { response: response({ apiCache: 'MISS', cacheKey: CACHE_KEY_A }) },
    { response: response({ apiCache: 'HIT', cacheKey: CACHE_KEY_A }) },
    { response: response({ apiCache: 'HIT', cacheKey: CACHE_KEY_A }) },
    { response: response({ pageCache: 'MISS', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, records, {
    mode: 'warm',
    scope: 'changed',
    maxAttempts: 5,
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(
    records.filter((record) => record.kind === 'api').map((record) => [record.cache, record.cacheWrite]),
    [
      ['HIT', 'SKIPPED'],
      ['STALE', 'SKIPPED'],
      ['MISS', 'STORED'],
      ['HIT', 'SKIPPED'],
      ['HIT', 'SKIPPED'],
    ]
  );
  assert.equal(calls.length, 10);
});

test('rejects an invalidated MISS that did not durably store', async () => {
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return response({ apiCache: 'MISS', cacheWrite: 'SKIPPED' });
  }, [], { mode: 'warm', scope: 'changed' }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /fresh MISS\+STORED/i);
});

test('fails closed when KV key or version evidence is missing', async () => {
  const summary = await runWarm(baseOptions(async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return response({ apiCache: 'MISS', cacheKey: null });
  }, [], { mode: 'warm', scope: 'changed' }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /did not expose x-kv-key and x-kv-version/i);
});

test('fails when cache key or version changes across the verification chain', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS' }) },
    {
      response: response({
        apiCache: 'HIT',
        cacheKey: '00000000bbbb',
        cacheVersion: 'cache-version-b',
      }),
    },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    mode: 'warm',
    scope: 'changed',
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /changed cache identity/i);
  assert.equal(calls.length, 3);
});

test('fails a persistent MISS and does not start HTML warming', async () => {
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'MISS' }) },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl));

  assert.equal(summary.success, false);
  assert.equal(summary.completedEndpoints.api, 0);
  assert.equal(summary.completedEndpoints.page, 0);
  assert.equal(summary.failedEndpoints, 1);
  assert.equal(summary.skippedEndpoints, 1);
  assert.match(summary.failures.join('\n'), /attempt deterministic cap/i);
  assert.equal(calls.some((call) => new URL(call.url).pathname === '/skills/alpha'), false);
});

test('requires two consecutive HITs after the newest fresh MISS', async () => {
  const calls = [];
  const records = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'MISS' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ pageCache: 'MISS', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, records, {
    mode: 'warm',
    scope: 'changed',
    maxAttempts: 5,
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(
    records.filter((record) => record.kind === 'api').map((record) => record.cache),
    ['MISS', 'HIT', 'MISS', 'HIT', 'HIT']
  );
});

test('retries headerless edge errors before strict application header validation', async () => {
  const calls = [];
  const records = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    { response: new Response('busy', { status: 429 }) },
    { response: new Response('unavailable', { status: 503 }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, records, {
    maxAttempts: 5,
    mode: 'warm',
    scope: 'high-traffic',
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(records.filter((record) => record.kind === 'api').map((record) => record.status), [429, 503, 200, 200, 200]);
  assert.equal(summary.budget.bytes >= versionBodyBytes() + 15, true);
});

test('cancels oversized error responses without applying the strict app byte contract', async () => {
  let cancelled = false;
  const calls = [];
  const fetchImpl = sequencedFetch([
    { response: versionResponse() },
    {
      response: streamingResponse({
        status: 503,
        contentLength: MAX_ERROR_RESPONSE_BYTES + 1,
        pending: true,
        onCancel: () => { cancelled = true; },
      }),
    },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ apiCache: 'HIT' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: response({ pageCache: 'HIT', body: '<html></html>' }) },
    { response: versionResponse() },
  ], calls);

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    maxAttempts: 4,
    mode: 'warm',
    scope: 'high-traffic',
  }));

  assert.equal(summary.success, true);
  assert.equal(cancelled, true);
  assert.equal(summary.budget.reservedBytes, 0);
});

test('reports a headerless non-retryable response by HTTP status without retrying it', async () => {
  let calls = 0;
  let endpointCalls = 0;
  const summary = await runWarm(baseOptions(async (url) => {
    calls++;
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    endpointCalls++;
    return new Response('not found', { status: 404 });
  }));

  assert.equal(summary.success, false);
  assert.match(summary.failures.join('\n'), /HTTP 404/i);
  assert.doesNotMatch(summary.failures.join('\n'), /Content-Length|build token/i);
  assert.equal(endpointCalls, 1, 'non-retryable endpoint must be requested exactly once');
  assert.equal(calls, 3, 'start and end build probes still bracket the failed run');
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

  const summary = await runWarm(baseOptions(fetchImpl, records, {
    maxAttempts: 5,
    mode: 'warm',
    scope: 'high-traffic',
  }));

  assert.equal(summary.success, true);
  assert.deepEqual(
    records.filter((record) => record.kind === 'api').map((record) => record.status),
    [429, 503, 200, 200, 200]
  );
  assert.deepEqual(
    records
      .filter((record) => record.kind === 'api' && record.status === 200)
      .map((record) => [record.cache, record.cacheWrite]),
    [['HIT', 'SKIPPED'], ['HIT', 'SKIPPED'], ['HIT', 'SKIPPED']]
  );
  assert.equal(summary.budget.requests, 10);
});

test('never exceeds the hard 120 second deadline for one endpoint', async () => {
  let clock = 0;
  const fetchImpl = async (url) => {
    if (new URL(url).pathname === '/_app/version.json') return versionResponse();
    return response({ apiCache: 'STALE' });
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
  assert.deepEqual(summary.plannedEndpoints, { api: 4, page: 4, zip: 0 });
  assert.deepEqual(summary.completedEndpoints, { api: 4, page: 4, zip: 0 });
  assert.equal(summary.budget.requests, 26);
  assert.equal(summary.failedEndpoints, 0);
  assert.equal(summary.skippedEndpoints, 0);
  assert.equal(calls.length, 26);
});

test('warms exact Skill and Pack targets with locale-specific API and page URLs in one budget', async () => {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url, init });
    const pathname = new URL(url).pathname;
    if (pathname === '/_app/version.json') return versionResponse();
    if (pathname.startsWith('/api/')) return response({ apiCache: 'HIT' });
    return response({ pageCache: 'HIT', body: '<html></html>' });
  };
  const targets = [
    { resource: 'skills', slug: 'alpha', locale: 'fr' },
    { resource: 'packs', slug: 'beta-pack', locale: 'ja' },
  ];

  const summary = await runWarm(baseOptions(fetchImpl, [], {
    slugs: undefined,
    targets,
    locales: undefined,
    requestBudget: calculateWorstCaseRequests(targets, { maxAttempts: 3 }),
  }));

  assert.equal(summary.success, true);
  assert.equal(summary.targets, 2);
  assert.deepEqual(summary.resources, { skills: 1, packs: 1 });
  assert.deepEqual(summary.plannedEndpoints, { api: 2, page: 2, zip: 0 });
  assert.equal(summary.budget.requests, 14);
  const requested = calls.map((call) => call.url);
  assert.equal(requested.some((url) => url.includes('/api/skills/alpha') && url.includes('lang=fr')), true);
  assert.equal(requested.some((url) => url.includes('/fr/skills/alpha')), true);
  assert.equal(requested.some((url) => url.includes('/api/packs/beta-pack') && url.includes('lang=ja')), true);
  assert.equal(requested.some((url) => url.includes('/ja/packs/beta-pack')), true);
});

test('workflow checks out scripts, requires bounded skill scope, and has no retired content branches', () => {
  const workflow = readFileSync(resolve(REPO_ROOT, '.github/workflows/warm-cache.yml'), 'utf8');
  const invalidateAction = readFileSync(resolve(REPO_ROOT, '.github/actions/invalidate-cache/action.yml'), 'utf8');

  assert.match(workflow, /sparse-checkout: \|\n\s+\.github\/actions\n\s+scripts/);
  assert.doesNotMatch(workflow, /full-catalog|approve_full_catalog|SUPABASE_SERVICE_KEY/);
  assert.match(workflow, /request_budget/);
  assert.match(workflow, /byte_budget/);
  assert.match(workflow, /CONCURRENCY: 4/);
  assert.match(workflow, /timeout-minutes: 120/);
  assert.match(workflow, /MAX_FORCE_INVALIDATION_SLUGS: 25/);
  assert.match(workflow, /INVALIDATE_BATCH_SIZE: 1/);
  assert.match(workflow, /default: '128'/);
  assert.match(workflow, /default: '20971520'/);
  assert.match(workflow, /concurrency must be a positive integer no greater than 4/);
  assert.match(workflow, /request_budget must be an integer between 1 and 128/);
  assert.match(workflow, /byte_budget must be an integer between 1 and 33554432/);
  assert.match(workflow, /CACHE_WRITE_HEADER: x-kv-write/);
  assert.match(workflow, /CACHE_KEY_HEADER: x-kv-key/);
  assert.match(workflow, /CACHE_VERSION_HEADER: x-kv-version/);
  assert.match(workflow, /Warm scope is empty/);
  assert.match(workflow, /Resolved scope needs at least \$MINIMUM_REQUESTS requests/);
  assert.match(workflow, /batch-size: \$\{\{ env\.INVALIDATE_BATCH_SIZE \}\}[\s\S]*concurrency: '1'[\s\S]*invalidate-artifacts: 'false'[\s\S]*invalidate-dependent-packs: 'false'/);
  assert.match(workflow, /node scripts\/warm-skill-cache\.mjs/);
  assert.doesNotMatch(workflow, /Warm workflows cache|Warm releases cache|type=skills/);
  assert.doesNotMatch(invalidateAction, /packs\/workflows/);
  assert.match(invalidateAction, /skills\|packs\|plugins\|releases/);
});

test('workflow rejects oversized and underbudget force invalidation before the invalidation step', () => {
  const workflow = readFileSync(resolve(REPO_ROOT, '.github/workflows/warm-cache.yml'), 'utf8');
  const runMarker = '        run: |\n';
  const stepStart = workflow.indexOf('      - name: Resolve and validate warm scope');
  const runStart = workflow.indexOf(runMarker, stepStart) + runMarker.length;
  const runEnd = workflow.indexOf('\n      - name: Invalidate selected skill caches', runStart);
  assert.ok(stepStart >= 0 && runStart >= runMarker.length && runEnd > runStart);

  const script = workflow
    .slice(runStart, runEnd)
    .split('\n')
    .map((line) => line.replace(/^ {10}/, ''))
    .join('\n');
  const workDir = mkdtempSync(resolve(tmpdir(), 'warm-cache-scope-'));

  try {
    const runScope = (overrides = {}) => spawnSync('bash', ['-c', script], {
        encoding: 'utf8',
        env: {
        ...process.env,
        RUNNER_TEMP: workDir,
        GITHUB_OUTPUT: resolve(workDir, 'github-output'),
        SUPPORTED_LOCALES: 'en zh-hans zh-hant ja ko de fr es pt ru ar',
        CONCURRENCY: '4',
        MAX_FORCE_INVALIDATION_SLUGS: '25',
        SCOPE: 'changed',
        MODE: 'force',
        INPUT_SLUGS: 'skill-1',
        INPUT_LOCALES: 'en',
        SOURCE_RUN_ID: '',
        APPROVE_FULL_CATALOG: 'false',
        REQUEST_BUDGET: '128',
        BYTE_BUDGET: '20971520',
        WARM_ZIP: 'false',
        SUPABASE_URL: '',
        SUPABASE_SERVICE_KEY: '',
        ...overrides,
      },
    });

    const oversized = runScope({
      INPUT_SLUGS: Array.from({ length: 26 }, (_, index) => `skill-${index + 1}`).join('\n'),
    });
    assert.equal(oversized.status, 1);
    assert.match(`${oversized.stdout}\n${oversized.stderr}`, /Force invalidation is limited to 25 skills per run; resolved 26/);

    const underbudget = runScope({
      INPUT_SLUGS: Array.from({ length: 22 }, (_, index) => `skill-${index + 1}`).join('\n'),
    });
    assert.equal(underbudget.status, 1);
    assert.match(`${underbudget.stdout}\n${underbudget.stderr}`, /needs at least 134 requests.*request_budget=128/);

    const exactBudget = runScope({
      INPUT_SLUGS: Array.from({ length: 21 }, (_, index) => `skill-${index + 1}`).join('\n'),
    });
    assert.equal(exactBudget.status, 0, `${exactBudget.stdout}\n${exactBudget.stderr}`);

    const expandedByteBudget = runScope({ BYTE_BUDGET: '33554432' });
    assert.equal(expandedByteBudget.status, 0, `${expandedByteBudget.stdout}\n${expandedByteBudget.stderr}`);

    const oversizedByteBudget = runScope({ BYTE_BUDGET: '33554433' });
    assert.equal(oversizedByteBudget.status, 1);
    assert.match(
      `${oversizedByteBudget.stdout}\n${oversizedByteBudget.stderr}`,
      /byte_budget must be an integer between 1 and 33554432/
    );

    const forceZip = runScope({ WARM_ZIP: 'true' });
    assert.equal(forceZip.status, 1);
    assert.match(`${forceZip.stdout}\n${forceZip.stderr}`, /force mode does not invalidate immutable ZIP artifacts/);
  } finally {
    rmSync(workDir, { recursive: true, force: true });
  }
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
  assert.match(invalidationSection, /finalize-english-cache:/);
  assert.match(invalidationSection, /finalize-translation-cache\.mjs/);
  assert.match(invalidationSection, /--request-budget 5000/);
  assert.match(invalidationSection, /--byte-budget 536870912/);
  assert.doesNotMatch(invalidationSection, /gh workflow run warm-cache\.yml/);
});
