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

test('verify mode can return the strict Codex judge schema required by skill verify', async () => {
  const judgeText = JSON.stringify({
    used_skill: false,
    task_completed: true,
    env_blocked: false,
    score: 10,
    reason: 'executor path healthy',
    issues: [],
  });
  const verifyServer = createPackEvaluatorPreflightMock({
    localToken: LOCAL_TOKEN,
    responsesOutput: judgeText,
  });
  verifyServer.listen(0, '127.0.0.1');
  await once(verifyServer, 'listening');
  const url = `http://127.0.0.1:${verifyServer.address().port}`;
  try {
    const response = await fetch(`${url}/v1/responses`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${LOCAL_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({ model: 'gpt-5.5', stream: true, input: 'private judge prompt' }),
    });
    const body = await response.text();
    assert.equal(response.status, 200);
    assert.match(body, /response\.completed/);
    assert.match(body, /used_skill/);
    assert.match(body, /executor path healthy/);
  } finally {
    await new Promise((resolve) => verifyServer.close(resolve));
  }
});

test('Pack preflight mock requires two ordered Skill results before returning the marker', async () => {
  const skillIds = ['pack-executor-preflight-a', 'pack-executor-preflight-b'];
  const packActivities = [];
  const packServer = createPackEvaluatorPreflightMock({
    localToken: LOCAL_TOKEN,
    preflightSkillIds: skillIds,
    onActivity: (activity) => packActivities.push(activity),
  });
  packServer.listen(0, '127.0.0.1');
  await once(packServer, 'listening');
  const url = `http://127.0.0.1:${packServer.address().port}`;
  const headers = {
    authorization: `Bearer ${LOCAL_TOKEN}`,
    'content-type': 'application/json',
  };
  try {
    const first = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [{ role: 'user', content: 'private Pack task' }],
      }),
    });
    const firstBody = await first.text();
    assert.equal(first.status, 200);
    for (const skillId of skillIds) assert.match(firstBody, new RegExp(skillId));
    assert.match(firstBody, /toolu_pack_preflight_1/);
    assert.match(firstBody, /toolu_pack_preflight_2/);

    const second = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [{
          role: 'user',
          content: [
            { type: 'tool_result', tool_use_id: 'toolu_pack_preflight_1', content: 'private result' },
            { type: 'tool_result', tool_use_id: 'toolu_pack_preflight_2', content: 'private result' },
          ],
        }],
      }),
    });
    assert.equal(second.status, 200);
    assert.match(await second.text(), /PACK_EVALUATOR_READY/);

    const third = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [],
      }),
    });
    assert.equal(third.status, 400);
    assert.doesNotMatch(
      JSON.stringify(packActivities),
      /private Pack task|private result|local-preflight-token|PACK_EVALUATOR_READY/,
    );
  } finally {
    await new Promise((resolve) => packServer.close(resolve));
  }
});

test('Pack preflight permits one bounded bootstrap without advancing the Skill protocol', async () => {
  const rejectedActivities = [];
  const packServer = createPackEvaluatorPreflightMock({
    localToken: LOCAL_TOKEN,
    preflightSkillIds: ['pack-executor-preflight-a', 'pack-executor-preflight-b'],
    onActivity: (activity) => rejectedActivities.push(activity),
  });
  packServer.listen(0, '127.0.0.1');
  await once(packServer, 'listening');
  const url = `http://127.0.0.1:${packServer.address().port}`;
  try {
    const bootstrap = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${LOCAL_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [
          { name: 'Read' },
          { name: 'mcp__safe.tool-1' },
          { name: 'unsafe tool name', input_schema: { private: 'sensitive schema' } },
        ],
        messages: [{ role: 'user', content: 'private Pack task' }],
      }),
    });
    assert.equal(bootstrap.status, 200);
    assert.match(await bootstrap.text(), /message_stop/);
    assert.equal(rejectedActivities.at(-1)?.protocolStage, 'bootstrap');
    assert.deepEqual(rejectedActivities.at(-1)?.toolNames, ['Read', 'mcp__safe.tool-1']);

    const skillRequest = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${LOCAL_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [{ role: 'user', content: 'private Pack task' }],
      }),
    });
    assert.equal(skillRequest.status, 200);
    assert.match(await skillRequest.text(), /toolu_pack_preflight_2/);

    const toolResults = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${LOCAL_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [{
          role: 'user',
          content: [
            { type: 'tool_result', tool_use_id: 'toolu_pack_preflight_1', content: 'private result' },
            { type: 'tool_result', tool_use_id: 'toolu_pack_preflight_2', content: 'private result' },
          ],
        }],
      }),
    });
    assert.equal(toolResults.status, 200);
    assert.match(await toolResults.text(), /PACK_EVALUATOR_READY/);

    const overBudget = await fetch(`${url}/v1/messages`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${LOCAL_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonnet',
        stream: true,
        max_tokens: 16384,
        tools: [{ name: 'Skill' }],
        messages: [],
      }),
    });
    assert.equal(overBudget.status, 400);
    assert.doesNotMatch(
      JSON.stringify(rejectedActivities),
      /private Pack task|private result|sensitive schema|unsafe tool name|local-preflight-token|PACK_EVALUATOR_READY/,
    );
  } finally {
    await new Promise((resolve) => packServer.close(resolve));
  }
});
