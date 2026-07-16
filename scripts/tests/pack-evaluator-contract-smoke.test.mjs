import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { runContractSmoke } from '../pack-evaluator-contract-smoke.mjs';

function sse(events) {
  return `${events.map(({ type, data }) => (
    `event: ${type}\ndata: ${JSON.stringify({ type, ...data })}`
  )).join('\n\n')}\n\n`;
}

function messagesEvents(text = 'PACK_EVALUATOR_READY', { completed = true } = {}) {
  return [
    { type: 'message_start', data: { message: { id: 'msg_safe' } } },
    { type: 'content_block_delta', data: { delta: { type: 'text_delta', text } } },
    ...(completed ? [{ type: 'message_stop', data: {} }] : []),
  ];
}

function responsesEvents(text = 'PACK_EVALUATOR_READY', { completed = true } = {}) {
  return [
    { type: 'response.created', data: { response: { id: 'resp_safe' } } },
    { type: 'response.output_text.delta', data: { delta: text } },
    ...(completed ? [{ type: 'response.completed', data: { response: { id: 'resp_safe' } } }] : []),
  ];
}

function contractSse(url, { messagesText, responsesText, responsesCompleted = true } = {}) {
  return String(url).endsWith('/v1/messages')
    ? sse(messagesEvents(messagesText))
    : sse(responsesEvents(responsesText, { completed: responsesCompleted }));
}

test('contract smoke makes one bounded request for Messages and Responses before evaluation', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  const calls = [];
  const diagnostics = await runContractSmoke({
    proxyUrl: 'http://127.0.0.1:18765',
    token: 'job-local-secret',
    diagnosticsFile,
    fetchImpl: async (url, init) => {
      calls.push({ url: String(url), init });
      const response = contractSse(url);
      return new Response(response, {
        status: 200,
        headers: { 'content-type': 'text/event-stream' },
      });
    },
  });
  assert.equal(calls.length, 2);
  assert.equal(calls[0].url, 'http://127.0.0.1:18765/v1/messages');
  assert.equal(JSON.parse(calls[0].init.body).max_tokens, 16);
  assert.equal(JSON.parse(calls[0].init.body).model, 'claude-sonnet-5');
  assert.equal(JSON.parse(calls[0].init.body).stream, true);
  assert.equal(calls[1].url, 'http://127.0.0.1:18765/v1/responses');
  assert.equal(JSON.parse(calls[1].init.body).max_output_tokens, 16);
  assert.equal(JSON.parse(calls[1].init.body).stream, true);
  assert.equal(diagnostics.outcome, 'passed');
  assert.deepEqual(
    diagnostics.contracts.map(({ name, status }) => ({ name, status })),
    [
      { name: 'claude_messages', status: 200 },
      { name: 'codex_responses', status: 200 },
    ],
  );
  const persisted = readFileSync(diagnosticsFile, 'utf8');
  assert.match(persisted, /"responseSha256": "[a-f0-9]{64}"/);
  assert.match(persisted, /"firstEventValid": true/);
  assert.match(persisted, /"textDeltaSeen": true/);
  assert.match(persisted, /"completed": true/);
  assert.doesNotMatch(persisted, /PACK_EVALUATOR_READY|job-local-secret|Reply with exactly/);
});

test('generated text mismatch is redacted diagnostics and not a protocol failure for either contract', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-content-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  let calls = 0;
  const diagnostics = await runContractSmoke({
    proxyUrl: 'http://127.0.0.1:18765',
    token: 'job-local-secret',
    diagnosticsFile,
    fetchImpl: async (url) => {
      calls += 1;
      return new Response(contractSse(url, {
        messagesText: 'Messages route is ready.',
        responsesText: 'Responses route is ready.',
      }), {
        status: 200,
        headers: { 'content-type': 'text/event-stream; charset=utf-8' },
      });
    },
  });
  assert.equal(calls, 2);
  assert.equal(diagnostics.outcome, 'passed');
  for (const contract of diagnostics.contracts) {
    assert.equal(contract.outcome, 'passed');
    assert.equal(contract.protocol.textDeltaSeen, true);
    assert.equal(contract.protocol.textMatches, false);
    assert.ok(contract.protocol.outputTextBytes > 0);
    assert.match(contract.protocol.outputTextSha256, /^[a-f0-9]{64}$/);
  }
  const persisted = readFileSync(diagnosticsFile, 'utf8');
  assert.doesNotMatch(persisted, /Messages route is ready|Responses route is ready|job-local-secret/);
});

for (const emptyContract of ['messages', 'responses']) {
  test(`empty ${emptyContract} text delta remains a protocol failure`, async () => {
    const directory = mkdtempSync(join(tmpdir(), `pack-contract-smoke-empty-${emptyContract}-`));
    const diagnosticsFile = join(directory, 'contract-smoke.json');
    let calls = 0;
    await assert.rejects(
      runContractSmoke({
        proxyUrl: 'http://127.0.0.1:18765',
        token: 'job-local-secret',
        diagnosticsFile,
        fetchImpl: async (url) => {
          calls += 1;
          return new Response(contractSse(url, {
            messagesText: emptyContract === 'messages' ? '  \n' : undefined,
            responsesText: emptyContract === 'responses' ? '\t' : undefined,
          }), {
            status: 200,
            headers: { 'content-type': 'text/event-stream' },
          });
        },
      }),
      new RegExp(`contract=(?:claude_messages|codex_responses) outcome=invalid_response status=200`),
    );
    assert.equal(calls, 2);
    const persisted = JSON.parse(readFileSync(diagnosticsFile, 'utf8'));
    const failed = persisted.contracts.find((contract) => contract.outcome === 'invalid_response');
    assert.equal(failed.name, emptyContract === 'messages' ? 'claude_messages' : 'codex_responses');
    assert.equal(failed.protocol.textDeltaSeen, false);
    assert.equal(failed.protocol.outputTextBytes, 0);
    assert.equal(failed.protocol.outputTextSha256, null);
  });
}

test('HTTP 200 JSON is not accepted as an SSE protocol response', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-json-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  let calls = 0;
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async () => {
        calls += 1;
        return new Response('{"status":"ok"}', {
          status: 200,
          headers: { 'content-type': 'application/json' },
        });
      },
    }),
    /contract=claude_messages outcome=invalid_response status=200/,
  );
  assert.equal(calls, 2);
  const persisted = JSON.parse(readFileSync(diagnosticsFile, 'utf8'));
  assert.equal(persisted.contracts[0].protocol.contentTypeValid, false);
});

test('malformed SSE JSON remains a protocol failure', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-malformed-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  let calls = 0;
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async (url) => {
        calls += 1;
        const body = String(url).endsWith('/v1/messages')
          ? 'event: message_start\ndata: {not-json}\n\n'
          : contractSse(url);
        return new Response(body, {
          status: 200,
          headers: { 'content-type': 'text/event-stream' },
        });
      },
    }),
    /contract=claude_messages outcome=invalid_response status=200/,
  );
  assert.equal(calls, 2);
  const persisted = JSON.parse(readFileSync(diagnosticsFile, 'utf8'));
  assert.equal(persisted.contracts[0].protocol.malformed, true);
});

test('wrong first SSE event remains a protocol failure', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-first-event-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async (url) => {
        const body = String(url).endsWith('/v1/messages')
          ? sse([
            { type: 'content_block_delta', data: { delta: { type: 'text_delta', text: 'ready' } } },
            { type: 'message_start', data: { message: { id: 'msg_safe' } } },
            { type: 'message_stop', data: {} },
          ])
          : contractSse(url);
        return new Response(body, {
          status: 200,
          headers: { 'content-type': 'text/event-stream' },
        });
      },
    }),
    /contract=claude_messages outcome=invalid_response status=200/,
  );
  const persisted = JSON.parse(readFileSync(diagnosticsFile, 'utf8'));
  assert.equal(persisted.contracts[0].protocol.firstEventValid, false);
});

test('missing completion SSE event remains a protocol failure', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-completed-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async (url) => new Response(contractSse(url, {
        responsesCompleted: !String(url).endsWith('/v1/responses'),
      }), {
        status: 200,
        headers: { 'content-type': 'text/event-stream' },
      }),
    }),
    /contract=codex_responses outcome=invalid_response status=200/,
  );
  const persisted = JSON.parse(readFileSync(diagnosticsFile, 'utf8'));
  assert.equal(persisted.contracts[1].protocol.completed, false);
});

test('contract smoke still sends exactly two probes after an HTTP error without persisting its body', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-error-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  let calls = 0;
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async (url) => {
        calls += 1;
        return new Response('{"error":{"message":"private upstream detail"}}', {
          status: String(url).endsWith('/v1/messages') ? 400 : 404,
        });
      },
    }),
    /contract=claude_messages outcome=http_failed status=400/,
  );
  assert.equal(calls, 2);
  const persisted = readFileSync(diagnosticsFile, 'utf8');
  assert.match(persisted, /"status": 400/);
  assert.match(persisted, /"status": 404/);
  assert.match(persisted, /"errorCategory": "other"/);
  assert.match(persisted, /"errorMessageSha256": "[a-f0-9]{64}"/);
  assert.doesNotMatch(persisted, /private upstream detail|job-local-secret/);
});
