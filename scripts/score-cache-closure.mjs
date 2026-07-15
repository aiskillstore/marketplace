#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { appendFileSync, readFileSync, writeFileSync } from 'node:fs';
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

async function fetchWithTimeout(fetchImpl, url, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, {
      headers: { Accept: 'application/json', 'User-Agent': 'skillstore-score-cache-closure' },
      redirect: 'error',
      signal: controller.signal,
    });
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
  if (!response.ok) fail(`${slug} cache readback returned HTTP ${response.status}`);
  const body = await response.json();
  if (body?.data?.slug !== slug) fail(`${slug} cache readback returned the wrong record`);
  const result = {
    build: response.headers.get('x-skillstore-build'),
    cache: response.headers.get('x-kv-cache'),
    key: response.headers.get('x-kv-key'),
    version: response.headers.get('x-kv-version'),
    write: response.headers.get('x-kv-write'),
  };
  if (!result.build || !result.key || !result.version) {
    fail(`${slug} cache readback omitted build/key/version identity`);
  }
  return { body, ...result };
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
  concurrency = 8,
  fetchImpl = fetch,
  siteUrl = 'https://skillstore.io',
  expectedScores,
  timeoutMs = 30_000,
}) {
  if (!Array.isArray(expectedScores)) fail('expected score evidence must be an array');
  const normalized = normalizeSlugs(expectedScores.map((item) => item?.slug));
  if (normalized.length !== expectedScores.length) fail('expected score evidence contains duplicate slugs');
  const expectedBySlug = new Map(expectedScores.map((item) => [item.slug, item]));
  const results = new Array(normalized.length);
  const failures = [];
  let cursor = 0;

  async function verifyOne(slug) {
    let lastError;
    for (let attempt = 1; attempt <= attempts; attempt += 1) {
      try {
        const first = await readSkill(fetchImpl, siteUrl, slug, timeoutMs);
        const second = await readSkill(fetchImpl, siteUrl, slug, timeoutMs);
        if (!firstReadCanClose(first)) {
          fail(`${slug} first read was ${first.cache || 'missing'}+${first.write || 'missing'}`);
        }
        const expected = expectedBySlug.get(slug);
        if (!readMatchesExpectedScore(first, expected) || !readMatchesExpectedScore(second, expected)) {
          fail(`${slug} API score identity does not match frozen DB evidence`);
        }
        if (second.cache !== 'HIT' || second.write !== 'SKIPPED') {
          fail(`${slug} second read was ${second.cache || 'missing'}+${second.write || 'missing'}`);
        }
        for (const field of ['build', 'key', 'version']) {
          if (first[field] !== second[field]) fail(`${slug} changed ${field} between cache reads`);
        }
        const { body: _firstBody, ...firstIdentity } = first;
        const { body: _secondBody, ...secondIdentity } = second;
        return { first: firstIdentity, second: secondIdentity, slug };
      } catch (error) {
        lastError = error;
        if (attempt < attempts) await new Promise((resolve) => setTimeout(resolve, attempt * 1000));
      }
    }
    throw lastError;
  }

  async function worker() {
    while (true) {
      const index = cursor;
      cursor += 1;
      if (index >= normalized.length) return;
      try {
        results[index] = await verifyOne(normalized[index]);
      } catch (error) {
        failures.push({ slug: normalized[index], error: error instanceof Error ? error.message : String(error) });
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, normalized.length) }, () => worker()));
  const builds = [...new Set(results.filter(Boolean).map((result) => result.second.build))].sort();
  if (builds.length > 1) failures.push({ slug: '*', error: `production build changed during readback: ${builds.join(', ')}` });
  return { builds, failures, results: results.filter(Boolean), slugCount: normalized.length };
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
      concurrency: positiveInteger(readOption(args, '--concurrency', { fallback: '8' }), 'concurrency', 16),
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
    if (evidence.failures.length > 0) {
      fail(`cache readback failed for ${evidence.failures.length} item(s): ${evidence.failures.slice(0, 10).map((item) => `${item.slug}: ${item.error}`).join('; ')}`);
    }
    return;
  }
  fail('usage: score-cache-closure.mjs <extract-run-log|extract-recovery-result|approved-catalog|freeze-score-evidence|verify-score-transitions|readback> [options]');
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((error) => {
    console.error(`::error::${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  });
}
