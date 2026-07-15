import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { createPackEvaluatorProxy } from '../pack-evaluator-proxy.mjs';

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
  assert.equal((await fetch(`${proxyUrl}/healthz`)).status, 401);
  const response = await fetch(`${proxyUrl}/healthz`, {
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(response.status, 200);
});

test('allows only the explicit inference endpoint allowlist', async () => {
  const response = await fetch(`${proxyUrl}/admin/api/keys`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(response.status, 403);
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
  assert.equal(JSON.parse(observed.body).max_output_tokens, 65536);
  assert.deepEqual(activities.slice(-2).map((activity) => activity.phase), ['started', 'completed']);
});

test('rejects models and token requests outside the evaluator budget', async () => {
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
    body: JSON.stringify({ model: 'sonnet', max_tokens: 65537, messages: [] }),
  });
  assert.equal(excessiveTokens.status, 400);
  assert.match((await excessiveTokens.json()).error, /max_tokens/);
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
