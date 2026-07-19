#!/usr/bin/env node

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

function fail(message) {
  throw new Error(`Fresh canonical audit cache recovery: ${message}`);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function nonNegativeInteger(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function planCounts(value) {
  if (!value || typeof value !== 'object') return null;
  const counts = {
    resources: value.resources,
    api: value.api,
    page: value.page,
    artifactPrefixes: value.artifactPrefixes,
    artifacts: value.artifacts,
    artifactListOperations: value.artifactListOperations,
  };
  return Object.values(counts).every(nonNegativeInteger) ? counts : null;
}

function resourcePlan(value, dependentResources) {
  if (!value || typeof value !== 'object') return null;
  const primary = planCounts(value.primary);
  const dependentPacks = planCounts(value.dependentPacks);
  const totalsBase = planCounts(value.totals);
  const totals = totalsBase && nonNegativeInteger(value.totals?.listWrites)
    && nonNegativeInteger(value.totals?.kvOperations)
    ? { ...totalsBase, listWrites: value.totals.listWrites, kvOperations: value.totals.kvOperations }
    : null;
  if (!primary || !dependentPacks || !totals
    || primary.resources !== 1 || dependentPacks.resources !== dependentResources
    || totals.resources !== primary.resources + dependentPacks.resources
    || totals.api !== primary.api + dependentPacks.api
    || totals.page !== primary.page + dependentPacks.page
    || totals.artifactPrefixes !== primary.artifactPrefixes + dependentPacks.artifactPrefixes
    || totals.artifacts !== primary.artifacts + dependentPacks.artifacts
    || totals.artifactListOperations !== (
      primary.artifactListOperations + dependentPacks.artifactListOperations
    )
    || totals.listWrites !== 2
    || totals.kvOperations !== (
      totals.api + totals.page + totals.artifacts + totals.artifactListOperations + totals.listWrites
    )
    || totals.kvOperations > 850) {
    return null;
  }
  return { primary, dependentPacks, totals };
}

function zeroWritePreflight(value) {
  return value && typeof value === 'object'
    && value.total === 0 && value.page === 0 && value.api === 0 && value.artifacts === 0
    && value.listVersionBumped === false && nonNegativeInteger(value.listMaxStaleSeconds);
}

function parsePlan(body, slug) {
  const closure = body?.closure?.dependentPacks;
  const plan = resourcePlan(body?.plan, closure?.all?.length);
  if (body?.preflight !== true || body?.type !== 'skills'
    || canonicalJson(body.slugs) !== canonicalJson([slug])
    || !Array.isArray(body.locales) || body.locales.length === 0
    || !closure || !Array.isArray(closure.all) || !Array.isArray(closure.warmable)
    || closure.overflow !== false || !Number.isSafeInteger(closure.cap)
    || !plan
    || body.locales.length !== 11
    || !/^[0-9a-f]{64}$/i.test(body?.planHash || '')
    || typeof body?.catalogEpoch !== 'string' || body.catalogEpoch.length === 0
    || !zeroWritePreflight(body?.invalidated)) {
    fail(`invalid cache preflight contract for ${slug}`);
  }
  return {
    slug,
    locales: body.locales,
    closure,
    catalogEpoch: body.catalogEpoch,
    plan,
    planHash: body.planHash,
    response: body,
  };
}

function verifyExecution(body, frozen) {
  if (body?.preflight !== false || body?.type !== 'skills'
    || canonicalJson(body.slugs) !== canonicalJson([frozen.slug])
    || canonicalJson(body.locales) !== canonicalJson(frozen.locales)
    || body.catalogEpoch !== frozen.catalogEpoch
    || body.planHash !== frozen.planHash
    || canonicalJson(body.closure) !== canonicalJson({ dependentPacks: frozen.closure })
    || canonicalJson(body.plan) !== canonicalJson(frozen.plan)
    || body?.invalidated?.listVersionBumped !== true
    || body?.invalidated?.api !== frozen.plan.primary.api
    || body?.invalidated?.page !== frozen.plan.primary.page
    || body?.invalidated?.artifacts !== frozen.plan.primary.artifacts
    || body?.invalidated?.total !== (
      frozen.plan.primary.api + frozen.plan.primary.page + frozen.plan.primary.artifacts
    )
    || body?.invalidated?.listMaxStaleSeconds !== 0) {
    fail(`invalid cache execution contract for ${frozen.slug}`);
  }
  if (frozen.closure.all.length > 0) {
    if (canonicalJson(body?.dependentPacks?.slugs) !== canonicalJson(frozen.closure.all)
      || canonicalJson(body?.dependentPacks?.anonymousWarmableSlugs) !== canonicalJson(frozen.closure.warmable)
      || body?.dependentPacks?.invalidated?.api !== frozen.plan.dependentPacks.api
      || body?.dependentPacks?.invalidated?.page !== frozen.plan.dependentPacks.page
      || body?.dependentPacks?.invalidated?.artifacts !== frozen.plan.dependentPacks.artifacts
      || body?.dependentPacks?.invalidated?.total !== (
        frozen.plan.dependentPacks.api + frozen.plan.dependentPacks.page
        + frozen.plan.dependentPacks.artifacts
      )
      || body?.dependentPacks?.invalidated?.listVersionBumped !== true
      || body?.dependentPacks?.invalidated?.listMaxStaleSeconds !== 0) {
      fail(`invalid dependent Pack closure for ${frozen.slug}`);
    }
  } else if (Object.hasOwn(body, 'dependentPacks')) {
    fail(`unexpected dependent Pack result for ${frozen.slug}`);
  }
}

async function request({ body, endpoint, fetchImpl, secret, timeoutMs }) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(endpoint, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        Authorization: `Bearer ${secret}`,
        'Content-Type': 'application/json',
        'User-Agent': 'skillstore-fresh-audit-recovery',
      },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => null);
    return { ok: response.ok, status: response.status, payload };
  } catch (error) {
    return { ok: false, status: 0, payload: null, error: error instanceof Error ? error.message : String(error) };
  } finally {
    clearTimeout(timer);
  }
}

async function preflight(options, slug, maxAttempts, sleepImpl) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const response = await request({ ...options, body: {
      type: 'skills', slugs: [slug], preflight: true,
      invalidateApi: true, invalidateLists: true, invalidateArtifacts: true,
      invalidateDependentPacks: true,
    } });
    if (response.ok) return parsePlan(response.payload, slug);
    if (attempt === maxAttempts) {
      fail(`cache preflight returned HTTP ${response.status} for ${slug}${response.error ? `: ${response.error}` : ''}`);
    }
    await sleepImpl(attempt * 5_000);
  }
  fail(`cache preflight attempts exhausted for ${slug}`);
}

export async function closeFreshAuditCaches({
  endpoint = 'https://skillstore.io/api/cache/invalidate',
  fetchImpl = fetch,
  maxAttempts = 4,
  interSkillDelayMs = 1_100,
  secret,
  sleepImpl = sleep,
  slugs,
  timeoutMs = 90_000,
}) {
  if (!secret) fail('cache invalidation secret is required');
  if (!Number.isSafeInteger(interSkillDelayMs) || interSkillDelayMs < 1_100) {
    fail('inter-Skill delay must be at least 1100ms');
  }
  const requested = [...new Set(slugs.map((slug) => String(slug).trim()).filter(Boolean))].sort();
  if (requested.length === 0 || requested.length !== slugs.length) fail('exact unique slug set is required');
  const results = [];
  for (const slug of requested) {
    let frozen = await preflight({ endpoint, fetchImpl, secret, timeoutMs }, slug, maxAttempts, sleepImpl);
    let completed = null;
    let transportFailures = 0;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      const response = await request({ endpoint, fetchImpl, secret, timeoutMs, body: {
        type: 'skills', slugs: [slug], locales: frozen.locales,
        invalidateApi: true, invalidateLists: true, invalidateArtifacts: true,
        invalidateDependentPacks: true,
        expectedDependentPacks: frozen.closure.all,
        expectedWarmableDependentPacks: frozen.closure.warmable,
        expectedPlanHash: frozen.planHash,
      } });
      if (response.ok) {
        verifyExecution(response.payload, frozen);
        completed = { attempt, execution: response.payload, preflight: frozen.response, slug };
        break;
      }
      if (response.status === 0) {
        transportFailures += 1;
        if (transportFailures > 1) {
          fail(`ambiguous cache execution repeated for ${slug}`);
        }
        await sleepImpl(35_000);
        continue;
      }
      if (response.status === 409 && [
        'Dependent pack closure changed; run preflight again',
        'Cache invalidation plan changed; run preflight again',
      ].includes(response.payload?.message)) {
        frozen = await preflight({ endpoint, fetchImpl, secret, timeoutMs }, slug, maxAttempts, sleepImpl);
      } else if (attempt === maxAttempts) {
        fail(`cache execution returned HTTP ${response.status} for ${slug}${response.error ? `: ${response.error}` : ''}`);
      }
      if (attempt < maxAttempts) await sleepImpl(attempt * 5_000);
    }
    if (!completed) fail(`cache closure attempts exhausted for ${slug}`);
    results.push(completed);
    if (results.length < requested.length) await sleepImpl(interSkillDelayMs);
  }
  return {
    schemaVersion: 1,
    status: 'fresh_canonical_audit_cache_closed',
    requestedCount: requested.length,
    closedCount: results.length,
    slugs: requested,
    results,
  };
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index < 0 || !args[index + 1] || args[index + 1].startsWith('--')) fail(`missing ${name}`);
  return args[index + 1];
}

export async function main(args = process.argv.slice(2)) {
  const slugs = readFileSync(option(args, '--slugs-file'), 'utf8').split(/\r?\n/).filter(Boolean);
  const output = resolve(option(args, '--output'));
  const result = await closeFreshAuditCaches({
    endpoint: `${option(args, '--site-url').replace(/\/$/, '')}/api/cache/invalidate`,
    secret: process.env.CACHE_INVALIDATE_SECRET,
    slugs,
  });
  mkdirSync(resolve(output, '..'), { recursive: true });
  writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
}

if (import.meta.url === pathToFileURL(resolve(process.argv[1] || '')).href) {
  main().catch((error) => {
    process.stderr.write(`fresh canonical audit cache recovery failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
