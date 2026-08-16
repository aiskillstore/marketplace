// ----------------------------------------------------------------------------
// selector-cache.js
//
// Self-healing selector cache. The agent's discovery loop is expensive
// (~3 min, ~$1 in tokens) so we cache the selectors it finds and reuse them
// indefinitely. A TTL would be wasted effort: if the site ever changes its
// markup the cached selectors will simply return incomplete data, which
// trips the fail counter and forces a fresh discovery anyway.
//
// Invalidation rules:
//   - Extract returns no records, or records missing required fields, 3
//     times in a row → entry is dropped, agent re-discovers.
//   - User can manually wipe via `browse refresh-cache`.
//
// Cache file layout (~/.cache/pricewin-hotel-deal-finder/selectors.json):
//   {
//     "<site>:<locale>:<task>": {
//       "selectors": { "card": "[...]", "name": "[...]", ... },
//       "discoveredAt": ISO,
//       "lastWorkedAt": ISO,
//       "consecutiveFails": 0
//     }
//   }
//
// NOTE: We deliberately do NOT ship a seed file. Selectors and aria-labels
// vary per locale (en-us vs th-th vs ja-jp), per region, and per A/B test
// bucket — shipping one author's selectors would just cause cache misses
// for every user on a different bucket, defeating the whole point of the
// cache. First-time users pay the discovery cost (~3 min, ~$1) once per
// (site, locale) and amortise from there.
// ----------------------------------------------------------------------------

import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { existsSync, mkdirSync } from 'node:fs';

const CACHE_DIR = path.join(os.homedir(), '.cache', 'pricewin-hotel-deal-finder');
const CACHE_FILE = path.join(CACHE_DIR, 'selectors.json');

const MAX_CONSECUTIVE_FAILS = 3;

function ensureCacheDir() {
  if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true });
}

function cacheKey(site, locale, task) {
  return `${site}:${locale}:${task}`;
}

async function readCache() {
  ensureCacheDir();
  if (!existsSync(CACHE_FILE)) return {};
  try {
    return JSON.parse(await fs.readFile(CACHE_FILE, 'utf8'));
  } catch {
    return {};
  }
}

async function writeCache(cache) {
  ensureCacheDir();
  await fs.writeFile(CACHE_FILE, JSON.stringify(cache, null, 2));
}

function isPoisoned(entry) {
  return (entry?.consecutiveFails || 0) >= MAX_CONSECUTIVE_FAILS;
}

/**
 * Get cached selectors. Returns `null` if there's nothing usable — the agent
 * discovery loop should fire and `recordDiscovery` should save the result.
 * No expiration: as long as the selectors keep producing usable data they
 * stay forever.
 */
export async function getSelectors(site, locale, task) {
  const cache = await readCache();
  const entry = cache[cacheKey(site, locale, task)];
  if (!entry) return null;
  if (isPoisoned(entry)) return null;
  return entry.selectors;
}

/**
 * Mark cached selectors as having worked. Resets the fail counter and bumps
 * `lastWorkedAt` so the entry stays warm.
 */
export async function recordSuccess(site, locale, task) {
  const cache = await readCache();
  const key = cacheKey(site, locale, task);
  const entry = cache[key];
  if (!entry) return;
  entry.lastWorkedAt = new Date().toISOString();
  entry.consecutiveFails = 0;
  cache[key] = entry;
  await writeCache(cache);
}

/**
 * Mark cached selectors as having failed (returned no usable data). After
 * `MAX_CONSECUTIVE_FAILS` in a row the entry is considered poisoned and
 * `getSelectors` will return null on the next call, forcing re-discovery.
 */
export async function recordFailure(site, locale, task) {
  const cache = await readCache();
  const key = cacheKey(site, locale, task);
  const entry = cache[key];
  if (!entry) return;
  entry.consecutiveFails = (entry.consecutiveFails || 0) + 1;
  cache[key] = entry;
  await writeCache(cache);
}

/**
 * Save freshly discovered selectors (or overwrite stale ones).
 */
export async function recordDiscovery(site, locale, task, selectors, urlTemplate = null, citySlug = null) {
  const cache = await readCache();
  const key = cacheKey(site, locale, task);
  cache[key] = {
    selectors,
    // Optional URL template. When the template contains a numeric site-specific
    // city param (e.g. Agoda city=3987) that was NOT templatized, citySlug records
    // which city this template is valid for. multi-extract uses citySlug to detect
    // a city mismatch and fall through to discovery instead of returning wrong data.
    urlTemplate,
    ...(citySlug ? { citySlug } : {}),
    discoveredAt: new Date().toISOString(),
    lastWorkedAt: new Date().toISOString(),
    consecutiveFails: 0,
  };
  await writeCache(cache);
}

export async function getEntry(site, locale, task) {
  const cache = await readCache();
  return cache[cacheKey(site, locale, task)] || null;
}

/**
 * Drop a single entry — exposed for manual cache busting via the CLI.
 */
export async function invalidate(site, locale, task) {
  const cache = await readCache();
  delete cache[cacheKey(site, locale, task)];
  await writeCache(cache);
}

/**
 * Drop everything. Useful for `browse refresh-cache --all`.
 */
export async function invalidateAll() {
  await writeCache({});
}

export const _internals = { isPoisoned, MAX_CONSECUTIVE_FAILS };
