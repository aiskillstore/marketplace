#!/usr/bin/env node
/**
 * Fail if this skill's documentation disagrees with the live BlackForge catalog.
 *
 * WHY THIS EXISTS
 * ---------------
 * The sold-column count has now drifted THREE separate times across this product — the Stripe
 * products said 69/117, the landing site said 38/72/119, and this skill said 119 — every time
 * because the number was typed by hand into prose and nothing could tell it had gone stale.
 * Worse, `references/metrics-glossary.md` claims to document every catalog metric and had
 * silently lost `baseAsset` when migration 007 added it: a reader could not tell, because a
 * glossary missing one row looks exactly like a glossary that is complete.
 *
 * Prose cannot be generated — the measurement wording is written by hand and that is the point
 * of the file. So it is CHECKED instead. This script is the artefact that makes the drift
 * visible, and it fails loudly rather than skipping.
 *
 *   node scripts/check-catalog-sync.mjs
 *
 * It reads the PUBLIC catalog (no key, no auth, no sibling checkout), so it works anywhere with
 * a network connection and cannot quietly pass by finding nothing to compare against. If the
 * catalog cannot be reached it EXITS NON-ZERO rather than reporting success — an unreachable
 * source is an unknown answer, not a passing one.
 *
 * WHAT IT CANNOT CHECK, AND WHY
 * -----------------------------
 * Which columns are QUERYABLE. Five of them — quoteAsset, baseAsset, enrichmentTs, bookSynced,
 * missingTrades — 400 the entire `/v1/latest` request if named in `columns=`, and the catalog
 * does not say so: it exposes `plottable`, which is a different idea (bookObservedAt is
 * queryable but not plottable). That set lives only in `api/src/metrics/metrics.service.ts`
 * (NON_QUERYABLE_KEYS), so no client can discover it without reading the API's source or
 * hitting the 400. The glossary's "Non-queryable" flags were reconciled against that file by
 * hand on 2026-07-28 and will silently rot if it changes. Exposing `queryable` on the catalog
 * would let this script check them like everything else.
 */

const CATALOG_URL = process.env.BF_CATALOG_URL ?? 'https://api.blackforge.so/v1/catalog';

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(resolve(root, rel), 'utf8');

/** `ultra` shares `max`'s set — nothing gates above `max`. */
const LADDER = ['free', 'pro', 'max'];

const problems = [];
const fail = (file, msg) => problems.push(`${file}: ${msg}`);

// ---------------------------------------------------------------------------
// 0. The live truth.
// ---------------------------------------------------------------------------
let metrics;
try {
  const res = await fetch(CATALOG_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  ({ metrics } = await res.json());
  if (!Array.isArray(metrics) || metrics.length === 0) throw new Error('no metrics in the response');
} catch (error) {
  console.error(`catalog-sync: could not read ${CATALOG_URL} — ${error.message}`);
  console.error('Refusing to report success against a source that could not be read.');
  process.exit(1);
}

const TOTAL = metrics.length;
const columnsFor = (plan) => {
  const ceiling = LADDER.indexOf(plan);
  return metrics.filter((m) => LADDER.indexOf(m.minPlan ?? 'free') <= ceiling).length;
};
const LADDER_COUNTS = { free: columnsFor('free'), pro: columnsFor('pro'), max: TOTAL, ultra: TOTAL };

const liveFamilies = new Map();
for (const m of metrics) liveFamilies.set(m.family, (liveFamilies.get(m.family) ?? 0) + 1);

// The two internal columns are catalogued but never served, so they are absent from this
// public response. They both live in `quality`, which is why quality's physical count is two
// higher than its sold count and no other family's is.
const INTERNAL = ['bookAgeTime', 'seedDepth'];
const PHYSICAL = TOTAL + INTERNAL.length;

// ---------------------------------------------------------------------------
// 1. The glossary table must cover exactly the catalog — in BOTH directions.
// ---------------------------------------------------------------------------
const glossaryFile = 'references/metrics-glossary.md';
const glossary = read(glossaryFile);

const rows = [];
for (const line of glossary.split('\n')) {
  const m = line.match(/^\|\s*`([A-Za-z0-9_]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|/);
  if (m) rows.push({ key: m[1], label: m[2].trim(), unit: m[3].trim(), minPlan: m[4].trim() });
}

const documented = new Map(rows.map((r) => [r.key, r]));
const live = new Map(metrics.map((m) => [m.key, m]));

for (const key of [...documented.keys()].filter((k, i, a) => a.indexOf(k) !== i)) {
  fail(glossaryFile, `\`${key}\` is documented more than once`);
}
for (const m of metrics) {
  if (!documented.has(m.key)) {
    fail(glossaryFile, `MISSING \`${m.key}\` (${m.family}/${m.unit}/${m.minPlan}) — the catalog serves it and this file claims to list every metric`);
  }
}
for (const r of rows) {
  if (!live.has(r.key) && !INTERNAL.includes(r.key)) {
    fail(glossaryFile, `documents \`${r.key}\`, which the catalog does not serve`);
  }
}

// A trailing parenthetical is editorial ("count (bitmask)"), so compare the leading token only.
const bare = (s) => s.replace(/\s*\(.*\)\s*$/, '').trim();
for (const r of rows) {
  const c = live.get(r.key);
  if (!c) continue;
  if (bare(r.unit) !== c.unit) fail(glossaryFile, `\`${r.key}\` unit is "${r.unit}", live says "${c.unit}"`);
  if (r.minPlan !== (c.minPlan ?? 'free')) fail(glossaryFile, `\`${r.key}\` min plan is "${r.minPlan}", live says "${c.minPlan}"`);
}

// ---------------------------------------------------------------------------
// 2. The "Families at a glance" paragraph must match the live grouping.
// ---------------------------------------------------------------------------
for (const [family, count] of liveFamilies) {
  const isQuality = family === 'quality';
  // quality is written as "quality (N physical, **M sold** ...)" because the two internal
  // columns sit in it; every other family is written as "family (N ...)".
  const re = isQuality
    ? new RegExp(`${family}\\s*\\((\\d+)\\s+physical[^)]*?\\*\\*(\\d+)\\s+sold\\*\\*`, 'i')
    : new RegExp(`\\b${family}\\s*\\((\\d+)`, 'i');
  const m = glossary.match(re);
  if (!m) {
    fail(glossaryFile, `"Families at a glance" does not state a count for \`${family}\` in the expected form`);
    continue;
  }
  if (isQuality) {
    if (Number(m[1]) !== count + INTERNAL.length) fail(glossaryFile, `quality physical count is ${m[1]}, should be ${count + INTERNAL.length}`);
    if (Number(m[2]) !== count) fail(glossaryFile, `quality sold count is ${m[2]}, should be ${count}`);
  } else if (Number(m[1]) !== count) {
    fail(glossaryFile, `family \`${family}\` is written as ${m[1]}, live has ${count}`);
  }
}

// ---------------------------------------------------------------------------
// 3. Each family section's subtitle states that family's own count. Check it against
//    that family, not against a global allowlist — otherwise "10 physical columns"
//    under quality would sail through simply because tradeFlow happens to have 10.
// ---------------------------------------------------------------------------
const SUBTITLE_RE = /^_family key: `([A-Za-z]+)`[^\n]*$/gm;
const seenSubtitles = new Set();
for (const m of glossary.matchAll(SUBTITLE_RE)) {
  const [subtitle, family] = m;
  const line = glossary.slice(0, m.index).split('\n').length;
  seenSubtitles.add(line);
  const count = liveFamilies.get(family);
  if (count === undefined) {
    fail(`${glossaryFile}:${line}`, `section claims family \`${family}\`, which the catalog does not have`);
    continue;
  }
  if (family === 'quality') {
    const q = subtitle.match(/(\d+)\s+physical columns,\s*\*\*(\d+)\s+sold\*\*/);
    if (!q) fail(`${glossaryFile}:${line}`, 'quality subtitle no longer states "N physical columns, **M sold**"');
    else {
      if (Number(q[1]) !== count + INTERNAL.length) fail(`${glossaryFile}:${line}`, `quality subtitle says ${q[1]} physical, should be ${count + INTERNAL.length}`);
      if (Number(q[2]) !== count) fail(`${glossaryFile}:${line}`, `quality subtitle says ${q[2]} sold, should be ${count}`);
    }
    continue;
  }
  const n = subtitle.match(/·\s*(\d+)\s+metrics/);
  if (!n) fail(`${glossaryFile}:${line}`, `\`${family}\` subtitle no longer states "· N metrics"`);
  else if (Number(n[1]) !== count) fail(`${glossaryFile}:${line}`, `\`${family}\` subtitle says ${n[1]} metrics, live has ${count}`);
}

// ---------------------------------------------------------------------------
// 4. No prose anywhere may state a metric/column count that is not one of the real ones.
// ---------------------------------------------------------------------------
// Only counts that QUALIFY metrics/columns are checked, and the per-family subtitles above are
// skipped because step 3 already checked them against their own family. A units note reading
// "3%-wide slices" never matches, which is what keeps this specific enough to be worth having.
const PROSE_FILES = ['SKILL.md', 'README.md', 'references/setup.md', 'references/metrics-glossary.md'];
const COUNT_RE = /\b(\d+)\s+(?:catalog\s+|measurement\s+|metric\s+|physical\s+|sold\s+)?(?:metrics|columns|metric definitions)\b/g;
const ALLOWED = new Set([...Object.values(LADDER_COUNTS), PHYSICAL]);

for (const file of PROSE_FILES) {
  const text = read(file);
  for (const m of text.matchAll(COUNT_RE)) {
    const n = Number(m[1]);
    if (ALLOWED.has(n)) continue;
    const line = text.slice(0, m.index).split('\n').length;
    if (file === glossaryFile && seenSubtitles.has(line)) continue;
    fail(`${file}:${line}`, `"${m[0].replace(/\s+/g, ' ')}" — not a real count. Live: ${TOTAL} sold, ${PHYSICAL} physical, ladder ${LADDER_COUNTS.free}/${LADDER_COUNTS.pro}/${LADDER_COUNTS.max}`);
  }
}

// ---------------------------------------------------------------------------
if (problems.length > 0) {
  console.error(`catalog-sync: ${problems.length} problem(s) — the skill's docs disagree with ${CATALOG_URL}\n`);
  for (const p of problems) console.error(`  ${p}`);
  console.error('\nFix the docs (this file is the source of truth about what is wrong, the catalog is the source of truth about what is right).');
  process.exit(1);
}

console.log(
  `catalog-sync: docs match the live catalog — ${TOTAL} sold metrics ` +
    `(${PHYSICAL} physical), ladder ${LADDER_COUNTS.free} / ${LADDER_COUNTS.pro} / ${LADDER_COUNTS.max}, ` +
    `${documented.size} glossary rows, ${liveFamilies.size} families.`,
);
