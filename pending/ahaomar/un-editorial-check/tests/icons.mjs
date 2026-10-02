// Icon artwork — provenance, vocabulary agreement, and both renderers.
//
// Stage A of the report redesign (.feedbacks/REPORT-REDESIGN-PLAN.md §6): the
// icons are new code that no other suite knows about yet, so this file carries
// the whole contract — that the tables match the tool's own vocabulary, that
// every path is real geometry, and that the HTML and PDF renderers emit
// something bounded, deterministic and free of the glyphs the PDF cannot draw.
//
// A test that only checks "it returns a string" would pass for garbage, so the
// structural checks below are written to fail when the guarantee is removed:
// coordinates are checked against the icon box, draw order is checked against
// the knockout rule, and unsupported path commands are checked to throw.

import assert from 'node:assert/strict';
import { CATEGORY_LEGEND } from '../lib/legend.mjs';
import {
  ICON_BOX,
  CATEGORY_ICONS,
  SEVERITY_ICONS,
  categoryIcon,
  severityIcon,
  pathOps,
  svgIcon,
  pdfIcon,
} from '../lib/icons.mjs';

const categoryNames = CATEGORY_LEGEND.map(entry => entry.category);

// ---------------------------------------------------------------------------
// 1. The tables agree with the tool's own vocabulary
// ---------------------------------------------------------------------------

assert.deepEqual(
  Object.keys(CATEGORY_ICONS),
  categoryNames,
  'every category has exactly one icon, in legend order — a category cannot gain '
  + 'a legend row without artwork or lose artwork without a legend row',
);

assert.deepEqual(
  Object.keys(SEVERITY_ICONS),
  ['error', 'warning', 'info'],
  'the severity keys are the engine\u2019s own values, not display labels: a finding '
  + 'carries info and the report presents it as NOTE',
);

// The legend is the consumer of record: it re-exports the same entries
// with an icon attached (stage A), so a category that has artwork but no legend
// row, or a legend row with no artwork, fails here rather than at draw time.
for (const row of CATEGORY_LEGEND) {
  assert.ok(Array.isArray(row.icon) && row.icon.length > 0,
    `${row.category}: the legend row must carry at least one shape`);
  assert.equal(row.icon, categoryIcon(row.category),
    `${row.category}: the legend must attach the same artwork the module exports`);
}

for (const [name, shapes] of Object.entries(CATEGORY_ICONS)) {
  assert.ok(Array.isArray(shapes) && shapes.length > 0, `${name}: icon has no shapes`);
}
for (const [name, shapes] of Object.entries(SEVERITY_ICONS)) {
  assert.ok(Array.isArray(shapes) && shapes.length > 0, `${name}: icon has no shapes`);
}
for (const shapes of Object.values(CATEGORY_ICONS)) {
  for (const s of shapes) {
    assert.ok(s.paint === 'stroke' || s.paint === 'fill', `${s.d.slice(0, 20)}: unknown paint`);
    const w = s.w ?? 1.5;
    assert.ok(Number.isFinite(w) && w > 0, `${s.d.slice(0, 20)}: stroke width must be positive`);
    assert.ok(s.d.length > 0, `${s.d.slice(0, 20)}: empty path data`);
  }
}

console.log('ok — icon vocabulary: thirteen categories, three severities, every shape painted');

// ---------------------------------------------------------------------------
// 2. Every path is real, finite geometry inside the icon box
// ---------------------------------------------------------------------------

for (const [name, shapes] of [
  ...Object.entries(CATEGORY_ICONS).map(([k, v]) => [`category/${k}`, v]),
  ...Object.entries(SEVERITY_ICONS).map(([k, v]) => [`severity/${k}`, v]),
]) {
  for (const s of shapes) {
    const ops = pathOps(s.d);
    assert.ok(ops.length > 0, `${name}: path produced no operations`);
    assert.equal(ops[0].op, 'M', `${name}: a path must open with a moveto`);

    const count = { M: 0, L: 0, C: 0, Z: 0 };
    for (const op of ops) {
      count[op.op] += 1;
      if (op.op === 'Z') continue; // closepath carries no coordinates
      const endpoints = [[op.x, op.y]];
      const controls = op.op === 'C' ? [[op.x1, op.y1], [op.x2, op.y2]] : [];
      // Endpoints must sit in the 16 x 16 box; control points may overshoot
      // slightly on a curve, so they get a half-box of slack.
      for (const [ux, uy] of endpoints) {
        assert.ok(
          ux >= -0.01 && ux <= ICON_BOX + 0.01 && uy >= -0.01 && uy <= ICON_BOX + 0.01,
          `${name}: endpoint ${ux},${uy} escapes the ${ICON_BOX} unit icon box`,
        );
      }
      for (const [ux, uy] of controls) {
        assert.ok(
          ux >= -ICON_BOX * 0.5 && ux <= ICON_BOX * 1.5
          && uy >= -ICON_BOX * 0.5 && uy <= ICON_BOX * 1.5,
          `${name}: control point ${ux},${uy} is implausibly far outside the box`,
        );
      }
    }
    assert.ok(count.M >= 1, `${name}: a path must open with a moveto`);
    assert.notEqual(ops[ops.length - 1].op, 'M',
      `${name}: a path ending in a bare moveto draws nothing`);
    assert.ok(count.Z <= count.M, `${name}: a closepath has nothing to close`);
    assert.ok(count.L + count.C > 0, `${name}: a path that only moves draws nothing`);
  }
}

console.log('ok — icon geometry: parses, opens with a moveto, stays inside the box');

// ---------------------------------------------------------------------------
// 3. The parser refuses what it does not understand
// ---------------------------------------------------------------------------

assert.throws(() => pathOps('M0 0 Q 4 4 8 8'), /unsupported command/,
  'a quadratic curve must be rejected, not silently dropped — artwork outside '
  + 'the supported set would render as a missing shape');
assert.throws(() => pathOps('0 0'), /begins with a number/,
  'path data without a command letter is not a path');
assert.throws(() => pathOps('M0 0 L 1'), /ran out of numbers/,
  'a truncated command must fail rather than draw half a line');
assert.throws(() => pathOps('M0 0 Z 5 5'), /must follow closepath/,
  'implicit commands after a closepath are not read as geometry');

// Smooth cubic: the second control point reflects the previous curve's.
const smooth = pathOps('M0 0 C0 10 10 10 10 0 S20 -10 20 0');
const reflected = smooth[smooth.length - 1];
assert.deepEqual(
  { x1: reflected.x1, y1: reflected.y1 },
  { x1: 10, y1: -10 },
  'a smooth cubic with a curve before it reflects the previous control point',
);
const smoothFirst = pathOps('M0 0 S20 -10 20 0');
assert.deepEqual(
  { x1: smoothFirst[1].x1, y1: smoothFirst[1].y1 },
  { x1: 0, y1: 0 },
  'a smooth cubic with nothing to reflect starts at the current point',
);

// Shorthand resolves to the same geometry as its long form. Values are chosen
// to be exact in binary so the comparison is exact too; `pdfIcon` rounds at
// emit time, so float noise in a sum like 2.4 + 4.4 never reaches the bytes.
assert.deepEqual(pathOps('M2 4h4'), pathOps('M2 4L6 4'), 'horizontal shorthand');
assert.deepEqual(pathOps('M2 4v4'), pathOps('M2 4L2 8'), 'vertical shorthand');
assert.deepEqual(pathOps('M0 0 5 5'), pathOps('M0 0L5 5'), 'coordinate pairs after a moveto are linetos');

console.log('ok — icon path parser: refuses the unknown, resolves shorthand, reflects smooth curves');

// ---------------------------------------------------------------------------
// 4. Knockout marks are drawn after the shape they sit on
// ---------------------------------------------------------------------------

for (const [name, shapes] of Object.entries(SEVERITY_ICONS)) {
  const firstFill = shapes.findIndex(s => s.paint === 'fill');
  shapes.forEach((s, i) => {
    if (s.colour !== 'white') return;
    assert.ok(
      firstFill >= 0 && i > firstFill,
      `${name}: a white knockout must be drawn after a filled shape, or it is hidden`,
    );
  });
}
for (const shapes of Object.values(CATEGORY_ICONS)) {
  assert.equal(
    shapes.some(s => s.colour === 'white'),
    false,
    'category icons are monochrome — they sit in a row of coloured text',
  );
}

// Reordering must change the output, or nothing above is actually checking order.
const note = SEVERITY_ICONS.info;
assert.notEqual(pdfIcon(note, { x: 0, y: 0, size: 16 }), pdfIcon([...note].reverse(), { x: 0, y: 0, size: 16 }),
  'drawing order must survive into the PDF');
assert.notEqual(svgIcon(note), svgIcon([...note].reverse()),
  'drawing order must survive into the HTML');

console.log('ok — icon draw order: knockouts sit on their shape, and order reaches both renderers');

// ---------------------------------------------------------------------------
// 5. Inline SVG for the HTML report
// ---------------------------------------------------------------------------

const SVG_OPERATORS = new Set(['path', 'title']);
const isAscii = s => /^[\x20-\x7E\n]*$/.test(s);

for (const [name, shapes] of [
  ...Object.entries(CATEGORY_ICONS).map(([k, v]) => [`category/${k}`, v]),
  ...Object.entries(SEVERITY_ICONS).map(([k, v]) => [`severity/${k}`, v]),
]) {
  const out = svgIcon(shapes, { size: 12, className: 'icon' });
  assert.ok(out.startsWith('<svg '), `${name}: output must open with <svg`);
  assert.ok(out.endsWith('</svg>'), `${name}: output must close`);
  assert.ok(out.includes('viewBox="0 0 16 16"'), `${name}: the 16 unit viewBox must be declared`);
  assert.ok(out.includes('class="icon"'), `${name}: the class must reach the element`);
  assert.ok(out.includes('width="12" height="12"'), `${name}: a requested size must be applied`);
  assert.ok(out.includes('aria-hidden="true"'), `${name}: a decorated icon is hidden from screen readers`);
  assert.ok(!/\bNaN\b|\bundefined\b/.test(out), `${name}: no broken coordinate`);
  assert.ok(isAscii(out), `${name}: the markup must stay ASCII`);

  const inner = out.replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '');
  for (const el of inner.matchAll(/<([a-z]+)/g)) {
    assert.ok(SVG_OPERATORS.has(el[1]), `${name}: unexpected <${el[1]}> — the icon is shapes only`);
  }
  const text = inner.replace(/<[^>]*>/g, '');
  assert.equal(text, '', `${name}: an icon carries no text`);

  for (const s of shapes) {
    assert.ok(!s.d.includes('"'), `${name}: path data would break out of an attribute`);
  }
  assert.equal(svgIcon(shapes, { size: 12, className: 'icon' }), out,
    `${name}: rendering is deterministic`);
}

const labelled = svgIcon(SEVERITY_ICONS.error, { label: 'Error' });
assert.ok(labelled.includes('role="img"') && labelled.includes('<title>Error</title>'),
  'a caller that wants the icon announced can ask for it by label');
assert.ok(!labelled.includes('aria-hidden'),
  'a labelled icon must not also be hidden from assistive technology');

const colourSplit = svgIcon(SEVERITY_ICONS.error);
assert.ok(colourSplit.includes('fill="currentColor"') && colourSplit.includes('stroke="#ffffff"'),
  'the filled tier and its white knockout keep distinct paints in HTML');

// The artwork omits `w` whenever it equals the default, so the default has to
// be applied by the renderer rather than read straight off the shape.
assert.ok(svgIcon(CATEGORY_ICONS.spelling).includes('stroke-width="1.5"'),
  'a shape with no explicit width must render at the artwork default, not "undefined"');
assert.ok(!svgIcon(CATEGORY_ICONS.spelling).includes('undefined'),
  'no shape may write an unset field into the markup');

console.log('ok — inline SVG: shapes only, ASCII only, deterministic, hidden unless labelled');

// ---------------------------------------------------------------------------
// 6. PDF path operators for the report PDF
// ---------------------------------------------------------------------------

const PDF_TOKENS = new Set(['q', 'Q', 'm', 'l', 'c', 'h', 'f', 'S', 'w', 'J', 'j', 'rg', 'RG']);
const noGlyphs = (s, what) => {
  assert.ok(isAscii(s), `${what}: the PDF is WinAnsi — a glyph here would render as a question mark`);
  assert.ok(!/[\u25A0-\u27BF\u{1F300}-\u{1FAFF}]/u.test(s), `${what}: no icon font, no emoji, drawn paths only`);
};

for (const [name, shapes] of [
  ...Object.entries(CATEGORY_ICONS).map(([k, v]) => [`category/${k}`, v]),
  ...Object.entries(SEVERITY_ICONS).map(([k, v]) => [`severity/${k}`, v]),
]) {
  const x = 100; const y = 200; const size = 16;
  const out = pdfIcon(shapes, { x, y, size, colour: [0.1, 0.2, 0.3] });
  const lines = out.split('\n');

  assert.equal(lines[0], 'q', `${name}: the icon must not leak graphics state onto the page`);
  assert.equal(lines[lines.length - 1], 'Q', `${name}: q and Q must balance`);
  noGlyphs(out, name);
  assert.ok(!/\bNaN\b|\bundefined\b|\bInfinity\b/.test(out), `${name}: no broken coordinate`);

  let started = false;
  let fills = 0; let strokes = 0;
  for (const line of lines) {
    const parts = line.split(/\s+/);
    const op = parts[parts.length - 1];
    assert.ok(PDF_TOKENS.has(op), `${name}: ${JSON.stringify(line)} ends in an operator PDF understands`);

    const values = parts.slice(0, -1).map(Number);
    for (const v of values) assert.ok(Number.isFinite(v), `${name}: ${line} holds a non-finite number`);

    if (op === 'm') { started = true; }
    if (op === 'l' || op === 'c') assert.ok(started, `${name}: ${line} continues a path that never started`);
    if (op === 'h' || op === 'S' || op === 'f') assert.ok(started, `${name}: ${line} paints an empty path`);
    if (op === 'S') { started = false; strokes += 1; }
    if (op === 'f') { started = false; fills += 1; }

    // Every endpoint must land inside the placed icon box.
    if (op === 'm' || op === 'l') {
      const [px, py] = values;
      assert.ok(px >= x - 0.01 && px <= x + size + 0.01, `${name}: x ${px} leaves the box`);
      assert.ok(py >= y - 0.01 && py <= y + size + 0.01, `${name}: y ${py} leaves the box`);
    }
    if (op === 'c') {
      const [px, py] = values.slice(4);
      assert.ok(px >= x - 0.01 && px <= x + size + 0.01, `${name}: curve end x ${px} leaves the box`);
      assert.ok(py >= y - 0.01 && py <= y + size + 0.01, `${name}: curve end y ${py} leaves the box`);
    }
    if (op === 'w') assert.ok(values[0] > 0 && values[0] <= 4, `${name}: stroke width ${values[0]} is implausible`);
  }

  assert.equal(
    fills,
    shapes.filter(s => s.paint === 'fill').length,
    `${name}: every filled shape must be filled`,
  );
  assert.equal(
    strokes,
    shapes.filter(s => s.paint === 'stroke').length,
    `${name}: every stroked shape must be stroked`,
  );

  const expectedPaths = shapes.reduce((n, s) => n + pathOps(s.d).filter(o => o.op === 'M').length, 0);
  assert.equal(
    lines.filter(l => l.endsWith(' m')).length,
    expectedPaths,
    `${name}: one moveto per subpath in the source artwork`,
  );

  assert.equal(pdfIcon(shapes, { x, y, size, colour: [0.1, 0.2, 0.3] }), out,
    `${name}: rendering is deterministic — identical input must give identical bytes`);
}

// Scale and placement: a 32 unit icon at (50, 60) must not draw outside the
// box it claims to occupy. Only x values are collected — the y coordinates run
// upwards from a different origin and would not belong in this range.
const scaled = pdfIcon(CATEGORY_ICONS.security, { x: 50, y: 60, size: 32 }).split('\n');
const xs = scaled.flatMap((l) => {
  if (l.endsWith(' m') || l.endsWith(' l')) return [Number(l.split(/\s+/)[0])];
  if (l.endsWith(' c')) return [Number(l.split(/\s+/)[4])];
  return [];
}).filter(Number.isFinite);
assert.ok(xs.length > 0, 'the placed icon must emit at least one coordinate');
assert.ok(Math.min(...xs) >= 49.99 && Math.max(...xs) <= 82.01,
  `a 32 unit icon placed at x=50 must stay within 50..82, got ${Math.min(...xs)}..${Math.max(...xs)}`);

// And the whole box is usable: an icon drawn at the origin spans 0..16.
const atOrigin = pdfIcon(CATEGORY_ICONS.security, { x: 0, y: 0, size: 16 }).split('\n');
const originXs = atOrigin.flatMap((l) => {
  if (l.endsWith(' m') || l.endsWith(' l')) return [Number(l.split(/\s+/)[0])];
  if (l.endsWith(' c')) return [Number(l.split(/\s+/)[4])];
  return [];
}).filter(Number.isFinite);
assert.ok(Math.min(...originXs) >= -0.01 && Math.max(...originXs) <= 16.01,
  `at size 16 the artwork must sit inside 0..16, got ${Math.min(...originXs)}..${Math.max(...originXs)}`);

const monochrome = pdfIcon(CATEGORY_ICONS.security, { x: 0, y: 0, size: 16 });
assert.ok(!monochrome.includes('1 1 1 RG') && !monochrome.includes('1 1 1 rg'),
  'category icons take the caller\u2019s colour, never the white knockout');

const tinted = pdfIcon(CATEGORY_ICONS.security, { x: 0, y: 0, size: 16, colour: [0, 0, 1] });
assert.ok(tinted.includes('0 0 1 RG'), 'the caller\u2019s colour reaches the PDF');

assert.ok(pdfIcon(SEVERITY_ICONS.error, { x: 0, y: 0, size: 16 }).includes('1 1 1 RG'),
  'the error tier\u2019s white knockout is drawn as white');

assert.throws(() => pdfIcon(CATEGORY_ICONS.security, { x: 0, y: 0, size: 0 }), /bad placement/,
  'a zero-sized icon draws nothing and must be refused');
assert.throws(() => pdfIcon(CATEGORY_ICONS.security, { x: Number.NaN, y: 0, size: 16 }), /bad placement/,
  'a NaN placement must be refused rather than written into the content stream');

console.log('ok — PDF path operators: q/Q balanced, box-bounded, deterministic, glyph-free');

console.log(`ok — icons: ${Object.keys(CATEGORY_ICONS).length} categories, `
  + `${Object.keys(SEVERITY_ICONS).length} severities, two renderers`);
