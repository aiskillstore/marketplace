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
      const response = String(url).endsWith('/v1/messages')
        ? sse([
          { type: 'message_start', data: { message: { id: 'msg_safe' } } },
          { type: 'content_block_delta', data: { delta: { type: 'text_delta', text: 'PACK_EVALUATOR_' } } },
          { type: 'content_block_delta', data: { delta: { type: 'text_delta', text: 'READY' } } },
          { type: 'message_stop', data: {} },
        ])
        : sse([
          { type: 'response.created', data: { response: { id: 'resp_safe' } } },
          { type: 'response.output_text.delta', data: { delta: 'PACK_EVALUATOR_' } },
          { type: 'response.output_text.delta', data: { delta: 'READY' } },
          { type: 'response.completed', data: { response: { id: 'resp_safe' } } },
        ]);
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

test('contract smoke fails closed after one exact HTTP error without persisting its body', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-contract-smoke-error-'));
  const diagnosticsFile = join(directory, 'contract-smoke.json');
  let calls = 0;
  await assert.rejects(
    runContractSmoke({
      proxyUrl: 'http://127.0.0.1:18765',
      token: 'job-local-secret',
      diagnosticsFile,
      fetchImpl: async () => {
        calls += 1;
        return new Response('{"error":{"message":"private upstream detail"}}', { status: 422 });
      },
    }),
    /contract=claude_messages outcome=http_failed status=422/,
  );
  assert.equal(calls, 1);
  const persisted = readFileSync(diagnosticsFile, 'utf8');
  assert.match(persisted, /"status": 422/);
  assert.doesNotMatch(persisted, /private upstream detail|job-local-secret/);
});
