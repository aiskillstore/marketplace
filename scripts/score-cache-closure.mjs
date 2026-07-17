#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { appendFileSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

function fail(message) {
  throw new Error(message);
}

function readOption(args, name, { fallback, required = false } = {}) {
  const index = args.indexOf(name);
  if (index < 0) {
    if (required) fail(`missing required option ${name}`);
    return fallback;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) {
    fail(`missing value for ${name}`);
  }
  return args[index + 1];
}

function positiveInteger(value, name, maximum) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1 || (maximum && parsed > maximum)) {
    fail(`${name} must be an integer between 1 and ${maximum || Number.MAX_SAFE_INTEGER}`);
  }
  return parsed;
}

function nonnegativeInteger(value, name, maximum) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 0 || (maximum !== undefined && parsed > maximum)) {
    fail(`${name} must be an integer between 0 and ${maximum ?? Number.MAX_SAFE_INTEGER}`);
  }
  return parsed;
}

export function normalizeSlugs(values, { allowEmpty = false, maximum = 10_000 } = {}) {
  const slugs = [...new Set(values.map((value) => String(value).trim()).filter(Boolean))].sort();
  if (!allowEmpty && slugs.length === 0) fail('slug set is empty');
  if (slugs.length > maximum) fail(`slug count ${slugs.length} exceeds maximum ${maximum}`);
  for (const slug of slugs) {
    if (!SLUG_RE.test(slug)) fail(`invalid canonical slug: ${slug}`);
  }
  return slugs;
}

function lastMetric(log, name) {
  const matches = [...log.matchAll(new RegExp(`${name}:\\s*(\\d+)`, 'g'))];
  if (matches.length === 0) fail(`source score log is missing ${name}`);
  return Number(matches.at(-1)[1]);
}

export function parseScoreRunLog(log) {
  const failureMatches = [...log.matchAll(/score ultimately failed for slug=([a-z0-9][a-z0-9-]*) after \d+ attempts/g)];
  const failedSlugs = normalizeSlugs(failureMatches.map((match) => match[1]), { allowEmpty: true });
  const processed = lastMetric(log, 'Processed');
  const updated = lastMetric(log, 'Updated');
  const errors = lastMetric(log, 'Errors');

  if (processed !== updated + errors) {
    fail(`source score summary is inconsistent: processed=${processed}, updated=${updated}, errors=${errors}`);
  }
  if (failureMatches.length !== failedSlugs.length) {
    fail(`source score log repeats terminal failures: matches=${failureMatches.length}, unique=${failedSlugs.length}`);
  }
  if (failedSlugs.length !== errors) {
    fail(`source score failure count mismatch: log=${failedSlugs.length}, summary=${errors}`);
  }
  return { errors, failedSlugs, processed, updated };
}

function recoveryCount(value, name) {
  if (!Number.isSafeInteger(value) || value < 0 || value > 10_000) {
    fail(`recovery result ${name} must be an integer between 0 and 10000`);
  }
  return value;
}

export function parseRecoveryResult({ failedText, metadata, successfulText }) {
  if (metadata?.schemaVersion !== 1) fail('unsupported recovery result schema');
  const requestedCount = recoveryCount(metadata.requestedCount, 'requestedCount');
  const successfulCount = recoveryCount(metadata.successfulCount, 'successfulCount');
  const failedCount = recoveryCount(metadata.failedCount, 'failedCount');
  const causallyProvenCount = recoveryCount(metadata.causallyProvenCount, 'causallyProvenCount');
  if (requestedCount !== successfulCount + failedCount) {
    fail('recovery result counts do not reconcile');
  }
  if (causallyProvenCount !== successfulCount) {
    fail('recovery result does not causally prove every success');
  }
  if (failedCount === 0) fail('recovery result has no residual failures');

  const successfulSlugs = normalizeSlugs(successfulText.split(/\r?\n/), { allowEmpty: true });
  const failedSlugs = normalizeSlugs(failedText.split(/\r?\n/));
  if (successfulSlugs.length !== successfulCount || failedSlugs.length !== failedCount) {
    fail('recovery result slug files do not match metadata counts');
  }
  const successfulSet = new Set(successfulSlugs);
  const overlap = failedSlugs.filter((slug) => successfulSet.has(slug));
  if (overlap.length > 0) fail(`recovery result success/failure overlap: ${overlap.slice(0, 10).join(', ')}`);
  if (successfulSlugs.length + failedSlugs.length !== requestedCount) {
    fail('recovery result slug union does not match requested count');
  }
  return { failedCount, failedSlugs, requestedCount, successfulCount };
}

export async function fetchApprovedCatalog({ fetchImpl = fetch, supabaseUrl, serviceRoleKey }) {
  if (!supabaseUrl || !serviceRoleKey) fail('Supabase credentials are required');
  const slugs = [];
  const pageSize = 1000;
  for (let offset = 0; ; offset += pageSize) {
    const url = new URL('/rest/v1/skills', supabaseUrl);
    url.searchParams.set('select', 'slug');
    url.searchParams.set('public_eligible', 'eq.true');
    url.searchParams.set('order', 'slug.asc');
    url.searchParams.set('limit', String(pageSize));
    url.searchParams.set('offset', String(offset));
    const response = await fetchImpl(url, {
      headers: {
        Accept: 'application/json',
        'Accept-Profile': 'skillstore',
        apikey: serviceRoleKey,
        Authorization: `Bearer ${serviceRoleKey}`,
      },
    });
    if (!response.ok) fail(`approved catalog query failed: HTTP ${response.status}`);
    const page = await response.json();
    if (!Array.isArray(page)) fail('approved catalog query returned a non-array');
    for (const row of page) slugs.push(row?.slug);
    if (page.length < pageSize) break;
  }
  return normalizeSlugs(slugs);
}

export async function fetchScoreEvidence({
  fetchImpl = fetch,
  requireSnapshot = false,
  serviceRoleKey,
  slugs,
  supabaseUrl,
}) {
  if (!supabaseUrl || !serviceRoleKey) fail('Supabase credentials are required');
  const requested = normalizeSlugs(slugs);
  const requestedSet = new Set(requested);
  const rows = [];
  const pageSize = 1000;
  for (let offset = 0; ; offset += pageSize) {
    const url = new URL('/rest/v1/skills', supabaseUrl);
    url.searchParams.set(
      'select',
      'slug,quality_score,quality_tier,quality_score_calculated_at,current_quality_score_snapshot_id',
    );
    url.searchParams.set('order', 'slug.asc');
    url.searchParams.set('limit', String(pageSize));
    url.searchParams.set('offset', String(offset));
    const response = await fetchImpl(url, {
      headers: {
        Accept: 'application/json',
        'Accept-Profile': 'skillstore',
        apikey: serviceRoleKey,
        Authorization: `Bearer ${serviceRoleKey}`,
      },
    });
    if (!response.ok) fail(`score evidence query failed: HTTP ${response.status}`);
    const page = await response.json();
    if (!Array.isArray(page)) fail('score evidence query returned a non-array');
    rows.push(...page.filter((row) => requestedSet.has(row?.slug)));
    if (page.length < pageSize) break;
  }

  const bySlug = new Map();
  for (const row of rows) {
    if (bySlug.has(row.slug)) fail(`score evidence query returned duplicate slug ${row.slug}`);
    const qualityScore = row.quality_score;
    const qualityTier = row.quality_tier;
    const calculatedAt = row.quality_score_calculated_at;
    const snapshotId = row.current_quality_score_snapshot_id;
    if (qualityScore !== null && (typeof qualityScore !== 'number' || !Number.isFinite(qualityScore))) {
      fail(`invalid quality score for ${row.slug}`);
    }
    if (qualityTier !== null && typeof qualityTier !== 'string') fail(`invalid quality tier for ${row.slug}`);
    if (calculatedAt !== null && (typeof calculatedAt !== 'string' || Number.isNaN(Date.parse(calculatedAt)))) {
      fail(`invalid calculatedAt for ${row.slug}`);
    }
    if (snapshotId !== null && (typeof snapshotId !== 'string' || !/^[0-9a-f-]{36}$/.test(snapshotId))) {
      fail(`invalid score snapshot id for ${row.slug}`);
    }
    if (requireSnapshot && (qualityScore === null || calculatedAt === null || snapshotId === null)) {
      fail(`rescored slug ${row.slug} has no current score snapshot identity`);
    }
    bySlug.set(row.slug, { calculatedAt, qualityScore, qualityTier, slug: row.slug, snapshotId });
  }
  const missing = requested.filter((slug) => !bySlug.has(slug));
  if (missing.length > 0) fail(`score evidence is missing ${missing.length} slug(s): ${missing.slice(0, 10).join(', ')}`);
  return requested.map((slug) => bySlug.get(slug));
}

function scoreEvidenceBySlug(scores, name) {
  if (!Array.isArray(scores)) fail(`${name} score evidence must be an array`);
  const slugs = normalizeSlugs(scores.map((item) => item?.slug));
  if (slugs.length !== scores.length) fail(`${name} score evidence contains duplicate slugs`);
  return new Map(scores.map((item) => [item.slug, item]));
}

export function verifyScoreTransitions({ afterScores, beforeScores, runBoundary }) {
  const boundaryMs = Date.parse(runBoundary);
  if (typeof runBoundary !== 'string' || Number.isNaN(boundaryMs)) {
    fail('run boundary must be an ISO-8601 timestamp');
  }

  const beforeBySlug = scoreEvidenceBySlug(beforeScores, 'before');
  const afterBySlug = scoreEvidenceBySlug(afterScores, 'after');
  const missingBefore = [...afterBySlug.keys()].filter((slug) => !beforeBySlug.has(slug));
  if (missingBefore.length > 0) {
    fail(`before score evidence is missing ${missingBefore.length} slug(s): ${missingBefore.slice(0, 10).join(', ')}`);
  }

  const transitions = [];
  for (const [slug, after] of afterBySlug) {
    const before = beforeBySlug.get(slug);
    if (typeof after.snapshotId !== 'string' || !/^[0-9a-f-]{36}$/.test(after.snapshotId)) {
      fail(`after score evidence has no valid snapshot identity for ${slug}`);
    }
    const calculatedAtMs = Date.parse(after.calculatedAt);
    if (typeof after.calculatedAt !== 'string' || Number.isNaN(calculatedAtMs)) {
      fail(`after score evidence has no valid calculatedAt for ${slug}`);
    }

    const snapshotChanged = before.snapshotId !== after.snapshotId;
    const beforeCalculatedAtMs = Date.parse(before.calculatedAt);
    const calculatedAtAdvanced = calculatedAtMs >= boundaryMs
      && (before.calculatedAt === null || (!Number.isNaN(beforeCalculatedAtMs) && calculatedAtMs > beforeCalculatedAtMs));
    if (!snapshotChanged && !calculatedAtAdvanced) {
      fail(`${slug} did not prove a causal score write: snapshot identity is unchanged and calculatedAt did not advance past the run boundary`);
    }
    transitions.push({
      afterCalculatedAt: after.calculatedAt,
      afterSnapshotId: after.snapshotId,
      beforeCalculatedAt: before.calculatedAt,
      beforeSnapshotId: before.snapshotId,
      calculatedAtAdvanced,
      slug,
      snapshotChanged,
    });
  }

  return { provenCount: transitions.length, runBoundary, transitions };
}

class ReadbackFailure extends Error {
  constructor(code, message, { retryable = false, observedBuild = null } = {}) {
    super(message);
    this.code = code;
    this.retryable = retryable;
    this.observedBuild = observedBuild;
  }
}

function readbackFail(code, message, options) {
  throw new ReadbackFailure(code, message, options);
}

const BUILD_TOKEN_RE = /^[0-9a-f]{40}\.[a-z0-9-]+$/i;
const DEFAULT_MAX_BODY_BYTES = 1024 * 1024;
const DEFAULT_MAX_ERROR_BODY_BYTES = 64 * 1024;
const sleep = (delayMs) => new Promise((resolve) => setTimeout(resolve, delayMs));

function validBuildToken(value) {
  return typeof value === 'string' && BUILD_TOKEN_RE.test(value);
}

function canonicalSha256(values) {
  return createHash('sha256').update(`${values.join('\n')}\n`).digest('hex');
}

export function calculateReadbackBudget({
  slugCount,
  readsPerSlug = 2,
  attempts = 2,
  buildAttempts = 2,
  concurrency = 16,
  requestTimeoutMs = 5_000,
  retryDelayMaxMs = 1_000,
  buildRetryDelayMs = 15_000,
  qps = 8,
  probeRequestsPerPass = 2,
  finalizerReserveMs = 20 * 60_000,
}) {
  for (const [name, value] of Object.entries({
    slugCount, readsPerSlug, attempts, buildAttempts, concurrency,
    requestTimeoutMs, qps, probeRequestsPerPass,
  })) {
    if (!Number.isFinite(value) || value <= 0) fail(`${name} must be positive`);
  }
  const waves = Math.ceil(slugCount / concurrency);
  const detailRequests = slugCount * readsPerSlug * attempts * buildAttempts;
  const probeRequests = probeRequestsPerPass * buildAttempts;
  const requestLimit = detailRequests + probeRequests;
  const retryLimit = slugCount * readsPerSlug * Math.max(0, attempts - 1) * buildAttempts;
  // Conservative additive upper bound: serialized timeout waves + retry waits
  // + globally rate-limited issuance + probes + inter-pass delay. Adding these
  // terms intentionally over-counts overlap so the 360-minute proof is safe.
  const timeoutWavesMs = waves * readsPerSlug * attempts * requestTimeoutMs * buildAttempts;
  const retryWavesMs = waves * readsPerSlug * Math.max(0, attempts - 1)
    * retryDelayMaxMs * buildAttempts;
  const qpsIssuanceMs = Math.max(0, requestLimit - 1) * 1000 / qps;
  const probeTimeoutMs = probeRequests * requestTimeoutMs;
  const interPassDelayMs = Math.max(0, buildAttempts - 1) * buildRetryDelayMs;
  const worstCaseReadbackMs = Math.ceil(
    timeoutWavesMs + retryWavesMs + qpsIssuanceMs + probeTimeoutMs + interPassDelayMs,
  );
  return {
    parameters: {
      slugCount, readsPerSlug, attempts, buildAttempts, concurrency, requestTimeoutMs,
      retryDelayMaxMs, buildRetryDelayMs, qps, probeRequestsPerPass, finalizerReserveMs,
    },
    waves,
    detailRequests,
    probeRequests,
    requestLimit,
    retryLimit,
    timeoutWavesMs,
    retryWavesMs,
    qpsIssuanceMs: Math.ceil(qpsIssuanceMs),
    probeTimeoutMs,
    interPassDelayMs,
    worstCaseReadbackMs,
    worstCaseTotalMs: worstCaseReadbackMs + finalizerReserveMs,
  };
}

class TokenBucket {
  constructor(qps, nowImpl, sleepImpl) {
    this.capacity = qps;
    this.tokens = qps;
    this.refillPerMs = qps / 1000;
    this.last = nowImpl();
    this.now = nowImpl;
    this.sleep = sleepImpl;
    this.tail = Promise.resolve();
  }

  acquire(signal) {
    const operation = this.tail.then(async () => {
      while (true) {
        if (signal.aborted) throw signal.reason || new Error('readback aborted');
        const now = this.now();
        this.tokens = Math.min(this.capacity, this.tokens + ((now - this.last) * this.refillPerMs));
        this.last = now;
        if (this.tokens >= 1) {
          this.tokens -= 1;
          return;
        }
        await this.sleep(Math.max(1, Math.ceil((1 - this.tokens) / this.refillPerMs)));
      }
    });
    this.tail = operation.catch(() => {});
    return operation;
  }
}

function linkedRequestController(parentSignal, timeoutMs) {
  const controller = new AbortController();
  let timedOut = false;
  const onParentAbort = () => controller.abort(parentSignal.reason || new Error('readback aborted'));
  if (parentSignal.aborted) onParentAbort();
  else parentSignal.addEventListener('abort', onParentAbort, { once: true });
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort(new Error('request timed out'));
  }, timeoutMs);
  return {
    signal: controller.signal,
    timedOut: () => timedOut,
    clear() {
      clearTimeout(timer);
      parentSignal.removeEventListener('abort', onParentAbort);
    },
  };
}

async function readBoundedBody(response, { signal, maximum, timedOut }) {
  if (!response.body) return new Uint8Array();
  const reader = response.body.getReader();
  const chunks = [];
  let bytes = 0;
  const cancel = () => { reader.cancel(signal.reason).catch(() => {}); };
  signal.addEventListener('abort', cancel, { once: true });
  if (signal.aborted) cancel();
  try {
    while (true) {
      let part;
      try {
        part = await reader.read();
      } catch (error) {
        if (timedOut()) readbackFail('read_timeout', 'cache readback body timed out', { retryable: true });
        if (signal.aborted && signal.reason instanceof ReadbackFailure) throw signal.reason;
        if (signal.aborted) readbackFail('read_aborted', 'cache readback body was aborted');
        throw error;
      }
      if (part.done) break;
      const chunk = part.value instanceof Uint8Array ? part.value : new Uint8Array(part.value);
      bytes += chunk.byteLength;
      if (bytes > maximum) {
        await reader.cancel('response too large').catch(() => {});
        readbackFail('response_too_large', `cache readback body exceeded ${maximum} bytes`);
      }
      chunks.push(chunk);
    }
  } finally {
    signal.removeEventListener('abort', cancel);
    if (signal.aborted) await reader.cancel(signal.reason).catch(() => {});
  }
  if (signal.aborted) {
    if (timedOut()) readbackFail('read_timeout', 'cache readback body timed out', { retryable: true });
    if (signal.reason instanceof ReadbackFailure) throw signal.reason;
    readbackFail('read_aborted', 'cache readback body was aborted');
  }
  const body = new Uint8Array(bytes);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return body;
}

function parseRetryAfter(response, maximumMs) {
  const raw = response.headers.get('retry-after');
  if (!raw) return maximumMs;
  if (/^\d+$/.test(raw)) return Math.min(maximumMs, Number(raw) * 1000);
  const parsed = Date.parse(raw);
  return Number.isNaN(parsed) ? maximumMs : Math.min(maximumMs, Math.max(0, parsed - Date.now()));
}

async function boundedJsonRequest(runtime, url, {
  expectedBuild = null,
  errorBodyBytes = DEFAULT_MAX_ERROR_BODY_BYTES,
  headers = {},
  kind,
  onObservedBuild,
}) {
  runtime.reserveRequest();
  await runtime.bucket.acquire(runtime.signal);
  const timer = linkedRequestController(runtime.signal, runtime.timeoutMs);
  let response;
  try {
    try {
      response = await runtime.fetchImpl(url, {
        headers: {
          Accept: 'application/json',
          'Accept-Encoding': 'identity',
          'User-Agent': 'skillstore-score-cache-closure',
          ...headers,
        },
        method: 'GET',
        redirect: 'error',
        signal: timer.signal,
      });
    } catch (error) {
      if (timer.timedOut()) readbackFail('read_timeout', `cache readback GET timed out after ${runtime.timeoutMs}ms`, { retryable: true });
      if (runtime.signal.aborted && runtime.signal.reason instanceof ReadbackFailure) throw runtime.signal.reason;
      readbackFail('network_error', `cache readback GET failed: ${error instanceof Error ? error.message : String(error)}`, { retryable: true });
    }

    const observedBuild = response.headers.get('x-skillstore-build');
    if (!validBuildToken(observedBuild)) {
      response.body?.cancel('invalid build identity').catch(() => {});
      readbackFail('build_identity', `${kind} did not expose one valid build token`, { observedBuild });
    }
    onObservedBuild?.(observedBuild);
    if (expectedBuild !== null && observedBuild !== expectedBuild) {
      response.body?.cancel('build transition').catch(() => {});
      const transition = new ReadbackFailure(
        'build_transition',
        `production build changed: expected ${expectedBuild}, observed ${observedBuild}`,
        { observedBuild },
      );
      runtime.taintTransition(transition);
      throw transition;
    }

    const body = await readBoundedBody(response, {
      signal: timer.signal,
      maximum: response.ok ? runtime.maxBodyBytes : errorBodyBytes,
      timedOut: timer.timedOut,
    });
    if (!response.ok) {
      const retryable = response.status === 429 || response.status === 500 || response.status === 502
        || response.status === 503 || response.status === 504;
      const error = new ReadbackFailure(
        retryable ? 'http_retryable' : 'http_error',
        `${kind} returned HTTP ${response.status}`,
        { retryable, observedBuild },
      );
      error.retryAfterMs = (response.status === 429 || response.status === 503)
        ? parseRetryAfter(response, runtime.retryDelayMaxMs)
        : runtime.retryDelayMaxMs;
      throw error;
    }
    let payload;
    try {
      payload = JSON.parse(new TextDecoder().decode(body));
    } catch {
      readbackFail('invalid_response', `${kind} returned invalid JSON`);
    }
    return { body: payload, response, build: observedBuild };
  } finally {
    timer.clear();
  }
}

async function probeBuild(runtime, phase, expectedBuild = null) {
  const url = new URL('/_app/version.json', `${runtime.siteUrl}/`);
  const result = await boundedJsonRequest(runtime, url, {
    expectedBuild,
    headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' },
    kind: `${phase} build probe`,
    onObservedBuild: runtime.onObservedBuild,
  });
  if (result.body?.version !== result.build) {
    readbackFail('build_probe_mismatch', `version body does not match build header during ${phase}`);
  }
  return result.build;
}

async function readSkill(runtime, slug, pinnedBuild) {
  const url = new URL(`/api/skills/${encodeURIComponent(slug)}`, `${runtime.siteUrl}/`);
  url.searchParams.set('__skillstore_build', pinnedBuild);
  const result = await boundedJsonRequest(runtime, url, {
    expectedBuild: pinnedBuild,
    kind: `${slug} cache readback`,
    onObservedBuild: runtime.onObservedBuild,
  });
  if (result.body?.data?.slug !== slug) readbackFail('wrong_record', `${slug} cache readback returned the wrong record`);
  const identity = {
    build: result.build,
    cache: result.response.headers.get('x-kv-cache'),
    key: result.response.headers.get('x-kv-key'),
    version: result.response.headers.get('x-kv-version'),
    write: result.response.headers.get('x-kv-write'),
    score: {
      qualityScore: result.body?.data?.qualityScore ?? null,
      qualityTier: result.body?.data?.qualityTier ?? null,
      calculatedAt: result.body?.data?.qualityBreakdown?.calculatedAt ?? null,
    },
  };
  if (!identity.key || !identity.version || !identity.cache || !identity.write) {
    readbackFail('missing_identity', `${slug} cache readback omitted complete cache identity`);
  }
  return identity;
}

async function readSkillWithRetries(runtime, slug, pinnedBuild) {
  let lastError;
  for (let attempt = 1; attempt <= runtime.attempts; attempt += 1) {
    try {
      return await readSkill(runtime, slug, pinnedBuild);
    } catch (error) {
      lastError = error;
      if (error?.code === 'build_transition') throw error;
      if (!(error instanceof ReadbackFailure) || !error.retryable || attempt >= runtime.attempts) throw error;
      runtime.reserveRetry();
      const boundedBase = Math.min(runtime.retryDelayMaxMs, error.retryAfterMs ?? (attempt * 250));
      const jitteredDelay = Math.floor(boundedBase * (0.5 + (runtime.randomImpl() * 0.5)));
      await runtime.sleepImpl(jitteredDelay);
    }
  }
  throw lastError;
}

function readMatchesExpectedScore(read, expected) {
  return read.score.qualityScore === expected.qualityScore
    && read.score.qualityTier === expected.qualityTier
    && read.score.calculatedAt === expected.calculatedAt;
}

function firstReadCanClose(read) {
  return (read.cache === 'MISS' && read.write === 'STORED')
    || (read.cache === 'HIT' && read.write === 'SKIPPED');
}

export async function verifyCacheReadback({
  attempts = 2,
  buildAttempts = 2,
  buildRetryDelayMs = 15_000,
  concurrency = 16,
  expectedBuild = null,
  expectedCacheVersion,
  fetchImpl = fetch,
  siteUrl = 'https://skillstore.io',
  sleepImpl = sleep,
  expectedScores,
  timeoutMs = 5_000,
  maxBodyBytes = DEFAULT_MAX_BODY_BYTES,
  qps = 8,
  requestLimit,
  retryLimit,
  wallClockMs,
  nowImpl = Date.now,
  randomImpl = Math.random,
}) {
  if (!Array.isArray(expectedScores)) fail('expected score evidence must be an array');
  positiveInteger(attempts, 'attempts', 2);
  positiveInteger(buildAttempts, 'buildAttempts', 2);
  nonnegativeInteger(buildRetryDelayMs, 'buildRetryDelayMs', 120_000);
  positiveInteger(concurrency, 'concurrency', 16);
  positiveInteger(timeoutMs, 'timeoutMs', 5_000);
  positiveInteger(maxBodyBytes, 'maxBodyBytes', 4 * 1024 * 1024);
  positiveInteger(qps, 'qps', 16);
  if (typeof sleepImpl !== 'function') fail('sleepImpl must be a function');
  if (expectedBuild !== null && !validBuildToken(expectedBuild)) fail('expected build is invalid');
  if (expectedCacheVersion !== undefined && !/^v[1-9][0-9]*$/.test(expectedCacheVersion)) {
    fail('expected cache version must have the form vN');
  }
  const normalized = normalizeSlugs(expectedScores.map((item) => item?.slug));
  if (normalized.length !== expectedScores.length) fail('expected score evidence contains duplicate slugs');
  const expectedBySlug = new Map(expectedScores.map((item) => [item.slug, item]));
  const budget = calculateReadbackBudget({
    slugCount: normalized.length, attempts, buildAttempts, concurrency,
    requestTimeoutMs: timeoutMs, retryDelayMaxMs: 1_000,
    buildRetryDelayMs, qps, readsPerSlug: 2, probeRequestsPerPass: 2,
    finalizerReserveMs: 20 * 60_000,
  });
  const effectiveRequestLimit = requestLimit ?? budget.requestLimit;
  const effectiveRetryLimit = retryLimit ?? budget.retryLimit;
  const effectiveWallClockMs = wallClockMs ?? Math.min(340 * 60_000, Math.max(1_000, budget.worstCaseReadbackMs + 60_000));
  const globalAbort = new AbortController();
  const globalTimer = setTimeout(() => globalAbort.abort(
    new ReadbackFailure('wall_clock_budget', 'readback wall-clock budget exhausted'),
  ), effectiveWallClockMs);
  const counters = { requests: 0, retries: 0 };
  const bucket = new TokenBucket(qps, nowImpl, sleepImpl);
  const buildPasses = [];
  const rejectedPassDiagnostics = [];

  function baseRuntime(passAbort, observedBuilds, retryCounter) {
    return {
      attempts, bucket, fetchImpl, maxBodyBytes, randomImpl, siteUrl: siteUrl.replace(/\/+$/, ''),
      sleepImpl, timeoutMs, retryDelayMaxMs: 1_000, signal: passAbort.signal,
      onObservedBuild(build) { observedBuilds.add(build); },
      reserveRequest() {
        if (globalAbort.signal.aborted) throw globalAbort.signal.reason;
        if (counters.requests >= effectiveRequestLimit) readbackFail('request_budget', 'readback request budget exhausted');
        counters.requests += 1;
      },
      reserveRetry() {
        if (counters.retries >= effectiveRetryLimit) readbackFail('retry_budget', 'readback retry budget exhausted');
        counters.retries += 1;
        retryCounter.count += 1;
      },
      taintTransition(error) {
        if (!passAbort.signal.aborted) passAbort.abort(error);
      },
    };
  }

  async function runPass(attemptNumber) {
    const passAbort = new AbortController();
    const onGlobalAbort = () => passAbort.abort(globalAbort.signal.reason);
    globalAbort.signal.addEventListener('abort', onGlobalAbort, { once: true });
    const observedBuilds = new Set(expectedBuild === null ? [] : [expectedBuild]);
    const retryCounter = { count: 0 };
    const runtime = baseRuntime(passAbort, observedBuilds, retryCounter);
    const failures = [];
    const passResults = new Array(normalized.length);
    let pinnedBuild = null;
    try {
      try {
        pinnedBuild = await probeBuild(runtime, 'start', expectedBuild);
      } catch (error) {
        failures.push({ slug: '*', code: error?.code || 'unexpected_error', error: error?.message || String(error) });
        return { attemptNumber, builds: [...observedBuilds].sort(), failures, results: [], retries: retryCounter.count };
      }

      let cursor = 0;
      async function verifyOne(slug) {
        const first = await readSkillWithRetries(runtime, slug, pinnedBuild);
        const second = await readSkillWithRetries(runtime, slug, pinnedBuild);
        if (expectedCacheVersion !== undefined
          && (first.version !== expectedCacheVersion || second.version !== expectedCacheVersion)) {
          readbackFail('cache_version_mismatch', `${slug} cache version was ${first.version}/${second.version}; expected ${expectedCacheVersion}`);
        }
        if (!firstReadCanClose(first)) readbackFail('cache_state_mismatch', `${slug} first read was ${first.cache}+${first.write}`);
        const expected = expectedBySlug.get(slug);
        if (!readMatchesExpectedScore(first, expected) || !readMatchesExpectedScore(second, expected)) {
          readbackFail('score_mismatch', `${slug} API score identity does not match frozen DB evidence`);
        }
        if (second.cache !== 'HIT' || second.write !== 'SKIPPED') {
          readbackFail('cache_state_mismatch', `${slug} second read was ${second.cache}+${second.write}`);
        }
        if (first.key !== second.key || first.version !== second.version) {
          readbackFail('cache_identity_mismatch', `${slug} changed cache key/version between reads`);
        }
        return { slug, first, second };
      }

      async function worker() {
        while (!passAbort.signal.aborted) {
          const index = cursor;
          cursor += 1;
          if (index >= normalized.length) return;
          try {
            passResults[index] = await verifyOne(normalized[index]);
          } catch (error) {
            const code = error?.code || 'unexpected_error';
            failures.push({ slug: normalized[index], code, error: error?.message || String(error) });
            if (code === 'build_transition') runtime.taintTransition(error);
          }
        }
      }
      await Promise.all(Array.from({ length: Math.min(concurrency, normalized.length) }, () => worker()));
      if (!passAbort.signal.aborted) {
        try {
          await probeBuild(runtime, 'end', pinnedBuild);
        } catch (error) {
          failures.push({ slug: '*', code: error?.code || 'unexpected_error', error: error?.message || String(error) });
          if (error?.code === 'build_transition') runtime.taintTransition(error);
        }
      }
      if (passAbort.signal.reason instanceof ReadbackFailure
        && passAbort.signal.reason.code === 'build_transition'
        && !failures.some((failure) => failure.code === 'build_transition')) {
        failures.push({ slug: '*', code: 'build_transition', error: passAbort.signal.reason.message });
      }
      return {
        attemptNumber,
        builds: [...observedBuilds].sort(),
        failures,
        results: passAbort.signal.aborted ? [] : passResults.filter(Boolean),
        retries: retryCounter.count,
        pinnedBuild,
      };
    } finally {
      globalAbort.signal.removeEventListener('abort', onGlobalAbort);
      if (!passAbort.signal.aborted) passAbort.abort(new Error('pass complete'));
    }
  }

  try {
    for (let buildAttempt = 1; buildAttempt <= buildAttempts; buildAttempt += 1) {
      const pass = await runPass(buildAttempt);
      const observedFailureCodes = [...new Set(pass.failures.map((failure) => failure.code))].sort();
      const transition = observedFailureCodes.includes('build_transition');
      // A transition invalidates every other observation from this pass. Keep
      // those details only in rejectedPassDiagnostics; accepted evidence sees
      // one reason for rejection and cannot be polluted by stale retry data.
      const failureCodes = transition ? ['build_transition'] : observedFailureCodes;
      buildPasses.push({
        attempt: buildAttempt,
        builds: pass.builds,
        failureCodes,
        status: pass.failures.length === 0 ? 'accepted' : 'rejected',
      });
      if (pass.failures.length === 0 && pass.results.length === normalized.length && validBuildToken(pass.pinnedBuild)) {
        return {
          acceptedBuild: pass.pinnedBuild,
          expectedBuild: expectedBuild ?? pass.pinnedBuild,
          buildAttemptCount: buildAttempt,
          buildPasses,
          builds: [pass.pinnedBuild],
          failures: [],
          rejectedPassDiagnostics,
          results: pass.results,
          retryableReadFailures: pass.retries,
          requestBudget: {
            requestLimit: effectiveRequestLimit, requestsUsed: counters.requests,
            retryLimit: effectiveRetryLimit, retriesUsed: counters.retries,
            wallClockMs: effectiveWallClockMs, qps,
          },
          slugCount: normalized.length,
          status: 'complete',
        };
      }
      if (transition) {
        rejectedPassDiagnostics.push({ attempt: buildAttempt, failures: pass.failures, retries: pass.retries });
        if (buildAttempt < buildAttempts) {
          await sleepImpl(buildRetryDelayMs);
          continue;
        }
      }
      return {
        acceptedBuild: null,
        expectedBuild,
        buildAttemptCount: buildAttempt,
        buildPasses,
        builds: [],
        failures: pass.failures,
        rejectedPassDiagnostics,
        results: [],
        retryableReadFailures: 0,
        requestBudget: {
          requestLimit: effectiveRequestLimit, requestsUsed: counters.requests,
          retryLimit: effectiveRetryLimit, retriesUsed: counters.retries,
          wallClockMs: effectiveWallClockMs, qps,
        },
        slugCount: normalized.length,
        status: transition ? 'blocked_deployment_change' : 'failed',
      };
    }
  } finally {
    clearTimeout(globalTimer);
    if (!globalAbort.signal.aborted) globalAbort.abort(new Error('readback complete'));
  }
  throw new Error('unreachable cache readback state');
}

export async function probeListGeneration({
  expectedBuild = null,
  fetchImpl = fetch,
  maxBodyBytes = DEFAULT_MAX_BODY_BYTES,
  siteUrl = 'https://skillstore.io',
  timeoutMs = 5_000,
}) {
  if (expectedBuild !== null && !validBuildToken(expectedBuild)) fail('expected build is invalid');
  const controller = new AbortController();
  const observed = new Set();
  const counters = { requests: 0 };
  const runtime = {
    attempts: 1,
    bucket: new TokenBucket(4, Date.now, sleep),
    fetchImpl,
    maxBodyBytes,
    siteUrl: siteUrl.replace(/\/+$/, ''),
    sleepImpl: sleep,
    timeoutMs,
    retryDelayMaxMs: 1_000,
    signal: controller.signal,
    onObservedBuild(build) { observed.add(build); },
    reserveRequest() {
      counters.requests += 1;
      if (counters.requests > 3) readbackFail('request_budget', 'list generation probe exceeded 3 requests');
    },
    reserveRetry() { readbackFail('retry_budget', 'list generation probe may not retry'); },
    taintTransition(error) { if (!controller.signal.aborted) controller.abort(error); },
  };
  try {
    const pinned = await probeBuild(runtime, 'list-start', expectedBuild);
    const url = new URL('/api/skills', `${runtime.siteUrl}/`);
    url.searchParams.set('page', '1');
    url.searchParams.set('limit', '1');
    url.searchParams.set('__skillstore_build', pinned);
    const result = await boundedJsonRequest(runtime, url, {
      expectedBuild: pinned,
      headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' },
      kind: 'list generation probe',
      onObservedBuild: runtime.onObservedBuild,
    });
    if (!Array.isArray(result.body?.data)) readbackFail('wrong_record', 'list generation probe returned invalid data');
    const identity = {
      build: pinned,
      cache: result.response.headers.get('x-kv-cache'),
      key: result.response.headers.get('x-kv-key'),
      version: result.response.headers.get('x-kv-version'),
      write: result.response.headers.get('x-kv-write'),
    };
    if (!identity.cache || !identity.key || !identity.version || !identity.write) {
      readbackFail('missing_identity', 'list generation probe omitted complete cache identity');
    }
    await probeBuild(runtime, 'list-end', pinned);
    return { schemaVersion: 1, ...identity, requestsUsed: counters.requests };
  } finally {
    if (!controller.signal.aborted) controller.abort(new Error('list probe complete'));
  }
}

function closureCount(value) {
  const parsed = typeof value === 'string' && /^\d+$/.test(value) ? Number(value) : value;
  return Number.isSafeInteger(parsed) && parsed >= 0 ? parsed : null;
}

function sameJson(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function exactCanonicalSlugs(values, name) {
  if (!Array.isArray(values)) fail(`${name} must be an array`);
  const normalized = normalizeSlugs(values);
  if (normalized.length !== values.length || !sameJson(normalized, values)) {
    fail(`${name} must be one exact canonical unique slug set`);
  }
  return normalized;
}

function exactScoreMap(document, name, { requireSnapshot = true } = {}) {
  if (document?.schemaVersion !== 1 || !Array.isArray(document.scores)) fail(`${name} is invalid`);
  const slugs = exactCanonicalSlugs(document.scores.map((row) => row?.slug), `${name} slugs`);
  const map = new Map();
  for (const row of document.scores) {
    const calculatedAtValid = row.calculatedAt === null
      ? !requireSnapshot
      : typeof row.calculatedAt === 'string' && !Number.isNaN(Date.parse(row.calculatedAt));
    const snapshotValid = row.snapshotId === null
      ? !requireSnapshot
      : typeof row.snapshotId === 'string' && /^[0-9a-f-]{36}$/i.test(row.snapshotId);
    if ((row.qualityScore !== null && (typeof row.qualityScore !== 'number' || !Number.isFinite(row.qualityScore)))
      || (row.qualityTier !== null && typeof row.qualityTier !== 'string')
      || !calculatedAtValid || !snapshotValid) {
      fail(`${name} contains invalid score identity for ${row.slug}`);
    }
    map.set(row.slug, row);
  }
  return { map, rows: document.scores, slugs };
}

function workflowIdentityIsValid(identity) {
  return identity && typeof identity.repository === 'string' && /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(identity.repository)
    && typeof identity.runId === 'string' && /^[1-9][0-9]*$/.test(identity.runId)
    && Number.isSafeInteger(identity.runAttempt) && identity.runAttempt >= 1
    && typeof identity.headSha === 'string' && /^[0-9a-f]{40}$/.test(identity.headSha)
    && identity.eventName === 'workflow_dispatch'
    && identity.workflowName === 'Recover Score and Cache Closure';
}

function scoreIdentity(read) {
  return {
    qualityScore: read?.score?.qualityScore ?? null,
    qualityTier: read?.score?.qualityTier ?? null,
    calculatedAt: read?.score?.calculatedAt ?? null,
  };
}

export function finalizeClosure(input) {
  const reasons = [];
  const reject = (reason) => { if (!reasons.includes(reason)) reasons.push(reason); };
  const scope = input?.scope;
  let planned = [];
  let selected = [];
  let invalidationSlugs = [];
  let expected = null;
  let scoreStatus = 'failed';
  let invalidationStatus = 'failed';
  let readbackStatus = 'failed';
  let acceptedBuild = null;

  try {
    if (!workflowIdentityIsValid(input.workflowIdentity)) fail('current workflow identity is invalid');
    if (input.planManifestVerified !== true) fail('plan checksum manifest was not verified');
    const metadata = input.plan?.metadata;
    if (metadata?.schemaVersion !== 2 || metadata.scope !== scope) fail('plan metadata scope/schema mismatch');
    if (!sameJson(metadata.workflowIdentity, input.workflowIdentity)) fail('plan belongs to another workflow run/head');
    planned = exactCanonicalSlugs(input.plan?.plannedSlugs, 'planned slugs');
    if (metadata.slugCount !== planned.length || metadata.slugSha256 !== canonicalSha256(planned)) {
      fail('plan slug count/hash mismatch');
    }
    if (closureCount(input.plannedSlugCount) !== planned.length) fail('planned slug count summary mismatch');
    selected = exactCanonicalSlugs(input.selectedSlugs, 'selected slugs');
    if (closureCount(input.selectedSlugCount) !== selected.length) fail('selected slug count summary mismatch');
    invalidationSlugs = exactCanonicalSlugs(input.invalidationSlugs, 'invalidation slugs');
    expected = exactScoreMap(input.expectedScoreEvidence, 'expected score evidence', {
      requireSnapshot: scope !== 'approved-catalog-cache',
    });
    if (!sameJson(expected.slugs, selected)) fail('expected score evidence does not match selected slugs');

    if (scope === 'approved-catalog-cache') {
      if (!sameJson(planned, selected)) fail('approved catalog selected set differs from plan');
      if (metadata.sourceRunId !== '' || metadata.sourceIdentity !== null) fail('approved catalog cannot bind a source run');
      scoreStatus = 'not_required';
    } else if (scope === 'source-run-failures' || scope === 'recovery-run-failures') {
      const source = metadata.sourceIdentity;
      const expectedTitle = scope === 'source-run-failures'
        ? 'Recalculate Skill Scores' : 'Recover Score and Cache Closure';
      if (!source || String(source.databaseId) !== metadata.sourceRunId
        || source.displayTitle !== expectedTitle || source.status !== 'completed'
        || !['failure', 'cancelled'].includes(source.conclusion)
        || !/^[0-9a-f]{40}$/.test(source.headSha) || source.event !== 'workflow_dispatch') {
        fail('source workflow identity is invalid or stale');
      }
      if (!sameJson(planned, selected)) fail('ordinary completed closure must select every planned slug');
      const before = exactScoreMap(input.beforeScoreEvidence, 'before score evidence');
      if (!sameJson(before.slugs, planned)) fail('before score evidence differs from planned slugs');
      const score = input.score;
      if (score?.schemaVersion !== 1 || score.wrapperExit !== 0
        || score.requestedCount !== planned.length || score.successfulCount !== selected.length
        || score.failedCount !== 0 || score.causallyProvenCount !== selected.length
        || score.runBoundary !== input.scoreWriteEvidence?.runBoundary) {
        fail('score metadata does not prove complete causal writes');
      }
      const transitions = input.scoreWriteEvidence?.transitions;
      if (input.scoreWriteEvidence?.schemaVersion !== 1
        || input.scoreWriteEvidence.provenCount !== selected.length || !Array.isArray(transitions)) {
        fail('score-write evidence is invalid');
      }
      const transitionSlugs = exactCanonicalSlugs(transitions.map((row) => row?.slug), 'score transition slugs');
      if (!sameJson(transitionSlugs, selected)) fail('score transition set differs from selected slugs');
      for (const transition of transitions) {
        const beforeRow = before.map.get(transition.slug);
        const afterRow = expected.map.get(transition.slug);
        if (transition.beforeSnapshotId !== beforeRow.snapshotId
          || transition.beforeCalculatedAt !== beforeRow.calculatedAt
          || transition.afterSnapshotId !== afterRow.snapshotId
          || transition.afterCalculatedAt !== afterRow.calculatedAt
          || (transition.snapshotChanged !== true && transition.calculatedAtAdvanced !== true)) {
          fail(`score transition does not bind before/after identity for ${transition.slug}`);
        }
      }
      scoreStatus = 'complete';
    } else {
      fail('unsupported closure scope');
    }
  } catch (error) {
    reject(`score_or_plan:${error instanceof Error ? error.message : String(error)}`);
  }

  try {
    const invalidation = input.invalidation;
    const exactExpectedInvalidation = scope === 'approved-catalog-cache'
      ? selected.slice(0, 1) : selected;
    if (!sameJson(invalidationSlugs, exactExpectedInvalidation)
      || invalidation?.schemaVersion !== 2
      || invalidation.type !== 'skills'
      || !sameJson(invalidation.exactSlugs, invalidationSlugs)
      || invalidation.slugSha256 !== canonicalSha256(invalidationSlugs)
      || invalidation.expectedCount !== invalidationSlugs.length
      || invalidation.totalCount !== invalidationSlugs.length
      || invalidation.successCount !== invalidationSlugs.length
      || invalidation.failedCount !== 0
      || invalidation.listVersionBumped !== true
      || !sameJson(invalidation.contract, {
        invalidateArtifacts: false,
        invalidateDependentPacks: false,
        failOnError: true,
      })
      || !sameJson(invalidation.workflowIdentity, input.workflowIdentity)) {
      fail('invalidation contract/count/slug identity mismatch');
    }
    const before = invalidation.before;
    const after = invalidation.after;
    if (!validBuildToken(before?.build) || before.build !== after?.build
      || !sameJson(before.workflowIdentity, input.workflowIdentity)
      || !sameJson(after.workflowIdentity, input.workflowIdentity)
      || !before.key || !after.key || before.key === after.key
      || !before.version || !after.version || before.version === after.version) {
      fail('list generation before/after identity is not a stable-build bump');
    }
    invalidationStatus = 'complete';
  } catch (error) {
    reject(`invalidation:${error instanceof Error ? error.message : String(error)}`);
  }

  try {
    const readback = input.readback;
    if (![1, 2].includes(readback?.schemaVersion)
      || !sameJson(readback.workflowIdentity, input.workflowIdentity)
      || readback.slugCount !== selected.length || readback.slugSha256 !== canonicalSha256(selected)) {
      fail('readback scope/workflow/slug identity mismatch');
    }
    const passes = readback.buildPasses;
    const passCount = closureCount(readback.buildAttemptCount);
    if (!Array.isArray(passes) || passCount === null || passCount < 1 || passCount > 2
      || passes.length !== passCount || !passes.every((pass, index) => pass?.attempt === index + 1)) {
      fail('readback pass sequence exceeds the bounded contract');
    }
    const budget = readback.requestBudget;
    const recomputedBudget = readback.budget?.parameters
      ? calculateReadbackBudget(readback.budget.parameters) : null;
    if (!budget || budget.requestsUsed > budget.requestLimit || budget.retriesUsed > budget.retryLimit
      || budget.requestsUsed < 1 || budget.requestLimit < 1 || budget.qps > 16
      || !recomputedBudget || !sameJson(readback.budget, recomputedBudget)
      || !sameJson(input.preflightBudget, recomputedBudget)
      || recomputedBudget.parameters.slugCount !== selected.length
      || recomputedBudget.requestLimit !== budget.requestLimit
      || recomputedBudget.retryLimit !== budget.retryLimit
      || recomputedBudget.worstCaseTotalMs >= 360 * 60_000) {
      fail('readback request/retry/QPS/wall-clock budget evidence is invalid');
    }
    if (readback.expectedBuild !== input.invalidation?.after?.build
      || readback.expectedCacheVersion !== 'v6'
      || readback.expectedScoreSha256 !== createHash('sha256').update(JSON.stringify(expected.rows)).digest('hex')) {
      fail('readback expected cache/score identity is not bound to frozen evidence');
    }

    if (readback.status === 'complete') {
      acceptedBuild = readback.acceptedBuild;
      if (!validBuildToken(acceptedBuild) || !sameJson(readback.builds, [acceptedBuild])
        || !Array.isArray(readback.failures) || readback.failures.length !== 0
        || !Array.isArray(readback.results)) {
        fail('accepted readback build/result envelope is invalid');
      }
      const rejectedDiagnostics = readback.rejectedPassDiagnostics;
      if (!Array.isArray(rejectedDiagnostics) || rejectedDiagnostics.length !== passes.length - 1
        || !rejectedDiagnostics.every((item, index) => item?.attempt === index + 1)) {
        fail('rejected readback pass diagnostics are incomplete or stale');
      }
      for (const pass of passes.slice(0, -1)) {
        if (pass.status !== 'rejected' || !sameJson(pass.failureCodes, ['build_transition'])
          || !Array.isArray(pass.builds) || pass.builds.length < 2
          || !pass.builds.every(validBuildToken)) {
          fail('a prior readback pass was not rejected solely for a valid build transition');
        }
      }
      const last = passes.at(-1);
      if (last.status !== 'accepted' || !sameJson(last.builds, [acceptedBuild])
        || !sameJson(last.failureCodes, [])) {
        fail('last readback pass is not the unique accepted build');
      }
      const resultSlugs = exactCanonicalSlugs(readback.results.map((row) => row?.slug), 'readback result slugs');
      if (!sameJson(resultSlugs, selected)) fail('readback result set differs from selected slugs');
      for (const result of readback.results) {
        const expectedRow = expected.map.get(result.slug);
        const first = result.first;
        const second = result.second;
        if (first?.build !== acceptedBuild || second?.build !== acceptedBuild
          || !first.key || first.key !== second.key || first.version !== 'v6' || second.version !== 'v6'
          || !first.cache || !first.write || second.cache !== 'HIT' || second.write !== 'SKIPPED'
          || !firstReadCanClose(first)
          || !sameJson(scoreIdentity(first), {
            qualityScore: expectedRow.qualityScore,
            qualityTier: expectedRow.qualityTier,
            calculatedAt: expectedRow.calculatedAt,
          })
          || !sameJson(scoreIdentity(second), scoreIdentity(first))) {
          fail(`readback contains incomplete or inconsistent cache/score identity for ${result.slug}`);
        }
      }
      if (input.invalidation?.after?.build !== acceptedBuild) fail('readback build differs from invalidation generation build');
      readbackStatus = 'complete';
    } else if (readback.status === 'blocked_deployment_change') {
      if (readback.acceptedBuild !== null || readback.results?.length !== 0
        || !Array.isArray(readback.rejectedPassDiagnostics)
        || readback.rejectedPassDiagnostics.length !== passes.length
        || !readback.rejectedPassDiagnostics.every((item, index) => item?.attempt === index + 1)
        || !passes.every((pass) => pass.status === 'rejected'
          && sameJson(pass.failureCodes, ['build_transition'])
          && Array.isArray(pass.builds) && pass.builds.length >= 2
          && pass.builds.every(validBuildToken))) {
        fail('deployment-blocked readback mixed or accepted evidence');
      }
      readbackStatus = 'blocked_deployment_change';
    } else {
      fail('readback status is not closed');
    }
  } catch (error) {
    reject(`readback:${error instanceof Error ? error.message : String(error)}`);
  }

  if (scoreStatus === 'failed') reject('score_not_closed');
  if (invalidationStatus === 'failed') reject('invalidation_not_closed');
  if (readbackStatus === 'failed') reject('readback_not_closed');
  if (readbackStatus === 'blocked_deployment_change') reject('production_deployment_changed');
  const preReadbackClosed = scoreStatus !== 'failed' && invalidationStatus === 'complete';
  const status = preReadbackClosed && readbackStatus === 'complete'
    ? 'complete'
    : preReadbackClosed && readbackStatus === 'blocked_deployment_change'
      ? 'blocked_deployment_change' : 'failed';
  return {
    finalizerStatus: status,
    invalidation: {
      expectedCount: invalidationSlugs.length,
      listVersionBumped: input?.invalidation?.listVersionBumped === true,
      status: invalidationStatus,
    },
    plannedSlugCount: planned.length || closureCount(input?.plannedSlugCount),
    readback: { acceptedBuild, buildAttemptCount: closureCount(input?.readback?.buildAttemptCount), status: readbackStatus },
    reasons,
    reentrant: true,
    schemaVersion: 2,
    scope,
    score: {
      causallyProvenCount: closureCount(input?.score?.causallyProvenCount),
      failedCount: closureCount(input?.score?.failedCount),
      requestedCount: closureCount(input?.score?.requestedCount),
      successfulCount: closureCount(input?.score?.successfulCount),
      status: scoreStatus,
    },
    selectedSlugCount: selected.length || closureCount(input?.selectedSlugCount),
    status,
    workflowIdentity: workflowIdentityIsValid(input?.workflowIdentity) ? input.workflowIdentity : null,
  };
}

function writeSlugs(path, slugs) {
  writeFileSync(path, `${slugs.join('\n')}\n`, { mode: 0o600 });
}

function appendOutput(name, value) {
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `${name}=${value}\n`);
}

function readJsonStrict(path, name) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`${name} is missing or invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function readCanonicalSlugFile(path, name) {
  return exactCanonicalSlugs(
    readFileSync(path, 'utf8').split(/\r?\n/).filter(Boolean),
    name,
  );
}

function verifySha256Manifest(directory) {
  const manifestPath = join(directory, 'SHA256SUMS');
  const lines = readFileSync(manifestPath, 'utf8').split(/\r?\n/).filter(Boolean);
  if (lines.length === 0) fail(`empty checksum manifest in ${directory}`);
  for (const line of lines) {
    const match = line.match(/^([0-9a-f]{64})  (.+)$/);
    if (!match) fail(`invalid checksum manifest line: ${line}`);
    const relative = match[2].replace(/^\.\//, '');
    if (!relative || relative.includes('..') || basename(relative) !== relative) {
      fail(`unsafe checksum manifest path: ${relative}`);
    }
    const path = resolve(directory, relative);
    const actual = createHash('sha256').update(readFileSync(path)).digest('hex');
    if (actual !== match[1]) fail(`checksum mismatch for ${relative}`);
  }
  return true;
}

function workflowIdentityFromArgs(args) {
  return {
    repository: readOption(args, '--workflow-repository', { required: true }),
    runId: readOption(args, '--workflow-run-id', { required: true }),
    runAttempt: positiveInteger(readOption(args, '--workflow-run-attempt', { required: true }), 'workflow-run-attempt'),
    headSha: readOption(args, '--workflow-head-sha', { required: true }),
    eventName: readOption(args, '--workflow-event-name', { required: true }),
    workflowName: readOption(args, '--workflow-name', { required: true }),
  };
}

function atomicWriteJson(path, value) {
  const temporary = join(dirname(path), `.${basename(path)}.${process.pid}.tmp`);
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  renameSync(temporary, path);
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (command === 'extract-run-log') {
    const log = readFileSync(readOption(args, '--log', { required: true }), 'utf8');
    const output = readOption(args, '--output', { required: true });
    const expected = readOption(args, '--expected-failures');
    const parsed = parseScoreRunLog(log);
    if (expected !== undefined && parsed.errors !== positiveInteger(expected, 'expected-failures', 10_000)) {
      fail(`expected ${expected} failures but source log proved ${parsed.errors}`);
    }
    writeSlugs(output, parsed.failedSlugs);
    appendOutput('slug_count', parsed.failedSlugs.length);
    appendOutput('processed', parsed.processed);
    appendOutput('updated', parsed.updated);
    return;
  }
  if (command === 'extract-recovery-result') {
    const resultDir = readOption(args, '--result-dir', { required: true });
    const parsed = parseRecoveryResult({
      failedText: readFileSync(join(resultDir, 'failed-slugs.txt'), 'utf8'),
      metadata: JSON.parse(readFileSync(join(resultDir, 'metadata.json'), 'utf8')),
      successfulText: readFileSync(join(resultDir, 'successful-slugs.txt'), 'utf8'),
    });
    const expected = readOption(args, '--expected-failures');
    if (expected !== undefined && parsed.failedCount !== positiveInteger(expected, 'expected-failures', 10_000)) {
      fail(`expected ${expected} failures but recovery result proved ${parsed.failedCount}`);
    }
    writeSlugs(readOption(args, '--output', { required: true }), parsed.failedSlugs);
    appendOutput('slug_count', parsed.failedSlugs.length);
    return;
  }
  if (command === 'approved-catalog') {
    const slugs = await fetchApprovedCatalog({
      supabaseUrl: process.env.PUBLIC_SUPABASE_URL,
      serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
    });
    writeSlugs(readOption(args, '--output', { required: true }), slugs);
    appendOutput('slug_count', slugs.length);
    return;
  }
  if (command === 'freeze-score-evidence') {
    const slugs = normalizeSlugs(readFileSync(readOption(args, '--slugs-file', { required: true }), 'utf8').split(/\r?\n/));
    const expectedScores = await fetchScoreEvidence({
      requireSnapshot: readOption(args, '--require-snapshot', { fallback: 'false' }) === 'true',
      serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
      slugs,
      supabaseUrl: process.env.PUBLIC_SUPABASE_URL,
    });
    const output = readOption(args, '--output', { required: true });
    writeFileSync(output, `${JSON.stringify({ schemaVersion: 1, scores: expectedScores }, null, 2)}\n`, { mode: 0o600 });
    appendOutput('slug_count', expectedScores.length);
    return;
  }
  if (command === 'verify-score-transitions') {
    const beforeDocument = JSON.parse(readFileSync(readOption(args, '--before', { required: true }), 'utf8'));
    const afterDocument = JSON.parse(readFileSync(readOption(args, '--after', { required: true }), 'utf8'));
    if (beforeDocument?.schemaVersion !== 1 || afterDocument?.schemaVersion !== 1) {
      fail('unsupported score transition evidence schema');
    }
    const proof = verifyScoreTransitions({
      afterScores: afterDocument.scores,
      beforeScores: beforeDocument.scores,
      runBoundary: readOption(args, '--run-boundary', { required: true }),
    });
    writeFileSync(
      readOption(args, '--output', { required: true }),
      `${JSON.stringify({ schemaVersion: 1, ...proof }, null, 2)}\n`,
      { mode: 0o600 },
    );
    appendOutput('proven_count', proof.provenCount);
    return;
  }
  if (command === 'prove-readback-budget') {
    const budget = calculateReadbackBudget({
      slugCount: positiveInteger(readOption(args, '--slug-count', { required: true }), 'slug-count', 10_000),
      readsPerSlug: 2,
      attempts: positiveInteger(readOption(args, '--attempts', { fallback: '2' }), 'attempts', 2),
      buildAttempts: positiveInteger(readOption(args, '--build-attempts', { fallback: '2' }), 'build-attempts', 2),
      concurrency: positiveInteger(readOption(args, '--concurrency', { fallback: '16' }), 'concurrency', 16),
      requestTimeoutMs: positiveInteger(readOption(args, '--timeout-ms', { fallback: '5000' }), 'timeout-ms', 5_000),
      retryDelayMaxMs: 1_000,
      buildRetryDelayMs: nonnegativeInteger(readOption(args, '--build-retry-delay-ms', { fallback: '15000' }), 'build-retry-delay-ms', 120_000),
      qps: positiveInteger(readOption(args, '--qps', { fallback: '8' }), 'qps', 16),
      probeRequestsPerPass: 2,
      finalizerReserveMs: 20 * 60_000,
    });
    atomicWriteJson(readOption(args, '--output', { required: true }), budget);
    if (budget.worstCaseTotalMs >= 360 * 60_000) {
      fail(`readback worst-case budget ${budget.worstCaseTotalMs}ms exceeds the 360-minute job`);
    }
    appendOutput('request_limit', budget.requestLimit);
    appendOutput('retry_limit', budget.retryLimit);
    appendOutput('worst_case_total_ms', budget.worstCaseTotalMs);
    return;
  }
  if (command === 'probe-list-generation') {
    const workflowIdentity = workflowIdentityFromArgs(args);
    const identity = await probeListGeneration({
      expectedBuild: readOption(args, '--expected-build'),
      maxBodyBytes: positiveInteger(readOption(args, '--max-body-bytes', { fallback: String(DEFAULT_MAX_BODY_BYTES) }), 'max-body-bytes', 4 * 1024 * 1024),
      siteUrl: readOption(args, '--site-url', { fallback: 'https://skillstore.io' }),
      timeoutMs: positiveInteger(readOption(args, '--timeout-ms', { fallback: '5000' }), 'timeout-ms', 5_000),
    });
    atomicWriteJson(readOption(args, '--output', { required: true }), {
      ...identity, generatedAt: new Date().toISOString(), workflowIdentity,
    });
    appendOutput('build', identity.build);
    appendOutput('version', identity.version);
    return;
  }
  if (command === 'finalize-closure') {
    const planDir = readOption(args, '--plan-dir', { required: true });
    const resultDir = readOption(args, '--result-dir');
    const workflowIdentity = workflowIdentityFromArgs(args);
    const selectedPath = readOption(args, '--selected-slugs', { required: true });
    const planMetadata = readJsonStrict(join(planDir, 'metadata.json'), 'plan metadata');
    const selectedSlugs = readCanonicalSlugFile(selectedPath, 'selected slugs');
    const input = {
      scope: readOption(args, '--scope', { required: true }),
      plannedSlugCount: planMetadata.slugCount,
      selectedSlugCount: selectedSlugs.length,
      workflowIdentity,
      planManifestVerified: verifySha256Manifest(planDir),
      plan: {
        metadata: planMetadata,
        plannedSlugs: readCanonicalSlugFile(join(planDir, 'requested-slugs.txt'), 'planned slugs'),
      },
      selectedSlugs,
      invalidationSlugs: readCanonicalSlugFile(readOption(args, '--invalidation-slugs', { required: true }), 'invalidation slugs'),
      expectedScoreEvidence: readJsonStrict(readOption(args, '--expected-score-evidence', { required: true }), 'expected score evidence'),
      invalidation: readJsonStrict(readOption(args, '--invalidation-evidence', { required: true }), 'invalidation evidence'),
      preflightBudget: readJsonStrict(readOption(args, '--preflight-budget', { required: true }), 'preflight budget evidence'),
      readback: readJsonStrict(readOption(args, '--readback', { required: true }), 'readback evidence'),
      score: null,
      beforeScoreEvidence: null,
      scoreWriteEvidence: null,
    };
    if (resultDir) {
      verifySha256Manifest(resultDir);
      input.score = readJsonStrict(join(resultDir, 'metadata.json'), 'score metadata');
      input.beforeScoreEvidence = readJsonStrict(join(resultDir, 'before-score-evidence.json'), 'before score evidence');
      input.scoreWriteEvidence = readJsonStrict(join(resultDir, 'score-write-evidence.json'), 'score-write evidence');
    }
    const final = finalizeClosure(input);
    atomicWriteJson(readOption(args, '--output', { required: true }), final);
    appendOutput('finalizer_status', final.status);
    appendOutput('accepted_build', final.readback.acceptedBuild || '');
    return;
  }
  if (command === 'readback') {
    const expectedPath = readOption(args, '--expected-score-evidence', { required: true });
    const expectedDocument = readJsonStrict(expectedPath, 'expected score evidence');
    if (expectedDocument?.schemaVersion !== 1) fail('unsupported expected score evidence schema');
    const expectedScores = expectedDocument.scores;
    if (!Array.isArray(expectedScores)) fail('expected score evidence scores must be an array');
    const slugs = normalizeSlugs(expectedScores.map((item) => item?.slug));
    const workflowIdentity = workflowIdentityFromArgs(args);
    const attempts = positiveInteger(readOption(args, '--attempts', { fallback: '2' }), 'attempts', 2);
    const buildAttempts = positiveInteger(readOption(args, '--build-attempts', { fallback: '2' }), 'build-attempts', 2);
    const concurrency = positiveInteger(readOption(args, '--concurrency', { fallback: '16' }), 'concurrency', 16);
    const timeoutMs = positiveInteger(readOption(args, '--timeout-ms', { fallback: '5000' }), 'timeout-ms', 5_000);
    const qps = positiveInteger(readOption(args, '--qps', { fallback: '8' }), 'qps', 16);
    const buildRetryDelayMs = nonnegativeInteger(readOption(args, '--build-retry-delay-ms', { fallback: '15000' }), 'build-retry-delay-ms', 120_000);
    const expectedBuild = readOption(args, '--expected-build', { required: true });
    if (!validBuildToken(expectedBuild)) fail('expected build is invalid');
    const expectedCacheVersion = readOption(args, '--expected-cache-version', { required: true });
    if (!/^v[1-9][0-9]*$/.test(expectedCacheVersion)) fail('expected cache version must have the form vN');
    const budget = calculateReadbackBudget({
      slugCount: slugs.length, readsPerSlug: 2, attempts, buildAttempts, concurrency,
      requestTimeoutMs: timeoutMs, retryDelayMaxMs: 1_000, buildRetryDelayMs, qps,
      probeRequestsPerPass: 2, finalizerReserveMs: 20 * 60_000,
    });
    if (budget.worstCaseTotalMs >= 360 * 60_000) {
      fail(`readback worst-case budget ${budget.worstCaseTotalMs}ms exceeds the 360-minute job`);
    }
    const evidence = await verifyCacheReadback({
      attempts, buildAttempts, buildRetryDelayMs, concurrency,
      expectedBuild,
      expectedCacheVersion,
      maxBodyBytes: positiveInteger(readOption(args, '--max-body-bytes', { fallback: String(DEFAULT_MAX_BODY_BYTES) }), 'max-body-bytes', 4 * 1024 * 1024),
      qps,
      siteUrl: readOption(args, '--site-url', { fallback: 'https://skillstore.io' }),
      expectedScores,
      timeoutMs,
      requestLimit: budget.requestLimit,
      retryLimit: budget.retryLimit,
      wallClockMs: Math.min(340 * 60_000, budget.worstCaseReadbackMs + 60_000),
    });
    const result = {
      ...evidence,
      budget,
      expectedCacheVersion,
      expectedScoreSha256: createHash('sha256').update(JSON.stringify(expectedScores)).digest('hex'),
      generatedAt: new Date().toISOString(),
      schemaVersion: 2,
      slugSha256: canonicalSha256(slugs),
      workflowIdentity,
    };
    atomicWriteJson(readOption(args, '--evidence', { required: true }), result);
    appendOutput('slug_count', slugs.length);
    appendOutput('failed_count', evidence.failures.length);
    if (evidence.status !== 'complete') {
      const prefix = evidence.status === 'blocked_deployment_change'
        ? 'cache readback blocked by production deployment change; no cross-build evidence was accepted'
        : 'cache readback failed';
      fail(`${prefix} for ${evidence.failures.length} item(s): ${evidence.failures.slice(0, 10).map((item) => `${item.slug}: ${item.error}`).join('; ')}`);
    }
    return;
  }
  fail('usage: score-cache-closure.mjs <extract-run-log|extract-recovery-result|approved-catalog|freeze-score-evidence|verify-score-transitions|prove-readback-budget|probe-list-generation|readback|finalize-closure> [options]');
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((error) => {
    console.error(`::error::${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  });
}
