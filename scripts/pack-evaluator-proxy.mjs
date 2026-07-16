#!/usr/bin/env node

import { timingSafeEqual } from 'node:crypto';
import { appendFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';

const ALLOWED_PATHS = new Set([
  '/v1/messages',
  '/v1/messages/count_tokens',
  '/v1/responses',
  '/v1/responses/compact',
]);
const STRIPPED_HEADERS = new Set([
  'authorization',
  'connection',
  'content-encoding',
  'content-length',
  'cookie',
  'host',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
  'x-api-key',
]);
const MAX_BODY_BYTES = 32 * 1024 * 1024;
const DEFAULT_ALLOWED_MODELS = new Set([
  'claude-sonnet-4.6',
  'claude-sonnet-4-6',
  'claude-sonnet-5',
  'sonnet',
  'gpt-5.5',
]);

function fail(message) {
  throw new Error(message);
}

function reject(message, status) {
  const error = new Error(message);
  error.status = status;
  throw error;
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

async function requestBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) fail('request body exceeds 32 MiB');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

function positiveInteger(value, name, fallback) {
  if (value == null || value === '') return fallback;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) fail(`${name} must be a positive integer`);
  return parsed;
}

function allowedModelSet(value = DEFAULT_ALLOWED_MODELS) {
  const models = value instanceof Set
    ? value
    : new Set(String(value).split(',').map((model) => model.trim()).filter(Boolean));
  if (models.size === 0) fail('PACK_EVALUATOR_ALLOWED_MODELS must not be empty');
  return models;
}

function boundedInferenceBody(body, pathname, allowedModels, maxOutputTokens) {
  let payload;
  try {
    payload = JSON.parse(body.toString('utf8'));
  } catch {
    reject('inference request body must be valid JSON', 400);
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    reject('inference request body must be a JSON object', 400);
  }

  const model = typeof payload.model === 'string' ? payload.model.trim() : '';
  if (!model || !allowedModels.has(model)) reject(`model is not allowed: ${model || '(missing)'}`, 403);

  for (const field of ['max_tokens', 'max_output_tokens']) {
    if (payload[field] == null) continue;
    if (!Number.isSafeInteger(payload[field]) || payload[field] < 1 || payload[field] > maxOutputTokens) {
      reject(`${field} must be between 1 and ${maxOutputTokens}`, 400);
    }
  }
  if (pathname === '/v1/messages' && payload.max_tokens == null) payload.max_tokens = maxOutputTokens;
  if (pathname === '/v1/responses' && payload.max_output_tokens == null) {
    payload.max_output_tokens = maxOutputTokens;
  }
  return Buffer.from(JSON.stringify(payload));
}

function upstreamHeaders(request, upstreamKey) {
  const headers = new Headers();
  for (const [name, rawValue] of Object.entries(request.headers)) {
    if (STRIPPED_HEADERS.has(name.toLowerCase()) || rawValue == null) continue;
    const values = Array.isArray(rawValue) ? rawValue : [rawValue];
    for (const value of values) headers.append(name, value);
  }
  headers.set('authorization', `Bearer ${upstreamKey}`);
  return headers;
}

function responseHeaders(upstream) {
  const headers = {};
  for (const [name, value] of upstream.headers.entries()) {
    if (STRIPPED_HEADERS.has(name.toLowerCase()) || name.toLowerCase() === 'set-cookie') continue;
    headers[name] = value;
  }
  return headers;
}

function json(response, status, payload) {
  response.writeHead(status, { 'content-type': 'application/json' });
  response.end(`${JSON.stringify(payload)}\n`);
}

export function createPackEvaluatorProxy({
  localToken,
  upstreamKey,
  upstreamBaseUrl,
  fetchImpl = fetch,
  allowedModels = DEFAULT_ALLOWED_MODELS,
  maxRequests = 256,
  maxConcurrent = 4,
  maxOutputTokens = 65_536,
  ttlMs = 4 * 60 * 60 * 1000,
  requestTimeoutMs = 10 * 60 * 1000,
  onActivity = () => {},
}) {
  if (!localToken || localToken.length < 32) fail('PACK_EVALUATOR_LOCAL_TOKEN must be at least 32 characters');
  if (!upstreamKey) fail('PACK_EVALUATOR_UPSTREAM_KEY is required');
  const modelAllowlist = allowedModelSet(allowedModels);
  const requestLimit = positiveInteger(maxRequests, 'maxRequests', 256);
  const concurrencyLimit = positiveInteger(maxConcurrent, 'maxConcurrent', 4);
  const outputTokenLimit = positiveInteger(maxOutputTokens, 'maxOutputTokens', 65_536);
  const lifetimeMs = positiveInteger(ttlMs, 'ttlMs', 4 * 60 * 60 * 1000);
  const timeoutMs = positiveInteger(requestTimeoutMs, 'requestTimeoutMs', 10 * 60 * 1000);
  const expiresAt = Date.now() + lifetimeMs;
  let requestsStarted = 0;
  let activeRequests = 0;
  const recordActivity = (activity) => {
    try {
      onActivity(activity);
    } catch (error) {
      process.stderr.write(`Pack evaluator activity marker failed: ${error?.code ?? 'unknown'}\n`);
    }
  };
  const upstreamBase = new URL(upstreamBaseUrl);
  if (upstreamBase.protocol !== 'https:' && upstreamBase.hostname !== '127.0.0.1') {
    fail('PACK_EVALUATOR_UPSTREAM_URL must use HTTPS');
  }

  return createServer(async (request, response) => {
    try {
      if (!sameToken(requestToken(request), localToken)) {
        json(response, 401, { error: 'invalid local proxy token' });
        return;
      }
      const incoming = new URL(request.url || '/', 'http://127.0.0.1');
      if (request.method === 'GET' && incoming.pathname === '/healthz') {
        json(response, 200, { ok: true });
        return;
      }
      if (request.method !== 'POST' || !ALLOWED_PATHS.has(incoming.pathname)) {
        json(response, 403, { error: 'endpoint is not allowed by the evaluator proxy' });
        return;
      }

      if (Date.now() >= expiresAt) {
        json(response, 403, { error: 'evaluator proxy token has expired' });
        return;
      }
      if (requestsStarted >= requestLimit) {
        json(response, 429, { error: 'evaluator proxy request budget exhausted' });
        return;
      }
      if (activeRequests >= concurrencyLimit) {
        json(response, 429, { error: 'evaluator proxy concurrency limit reached' });
        return;
      }

      const target = new URL(`${incoming.pathname}${incoming.search}`, upstreamBase);
      const body = boundedInferenceBody(
        await requestBody(request),
        incoming.pathname,
        modelAllowlist,
        outputTokenLimit,
      );
      requestsStarted += 1;
      activeRequests += 1;
      recordActivity({ phase: 'started', requestNumber: requestsStarted });
      const requestNumber = requestsStarted;
      const upstreamController = new AbortController();
      const upstreamTimeout = setTimeout(() => upstreamController.abort(), timeoutMs);
      const abortUpstream = () => {
        if (!response.writableEnded) upstreamController.abort();
      };
      request.once('aborted', abortUpstream);
      response.once('close', abortUpstream);
      try {
        const upstream = await fetchImpl(target, {
          method: 'POST',
          headers: upstreamHeaders(request, upstreamKey),
          body,
          redirect: 'error',
          signal: upstreamController.signal,
        });
        recordActivity({
          phase: 'response',
          requestNumber,
          statusClass: Math.floor(upstream.status / 100) * 100,
        });
        response.writeHead(upstream.status, responseHeaders(upstream));
        if (!upstream.body) {
          response.end();
          return;
        }
        const reader = upstream.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          if (!response.write(Buffer.from(value))) {
            await new Promise((resolve) => response.once('drain', resolve));
          }
        }
        response.end();
      } finally {
        clearTimeout(upstreamTimeout);
        request.off('aborted', abortUpstream);
        response.off('close', abortUpstream);
        activeRequests -= 1;
        recordActivity({ phase: 'completed', requestNumber });
      }
    } catch (error) {
      if (response.destroyed || response.writableEnded) return;
      const status = Number.isSafeInteger(error?.status) ? error.status : 502;
      json(response, status, { error: error instanceof Error ? error.message : 'proxy request failed' });
    }
  });
}

export async function startPackEvaluatorProxy(environment = process.env) {
  const port = Number(environment.PACK_EVALUATOR_PROXY_PORT || '18765');
  if (!Number.isSafeInteger(port) || port < 1 || port > 65535) fail('invalid PACK_EVALUATOR_PROXY_PORT');
  const server = createPackEvaluatorProxy({
    localToken: environment.PACK_EVALUATOR_LOCAL_TOKEN,
    upstreamKey: environment.PACK_EVALUATOR_UPSTREAM_KEY,
    upstreamBaseUrl: environment.PACK_EVALUATOR_UPSTREAM_URL || 'https://helm.easymeta.au',
    allowedModels: environment.PACK_EVALUATOR_ALLOWED_MODELS,
    maxRequests: environment.PACK_EVALUATOR_MAX_REQUESTS,
    maxConcurrent: environment.PACK_EVALUATOR_MAX_CONCURRENT,
    maxOutputTokens: environment.PACK_EVALUATOR_MAX_OUTPUT_TOKENS,
    ttlMs: environment.PACK_EVALUATOR_TTL_MS,
    requestTimeoutMs: environment.PACK_EVALUATOR_REQUEST_TIMEOUT_MS,
    onActivity: environment.PACK_EVALUATOR_ACTIVITY_FILE
      ? (activity) => appendFileSync(
        environment.PACK_EVALUATOR_ACTIVITY_FILE,
        `${JSON.stringify({ at: Date.now(), ...activity })}\n`,
        { mode: 0o600 },
      )
      : undefined,
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolve);
  });
  process.stderr.write(`Pack evaluator inference proxy listening on 127.0.0.1:${port}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  startPackEvaluatorProxy().catch((error) => {
    process.stderr.write(`Pack evaluator proxy failed: ${error instanceof Error ? error.message : error}\n`);
    process.exitCode = 1;
  });
}
