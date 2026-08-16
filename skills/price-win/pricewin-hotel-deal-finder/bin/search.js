#!/usr/bin/env node
/**
 * search.js — one-shot hotel search wrapper.
 *
 * Usage:
 *   node bin/search.js "<city>" <checkIn> <checkOut> <adults> [locale]
 *
 * Returns formatted tier-card result for Telegram.
 * Handles: daemon launch, multi-extract (cache), Agoda discovery, formatting.
 */

import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import readline from 'node:readline';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BROWSE = path.join(__dirname, 'browse.js');

const [,, city, checkIn, checkOut, adults = '2', locale = 'en-us'] = process.argv;
if (!city || !checkIn || !checkOut) {
  console.error('Usage: node bin/search.js "<city>" <checkIn> <checkOut> [adults] [locale]');
  process.exit(1);
}

function run(args, timeoutMs = 60000) {
  return new Promise((resolve, reject) => {
    const child = spawn('node', [BROWSE, ...args], { cwd: path.dirname(__dirname) });
    let out = '';
    child.stdout.on('data', d => out += d);
    child.stderr.on('data', d => out += d);
    const t = setTimeout(() => { child.kill(); reject(new Error(`Timeout after ${timeoutMs}ms: node ${BROWSE} ${args[0]}`)); }, timeoutMs);
    child.on('close', code => { clearTimeout(t); resolve(out.trim()); });
  });
}

function parse(raw) {
  try { return JSON.parse(raw); } catch { return null; }
}

function fmt(n) { return '$' + Number(n).toLocaleString('en-US'); }

/**
 * Neutralize untrusted third-party text before it reaches model-visible output.
 *
 * Hotel names come from OTA DOM (Booking title, Agoda hotel-name), Google
 * aria-labels, and the OpenTravel API — none of it is trusted. sanitizeText
 * defends on two fronts:
 *   1. Indirect prompt injection — strips control/zero-width/bidi chars, defangs
 *      the markdown/link control set, and collapses whitespace so scraped text
 *      cannot smuggle directives or fake structure into the agent's context.
 *   2. MarkdownV2 integrity — the same removed characters (brackets, parens,
 *      backticks, backslashes, angle/brace/pipe) are exactly what would corrupt
 *      the `[name](url)` link syntax, so a crafted or malformed name can't break
 *      the rendered output.
 * Empty string ⇒ record is skipped upstream (treated as "no name").
 */
function sanitizeText(s, max = 80) {
  if (typeof s !== 'string') return '';
  let t = s
    .normalize('NFC')
    .replace(/[\u0000-\u001F\u007F-\u009F]/g, " ")   // control chars
    .replace(/[\u200B-\u200F\u202A-\u202E\u2066-\u2069\u2028\u2029\uFEFF]/g, "") // zero-width / bidi / line-sep
    .replace(/[`[\]()<>{}\\|]/g, ' ')                    // markdown + link-breaking chars
    .replace(/\s+/g, ' ')
    .trim();
  if (t.length > max) t = t.slice(0, max).trim() + '…';
  return t;
}

// Prices are normalized to USD for display. Agoda, Google and OpenTravel
// geo-lock to VND by IP (so they need conversion); Booking honours USD. The
// per-record `currency` from extraction drives the conversion. Rate is fetched
// live with a sane fallback.
let VND_PER_USD = 25400;
async function loadFxRate() {
  try {
    const res = await fetch('https://open.er-api.com/v6/latest/USD', { signal: AbortSignal.timeout(8000) });
    const j = await res.json();
    const r = j?.rates?.VND;
    if (Number.isFinite(r) && r > 1000) VND_PER_USD = r;
  } catch { /* keep fallback */ }
}
function toUSD(price, currency) {
  const n = Number(price);
  if (!Number.isFinite(n) || n <= 0) return 0;
  if (currency === 'VND') return Math.max(1, Math.round(n / VND_PER_USD));
  return Math.max(1, Math.round(n)); // already USD (or assume USD)
}

// OTAs compared by this skill. OpenTravel is an independent provider, listed
// in the same tier as Booking/Agoda/Google (not a PriceWin "direct" source).
const OTAS = ['agoda', 'booking', 'google', 'opentravel'];
const OTA_LABEL = { agoda: 'Agoda', booking: 'Booking', google: 'Google', opentravel: 'OpenTravel' };
function label(site) { return OTA_LABEL[site] || (site.charAt(0).toUpperCase() + site.slice(1)); }

/**
 * Normalize a raw link from extraction:
 *   - Resolve relative Agoda paths to absolute URLs
 *   - Strip session/tracking params that add noise and can break markdown parsers
 *     (e.g. flightSearchCriteria=[object Object] breaks MarkdownV2 link regex)
 */
function cleanLink(url, site) {
  if (!url) return '';
  // Agoda and Google both return relative hrefs — prepend their host
  if (url.startsWith('/')) {
    if (site === 'agoda') url = 'https://www.agoda.com' + url;
    else if (site === 'google') url = 'https://www.google.com' + url;
  }
  // Leave other relative/unknown links blank (can't produce a clickable URL)
  if (!url.startsWith('http')) return '';
  try {
    const u = new URL(url);
    if (site === 'agoda') {
      // Strip Agoda session + noise params (includes the [object Object] offender)
      for (const p of [
        'flightSearchCriteria', 'searchrequestid', 'isShowMobileAppPrice',
        'finalPriceView', 'isCalendarCallout', 'missingChildAges',
        'numberOfGuest', 'numberOfBedrooms', 'familyMode', 'maxRooms',
        'showReviewSubmissionEntry', 'isFreeOccSearch', 'tspTypes', 'cid',
      ]) u.searchParams.delete(p);
    }
    if (site === 'booking') {
      // Strip Booking tracking/session params
      for (const p of [
        'aid', 'label', 'ucfs', 'arphpl', 'srpvid', 'srepoch',
        'all_sr_blocks', 'highlighted_blocks', 'matching_block_id',
        'sr_pri_blocks', 'from', 'hapos', 'hpos', 'sr_order',
        'nad_id', 'nad_cpc', 'nad_track', 'nad_placement',
        'req_adults', 'req_children', 'group_children', 'no_rooms',
      ]) u.searchParams.delete(p);
    }
    if (site === 'google') {
      // Strip Google's search-context noise. `qs=` identifies the hotel
      // itself; ved/ts/ap/q are derived from the originating search.
      for (const p of ['ved', 'ts', 'ap', 'q']) u.searchParams.delete(p);
    }
    return u.toString();
  } catch {
    return url;
  }
}

async function main() {
  // ── Step 0: ensure daemon ────────────────────────────────────────────────
  process.stderr.write('[search] launching daemon...\n');
  const launchRaw = await run(['launch'], 30000);
  const launchR = parse(launchRaw);
  if (!launchR || (launchR.status !== 'launched' && launchR.status !== 'already-running')) {
    process.stderr.write(`[search] daemon error: ${launchRaw}\n`);
    process.exit(1);
  }
  process.stderr.write(`[search] daemon ok (pid ${launchR.pid || '?'})\n`);

  // FX rate for VND→USD display conversion (all sources price in VND).
  await loadFxRate();
  process.stderr.write(`[search] fx: 1 USD = ${VND_PER_USD} VND\n`);

  // ── Step 1: OpenTravel API ──────────────────────────────────────────────
  process.stderr.write('[search] opentravel API...\n');
  const otRaw = await run(['opentravel', city, checkIn, checkOut, adults], 20000);
  const otR = parse(otRaw) || {};

  // ── Step 1.5: fast-path multi-extract (Booking + Agoda) ──────────────────
  process.stderr.write('[search] multi-extract (booking + agoda)...\n');
  const meRaw = await run(['multi-extract', city, checkIn, checkOut, adults, locale], 60000);
  let meR = parse(meRaw);

  // ── Step 3.5: discovery for missing Agoda (per-city numeric cityId) ──────
  let missing = meR?.missing ?? [];
  if (missing.includes('agoda')) {
    process.stderr.write('[search] agoda not cached — running discovery...\n');
    try {
      await discoverAgoda(city, checkIn, checkOut, adults, locale);
      process.stderr.write('[search] agoda discovery done, re-running multi-extract...\n');
      const meRaw2 = await run(['multi-extract', city, checkIn, checkOut, adults, locale], 60000);
      meR = parse(meRaw2) ?? meR;
    } catch (e) {
      process.stderr.write(`[search] agoda discovery failed: ${e.message}\n`);
    }
  }

  // ── Step 5: merge Booking + Agoda + OpenTravel ─────────────────────────
  const all = {};

  for (const r of (meR?.ota?.results ?? [])) {
    const site = r.site;
    for (const h of (r.records ?? [])) {
      const name = sanitizeText(h.name);
      if (!name || !h.price) continue;
      if (!all[name]) all[name] = { prices: {}, links: {} };
      all[name].prices[site] = toUSD(h.price, h.currency);
      all[name].links[site] = cleanLink(h.link ?? '', site);
    }
  }

  // ── Step 5.5: Google Hotels via aria-label extraction ────────────────────
  // No URL caching — Google's destination layout varies per city and the
  // aria-label structure changes with locale. Always re-navigate.
  process.stderr.write('[search] google search inline...\n');
  try {
    const googleRecords = await searchGoogleHotels(city, checkIn, checkOut, locale);
    process.stderr.write(`[search] google returned ${googleRecords.length} records\n`);
    for (const h of googleRecords) {
      const name = sanitizeText(h.name);
      if (!name || !h.price) continue;
      if (!all[name]) all[name] = { prices: {}, links: {} };
      all[name].prices.google = toUSD(h.price, h.currency);
      all[name].links.google = cleanLink(h.link ?? '', 'google');
    }
  } catch (e) {
    process.stderr.write(`[search] google search failed: ${e.message}\n`);
  }

  // ── Step 5.6: Booking.com via direct searchresults URL ───────────────────
  // Booking honours `selected_currency=USD`, so its prices come back in USD.
  process.stderr.write('[search] booking search inline...\n');
  try {
    const bookingRecords = await searchBookingHotels(city, checkIn, checkOut, adults);
    process.stderr.write(`[search] booking returned ${bookingRecords.length} records\n`);
    for (const h of bookingRecords) {
      const name = sanitizeText(h.name);
      if (!name || !h.price) continue;
      if (!all[name]) all[name] = { prices: {}, links: {} };
      all[name].prices.booking = toUSD(h.price, h.currency);
      all[name].links.booking = cleanLink(h.link ?? '', 'booking');
    }
  } catch (e) {
    process.stderr.write(`[search] booking search failed: ${e.message}\n`);
  }

  // OpenTravel — an independent OTA, same tier as Booking/Agoda/Google.
  // Per-night price comes from `cheapestPrice`; the public API returns no
  // booking URL, so the link stays empty (name renders as plain text).
  for (const h of [...(otR.hotels ?? []), ...(otR.indicativeHotels ?? [])]) {
    const name = sanitizeText(h.name);
    const price = h.cheapestPrice ?? h.price ?? h.pricePerNight;
    if (!name || !price) continue;
    if (!all[name]) all[name] = { prices: {}, links: {} };
    all[name].prices.opentravel = toUSD(price, h.currency ?? 'VND');
    // Route the partner-API link through cleanLink too, so a non-http(s)
    // value (e.g. javascript:) can never reach a rendered hyperlink.
    all[name].links.opentravel = cleanLink(h.url ?? h.link ?? '', 'opentravel');
  }

  const sorted = Object.entries(all).sort((a, b) =>
    Math.min(...Object.values(a[1].prices)) - Math.min(...Object.values(b[1].prices)));

  if (!sorted.length) {
    console.log(`❌ No hotels found for ${city} (${checkIn}→${checkOut}).`);
    console.log('   No results from Booking · Agoda · Google · OpenTravel for this city/date.');
    process.exit(0);
  }

  const nights = Math.round((new Date(checkOut) - new Date(checkIn)) / 86400000);
  const d1 = checkIn.slice(5).replace('-', '/');
  const d2 = checkOut.slice(5).replace('-', '/');

  const lines = [];
  lines.push(`🏨 ${sanitizeText(city, 60) || city} • ${d1}–${d2} • ${nights} nights • ${adults} guests`);
  lines.push('━'.repeat(20));

  const labels = ['🥇 BEST VALUE', '🥈 CHEAPEST', '🥉 QUALITY'];
  for (let i = 0; i < Math.min(3, sorted.length); i++) {
    const [name, { prices, links }] = sorted[i];
    const priceEntries = Object.entries(prices).sort((a, b) => a[1] - b[1]);
    const best = priceEntries[0];
    const worst = priceEntries[priceEntries.length - 1];
    lines.push('');
    lines.push(labels[i]);
    // Hotel name as Markdown link → cheapest OTA. transform_llm_output bypasses
    // the model so [text](url) syntax survives intact through to Telegram's
    // format_message which converts it to a MarkdownV2 hyperlink (clickable,
    // no raw URL visible).
    const cheapestUrl = links[best[0]];
    lines.push(`  ${cheapestUrl ? `[${name}](${cheapestUrl})` : name}`);
    for (const [site, price] of priceEntries) {
      const mark = site === best[0] ? '✅' : '  ';
      lines.push(`  ${mark} ${site.padEnd(10)} 💰 ${fmt(price)}/night`);
    }
    const diff = worst[1] - best[1];
    if (priceEntries.length > 1 && diff > 3) {
      lines.push(`     → Save ${fmt(diff)} vs ${label(worst[0])}`);
    }
  }

  // "More good deals" — balanced per-OTA picks instead of a flat
  // cheapest-first list (which Google would dominate, since it returns the
  // most records). For each OTA in order: take the 3 cheapest hotels on
  // that OTA that aren't already in the top-3 tier cards above.
  if (sorted.length > 3) {
    const topNames = new Set(sorted.slice(0, 3).map(([n]) => n));
    const picks = [];
    const used = new Set();
    for (const ota of OTAS) {
      const onOta = Object.entries(all)
        .filter(([n, d]) => d.prices[ota] != null && !topNames.has(n) && !used.has(n))
        .sort((a, b) => a[1].prices[ota] - b[1].prices[ota])
        .slice(0, 3);
      for (const entry of onOta) {
        picks.push({ ota, entry });
        used.add(entry[0]);
      }
    }
    if (picks.length) {
      lines.push('');
      lines.push('📋 More good deals');
      let curOta = null;
      for (const { ota, entry } of picks) {
        if (ota !== curOta) {
          lines.push(`  — ${label(ota)} —`);
          curOta = ota;
        }
        const [name, { prices, links }] = entry;
        // Order prices so the section's own OTA is first; hyperlink hotel
        // name to that OTA's URL so the click goes to the platform the row
        // is grouped under.
        const priceEntries = Object.entries(prices).sort((a, b) => {
          if (a[0] === ota) return -1;
          if (b[0] === ota) return 1;
          return a[1] - b[1];
        });
        const sectionUrl = links[ota];
        const truncName = name.slice(0, 45);
        const nameLink = sectionUrl ? `[${truncName}](${sectionUrl})` : truncName;
        const priceStr = priceEntries.map(([s, p]) => `${s}: ${fmt(p)}`).join(' | ');
        lines.push(`  • ${nameLink} — ${priceStr}`);
      }
    }
  }

  const [bestName, bestData] = sorted[0];
  const bestSite = Object.entries(bestData.prices).sort((a,b)=>a[1]-b[1])[0][0];
  const bestPrice = Math.min(...Object.values(bestData.prices));
  lines.push('');
  lines.push(`💡 Tip: ${bestName}`);
  const bestLink = bestData.links[bestSite];
  const bestSiteCap = label(bestSite);
  const cta = bestLink ? `[Book on ${bestSiteCap}](${bestLink})` : `Book on ${bestSiteCap}`;
  lines.push(`   ${cta} — ${fmt(bestPrice)}/night`);
  // Only credit sources that actually returned data this run.
  const presentSites = OTAS.filter(s => sorted.some(([, d]) => d.prices[s] != null));
  lines.push(`\n📊 ${sorted.length} hotels | ${presentSites.map(label).join(' · ')} • prices in USD`);

  console.log(lines.join('\n'));

  // ── Cleanup ────────────────────────────────────────────────────────────────
  await run(['close'], 5000).catch(() => {});
}

async function discoverAgoda(city, checkIn, checkOut, adults, locale) {
  async function r(args, t = 30000) { return parse(await run(args, t)); }

  // Navigate to Agoda homepage
  await r(['goto', `https://www.agoda.com/${locale}/`], 20000);

  // Find and type in search box
  const snap1Raw = await run(['snapshot'], 10000);
  const inputRef = snap1Raw.match(/\[(\d+)\][^\n]*data-selenium="textInput"/)?.[1];
  if (!inputRef) throw new Error('Agoda search input not found');

  await r(['type', inputRef, city]);
  await new Promise(res => setTimeout(res, 3000));

  // Click first autocomplete suggestion
  const snap2Raw = await run(['snapshot'], 10000);
  const optRef = snap2Raw.match(/\[(\d+)\][^\n]*autosuggest-item/)?.[1];
  if (!optRef) throw new Error('No autocomplete suggestion for: ' + city);

  await r(['click', optRef]);
  await new Promise(res => setTimeout(res, 1000));
  await r(['keyboard-press', 'Escape']);
  await new Promise(res => setTimeout(res, 500));

  // Find and click search button. Agoda's en-us label is "SEARCH" (uppercase);
  // match case-insensitively to tolerate locale/label variations.
  const snap3Raw = await run(['snapshot'], 10000);
  const btnRef = snap3Raw.match(/\[(\d+)\] button "SEARCH"/i)?.[1];
  if (!btnRef) throw new Error('Search button not found');

  await r(['click', btnRef]);
  await new Promise(res => setTimeout(res, 4000));

  // Switch to hotel results tab if needed. Agoda opens hotel results in a new
  // tab at `agoda.com/search` (no locale segment), while the original tab may
  // land on `/activities/`. Match the hotel-results URL, not a locale path.
  const urlRaw = await r(['current-url'], 5000);
  if (!urlRaw?.url?.includes('agoda.com/search')) {
    await r(['switch-to-tab-matching', 'agoda.com/search', 'activities'], 10000);
    await new Promise(res => setTimeout(res, 2000));
  }

  // Guard: only cache once we're actually on a hotel-results page. If Agoda
  // redirected to the homepage/overview (anti-bot, or the search never went
  // through), bail without caching a broken URL — the caller continues with
  // Booking + Google, and the next run retries discovery cleanly.
  const finalUrl = await r(['current-url'], 5000);
  if (!finalUrl?.url?.includes('agoda.com/search')) {
    throw new Error('Agoda did not reach a results page (homepage redirect / anti-bot)');
  }

  // Save selectors immediately with city as slug
  await r(['save-selectors', 'agoda', locale, 'search-cards',
    JSON.stringify({
      card: 'li[data-selenium=hotel-item]',
      name: '[data-selenium=hotel-name]',
      price: '[data-element-name=final-price]',
      link: '[data-selenium=hotel-name]',
    }),
    city,
  ], 10000);

  // Wait for cards and extract
  await new Promise(res => setTimeout(res, 3000));
  await r(['try-extract', 'agoda', locale, 'search-cards'], 15000);
}

/**
 * Search Google Hotels for a city and parse cards via aria-label.
 *
 * Google's destination layout doesn't fit our generic textContent extractor:
 *   - h2 inside a card can be the room description instead of the hotel name
 *     → unreliable for matching across OTAs
 *   - Price text concatenates discounts/totals → naive digit-parsing produces
 *     garbage
 *
 * The price link for each card has an aria-label of the form
 *   "Prices for <HotelName> start at <currency><price>"
 * which contains both name and price in a single, parseable string.
 *
 * Returns array of { name, price, link }. Throws on navigation failure.
 */
async function searchGoogleHotels(city, checkIn, checkOut, locale) {
  async function r(args, t = 30000) { return parse(await run(args, t)); }
  const lang = (locale || 'en-us').split('-')[0];

  const url = `https://www.google.com/travel/search`
    + `?q=${encodeURIComponent(city)}`
    + `&hl=${lang}&gl=us&curr=USD`
    + `&checkin=${checkIn}&checkout=${checkOut}`;
  await r(['goto', url], 25000);
  await new Promise(res => setTimeout(res, 6000));

  // Per-card aria-label selector — the English Google Hotels price link reads
  // "Prices starting from <price>, <HotelName>".
  const selector = 'a[aria-label^="Prices starting from"]';

  const probeRaw = await run(['query-all', selector, '50', '0'], 15000);
  const probe = parse(probeRaw);
  if (!probe?.matches?.length) {
    throw new Error('Google Hotels: no price-link cards found (selector="' + selector + '")');
  }

  // Parse aria-label "Prices starting from <currency><price>, <HotelName>".
  // Price comes first (skip the currency symbol/code before the digits), then
  // the hotel name after the comma.
  const enRe = /^Prices starting from\s*\D*?([\d.,]+),\s*(.+)$/;
  const records = [];
  for (const m of probe.matches) {
    const aria = m.ariaLabel || '';
    const match = aria.match(enRe);
    if (!match) continue;
    // Strip Google's promo suffix ("... GREAT DEAL 51% less than usual",
    // "... DEAL 19% less than") so the name dedupes cleanly across OTAs.
    const name = match[2].replace(/\s+(GREAT DEAL|DEAL)\b.*$/i, '').trim();
    const priceDigits = match[1].replace(/[^\d]/g, '');
    const price = Number(priceDigits);
    if (!name || !Number.isFinite(price) || price <= 0) continue;
    const currency = /US\$|\bUSD\b|^\$|\s\$/.test(aria) ? 'USD' : 'VND';
    records.push({ name, price, link: m.href || '', currency });
  }
  return records;
}

/**
 * Search Booking.com via its direct searchresults URL and extract cards with an
 * ad-hoc selector recipe (no cache/discovery needed — the URL is built fresh
 * each time). Booking honours `selected_currency=USD`, so prices come back in
 * USD; the recipe also reports the detected currency per record.
 *
 * Returns array of { name, price, currency, link }.
 */
async function searchBookingHotels(city, checkIn, checkOut, adults) {
  const url = 'https://www.booking.com/searchresults.html'
    + `?ss=${encodeURIComponent(city)}`
    + `&checkin=${checkIn}&checkout=${checkOut}`
    + `&group_adults=${adults}&no_rooms=1&group_children=0&selected_currency=USD`;
  await run(['goto', url], 30000);
  await new Promise(res => setTimeout(res, 6000));
  // Booking lazy-loads property cards on scroll — scroll down to populate more.
  for (let i = 0; i < 3; i++) {
    await run(['scroll', '6000', '900', '250'], 15000);
    await new Promise(res => setTimeout(res, 1200));
  }

  const recipe = JSON.stringify({
    card: 'div[data-testid=property-card]',
    name: 'div[data-testid=title]',
    price: 'span[data-testid=price-and-discounted-price]',
    link: 'a[data-testid=title-link]',
  });
  const raw = parse(await run(['extract-all', recipe], 15000));
  const recs = raw?.records ?? [];
  return recs
    .filter(r => r?.name && r?.price)
    .map(r => ({ name: r.name.trim(), price: r.price, currency: r.currency, link: r.link || '' }));
}

main().catch(e => {
  console.error('[search] fatal:', e.message);
  process.exit(1);
});
