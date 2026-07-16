import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer, request as httpRequest } from 'node:http';
import { once } from 'node:events';
import {
  classifyUpstreamErrorMessage,
  createPackEvaluatorProxy,
} from '../pack-evaluator-proxy.mjs';

const LOCAL_TOKEN = 'local-token-that-is-longer-than-thirty-two-bytes';
const UPSTREAM_KEY = 'upstream-secret-that-must-never-be-forwarded-back';
let upstream;
let proxy;
let upstreamUrl;
let proxyUrl;
let observed;
let activities;

before(async () => {
  upstream = createServer(async (request, response) => {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    observed = {
      method: request.method,
      url: request.url,
      authorization: request.headers.authorization,
      apiKey: request.headers['x-api-key'],
      body: Buffer.concat(chunks).toString('utf8'),
    };
    response.writeHead(200, { 'content-type': 'application/json', 'set-cookie': 'secret=bad' });
    response.end('{"ok":true}');
  });
  upstream.listen(0, '127.0.0.1');
  await once(upstream, 'listening');
  upstreamUrl = `http://127.0.0.1:${upstream.address().port}`;
  activities = [];

  proxy = createPackEvaluatorProxy({
    localToken: LOCAL_TOKEN,
    upstreamKey: UPSTREAM_KEY,
    upstreamBaseUrl: upstreamUrl,
    maxOutputTokens: 16384,
    onActivity: (activity) => activities.push(activity),
  });
  proxy.listen(0, '127.0.0.1');
  await once(proxy, 'listening');
  proxyUrl = `http://127.0.0.1:${proxy.address().port}`;
});

after(async () => {
  await Promise.all([
    new Promise((resolve) => proxy.close(resolve)),
    new Promise((resolve) => upstream.close(resolve)),
  ]);
});

test('requires the job-local token even for health checks', async () => {
  const activityCount = activities.length;
  assert.equal((await fetch(`${proxyUrl}/healthz`)).status, 401);
  assert.equal((await fetch(`${proxyUrl}/v1/messages`, { method: 'HEAD' })).status, 401);
  const response = await fetch(`${proxyUrl}/healthz`, {
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(response.status, 200);
  assert.equal(activities.length, activityCount, 'unauthenticated probes must not emit fatal activity');
});

test('allows only the explicit inference endpoint allowlist', async () => {
  const activityCount = activities.length;
  const response = await fetch(`${proxyUrl}/admin/api/keys`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(response.status, 403);
  const head = await fetch(`${proxyUrl}/v1/messages`, {
    method: 'HEAD',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(head.status, 403);
  assert.equal(activities.length, activityCount, 'HEAD and non-inference probes must not emit fatal activity');
});

test('replaces local credentials with the bounded upstream credential', async () => {
  const response = await fetch(`${proxyUrl}/v1/responses?trace=1`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${LOCAL_TOKEN}`,
      'x-api-key': LOCAL_TOKEN,
      'content-type': 'application/json',
    },
    body: JSON.stringify({ model: 'gpt-5.5', input: 'ok' }),
  });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true });
  assert.equal(observed.method, 'POST');
  assert.equal(observed.url, '/v1/responses?trace=1');
  assert.equal(observed.authorization, `Bearer ${UPSTREAM_KEY}`);
  assert.equal(observed.apiKey, undefined);
  assert.match(observed.body, /gpt-5\.5/);
  assert.equal(response.headers.has('set-cookie'), false);
  assert.equal(JSON.parse(observed.body).max_output_tokens, 16384);
  assert.deepEqual(
    activities.slice(-3).map((activity) => activity.phase),
    ['started', 'response', 'completed']
  );
  assert.deepEqual(
    {
      path: activities.at(-2).path,
      model: activities.at(-2).model,
      requestBytes: activities.at(-2).requestBytes,
      stream: activities.at(-2).stream,
      status: activities.at(-2).status,
    },
    {
      path: '/v1/responses',
      model: 'gpt-5.5',
      requestBytes: Buffer.byteLength(JSON.stringify({ model: 'gpt-5.5', input: 'ok' })),
      stream: false,
      status: 200,
    },
  );
});

test('records exact redacted upstream error diagnostics without response text or credentials', async () => {
  const redactedActivities = [];
  const secretMessage = 'invalid routing secret must not be persisted';
  let upstreamCalls = 0;
  const rejectingProxy = createPackEvaluatorProxy({
    localToken: LOCAL_TOKEN,
    upstreamKey: UPSTREAM_KEY,
    upstreamBaseUrl: upstreamUrl,
    fetchImpl: async () => {
      upstreamCalls += 1;
      return new Response(JSON.stringify({
        error: {
          type: 'invalid_request_error',
          code: 'model_not_allowed',
          param: 'model',
          message: secretMessage,
        },
      }), {
        status: 422,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req_123-safe',
        },
      });
    },
    onActivity: (activity) => redactedActivities.push(activity),
  });
  rejectingProxy.listen(0, '127.0.0.1');
  await once(rejectingProxy, 'listening');
  const url = `http://127.0.0.1:${rejectingProxy.address().port}`;
  const body = JSON.stringify({
    model: 'sonnet',
    max_tokens: 16,
    stream: true,
    messages: [{ role: 'user', content: 'sensitive prompt must not be logged' }],
  });
  const response = await fetch(`${url}/v1/messages?unlogged=query`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${LOCAL_TOKEN}`,
      'content-type': 'application/json',
    },
    body,
  });
  assert.equal(response.status, 422);
  const activity = redactedActivities.find((entry) => entry.phase === 'response');
  assert.deepEqual({
    path: activity.path,
    model: activity.model,
    requestBytes: activity.requestBytes,
    stream: activity.stream,
    status: activity.status,
    errorType: activity.errorType,
    errorCode: activity.errorCode,
    errorParam: activity.errorParam,
    errorCategory: activity.errorCategory,
    traceHeaders: activity.traceHeaders,
  }, {
    path: '/v1/messages',
    model: 'sonnet',
    requestBytes: Buffer.byteLength(body),
    stream: true,
    status: 422,
    errorType: 'invalid_request_error',
    errorCode: 'model_not_allowed',
    errorParam: 'model',
    errorCategory: 'other',
    traceHeaders: { 'x-request-id': 'req_123-safe' },
  });
  assert.match(activity.errorMessageSha256, /^[a-f0-9]{64}$/);
  const serialized = JSON.stringify(redactedActivities);
  assert.doesNotMatch(serialized, /invalid routing secret|sensitive prompt|local-token|upstream-secret|unlogged=query/);
  const circuitResponse = await fetch(`${url}/v1/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${LOCAL_TOKEN}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({ model: 'sonnet', max_tokens: 16, messages: [] }),
  });
  assert.equal(circuitResponse.status, 424);
  assert.equal(upstreamCalls, 1, 'a deterministic 4xx must open the circuit before another upstream call');
  assert.ok(redactedActivities.some((entry) => (
    entry.phase === 'circuit_open'
    && entry.status === 422
    && entry.originalRequestNumber === 1
    && entry.requestNumber === 2
  )));
  await new Promise((resolve) => rejectingProxy.close(resolve));
});

test('classifies upstream 400 causes into a fixed enum without retaining raw text', () => {
  const cases = [
    ['Model claude-x is unknown on lane paid-secret-token', 'unknown_model_or_lane'],
    ['Parameter reasoning_effort is not supported for this route', 'unsupported_parameter'],
    ['Authentication failed for api key private-token', 'authentication_failed'],
    ['Maximum context length exceeded by sensitive prompt', 'context_length_exceeded'],
    ['Malformed request body: invalid JSON after private-token', 'malformed_request'],
    ['opaque private-token routing failure', 'other'],
  ];
  const categories = cases.map(([message, expected]) => {
    const category = classifyUpstreamErrorMessage(message);
    assert.equal(category, expected);
    return category;
  });
  const serialized = JSON.stringify(categories);
  assert.doesNotMatch(serialized, /private-token|sensitive prompt|reasoning_effort|claude-x/);
});

test('rejects models and token requests outside the evaluator budget', async () => {
  const activityStart = activities.length;
  const forbiddenModel = await fetch(`${proxyUrl}/v1/responses`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'gpt-unbounded', input: 'no' }),
  });
  assert.equal(forbiddenModel.status, 403);
  assert.match((await forbiddenModel.json()).error, /model is not allowed/);

  const excessiveTokens = await fetch(`${proxyUrl}/v1/messages`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'sonnet', max_tokens: 16385, messages: [] }),
  });
  assert.equal(excessiveTokens.status, 400);
  assert.match((await excessiveTokens.json()).error, /max_tokens/);

  const malformedBody = await fetch(`${proxyUrl}/v1/messages`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: '{"sensitive request text":',
  });
  assert.equal(malformedBody.status, 400);

  const policyActivities = activities.slice(activityStart);
  assert.deepEqual(
    policyActivities.map(({ phase, path, status, errorCategory }) => ({
      phase,
      path,
      status,
      errorCategory,
    })),
    [
      {
        phase: 'response',
        path: '/v1/responses',
        status: 403,
        errorCategory: 'model_not_allowed',
      },
      {
        phase: 'response',
        path: '/v1/messages',
        status: 400,
        errorCategory: 'invalid_output_token_limit',
      },
      {
        phase: 'response',
        path: '/v1/messages',
        status: 400,
        errorCategory: 'malformed_request',
      },
    ],
  );
  for (const activity of policyActivities) {
    assert.deepEqual(
      Object.keys(activity).sort(),
      ['errorCategory', 'path', 'phase', 'requestNumber', 'status'],
    );
  }
  assert.deepEqual(
    policyActivities.map((activity) => activity.requestNumber),
    [
      policyActivities[0].requestNumber,
      policyActivities[0].requestNumber + 1,
      policyActivities[0].requestNumber + 2,
    ],
    'consecutive local policy rejections must receive distinct monotonic identifiers',
  );
  assert.doesNotMatch(
    JSON.stringify(policyActivities),
    /gpt-unbounded|sensitive request text|local-token|upstream-secret/,
  );

  const authorized = await fetch(`${proxyUrl}/v1/responses`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'gpt-5.5', input: 'allowed after policy rejection' }),
  });
  assert.equal(authorized.status, 200);
  const nextStarted = activities.slice(activityStart + policyActivities.length)
    .find((activity) => activity.phase === 'started');
  assert.equal(nextStarted.requestNumber, policyActivities.at(-1).requestNumber + 1);
});

test('policy rejections use monotonic activity ids without spending the forwarding budget', async () => {
  const recorded = [];
  let upstreamCalls = 0;
  const bounded = createPackEvaluatorProxy({
    localToken: LOCAL_TOKEN,
    upstreamKey: UPSTREAM_KEY,
    upstreamBaseUrl: upstreamUrl,
    maxRequests: 1,
    maxOutputTokens: 16384,
    fetchImpl: async () => {
      upstreamCalls += 1;
      return new Response('{"ok":true}', {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });
    },
    onActivity: (activity) => recorded.push(activity),
  });
  bounded.listen(0, '127.0.0.1');
  await once(bounded, 'listening');
  const url = `http://127.0.0.1:${bounded.address().port}`;
  const headers = { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' };

  assert.equal((await fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model: 'not-allowed', input: 'one' }),
  })).status, 403);
  assert.equal((await fetch(`${url}/v1/messages`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model: 'sonnet', max_tokens: 16385, messages: [] }),
  })).status, 400);
  assert.equal((await fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model: 'gpt-5.5', input: 'forward exactly once' }),
  })).status, 200);
  assert.equal((await fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model: 'gpt-5.5', input: 'budget exhausted' }),
  })).status, 429);

  assert.equal(upstreamCalls, 1);
  assert.deepEqual(
    recorded.map(({ phase, requestNumber }) => ({ phase, requestNumber })),
    [
      { phase: 'response', requestNumber: 1 },
      { phase: 'response', requestNumber: 2 },
      { phase: 'started', requestNumber: 3 },
      { phase: 'response', requestNumber: 3 },
      { phase: 'completed', requestNumber: 3 },
    ],
  );
  await new Promise((resolve) => bounded.close(resolve));
});

test('enforces request, concurrency, and TTL limits', async () => {
  let release;
  const blockedFetch = () => new Promise((resolve) => { release = resolve; });
  const limited = createPackEvaluatorProxy({
    localToken: LOCAL_TOKEN,
    upstreamKey: UPSTREAM_KEY,
    upstreamBaseUrl: upstreamUrl,
    fetchImpl: blockedFetch,
    maxRequests: 1,
    maxConcurrent: 1,
    ttlMs: 25,
  });
  limited.listen(0, '127.0.0.1');
  await once(limited, 'listening');
  const url = `http://127.0.0.1:${limited.address().port}`;
  const first = fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'gpt-5.5', input: 'one' }),
  });
  await new Promise((resolve) => setTimeout(resolve, 10));
  const second = await fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'gpt-5.5', input: 'two' }),
  });
  assert.equal(second.status, 429);
  release(new Response('{"ok":true}', { status: 200, headers: { 'content-type': 'application/json' } }));
  assert.equal((await first).status, 200);
  await new Promise((resolve) => setTimeout(resolve, 20));
  const expired = await fetch(`${url}/v1/responses`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}`, 'content-type': 'application/json' },
    body: JSON.stringify({ model: 'gpt-5.5', input: 'late' }),
  });
  assert.equal(expired.status, 403);
  await new Promise((resolve) => limited.close(resolve));
});

test('aborts an in-flight upstream request when the evaluator disconnects', async () => {
  let markStarted;
  let markAborted;
  const started = new Promise((resolve) => { markStarted = resolve; });
  const aborted = new Promise((resolve) => { markAborted = resolve; });
  const hangingFetch = (_url, init) => new Promise((_resolve, reject) => {
    markStarted();
    init.signal.addEventListener('abort', () => {
      markAborted();
      reject(new Error('aborted by downstream disconnect'));
    }, { once: true });
  });
  const abortingProxy = createPackEvaluatorProxy({
    localToken: LOCAL_TOKEN,
    upstreamKey: UPSTREAM_KEY,
    upstreamBaseUrl: upstreamUrl,
    fetchImpl: hangingFetch,
    requestTimeoutMs: 60_000,
  });
  abortingProxy.listen(0, '127.0.0.1');
  await once(abortingProxy, 'listening');
  const request = httpRequest({
    host: '127.0.0.1',
    port: abortingProxy.address().port,
    path: '/v1/responses',
    method: 'POST',
    headers: {
      Authorization: `Bearer ${LOCAL_TOKEN}`,
      'content-type': 'application/json',
    },
  });
  request.on('error', () => {});
  request.end(JSON.stringify({ model: 'gpt-5.5', input: 'hang' }));
  await started;
  request.destroy();
  await aborted;
  await new Promise((resolve) => abortingProxy.close(resolve));
});
