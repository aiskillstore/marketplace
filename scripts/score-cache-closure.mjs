#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { appendFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
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
  constructor(code, message, { retryable = false } = {}) {
    super(message);
    this.code = code;
    this.retryable = retryable;
  }
}

function readbackFail(code, message, options) {
  throw new ReadbackFailure(code, message, options);
}

const sleep = (delayMs) => new Promise((resolve) => setTimeout(resolve, delayMs));

async function fetchWithTimeout(fetchImpl, url, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, {
      headers: { Accept: 'application/json', 'User-Agent': 'skillstore-score-cache-closure' },
      method: 'GET',
      redirect: 'error',
      signal: controller.signal,
    });
  } catch (error) {
    if (controller.signal.aborted) {
      readbackFail('read_timeout', `cache readback GET timed out after ${timeoutMs}ms`, { retryable: true });
    }
    readbackFail(
      'network_error',
      `cache readback GET failed: ${error instanceof Error ? error.message : String(error)}`,
      { retryable: true },
    );
  } finally {
    clearTimeout(timer);
  }
}

async function readSkill(fetchImpl, siteUrl, slug, timeoutMs) {
  const response = await fetchWithTimeout(
    fetchImpl,
    `${siteUrl.replace(/\/+$/, '')}/api/skills/${encodeURIComponent(slug)}`,
    timeoutMs,
  );
  if (!response.ok) {
    const isServerError = response.status >= 500 && response.status <= 599;
    readbackFail(
      isServerError ? 'http_5xx' : 'http_error',
      `${slug} cache readback returned HTTP ${response.status}`,
      { retryable: isServerError },
    );
  }
  let body;
  try {
    body = await response.json();
  } catch {
    readbackFail('invalid_response', `${slug} cache readback returned invalid JSON`);
  }
  if (body?.data?.slug !== slug) {
    readbackFail('wrong_record', `${slug} cache readback returned the wrong record`);
  }
  const result = {
    build: response.headers.get('x-skillstore-build'),
    cache: response.headers.get('x-kv-cache'),
    key: response.headers.get('x-kv-key'),
    version: response.headers.get('x-kv-version'),
    write: response.headers.get('x-kv-write'),
  };
  if (!result.build || !result.key || !result.version) {
    readbackFail('missing_identity', `${slug} cache readback omitted build/key/version identity`);
  }
  return { body, ...result };
}

async function readSkillWithRetries({
  attempts,
  fetchImpl,
  onRetryableFailure,
  siteUrl,
  sleepImpl,
  slug,
  timeoutMs,
}) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await readSkill(fetchImpl, siteUrl, slug, timeoutMs);
    } catch (error) {
      lastError = error;
      if (!(error instanceof ReadbackFailure) || !error.retryable) throw error;
      onRetryableFailure();
      if (attempt < attempts) await sleepImpl(attempt * 1000);
    }
  }
  throw lastError;
}

function readMatchesExpectedScore(read, expected) {
  const actualScore = read.body?.data?.qualityScore ?? null;
  const actualTier = read.body?.data?.qualityTier ?? null;
  const actualCalculatedAt = read.body?.data?.qualityBreakdown?.calculatedAt ?? null;
  return actualScore === expected.qualityScore
    && actualTier === expected.qualityTier
    && actualCalculatedAt === expected.calculatedAt;
}

function firstReadCanClose(read) {
  return (read.cache === 'MISS' && read.write === 'STORED')
    || (read.cache === 'HIT' && read.write === 'SKIPPED');
}

export async function verifyCacheReadback({
  attempts = 3,
  buildAttempts = 1,
  buildRetryDelayMs = 5_000,
  concurrency = 8,
  expectedCacheVersion,
  fetchImpl = fetch,
  siteUrl = 'https://skillstore.io',
  sleepImpl = sleep,
  expectedScores,
  timeoutMs = 30_000,
}) {
  if (!Array.isArray(expectedScores)) fail('expected score evidence must be an array');
  positiveInteger(attempts, 'attempts', 5);
  positiveInteger(buildAttempts, 'buildAttempts', 5);
  nonnegativeInteger(buildRetryDelayMs, 'buildRetryDelayMs', 120_000);
  positiveInteger(concurrency, 'concurrency', 16);
  positiveInteger(timeoutMs, 'timeoutMs', 120_000);
  if (typeof sleepImpl !== 'function') fail('sleepImpl must be a function');
  if (expectedCacheVersion !== undefined && !/^v[1-9][0-9]*$/.test(expectedCacheVersion)) {
    fail('expected cache version must have the form vN');
  }
  const normalized = normalizeSlugs(expectedScores.map((item) => item?.slug));
  if (normalized.length !== expectedScores.length) fail('expected score evidence contains duplicate slugs');
  const expectedBySlug = new Map(expectedScores.map((item) => [item.slug, item]));
  let retryableReadFailures = 0;

  async function verifyOne(slug) {
    const read = () => readSkillWithRetries({
      attempts,
      fetchImpl,
      onRetryableFailure: () => {
        retryableReadFailures += 1;
      },
      siteUrl,
      sleepImpl,
      slug,
      timeoutMs,
    });
    const first = await read();
    const second = await read();
    if (first.build !== second.build) {
      readbackFail('build_transition', `${slug} changed build between cache reads`);
    }
    if (
      expectedCacheVersion !== undefined &&
      (first.version !== expectedCacheVersion || second.version !== expectedCacheVersion)
    ) {
      readbackFail(
        'cache_version_mismatch',
        `${slug} cache version was ${first.version}/${second.version}; expected ${expectedCacheVersion}`,
      );
    }
    if (!firstReadCanClose(first)) {
      readbackFail(
        'cache_state_mismatch',
        `${slug} first read was ${first.cache || 'missing'}+${first.write || 'missing'}`,
      );
    }
    const expected = expectedBySlug.get(slug);
    if (!readMatchesExpectedScore(first, expected) || !readMatchesExpectedScore(second, expected)) {
      readbackFail('score_mismatch', `${slug} API score identity does not match frozen DB evidence`);
    }
    if (second.cache !== 'HIT' || second.write !== 'SKIPPED') {
      readbackFail(
        'cache_state_mismatch',
        `${slug} second read was ${second.cache || 'missing'}+${second.write || 'missing'}`,
      );
    }
    for (const field of ['key', 'version']) {
      if (first[field] !== second[field]) {
        readbackFail('cache_identity_mismatch', `${slug} changed ${field} between cache reads`);
      }
    }
    const { body: _firstBody, ...firstIdentity } = first;
    const { body: _secondBody, ...secondIdentity } = second;
    return { first: firstIdentity, second: secondIdentity, slug };
  }

  async function runPass() {
    const passResults = new Array(normalized.length);
    const passFailures = new Array(normalized.length);
    let cursor = 0;

    async function worker() {
      while (true) {
        const index = cursor;
        cursor += 1;
        if (index >= normalized.length) return;
        try {
          passResults[index] = await verifyOne(normalized[index]);
        } catch (error) {
          passFailures[index] = {
            code: error instanceof ReadbackFailure ? error.code : 'unexpected_error',
            error: error instanceof Error ? error.message : String(error),
            slug: normalized[index],
          };
        }
      }
    }

    await Promise.all(Array.from({ length: Math.min(concurrency, normalized.length) }, () => worker()));
    const results = passResults.filter(Boolean);
    const failures = passFailures.filter(Boolean);
    const builds = [...new Set(results.flatMap((result) => [
      result.first.build,
      result.second.build,
    ]))].sort();
    if (builds.length > 1) {
      failures.push({
        code: 'build_transition',
        error: `production build changed during readback: ${builds.join(', ')}`,
        slug: '*',
      });
    }
    return { builds, failures, results };
  }

  const buildPasses = [];
  for (let buildAttempt = 1; buildAttempt <= buildAttempts; buildAttempt += 1) {
    const pass = await runPass();
    if (pass.failures.length === 0 && pass.builds.length !== 1) {
      pass.failures.push({
        code: 'build_identity',
        error: 'production readback did not produce exactly one build identity',
        slug: '*',
      });
    }
    buildPasses.push({
      attempt: buildAttempt,
      builds: pass.builds,
      failureCodes: [...new Set(pass.failures.map((failure) => failure.code))].sort(),
    });

    if (pass.failures.length === 0) {
      return {
        acceptedBuild: pass.builds[0],
        buildAttemptCount: buildAttempt,
        buildPasses,
        builds: pass.builds,
        failures: [],
        results: pass.results,
        retryableReadFailures,
        slugCount: normalized.length,
        status: 'complete',
      };
    }

    // A split deployment invalidates the entire pass, including unrelated
    // read failures observed while traffic crossed builds. Retry only this
    // GET-only pass; score writes and cache invalidation are never repeated.
    const hasBuildTransition = pass.failures.some((failure) => failure.code === 'build_transition');
    if (hasBuildTransition && buildAttempt < buildAttempts) {
      await sleepImpl(buildRetryDelayMs);
      continue;
    }
    return {
      acceptedBuild: null,
      buildAttemptCount: buildAttempt,
      buildPasses,
      builds: [],
      failures: pass.failures,
      results: [],
      retryableReadFailures,
      slugCount: normalized.length,
      status: hasBuildTransition ? 'blocked_deployment_change' : 'failed',
    };
  }

  throw new Error('unreachable cache readback state');
}

function closureCount(value) {
  const parsed = typeof value === 'string' && /^\d+$/.test(value) ? Number(value) : value;
  return Number.isSafeInteger(parsed) && parsed >= 0 ? parsed : null;
}

export function finalizeClosure({
  invalidation,
  plannedSlugCount,
  readback,
  scope,
  score,
  selectedSlugCount,
}) {
  const planned = closureCount(plannedSlugCount);
  const selected = closureCount(selectedSlugCount);
  const reasons = [];

  let scoreStatus = 'failed';
  const scoreSummary = {
    causallyProvenCount: closureCount(score?.causallyProvenCount),
    failedCount: closureCount(score?.failedCount),
    requestedCount: closureCount(score?.requestedCount),
    status: scoreStatus,
    successfulCount: closureCount(score?.successfulCount),
  };
  if (scope === 'approved-catalog-cache') {
    scoreStatus = planned !== null && selected === planned ? 'not_required' : 'failed';
  } else if (
    (scope === 'source-run-failures' || scope === 'recovery-run-failures')
    && score?.schemaVersion === 1
    && planned !== null
    && selected !== null
    && [
      scoreSummary.requestedCount,
      scoreSummary.successfulCount,
      scoreSummary.failedCount,
      scoreSummary.causallyProvenCount,
    ].every((value) => value !== null)
    && scoreSummary.requestedCount === planned
    && scoreSummary.successfulCount === selected
    && scoreSummary.requestedCount === scoreSummary.successfulCount + scoreSummary.failedCount
    && scoreSummary.causallyProvenCount === scoreSummary.successfulCount
    && scoreSummary.failedCount === 0
  ) {
    scoreStatus = 'complete';
  }
  scoreSummary.status = scoreStatus;
  if (scoreStatus === 'failed') reasons.push('score_not_closed');

  const invalidationSummary = {
    expectedCount: closureCount(invalidation?.expectedCount),
    failedCount: closureCount(invalidation?.failedCount),
    listVersionBumped: invalidation?.listVersionBumped === true,
    status: 'failed',
    successCount: closureCount(invalidation?.successCount),
    totalCount: closureCount(invalidation?.totalCount),
  };
  if (
    invalidationSummary.expectedCount !== null
    && invalidationSummary.expectedCount > 0
    && invalidationSummary.totalCount === invalidationSummary.expectedCount
    && invalidationSummary.successCount === invalidationSummary.expectedCount
    && invalidationSummary.failedCount === 0
    && invalidationSummary.listVersionBumped
  ) {
    invalidationSummary.status = 'complete';
  } else {
    reasons.push('invalidation_not_closed');
  }

  const readbackFailures = Array.isArray(readback?.failures) ? readback.failures : [];
  const readbackFailureCodes = [...new Set(
    readbackFailures.map((failure) => failure?.code).filter(Boolean),
  )].sort();
  const acceptedBuild = typeof readback?.acceptedBuild === 'string' && readback.acceptedBuild
    ? readback.acceptedBuild
    : null;
  const buildAttemptCount = closureCount(readback?.buildAttemptCount);
  const buildPasses = Array.isArray(readback?.buildPasses) ? readback.buildPasses : [];
  const buildPassesAreSequential = buildAttemptCount !== null
    && buildAttemptCount > 0
    && buildPasses.length === buildAttemptCount
    && buildPasses.every((pass, index) => (
      pass?.attempt === index + 1
      && Array.isArray(pass?.builds)
      && Array.isArray(pass?.failureCodes)
    ));
  const lastBuildPass = buildPassesAreSequential ? buildPasses.at(-1) : null;
  const builds = Array.isArray(readback?.builds) ? readback.builds : [];
  const results = Array.isArray(readback?.results) ? readback.results : [];
  const resultSlugs = results.map((result) => result?.slug);
  const canonicalResultSlugs = resultSlugs.every((slug) => typeof slug === 'string' && SLUG_RE.test(slug))
    ? [...new Set(resultSlugs)].sort()
    : [];
  const resultSlugSha256 = canonicalResultSlugs.length === results.length
    ? createHash('sha256').update(`${canonicalResultSlugs.join('\n')}\n`).digest('hex')
    : null;
  const readbackIsComplete = readback?.schemaVersion === 1
    && readback?.status === 'complete'
    && selected !== null
    && readback?.slugCount === selected
    && acceptedBuild !== null
    && buildPassesAreSequential
    && lastBuildPass.builds.length === 1
    && lastBuildPass.builds[0] === acceptedBuild
    && lastBuildPass.failureCodes.length === 0
    && builds.length === 1
    && builds[0] === acceptedBuild
    && readbackFailures.length === 0
    && results.length === selected
    && canonicalResultSlugs.length === selected
    && readback?.slugSha256 === resultSlugSha256
    && results.every((result) => (
      result?.first?.build === acceptedBuild && result?.second?.build === acceptedBuild
    ));
  const readbackIsDeploymentBlocked = readback?.schemaVersion === 1
    && readback?.status === 'blocked_deployment_change'
    && acceptedBuild === null
    && buildPassesAreSequential
    && lastBuildPass.failureCodes.includes('build_transition')
    && builds.length === 0
    && results.length === 0
    && readbackFailureCodes.includes('build_transition');
  const readbackStatus = readbackIsComplete
    ? 'complete'
    : readbackIsDeploymentBlocked ? 'blocked_deployment_change' : 'failed';
  if (readbackStatus === 'blocked_deployment_change') reasons.push('production_deployment_changed');
  else if (readbackStatus === 'failed') reasons.push('readback_not_closed');
  const readbackSummary = {
    acceptedBuild,
    buildAttemptCount,
    failureCodes: readbackFailureCodes,
    status: readbackStatus,
  };

  const preReadbackClosed = scoreStatus !== 'failed' && invalidationSummary.status === 'complete';
  const status = preReadbackClosed && readbackStatus === 'complete'
    ? 'complete'
    : preReadbackClosed && readbackStatus === 'blocked_deployment_change'
      ? 'blocked_deployment_change'
      : 'failed';
  return {
    finalizerStatus: status,
    invalidation: invalidationSummary,
    plannedSlugCount: planned,
    readback: readbackSummary,
    reasons,
    reentrant: true,
    schemaVersion: 1,
    scope,
    score: scoreSummary,
    selectedSlugCount: selected,
    status,
  };
}

function writeSlugs(path, slugs) {
  writeFileSync(path, `${slugs.join('\n')}\n`, { mode: 0o600 });
}

function appendOutput(name, value) {
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `${name}=${value}\n`);
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
  if (command === 'finalize-closure') {
    const readJsonIfPresent = (path) => {
      if (!path || !existsSync(path)) return null;
      try {
        return JSON.parse(readFileSync(path, 'utf8'));
      } catch {
        return null;
      }
    };
    const final = finalizeClosure({
      invalidation: {
        expectedCount: readOption(args, '--invalidation-expected-count', { required: true }),
        failedCount: readOption(args, '--invalidation-failed-count', { required: true }),
        listVersionBumped: readOption(args, '--list-version-bumped', { required: true }) === 'true',
        successCount: readOption(args, '--invalidation-success-count', { required: true }),
        totalCount: readOption(args, '--invalidation-total-count', { required: true }),
      },
      plannedSlugCount: readOption(args, '--planned-slug-count', { required: true }),
      readback: readJsonIfPresent(readOption(args, '--readback', { required: true })),
      scope: readOption(args, '--scope', { required: true }),
      score: readJsonIfPresent(readOption(args, '--score-metadata')),
      selectedSlugCount: readOption(args, '--selected-slug-count', { required: true }),
    });
    writeFileSync(
      readOption(args, '--output', { required: true }),
      `${JSON.stringify(final, null, 2)}\n`,
      { mode: 0o600 },
    );
    appendOutput('finalizer_status', final.status);
    appendOutput('accepted_build', final.readback.acceptedBuild || '');
    return;
  }
  if (command === 'readback') {
    const expectedPath = readOption(args, '--expected-score-evidence', { required: true });
    const expectedDocument = JSON.parse(readFileSync(expectedPath, 'utf8'));
    if (expectedDocument?.schemaVersion !== 1) fail('unsupported expected score evidence schema');
    const expectedScores = expectedDocument.scores;
    if (!Array.isArray(expectedScores)) fail('expected score evidence scores must be an array');
    const slugs = normalizeSlugs(expectedScores.map((item) => item?.slug));
    const evidencePath = readOption(args, '--evidence', { required: true });
    const evidence = await verifyCacheReadback({
      attempts: positiveInteger(readOption(args, '--attempts', { fallback: '3' }), 'attempts', 5),
      buildAttempts: positiveInteger(
        readOption(args, '--build-attempts', { fallback: '1' }),
        'build-attempts',
        5,
      ),
      buildRetryDelayMs: nonnegativeInteger(
        readOption(args, '--build-retry-delay-ms', { fallback: '15000' }),
        'build-retry-delay-ms',
        120_000,
      ),
      concurrency: positiveInteger(readOption(args, '--concurrency', { fallback: '8' }), 'concurrency', 16),
      expectedCacheVersion: readOption(args, '--expected-cache-version'),
      siteUrl: readOption(args, '--site-url', { fallback: 'https://skillstore.io' }),
      expectedScores,
      timeoutMs: positiveInteger(readOption(args, '--timeout-ms', { fallback: '30000' }), 'timeout-ms', 120_000),
    });
    const result = {
      ...evidence,
      generatedAt: new Date().toISOString(),
      schemaVersion: 1,
      slugSha256: createHash('sha256').update(`${slugs.join('\n')}\n`).digest('hex'),
    };
    writeFileSync(evidencePath, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
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
  fail('usage: score-cache-closure.mjs <extract-run-log|extract-recovery-result|approved-catalog|freeze-score-evidence|verify-score-transitions|readback|finalize-closure> [options]');
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((error) => {
    console.error(`::error::${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  });
}
