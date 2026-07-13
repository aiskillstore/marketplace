#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { createWriteStream } from 'node:fs';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import {
  calculateWorstCaseRequests,
  normalizeSlugs,
  normalizeWarmTargets,
  runWarm,
  WarmError,
} from './warm-skill-cache.mjs';

const MUTATED_STATUSES = new Set(['translated', 'stale_retranslated']);
const SUPPORTED_LOCALES = new Set([
  'en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'de', 'fr', 'es', 'pt', 'ru', 'ar',
]);
const PLAN_SCHEMA_VERSION = 1;
const DEFAULT_CAPS = Object.freeze({
  skills: 25,
  packs: 100,
  targets: 250,
  requestBudget: 5_000,
  byteBudget: 512 * 1024 * 1024,
  bytesPerTarget: 10 * 1024 * 1024,
  fixedByteReserve: 10 * 1024 * 1024,
});

export class FinalizerError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'FinalizerError';
    this.details = details;
  }
}

function canonicalStrings(values) {
  return [...new Set((values || []).map((value) => String(value).trim()).filter(Boolean))].sort();
}

function stablePlanPayload(plan) {
  const { checksum: _checksum, ...payload } = plan;
  return JSON.stringify(payload);
}

export function planChecksum(plan) {
  return createHash('sha256').update(stablePlanPayload(plan)).digest('hex');
}

export function verifyFinalizationPlan(plan) {
  if (!plan || plan.schemaVersion !== PLAN_SCHEMA_VERSION) {
    throw new FinalizerError(`Unsupported cache finalization plan schema: ${plan?.schemaVersion ?? '<missing>'}`);
  }
  if (!/^[0-9a-f]{64}$/.test(plan.checksum || '') || planChecksum(plan) !== plan.checksum) {
    throw new FinalizerError('Cache finalization plan checksum mismatch');
  }
  normalizeWarmTargets(plan.targets);
  return plan;
}

export function groupsFromTranslationResults(documents) {
  const groups = new Map();
  for (const document of documents) {
    for (const language of document?.languages || []) {
      const locale = String(language?.language || '').trim();
      if (!locale) continue;
      if (!SUPPORTED_LOCALES.has(locale)) {
        throw new FinalizerError(`Unsupported translation result locale: ${locale}`);
      }
      if (locale === 'en') continue;
      for (const skill of language?.skills || []) {
        if (!MUTATED_STATUSES.has(skill?.status)) continue;
        const slug = String(skill?.slug || '').trim();
        if (!slug) throw new FinalizerError(`Translated result for ${locale} is missing a slug`);
        const slugs = groups.get(locale) || new Set();
        slugs.add(slug);
        groups.set(locale, slugs);
      }
    }
  }
  return [...groups.entries()]
    .map(([locale, slugs]) => ({ locale, slugs: [...slugs].sort() }))
    .sort((left, right) => left.locale.localeCompare(right.locale));
}

async function loadTranslationDocuments(resultsDir) {
  const files = (await readdir(resultsDir))
    .filter((name) => /^shard-.*-result\.json$/.test(name))
    .sort();
  const documents = [];
  for (const file of files) {
    documents.push(JSON.parse(await readFile(join(resultsDir, file), 'utf8')));
  }
  return documents;
}

function parsePositiveInteger(value, label) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    throw new FinalizerError(`${label} must be a positive integer`);
  }
  return parsed;
}

async function responseJson(response, source) {
  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    throw new FinalizerError(`${source} returned invalid JSON (HTTP ${response.status})`);
  }
  if (!response.ok) {
    throw new FinalizerError(`${source} returned HTTP ${response.status}: ${payload?.message || payload?.error || text.slice(0, 500)}`);
  }
  return payload;
}

async function callInvalidation(options, body, source) {
  const response = await options.fetchImpl(`${options.siteUrl}/api/cache/invalidate`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${options.cacheSecret}`,
      'Content-Type': 'application/json',
      'User-Agent': 'GitHub-Actions/SkillstoreCacheFinalizer',
      'X-Skillstore-Callback': 'true',
    },
    body: JSON.stringify(body),
  });
  return responseJson(response, source);
}

function invalidationBody(group, overrides = {}) {
  return {
    type: 'skills',
    slugs: group.slugs,
    locales: [group.locale],
    invalidateApi: true,
    invalidateLists: false,
    invalidateArtifacts: false,
    invalidateDependentPacks: true,
    ...overrides,
  };
}

function readClosure(payload, source) {
  const closure = payload?.closure?.dependentPacks;
  if (!closure || closure.overflow !== false) {
    throw new FinalizerError(`${source} did not return a complete dependent-Pack closure`);
  }
  const all = canonicalStrings(closure.all);
  const warmable = canonicalStrings(closure.warmable);
  if (warmable.some((slug) => !all.includes(slug))) {
    throw new FinalizerError(`${source} returned a warmable Pack outside the invalidation closure`);
  }
  return { all, warmable, cap: closure.cap };
}

export async function buildFinalizationPlan(rawOptions) {
  const caps = { ...DEFAULT_CAPS, ...(rawOptions.caps || {}) };
  const groups = rawOptions.groups
    .map((group) => ({ locale: group.locale, slugs: canonicalStrings(group.slugs) }))
    .filter((group) => group.slugs.length > 0)
    .sort((left, right) => left.locale.localeCompare(right.locale));
  const uniqueSkills = canonicalStrings(groups.flatMap((group) => group.slugs));
  if (uniqueSkills.length === 0) return null;
  if (uniqueSkills.length > caps.skills) {
    throw new FinalizerError(`Automatic cache finalization has ${uniqueSkills.length} Skills; cap is ${caps.skills}`);
  }

  const invalidations = [];
  for (const group of groups) {
    if (!SUPPORTED_LOCALES.has(group.locale)) {
      throw new FinalizerError(`Unsupported finalization locale: ${group.locale}`);
    }
    const payload = await callInvalidation(
      rawOptions,
      invalidationBody(group, { preflight: true }),
      `Cache invalidation preflight for ${group.locale}`
    );
    if (payload.preflight !== true) {
      throw new FinalizerError(`Cache invalidation preflight for ${group.locale} performed an unexpected execution`);
    }
    const closure = readClosure(payload, `Cache invalidation preflight for ${group.locale}`);
    invalidations.push({ ...group, dependentPacks: closure });
  }

  const uniquePacks = canonicalStrings(invalidations.flatMap((item) => item.dependentPacks.all));
  if (uniquePacks.length > caps.packs) {
    throw new FinalizerError(`Dependent-Pack closure has ${uniquePacks.length} Packs; cap is ${caps.packs}`);
  }
  const targets = normalizeWarmTargets(invalidations.flatMap((item) => [
    ...item.slugs.map((slug) => ({ resource: 'skills', slug, locale: item.locale })),
    ...item.dependentPacks.warmable.map((slug) => ({ resource: 'packs', slug, locale: item.locale })),
  ]));
  if (targets.length > caps.targets) {
    throw new FinalizerError(`Exact cache warm plan has ${targets.length} resource-locale targets; cap is ${caps.targets}`);
  }

  const computedRequests = calculateWorstCaseRequests(targets);
  const computedBytes = caps.fixedByteReserve + (targets.length * caps.bytesPerTarget);
  if (computedRequests > caps.requestBudget) {
    throw new FinalizerError(`Worst-case warm requests ${computedRequests} exceed aggregate cap ${caps.requestBudget}`);
  }
  if (computedBytes > caps.byteBudget) {
    throw new FinalizerError(`Computed warm byte budget ${computedBytes} exceeds aggregate cap ${caps.byteBudget}`);
  }

  const invalidateOnly = invalidations.flatMap((item) =>
    item.dependentPacks.all
      .filter((slug) => !item.dependentPacks.warmable.includes(slug))
      .map((slug) => ({ resource: 'packs', slug, locale: item.locale, reason: 'not_anonymous_warmable' }))
  );
  const plan = {
    schemaVersion: PLAN_SCHEMA_VERSION,
    createdAt: new Date().toISOString(),
    source: rawOptions.source || 'translation',
    invalidations,
    targets,
    invalidateOnly,
    counts: {
      skills: uniqueSkills.length,
      packs: uniquePacks.length,
      targets: targets.length,
    },
    budgets: {
      requests: computedRequests,
      bytes: computedBytes,
    },
    caps,
  };
  return { ...plan, checksum: planChecksum(plan) };
}

async function executeInvalidations(options, plan) {
  for (const item of plan.invalidations) {
    const payload = await callInvalidation(
      options,
      invalidationBody(item, {
        preflight: false,
        expectedDependentPacks: item.dependentPacks.all,
        expectedWarmableDependentPacks: item.dependentPacks.warmable,
      }),
      `Cache invalidation execution for ${item.locale}`
    );
    if (payload.preflight !== false) {
      throw new FinalizerError(`Cache invalidation execution for ${item.locale} returned preflight state`);
    }
    const closure = readClosure(payload, `Cache invalidation execution for ${item.locale}`);
    if (JSON.stringify(closure.all) !== JSON.stringify(item.dependentPacks.all)) {
      throw new FinalizerError(`Dependent-Pack closure drifted during execution for ${item.locale}`);
    }
    if (JSON.stringify(closure.warmable) !== JSON.stringify(item.dependentPacks.warmable)) {
      throw new FinalizerError(`Dependent-Pack warmability drifted during execution for ${item.locale}`);
    }
    if (payload?.invalidated?.listVersionBumped !== false || payload?.invalidated?.artifacts !== 0) {
      throw new FinalizerError(`Translation finalization unexpectedly invalidated lists or artifacts for ${item.locale}`);
    }
  }
}

export async function executeFinalization(rawOptions) {
  const options = {
    ...rawOptions,
    siteUrl: String(rawOptions.siteUrl || 'https://skillstore.io').replace(/\/$/, ''),
    fetchImpl: rawOptions.fetchImpl || globalThis.fetch,
  };
  if (!options.cacheSecret) throw new FinalizerError('Cache invalidation secret is required');
  if (typeof options.fetchImpl !== 'function') throw new FinalizerError('fetch implementation is required');

  const plan = await buildFinalizationPlan(options);
  if (!plan) return { success: true, skipped: true, reason: 'no_mutated_targets' };
  if (options.planPath) await writeFile(options.planPath, `${JSON.stringify(plan, null, 2)}\n`);
  verifyFinalizationPlan(plan);
  await executeInvalidations(options, plan);

  const stream = options.reportPath ? createWriteStream(options.reportPath, { flags: 'w' }) : null;
  try {
    const warm = await runWarm({
      targets: plan.targets,
      siteUrl: options.siteUrl,
      mode: 'warm',
      scope: 'changed',
      concurrency: options.concurrency || 1,
      requestBudget: plan.budgets.requests,
      byteBudget: plan.budgets.bytes,
      expectedBuildToken: options.expectedBuildToken || undefined,
      report: stream ? (record) => stream.write(`${JSON.stringify(record)}\n`) : undefined,
      fetchImpl: options.warmFetchImpl || globalThis.fetch,
    });
    const result = { success: warm.success, skipped: false, plan, warm };
    if (!warm.success) throw new FinalizerError('Exact cache warm verification failed', { result });
    return result;
  } finally {
    if (stream) await new Promise((resolveStream) => stream.end(resolveStream));
  }
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index++) {
    const current = argv[index];
    if (!current.startsWith('--')) throw new FinalizerError(`Unexpected argument: ${current}`);
    const value = argv[++index];
    if (value === undefined) throw new FinalizerError(`Missing value for ${current}`);
    args[current.slice(2)] = value;
  }
  return args;
}

async function cli(argv) {
  const args = parseArgs(argv);
  const hasResults = !!args['results-dir'];
  const hasSlugs = !!args['slugs-file'];
  if (hasResults === hasSlugs) {
    throw new FinalizerError('Exactly one of --results-dir or --slugs-file is required');
  }
  let groups;
  let source;
  if (hasResults) {
    groups = groupsFromTranslationResults(await loadTranslationDocuments(resolve(args['results-dir'])));
    source = 'translation';
  } else {
    const locales = canonicalStrings(String(args.locales || 'en').split(/[\s,]+/));
    const slugs = normalizeSlugs(await readFile(resolve(args['slugs-file']), 'utf8'));
    groups = locales.map((locale) => ({ locale, slugs }));
    source = 'sync';
  }
  const caps = {
    skills: parsePositiveInteger(args['max-skills'] || DEFAULT_CAPS.skills, 'max skills'),
    packs: parsePositiveInteger(args['max-packs'] || DEFAULT_CAPS.packs, 'max packs'),
    targets: parsePositiveInteger(args['max-targets'] || DEFAULT_CAPS.targets, 'max targets'),
    requestBudget: parsePositiveInteger(args['request-budget'] || DEFAULT_CAPS.requestBudget, 'request budget'),
    byteBudget: parsePositiveInteger(args['byte-budget'] || DEFAULT_CAPS.byteBudget, 'byte budget'),
    bytesPerTarget: DEFAULT_CAPS.bytesPerTarget,
    fixedByteReserve: DEFAULT_CAPS.fixedByteReserve,
  };
  try {
    const result = await executeFinalization({
      groups,
      source,
      siteUrl: args['site-url'] || process.env.SITE_URL || 'https://skillstore.io',
      cacheSecret: args['cache-secret'] || process.env.CACHE_INVALIDATE_SECRET,
      expectedBuildToken: args['expected-build-token'] || process.env.EXPECTED_BUILD_TOKEN,
      concurrency: parsePositiveInteger(args.concurrency || 1, 'concurrency'),
      caps,
      planPath: args.plan,
      reportPath: args.report,
    });
    if (args.summary) await writeFile(args.summary, `${JSON.stringify(result, null, 2)}\n`);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } catch (error) {
    const failure = {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      details: error instanceof FinalizerError ? error.details : undefined,
    };
    if (args.summary) await writeFile(args.summary, `${JSON.stringify(failure, null, 2)}\n`);
    throw error;
  }
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (isMain) {
  cli(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.stack || error.message : String(error));
    process.exitCode = 1;
  });
}
