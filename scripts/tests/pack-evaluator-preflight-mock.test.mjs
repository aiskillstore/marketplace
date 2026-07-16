import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createPackEvaluatorPreflightMock } from '../pack-evaluator-preflight-mock.mjs';

const LOCAL_TOKEN = 'local-preflight-token-longer-than-thirty-two-bytes';
let server;
let baseUrl;
let activities;

before(async () => {
  activities = [];
  server = createPackEvaluatorPreflightMock({
    localToken: LOCAL_TOKEN,
    onActivity: (activity) => activities.push(activity),
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  await new Promise((resolve) => server.close(resolve));
});

test('mock requires the local token and exposes only a local health check', async () => {
  assert.equal((await fetch(`${baseUrl}/healthz`)).status, 401);
  const response = await fetch(`${baseUrl}/healthz`, {
    headers: { authorization: `Bearer ${LOCAL_TOKEN}` },
  });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true });
});

test('mock serves protocol-complete Messages and Responses streams without retaining bodies', async () => {
  const headers = {
    authorization: `Bearer ${LOCAL_TOKEN}`,
    'content-type': 'application/json',
  };
  const messages = await fetch(`${baseUrl}/v1/messages`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: 'sonnet',
      stream: true,
      max_tokens: 16384,
      messages: [{ role: 'user', content: 'sensitive mock prompt' }],
    }),
  });
  assert.equal(messages.status, 200);
  assert.match(messages.headers.get('content-type'), /^text\/event-stream/);
  assert.match(await messages.text(), /message_stop/);

  const responses = await fetch(`${baseUrl}/v1/responses`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: 'gpt-5.5',
      stream: true,
      max_output_tokens: 4096,
      input: 'sensitive mock prompt',
    }),
  });
  assert.equal(responses.status, 200);
  const responseBody = await responses.text();
  assert.match(responseBody, /response\.output_text\.delta/);
  assert.match(responseBody, /response\.completed/);

  assert.deepEqual(
    activities.filter((activity) => activity.status === 200).map(({ path, model, stream, maxTokens }) => ({
      path,
      model,
      stream,
      maxTokens,
    })),
    [
      { path: '/v1/messages', model: 'sonnet', stream: true, maxTokens: 16384 },
      { path: '/v1/responses', model: 'gpt-5.5', stream: true, maxTokens: 4096 },
    ],
  );
  const serialized = JSON.stringify(activities);
  assert.doesNotMatch(serialized, /sensitive mock prompt|local-preflight-token|PACK_EVALUATOR_READY/);
});
