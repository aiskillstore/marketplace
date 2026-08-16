#!/usr/bin/env node
// ----------------------------------------------------------------------------
// browse.js — thin HTTP client for the daemon.
//
// All real work happens in bin/daemon.js (a long-running process that owns
// the Patchright browser). This script just spawns the daemon on `launch`
// and POSTs to it for every other subcommand.
//
// Architecture rationale: Patchright's stealth patches only apply when
// commands are issued from the same Node process that called
// `chromium.launch()`. A detached chromium re-attached via CDP from a
// fresh process loses those patches, and Booking/Agoda flag the session
// as a bot. Hence: persistent daemon, ephemeral CLI clients.
// ----------------------------------------------------------------------------

import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  saveState,
  loadState,
  clearState,
  isProcessAlive,
} from '../lib/browser-state.js';
import {
  getSelectors,
  getEntry,
  recordSuccess,
  recordFailure,
  recordDiscovery,
  invalidate,
  invalidateAll,
} from '../lib/selector-cache.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DAEMON_PATH = path.join(__dirname, 'daemon.js');
const OPENTRAVEL_DEFAULT_BASE = 'https://api.opentravel.one';

// --- helpers ----------------------------------------------------------------

function out(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + '\n');
}

function bail(msg, code = 1) {
  process.stdout.write(JSON.stringify({ error: msg }) + '\n');
  process.exit(code);
}

// Every daemon endpoint requires the per-run token from the 0600 state file.
// A state file without one belongs to a pre-1.1.3 daemon still running; the
// call will 401 and the user just needs `browse close` + `launch`.
function authHeaders(state) {
  return state?.token ? { 'x-pricewin-token': state.token } : {};
}

async function daemonState() {
  const state = await loadState();
  if (!state) return null;
  if (!isProcessAlive(state.pid)) return null;
  // ping to confirm daemon is responsive
  try {
    const res = await fetch(`http://127.0.0.1:${state.port}/ping`, {
      headers: authHeaders(state),
      signal: AbortSignal.timeout(2000),
    });
    if (res.ok) return state;
  } catch { /* dead */ }
  return null;
}

async function call(endpoint, args = {}) {
  const state = await daemonState();
  if (!state) bail('No daemon running — call `launch` first.');
  const res = await fetch(`http://127.0.0.1:${state.port}/${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(state) },
    body: JSON.stringify(args),
    signal: AbortSignal.timeout(120_000),
  });
  const json = await res.json();
  if (!res.ok || json.error) bail(json.error || `HTTP ${res.status}`);
  return json;
}

// --- subcommands ------------------------------------------------------------

async function cmdLaunch() {
  const existing = await daemonState();
  if (existing) {
    out({ status: 'already-running', port: existing.port, pid: existing.pid });
    return;
  }

  // Spawn daemon detached. It writes its own state file once the HTTP
  // server is listening; we poll for that file appearing.
  await clearState();
  const child = spawn('node', [DAEMON_PATH], {
    detached: true,
    stdio: 'ignore',
  });
  child.unref();

  const deadline = Date.now() + 30_000; // Patchright launch + Chromium boot
  while (Date.now() < deadline) {
    const state = await daemonState();
    if (state) {
      out({ status: 'launched', port: state.port, pid: state.pid });
      return;
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  bail('Daemon failed to come up within 30s — check stderr or ~/.cache/pricewin-hotel-deal-finder/');
}

async function cmdGoto(url) {
  if (!url) bail('Usage: browse goto <url>');
  out(await call('goto', { url }));
}

async function cmdSnapshot(opts) {
  const r = await call('snapshot');
  if (opts.json) out({ status: 'snapshot', ...r });
  else {
    process.stdout.write(r.text + '\n');
    process.stdout.write(`# snapshot ok · ${r.elementCount} elements\n`);
  }
}

async function cmdClick(ref) {
  if (!ref) bail('Usage: browse click <ref>');
  out(await call('click', { ref }));
}

async function cmdFill(ref, text) {
  if (!ref || text === undefined) bail('Usage: browse fill <ref> <text>');
  out(await call('fill', { ref, text }));
}

async function cmdType(ref, text) {
  if (!ref || text === undefined) bail('Usage: browse type <ref> <text>');
  out(await call('type', { ref, text }));
}

async function cmdPress(ref, key) {
  if (!ref || !key) bail('Usage: browse press <ref> <key>');
  out(await call('press', { ref, key }));
}

async function cmdWaitFor(selector, minCount, timeoutMs) {
  if (!selector) bail('Usage: browse wait-for <selector> [minCount] [timeoutMs]');
  out(await call('wait-for', {
    selector,
    minCount: minCount ? Number(minCount) : 1,
    timeoutMs: timeoutMs ? Number(timeoutMs) : 15_000,
  }));
}

async function cmdTrySelectors(jsonStr) {
  if (!jsonStr) bail('Usage: browse try-selectors <json>');
  let selectors;
  try { selectors = JSON.parse(jsonStr); } catch (e) { bail(`Invalid JSON: ${e.message}`); }
  out(await call('try-selectors', { selectors }));
}

// Like try-selectors but returns the FULL record set (try-selectors caps the
// sample at 3 for a discovery preview). Used for inline ad-hoc extraction.
async function cmdExtractAll(jsonStr) {
  if (!jsonStr) bail('Usage: browse extract-all <json>');
  let selectors;
  try { selectors = JSON.parse(jsonStr); } catch (e) { bail(`Invalid JSON: ${e.message}`); }
  out(await call('extract-all', { selectors }));
}

/**
 * Replace concrete search params + locale segments in a URL with placeholders
 * so the cache can rebuild fresh URLs for new (city, dates, adults, locale)
 * combinations. Handles every well-known query-param name across
 * Booking/Agoda/Traveloka plus the two common locale-segment conventions:
 *   - Booking file suffix:   ".en-gb.html"   → ".{locale-short}.html"
 *   - Agoda path segment:    "/en-us/"       → "/{locale}/"
 * `locale` is the canonical cache-key locale (e.g. "en-us"); `{locale-short}`
 * substitution uses just the language part ("en"). Pass `locale=null` to
 * skip locale templating (rare — only when the captured URL has no locale).
 */
function templatize(url, locale) {
  if (!url) return null;
  let t = url
    .replace(/(?<=[?&])(checkIn|checkin|check_in)=\d{4}-\d{2}-\d{2}/g, '$1={checkIn}')
    .replace(/(?<=[?&])(checkOut|checkout|check_out)=\d{4}-\d{2}-\d{2}/g, '$1={checkOut}')
    // Replace text-based city params with {city}.
    // `city=` is only templated when the value is NOT purely numeric — Agoda stores
    // a numeric cityId (e.g. city=3987) that is city-specific and must be kept
    // as-is; the citySlug cache field handles city validation in multi-extract.
    .replace(/(?<=[?&])(ss|q|destination|textToSearch|searchText)=[^&]+/g, '$1={city}')
    .replace(/(?<=[?&])(city)=(?!\d+(?:&|$))([^&]+)/g, '$1={city}')
    .replace(/(?<=[?&])(adults|group_adults)=\d+/g, '$1={adults}');
  if (locale) {
    const lang = locale.split('-')[0];
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Agoda-style: "/en-us/" → "/{locale}/"
    t = t.replaceAll(`/${locale}/`, '/{locale}/');
    // Booking-style: ".en-gb.html" or ".en-us.html" → ".{locale-short}.html" / ".{locale}.html"
    t = t.replace(new RegExp(`\\.${esc(locale)}\\.html`, 'g'), '.{locale}.html');
    if (lang && lang !== locale) {
      t = t.replace(new RegExp(`\\.${esc(lang)}\\.html`, 'g'), '.{locale-short}.html');
    }
  }
  return t;
}

/**
 * Substitute the `{locale}` / `{locale-short}` placeholders that templatize()
 * introduced. Called when rebuilding a concrete URL from a cached template.
 */
function applyLocale(template, locale) {
  if (!template || !locale) return template;
  const lang = locale.split('-')[0];
  return template
    .replaceAll('{locale}', locale)
    .replaceAll('{locale-short}', lang);
}

async function cmdSaveSelectors(site, locale, task, jsonStr, cityOverride = null) {
  if (!site || !locale || !task || !jsonStr) {
    bail('Usage: browse save-selectors <site> <locale> <task> <json> [city]');
  }
  let selectors;
  try { selectors = JSON.parse(jsonStr); } catch (e) { bail(`Invalid JSON: ${e.message}`); }
  // Capture the current results URL so we can warm-replay it next time.
  let urlTemplate = null;
  let citySlug = null;
  try {
    const cur = await call('current-url');
    urlTemplate = templatize(cur.url, locale);
    // Extract citySlug from text-based city params in the original URL.
    // Stored so multi-extract can validate city-specific templates (e.g. Agoda
    // numeric cityId that wasn't templated).
    try {
      const urlObj = new URL(cur.url);
      const cityParam = urlObj.searchParams.get('textToSearch')
        || urlObj.searchParams.get('ss')
        || urlObj.searchParams.get('q')
        || urlObj.searchParams.get('destination')
        || urlObj.searchParams.get('searchText');
      if (cityParam) citySlug = cityParam.trim().toLowerCase().replace(/\s+/g, '-');
    } catch { /* ignore */ }
  } catch { /* daemon may not be running — fine, save selectors only */ }
  // If caller supplies the city name explicitly (5th arg), it takes priority over
  // the auto-extracted textToSearch. Use this when the URL uses a localized city name
  // (e.g. an OTA may localize the city name) but the user searched in English.
  if (cityOverride) citySlug = cityOverride.trim().toLowerCase().replace(/\s+/g, '-');
  await recordDiscovery(site, locale, task, selectors, urlTemplate, citySlug);
  out({ status: 'saved', site, locale, task, urlTemplate, citySlug });
}

async function cmdTryExtract(site, locale, task) {
  if (!site || !locale || !task) bail('Usage: browse try-extract <site> <locale> <task>');
  const selectors = await getSelectors(site, locale, task);
  if (!selectors) { out({ status: 'cache-miss', site, locale, task }); return; }
  const result = await call('extract-all', { selectors });
  const records = result.records ?? [];
  const stats = result.stats ?? {};
  // "healthy" = at least 3 results with a price. Agoda commonly has 30-50% of
  // cards without a price (sold-out / loading) so we use a loose threshold.
  // IMPORTANT: always return records even when stale — partial data beats nothing.
  const priceRatio = stats.withPrice / Math.max(stats.total, 1);
  const healthy = records.length >= 3 && priceRatio >= 0.3;
  if (healthy) {
    await recordSuccess(site, locale, task);
    out({ status: 'cache-hit', site, locale, task, records, stats });
  } else if (records.length > 0) {
    // partial results — include them so the agent can still present something
    await recordFailure(site, locale, task);
    out({ status: 'cache-partial', site, locale, task, records, stats });
  } else {
    await recordFailure(site, locale, task);
    out({ status: 'cache-stale', site, locale, task, records: [], stats });
  }
}

async function cmdCurrentUrl() {
  out(await call('current-url'));
}

async function cmdMultiExtract(city, checkIn, checkOut, adults = '2', localeArg) {
  if (!city || !checkIn || !checkOut || !localeArg) {
    bail('Usage: browse multi-extract <city> <checkIn> <checkOut> <adults> <locale>\n' +
         '  <locale> is required — pass the user\'s locale code, e.g. en-us, th-th, ja-jp.');
  }
  const locale = localeArg;
  // Google deliberately excluded — its destination layout varies per city
  // (sponsored-overview vs hotel-list), and cards require aria-label parsing,
  // not the textContent extraction multi-extract uses. search.js calls Google
  // inline via searchGoogleHotels() after merging Booking/Agoda results.
  const wantedSites = ['booking', 'agoda'];
  const requests = [];
  const missing = [];
  const citySlugNorm = city.trim().toLowerCase().replace(/\s+/g, '-');
  for (const site of wantedSites) {
    const entry = await getEntry(site, locale, 'search-cards');
    if (!entry?.urlTemplate || !entry?.selectors) {
      missing.push(site);
      continue;
    }
    // City-slug validation: enforce when the URL template contains a
    // hardcoded numeric city ID (Agoda's city=1569). Booking templates use
    // ss={city} placeholders → work for any city, skip check.
    const hasNumericCityId = /(?:^|[?&])(?:city|cityId|dest_id|destinationId)=\d+/i
      .test(entry.urlTemplate || '');
    if (hasNumericCityId && entry.citySlug && entry.citySlug !== citySlugNorm) {
      missing.push(site);
      continue;
    }
    const url = applyLocale(entry.urlTemplate, locale)
      .replaceAll('{city}', encodeURIComponent(city))
      .replaceAll('{checkIn}', checkIn)
      .replaceAll('{checkOut}', checkOut)
      .replaceAll('{adults}', String(adults));
    requests.push({ site, url, selectors: entry.selectors });
  }
  if (!requests.length) {
    out({ status: 'no-cache', missing, message: 'No cached URL templates. Run discovery for at least one OTA.' });
    return;
  }
  // Fire daemon multi-extract + the OpenTravel API call in parallel.
  const [otaResp, otResp] = await Promise.allSettled([
    call('multi-extract-urls', { requests }),
    cmdOpentravelInternal(city, checkIn, checkOut, adults),
  ]);
  out({
    status: 'multi-extract',
    missing,
    ota: otaResp.status === 'fulfilled' ? otaResp.value : { error: otaResp.reason?.message },
    opentravel: otResp.status === 'fulfilled' ? otResp.value : { error: otResp.reason?.message },
  });
}

async function cmdOpentravelInternal(city, checkIn, checkOut, adults) {
  const base = process.env.OPENTRAVEL_API_BASE_URL || OPENTRAVEL_DEFAULT_BASE;
  const url = new URL('/api/v1/public/hotels/search', base);
  url.searchParams.set('city', city);
  url.searchParams.set('checkIn', checkIn);
  url.searchParams.set('checkOut', checkOut);
  url.searchParams.set('adults', String(adults));
  url.searchParams.set('limit', '20');
  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(15_000),
  });
  if (!res.ok) throw new Error(`OpenTravel API ${res.status}`);
  const json = await res.json();
  const payload = json?.data ?? json;
  return {
    hotels: payload.hotels || [],
    indicativeHotels: payload.indicativeHotels || [],
    meta: payload.meta || null,
  };
}

async function cmdOpentravel(city, checkIn, checkOut, adults = '2') {
  if (!city || !checkIn || !checkOut) {
    bail('Usage: browse opentravel <city> <checkIn YYYY-MM-DD> <checkOut YYYY-MM-DD> [adults]');
  }
  const base = process.env.OPENTRAVEL_API_BASE_URL || OPENTRAVEL_DEFAULT_BASE;
  const url = new URL('/api/v1/public/hotels/search', base);
  url.searchParams.set('city', city);
  url.searchParams.set('checkIn', checkIn);
  url.searchParams.set('checkOut', checkOut);
  url.searchParams.set('adults', String(adults));
  url.searchParams.set('limit', '20');
  try {
    const res = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) bail(`OpenTravel API ${res.status}`);
    const json = await res.json();
    const payload = json?.data ?? json;
    out({
      status: 'opentravel-ok',
      hotels: payload.hotels || [],
      indicativeHotels: payload.indicativeHotels || [],
      meta: payload.meta || null,
    });
  } catch (e) {
    bail(`OpenTravel fetch failed: ${e.message}`);
  }
}

async function cmdCacheList() {
  const fs = await import('node:fs/promises');
  const path = await import('node:path');
  const os = await import('node:os');
  const cacheFile = path.join(os.homedir(), '.cache', 'pricewin-hotel-deal-finder', 'selectors.json');
  try {
    const raw = await fs.readFile(cacheFile, 'utf8');
    const cache = JSON.parse(raw);
    const entries = Object.entries(cache).map(([key, v]) => ({
      key,
      lastWorkedAt: v.lastWorkedAt,
      discoveredAt: v.discoveredAt,
      consecutiveFails: v.consecutiveFails || 0,
      fields: Object.keys(v.selectors || {}),
    }));
    out({ status: 'cache-list', entries });
  } catch (e) {
    if (e.code === 'ENOENT') out({ status: 'cache-list', entries: [] });
    else bail(`Cache read failed: ${e.message}`);
  }
}

async function cmdRefreshCache(siteOrAll, locale, task) {
  if (siteOrAll === '--all') {
    await invalidateAll();
    out({ status: 'cache-wiped' });
    return;
  }
  if (!siteOrAll || !locale || !task) {
    bail('Usage: browse refresh-cache <site> <locale> <task>  |  browse refresh-cache --all');
  }
  await invalidate(siteOrAll, locale, task);
  out({ status: 'cache-evicted', site: siteOrAll, locale, task });
}

async function cmdClose() {
  const state = await daemonState();
  if (!state) { out({ status: 'no-session' }); return; }
  try { await call('shutdown'); } catch { /* daemon may have exited mid-reply */ }
  // give daemon a beat to actually exit
  await new Promise((r) => setTimeout(r, 500));
  await clearState();
  out({ status: 'closed' });
}

// --- dispatcher -------------------------------------------------------------

const [, , cmd, ...args] = process.argv;

const router = {
  launch: () => cmdLaunch(),
  goto: () => cmdGoto(args[0]),
  snapshot: () => cmdSnapshot({ json: args.includes('--json') }),
  click: () => cmdClick(args[0]),
  fill: () => cmdFill(args[0], args.slice(1).join(' ')),
  type: () => cmdType(args[0], args.slice(1).join(' ')),
  scroll: async () => out(await call('scroll', {
    to: args[0] ? Number(args[0]) : 3000,
    step: args[1] ? Number(args[1]) : 600,
    delayMs: args[2] ? Number(args[2]) : 200,
  })),
  'keyboard-press': async () => out(await call('keyboard-press', { key: args[0] || 'Escape' })),
  'list-pages': async () => out(await call('list-pages')),
  'query-all': async () => out(await call('query-all', {
    selector: args[0] || '',
    limit: args[1] ? Number(args[1]) : 20,
    textLimit: args[2] !== undefined ? Number(args[2]) : 80,
  })),
  'switch-to-newest-tab': async () => out(await call('switch-to-newest-tab')),
  'switch-to-tab-matching': async () => out(await call('switch-to-tab-matching', { urlIncludes: args[0] || '', urlAvoids: args[1] || '' })),
  'close-tabs-matching': async () => out(await call('close-tabs-matching', { urlIncludes: args[0] || '' })),
  press: () => cmdPress(args[0], args[1]),
  'wait-for': () => cmdWaitFor(args[0], args[1], args[2]),
  'try-selectors': () => cmdTrySelectors(args[0]),
  'extract-all': () => cmdExtractAll(args[0]),
  'save-selectors': () => cmdSaveSelectors(args[0], args[1], args[2], args[3], args[4]),
  'try-extract': () => cmdTryExtract(args[0], args[1], args[2]),
  'current-url': () => cmdCurrentUrl(),
  opentravel: () => cmdOpentravel(args[0], args[1], args[2], args[3]),
  'multi-extract': () => cmdMultiExtract(args[0], args[1], args[2], args[3], args[4]),
  'cache-list': () => cmdCacheList(),
  'refresh-cache': () => cmdRefreshCache(args[0], args[1], args[2]),
  close: () => cmdClose(),
};

if (!cmd || !router[cmd]) {
  process.stderr.write(`Usage: browse <command> [args]\nCommands: ${Object.keys(router).join(', ')}\n`);
  process.exit(2);
}

router[cmd]().catch((e) => bail(e.message || String(e)));
