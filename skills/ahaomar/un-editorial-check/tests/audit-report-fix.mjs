// Wave W3 audit: the report / PDF / fixer promises that had no lock.
//
//   Item 1 — the PDF must show a real en dash: UE-NU002's defect IS the dash,
//            so `Current` (hyphen) and `Should be` (en dash) must not print
//            identically; WinAnsi encodes en dash at 0x96 and em dash at 0x97.
//            Determinism, the magic, the trailer and the every-page header
//            and footer furniture are re-locked here for the real --report
//            output, not just synthetic elements. Phase 9 adds the JSON-vs-PDF
//            locks: the banner, the six provenance rows, the Occurrences list,
//            the counts paragraph and the thirteen-row legend are all compared
//            against the same run's `--format json` output.
//   Item 1c — the grouped layout: two findings that render identically become
//            one issue — one banner without a location, exactly one count
//            marker (`2 occurrences`), both positions listed, and legend
//            counts that sum to the findings rather than to the issue count.
//   Item 1d — `--report-detail full` is presentation only: both findings keep
//            their located banners, there is no Occurrences list and no count
//            marker, and the counts paragraph is byte-identical to the
//            grouped report's. Confidence rides the banner here, so the five
//            lane rows close each block instead of six kv rows.
//   Item 4 — --fix must not leave a sentence starting in lower case: a
//            replacement that lands at a sentence start is capitalised, a
//            mid-sentence replacement keeps its lower case, and the existing
//            case-preservation is untouched. The fixed file re-scans clean.
//            Terminology left the --fix set, so the lock now runs on the
//            spelling replacement that still reaches the fixer. Brief §8
//            removed the terminology replacement that used to drive these
//            probes; the mechanism under test never depended on which rule
//            supplied the lower-case replacement.
//   Item 4b — UE-TE003 and UE-TE004 pass no replacement: when --fix writes a
//            spelling replacement from the very same line, the percent sign
//            and the country name survive byte for byte and the unfixed
//            terminology error still fails the run.
//   Item 5 — README's "A fix is skipped, never guessed": a finding whose
//            reported offset does not hold the matched copy produces no plan,
//            no write and no exception.
//
// (Items 2 and 3 — the placeholder and the queue excerpt — are locked in
// tests/report-model.mjs, where their model assertions already live.)
//
// TDD: this file was written before the fixes. Standalone run:
//   node tests/audit-report-fix.mjs
// Only node:assert, the modules under test and the in-process CLI are used;
// every fixture lives in a fresh mkdtemp directory under os.tmpdir().

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { run, VERSION } from '../bin/check.mjs';
import { planFixes, writeSafely } from '../lib/fix.mjs';
import { renderPdf } from '../lib/pdf.mjs';
import { severityCounts } from '../lib/output.mjs';
import { CATEGORY_LEGEND, legendRows } from '../lib/legend.mjs';
import { footerCells, headerRows } from '../lib/furniture.mjs';

// --- harness ----------------------------------------------------------------

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-audit-'));
const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.writeFileSync(file, value);
  return file;
};
const config = write('config.json', '{}');

const capture = (argv) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', config];
  const code = run(args, {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};

const scanIds = (file) => {
  const result = capture([file, '--format', 'json']);
  assert.notEqual(result.code, 2, `scan failed for ${file}: ${result.stderr}`);
  return JSON.parse(result.stdout).findings.map(f => f.ruleId).sort();
};

// Text extraction from the uncompressed Tj operands — the same latin1-read
// technique the audit used, mirroring tests/pdf-structural.mjs. Only F1 and F2
// exist since Stage D dropped the italic resource, so an /F3 operand here would
// be a renderer drawing a face no code path asks for.
const LINE_RE = /\/(F[12]) ([0-9.]+) Tf ([0-9.-]+) ([0-9.-]+) Td \(((?:\\[\s\S]|[^\\()])*)\) Tj/g;

// Page geometry, restated from the contract rather than imported from the
// renderer the assertions check.
const MARGIN = 54;
const LABEL_COL = 84;

// Page furniture is drawn outside the content box: the footer cells sit below
// MARGIN and the header cells above the first line the body can draw. Their
// baselines are 780.51 and 768.92 against a body that starts at 742, so 760
// separates them without straddling either. A kv value may wrap across a page
// break, and the next page's header is drawn between the two halves — the
// continuation has to be read past the furniture rather than stopped by it.
// Nothing else is skipped: any other run between two halves ends the value, so
// an unrelated row can never be mistaken for its tail.
const HEADER_CELL_FLOOR = 760;
const isPageFurniture = (l) => l.y < MARGIN || l.y > HEADER_CELL_FLOOR;
// The premise of the rule above, restated so it cannot rot silently if the
// header moves closer to the body: a header cell is furniture, a line inside
// the content box is not.
assert(isPageFurniture({ y: 768.92 }) && isPageFurniture({ y: 30 }),
  'header and footer baselines are recognised as page furniture');
assert(!isPageFurniture({ y: 742.39 }),
  'the first body line is not mistaken for page furniture');

function unpdf(operand) {
  return operand.replace(/\\([()\\])/g, '$1');
}

function extractLinesFrom(body) {
  const out = [];
  for (const m of body.matchAll(LINE_RE)) {
    out.push({
      font: m[1],
      size: Number(m[2]),
      x: Number(m[3]),
      y: Number(m[4]),
      text: unpdf(m[5]),
    });
  }
  return out;
}

// The page content streams, in file order, read by the dictionary's `/Length`
// rather than by sweeping `stream…endstream`: Stage D embeds `/FontFile2` and
// `/ToUnicode` as compressed binary, and a sweep would hand font-program bytes
// to the extractor as drawn copy. A dictionary carrying `/Filter` is skipped —
// no page content stream has one — which is also what keeps the binary out of
// the control-byte and furniture checks below.
// Mirrors tests/pdf-structural.mjs deliberately: both must read the same file
// the same way, or a disagreement between them would be invisible.
function streamBodies(pdf) {
  const text = pdf.toString('latin1');
  const out = [];
  for (const m of text.matchAll(/<<(.*?)>>\nstream\n/gs)) {
    // The match may open at an earlier object's `<<` and run on to the `>>`
    // closing this stream's own dictionary (a page object precedes its content
    // object and neither is a stream), so only the last dictionary in the span
    // belongs to this stream.
    const open = m[1].lastIndexOf('<<');
    const dict = open === -1 ? m[1] : m[1].slice(open + 2);
    if (dict.includes('/Filter')) continue;
    const length = /\/Length (\d+)/.exec(dict);
    assert(length, `a content stream without a /Length: ${JSON.stringify(dict.slice(0, 80))}`);
    out.push(text.slice(m.index + m[0].length, m.index + m[0].length + Number(length[1])));
  }
  return out;
}

/** Every drawn line of the whole document, in stream (page) order. */
function extractLines(pdf) {
  return streamBodies(pdf).flatMap(extractLinesFrom);
}

/** The drawn lines page by page: header first, footer last, on every page. */
function pageLines(pdf) {
  return streamBodies(pdf).map(extractLinesFrom);
}

// Word wrapping collapses runs of whitespace, so a drawn line and the string
// it was drawn from are compared with the runs collapsed on both sides.
const squash = (text) => text.replace(/\s+/g, ' ').trim();

// The kv label sits at x=54 (bold), its value at x=54+84=138 (regular).
function kvValue(lines, label) {
  const i = lines.findIndex(l => l.text === label && l.x === 54 && l.font === 'F2');
  assert(i >= 0, `missing kv label: ${label}`);
  const value = lines[i + 1];
  assert(value && value.x === 138 && value.font === 'F1',
    `missing kv value row after ${label}: ${JSON.stringify(lines[i + 1])}`);
  return value.text;
}

/**
 * The value of one kv row including every wrapped continuation line: a value
 * wider than the value column continues at x=138 on the lines below, and a
 * truncated read would compare only the first fragment.
 */
function kvValueAll(lines, label, from = 0) {
  const i = lines.findIndex((l, j) =>
    j >= from && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
  assert(i >= 0, `missing kv label: ${label}`);
  const parts = [];
  for (let j = i + 1; j < lines.length
    && lines[j].x === MARGIN + LABEL_COL && lines[j].font === 'F1'
    && lines[j].size === 10.5; j++) {
    parts.push(lines[j].text);
  }
  assert(parts.length > 0, `missing kv value row after ${label}`);
  return squash(parts.join(' '));
}

// The legend's four columns, read positionally from the slice between the
// `Categories` heading and the next level-1 heading.
function legendSlice(lines) {
  const start = lines.findIndex(l =>
    l.text === 'Categories' && l.font === 'F2' && l.size === 16 && l.x === MARGIN);
  assert(start >= 0, 'the category legend heading is present');
  const end = lines.findIndex((l, j) =>
    j > start && l.font === 'F2' && l.size === 16 && l.x === MARGIN);
  return lines.slice(start + 1, end === -1 ? lines.length : end);
}

function legendFields(lines) {
  const region = legendSlice(lines);
  // D11 moved both columns: the category's artwork now leads the row at the
  // content margin, so the swatch sits at 65 and the name at 95. Read
  // positionally, so an icon that displaced them would fail here.
  return {
    names: region.filter(l => l.font === 'F2' && l.size === 10.5 && l.x === 95)
      .map(l => l.text),
    codes: region.filter(l => l.font === 'F2' && l.size === 8 && l.x > 65 && l.x < 91)
      .map(l => l.text),
    intents: region.filter(l => l.font === 'F1' && l.size === 9 && l.x === 200)
      .map(l => l.text),
    counts: region.filter(l => l.font === 'F1' && l.size === 9 && l.x > 400
      && /^\d+$/.test(l.text)).map(l => Number(l.text)),
  };
}

/**
 * The JSON-side mirror of the WinAnsi fold, so a value read out of `--format
 * json` can be compared with the bytes the PDF drew: curly quotes fold to
 * ASCII, en/em dash take their WinAnsi bytes, the ellipsis becomes three dots
 * and the soft hyphen disappears.
 */
const winansi = (text) => String(text)
  .replace(/[\u2018\u2019]/g, "'")
  .replace(/[\u201C\u201D]/g, '"')
  .replace(/\u2013/g, '\u0096')
  .replace(/\u2014/g, '\u0097')
  .replace(/\u2026/g, '...')
  .replace(/\u00AD/g, '');

// Severity presentation, restated from the report's own rule: error and
// warning keep their name, everything else reads as a note.
const severityTag = (severity) =>
  ({ error: 'ERROR', warning: 'WARNING', info: 'NOTE' }[severity] || 'NOTE');

/**
 * The banner text for a finding, built from the JSON finding the way
 * lib/report.mjs composes it: severity, rule, category, confidence, and the
 * location only while the group is a single occurrence.
 */
const bannerFor = (f, count) =>
  `[${severityTag(f.severity)}] ${f.ruleId} · ${f.category} · ${f.confidence}`
  + (count === 1 ? ` · line ${f.line}:${f.column}` : '');

/** The counts paragraph as the summary would print it — same helper as the PDF. */
const countsFor = (json) => severityCounts(json.summary, ' · ');

/** Parse the same run's JSON output — the source the PDF must agree with. */
const jsonOf = (file) => {
  const result = capture([file, '--format', 'json']);
  assert.notEqual(result.code, 2, `scan failed for ${file}: ${result.stderr}`);
  return JSON.parse(result.stdout);
};

// All six provenance rows on one issue, in contract order, bounded by the
// issue's own block (its banner to the next banner) so a row missing from
// this issue cannot be satisfied by the next issue's copy of it.
function assertProvenance(lines, bannerText, expected) {
  const start = lines.findIndex(l =>
    l.text === bannerText && l.font === 'F2' && l.size === 11);
  assert(start >= 0, `the issue banner is drawn: ${bannerText}`);
  const next = lines.findIndex((l, j) =>
    j > start && l.font === 'F2' && l.size === 11 && l.text.startsWith('['));
  const end = next === -1 ? lines.length : next;
  let cursor = start;
  for (const [label, value] of expected) {
    const idx = lines.findIndex((l, j) => j > cursor && j < end
      && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
    assert(idx > cursor && idx < end,
      `issue ${bannerText} carries the ${label} row, after the rows before it`);
    const parts = [];
    for (let k = idx + 1; k < lines.length; k++) {
      const l = lines[k];
      if (l.x === MARGIN + LABEL_COL && l.font === 'F1' && l.size === 10.5) {
        parts.push(l.text);
        continue;
      }
      if (isPageFurniture(l)) continue;
      break;
    }
    assert.equal(squash(parts.join(' ')), squash(value),
      `${label} on ${bannerText} prints its value`);
    cursor = idx;
  }
}

/**
 * The header and footer furniture on every page of a real CLI report, plus
 * the endorsement boundary: two header rows of two cells drawn from the
 * cover's own Date and from this report's version, and the three footer cells
 * carrying the page number, the copyright and the repository address
 * (decisions D2 and D3). The scanned target is passed in so the header can be
 * asserted *not* to repeat it: targets are cover material now.
 */
function assertFurniture(s, lines, pages, target) {
  const date = kvValue(lines, 'Date');
  const expectedHeader = headerRows({ date, targets: [target], version: VERSION }, VERSION)
    .map((row) => ({ left: squash(row.left), right: squash(row.right) }));
  const expectedCells = [
    expectedHeader[0].left, expectedHeader[0].right,
    expectedHeader[1].left, expectedHeader[1].right,
  ];
  pages.forEach((ls, i) => {
    assert.deepEqual(ls.slice(0, 4).map((l) => squash(l.text)), expectedCells,
      `page ${i + 1} carries the two header rows, cell by cell`);
    ls.slice(0, 4).forEach((l, j) => {
      const row = j < 2 ? 1 : 2;
      assert.equal(l.font, row === 1 ? 'F2' : 'F1', `header row ${row} font on page ${i + 1}`);
      assert.equal(l.size, row === 1 ? 9 : 8.5, `header row ${row} size on page ${i + 1}`);
      if (j % 2 === 0) {
        assert.equal(l.x, MARGIN, `header row ${row} left cell starts in the margin on page ${i + 1}`);
      } else {
        assert(l.x > MARGIN, `header row ${row} right cell is not sitting on the left margin on page ${i + 1}`);
      }
    });
    assert(ls.slice(0, 4).every((l) => !l.text.includes(target)),
      `page ${i + 1} header does not repeat the scanned target`);
    const cells = footerCells({ date, page: i + 1, pages: pages.length });
    assert.deepEqual(ls.slice(-3).map((l) => l.text),
      [cells.left, cells.centre, cells.right],
      `page ${i + 1} carries its three footer cells verbatim`);
    // The literal n/m stamp, quoted rather than derived from footerCells: if
    // the furniture function itself lost the page numbers, the deepEqual above
    // would follow it there — this one would not.
    assert.equal(ls.slice(-3)[0].text, `Page ${i + 1} of ${pages.length}`,
      `page ${i + 1} footer stamps its own n/m page number`);
    for (const l of ls.slice(-3)) {
      assert.equal(l.font, 'F1', `footer cell is regular: ${l.text}`);
      assert.equal(l.size, 7.5, `footer cell is 7.5 pt: ${l.text}`);
      assert(l.y < MARGIN, `footer sits below the content box: ${l.text} at y=${l.y}`);
    }
  });
  assert(s.includes('EDITORIAL REVIEW'), 'the header text is present in the file');
  assert(!s.includes('UNITED NATIONS'),
    'the endorsement boundary: the report never prints UNITED NATIONS');
}

// --- item 1: the PDF shows a real en dash for UE-NU002 -----------------------

{
  const target = write('nu002.txt', 'Coverage was 1990-2025.\n');
  assert.deepEqual(scanIds(target), ['UE-NU002'], 'the fixture fires exactly UE-NU002');

  const pdfA = path.join(tmp, 'a.pdf');
  const pdfB = path.join(tmp, 'b.pdf');
  const first = capture([target, '--report', pdfA]);
  assert.equal(first.code, 0, `a warning-only file must exit 0: ${first.stderr}`);
  const second = capture([target, '--report', pdfB]);
  assert.equal(second.code, 0, `second run must exit 0: ${second.stderr}`);

  const a = fs.readFileSync(pdfA);
  const b = fs.readFileSync(pdfB);
  assert.equal(Buffer.compare(a, b), 0, 'the same input twice must yield a byte-identical PDF');

  const s = a.toString('latin1');
  assert(s.startsWith('%PDF-1.4\n'), 'the report starts with the PDF 1.4 magic');
  assert(s.endsWith('%%EOF\n'), 'the report ends with the %%EOF trailer');
  // The three footer cells (decision D3). This block took the place of the
  // report-only promise lock, which moved with that line's removal rather than
  // being deleted, so "every report carries its footer" still fails if a
  // renderer stops drawing one.
  assert(/Page \d+ of \d+/.test(s), 'every report stamps its page position');
  assert(s.includes('un-editorial-check contributors'), 'every report carries the copyright');
  assert(s.includes('github.com/ahaomar/un-editorial-check'),
    'every report carries the repository address');

  // Every page object carries its own n/m footer stamp — the guarantee the
  // old regex over `- page (\d+)/(\d+)` held, now checked against the real
  // footer text line by line. The stream-to-page-object tie below is what
  // makes "per page object" mean per page: a page object with no content
  // stream, or a stream with no footer line, fails one of the two locks.
  const pageCount = (s.match(/\/Type \/Page(?!s)/g) || []).length;
  assert(pageCount >= 1, 'at least one page object');
  const lines = extractLines(a);
  const pages = pageLines(a);
  assert.equal(pages.length, pageCount, 'one content stream per page object');
  assertFurniture(s, lines, pages, target);

  // The defect: NU002's Current is a plain hyphen, its Should be an en dash.
  // Both halves must reach the page, and the en dash must be byte 0x96.
  const current = kvValue(lines, 'Current');
  const should = kvValue(lines, 'Should be');
  assert(current.includes('1990-2025'), `Current must print the hyphen range: ${JSON.stringify(current)}`);
  assert(!current.includes('\u0096'), 'Current holds no en dash byte');
  assert(should.includes('1990\u00962025'),
    'Should be must carry the WinAnsi en dash at 0x96: ' + JSON.stringify(should));
  assert(should !== current,
    'Current and Should be must not print identically: ' + JSON.stringify({ current, should }));

  // The framing disclaimer leads the body, directly under the title banner,
  // before any kv row or finding.
  assert(lines[5].text.startsWith('The report never presents itself as verification of facts'),
    'the framing disclaimer still leads the report body');

  // Phase 9, on the real --report output: every string below is read from
  // the same run's JSON, so the PDF and the machine-readable output cannot
  // drift apart without one of the two comparisons failing.
  const json = jsonOf(target);
  assert.deepEqual(json.findings.map(f => f.ruleId), ['UE-NU002'],
    'the fixture fires exactly one finding in JSON too');
  const f = json.findings[0];

  // The banner is composed from the finding: severity, rule, category,
  // confidence — and the location, because this group is a lone finding.
  const banner = bannerFor(f, 1);
  assert.equal(banner, `[WARNING] ${f.ruleId} · ${f.category} · ${f.confidence} · line ${f.line}:${f.column}`,
    'fixture: the lone-finding banner carries its line and column');
  assert(lines.some(l => l.text === banner && l.font === 'F2' && l.size === 11),
    `the issue banner is drawn from the finding: ${banner}`);

  // A count is shown only when it is greater than one: a group of one is not
  // a summary, so no count row is drawn at all.
  assert(!lines.some(l => /^\d+ occurrences?$/.test(l.text)),
    'a group of one shows no count at all');

  // All six provenance rows, in contract order, bounded by this issue's own
  // block: the next issue's copy of a row cannot satisfy a row missing here.
  assertProvenance(lines, banner, [
    ['Lane', f.lane],
    ['Source', f.source],
    ['Profile', f.profile],
    ['Confidence', f.confidence],
    ['Limitation', f.limitation],
    ['Action', f.action],
  ]);

  // The Occurrences list: one heading, then File, Location, Content and
  // Should be in order — every value compared with the JSON finding.
  const occAt = lines.findIndex(l =>
    l.text === 'Occurrences' && l.font === 'F2' && l.size === 13 && l.x === MARGIN);
  assert(occAt > 0, 'the Occurrences heading is drawn');
  const occIndex = {};
  let cursor = occAt;
  for (const label of ['File', 'Location', 'Content', 'Should be']) {
    const idx = lines.findIndex((l, j) => j > cursor
      && l.text === label && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
    assert(idx > cursor, `the occurrence block carries a ${label} row in order`);
    occIndex[label] = idx;
    cursor = idx;
  }
  // D9 moved this lock rather than deleting it, and it now checks the whole
  // decision instead of one half of it. The rule is **restated here** rather
  // than imported from lib/cli.mjs, so this cannot pass by simply agreeing
  // with the code it is meant to check: the scan root is the directory the
  // target sits in, the row is relative to that directory, and resolving one
  // against the other reconstructs exactly the path JSON carries. A report
  // that stated a plausible-but-wrong root would still be internally
  // consistent, so the root itself is compared with the target first.
  assert(!target.includes(' '), 'fixture: the scanned path contains no spaces');
  const expectedRoot = path.dirname(path.resolve(target));
  const root = kvValue(lines, 'Root');
  assert.equal(root, expectedRoot,
    'Summary states the directory the scan was actually pointed at');
  assert(path.isAbsolute(root), 'the scan root is absolute, so a relative path resolves against it');
  const printed = kvValueAll(lines, 'File', occIndex.File).replace(/ /g, '');
  assert.equal(printed, path.relative(root, f.file).split(path.sep).join('/'),
    'the File row prints the scanned path relative to the stated root, wrap aside');
  assert.equal(path.resolve(root, printed), f.file,
    'the printed path resolves against the stated root to exactly the file JSON names');
  assert.equal(kvValueAll(lines, 'Location', occIndex.Location), `${f.line}:${f.column}`,
    'the Location row prints the finding position from JSON');
  assert(kvValueAll(lines, 'Content', occIndex.Content).includes(`\u00BB${f.current}\u00AB`),
    'the Content row marks the matched copy between guillemets');
  assert.equal(kvValueAll(lines, 'Should be', occIndex['Should be']), winansi(f.proposed),
    'the Should be row prints the proposed copy, folded to WinAnsi');

  // The counts paragraph: the JSON summary as printed, and restated straight
  // from the findings so neither side can drift alone. The restatement below is
  // written out longhand on purpose — an independent second implementation of
  // the plural, so the two assertions cannot agree by both calling severityCounts.
  const countRows = lines.filter(l => l.font === 'F1' && l.size === 10.5 && l.x === MARGIN
    && /^\d+ errors? · \d+ warnings? · \d+ notes?$/.test(l.text));
  assert.equal(countRows.length, 1, 'exactly one counts paragraph is drawn');
  assert.equal(countRows[0].text, countsFor(json),
    'the counts paragraph is the JSON summary');
  const errors = json.findings.filter(x => x.severity === 'error').length;
  const warnings = json.findings.filter(x => x.severity === 'warning').length;
  const notes = json.findings.length - errors - warnings;
  assert.equal(countRows[0].text,
    `${errors} error${errors === 1 ? '' : 's'} · ${warnings} warning${warnings === 1 ? '' : 's'}`
    + ` · ${notes} note${notes === 1 ? '' : 's'}`,
    'the counts paragraph is also restated from the findings themselves');

  // The legend: exactly thirteen categories by their text labels, with the
  // counts taken from the findings of this run.
  const legend = legendFields(lines);
  assert.deepEqual(legend.names, CATEGORY_LEGEND.map(e => e.category),
    'the legend lists exactly the thirteen categories by name, in catalogue order');
  assert.deepEqual(legend.codes, CATEGORY_LEGEND.map(e => e.code),
    'each legend row prints its short code');
  assert.equal(legend.counts.length, 13, 'thirteen count cells');
  assert.deepEqual(legend.counts, legendRows(json.findings).map(r => r.count),
    'the legend counts are the findings per category of this run');
}

// --- item 1b: em dash at 0x97, every other fold unchanged --------------------

{
  const pdf = renderPdf([{ type: 'paragraph', text: 'Range 2020—2021, “quoted”, it’s… and Ω stays.' }]);
  const text = extractLines(pdf).map(l => l.text).join('\n');
  assert(text.includes('2020\u00972021'),
    'the em dash keeps its WinAnsi byte 0x97: ' + JSON.stringify(text));
  assert(text.includes('"quoted"'), 'curly double quotes still fold to ASCII');
  assert(text.includes("it's"), 'the curly apostrophe still folds to ASCII');
  assert(text.includes('...'), 'the ellipsis still folds to three dots');
  assert(text.includes('and ? stays.'), 'a character outside WinAnsi still becomes ?');
}

// --- item 1c: Phase 9 — a grouped issue of two, on the real report -----------

{
  const target = write('count2.txt',
    'The range 1990-2025 was set.\nThe range 1990-2025 was noted.\n');
  const json = jsonOf(target);
  assert.deepEqual(json.findings.map(f => f.line), [1, 2],
    'the fixture fires two findings, on lines 1 and 2');

  const pdfPath = path.join(tmp, 'count2.pdf');
  const result = capture([target, '--report', pdfPath]);
  assert.equal(result.code, 0, `a warning-only file must exit 0: ${result.stderr}`);
  const pdf = fs.readFileSync(pdfPath);
  const s = pdf.toString('latin1');
  const lines = extractLines(pdf);

  // Two findings that render identically collapse into one issue: the banner
  // carries the shared fields and no location — the model left it out.
  const banner = bannerFor(json.findings[0], 2);
  assert.equal(banner,
    `[WARNING] ${json.findings[0].ruleId} · ${json.findings[0].category} · ${json.findings[0].confidence}`,
    'fixture: the grouped banner carries no location');
  assert(lines.some(l => l.text === banner && l.font === 'F2' && l.size === 11),
    `the grouped banner is drawn: ${banner}`);
  assert(!lines.some(l => /^\[WARNING\]/.test(l.text) && l.text.includes(' · line ')),
    'a grouped banner never invents a location the model left out');

  // A count is shown only when it is greater than one — here exactly one
  // count marker, for the two-occurrence group.
  const countRows = lines.filter(l => /^\d+ occurrences$/.test(l.text));
  assert.equal(countRows.length, 1, 'exactly one count marker in the document');
  assert.equal(countRows[0].text, '2 occurrences', 'the count is the group size');
  assert.equal(countRows[0].font, 'F1', 'the count sits in the regular weight');
  assert.equal(countRows[0].size, 10.5, 'the count sits at body size');
  assert(countRows[0].x > 400, 'the count is right-aligned in the marker row');
  assert(!lines.some(l => l.text === '1 occurrences' || l.text === '1 occurrence'),
    'no part of the report counts a lone finding');

  // All six provenance rows, in contract order, on the grouped issue.
  const f = json.findings[0];
  assertProvenance(lines, banner, [
    ['Lane', f.lane],
    ['Source', f.source],
    ['Profile', f.profile],
    ['Confidence', f.confidence],
    ['Limitation', f.limitation],
    ['Action', f.action],
  ]);

  // One Occurrences list for the group, one File row per occurrence, and the
  // positions in the order the findings listed them.
  const occHeadings = lines.filter(l => l.text === 'Occurrences'
    && l.font === 'F2' && l.size === 13 && l.x === MARGIN);
  assert.equal(occHeadings.length, 1, 'the group draws one Occurrences heading');
  const fileRows = lines.filter(l => l.text === 'File'
    && l.font === 'F2' && l.size === 10.5 && l.x === MARGIN);
  assert.equal(fileRows.length, 2, 'one File row per occurrence');
  const locations = [];
  const contents = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l.x !== MARGIN || l.font !== 'F2' || l.size !== 10.5) continue;
    if (l.text === 'Location') locations.push(kvValueAll(lines, 'Location', i));
    if (l.text === 'Content') contents.push(kvValueAll(lines, 'Content', i));
  }
  assert.deepEqual(locations, json.findings.map(x => `${x.line}:${x.column}`),
    'every occurrence prints its position, in order');
  assert.equal(contents.length, 2, 'one Content row per occurrence');
  for (const content of contents) {
    assert(content.includes(`\u00BB${f.current}\u00AB`),
      `each Content row marks the matched copy: ${content}`);
  }

  // The counts paragraph: what the JSON summary says, restated from the
  // findings as a second, independent computation.
  const summaryRows = lines.filter(l => l.font === 'F1' && l.size === 10.5 && l.x === MARGIN
    && /^\d+ errors \u00B7 \d+ warnings \u00B7 \d+ notes$/.test(l.text));
  assert.equal(summaryRows.length, 1, 'exactly one counts paragraph is drawn');
  assert.equal(summaryRows[0].text, countsFor(json),
    'the counts paragraph is the JSON summary');
  const errors = json.findings.filter(x => x.severity === 'error').length;
  const warnings = json.findings.filter(x => x.severity === 'warning').length;
  assert.equal(summaryRows[0].text,
    `${errors} errors \u00B7 ${warnings} warnings \u00B7 ${json.findings.length - errors - warnings} notes`,
    'the counts paragraph is also restated from the findings themselves');

  // The legend counts both occurrences — never one per grouped issue.
  const legend = legendFields(lines);
  assert.deepEqual(legend.counts, legendRows(json.findings).map(r => r.count),
    'the legend counts are the findings per category of this run');
  assert.equal(legend.counts.reduce((a, b) => a + b, 0), json.findings.length,
    'the legend rows sum to the findings behind them');
}

// --- item 1d: Phase 9 — --report-detail full is presentation only ------------

{
  const target = write('count2.txt',
    'The range 1990-2025 was set.\nThe range 1990-2025 was noted.\n');
  const json = jsonOf(target);
  const pdfPath = path.join(tmp, 'count2-full.pdf');
  const result = capture([target, '--report', pdfPath, '--report-detail', 'full']);
  assert.equal(result.code, 0, `a warning-only file must exit 0: ${result.stderr}`);
  const pdf = fs.readFileSync(pdfPath);
  const s = pdf.toString('latin1');
  const lines = extractLines(pdf);

  // One block per finding: both findings keep their own banner, and each
  // carries its location because in this layout nothing is grouped.
  for (const finding of json.findings) {
    const banner = bannerFor(finding, 1);
    assert(lines.some(l => l.text === banner && l.font === 'F2' && l.size === 11),
      `full detail draws the located banner: ${banner}`);
  }

  // Grouping is presentation: `full` never groups, so no count marker is ever
  // drawn. The Occurrences assertion moved with D12 — the uncapped row is now
  // the *same* row the capped layout draws, occurrence table included. Before
  // D12 this layout printed no file anywhere inside the block, so a reader of
  // `--report-detail full` could not tell which file a finding came from at
  // all: exactly the divergence D12 (and §10 item 4) exists to close.
  const occurrenceBlocks = lines.filter(l => l.text === 'Occurrences');
  assert.equal(occurrenceBlocks.length, json.findings.length,
    'full detail draws one occurrence block per finding, never a merged one');
  const fileLabels = lines.filter(l => l.text === 'File'
    && l.x === MARGIN && l.font === 'F2' && l.size === 10.5);
  assert.equal(fileLabels.length, json.findings.length,
    'each uncapped row still names the file its finding was read from');
  assert(!lines.some(l => /^\d+ occurrences$/.test(l.text)),
    'full detail shows no count marker');

  // The matched copy still reaches the page.
  assert.equal(kvValue(lines, 'Current'), json.findings[0].current,
    'full detail still prints the matched copy');

  // The counts paragraph is byte-identical to the grouped report's: counts
  // are computed from the findings before either layout runs.
  const countsOf = (ls) => ls.filter(l => l.font === 'F1' && l.size === 10.5 && l.x === MARGIN
    && /^\d+ errors \u00B7 \d+ warnings \u00B7 \d+ notes$/.test(l.text));
  const fullCounts = countsOf(lines);
  assert.equal(fullCounts.length, 1, 'full detail draws one counts paragraph');
  assert.equal(fullCounts[0].text, countsFor(json),
    'the full-detail counts paragraph is the JSON summary');
  const groupedCounts = countsOf(extractLines(fs.readFileSync(path.join(tmp, 'count2.pdf'))));
  assert.equal(groupedCounts.length, 1, 'the grouped report draws one counts paragraph too');
  assert.equal(fullCounts[0].text, groupedCounts[0].text,
    'grouping changes presentation, never the counts');

  // The legend here is parsed from the finding banners the model printed,
  // not from an issue element — the counts must still be the findings'.
  const legend = legendFields(lines);
  assert.deepEqual(legend.names, CATEGORY_LEGEND.map(e => e.category),
    'full detail lists all thirteen categories by name');
  assert.deepEqual(legend.counts, legendRows(json.findings).map(r => r.count),
    'full-detail legend counts are parsed from the findings');

  // The provenance rows in full detail — all six of them, in contract order.
  // This list was five and had no Confidence in it: `full` printed confidence
  // in the banner instead, which is why the row carried one field fewer than
  // the grouped layout did. D12 (§10 item 4) requires every row, in every
  // detail mode, to carry the same six.
  for (const finding of json.findings) {
    assertProvenance(lines, bannerFor(finding, 1), [
      ['Lane', finding.lane],
      ['Source', finding.source],
      ['Profile', finding.profile],
      ['Confidence', finding.confidence],
      ['Limitation', finding.limitation],
      ['Action', finding.action],
    ]);
  }

  // The same furniture and endorsement boundary as the grouped report.
  assertFurniture(s, lines, pageLines(pdf), target);
}

// --- item 4: sentence-start capitalisation in the fixer ----------------------

const applyFix = (name, body) => {
  const file = write(name, body);
  const beforeIds = scanIds(file);
  const result = capture([file, '--fix', '--apply']);
  assert.equal(result.code, 0, `${name}: --fix --apply must succeed: ${result.stderr}`);
  const after = fs.readFileSync(file, 'utf8');
  const afterIds = scanIds(file);
  for (const id of afterIds) {
    assert(beforeIds.includes(id),
      `${name}: the rewrite raised a new finding ${id} (before: ${beforeIds.join(',') || 'none'})`);
  }
  return after;
};

{
  // The reported corruption defect was a lower-case replacement landing at a
  // sentence start. Terminology left the --fix set, so the same mechanism is
  // now locked on UE-SP001's replacement — the case-preservation path that
  // still reaches --fix — at a sentence start, mid-sentence and at a start of
  // line. The probe word is a non-conflict map entry: the
  // organisation/organization family is profile-choice — warning, not
  // fixable by default — after W2a's spelling inversion.
  assert.equal(
    applyFix('cap-sentence.txt', 'The report lands here. color is used for emphasis.\n'),
    'The report lands here. Colour is used for emphasis.\n',
    'a replacement at a sentence start must be capitalised',
  );
  // Mid-sentence stays lower case.
  assert.equal(
    applyFix('cap-mid.txt', 'Gains from color were reported.\n'),
    'Gains from colour were reported.\n',
    'a mid-sentence replacement must keep its lower case',
  );
  // Start of line is a sentence start too.
  assert.equal(
    applyFix('cap-line.txt', 'color is used for emphasis.\n'),
    'Colour is used for emphasis.\n',
    'a replacement at the start of a line must be capitalised',
  );
  // Sentence-initial SP001: case-preservation already produces the capital.
  // The word is a non-conflict map entry: the -ize family would be a profile
  // choice and not fixable without a profile.
  assert.equal(
    applyFix('cap-sp001.txt', 'Color is key.\n'),
    'Colour is key.\n',
    'a sentence-initial Color stays grammatical after the fix',
  );
  // Whole-word upper-case preservation is untouched by the mechanism.
  assert.equal(
    applyFix('cap-upper.txt', 'COLOR is key here.\n'),
    'COLOUR is key here.\n',
    'COLOR still maps to COLOUR',
  );

  // No fixed file may start a sentence in lower case, and the reported
  // corruption must be gone after a re-scan.
  for (const name of ['cap-sentence.txt', 'cap-mid.txt', 'cap-line.txt',
    'cap-sp001.txt', 'cap-upper.txt']) {
    const text = fs.readFileSync(path.join(tmp, name), 'utf8');
    assert(!/\.\s+[a-z]/.test(text), `${name}: lower case survives after a full stop: ${text}`);
  }
  assert.deepEqual(scanIds(path.join(tmp, 'cap-sentence.txt')), [],
    'the fixed sentence carries no finding at all on re-scan');
}

// --- item 4b: terminology never enters the --fix set ------------------------

{
  // UE-TE003 and UE-TE004 pass no replacement (rules/terminology.md), so the
  // sign and the country name are not rewrite candidates even on a line where
  // the fixer does write a spelling replacement. The unfixed terminology
  // error still fails the run, which is the exit-code promise. The word is a
  // non-conflict spelling (W2a: the -ize family is a profile choice and would
  // not be fixable without a profile).
  const file = write('te-no-fix.txt',
    'The US color reported approximately 25% coverage.\n');
  const before = fs.readFileSync(file, 'utf8');
  const result = capture([file, '--fix', '--apply']);
  assert.equal(result.code, 1,
    `an unfixed terminology error must still fail the run: ${result.stderr}`);
  assert.equal(fs.readFileSync(file, 'utf8'),
    'The US colour reported approximately 25% coverage.\n',
    '--fix may write the spelling only: bare US and the sign must survive');
  assert.match(result.stdout, /APPLIED — /,
    'the spelling replacement on the same line must still be applied');
  assert.match(before, /US\b/, 'fixture: the country name is present before the fix');
  assert.match(before, /25%/, 'fixture: the sign is present before the fix');
}

// --- item 5: the offset-mismatch skip path (README:346) ---------------------

{
  const file = write('mismatch.md', 'The organization reports the figure.\n');
  const source = fs.readFileSync(file, 'utf8');
  const sources = new Map([[file, source]]);
  assert.equal(source.indexOf('organization'), 4, 'fixture: the match sits at offset 4');

  const finding = (overrides = {}) => ({
    file,
    line: 1,
    column: 5,
    ruleId: 'UE-SP001',
    category: 'spelling',
    severity: 'error',
    confidence: 'deterministic',
    scope: 'user-visible-copy',
    message: 'American spelling "organization" in prose.',
    suggestion: 'Use "organisation".',
    current: 'organization',
    proposed: 'organisation',
    // A mapped unit: resolveSpan may only fix where the map points.
    _unit: { map: Array.from({ length: source.length }, (_, i) => i), offset: 0, raw: source },
    _index: 0,
    _matched: 'organization',
    _offset: 4,
    _replacement: 'organisation',
    ...overrides,
  });

  // Control: the offset that holds the match is fixable — proof the setup is
  // not trivially skipping every finding.
  const controlPlans = planFixes([finding()], sources);
  assert.equal(controlPlans.length, 1, 'control: an anchored match produces exactly one plan');
  assert.equal(controlPlans[0].after, 'The organisation reports the figure.\n');

  // The promise under test: the offset points at text that does not match the
  // reported copy, so the fix must be skipped — not guessed at the right spot,
  // not invented, and with no exception.
  const stale = finding({ _offset: 0 }); // offset 0 is "The ", not the match
  const snapshot = JSON.parse(JSON.stringify(stale));
  let plans;
  assert.doesNotThrow(() => { plans = planFixes([stale], sources); },
    'a stale offset must not throw');
  assert.deepEqual(plans, [], 'a finding whose offset does not hold the match is skipped');
  assert.deepEqual(JSON.parse(JSON.stringify(stale)), snapshot,
    'the finding is left alone: no field is mutated or stripped');
  assert.equal(fs.readFileSync(file, 'utf8'), source, 'file bytes unchanged');

  // The apply path receives no plan, so the write layer cannot be reached.
  for (const plan of plans) writeSafely(plan.file, plan.before, plan.after);
  assert.equal(fs.readFileSync(file, 'utf8'), source, 'no invented write through writeSafely');

  // Second shape: no offset map at all and the matched copy is absent from the
  // source entirely — the same skip, via the near-neighbour search.
  const absent = finding({
    _unit: { offset: 0, raw: source },
    _matched: 'organizationnation',
    _offset: 4,
  });
  assert.deepEqual(planFixes([absent], sources), [],
    'a matched copy that is absent from the source is skipped, never guessed');
  assert.equal(fs.readFileSync(file, 'utf8'), source, 'still no write for the absent match');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — audit report/fix: PDF en/em dash bytes, determinism, header and '
  + 'three-cell footer furniture on every page, issue banner and six provenance rows '
  + 'from JSON, count only above one, occurrence list, counts paragraph, thirteen-row '
  + 'legend, endorsement boundary, grouped vs full detail, '
  + 'sentence-start capitalisation, terminology never rewritten, offset-mismatch skip');
