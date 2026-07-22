#!/usr/bin/env node

import { createHash, timingSafeEqual } from 'node:crypto';
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
const MAX_ERROR_DIAGNOSTIC_BYTES = 64 * 1024;
const MAX_AUTH_REJECTION_DIAGNOSTICS = 8;
const HARD_MAX_REQUESTS = 160;
const HARD_MAX_CONCURRENT = 1;
const HARD_MAX_INPUT_TOKENS = 600_000;
const HARD_MAX_OUTPUT_TOKENS = 120_000;
const HARD_MAX_COST_MICRO_USD = 10_000_000;
const TRACE_HEADERS = [
  'cf-ray',
  'request-id',
  'traceparent',
  'x-request-id',
  'x-trace-id',
];
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

function reject(message, status, policyCategory) {
  const error = new Error(message);
  error.status = status;
  if (policyCategory) error.policyCategory = policyCategory;
  throw error;
}

function sameToken(actual, expected) {
  const left = Buffer.from(actual || '');
  const right = Buffer.from(expected || '');
  return left.length === right.length && left.length > 0 && timingSafeEqual(left, right);
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

/**
 * Convert a potentially sensitive upstream message into one fixed operational
 * category. The caller may retain the category and hash, never the raw text.
 */
export function classifyUpstreamErrorMessage(message) {
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

function traceHeaders(headers) {
  const traces = {};
  for (const name of TRACE_HEADERS) {
    const value = safeDiagnosticToken(headers.get(name), 256);
    if (value) traces[name] = value;
  }
  return traces;
}

async function boundedResponseBody(response, maximumBytes = MAX_ERROR_DIAGNOSTIC_BYTES) {
  if (!response.body) return Buffer.alloc(0);
  const reader = response.body.getReader();
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > maximumBytes) {
        await reader.cancel('diagnostic body limit reached');
        return null;
      }
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return Buffer.concat(chunks);
}

async function errorDiagnostics(upstream) {
  if (upstream.status < 400) return {};
  const body = await boundedResponseBody(upstream.clone());
  if (!body) return { errorBodyTruncated: true };
  let payload;
  try {
    payload = JSON.parse(body.toString('utf8'));
  } catch {
    return {
      errorBodyBytes: body.length,
      errorBodySha256: body.length > 0 ? sha256(body) : null,
    };
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
    errorCategory: classifyUpstreamErrorMessage(message),
    errorMessageSha256: message ? sha256(message) : null,
    errorBodyBytes: body.length,
  };
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
    if (size > MAX_BODY_BYTES) {
      reject('request body exceeds 32 MiB', 400, 'request_body_too_large');
    }
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

function positiveNumber(value, name, fallback) {
  if (value == null || value === '') return fallback;
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) fail(`${name} must be a positive number`);
  return parsed;
}

function usageFromPayload(payload) {
  const candidates = [payload?.usage, payload?.response?.usage, payload?.message?.usage]
    .filter((usage) => usage && typeof usage === 'object' && !Array.isArray(usage));
  if (candidates.length === 0) return null;
  const result = { inputTokens: null, outputTokens: null, costMicroUsd: null };
  for (const usage of candidates) {
    const input = usage.input_tokens ?? usage.prompt_tokens;
    const output = usage.output_tokens ?? usage.completion_tokens;
    if (Number.isSafeInteger(input) && input >= 0) {
      const cache = [usage.cache_creation_input_tokens, usage.cache_read_input_tokens]
        .filter((value) => value != null);
      if (cache.every((value) => Number.isSafeInteger(value) && value >= 0)) {
        const total = input + cache.reduce((sum, value) => sum + value, 0);
        if (Number.isSafeInteger(total)) result.inputTokens = Math.max(result.inputTokens ?? 0, total);
      }
    }
    if (Number.isSafeInteger(output) && output >= 0) {
      result.outputTokens = Math.max(result.outputTokens ?? 0, output);
    }
    const costs = [usage.cost_usd, usage.total_cost_usd]
      .filter((cost) => Number.isFinite(Number(cost)) && Number(cost) >= 0)
      .map((cost) => Math.ceil(Number(cost) * 1_000_000));
    if (costs.length > 0) result.costMicroUsd = Math.max(result.costMicroUsd ?? 0, ...costs);
  }
  return result;
}

async function responseUsage(upstream, stream) {
  const body = await boundedResponseBody(upstream.clone(), MAX_BODY_BYTES);
  if (!body) return null;
  const payloads = [];
  if (!stream) {
    try {
      payloads.push(JSON.parse(body.toString('utf8')));
    } catch {
      return null;
    }
  } else {
    for (const line of body.toString('utf8').split(/\r?\n/)) {
      const value = line.startsWith('data:') ? line.slice(5).trim() : line.trim();
      if (!value || value === '[DONE]') continue;
      try {
        payloads.push(JSON.parse(value));
      } catch {
        // Non-data SSE fields and partial diagnostics are not usage evidence.
      }
    }
  }
  let merged = null;
  for (const payload of payloads) {
    const usage = usageFromPayload(payload);
    if (!usage) continue;
    merged ??= { inputTokens: null, outputTokens: null, costMicroUsd: null };
    for (const field of Object.keys(merged)) {
      if (usage[field] != null) merged[field] = Math.max(merged[field] ?? 0, usage[field]);
    }
  }
  return merged;
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
    reject('inference request body must be valid JSON', 400, 'malformed_request');
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    reject('inference request body must be a JSON object', 400, 'malformed_request');
  }

  const model = typeof payload.model === 'string' ? payload.model.trim() : '';
  if (!model || !allowedModels.has(model)) {
    reject(`model is not allowed: ${model || '(missing)'}`, 403, 'model_not_allowed');
  }

  for (const field of ['max_tokens', 'max_output_tokens']) {
    if (payload[field] == null) continue;
    if (!Number.isSafeInteger(payload[field]) || payload[field] < 1 || payload[field] > maxOutputTokens) {
      reject(`${field} must be between 1 and ${maxOutputTokens}`, 400, 'invalid_output_token_limit');
    }
  }
  if (pathname === '/v1/messages' && payload.max_output_tokens != null) {
    reject('max_output_tokens is not allowed for the Messages API', 400, 'invalid_output_token_limit');
  }
  if ((pathname === '/v1/responses' || pathname === '/v1/responses/compact')
    && payload.max_tokens != null) {
    reject('max_tokens is not allowed for the Responses API', 400, 'invalid_output_token_limit');
  }
  if (pathname === '/v1/messages' && payload.max_tokens == null) payload.max_tokens = maxOutputTokens;
  if ((pathname === '/v1/responses' || pathname === '/v1/responses/compact')
    && payload.max_output_tokens == null) {
    payload.max_output_tokens = maxOutputTokens;
  }
  return {
    body: Buffer.from(JSON.stringify(payload)),
    model,
    stream: payload.stream === true,
    outputReservation: pathname === '/v1/messages'
      ? payload.max_tokens
      : (pathname === '/v1/responses' || pathname === '/v1/responses/compact')
        ? payload.max_output_tokens
        : 0,
  };
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

function isDeterministicClientFailure(status) {
  return status >= 400 && status < 500 && ![408, 425, 429].includes(status);
}

export function createPackEvaluatorProxy({
  localToken,
  upstreamKey,
  upstreamBaseUrl,
  fetchImpl = fetch,
  allowedModels = DEFAULT_ALLOWED_MODELS,
  maxRequests = HARD_MAX_REQUESTS,
  maxConcurrent = HARD_MAX_CONCURRENT,
  maxOutputTokens = 65_536,
  maxInputTokens = HARD_MAX_INPUT_TOKENS,
  maxTotalOutputTokens = HARD_MAX_OUTPUT_TOKENS,
  maxCostUsd = 10,
  maxInputCostPerMillionUsd = 15,
  maxOutputCostPerMillionUsd = 75,
  ttlMs = 4 * 60 * 60 * 1000,
  requestTimeoutMs = 10 * 60 * 1000,
  onActivity = () => {},
}) {
  if (!localToken || localToken.length < 32) fail('PACK_EVALUATOR_LOCAL_TOKEN must be at least 32 characters');
  if (!upstreamKey) fail('PACK_EVALUATOR_UPSTREAM_KEY is required');
  const modelAllowlist = allowedModelSet(allowedModels);
  const requestLimit = Math.min(HARD_MAX_REQUESTS, positiveInteger(maxRequests, 'maxRequests', HARD_MAX_REQUESTS));
  const concurrencyLimit = Math.min(
    HARD_MAX_CONCURRENT,
    positiveInteger(maxConcurrent, 'maxConcurrent', HARD_MAX_CONCURRENT),
  );
  const outputTokenLimit = Math.min(
    HARD_MAX_OUTPUT_TOKENS,
    positiveInteger(maxOutputTokens, 'maxOutputTokens', 65_536),
  );
  const inputTokenLimit = Math.min(
    HARD_MAX_INPUT_TOKENS,
    positiveInteger(maxInputTokens, 'maxInputTokens', HARD_MAX_INPUT_TOKENS),
  );
  const totalOutputTokenLimit = Math.min(
    HARD_MAX_OUTPUT_TOKENS,
    positiveInteger(maxTotalOutputTokens, 'maxTotalOutputTokens', HARD_MAX_OUTPUT_TOKENS),
  );
  const costLimitMicroUsd = Math.min(
    HARD_MAX_COST_MICRO_USD,
    Math.floor(positiveNumber(maxCostUsd, 'maxCostUsd', 10) * 1_000_000),
  );
  const inputCostCeiling = positiveNumber(
    maxInputCostPerMillionUsd,
    'maxInputCostPerMillionUsd',
    15,
  );
  const outputCostCeiling = positiveNumber(
    maxOutputCostPerMillionUsd,
    'maxOutputCostPerMillionUsd',
    75,
  );
  const lifetimeMs = positiveInteger(ttlMs, 'ttlMs', 4 * 60 * 60 * 1000);
  const timeoutMs = positiveInteger(requestTimeoutMs, 'requestTimeoutMs', 10 * 60 * 1000);
  const expiresAt = Date.now() + lifetimeMs;
  let requestsStarted = 0;
  let activityRequestSequence = 0;
  let activeRequests = 0;
  let inputTokens = 0;
  let outputTokens = 0;
  let costMicroUsd = 0;
  let reservedInputTokens = 0;
  let reservedOutputTokens = 0;
  let reservedCostMicroUsd = 0;
  let budgetFailure = null;
  let authRejectionDiagnostics = 0;
  let circuitFailure = null;
  const recordActivity = (activity) => {
    try {
      onActivity(activity);
    } catch (error) {
      process.stderr.write(`Pack evaluator activity marker failed: ${error?.code ?? 'unknown'}\n`);
    }
  };
  const recordBudget = (status, reason = null) => recordActivity({
    phase: 'budget',
    status,
    reason,
    modelRequests: requestsStarted,
    inputTokens,
    outputTokens,
    costUsd: costMicroUsd / 1_000_000,
    reservedCostUsd: reservedCostMicroUsd / 1_000_000,
    billable: status !== 'unbillable',
  });
  const upstreamBase = new URL(upstreamBaseUrl);
  if (upstreamBase.protocol !== 'https:' && upstreamBase.hostname !== '127.0.0.1') {
    fail('PACK_EVALUATOR_UPSTREAM_URL must use HTTPS');
  }

  return createServer(async (request, response) => {
    try {
      if (!sameToken(requestToken(request), localToken)) {
        if (authRejectionDiagnostics < MAX_AUTH_REJECTION_DIAGNOSTICS) {
          const rejectedPath = new URL(request.url || '/', 'http://127.0.0.1').pathname;
          recordActivity({
            phase: 'response',
            requestNumber: ++activityRequestSequence,
            path: ALLOWED_PATHS.has(rejectedPath) ? rejectedPath : 'not_allowed',
            status: 401,
            errorCategory: 'authentication_failed',
          });
          authRejectionDiagnostics += 1;
        }
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
      if (budgetFailure) {
        recordBudget(budgetFailure === 'usage_unavailable' ? 'unbillable' : 'exhausted', budgetFailure);
        json(response, 429, { error: 'evaluator proxy cumulative budget is not admissible' });
        return;
      }
      if (requestsStarted >= requestLimit) {
        budgetFailure = 'request_limit';
        recordBudget('exhausted', budgetFailure);
        json(response, 429, { error: 'evaluator proxy request budget exhausted' });
        return;
      }
      if (activeRequests >= concurrencyLimit) {
        json(response, 429, { error: 'evaluator proxy concurrency limit reached' });
        return;
      }

      const target = new URL(`${incoming.pathname}${incoming.search}`, upstreamBase);
      const requestNumber = ++activityRequestSequence;
      let incomingBody;
      let bounded;
      try {
        incomingBody = await requestBody(request);
        bounded = boundedInferenceBody(
          incomingBody,
          incoming.pathname,
          modelAllowlist,
          outputTokenLimit,
        );
      } catch (error) {
        if ([400, 403].includes(error?.status) && error?.policyCategory) {
          recordActivity({
            phase: 'response',
            requestNumber,
            path: incoming.pathname,
            status: error.status,
            errorCategory: error.policyCategory,
          });
        }
        throw error;
      }
      const requestDiagnostics = {
        path: incoming.pathname,
        model: bounded.model,
        requestBytes: incomingBody.length,
        stream: bounded.stream,
      };
      if (circuitFailure) {
        recordActivity({
          phase: 'circuit_open',
          requestNumber,
          ...requestDiagnostics,
          status: circuitFailure.status,
          originalRequestNumber: circuitFailure.requestNumber,
        });
        json(response, 424, { error: 'upstream deterministic client failure opened the evaluator circuit' });
        return;
      }
      const inputReservation = incomingBody.length;
      if (inputTokens + reservedInputTokens + inputReservation > inputTokenLimit) {
        budgetFailure = 'input_token_limit';
        recordBudget('exhausted', budgetFailure);
        json(response, 429, { error: 'evaluator proxy input token budget exhausted' });
        return;
      }
      const outputReservation = incoming.pathname === '/v1/messages/count_tokens'
        ? 0
        : bounded.outputReservation || outputTokenLimit;
      if (outputTokens + reservedOutputTokens + outputReservation > totalOutputTokenLimit) {
        budgetFailure = 'output_token_limit';
        recordBudget('exhausted', budgetFailure);
        json(response, 429, { error: 'evaluator proxy output token budget exhausted' });
        return;
      }
      // The request body byte count is a conservative upper bound for input
      // tokens. Reserve against explicit worst-case per-model price ceilings
      // before forwarding so one in-flight request cannot cross the USD cap.
      const costReservationMicroUsd = incoming.pathname === '/v1/messages/count_tokens'
        ? 0
        : Math.ceil(inputReservation * inputCostCeiling + outputReservation * outputCostCeiling);
      if (costMicroUsd + reservedCostMicroUsd + costReservationMicroUsd > costLimitMicroUsd) {
        budgetFailure = 'cost_limit';
        recordBudget('exhausted', budgetFailure);
        json(response, 429, { error: 'evaluator proxy worst-case cost reservation exceeds budget' });
        return;
      }
      requestsStarted += 1;
      activeRequests += 1;
      reservedInputTokens += inputReservation;
      reservedOutputTokens += outputReservation;
      reservedCostMicroUsd += costReservationMicroUsd;
      recordActivity({ phase: 'started', requestNumber, ...requestDiagnostics });
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
          body: bounded.body,
          redirect: 'error',
          signal: upstreamController.signal,
        });
        const isModelRequest = incoming.pathname !== '/v1/messages/count_tokens';
        const usagePromise = upstream.ok && isModelRequest
          ? responseUsage(upstream, bounded.stream)
          : Promise.resolve(null);
        const upstreamDiagnostics = await errorDiagnostics(upstream);
        if (isDeterministicClientFailure(upstream.status)) {
          circuitFailure = { status: upstream.status, requestNumber };
        }
        recordActivity({
          phase: 'response',
          requestNumber,
          ...requestDiagnostics,
          status: upstream.status,
          traceHeaders: traceHeaders(upstream.headers),
          ...upstreamDiagnostics,
        });
        response.writeHead(upstream.status, responseHeaders(upstream));
        if (!upstream.body) {
          response.end();
          if (upstream.ok && isModelRequest) {
            budgetFailure = 'usage_unavailable';
            recordBudget('unbillable', budgetFailure);
          }
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
        if (upstream.ok && isModelRequest) {
          const usage = await usagePromise;
          if (
            usage?.inputTokens == null
            || usage.outputTokens == null
            || usage.costMicroUsd == null
          ) {
            budgetFailure = 'usage_unavailable';
            recordBudget('unbillable', budgetFailure);
          } else {
            inputTokens += usage.inputTokens;
            outputTokens += usage.outputTokens;
            costMicroUsd += usage.costMicroUsd;
            if (inputTokens > inputTokenLimit) budgetFailure = 'input_token_limit';
            else if (outputTokens > totalOutputTokenLimit) budgetFailure = 'output_token_limit';
            else if (costMicroUsd > costLimitMicroUsd) budgetFailure = 'cost_limit';
            recordBudget(budgetFailure ? 'exhausted' : 'within', budgetFailure);
          }
        }
      } catch (error) {
        recordActivity({
          phase: 'error',
          requestNumber,
          ...requestDiagnostics,
          status: null,
          errorType: safeDiagnosticToken(error?.name) ?? 'proxy_upstream_error',
          errorCode: safeDiagnosticToken(error?.code),
          errorCategory: classifyUpstreamErrorMessage(error instanceof Error ? error.message : null),
          errorMessageSha256: error instanceof Error ? sha256(error.message) : null,
        });
        if (!budgetFailure && incoming.pathname !== '/v1/messages/count_tokens') {
          budgetFailure = 'usage_unavailable';
          recordBudget('unbillable', budgetFailure);
        }
        throw error;
      } finally {
        clearTimeout(upstreamTimeout);
        request.off('aborted', abortUpstream);
        response.off('close', abortUpstream);
        activeRequests -= 1;
        reservedInputTokens -= inputReservation;
        reservedOutputTokens -= outputReservation;
        reservedCostMicroUsd -= costReservationMicroUsd;
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
    maxInputTokens: environment.PACK_EVALUATOR_MAX_INPUT_TOKENS,
    maxTotalOutputTokens: environment.PACK_EVALUATOR_MAX_TOTAL_OUTPUT_TOKENS,
    maxCostUsd: environment.PACK_EVALUATOR_MAX_COST_USD,
    maxInputCostPerMillionUsd: environment.PACK_EVALUATOR_MAX_INPUT_COST_PER_MILLION_USD,
    maxOutputCostPerMillionUsd: environment.PACK_EVALUATOR_MAX_OUTPUT_COST_PER_MILLION_USD,
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
