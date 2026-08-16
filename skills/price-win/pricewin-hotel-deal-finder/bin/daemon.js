#!/usr/bin/env node
// ----------------------------------------------------------------------------
// daemon.js
//
// Long-running process that owns the Patchright Chromium browser and serves
// each agent action over a localhost HTTP endpoint. Critical: Patchright's
// stealth patches (CDP-level fingerprint masking) only apply when commands
// flow through the same Node process that called `chromium.launch()`. If we
// instead detached the browser and re-attached via `connectOverCDP` from a
// fresh process (the v0.2-rc.1 design), Booking/Agoda see plain headless
// Chrome and degrade the response. Hence: one daemon, many CLI clients.
//
// Lifecycle:
//   - bin/browse.js spawns this with `detached: true` + `unref()` on launch.
//   - State (port, pid, token) is written to
//     ~/.cache/pricewin-hotel-deal-finder/session-default.json (0600)
//   - SIGTERM (sent by `browse close`) → clean shutdown.
//
// Security: this endpoint drives a real browser and returns page content, so it
// is treated as privileged. It binds loopback only, requires a per-run bearer
// token that lives in the 0600 state file, and rejects non-loopback Host headers
// (DNS-rebinding defence — a web page cannot reach it even knowing the port).
// ----------------------------------------------------------------------------

import http from 'node:http';
import net from 'node:net';
import crypto from 'node:crypto';
import { chromium } from 'patchright';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { takeSnapshot } from '../lib/snapshot.js';
import { extractWithSelectors, isExtractionHealthy } from '../lib/dom-extract.js';
import { saveState, clearState } from '../lib/browser-state.js';

const CACHE_DIR = path.join(os.homedir(), '.cache', 'pricewin-hotel-deal-finder');

// Per-run bearer token. Generated here, handed to clients only through the 0600
// state file, so a process that cannot read that file cannot drive the browser.
const AUTH_HEADER = 'x-pricewin-token';
const AUTH_TOKEN = crypto.randomBytes(32).toString('hex');

function isAuthorized(req) {
  const got = req.headers[AUTH_HEADER];
  if (typeof got !== 'string') return false;
  const a = Buffer.from(got);
  const b = Buffer.from(AUTH_TOKEN);
  // timingSafeEqual throws on length mismatch, so compare lengths first.
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Reject anything whose Host is not loopback. Without this, a page in any
// browser could POST to http://<attacker-domain>/ resolving to 127.0.0.1 and
// hit the daemon; with it, only a client that already knows to say "127.0.0.1"
// (and holds the token) gets through.
function isLoopbackHost(req) {
  const host = String(req.headers.host || '');
  const name = host.replace(/:\d+$/, '').replace(/^\[|\]$/g, '');
  return name === '127.0.0.1' || name === 'localhost' || name === '::1';
}

let browser;
let context;
let page;
// In-memory map of ref → stable CSS selector, populated by each snapshot
// and consumed by click/type/fill/press so the agent doesn't fail when
// React/Vue re-renders strip our data-browse-ref attribute.
let lastSnapshotRefs = {};

// In-memory results cache for multi-extract-urls.
// Key: "<site>:<url>". Entries expire after RESULTS_CACHE_TTL_MS (10 min).
// Purpose: avoid re-scraping the same (site, city, dates, adults) within a
// single working session — prices don't change that fast, and the scroll
// pipeline (~10s per OTA) is expensive.
const RESULTS_CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes
const resultsCache = new Map();

function getCachedResult(site, url) {
  const key = `${site}:${url}`;
  const entry = resultsCache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.cachedAt > RESULTS_CACHE_TTL_MS) {
    resultsCache.delete(key);
    return null;
  }
  return entry;
}

function setCachedResult(site, url, records, stats) {
  resultsCache.set(`${site}:${url}`, { records, stats, cachedAt: Date.now() });
}

function normalizeRef(ref) {
  // Some LLMs hand us refs with prefixes ("@e16", "ref-12", "#27").
  // Strip everything that isn't a digit so the lookup still hits the map.
  const s = String(ref ?? '');
  const m = s.match(/\d+/);
  return m ? m[0] : s;
}

function refToEntry(ref) {
  const key = normalizeRef(ref);
  const entry = lastSnapshotRefs[key];
  if (entry && typeof entry === 'object') return entry;
  return { selector: `[data-browse-ref="${key}"]`, signature: null };
}

function refToSelector(ref) {
  return refToEntry(ref).selector;
}

/**
 * Resolve a ref to the live DOM element by trying:
 *   1) stable CSS selector saved at snapshot time
 *   2) data-browse-ref attribute (may have been stripped by React)
 *   3) signature match (tag + kind + text + testid + ariaLabel + placeholder + href)
 * Returns the matching CSS selector (possibly a fresh data-browse-ref the
 * resolver wrote back onto the element) or throws.
 */
async function resolveRef(page, ref) {
  const refKey = normalizeRef(ref);
  const entry = refToEntry(refKey);
  const sel = await page.evaluate(
    ({ ref, entry }) => {
      const tryCount = (s) => {
        try { return document.querySelectorAll(s).length; } catch { return 0; }
      };
      if (entry.selector && tryCount(entry.selector) === 1) return entry.selector;
      const byRef = '[data-browse-ref="' + ref + '"]';
      if (tryCount(byRef) === 1) return byRef;
      const sig = entry.signature;
      if (!sig) return null;
      // Re-scan the DOM for an element matching the signature.
      const candidates = Array.from(document.querySelectorAll(sig.tag || '*'));
      const norm = (s) => (s || '').replace(/\s+/g, ' ').trim().toLowerCase().slice(0, 160);
      const targetText = norm(sig.text);
      let best = null;
      let bestScore = -1;
      for (const el of candidates) {
        let score = 0;
        if (sig.testid && (el.getAttribute('data-testid') === sig.testid || el.getAttribute('data-selenium') === sig.testid)) score += 5;
        if (sig.ariaLabel && el.getAttribute('aria-label') === sig.ariaLabel) score += 4;
        if (sig.placeholder && el.getAttribute('placeholder') === sig.placeholder) score += 3;
        if (sig.href && el.getAttribute('href') === sig.href) score += 4;
        if (targetText && norm(el.innerText || el.value || '') === targetText) score += 2;
        if (score > bestScore) { bestScore = score; best = el; }
      }
      if (!best || bestScore < 2) return null;
      // Tag the winner with a fresh data-browse-ref so callers have a stable
      // handle for follow-up operations.
      best.setAttribute('data-browse-ref', String(ref));
      return '[data-browse-ref="' + ref + '"]';
    },
    { ref: refKey, entry },
  );
  if (!sel) throw new Error(`could not resolve ref ${ref} after re-scan`);
  return sel;
}

// Chromium's own sandbox is the last line of defence between a hostile OTA page
// and the user's machine, so we keep it ON by default. It genuinely cannot run
// as root on Linux, and most container images lack the user namespaces it needs
// — those two cases (and only those) drop it, loudly.
function browserArgs() {
  const args = [
    '--disable-dev-shm-usage',
    '--password-store=basic',
    '--use-mock-keychain',
    '--disable-blink-features=AutomationControlled',
  ];
  const isLinuxRoot = process.platform === 'linux'
    && typeof process.getuid === 'function'
    && process.getuid() === 0;
  if (process.env.PRICEWIN_NO_SANDBOX === '1' || isLinuxRoot) {
    process.stderr.write(
      `[daemon] WARNING: launching Chromium with --no-sandbox (${isLinuxRoot ? 'running as root on Linux' : 'PRICEWIN_NO_SANDBOX=1'})\n`,
    );
    args.unshift('--no-sandbox');
  }
  return args;
}

async function ensurePage() {
  if (!browser) {
    // Default headless. Override via PRICEWIN_HEADED=1 for local debugging
    // (helps when Google Hotels triggers bot detection in headless mode).
    const headless = process.env.PRICEWIN_HEADED !== '1';
    browser = await chromium.launch({
      headless,
      args: browserArgs(),
    });
    process.stderr.write(`[daemon] browser launched (headless=${headless})\n`);
  }
  if (!context) {
    context = await browser.newContext({
      locale: 'en-US',
      viewport: { width: 1440, height: 900 },
      userAgent:
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    });
  }
  if (!page || page.isClosed()) {
    const existing = context.pages()[0];
    page = existing || (await context.newPage());
  }
  return page;
}

async function findFreePort() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => resolve(p));
    });
    s.on('error', reject);
  });
}

// --- handlers ---------------------------------------------------------------

async function handle(req) {
  const path = new URL(req.url, 'http://x').pathname.slice(1);
  let body = '';
  for await (const chunk of req) body += chunk;
  const args = body ? JSON.parse(body) : {};

  switch (path) {
    case 'ping':
      return { status: 'ok' };

    case 'goto': {
      const p = await ensurePage();
      // Tight ceilings so every command stays under the 30s shell timeout.
      await p.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 20_000 });
      await p.waitForLoadState('networkidle', { timeout: 3_000 }).catch(() => {});
      return { status: 'loaded', url: p.url(), title: await p.title() };
    }

    case 'snapshot': {
      const p = await ensurePage();
      // We deliberately do NOT scroll here — scrolling closes open
      // autocomplete dropdowns (Agoda's symptom). The agent should call
      // `scroll` explicitly when it needs to surface lazy-loaded content.
      const snap = await Promise.race([
        takeSnapshot(p),
        new Promise((_, reject) => setTimeout(() => reject(new Error('snapshot timed out (page too heavy)')), 22_000)),
      ]);
      lastSnapshotRefs = snap.refs;
      return { text: snap.text, elementCount: Object.keys(snap.refs).length };
    }

    case 'list-pages': {
      // Debug helper: list all tabs in the current context.
      if (!context) return { pages: [] };
      const pages = context.pages();
      const info = [];
      for (const pg of pages) {
        info.push({ url: pg.url(), title: await pg.title().catch(() => '?') });
      }
      return { pages: info, count: pages.length, activeIndex: pages.indexOf(page) };
    }

    case 'switch-to-newest-tab': {
      // After a click that opens target=_blank, switch focus to the new tab.
      if (!context) throw new Error('no context');
      const pages = context.pages();
      if (pages.length < 2) return { status: 'no-other-tab', currentUrl: page?.url() };
      page = pages[pages.length - 1];
      await page.waitForLoadState('domcontentloaded', { timeout: 15_000 }).catch(() => {});
      return { status: 'switched', url: page.url(), title: await page.title() };
    }

    case 'switch-to-tab-matching': {
      // Focus the first tab whose URL matches `urlIncludes`. Useful when
      // a click might open results in a new tab (Agoda) but might also
      // navigate the existing tab (Booking) — the agent just says
      // "find me the /search? tab" and we handle both shapes.
      if (!context) throw new Error('no context');
      const pages = context.pages();
      const needle = String(args.urlIncludes || '');
      const avoid = String(args.urlAvoids || '');
      const match = pages.find((pg) => {
        const u = pg.url();
        if (needle && !u.includes(needle)) return false;
        if (avoid && u.includes(avoid)) return false;
        return true;
      });
      if (!match) return { status: 'no-match', urlIncludes: needle, urlAvoids: avoid, currentUrl: page?.url(), tabCount: pages.length };
      page = match;
      await page.waitForLoadState('domcontentloaded', { timeout: 15_000 }).catch(() => {});
      return { status: 'switched', url: page.url(), title: await page.title() };
    }

    case 'close-tabs-matching': {
      // Close every tab whose URL contains `urlIncludes`. Won't touch the
      // currently active page even if it matches (so we never accidentally
      // close the results tab we just switched to).
      if (!context) throw new Error('no context');
      const pages = context.pages();
      const needle = String(args.urlIncludes || '');
      let closed = 0;
      for (const pg of pages) {
        if (pg === page) continue;
        if (needle && pg.url().includes(needle)) {
          await pg.close().catch(() => {});
          closed += 1;
        }
      }
      return { status: 'closed-tabs', count: closed, remainingTabs: context.pages().length };
    }

    case 'query-all': {
      // Debug + extraction helper: return innerText + attrs for all matches.
      // `limit` defaults to 20 (debug-friendly); callers extracting full
      // result sets (e.g. Google Hotels via aria-label parsing) can pass up
      // to 100. `textLimit` controls per-match text truncation; 0 disables.
      const p = await ensurePage();
      const limit = Math.min(Math.max(Number(args.limit) || 20, 1), 100);
      const textLimit = args.textLimit === 0 ? 0 : (Number(args.textLimit) || 80);
      const out = await p.evaluate(({ sel, lim, tlim }) => {
        const els = Array.from(document.querySelectorAll(sel));
        return els.slice(0, lim).map((el) => {
          const rect = el.getBoundingClientRect();
          const style = getComputedStyle(el);
          const raw = (el.innerText || '').replace(/\s+/g, ' ').trim();
          return {
            tag: el.tagName,
            text: tlim > 0 ? raw.slice(0, tlim) : raw,
            testid: el.getAttribute('data-testid') || el.getAttribute('data-selenium') || null,
            visible: rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden',
            opacity: style.opacity,
            display: style.display,
            ariaLabel: el.getAttribute('aria-label') || null,
            href: el.getAttribute('href') || null,
          };
        });
      }, { sel: args.selector, lim: limit, tlim: textLimit });
      return { selector: args.selector, count: out.length, matches: out };
    }

    case 'keyboard-press': {
      // Page-level key press (no element ref needed). Useful for closing
      // overlays via Escape, navigating with Tab, submitting with Enter.
      const p = await ensurePage();
      await p.keyboard.press(String(args.key || 'Escape'));
      return { status: 'pressed', key: args.key };
    }

    case 'scroll': {
      // Explicit scroll command. Used when the agent wants to surface
      // lazy-loaded content (search results pagination, infinite scroll).
      // Do NOT call before snapshot when a dropdown is open — scrolling
      // closes them.
      const p = await ensurePage();
      const yTo = typeof args.to === 'number' ? args.to : 3000;
      const step = typeof args.step === 'number' ? args.step : 600;
      const delayMs = typeof args.delayMs === 'number' ? args.delayMs : 200;
      await p.evaluate(
        async ({ yTo, step, delayMs }) => {
          for (let y = 0; y <= yTo; y += step) {
            window.scrollTo(0, y);
            await new Promise((r) => setTimeout(r, delayMs));
          }
        },
        { yTo, step, delayMs },
      );
      return { status: 'scrolled', to: yTo };
    }

    case 'click': {
      const p = await ensurePage();
      const sel = await resolveRef(p, args.ref);
      const locator = p.locator(sel).first();
      // Normal click first. If an overlay intercepts pointer events
      // (common on Booking's autocomplete + tooltips), fall back to a
      // direct DOM .click() via evaluate, which bypasses the overlay.
      let mode = 'pointer';
      try {
        await locator.click({ timeout: 4_000 });
      } catch (e) {
        mode = 'dispatch';
        await p.evaluate((s) => {
          const el = document.querySelector(s);
          if (!el) throw new Error('element not found');
          el.click();
        }, sel);
      }
      await p.waitForLoadState('domcontentloaded', { timeout: 5_000 }).catch(() => {});
      return { status: 'clicked', ref: args.ref, mode, url: p.url() };
    }

    case 'fill': {
      // Fast path: set the input value directly. Works for Booking and most
      // sites whose autocomplete listens to the `input` event. Use `type`
      // (below) when a site only fires its autocomplete on real keystrokes.
      const p = await ensurePage();
      const sel = await resolveRef(p, args.ref);
      await p.locator(sel).first().fill(String(args.text ?? ''), { timeout: 10_000 });
      return { status: 'filled', ref: args.ref };
    }

    case 'type': {
      // Slow path: focus + clear + send keystrokes one at a time. Use this
      // for SPAs whose autocomplete only fires on actual keydown events
      // (Agoda is the canonical example). Bypasses overlay-intercepts by
      // calling focus() via JS instead of relying on a pointer click.
      const p = await ensurePage();
      const sel = await resolveRef(p, args.ref);
      await p.evaluate((s) => {
        const el = document.querySelector(s);
        if (!el) throw new Error('element not found');
        el.focus();
        if ('value' in el) el.value = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
      }, sel);
      // Now type via keyboard at page level — works as long as the input
      // is focused, regardless of any overlay.
      await p.keyboard.type(String(args.text ?? ''), { delay: 80 });
      return { status: 'typed', ref: args.ref };
    }

    case 'press': {
      const p = await ensurePage();
      const sel = await resolveRef(p, args.ref);
      await p.locator(sel).first().press(args.key, { timeout: 10_000 });
      return { status: 'pressed', ref: args.ref, key: args.key };
    }

    case 'wait-for': {
      const p = await ensurePage();
      // Wait until at least N elements match the given selector.
      const { selector, minCount = 1, timeoutMs = 15_000 } = args;
      const ok = await p
        .waitForFunction(
          ({ s, n }) => document.querySelectorAll(s).length >= n,
          { s: selector, n: minCount },
          { timeout: timeoutMs },
        )
        .then(() => true)
        .catch(() => false);
      return { status: ok ? 'matched' : 'timeout', selector, minCount };
    }

    case 'try-selectors': {
      const p = await ensurePage();
      const result = await extractWithSelectors(p, args.selectors);
      return {
        healthy: isExtractionHealthy(result),
        sampleCount: result.records.length,
        stats: result.stats,
        sample: result.records.slice(0, 3),
      };
    }

    case 'extract-all': {
      const p = await ensurePage();
      const result = await extractWithSelectors(p, args.selectors);
      return result;
    }

    case 'multi-extract-urls': {
      // Parallel cache-warm extraction. Opens one new tab per OTA inside the
      // SAME main browser context (shared cookies + stealth patches), navigates
      // them concurrently, extracts, then closes each tab.
      //
      // We deliberately stay in the main context instead of creating ephemeral
      // contexts: Booking.com and Agoda use session cookies that are not present
      // in a cold context, causing bot-detection redirects with zero hotel cards.
      if (!context) throw new Error('daemon not launched');
      const requests = Array.isArray(args.requests) ? args.requests : [];
      const results = await Promise.all(
        requests.map(async (req) => {
          // Check in-memory results cache (TTL = 10 min) before opening a tab.
          const cached = getCachedResult(req.site, req.url);
          if (cached) {
            process.stderr.write(`[daemon] results cache hit: ${req.site} (${cached.records.length} records, age ${Math.round((Date.now() - cached.cachedAt) / 1000)}s)\n`);
            return { site: req.site, healthy: true, records: cached.records, stats: cached.stats, fromCache: true };
          }
          const pg = await context.newPage();
          try {
            await pg.goto(req.url, { waitUntil: 'domcontentloaded', timeout: 20_000 });
            // Best-effort wait for the card selector to render — gives lazy
            // SPA pages a chance to paint without blocking the extraction.
            if (req.selectors?.card) {
              await pg.waitForSelector(req.selectors.card, { timeout: 12_000 }).catch(() => {});
            }
            // Scroll progressively to trigger lazy-loaded prices (Agoda, Booking
            // both load prices only when cards scroll into the viewport).
            // 4 scroll steps × 3000px each covers the first ~25-40 hotels.
            for (const y of [3000, 6000, 9000, 12000]) {
              await pg.evaluate((yy) => window.scrollTo(0, yy), y).catch(() => {});
              await pg.waitForTimeout(800).catch(() => {});
            }
            const r = await extractWithSelectors(pg, req.selectors);
            // Populate results cache on successful extraction.
            if (r.records.length > 0) {
              setCachedResult(req.site, req.url, r.records, r.stats);
            }
            return { site: req.site, healthy: isExtractionHealthy(r), records: r.records, stats: r.stats };
          } catch (e) {
            return { site: req.site, error: e.message };
          } finally {
            await pg.close().catch(() => {});
          }
        }),
      );
      return { status: 'multi-extract-done', count: results.length, results };
    }

    case 'current-url': {
      const p = await ensurePage();
      return { url: p.url() };
    }

    case 'inspect-ref': {
      const entry = refToEntry(args.ref);
      const p = await ensurePage();
      let resolved = null;
      try { resolved = await resolveRef(p, args.ref); } catch (e) { resolved = `(failed: ${e.message})`; }
      const match = await p.evaluate((s) => {
        try { return document.querySelectorAll(s).length; } catch { return -1; }
      }, entry.selector || '');
      return { ref: args.ref, savedSelector: entry.selector, signature: entry.signature, resolvedSelector: resolved, savedSelectorMatchCount: match };
    }


    case 'shutdown': {
      // Trigger graceful close after replying
      setImmediate(async () => {
        try { await browser?.close(); } catch {}
        try { await clearState(); } catch {}
        process.exit(0);
      });
      return { status: 'shutting-down' };
    }

    default:
      throw new Error(`unknown endpoint: ${path}`);
  }
}

// --- server boot ------------------------------------------------------------

async function main() {
  await fs.mkdir(CACHE_DIR, { recursive: true });

  // Pre-warm browser so first /goto is fast.
  await ensurePage();

  const port = await findFreePort();
  const server = http.createServer(async (req, res) => {
    // Gate every endpoint, /ping included — an unauthenticated liveness probe
    // is still a way to fingerprint the daemon.
    if (!isLoopbackHost(req)) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'forbidden: non-loopback Host' }));
      return;
    }
    if (!isAuthorized(req)) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: `unauthorized: missing or bad ${AUTH_HEADER}` }));
      return;
    }
    try {
      const result = await handle(req);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(result));
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message || String(e) }));
    }
  });
  server.listen(port, '127.0.0.1', async () => {
    await saveState({ port, pid: process.pid, token: AUTH_TOKEN, createdAt: new Date().toISOString() });
    process.stderr.write(`[daemon] ready on port ${port} (pid ${process.pid})\n`);
  });

  // Auto-shutdown if the cache state file is removed (boss can clean manually).
  // Also handle SIGTERM/SIGINT cleanly.
  const shutdown = async () => {
    try { await browser?.close(); } catch {}
    try { await clearState(); } catch {}
    process.exit(0);
  };
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

main().catch((e) => {
  process.stderr.write(`[daemon] fatal: ${e.stack || e.message}\n`);
  process.exit(1);
});
