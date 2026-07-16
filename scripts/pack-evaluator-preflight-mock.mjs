#!/usr/bin/env node

import { timingSafeEqual } from 'node:crypto';
import { appendFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';

const READY_TEXT = 'PACK_EVALUATOR_READY';
const MAX_REQUEST_BYTES = 1024 * 1024;

function fail(message) {
  throw new Error(message);
}

function sameToken(actual, expected) {
  const left = Buffer.from(actual || '');
  const right = Buffer.from(expected || '');
  return left.length === right.length && left.length > 0 && timingSafeEqual(left, right);
}

function requestToken(request) {
  const authorization = request.headers.authorization;
  if (authorization?.startsWith('Bearer ')) return authorization.slice('Bearer '.length);
  const apiKey = request.headers['x-api-key'];
  return Array.isArray(apiKey) ? apiKey[0] : apiKey;
}

function json(response, status, body) {
  response.writeHead(status, { 'content-type': 'application/json' });
  response.end(`${JSON.stringify(body)}\n`);
}

function sse(response, events) {
  response.writeHead(200, {
    'cache-control': 'no-store',
    'content-type': 'text/event-stream; charset=utf-8',
  });
  for (const event of events) {
    response.write(`event: ${event.type}\n`);
    response.write(`data: ${JSON.stringify(event)}\n\n`);
  }
  response.end();
}

async function requestJson(request) {
  const chunks = [];
  let bytes = 0;
  for await (const chunk of request) {
    bytes += chunk.length;
    if (bytes > MAX_REQUEST_BYTES) fail('mock preflight request exceeded 1 MiB');
    chunks.push(chunk);
  }
  const body = Buffer.concat(chunks);
  const value = JSON.parse(body.toString('utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail('mock preflight request must be a JSON object');
  }
  return { value, bytes: body.length };
}

function messageObject(model, content, stopReason) {
  return {
    id: 'msg_pack_preflight_mock',
    type: 'message',
    role: 'assistant',
    model,
    content,
    stop_reason: stopReason,
    stop_sequence: null,
    usage: { input_tokens: 1, output_tokens: content.length > 0 ? 1 : 0 },
  };
}

function messagesEvents(model) {
  return [
    { type: 'message_start', message: messageObject(model, [], null) },
    {
      type: 'content_block_start',
      index: 0,
      content_block: { type: 'text', text: '' },
    },
    {
      type: 'content_block_delta',
      index: 0,
      delta: { type: 'text_delta', text: READY_TEXT },
    },
    { type: 'content_block_stop', index: 0 },
    {
      type: 'message_delta',
      delta: { stop_reason: 'end_turn', stop_sequence: null },
      usage: { output_tokens: 1 },
    },
    { type: 'message_stop' },
  ];
}

function responseItem() {
  return {
    id: 'msg_pack_preflight_mock',
    type: 'message',
    role: 'assistant',
    content: [{ type: 'output_text', text: READY_TEXT, annotations: [] }],
  };
}

function responsesEvents() {
  const id = 'resp_pack_preflight_mock';
  const item = responseItem();
  return [
    { type: 'response.created', response: { id } },
    { type: 'response.output_item.added', output_index: 0, item: { ...item, content: [] } },
    {
      type: 'response.content_part.added',
      item_id: item.id,
      output_index: 0,
      content_index: 0,
      part: { type: 'output_text', text: '', annotations: [] },
    },
    {
      type: 'response.output_text.delta',
      item_id: item.id,
      output_index: 0,
      content_index: 0,
      delta: READY_TEXT,
    },
    {
      type: 'response.output_text.done',
      item_id: item.id,
      output_index: 0,
      content_index: 0,
      text: READY_TEXT,
    },
    {
      type: 'response.content_part.done',
      item_id: item.id,
      output_index: 0,
      content_index: 0,
      part: item.content[0],
    },
    { type: 'response.output_item.done', output_index: 0, item },
    {
      type: 'response.completed',
      response: {
        id,
        status: 'completed',
        output: [item],
        usage: {
          input_tokens: 1,
          input_tokens_details: null,
          output_tokens: 1,
          output_tokens_details: null,
          total_tokens: 2,
        },
      },
    },
  ];
}

export function createPackEvaluatorPreflightMock({ localToken, onActivity = () => {} }) {
  if (typeof localToken !== 'string' || localToken.length < 32) {
    fail('PACK_EVALUATOR_LOCAL_TOKEN must be at least 32 characters');
  }
  let requestNumber = 0;
  return createServer(async (request, response) => {
    const path = new URL(request.url || '/', 'http://127.0.0.1').pathname;
    if (!sameToken(requestToken(request), localToken)) {
      onActivity({ phase: 'rejected', path, status: 401 });
      json(response, 401, { error: 'invalid local mock token' });
      return;
    }
    if (request.method === 'GET' && path === '/healthz') {
      json(response, 200, { ok: true });
      return;
    }
    if (request.method !== 'POST') {
      onActivity({ phase: 'rejected', path, status: 405 });
      json(response, 405, { error: 'method not allowed' });
      return;
    }

    let parsed;
    try {
      parsed = await requestJson(request);
    } catch {
      onActivity({ phase: 'response', path, status: 400 });
      json(response, 400, { error: 'invalid mock request' });
      return;
    }
    requestNumber += 1;
    const model = typeof parsed.value.model === 'string' ? parsed.value.model : null;
    const activity = {
      phase: 'response',
      requestNumber,
      path,
      model,
      requestBytes: parsed.bytes,
      stream: parsed.value.stream === true,
      status: 200,
    };

    if (path === '/v1/messages/count_tokens') {
      onActivity(activity);
      json(response, 200, { input_tokens: 1 });
      return;
    }
    if (path === '/v1/messages') {
      onActivity(activity);
      if (parsed.value.stream === true) {
        sse(response, messagesEvents(model || 'sonnet'));
      } else {
        json(response, 200, messageObject(model || 'sonnet', [{ type: 'text', text: READY_TEXT }], 'end_turn'));
      }
      return;
    }
    if (path === '/v1/responses') {
      onActivity(activity);
      if (parsed.value.stream === true) {
        sse(response, responsesEvents());
      } else {
        json(response, 200, responsesEvents().at(-1).response);
      }
      return;
    }
    if (path === '/v1/responses/compact') {
      onActivity(activity);
      json(response, 200, { output: [], usage: { input_tokens: 1, output_tokens: 0, total_tokens: 1 } });
      return;
    }

    onActivity({ ...activity, status: 403 });
    json(response, 403, { error: 'endpoint not allowed by preflight mock' });
  });
}

export async function startPackEvaluatorPreflightMock(environment = process.env) {
  const port = Number(environment.PACK_EVALUATOR_PROXY_PORT || '18765');
  if (!Number.isSafeInteger(port) || port < 1 || port > 65535) fail('invalid mock proxy port');
  const activityFile = environment.PACK_EVALUATOR_ACTIVITY_FILE;
  const server = createPackEvaluatorPreflightMock({
    localToken: environment.PACK_EVALUATOR_LOCAL_TOKEN,
    onActivity: activityFile
      ? (activity) => appendFileSync(
        activityFile,
        `${JSON.stringify({ at: Date.now(), ...activity })}\n`,
        { mode: 0o600 },
      )
      : undefined,
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolve);
  });
  process.stderr.write(`Pack evaluator preflight mock listening on 127.0.0.1:${port}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  startPackEvaluatorPreflightMock().catch((error) => {
    process.stderr.write(`Pack evaluator preflight mock failed: ${error instanceof Error ? error.message : error}\n`);
    process.exitCode = 1;
  });
}
