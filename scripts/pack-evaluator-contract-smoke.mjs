#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const MAX_RESPONSE_BYTES = 1024 * 1024;
const EXPECTED_RESPONSE_TEXT = 'PACK_EVALUATOR_READY';
const REQUIRED_PROTOCOL_CHECKS = [
  'contentTypeValid',
  'firstEventValid',
  'textDeltaSeen',
  'completed',
];

function fail(message) {
  throw new Error(message);
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function safeDiagnosticToken(value, maximumLength = 128) {
  if (typeof value !== 'string') return null;
  const trimmed = value.trim();
  if (!trimmed || trimmed.length > maximumLength) return null;
  return /^[A-Za-z0-9_.:/\[\]-]+$/.test(trimmed) ? trimmed : null;
}

function classifyErrorMessage(message) {
  if (typeof message !== 'string' || !message.trim()) return 'other';
  const normalized = message.toLowerCase();
  if (
    /(?:unknown|unsupported|invalid|unavailable|not found|does not exist)[\s\S]{0,80}(?:model|lane)/.test(normalized)
    || /(?:model|lane)[\s\S]{0,80}(?:unknown|unsupported|invalid|unavailable|not found|does not exist|not allowed)/.test(normalized)
    || /no (?:available )?(?:model|lane|route|endpoint)/.test(normalized)
  ) return 'unknown_model_or_lane';
  if (
    /(?:unknown|unsupported|unrecognized|invalid)[\s\S]{0,80}(?:parameter|param|field)/.test(normalized)
    || /(?:parameter|param|field)[\s\S]{0,80}(?:unknown|unsupported|unrecognized|not supported|not allowed)/.test(normalized)
  ) return 'unsupported_parameter';
  if (/unauthori[sz]ed|authentication|invalid api key|api key is invalid|credential|forbidden/.test(normalized)) {
    return 'authentication_failed';
  }
  if (/context (?:length|window)|maximum context|too many tokens|token limit|input is too long/.test(normalized)) {
    return 'context_length_exceeded';
  }
  if (/malformed|invalid json|request body|could not parse|failed to parse|schema validation/.test(normalized)) {
    return 'malformed_request';
  }
  return 'other';
}

function sanitizedErrorDiagnostics(body) {
  let payload;
  try {
    payload = JSON.parse(body.toString('utf8'));
  } catch {
    return {};
  }
  const error = payload?.error && typeof payload.error === 'object' ? payload.error : payload;
  const message = typeof error?.message === 'string'
    ? error.message
    : typeof payload?.message === 'string'
      ? payload.message
      : null;
  return {
    errorType: safeDiagnosticToken(error?.type),
    errorCode: safeDiagnosticToken(error?.code),
    errorParam: safeDiagnosticToken(error?.param),
    errorCategory: classifyErrorMessage(message),
    errorMessageSha256: message ? sha256(message) : null,
  };
}

async function boundedBody(response) {
  if (!response.body) return Buffer.alloc(0);
  const reader = response.body.getReader();
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_RESPONSE_BYTES) {
        await reader.cancel('contract smoke response limit reached');
        fail('Helm contract smoke response exceeded 1 MiB');
      }
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return Buffer.concat(chunks);
}

function sseEvents(body) {
  const text = body.toString('utf8');
  const events = [];
  for (const block of text.split(/\r?\n\r?\n/)) {
    if (!block.trim()) continue;
    let eventName = null;
    const dataLines = [];
    for (const line of block.split(/\r?\n/)) {
      if (line.startsWith('event:')) eventName = line.slice('event:'.length).trim();
      if (line.startsWith('data:')) dataLines.push(line.slice('data:'.length).trimStart());
    }
    if (dataLines.length === 0) continue;
    const dataText = dataLines.join('\n');
    if (dataText === '[DONE]') {
      events.push({ type: eventName ?? 'done', data: null });
      continue;
    }
    let data;
    try {
      data = JSON.parse(dataText);
    } catch {
      fail('Helm contract smoke returned malformed SSE JSON');
    }
    events.push({ type: eventName || data?.type || null, data });
  }
  return events;
}

function outputTextDiagnostics(text) {
  const normalized = text.trim();
  return {
    textDeltaSeen: normalized.length > 0,
    textMatches: normalized === EXPECTED_RESPONSE_TEXT,
    outputTextBytes: Buffer.byteLength(normalized),
    outputTextSha256: normalized ? sha256(normalized) : null,
  };
}

function validateMessagesEvents(events) {
  const firstEventValid = events[0]?.type === 'message_start';
  const deltas = events.filter((event) => (
    event.type === 'content_block_delta'
    && event.data?.delta?.type === 'text_delta'
    && typeof event.data.delta.text === 'string'
  ));
  const completed = events.some((event) => event.type === 'message_stop');
  const text = deltas.map((event) => event.data.delta.text).join('');
  return {
    firstEventValid,
    completed,
    ...outputTextDiagnostics(text),
  };
}

function validateResponsesEvents(events) {
  const firstEventValid = events[0]?.type === 'response.created';
  const deltas = events.filter((event) => (
    event.type === 'response.output_text.delta'
    && typeof event.data?.delta === 'string'
  ));
  const completed = events.some((event) => event.type === 'response.completed');
  const text = deltas.map((event) => event.data.delta).join('');
  return {
    firstEventValid,
    completed,
    ...outputTextDiagnostics(text),
  };
}

const CONTRACTS = [
  {
    name: 'claude_messages',
    path: '/v1/messages',
    model: 'claude-sonnet-5',
    payload: {
      model: 'claude-sonnet-5',
      max_tokens: 16,
      stream: true,
      messages: [{
        role: 'user',
        content: 'Reply with exactly PACK_EVALUATOR_READY and nothing else.',
      }],
    },
    validateEvents: validateMessagesEvents,
  },
  {
    name: 'codex_responses',
    path: '/v1/responses',
    model: 'gpt-5.5',
    payload: {
      model: 'gpt-5.5',
      max_output_tokens: 16,
      stream: true,
      input: 'Reply with exactly PACK_EVALUATOR_READY and nothing else.',
    },
    validateEvents: validateResponsesEvents,
  },
];

async function runOneContract({ contract, proxyUrl, token, fetchImpl, timeoutMs }) {
  const endpoint = new URL(contract.path, proxyUrl);
  const requestBody = Buffer.from(JSON.stringify(contract.payload));
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  let response;
  let responseBody = Buffer.alloc(0);
  let transportError = null;
  try {
    response = await fetchImpl(endpoint, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${token}`,
        'content-type': 'application/json',
      },
      body: requestBody,
      redirect: 'error',
      signal: controller.signal,
    });
    responseBody = await boundedBody(response);
  } catch (error) {
    transportError = error;
  } finally {
    clearTimeout(timeout);
  }

  let protocol = {
    contentTypeValid: false,
    firstEventValid: false,
    textDeltaSeen: false,
    completed: false,
    textMatches: false,
    outputTextBytes: 0,
    outputTextSha256: null,
  };
  let eventCount = 0;
  if (response?.ok) {
    try {
      const events = sseEvents(responseBody);
      eventCount = events.length;
      protocol = {
        contentTypeValid: response.headers.get('content-type')?.toLowerCase().startsWith('text/event-stream') === true,
        ...contract.validateEvents(events),
      };
    } catch {
      protocol = { ...protocol, malformed: true };
    }
  }
  const validResponse = REQUIRED_PROTOCOL_CHECKS.every((check) => protocol[check] === true);
  return {
    name: contract.name,
    outcome: transportError
      ? 'transport_failed'
      : response?.ok && validResponse
        ? 'passed'
        : response?.ok
          ? 'invalid_response'
          : 'http_failed',
    path: endpoint.pathname,
    model: contract.model,
    requestBytes: requestBody.length,
    stream: contract.payload.stream,
    status: response?.status ?? null,
    responseBytes: responseBody.length,
    responseSha256: responseBody.length > 0 ? sha256(responseBody) : null,
    eventCount,
    protocol,
    ...(response && !response.ok ? sanitizedErrorDiagnostics(responseBody) : {}),
    transportErrorType: transportError?.name ?? null,
    transportErrorMessageSha256: transportError instanceof Error ? sha256(transportError.message) : null,
  };
}

export async function runContractSmoke({
  proxyUrl,
  token,
  diagnosticsFile,
  fetchImpl = fetch,
  timeoutMs = 30_000,
}) {
  if (!proxyUrl) fail('PACK_EVALUATOR_PROXY_URL is required');
  if (!token) fail('PACK_EVALUATOR_PROXY_TOKEN is required');
  if (!diagnosticsFile) fail('PACK_EVALUATOR_CONTRACT_DIAGNOSTICS_FILE is required');
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 120_000) {
    fail('PACK_EVALUATOR_CONTRACT_TIMEOUT_MS must be between 1 and 120000');
  }
  const contracts = [];
  for (const contract of CONTRACTS) {
    const result = await runOneContract({ contract, proxyUrl, token, fetchImpl, timeoutMs });
    contracts.push(result);
  }
  const failed = contracts.find((contract) => contract.outcome !== 'passed');
  const diagnostics = {
    schemaVersion: 'marketplace.pack-evaluator-contract-smoke/v1',
    outcome: failed ? 'failed' : contracts.length === CONTRACTS.length ? 'passed' : 'incomplete',
    contracts,
  };
  await writeFile(diagnosticsFile, `${JSON.stringify(diagnostics, null, 2)}\n`, { mode: 0o600 });
  if (diagnostics.outcome !== 'passed') {
    fail(
      `Helm contract smoke failed: contract=${failed?.name ?? 'unknown'} `
      + `outcome=${failed?.outcome ?? diagnostics.outcome} status=${failed?.status ?? 'none'}`,
    );
  }
  return diagnostics;
}

async function main(environment = process.env) {
  const result = await runContractSmoke({
    proxyUrl: environment.PACK_EVALUATOR_PROXY_URL || 'http://127.0.0.1:18765',
    token: environment.PACK_EVALUATOR_PROXY_TOKEN,
    diagnosticsFile: environment.PACK_EVALUATOR_CONTRACT_DIAGNOSTICS_FILE,
    timeoutMs: Number(environment.PACK_EVALUATOR_CONTRACT_TIMEOUT_MS || '30000'),
  });
  process.stdout.write(`${JSON.stringify({
    outcome: result.outcome,
    contracts: result.contracts.map(({ name, status }) => ({ name, status })),
  })}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : 'Helm contract smoke failed'}\n`);
    process.exitCode = 1;
  });
}
