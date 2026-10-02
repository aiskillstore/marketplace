// Colour palette contract — `lib/palette.mjs` as the single source of truth.
//
// Stages C and E of the Phase 10 colour refactor (.feedbacks/PHASE-10-PLAN.md
// §6.9): C hoisted every colour lib/html.mjs paints out of the stylesheet and
// into the palette, byte-identical; E moved the values. Two renderers painting
// the same document must not decide independently what "warning" or "footer
// grey" looks like, so this file locks four things:
//
//   * the palette's own html values, pinned here so a change to palette.mjs
//     has to change a test deliberately — that is the "stability" half of the
//     contract; a value may only move in a sanctioned stage, never as a side
//     effect;
//   * the renderer paints exactly those roles and no others: the set of hexes
//     in the rendered stylesheet is compared both ways against the palette,
//     so a palette role that stops reaching CSS fails, and so does a colour
//     appearing in CSS that no role accounts for;
//   * no #rrggbb literal survives in lib/html.mjs, and the three PDF-chrome
//     roles never appear there at all — the structural half, without which the
//     checks above would be reading the wrong file;
//   * divergences() — now empty, because Stage E closed all five of the ones
//     recorded at Stage C. Pinned as empty so the next one has to be added
//     here, deliberately, rather than arriving quietly.
//
// No test framework, matching tests/ttf.mjs and tests/icons.mjs: assertions
// throw, each group prints one `ok —` line, exit code 0 means green.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { PALETTE, SEVERITY, divergences, pdfHex } from '../lib/palette.mjs';
import { renderHtml } from '../lib/html.mjs';

const ROOT = path.resolve(fileURLToPath(new URL('..', import.meta.url)));

/** The whole palette flattened to `role -> html hex`, severity nested out. */
function flatten() {
  const flat = {};
  for (const [role, entry] of Object.entries(PALETTE)) {
    if (role === 'severity') {
      for (const [name, value] of Object.entries(entry)) flat[`severity.${name}`] = value.html;
    } else {
      flat[role] = entry.html;
    }
  }
  return flat;
}

// --- 1: the palette values, pinned -------------------------------------------

// The roles the HTML stylesheet paints. Every value here is Omar's Stage E
// palette: body #171b26, the meta and footer ink darkened to #616161 (R10 and
// the same reasoning for the footer band), headings #1F3A7A, structure
// #C5CEDF, and one light fill #EEF1F8 across the page ground, the panels, the
// findings, the empty lanes, the table head and the callout.
//
// Duplicates are still two roles on purpose, not aliases: surface/onChip are
// both #ffffff, and the four structural roles are all #C5CEDF because Omar's
// palette names one value for borders — collapsing them into a single role
// would re-create the coupling the refactor exists to remove. The old Stage C
// pairs (page/codeType, body/codeGround, marker/footer) *decoupled* in Stage E:
// they were equal because both sides happened to be near-neutral, and recolour
// independently from here.
const PAINTED = {
  body: '#171b26',
  meta: '#616161',
  secondary: '#4a4a4a',
  footer: '#616161',
  heading: '#1f3a7a',
  rule: '#c5cedf',
  border: '#c5cedf',
  findingBorder: '#c5cedf',
  emptyBorder: '#c5cedf',
  page: '#eef1f8',
  surface: '#ffffff',
  panel: '#eef1f8',
  finding: '#eef1f8',
  empty: '#eef1f8',
  tableHead: '#eef1f8',
  callout: '#eef1f8',
  calloutBorder: '#b9a05a',
  clean: '#e8f2e8',
  cleanBorder: '#7fa87f',
  marker: '#5c5850',
  onChip: '#ffffff',
  codeGround: '#1c1c1c',
  codeType: '#f4f4f2',
  icon: '#1d1b18',
  // R7: the filled masthead and the rule that closes it. These were UNPAINTED
  // at Stage C, when byte-identity meant the HTML report could not grow a
  // band; Stage E is the sanctioned place the band crosses over, so it moves
  // from the unpainted list below to this one rather than appearing from
  // nowhere — which is exactly the edit the Stage C comment promised would
  // have to be deliberate.
  masthead: '#24356b',
  divider: '#1b2852',
  'severity.error': '#c62828',
  'severity.warning': '#e07b00',
  'severity.note': '#1565c0',
};

// The one role the HTML renderer still does not paint: the PDF's footer band
// (R8). Recorded so the role set below is exact. Note it is *not* asserted
// absent from the stylesheet by colour — Stage E gave the HTML light fill and
// the PDF footer band the same value, because both are Omar's #EEF1F8, so its
// presence proves nothing about a band. Section 3 checks that structurally.
const UNPAINTED = {
  footerBand: '#eef1f8',
};

const flat = flatten();
assert.deepEqual(
  Object.keys(flat).sort(),
  [...Object.keys(PAINTED), ...Object.keys(UNPAINTED)].sort(),
  'the palette gained or lost a role: update the Stage E mapping deliberately',
);
for (const [role, hex] of Object.entries({ ...PAINTED, ...UNPAINTED })) {
  assert.equal(flat[role], hex, `${role}: the palette html value moved (${flat[role]} → ${hex})`);
}
for (const [role, hex] of Object.entries({ ...PAINTED, ...UNPAINTED })) {
  assert.match(hex, /^#[0-9a-f]{6}$/, `${role}: an html colour is a lowercase #rrggbb string`);
}
assert.equal(SEVERITY, PALETTE.severity, 'SEVERITY is PALETTE.severity, not a second copy');
for (const [name, entry] of Object.entries(SEVERITY)) {
  assert.match(entry.pdf, /^\d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)?$/,
    `severity.${name}: the pdf field stays a device-RGB decimal string`);
}
// pdfHex is how the two halves are compared at all; its rounding is what
// makes divergences() below a comparison of rendered colours rather than of
// strings.
assert.equal(pdfHex('0.45 0.45 0.45'), '#737373', 'pdfHex rounds components like a PDF consumer');
assert.equal(pdfHex(null), null, 'pdfHex refuses anything that is not three numbers');
console.log(`ok — palette: ${Object.keys(PAINTED).length} painted roles and `
  + `${Object.keys(UNPAINTED).length} PDF-chrome roles pinned at their html values`);

// --- 2: the stylesheet paints exactly those roles, and only those -------------

// The report model the renderer is pure over, with one finding so the document
// carries a card and a lane as well as the style block. Every colour lives in
// the static STYLE, which is embedded whole whatever the scan found — but the
// render is a real one, so what is asserted is what a reader receives.
const report = renderHtml({
  version: '1.5.0',
  date: '2026-10-02',
  targets: ['docs'],
  profiles: [],
  filesCount: 1,
  findings: [{
    file: 'docs/page.md',
    line: 12,
    column: 5,
    ruleId: 'UE-GR002',
    category: 'grammar',
    severity: 'warning',
    confidence: 'deterministic',
    scope: 'user-visible-copy',
    message: 'The full stop runs into the next word.',
    suggestion: null,
    current: null,
    proposed: null,
    _replacement: null,
  }],
  sources: [],
}, { version: '1.5.0' });

const style = /<style>([^]*)<\/style>/.exec(report);
assert(style, 'the report carries its one inline style block');
const stylesheet = style[1];

// Both directions of the mapping. Every painted role's colour is in the
// stylesheet, and every colour in the stylesheet belongs to a painted role —
// so a role that stops reaching CSS fails, and so does a literal (or a new
// role the mapping has not heard of) appearing in CSS. The marker chips in
// the body carry category colours from lib/legend.mjs, not palette roles;
// they are outside the <style> block and outside this comparison.
const paintedHexes = [...new Set(Object.values(PAINTED))].sort();
const stylesheetHexes = [...new Set(stylesheet.match(/#[0-9a-f]{6}/g) || [])].sort();
assert.deepEqual(stylesheetHexes, paintedHexes,
  'the stylesheet must paint exactly the palette\'s painted roles — every one, and nothing else');
for (const [role, hex] of Object.entries(PAINTED)) {
  assert(stylesheet.includes(hex), `the stylesheet never paints ${role} (${hex})`);
}

// UNPAINTED must not appear as a colour assertion here: the stylesheet and the
// PDF footer band share #EEF1F8 by design (both are Omar's light fill), so its
// presence would prove nothing either way. The masthead and the divider are no
// longer in that list at all — Stage E brought them across, and they are
// asserted present above like any other painted role. What remains is checked
// structurally in section 3, which is the check colour cannot make.

// The four declarations the paired assertions above cannot carry alone: each
// surface and its counterpart are named in their own CSS rule, so a shared
// hex passes only if both roles really do reach their own declaration.
for (const rule of [
  `background: ${PAINTED.page};`,       // body — the page ground
  `color: ${PAINTED.body};`,            // body — the type on it
  `background: ${PAINTED.codeGround};`, // .cap pre — the inverted ground
  `color: ${PAINTED.codeType};`,        // .cap code — the type on it
  `background: ${PAINTED.surface};`,    // main — the sheet
  `color: ${PAINTED.onChip};`,          // .marker — the code on the chip
  `background: ${PAINTED.marker};`,     // .marker — the chip itself
  `color: ${PAINTED.footer};`,          // footer — the closing ink
]) {
  assert(stylesheet.includes(rule), `the stylesheet is missing the rule "${rule.trim()}"`);
}
console.log(`ok — renderer: stylesheet paints exactly ${paintedHexes.length} palette colours `
  + 'in both directions, shared hexes one rule each');

// --- 3: no hex literal, and no chrome role, survives in lib/html.mjs ----------

const source = fs.readFileSync(path.join(ROOT, 'lib', 'html.mjs'), 'utf8');
assert.match(source, /import \{ PALETTE \} from '\.\/palette\.mjs';/,
  'lib/html.mjs reads its colours from lib/palette.mjs');
// Not even in a comment: a literal in a comment is one merge away from being
// pasted back into STYLE, and the whole point of the hoist is that the only
// place a colour value lives is palette.mjs. Comments in this file do happen
// to mention hexes today only inside lib/palette.mjs — html.mjs must not.
assert.doesNotMatch(source, /#[0-9a-fA-F]{6}/,
  'lib/html.mjs carries a #rrggbb literal: every colour belongs in lib/palette.mjs');
// The structural half of the check above, and the one that holds for
// footerBand: the HTML renderer never reaches for it, so the value it shares
// with the light fill cannot be painted as a band by accident — there is no
// code path that would paint it. Checked as a *palette reference*, not as the
// bare word: lib/html.mjs says "masthead" in a comment about why the header
// must never read as UNITED NATIONS, and prose is not a paint operation.
const chromeRoleRef = /PALETTE\.footerBand\b/;
assert(!chromeRoleRef.test(source),
  'lib/html.mjs reads PALETTE.footerBand: the footer band is PDF chrome, and the '
  + 'HTML footer sits on the page light fill instead');
console.log('ok — source: no #rrggbb literal survives, and no PDF-chrome role is referenced');

// --- 4: divergences() — empty, because Stage E closed them ---------------------

// Run and recorded on 2 Oct 2026. Stage C found five — body, meta, footer,
// heading and rule — where the PDF and the HTML painted different colours for
// the same role (a sixth, severity.warning, had been closed earlier by R12).
// Stage E moved every html field onto the value the pdf field already held, so
// the set is empty: the two renderers now paint the same report the same
// colour.
//
// Pinned as `[]` rather than dropped, which is the whole point: an assertion
// that nothing diverges is what forces the next divergence to be added here
// deliberately, with a stated reason, instead of arriving the way these five
// did — unnoticed, because no test compared the two renderers.
assert.deepEqual(divergences(), [],
  'divergences() is no longer empty: two renderers disagree about a role, which '
  + 'Phase 10 §6.9 exists to prevent. Either close it or record it here on purpose.');
// These two must never reappear as divergences: the severities where the
// renderers already agreed before Stage C, and the ones R12 aligned.
for (const name of ['error', 'warning', 'note']) {
  assert(!divergences().some(([role]) => role === `severity.${name}`),
    `severity.${name} diverges: severity is a signal a reader must recognise across formats`);
}
console.log('ok — divergences: empty — Phase 10 §6.9 closed, and pinned so it stays closed');

console.log('ok — palette: stage C hoist and stage E recolour green');
