#!/usr/bin/env node

import { createWriteStream } from 'node:fs';
import { readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const DEFAULTS = {
  siteUrl: 'https://skillstore.io',
  locales: ['en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'de', 'fr', 'es', 'pt', 'ru', 'ar'],
  concurrency: 10,
  maxAttempts: 5,
  retryWindowMinMs: 90_000,
  retryWindowMaxMs: 120_000,
  timeoutMs: 60_000,
  buildHeader: 'x-skillstore-build',
  apiCacheHeader: 'x-api-kv-cache',
  pageCacheHeader: 'x-page-kv-cache',
  zipCacheHeader: 'x-cache',
};

const BUILD_TOKEN_RE = /^[0-9a-f]{40}\.[a-z0-9-]+$/i;
const RETRYABLE_STATUSES = new Set([408, 425, 429, 500, 502, 503, 504]);
const RETRYABLE_CACHE_STATES = new Set(['MISS', 'STALE']);
const RETRY_BASE_DELAY_MS = 1_000;
const RETRY_MAX_DELAY_MS = 15_000;
const VERIFICATION_RESERVE_PER_REQUEST_MS = 10_000;
export const MAX_EDGE_TRANSFORM_OVERHEAD = 16 * 1024;

export class WarmError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'WarmError';
    this.details = details;
  }
}

function parsePositiveInteger(value, label) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    throw new WarmError(`${label} must be a positive integer`);
  }
  return parsed;
}

function normalizeSiteUrl(value) {
  const url = new URL(value);
  if (url.protocol !== 'https:' && url.protocol !== 'http:') {
    throw new WarmError('site URL must use HTTP or HTTPS');
  }
  return url.toString().replace(/\/$/, '');
}

export function normalizeSlugs(input) {
  const values = Array.isArray(input) ? input : String(input || '').split(/[\s,]+/);
  const slugs = [...new Set(values.map((value) => String(value).trim()).filter(Boolean))].sort();
  if (slugs.length === 0) {
    throw new WarmError('Warm scope is empty; provide changed/high-traffic slugs or explicitly approve full-catalog mode');
  }
  return slugs;
}

function buildSkillApiUrl(siteUrl, slug) {
  const url = new URL(`/api/skills/${encodeURIComponent(slug)}`, `${siteUrl}/`);
  url.searchParams.set('lang', 'en');
  return url;
}

function buildSkillPageUrl(siteUrl, slug, locale) {
  const prefix = locale === 'en' ? '' : `/${locale}`;
  return new URL(`${prefix}/skills/${encodeURIComponent(slug)}`, `${siteUrl}/`);
}

function buildSkillZipUrl(siteUrl, slug) {
  return new URL(`/api/skills/${encodeURIComponent(slug)}/download`, `${siteUrl}/`);
}

function withBuildToken(url, token) {
  const result = new URL(url);
  result.searchParams.set('__skillstore_build', token);
  return result;
}

function coloFromRay(cfRay) {
  if (!cfRay) return null;
  const separator = cfRay.lastIndexOf('-');
  return separator >= 0 ? cfRay.slice(separator + 1) || null : null;
}

function stableHash(value, seed = 0) {
  let hash = seed >>> 0;
  for (const character of value) hash = (hash * 33 + character.charCodeAt(0)) >>> 0;
  return hash;
}

function endpointWindow(url, minimum, maximum) {
  if (maximum <= minimum) return minimum;
  return minimum + (stableHash(url) % (maximum - minimum + 1));
}

function retryDelay(url, attempt) {
  const exponent = Math.max(0, attempt - 2);
  const base = Math.min(RETRY_MAX_DELAY_MS, RETRY_BASE_DELAY_MS * (2 ** exponent));
  const jitterPercent = 75 + (stableHash(url, attempt) % 51);
  return Math.max(1, Math.floor(base * jitterPercent / 100));
}

function timeoutSignal(timeoutMs, runSignal) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('request timed out')), timeoutMs);
  const abortFromRun = () => controller.abort(runSignal.reason || new Error('warm run aborted'));
  if (runSignal.aborted) abortFromRun();
  else runSignal.addEventListener('abort', abortFromRun, { once: true });
  return {
    signal: controller.signal,
    clear: () => {
      clearTimeout(timeout);
      runSignal.removeEventListener('abort', abortFromRun);
    },
  };
}

function contentBytes(buffer) {
  return buffer?.byteLength || 0;
}

function requireBuildToken(value, source) {
  if (!value || !BUILD_TOKEN_RE.test(value)) {
    throw new WarmError(`${source} did not provide a valid exact Skillstore build token`, {
      buildToken: value || null,
    });
  }
  return value;
}

class Budget {
  constructor(requestLimit, byteLimit) {
    this.requestLimit = requestLimit;
    this.byteLimit = byteLimit;
    this.requests = 0;
    this.bytes = 0;
    this.reservedBytes = 0;
  }

  reserveRequest(url) {
    if (this.requests >= this.requestLimit) {
      throw new WarmError(`Request budget exhausted before ${url}`, {
        ...this.snapshot(),
        fatal: true,
      });
    }
    this.requests += 1;
  }

  reserveResponseBytes(bytes, url) {
    if (this.bytes + this.reservedBytes + bytes > this.byteLimit) {
      throw new WarmError(`Byte budget would be exceeded before reading ${url}`, {
        ...this.snapshot(),
        contentLength: bytes,
        responseBytes: 0,
        fatal: true,
      });
    }
    this.reservedBytes += bytes;
    return { remaining: bytes, released: false };
  }

  consumeBytes(bytes, url, reservation, responseBytes) {
    const covered = reservation ? Math.min(bytes, reservation.remaining) : 0;
    const extra = bytes - covered;
    if (this.bytes + this.reservedBytes + extra > this.byteLimit) {
      throw new WarmError(`Byte budget would be exceeded while reading ${url}`, {
        ...this.snapshot(),
        chunkBytes: bytes,
        responseBytes,
        fatal: true,
      });
    }
    if (reservation) {
      reservation.remaining -= covered;
      this.reservedBytes -= covered;
    }
    this.bytes += bytes;
  }

  releaseResponseBytes(reservation) {
    if (!reservation || reservation.released) return;
    this.reservedBytes -= reservation.remaining;
    reservation.remaining = 0;
    reservation.released = true;
  }

  snapshot() {
    return {
      requests: this.requests,
      requestLimit: this.requestLimit,
      bytes: this.bytes,
      reservedBytes: this.reservedBytes,
      byteLimit: this.byteLimit,
    };
  }
}

function parseDeclaredBytes(value, headerName) {
  if (value === null) return null;
  if (!/^\d+$/.test(value)) {
    throw new WarmError(`${headerName} must be a non-negative integer`, {
      fatal: true,
      responseBytes: 0,
    });
  }
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed)) {
    throw new WarmError(`${headerName} exceeds the safe integer range`, {
      fatal: true,
      responseBytes: 0,
    });
  }
  return parsed;
}

function declaredResponseBytes(response) {
  const contentLength = parseDeclaredBytes(
    response.headers.get('content-length'),
    'Content-Length'
  );
  const skillstoreLength = parseDeclaredBytes(
    response.headers.get('x-skillstore-response-bytes'),
    'x-skillstore-response-bytes'
  );
  if (contentLength === null && skillstoreLength === null) {
    throw new WarmError(
      'Response is missing Content-Length and x-skillstore-response-bytes',
      { fatal: true, responseBytes: 0 }
    );
  }
  if (contentLength !== null && skillstoreLength !== null && contentLength !== skillstoreLength) {
    throw new WarmError(
      `Conflicting response sizes: Content-Length=${contentLength}, x-skillstore-response-bytes=${skillstoreLength}`,
      { fatal: true, responseBytes: 0 }
    );
  }
  return contentLength ?? skillstoreLength;
}

async function cancelBody(body, reason) {
  if (!body) return;
  try {
    await body.cancel(reason);
  } catch {
    // The body may already be locked/cancelled by fetch abort propagation.
  }
}

async function readResponseBody(response, context, url, signal, allowEdgeTransform) {
  const body = response.body;
  let reservation = null;
  let declaredBytes;
  // Cloudflare may rewrite canonical HTML (for example Rocket Loader and JSD)
  // after the Pages function has emitted its origin byte count. Only page
  // responses get this bounded allowance; every other response stays exact.
  const edgeAllowance = allowEdgeTransform ? MAX_EDGE_TRANSFORM_OVERHEAD : 0;
  try {
    declaredBytes = declaredResponseBytes(response);
    const reservationBytes = declaredBytes + edgeAllowance;
    if (!Number.isSafeInteger(reservationBytes)) {
      throw new WarmError(`Response reservation exceeds the safe integer range for ${url}`, {
        fatal: true,
        responseBytes: 0,
      });
    }
    // This synchronous reservation occurs before getReader()/reader.read(), so
    // concurrent responses cannot collectively cross the hard run budget.
    reservation = context.budget.reserveResponseBytes(reservationBytes, url);
  } catch (error) {
    const failure = error instanceof WarmError
      ? error
      : new WarmError(error instanceof Error ? error.message : String(error), { fatal: true });
    failure.details = {
      ...failure.details,
      declared: Number.isSafeInteger(declaredBytes) ? declaredBytes : null,
      actual: 0,
      edgeDelta: Number.isSafeInteger(declaredBytes) ? -declaredBytes : null,
    };
    const fatal = context.abortRun(failure);
    await cancelBody(body, fatal);
    throw fatal;
  }

  if (!body) {
    context.budget.releaseResponseBytes(reservation);
    if (declaredBytes === 0) {
      return {
        body: new Uint8Array(),
        declared: 0,
        actual: 0,
        edgeDelta: 0,
      };
    }
    const fatal = context.abortRun(new WarmError(
      `Response body ended before its declared ${declaredBytes} bytes for ${url}`,
      {
        fatal: true,
        responseBytes: 0,
        declared: declaredBytes,
        actual: 0,
        edgeDelta: -declaredBytes,
      }
    ));
    throw fatal;
  }

  const reader = body.getReader();
  const chunks = [];
  let bytesRead = 0;
  const cancelReader = () => {
    reader.cancel(signal.reason || new Error('request aborted')).catch(() => {});
  };
  signal.addEventListener('abort', cancelReader, { once: true });

  try {
    while (true) {
      if (signal.aborted) throw signal.reason || new Error('request aborted');
      const { done, value } = await reader.read();
      if (signal.aborted) throw signal.reason || new Error('request aborted');
      if (done) break;
      const chunk = value instanceof Uint8Array ? value : new Uint8Array(value);
      if (chunk.byteLength > reservation.remaining) {
        const actual = bytesRead + chunk.byteLength;
        const fatal = context.abortRun(new WarmError(
          allowEdgeTransform
            ? `HTML response body exceeded declared bytes plus the ${MAX_EDGE_TRANSFORM_OVERHEAD}-byte edge transform allowance for ${url}`
            : `Response body exceeded its declared ${declaredBytes} bytes for ${url}`,
          {
            fatal: true,
            responseBytes: actual,
            chunkBytes: chunk.byteLength,
            declared: declaredBytes,
            actual,
            edgeDelta: actual - declaredBytes,
          }
        ));
        await reader.cancel(fatal).catch(() => {});
        throw fatal;
      }
      try {
        context.budget.consumeBytes(chunk.byteLength, url, reservation, bytesRead);
      } catch (error) {
        const actual = bytesRead + chunk.byteLength;
        const failure = error instanceof WarmError
          ? error
          : new WarmError(error instanceof Error ? error.message : String(error), { fatal: true });
        failure.details = {
          ...failure.details,
          declared: declaredBytes,
          actual,
          edgeDelta: actual - declaredBytes,
        };
        const fatal = context.abortRun(failure);
        await reader.cancel(fatal).catch(() => {});
        throw fatal;
      }
      chunks.push(chunk);
      bytesRead += chunk.byteLength;
    }
    const edgeDelta = bytesRead - declaredBytes;
    if (allowEdgeTransform && edgeDelta < 0) {
      throw context.abortRun(new WarmError(
        `HTML response body ended at ${bytesRead} bytes; expected at least its declared ${declaredBytes} bytes for ${url}`,
        {
          fatal: true,
          responseBytes: bytesRead,
          declared: declaredBytes,
          actual: bytesRead,
          edgeDelta,
        }
      ));
    }
    if (!allowEdgeTransform && edgeDelta !== 0) {
      throw context.abortRun(new WarmError(
        `Response body ended at ${bytesRead} bytes; expected ${declaredBytes} for ${url}`,
        {
          fatal: true,
          responseBytes: bytesRead,
          declared: declaredBytes,
          actual: bytesRead,
          edgeDelta,
        }
      ));
    }
  } finally {
    signal.removeEventListener('abort', cancelReader);
    context.budget.releaseResponseBytes(reservation);
  }

  const result = new Uint8Array(bytesRead);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return {
    body: result,
    declared: declaredBytes,
    actual: bytesRead,
    edgeDelta: bytesRead - declaredBytes,
  };
}

async function sleepUnlessAborted(context, milliseconds) {
  const signal = context.runAbortController.signal;
  if (signal.aborted) throw context.abortReason || signal.reason;
  let abortListener;
  try {
    await Promise.race([
      context.sleep(milliseconds),
      new Promise((_, reject) => {
        abortListener = () => reject(context.abortReason || signal.reason);
        signal.addEventListener('abort', abortListener, { once: true });
      }),
    ]);
  } finally {
    if (abortListener) signal.removeEventListener('abort', abortListener);
  }
  if (signal.aborted) throw context.abortReason || signal.reason;
}

function makeRecord({
  phase,
  kind,
  slug = null,
  locale = null,
  url,
  attempt,
  status,
  cache = null,
  bytes,
  response,
  buildToken = null,
  declared = null,
  actual = null,
  edgeDelta = null,
  error = null,
}) {
  const cfRay = response?.headers?.get('cf-ray') || null;
  return {
    timestamp: new Date().toISOString(),
    phase,
    kind,
    slug,
    locale,
    url,
    attempt,
    status,
    cache,
    bytes,
    declared,
    actual,
    edgeDelta,
    cfRay,
    colo: coloFromRay(cfRay),
    buildToken,
    ok: !error && status >= 200 && status < 300,
    error,
  };
}

async function fetchRecorded(context, request) {
  const url = String(request.url);
  if (context.abortReason) throw context.abortReason;
  try {
    context.budget.reserveRequest(url);
  } catch (error) {
    throw context.abortRun(error);
  }
  const timer = timeoutSignal(
    request.timeoutMs ?? context.timeoutMs,
    context.runAbortController.signal
  );
  const fetchHeaders = new Headers(request.headers);
  fetchHeaders.set('Accept-Encoding', 'identity');
  let response;
  let body;
  let bodyMetadata;
  try {
    response = await context.fetchImpl(url, {
      method: 'GET',
      headers: fetchHeaders,
      redirect: 'follow',
      signal: timer.signal,
    });
    bodyMetadata = await readResponseBody(
      response,
      context,
      url,
      timer.signal,
      request.kind === 'page'
    );
    body = bodyMetadata.body;
  } catch (error) {
    const effectiveError = context.abortReason || error;
    const message = effectiveError instanceof Error ? effectiveError.message : String(effectiveError);
    const responseBytes = error instanceof WarmError && Number.isSafeInteger(error.details?.responseBytes)
      ? error.details.responseBytes
      : contentBytes(body);
    const record = makeRecord({
      ...request,
      url,
      status: response?.status || 0,
      bytes: responseBytes,
      response,
      declared: error instanceof WarmError ? error.details?.declared ?? null : null,
      actual: error instanceof WarmError ? error.details?.actual ?? responseBytes : responseBytes,
      edgeDelta: error instanceof WarmError ? error.details?.edgeDelta ?? null : null,
      error: message,
    });
    await context.report(record);
    throw effectiveError instanceof WarmError
      ? effectiveError
      : new WarmError(`Request failed for ${url}: ${message}`);
  } finally {
    timer.clear();
  }

  const buildToken = response.headers.get(context.buildHeader);
  const cache = request.cacheHeader
    ? (response.headers.get(request.cacheHeader) || '').trim().toUpperCase() || null
    : null;
  const record = makeRecord({
    ...request,
    url,
    status: response.status,
    cache,
    bytes: contentBytes(body),
    response,
    buildToken,
    declared: bodyMetadata.declared,
    actual: bodyMetadata.actual,
    edgeDelta: bodyMetadata.edgeDelta,
  });
  await context.report(record);
  return { response, body, buildToken, cache, record };
}

async function assertPinnedBuild(context, result, source) {
  let token;
  try {
    token = requireBuildToken(result.buildToken, source);
  } catch (error) {
    const failure = new WarmError(error instanceof Error ? error.message : String(error), {
      fatal: true,
      source,
    });
    throw context.abortRun(failure);
  }
  if (token !== context.buildToken) {
    const failure = new WarmError(`Production deployment changed during warm: expected ${context.buildToken}, received ${token}`, {
      expected: context.buildToken,
      actual: token,
      source,
      fatal: true,
    });
    throw context.abortRun(failure);
  }
}

async function probeBuild(context, phase) {
  try {
    const url = new URL('/_app/version.json', `${context.siteUrl}/`);
    const result = await fetchRecorded(context, {
      phase,
      kind: 'build',
      url,
      attempt: 1,
      status: 0,
      bytes: 0,
      headers: {
        Accept: 'application/json',
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
        'User-Agent': context.userAgent,
        'X-Skillstore-Callback': 'true',
      },
    });
    if (!result.response.ok) {
      throw new WarmError(`Build probe returned HTTP ${result.response.status}`);
    }

    const headerToken = requireBuildToken(result.buildToken, 'build probe');
    let payload;
    try {
      payload = JSON.parse(new TextDecoder().decode(result.body));
    } catch {
      throw new WarmError('Build probe did not return valid JSON');
    }
    if (payload?.version !== headerToken) {
      throw new WarmError(`Build probe mismatch: version.json=${payload?.version || '<missing>'}, header=${headerToken}`);
    }
    return headerToken;
  } catch (error) {
    if (context.abortReason) throw context.abortReason;
    const failure = new WarmError(
      error instanceof Error ? error.message : String(error),
      { fatal: true, phase }
    );
    throw context.abortRun(failure);
  }
}

async function warmEndpoint(context, item) {
  const baseUrl = new URL(item.url);
  const endpointStartedAt = context.now();
  const endpointWindowMs = endpointWindow(
    String(baseUrl),
    context.retryWindowMinMs,
    context.retryWindowMaxMs
  );
  const deadlineAt = endpointStartedAt + endpointWindowMs;
  const headers = {
    Accept: item.accept,
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
    'User-Agent': context.userAgent,
    'X-Skillstore-Callback': 'true',
  };

  const remainingMs = () => Math.max(0, deadlineAt - context.now());
  const deadlineError = (phase) => new WarmError(
    `${item.kind} ${baseUrl} exhausted its ${endpointWindowMs}ms endpoint deadline during ${phase}`,
    {
      deadlineAt,
      elapsedMs: context.now() - endpointStartedAt,
      phase,
    }
  );
  const verificationReserveMs = Math.min(
    context.timeoutMs,
    VERIFICATION_RESERVE_PER_REQUEST_MS
  ) * 2;

  let hitResult = null;
  for (let attempt = 1; attempt <= context.maxAttempts; attempt++) {
    if (attempt > 1) {
      const availableForDelay = remainingMs() - verificationReserveMs - 1;
      if (availableForDelay <= 0) throw deadlineError('inner-cache backoff');
      const delayMs = Math.min(retryDelay(String(baseUrl), attempt), availableForDelay);
      await sleepUnlessAborted(context, delayMs);
      if (remainingMs() <= verificationReserveMs) throw deadlineError('inner-cache backoff');
    }

    const innerTimeoutMs = Math.min(
      context.timeoutMs,
      remainingMs() - verificationReserveMs
    );
    if (innerTimeoutMs <= 0) throw deadlineError('inner-cache request');

    let result;
    try {
      result = await fetchRecorded(context, {
        phase: 'inner-cache',
        kind: item.kind,
        slug: item.slug,
        locale: item.locale,
        url: baseUrl,
        attempt,
        status: 0,
        bytes: 0,
        cacheHeader: item.cacheHeader,
        headers,
        timeoutMs: innerTimeoutMs,
      });
      await assertPinnedBuild(context, result, `${item.kind} ${baseUrl}`);
    } catch (error) {
      if (error instanceof WarmError && error.details?.fatal) {
        throw context.abortRun(error);
      }
      if (attempt < context.maxAttempts) continue;
      throw error;
    }

    if (result.response.ok && result.cache === 'HIT') {
      hitResult = result;
      break;
    }

    const retryableStatus = RETRYABLE_STATUSES.has(result.response.status);
    const retryableCache = result.response.ok && RETRYABLE_CACHE_STATES.has(result.cache);
    if (!retryableStatus && !retryableCache) {
      throw new WarmError(
        `${item.kind} ${baseUrl} returned HTTP ${result.response.status} with ${item.cacheHeader}=${result.cache || '<missing>'}`
      );
    }
  }

  if (!hitResult) {
    throw new WarmError(
      `${item.kind} ${baseUrl} never reached ${item.cacheHeader}=HIT after ${context.maxAttempts} attempts`
    );
  }

  const verificationUrl = withBuildToken(baseUrl, context.buildToken);
  const verifications = [];
  for (let attempt = 1; attempt <= 2; attempt++) {
    if (context.abortReason) throw context.abortReason;
    const requestsRemaining = 3 - attempt;
    const verificationTimeoutMs = Math.min(
      context.timeoutMs,
      Math.floor(remainingMs() / requestsRemaining)
    );
    if (verificationTimeoutMs <= 0) throw deadlineError(`ordinary verification ${attempt}`);

    const verification = await fetchRecorded(context, {
      phase: 'ordinary-verification',
      kind: item.kind,
      slug: item.slug,
      locale: item.locale,
      url: verificationUrl,
      attempt,
      status: 0,
      bytes: 0,
      cacheHeader: item.cacheHeader,
      headers: {
        Accept: item.accept,
        'User-Agent': context.userAgent,
        'X-Skillstore-Callback': 'true',
      },
      timeoutMs: verificationTimeoutMs,
    });
    await assertPinnedBuild(
      context,
      verification,
      `${item.kind} ordinary verification ${attempt} ${verificationUrl}`
    );
    if (!verification.response.ok || verification.cache !== 'HIT') {
      throw new WarmError(
        `${item.kind} ordinary verification ${attempt} replayed a non-HIT response: HTTP ${verification.response.status}, ${item.cacheHeader}=${verification.cache || '<missing>'}`
      );
    }
    verifications.push(verification);
  }

  return {
    kind: item.kind,
    slug: item.slug,
    locale: item.locale,
    url: String(baseUrl),
    innerAttempts: hitResult.record.attempt,
    bytes: hitResult.record.bytes + verifications.reduce(
      (total, result) => total + result.record.bytes,
      0
    ),
  };
}

async function mapWithConcurrency(items, concurrency, mapper) {
  const results = new Array(items.length);
  let cursor = 0;
  let stopped = false;
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (!stopped) {
      const index = cursor++;
      if (index >= items.length) return;
      try {
        results[index] = { ok: true, value: await mapper(items[index], index) };
      } catch (error) {
        results[index] = { ok: false, error };
        stopped = true;
      }
    }
  });
  await Promise.all(workers);
  return results.filter(Boolean);
}

function summarizeFailures(results) {
  return results
    .filter((result) => !result.ok)
    .map((result) => result.error instanceof Error ? result.error.message : String(result.error));
}

function endpointItems(options, slugs) {
  const api = slugs.map((slug) => ({
    kind: 'api',
    slug,
    locale: 'en',
    url: buildSkillApiUrl(options.siteUrl, slug),
    cacheHeader: options.apiCacheHeader,
    accept: 'application/json',
  }));
  const pages = slugs.flatMap((slug) => options.locales.map((locale) => ({
    kind: 'page',
    slug,
    locale,
    url: buildSkillPageUrl(options.siteUrl, slug, locale),
    cacheHeader: options.pageCacheHeader,
    accept: 'text/html',
  })));
  const zips = options.warmZip ? slugs.map((slug) => ({
    kind: 'zip',
    slug,
    locale: null,
    url: buildSkillZipUrl(options.siteUrl, slug),
    cacheHeader: options.zipCacheHeader,
    accept: 'application/zip',
  })) : [];
  return { api, pages, zips };
}

export async function runWarm(rawOptions) {
  const options = {
    ...DEFAULTS,
    ...rawOptions,
    siteUrl: normalizeSiteUrl(rawOptions.siteUrl || DEFAULTS.siteUrl),
    locales: rawOptions.locales || DEFAULTS.locales,
    concurrency: parsePositiveInteger(rawOptions.concurrency ?? DEFAULTS.concurrency, 'concurrency'),
    maxAttempts: parsePositiveInteger(rawOptions.maxAttempts ?? DEFAULTS.maxAttempts, 'max attempts'),
    retryWindowMinMs: Number(rawOptions.retryWindowMinMs ?? DEFAULTS.retryWindowMinMs),
    retryWindowMaxMs: Number(rawOptions.retryWindowMaxMs ?? DEFAULTS.retryWindowMaxMs),
    timeoutMs: parsePositiveInteger(rawOptions.timeoutMs ?? DEFAULTS.timeoutMs, 'timeout'),
    requestBudget: parsePositiveInteger(rawOptions.requestBudget, 'request budget'),
    byteBudget: parsePositiveInteger(rawOptions.byteBudget, 'byte budget'),
    fetchImpl: rawOptions.fetchImpl || globalThis.fetch,
    sleep: rawOptions.sleep || ((milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))),
    now: rawOptions.now || (() => Date.now()),
    report: rawOptions.report || (() => {}),
    userAgent: rawOptions.userAgent || 'GitHub-Actions/SkillstoreCacheWarmer',
    warmZip: rawOptions.warmZip === true,
  };
  if (typeof options.fetchImpl !== 'function') throw new WarmError('fetch implementation is required');
  if (!Array.isArray(options.locales) || options.locales.length === 0) {
    throw new WarmError('At least one locale is required');
  }
  if (!Number.isSafeInteger(options.retryWindowMinMs) || options.retryWindowMinMs <= 0 ||
      !Number.isSafeInteger(options.retryWindowMaxMs) || options.retryWindowMaxMs < options.retryWindowMinMs ||
      options.retryWindowMaxMs > 120_000) {
    throw new WarmError(
      'Retry window must use integer milliseconds satisfying 0 < minimum <= maximum <= 120000'
    );
  }

  const slugs = normalizeSlugs(rawOptions.slugs);
  const items = endpointItems(options, slugs);
  const minimumRequests = 2 + (items.api.length + items.pages.length + items.zips.length) * 3;
  if (options.requestBudget < minimumRequests) {
    throw new WarmError(
      `Request budget ${options.requestBudget} is below the minimum ${minimumRequests} required for one inner request plus two ordinary verifications per endpoint`
    );
  }

  const budget = new Budget(options.requestBudget, options.byteBudget);
  const runAbortController = new AbortController();
  const context = {
    ...options,
    budget,
    buildToken: null,
    abortReason: null,
    runAbortController,
    abortRun(error) {
      const failure = error instanceof WarmError
        ? error
        : new WarmError(error instanceof Error ? error.message : String(error), { fatal: true });
      if (!context.abortReason) context.abortReason = failure;
      if (!runAbortController.signal.aborted) runAbortController.abort(context.abortReason);
      return context.abortReason;
    },
  };
  const startedAt = new Date().toISOString();
  const failures = [];
  const completed = [];
  let failedEndpointCount = 0;

  try {
    const pinned = await probeBuild(context, 'build-start');
    if (rawOptions.expectedBuildToken && pinned !== rawOptions.expectedBuildToken) {
      throw context.abortRun(new WarmError(
        `Active build ${pinned} does not match expected build ${rawOptions.expectedBuildToken}`,
        { fatal: true }
      ));
    }
    context.buildToken = pinned;

    const apiResults = await mapWithConcurrency(items.api, options.concurrency, (item) => warmEndpoint(context, item));
    const apiFailures = summarizeFailures(apiResults);
    failedEndpointCount += apiFailures.length;
    failures.push(...apiFailures);
    completed.push(...apiResults.filter((result) => result.ok).map((result) => result.value));

    if (failures.length === 0) {
      const pageResults = await mapWithConcurrency(items.pages, options.concurrency, (item) => warmEndpoint(context, item));
      const pageFailures = summarizeFailures(pageResults);
      failedEndpointCount += pageFailures.length;
      failures.push(...pageFailures);
      completed.push(...pageResults.filter((result) => result.ok).map((result) => result.value));
    }

    if (failures.length === 0 && items.zips.length > 0) {
      const zipResults = await mapWithConcurrency(items.zips, Math.min(options.concurrency, 2), (item) => warmEndpoint(context, item));
      const zipFailures = summarizeFailures(zipResults);
      failedEndpointCount += zipFailures.length;
      failures.push(...zipFailures);
      completed.push(...zipResults.filter((result) => result.ok).map((result) => result.value));
    }
  } catch (error) {
    failures.push(error instanceof Error ? error.message : String(error));
  } finally {
    if (context.buildToken && !runAbortController.signal.aborted) {
      try {
        const finalToken = await probeBuild(context, 'build-end');
        if (finalToken !== context.buildToken) {
          const failure = context.abortRun(new WarmError(
            `Production deployment changed before completion: expected ${context.buildToken}, received ${finalToken}`,
            { fatal: true }
          ));
          failures.push(failure.message);
        }
      } catch (error) {
        failures.push(error instanceof Error ? error.message : String(error));
      }
    }
  }

  const endpointCounts = completed.reduce((counts, item) => {
    counts[item.kind] = (counts[item.kind] || 0) + 1;
    return counts;
  }, { api: 0, page: 0, zip: 0 });
  const plannedEndpointTotal = items.api.length + items.pages.length + items.zips.length;
  const completedEndpointTotal = endpointCounts.api + endpointCounts.page + endpointCounts.zip;
  return {
    success: failures.length === 0,
    mode: rawOptions.mode || 'warm',
    scope: rawOptions.scope || 'explicit',
    startedAt,
    finishedAt: new Date().toISOString(),
    buildToken: context.buildToken,
    slugs: slugs.length,
    locales: options.locales.length,
    plannedEndpoints: {
      api: items.api.length,
      page: items.pages.length,
      zip: items.zips.length,
    },
    completedEndpoints: endpointCounts,
    failedEndpoints: failedEndpointCount,
    skippedEndpoints: Math.max(0, plannedEndpointTotal - completedEndpointTotal - failedEndpointCount),
    failureCount: failures.length,
    failures,
    budget: budget.snapshot(),
  };
}

function parseArguments(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index++) {
    const current = argv[index];
    if (!current.startsWith('--')) throw new WarmError(`Unexpected argument: ${current}`);
    const name = current.slice(2);
    if (name === 'warm-zip') {
      args.warmZip = true;
      continue;
    }
    const value = argv[++index];
    if (value === undefined) throw new WarmError(`Missing value for --${name}`);
    args[name] = value;
  }
  return args;
}

function markdownSummary(summary) {
  const status = summary.success ? '✅ Passed' : '❌ Failed';
  const failures = summary.failures.length
    ? `\n\n### Failures\n\n${summary.failures.map((failure) => `- ${failure}`).join('\n')}`
    : '';
  return `## Skill cache warm verification\n\n` +
    `| Metric | Value |\n|---|---:|\n` +
    `| Result | ${status} |\n` +
    `| Mode | \`${summary.mode}\` |\n` +
    `| Scope | \`${summary.scope}\` |\n` +
    `| Build | \`${summary.buildToken || 'unavailable'}\` |\n` +
    `| Skills | ${summary.slugs} |\n` +
    `| API endpoints | ${summary.completedEndpoints.api}/${summary.plannedEndpoints.api} |\n` +
    `| Page endpoints | ${summary.completedEndpoints.page}/${summary.plannedEndpoints.page} |\n` +
    `| ZIP endpoints | ${summary.completedEndpoints.zip}/${summary.plannedEndpoints.zip} |\n` +
    `| HTTP requests | ${summary.budget.requests}/${summary.budget.requestLimit} |\n` +
    `| Response bytes | ${summary.budget.bytes}/${summary.budget.byteLimit} |\n` +
    `| Failed endpoints | ${summary.failedEndpoints} |\n` +
    `| Skipped endpoints | ${summary.skippedEndpoints} |\n` +
    `| Failure messages | ${summary.failureCount} |${failures}\n`;
}

async function cli(argv) {
  const args = parseArguments(argv);
  const slugsFile = args['slugs-file'];
  if (!slugsFile) throw new WarmError('--slugs-file is required');
  const reportPath = args.report || 'warm-cache-report.jsonl';
  const summaryPath = args.summary || 'warm-cache-summary.json';
  const stream = createWriteStream(reportPath, { flags: 'w' });
  const report = (record) => new Promise((resolve, reject) => {
    const line = `${JSON.stringify(record)}\n`;
    const onError = (error) => {
      stream.off('error', onError);
      reject(error);
    };
    stream.once('error', onError);
    stream.write(line, () => {
      stream.off('error', onError);
      resolve();
    });
  });

  let summary;
  try {
    const slugs = normalizeSlugs(await readFile(slugsFile, 'utf8'));
    summary = await runWarm({
      slugs,
      siteUrl: args['site-url'] || process.env.SITE_URL || DEFAULTS.siteUrl,
      locales: String(args.locales || process.env.LOCALES || DEFAULTS.locales.join(' ')).split(/[\s,]+/).filter(Boolean),
      concurrency: args.concurrency || process.env.CONCURRENCY || DEFAULTS.concurrency,
      maxAttempts: args['max-attempts'] || process.env.MAX_ATTEMPTS || DEFAULTS.maxAttempts,
      retryWindowMinMs: args['retry-window-min-ms'] ?? process.env.RETRY_WINDOW_MIN_MS ?? DEFAULTS.retryWindowMinMs,
      retryWindowMaxMs: args['retry-window-max-ms'] ?? process.env.RETRY_WINDOW_MAX_MS ?? DEFAULTS.retryWindowMaxMs,
      timeoutMs: args['timeout-ms'] || process.env.REQUEST_TIMEOUT_MS || DEFAULTS.timeoutMs,
      requestBudget: args['request-budget'] || process.env.REQUEST_BUDGET,
      byteBudget: args['byte-budget'] || process.env.BYTE_BUDGET,
      buildHeader: args['build-header'] || process.env.BUILD_HEADER || DEFAULTS.buildHeader,
      apiCacheHeader: args['api-cache-header'] || process.env.API_CACHE_HEADER || DEFAULTS.apiCacheHeader,
      pageCacheHeader: args['page-cache-header'] || process.env.PAGE_CACHE_HEADER || DEFAULTS.pageCacheHeader,
      expectedBuildToken: args['expected-build-token'] || process.env.EXPECTED_BUILD_TOKEN || null,
      mode: args.mode || process.env.WARM_MODE || 'warm',
      scope: args.scope || process.env.WARM_SCOPE || 'explicit',
      warmZip: args.warmZip,
      report,
    });
  } finally {
    await new Promise((resolve) => stream.end(resolve));
  }

  await writeFile(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  const markdown = markdownSummary(summary);
  process.stdout.write(`${markdown}\n`);
  if (process.env.GITHUB_STEP_SUMMARY) {
    await writeFile(process.env.GITHUB_STEP_SUMMARY, markdown, { flag: 'a' });
  }
  if (!summary.success) process.exitCode = 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  cli(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
