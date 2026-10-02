// un-editorial-check — HTML report contract suite (Phase 7, Agent 2).
//
// The contract under test, from the Phase 7 plan row for the HTML report:
// `--report review.html` writes a lane-aware HTML report parallel to the PDF —
// five lanes, quoted material counted separately, the audits section, every
// finding carrying source / profile / confidence / limitation / recommended
// human action, the framing disclaimer, and the exact clean-run sentence
// "No findings under the enabled, documented local rules." on a clean run.
// Deterministic output (same input, identical bytes), zero dependencies, no
// external assets or network, one self-contained file. The `--report` help text
// names both formats and an unsupported extension fails closed with exit 2.
//
// Two layers are exercised, deliberately:
//   * renderHtml() directly, for the parts of the model a live scan cannot
//     produce (quoted context, a hand-built finding with no captured copy),
//   * the real CLI, for everything about dispatch: extension routing, exit
//     codes, what actually lands on disk.
//
// Fixtures are copied out of the repository before use: the scanner never
// reads files inside its own skill root unless --self-scan is given. Every
// rendered report collected here is swept at the end for the banned phrases
// ("UN approved", "fully compliant", "finds all errors", "factual
// verification", "legal advice").

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';
import { renderHtml } from '../lib/html.mjs';
import { buildReport } from '../lib/report.mjs';
import { CATEGORY_LEGEND, legendRows } from '../lib/legend.mjs';
import { categoryIcon, severityIcon, svgIcon } from '../lib/icons.mjs';
import { footerCells, headerRows, TITLE } from '../lib/furniture.mjs';
import { LANE_NAMES } from '../lib/output.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-html-'));

fs.cpSync(path.join(root, 'tests', 'fixtures'), path.join(tmp, 'fixtures'), { recursive: true });
const fixture = (...parts) => path.join(tmp, 'fixtures', ...parts);

const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
// An explicit config keeps the suite independent of any .un-editorial.json in
// the working directory.
const config = write('config.json', '{}');

const capture = (argv, configPath = config) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', configPath];
  const code = run(args, {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const json = result => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);
const sha = text => createHash('sha256').update(text, 'utf8').digest('hex');

// --- model fixtures ---------------------------------------------------------

const MANUAL_SUFFIX = ' — manual / agent rewrite; not --fix-able';
const FIXABLE_SUFFIX = ' — --fix-able';
const CLEAN = 'No findings under the enabled, documented local rules.';

// The six fields every finding must carry, in the order the card renders them.
const SIX_FIELDS = ['Lane', 'Source', 'Profile', 'Confidence', 'Limitation', 'Action'];

// Long enough that nothing in a findings section can plausibly be truncating
// it — the old review queue's excerpt limit is gone with the queue itself.
const LONG_MESSAGE =
  'Each finding explains why the wording was flagged and what a reviewer should consider before any change is made in the source document.';
assert(LONG_MESSAGE.length > 80, 'fixture message long enough to prove nothing shortens it');

function finding(overrides = {}) {
  return {
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
    ...overrides,
  };
}

function makeInput(overrides = {}) {
  return {
    version: '1.1.0',
    date: '2026-09-28',
    targets: ['docs'],
    profiles: [],
    filesCount: 4,
    findings: [finding()],
    sources: [],
    ...overrides,
  };
}

const render = (input, opts = { version: '1.1.0' }) => renderHtml(input, opts);

// One finding per lane, plus a quoted finding. Hand-built because a live scan
// masks quoted spans before the rules run, and because it lets every lane be
// present in a single document without waiting for five separate corpora.
// The lane follows lib/output.mjs laneOf(): category beats confidence, so the
// heuristic finding carries a non-safety, non-diplomacy category.
const ALL_LANES = [
  finding({ file: 'a.txt', line: 1, column: 1, ruleId: 'UE-SP001', category: 'spelling', severity: 'error' }),
  finding({ file: 'b.txt', line: 3, column: 1, ruleId: 'UE-GR002', category: 'grammar',
    severity: 'error', confidence: 'heuristic', message: LONG_MESSAGE }),
  finding({ file: 'c.txt', line: 4, column: 1, ruleId: 'UE-DM001', category: 'discriminatory', severity: 'error' }),
  finding({ file: 'd.txt', line: 5, column: 1, ruleId: 'UE-DP001', category: 'diplomacy', severity: 'warning' }),
  finding({ file: 'e.html', line: 6, column: 1, ruleId: 'UE-EO001', category: 'publishing',
    severity: 'warning', audit: 'publishing' }),
  finding({ file: 'f.md', line: 7, column: 1, ruleId: 'UE-TE003', category: 'terminology',
    severity: 'warning', context: 'quoted' }),
];
const allLanes = render(makeInput({ findings: ALL_LANES, profiles: ['publishing'] }));

// --- 1: the document is well formed and self-contained -----------------------

assert(allLanes.startsWith('<!DOCTYPE html>\n<html lang="en">\n'), 'the file opens as an HTML document');
assert(allLanes.endsWith('</html>') && !allLanes.endsWith('\n'), 'the file closes the document and adds nothing after it');
assert.equal((allLanes.match(/<html\b/g) || []).length, 1, 'exactly one html element');
assert.equal((allLanes.match(/<body\b/g) || []).length, 1, 'exactly one body element');
assert.equal((allLanes.match(/<\/body>/g) || []).length, 1, 'the body is closed');
assert.match(allLanes, /<meta charset="utf-8">/, 'the encoding is declared, so copy is not re-decoded');

// Self-contained: no network, no external assets, no script. This is the whole
// point of the file being a single artefact a reviewer can forward.
assert(!/<script\b/i.test(allLanes), 'no script element may be emitted');
assert(!/\son\w+\s*=/i.test(allLanes), 'no inline event-handler attribute may be emitted');
assert(!/<(iframe|object|embed|link|img)\b/i.test(allLanes), 'no element that fetches an external resource');
assert(!/@import/i.test(allLanes), 'the style block may not import another stylesheet');
assert(!/url\(/i.test(allLanes), 'the style block may not reference an external url()');
assert(!/<link\b/i.test(allLanes), 'no external stylesheet link');
assert.equal((allLanes.match(/<style>/g) || []).length, 1, 'exactly one inline style block');
assert(!/\bhttps?:\/\/(?!www\.un\.org|www\.ohchr\.org|www\.un\.org)/i.test(allLanes.replace(/<li>[^]*?<\/li>/g, '')),
  'outside the sources appendix no http(s) URL may appear: nothing may be fetched or linked');

// D11 put the report's own artwork inline, so <svg> had to come off the ban
// above without dropping what that entry was standing for: the file reaches
// for nothing. The blanket ban cannot say that about <svg> any more, so the
// guarantee is restated here, on the element itself — an icon may declare
// shapes and nothing else, may not point at a resource by any route an SVG
// offers (an href, a url() paint server, a raster, another document), and
// must stay out of the accessibility tree unless the caller asked for it to
// be read. Every lock below fails on the markup that would fetch.
const iconSvgs = [...allLanes.matchAll(/<svg\b[^>]*>([\s\S]*?)<\/svg>/g)].map((m) => m[0]);
assert(iconSvgs.length > 0, 'the report draws its marks rather than reaching for an icon font');
for (const icon of iconSvgs) {
  assert(!/<image\b/i.test(icon), 'an icon may not embed a raster, which is one to fetch');
  assert(!/<use\b/i.test(icon), 'an icon may not compose from a resource by reference');
  assert(!/<foreignObject\b/i.test(icon), 'an icon may not carry foreign markup to load');
  assert(!/\bhref\s*=/i.test(icon), 'an icon may not name an address outside the file');
  assert(!/\burl\s*\(/i.test(icon), 'an icon may not paint from a url() paint server');
  assert(/aria-hidden="true"/.test(icon),
    'an icon is hidden from assistive technology unless the caller labelled it');
}

// --- 2: all five lanes render, with quoted material reported separately ------

for (const lane of LANE_NAMES) {
  assert(allLanes.includes(`id="lane-${lane}"`),
    `the ${lane} lane must have its own section`);
}
// D5/D6: the section headers carry their title, their lane metadata and
// their finding count as three separate spans, so no number is ever part of a
// section's name, and every section is drawn — including Editorial Warnings,
// which this fixture leaves empty, because a lane with nothing in it still
// says it was checked (D10).
const head = (title, meta, count) =>
  `<h2><span class="sec-t">${title}</span><span class="sec-d">${meta}</span>`
  + `<span class="sec-c">${count}</span></h2>`;
const HEADS = [
  ['Harmful / Discriminatory Content', 'harmful-discriminatory', '1 finding'],
  ['Diplomatic Sensitivity', 'diplomacy', '1 finding'],
  ['Editorial Errors', 'deterministic · error only', '1 finding'],
  ['Editorial Warnings', 'deterministic · warning only', '0 findings'],
  ['Agent Review Required', 'heuristic-review', '1 finding'],
  ['Audit Findings', 'audit', '1 finding'],
];
let cursor = -1;
for (const [title, meta, count] of HEADS) {
  const text = head(title, meta, count);
  const at = allLanes.indexOf(text);
  assert(at > cursor, `the ${title} section renders, in D5 order`);
  cursor = at;
}
assert(allLanes.includes('<p class="empty">No findings under this lane in this scan. The lane was checked.</p>'),
  'an empty lane states that it was checked rather than being omitted (D10)');
assert.match(allLanes, /<span class="sec-t">Summary<\/span><span class="sec-c">6 findings<\/span><\/h2>/,
  'Summary opens the report and states the finding count');
assert.match(allLanes, /<span class="sec-t">Categories<\/span><span class="sec-d">thirteen checked categories<\/span>/,
  'the legend hangs from the Categories section');
assert.match(allLanes,
  /<span class="sec-t">Quoted material<\/span><span class="sec-d">context, not a lane<\/span><span class="sec-c">1 finding<\/span>/,
  'quoted material has its own section and its own count');
assert.match(allLanes, /<span class="sec-t">Priority Recommendations<\/span>/,
  'the report closes its findings with priority recommendations');
assert(allLanes.includes('<ol>'), 'the recommendations render as an ordered list');
assert(!/class="sec-t">\s*\d/.test(allLanes), 'no section title begins with a number (D6)');

// Every non-quoted finding is inside a lane section; the quoted one is not.
{
  const quotedAt = allLanes.indexOf('id="quoted-material"');
  const laneStart = allLanes.indexOf('id="lane-deterministic"');
  assert(laneStart < quotedAt, 'lane sections precede the quoted section');
  for (const [rule, beforeQuote] of [['UE-SP001', true], ['UE-GR002', true], ['UE-DM001', true],
    ['UE-DP001', true], ['UE-EO001', true], ['UE-TE003', false]]) {
    const at = allLanes.indexOf(`] ${rule} ·`);
    assert(at > 0, `${rule} must be rendered`);
    assert.equal(at < quotedAt, beforeQuote, `${rule}: quoted findings leave the lane sections`);
  }
}

// Quoted material is counted on its own, never inside a lane count.
assert.match(allLanes,
  /lanes: deterministic 1 · heuristic-review 1 · harmful-discriminatory 1 · diplomacy 1 · audit 1 · quoted 1/,
  'the lane counts name all five lanes plus quoted');
assert.equal((allLanes.match(/<article class="finding/g) || []).length, 6,
  'every finding, quoted included, renders as its own block (one issue per group in the default detail)');

// --- 3: six fields on every finding -----------------------------------------

// Parse the cards and check the field tail of each: the six rows must be
// present, in order, non-empty, and must close the card.
const CARD_RE = /<article class="finding[^"]*"[^>]*>[\s\S]*?<\/article>/g;
const cards = [...allLanes.matchAll(CARD_RE)].map(m => m[0]);
assert.equal(cards.length, 6, 'six cards to inspect');

// The card-shape contract, applied to every layout the renderer can draw.
// The default detail renders grouped issue blocks here and `detail: 'full'`
// renders one card per finding (asserted further down), and both must close
// with the six lane fields in order — so a provenance field dropped from
// either mode fails the suite, whichever layout the reader asks for.
const assertCardShape = (list, label) => {
  for (const [index, card] of list.entries()) {
    const rows = [...card.matchAll(/<dt>([^<]*)<\/dt><dd>([^<]*)<\/dd>/g)].map(m => [m[1], m[2]]);
    const tail = rows.slice(-SIX_FIELDS.length);
    assert.deepEqual(tail.map(([name]) => name), SIX_FIELDS,
      `${label} ${index + 1} must close with the six lane fields, in order: ${rows.map(([l]) => l).join(', ')}`);
    for (const [field, value] of tail) {
      assert(value.length > 0, `${label} ${index + 1} ${field} must not be empty`);
      assert(value !== 'undefined', `${label} ${index + 1} ${field} must never render the string "undefined"`);
    }
    // Nothing may follow the six rows inside the card: the Action row is the
    // last field row, and the card closes straight after it.
    const actionRow = `<dt>${SIX_FIELDS[5]}</dt>`;
    const actionAt = card.indexOf(actionRow);
    assert(actionAt > 0, `${label} ${index + 1} must render its Action row`);
    assert(!/<dt>/.test(card.slice(actionAt + actionRow.length)),
      `${label} ${index + 1} may carry no field row after Action`);
  }
};
assertCardShape(cards, 'grouped issue card');

// --- 3b: every row is marked, and only rows are (D11) -----------------------

// The marks D11 draws are not decoration sprinkled where it was convenient:
// the severity artwork leads every row and appears nowhere else, the category
// artwork follows it in every row and in every legend row, so the legend
// teaches a mark the rows actually use. Both counts are read out of the
// document, so a row that quietly lost its mark, or a mark drawn outside a
// row, fails here rather than reaching a reader as a blank.
const severityMarks = (allLanes.match(/class="icon sev"/g) || []).length;
const categoryMarks = (allLanes.match(/class="icon cat"/g) || []).length;
assert.equal(severityMarks, cards.length,
  'every row carries a severity mark, and a severity mark appears only in rows');
assert.equal(categoryMarks, cards.length + 13,
  'every row and every one of the thirteen legend rows carries its category mark, and nothing else does');
for (const [index, card] of cards.entries()) {
  assert(/<svg[^>]*class="icon sev"/.test(card),
    `row ${index + 1} opens with its severity mark`);
  assert(card.indexOf('class="icon sev"') < card.indexOf('class="icon cat"'),
    `row ${index + 1} puts the severity mark before the category mark — D12's row order`);
  assert(card.indexOf('class="icon cat"') < card.indexOf('class="marker"'),
    `row ${index + 1} puts the category mark beside the code it names`);

  // And it is *that row's* mark. A renderer that drew one icon for every row
  // would satisfy every count above — same number of marks, same places — so
  // the expected artwork is rebuilt here from the icon table using what the
  // row itself says it is: its own severity class and its own category, read
  // off the headline rather than handed in by the renderer.
  const kind = /class="finding issue severity-(\w+)"/.exec(card)[1];
  assert(card.includes(svgIcon(severityIcon(kind), { size: 13, className: 'icon sev' })),
    `row ${index + 1} wears the ${kind} severity mark its own severity asks for`);
  const category = /\] \S+ · (\S+) ·/.exec(card)[1];
  const shapes = categoryIcon(category);
  assert(card.includes(svgIcon(shapes, { size: 13, className: 'icon cat' })),
    `row ${index + 1} wears the ${category} category mark it names, not a neighbour's`);
}
// The legend's mark must be the same artwork the rows use. It is keyed by
// category name, so a legend row that borrowed a neighbour's icon would be
// saying which category it is, and the rows would then disagree with it.
const legendRowsHtml = [...allLanes.matchAll(/<tr><td><svg[\s\S]*?<\/tr>/g)].map((m) => m[0]);
assert.equal(legendRowsHtml.length, 13, 'thirteen legend rows, each led by a mark (twelve catalogue categories plus organisation)');
for (const [index, row] of legendRowsHtml.entries()) {
  const category = /<\/td><td>([^<]*)<\/td>/.exec(row)[1];
  assert(category, `legend row ${index + 1} names its category`);
  assert(row.includes(svgIcon(categoryIcon(category), { size: 13, className: 'icon cat' })),
    `legend row ${index + 1} wears the ${category} mark it names, not a neighbour's`);
}

// The lane row names the lane the section is in, and the source row names the
// rule file, for every lane — the metadata is real, not a placeholder.
const cardFields = (ruleId) => {
  const card = cards.find(part => part.includes(`] ${ruleId} ·`));
  assert(card, `no card for ${ruleId}`);
  return Object.fromEntries([...card.matchAll(/<dt>([^<]*)<\/dt><dd>([^<]*)<\/dd>/g)].map(m => [m[1], m[2]]));
};
assert.equal(cardFields('UE-SP001').Lane, 'deterministic');
assert.equal(cardFields('UE-GR002').Lane, 'heuristic-review');
assert.equal(cardFields('UE-DM001').Lane, 'harmful-discriminatory');
assert.equal(cardFields('UE-DP001').Lane, 'diplomacy');
assert.equal(cardFields('UE-EO001').Lane, 'audit');
assert.equal(cardFields('UE-SP001').Source, 'rules/spelling.md', 'the source names the rule file');
assert.equal(cardFields('UE-EO001').Source, 'config/profiles/publishing.json', 'an audit cites its profile file');
assert.equal(cardFields('UE-EO001').Profile, 'publishing', 'an audit names itself as the profile');
assert.equal(cardFields('UE-GR002').Confidence, 'heuristic', 'confidence is rendered, not implied');
assert.match(cardFields('UE-GR002').Limitation, /\S/, 'a heuristic finding states its limitation');
assert.match(cardFields('UE-DP001').Action, /diplomatic review/i,
  'the recommended action routes the reader to diplomatic review');
// A hand-built finding with no metadata still gets every row: annotate() supplies
// the lane defaults, so a row can never be dropped as undefined.
{
  const bare = render(makeInput({ findings: [finding({ lane: undefined, source: undefined,
    profile: undefined, limitation: undefined, action: undefined })] }));
  const rows = [...bare.matchAll(/<dt>(Lane|Source|Profile|Limitation|Action)<\/dt><dd>([^<]*)<\/dd>/g)]
    .map(m => [m[1], m[2]]);
  assert.deepEqual(rows.map(([label]) => label), ['Lane', 'Source', 'Profile', 'Limitation', 'Action']);
  for (const [label, value] of rows) {
    assert(value.length > 0 && value !== 'undefined', `the default ${label} must render a real value`);
  }
}

// --- 4: current-to-should-be parity with the PDF block -----------------------

{
  const card = cards.find(part => part.includes('] UE-SP001 ·'));
  assert.match(card, /<dt>Current<\/dt><dd>organization<\/dd>|Current<\/dt><dd>\(not applicable\)<\/dd>/,
    'the Current row is present');
  assert(card.includes(MANUAL_SUFFIX) || card.includes(FIXABLE_SUFFIX),
    'the Should be row carries the same fixability marker the PDF prints');
}
{
  // A finding with no captured copy must not show a developer placeholder in a
  // director-facing report (the rule lib/report.mjs states).
  const auditCard = cards.find(part => part.includes('] UE-EO001 ·'));
  assert.match(auditCard, /<dt>Current<\/dt><dd>\(not applicable\)<\/dd>/, 'the audit card states no context');
  assert(!auditCard.includes('whole line context'), 'no developer placeholder may reach the report');
  assert.match(auditCard, /<dt>Audit<\/dt><dd>publishing<\/dd>/, 'an audit card names its audit');
}
{
  const detCard = cards.find(part => part.includes('] UE-SP001 ·'));
  assert(!/<dt>Audit<\/dt>/.test(detCard), 'an editorial card carries no audit row');
  assert.match(cards.find(part => part.includes('] UE-GR002 ·')),
    /Heuristic finding — routed to review\./, 'a heuristic card states that it is routed to review');
  assert(!/Heuristic finding — routed to review\./.test(detCard),
    'a deterministic card must not claim to be routed to review');
}
{
  // D5 gives the old review queue's job to the Agent Review Required section,
  // which prints whole issue blocks instead of an excerpt: every heuristic
  // finding of that lane is listed, and none of them is shortened. Quoted
  // material and the other lanes stay out — lane choice is by category and
  // audit first, so a heuristic finding elsewhere is reported there.
  const sliceLane = (html, lane) => {
    const at = html.indexOf(`id="lane-${lane}"`);
    assert(at > 0, `the ${lane} section is drawn`);
    return html.slice(at, html.indexOf('</section>', at));
  };
  const agent = sliceLane(allLanes, 'heuristic-review');
  assert.match(agent, /<span class="sec-c">1 finding<\/span>/,
    'the agent review section counts its own findings');
  assert(agent.includes(LONG_MESSAGE),
    'the section carries the whole explanation, where the old queue cut it at 80 characters');
  assert(!agent.includes(`${LONG_MESSAGE.slice(0, 80)}...`),
    'nothing in a findings section is ever an excerpt');
  // The full message still reaches the reader in the finding card itself.
  assert(allLanes.includes(LONG_MESSAGE), 'the finding card carries the untruncated explanation');

  // A scan with nothing in the lane still draws the section, stating zero and
  // saying it was checked: a reader can tell a clean lane from one that was
  // never run (D10).
  const noAgent = render(makeInput({ findings: [finding({ confidence: 'deterministic' })] }));
  assert.match(noAgent,
    /<span class="sec-t">Agent Review Required<\/span><span class="sec-d">heuristic-review<\/span><span class="sec-c">0 findings<\/span>/,
    'a lane with nothing in it still renders its header with a zero count');
  assert(noAgent.includes('The lane was checked.'), 'and it says the lane was checked');

  // A quoted heuristic is a quotation, not work for an agent to take on: it
  // keeps its own section and never counts towards this one.
  const quotedHeuristic = render(makeInput({ findings: [finding({ confidence: 'heuristic',
    context: 'quoted', message: LONG_MESSAGE })] }));
  assert.match(sliceLane(quotedHeuristic, 'heuristic-review'), /<span class="sec-c">0 findings<\/span>/,
    'a quoted heuristic stays out of the Agent Review Required section');
  assert(!sliceLane(quotedHeuristic, 'heuristic-review').includes(LONG_MESSAGE),
    'and its message never leaks into that section');
}

// --- 5: framing, legend and the clean-run sentence --------------------------

{
  // Sanctioned wording, reused from the shipped surfaces.
  assert.match(allLanes,
    /Deterministic finding: the wording proves the defect\./,
    'the deterministic promise from lib/report.mjs is present');
  assert.match(allLanes,
    /Heuristic finding: routed to review; this report never asserts that a claim is true or false, or that any legal threshold is met\./,
    'the heuristic promise from lib/report.mjs is present verbatim');
  assert.match(allLanes, /This report changes nothing; re-run the checker to verify corrections\./,
    'the report-only promise from lib/report.mjs is present');
  // The footer's own promise ("report only; findings are not changed by this
  // report.") was retired with the footer itself under decision D3. The footer
  // now carries the page position, the copyright and the repository address,
  // and that is locked cell by cell in 5d below; the sentence a reader can act
  // on is the one three lines up and still leads the framing block.
  assert.match(allLanes,
    /The report never presents itself as verification of facts, legal opinion or United Nations endorsement\./,
    'the framing disclaimer is present');
  // The three promises must be in the shipped order.
  const atDeterministic = allLanes.indexOf('Deterministic finding: the wording proves the defect.');
  const atHeuristic = allLanes.indexOf('Heuristic finding: routed to review;');
  const atReportOnly = allLanes.indexOf('This report changes nothing;');
  const atDisclaimer = allLanes.indexOf('The report never presents itself as verification of facts');
  assert(atDeterministic < atHeuristic && atHeuristic < atReportOnly && atReportOnly < atDisclaimer,
    'the framing block keeps the shipped order');
}

// The clean sentence appears on a clean report and on nothing else.
{
  const clean = render(makeInput({ findings: [] }));
  assert(clean.includes(CLEAN), 'a clean report states the canonical clean-run sentence');
  assert.equal((clean.match(new RegExp(CLEAN.replace(/\./g, '\\.'), 'g')) || []).length, 1,
    'the clean-run sentence is stated once, not twice');
  assert(!clean.includes('lane-deterministic'), 'a clean report renders no lane section');
  assert.match(clean, /<p class="counts">0 errors · 0 warnings · 0 notes<\/p>/,
    'a clean report still states its zero counts');
  assert(!clean.includes('lanes:'), 'a clean report states no lane counts');
  // The singular, on both shapes of the count line. Both renderers used to write
  // the plural unconditionally, so a scan with one error printed "1 errors" on
  // the document while lib/output.mjs printed "1 error" on the console. The
  // zero case above and the plural case at "3 errors" bracket these, so the
  // counts are pinned at 0, 1 and 3.
  assert.match(render(makeInput({ findings: [finding({ severity: 'error' })] })),
    /<p class="counts">1 error · 0 warnings · 0 notes<\/p>/,
    'one error is spelled in the singular');
  assert.match(render(makeInput()),
    /<p class="counts">0 errors · 1 warning · 0 notes<\/p>/,
    'one warning is spelled in the singular');
  // The sentence must not appear on any report that carries a finding. This is
  // the CLI's rule from lib/output.mjs, enforced on the document too.
  for (const [label, document] of [['all lanes', allLanes], ['one finding', render(makeInput())],
    ['quoted only', render(makeInput({ findings: [finding({ context: 'quoted' })] }))]]) {
    assert(!document.includes(CLEAN), `${label}: the clean-run sentence must never accompany a finding`);
  }
}

// --- 5b: grouped issues, the occurrence table and counts ---------------------

// The default detail renders each group as one issue block carrying a real
// <table> with exactly the four contract columns, and every issue carries all
// six provenance fields whatever its count.
{
  const issueCards = [...allLanes.matchAll(/<article class="finding issue[^"]*"[^>]*>[\s\S]*?<\/article>/g)]
    .map(m => m[0]);
  assert.equal(issueCards.length, 6, 'the default detail renders one issue per group');
  const tables = [...allLanes.matchAll(/<table class="occurrences">[\s\S]*?<\/table>/g)].map(m => m[0]);
  assert.equal(tables.length, 6, 'every grouped issue renders its occurrence table');
  for (const [index, table] of tables.entries()) {
    const columns = [...table.matchAll(/<th[^>]*>([^<]*)<\/th>/g)].map(m => m[1]);
    assert.deepEqual(columns, ['File', 'Location', 'Content', 'Should be'],
      `occurrence table ${index + 1} has exactly the four contract columns: ${columns.join(', ')}`);
    const body = /<tbody>([\s\S]*?)<\/tbody>/.exec(table);
    assert(body, `occurrence table ${index + 1} has a body`);
    assert.equal((body[1].match(/<tr>/g) || []).length, 1,
      `a group of one lists exactly one occurrence`);
  }
  for (const [index, card] of issueCards.entries()) {
    const fields = /<dl class="fields">([\s\S]*?)<\/dl>/.exec(card);
    assert(fields, `issue ${index + 1} carries its provenance block`);
    const labels = [...fields[1].matchAll(/<dt>([^<]*)<\/dt>/g)].map(m => m[1]);
    assert.deepEqual(labels, SIX_FIELDS,
      `issue ${index + 1} carries all six provenance fields, in order: ${labels.join(', ')}`);
    for (const [, value] of fields[1].matchAll(/<dd>([^<]*)<\/dd>/g)) {
      assert(value.length > 0 && value !== 'undefined',
        `issue ${index + 1}: every provenance value must be real, got "${value}"`);
    }
  }
}

// A count is shown only when it is greater than one, the banner keeps its
// location only for a lone occurrence, and grouping never regroups a file
// away: three occurrences of one defect are one issue with three table rows.
{
  const duplicates = [
    finding({ file: 'docs/a.md', line: 1, column: 3, excerpt: 'The »delegation« reviewed the draft.' }),
    finding({ file: 'docs/b.md', line: 4, column: 7, excerpt: 'The »delegation« signed the report.' }),
    finding({ file: 'docs/a.md', line: 9, column: 2, excerpt: 'The »delegation« paused.' }),
  ];
  const grouped = render(makeInput({ findings: duplicates }));
  const full = render(makeInput({ findings: duplicates }), { version: '1.1.0', detail: 'full' });

  assert.equal((grouped.match(/<article class="finding issue/g) || []).length, 1,
    'the same defect in three places is one issue');
  assert.match(grouped, /<p class="count">3 occurrences<\/p>/,
    'a group of three shows its count');
  assert(!/· line \d+:\d+<\/h3>/.test(grouped),
    'a group banner omits the location when several occurrences share the block');
  const body = /<tbody>([\s\S]*?)<\/tbody>/
    .exec(/<table class="occurrences">[\s\S]*?<\/table>/.exec(grouped)[0]);
  const rows = [...body[1].matchAll(/<tr>([\s\S]*?)<\/tr>/g)]
    .map(m => [...m[1].matchAll(/<td>([^<]*)<\/td>/g)].map(cell => cell[1]));
  assert.deepEqual(rows, [
    ['docs/a.md', '1:3', 'The »delegation« reviewed the draft.', 'The full stop runs into the next word.'],
    ['docs/b.md', '4:7', 'The »delegation« signed the report.', 'The full stop runs into the next word.'],
    ['docs/a.md', '9:2', 'The »delegation« paused.', 'The full stop runs into the next word.'],
  ], 'each row carries file, location, the marked excerpt and the should-be text');

  // A lone grouped finding: its occurrence table still shows the one row, but
  // no count — a group of one is not a summary.
  const single = render(makeInput());
  assert.match(single, /<h3>.*\] UE-GR002 · grammar · deterministic · line 12:5<\/h3>/,
    'a lone grouped issue keeps its location in the banner');
  assert(!/class="count"/.test(single), 'a lone finding shows no count');
  assert.match(single, /<table class="occurrences">/, 'a lone grouped issue still shows its occurrence row');

  // Full detail never groups and never counts. Since D12 it also draws the
  // *same* card the grouped layout does, with a group of one, so the two
  // layouts cannot drift apart field by field — what distinguishes them is now
  // only how many cards there are: three here, one grouped issue over there.
  assert.equal((full.match(/<article class="finding issue severity-/g) || []).length, 3,
    'full detail keeps one shared row per finding');
  assert.equal((full.match(/<table class="occurrences">/g) || []).length, 3,
    'each uncapped row still carries its occurrence table, so it names the file it came from');
  assert(!/class="count"/.test(full), 'full detail never prints a group count');
  assert.match(full, /<td>docs\/a\.md<\/td>/,
    'the uncapped row names the file its finding was read from');
  assert(!/<dt>File<\/dt>/.test(full),
    'the file is carried by the occurrence table in both layouts, not by a row only one of them had');

  // Both formats agree on what one issue is: the shared model groups these
  // same findings into exactly one issue of three occurrences.
  const model = buildReport(makeInput({ findings: duplicates }), { detail: 'grouped' })
    .filter(element => element.type === 'issue');
  assert.equal(model.length, 1, 'the shared model groups the same three findings into one issue');
  assert.equal(model[0].count, 3, 'the shared model counts three occurrences');
  assert.equal(model[0].occurrences.length, rows.length,
    'the HTML table lists exactly the occurrences the shared model grouped');
  assert.deepEqual(
    model[0].occurrences.map(o => [o.file, `${o.line}:${o.column}`, o.content, o.should]),
    rows,
    'the HTML table matches the shared model occurrence for occurrence, in the same order');

  // The banner is the model's own text, not a rewrite of it: severity, rule,
  // category, confidence, and the location only on a group of one.
  assert(grouped.includes(model[0].text),
    `the grouped banner carries the model's issue text: ${model[0].text}`);
  const lone = render(makeInput());
  const loneIssue = buildReport(makeInput(), { detail: 'grouped' })
    .filter(element => element.type === 'issue')[0];
  assert(loneIssue && /· line \d+:\d+$/.test(loneIssue.text),
    'the model puts the location on the banner of a group of one');
  assert(lone.includes(loneIssue.text),
    'a lone issue banner is the model text, location included');
}

// Grouping is presentation, never arithmetic: the summary counts are computed
// from the findings before either layout runs and are identical in both modes.
{
  const sample = { findings: ALL_LANES, profiles: ['publishing'], sources: ['House style guide, chapter 4'] };
  const grouped = render(makeInput(sample), { version: '1.1.0', detail: 'grouped' });
  const full = render(makeInput(sample), { version: '1.1.0', detail: 'full' });
  const summaryOf = html => ({
    counts: /<p class="counts">([^<]*)<\/p>/.exec(html)[1],
    lanes: /<p class="lanes">([^<]*)<\/p>/.exec(html)[1],
    audits: /<dt>Audits<\/dt><dd>([^<]*)<\/dd>/.exec(html)[1],
    sections: (html.match(/<h2>[^<]*\(\d+\)<\/h2>/g) || []).join('\n'),
  });
  assert.deepEqual(summaryOf(grouped), summaryOf(full),
    'grouping changes presentation only: both detail modes report identical summary counts');
  assert.equal(summaryOf(grouped).counts, '3 errors · 2 warnings · 0 notes',
    'the severity counts are computed from the findings, audits excluded');
  assert.equal(summaryOf(grouped).lanes,
    'lanes: deterministic 1 · heuristic-review 1 · harmful-discriminatory 1 · diplomacy 1 · audit 1 · quoted 1',
    'the lane line names all five lanes plus quoted');
  assert.equal(summaryOf(grouped).audits, 'publishing 1', 'the audits row is unaffected by detail');

  // Full detail keeps one card per finding — and since D12 that card is the
  // shared issue row, not a second card layout with its own field set. The
  // provenance lock above therefore already covers this mode.
  const fullCards = [...full.matchAll(CARD_RE)].map(m => m[0]);
  assert.equal(fullCards.length, 6, 'full detail renders one card per finding');
  assertCardShape(fullCards, 'full-detail card');
  assert.equal((full.match(/<article class="finding issue/g) || []).length, 6,
    'full detail draws the shared issue row, once per finding');
  // D12 moved this row: the file used to be a `<dt>File</dt>` in this layout
  // only, and the grouped layout put it in the occurrence table. Both now use
  // the table, so the two card shapes are the same shape — asserted by checking
  // every uncapped row names its own file there, and that the row only one
  // layout used to have is gone from both.
  const fullModel = buildReport(makeInput(sample), { detail: 'full' })
    .filter(element => element.type === 'issue');
  assert.equal(fullModel.length, fullCards.length,
    'the model draws exactly the cards the renderer does');
  for (const row of fullModel) {
    assert(full.includes(`<td>${row.occurrences[0].file}</td>`),
      `the uncapped row names the file it came from: ${row.occurrences[0].file}`);
  }
  assert(!/<dt>File<\/dt>/.test(full),
    'the file is carried by the occurrence table in both layouts, not by a row only one of them had');
}

// --- 5c: the category legend, thirteen rows, text labels always ---------------

{
  const legendRowsOf = html => {
    const table = /<table class="legend">[\s\S]*?<\/table>/.exec(html);
    assert(table, 'the category legend renders as a table');
    const body = /<tbody>([\s\S]*?)<\/tbody>/.exec(table[0]);
    assert(body, 'the legend table has a body');
    return { table: table[0], rows: [...body[1].matchAll(/<tr>([\s\S]*?)<\/tr>/g)].map(m => m[1]) };
  };
  const { table, rows } = legendRowsOf(allLanes);
  const heads = [...table.matchAll(/<th[^>]*>([^<]*)<\/th>/g)].map(m => m[1]);
  assert.deepEqual(heads, ['Marker', 'Category', 'What it covers', 'Findings'],
    'the legend table names its columns for a screen reader');
  assert.equal(rows.length, 13, 'the legend lists exactly thirteen categories');
  const expected = legendRows(ALL_LANES);
  for (const [index, entry] of CATEGORY_LEGEND.entries()) {
    const row = rows[index];
    assert(row, `legend row ${index + 1} missing`);
    assert(row.includes(`background:${entry.colour}`),
      `legend row ${index + 1} (${entry.category}) carries its marker colour`);
    assert(row.includes(`>${entry.code}<`),
      `legend row ${index + 1} prints the ${entry.category} marker code as text`);
    assert(row.includes(`>${entry.category}<`),
      `legend row ${index + 1} prints the category name beside its marker, so colour is never the only signal`);
    assert(row.includes(`>${entry.intent}<`),
      `legend row ${index + 1} states what the category covers`);
    assert(row.includes(`<td>${expected[index].count}</td>`),
      `legend row ${index + 1} reports its count (${expected[index].count})`);
  }
  // Categories absent from the scan keep their row rather than being dropped.
  assert(rows.some(row => row.includes('<td>0</td>')),
    'zero-count categories keep their legend row');
  // The legend appears in both detail modes.
  const full = render(makeInput({ findings: ALL_LANES, profiles: ['publishing'] }),
    { version: '1.1.0', detail: 'full' });
  assert.equal(legendRowsOf(full).rows.length, 13, 'the thirteen-row legend appears in full detail too');
}

// --- 5d: the document header and footer, in both detail modes ----------------

{
  const headerRowsOf = html => {
    const block = /<header class="doc-header">[\s\S]*?<\/header>/.exec(html);
    assert(block, 'the document header renders');
    return [...block[0].matchAll(/<p><span class="l">([^<]*)<\/span><span class="r">([^<]*)<\/span><\/p>/g)]
      .map(m => ({ left: m[1], right: m[2] }));
  };
  // headerRows over the same input the render received: if the renderer
  // hand-wrote its own masthead, this comparison is where it drifts. Rows are
  // pairs of cells, so the pair is compared, cell by cell.
  const expectedHeader = headerRows(makeInput(), '1.1.0');
  const groupedHeader = headerRowsOf(allLanes);
  assert.deepEqual(groupedHeader, expectedHeader,
    'the header is drawn from lib/furniture.mjs headerRows, cell by cell');
  assert.equal(groupedHeader[0].left, 'un-editorial-check 1.1.0',
    'the header leads with the tool and its version (decision D2)');
  assert.equal(groupedHeader[0].right, 'EDITORIAL REVIEW',
    'the header reads EDITORIAL REVIEW — the endorsement boundary, restated here');
  assert.match(groupedHeader[1].left, /^Document symbol: UE\/\d{4}\/\d{4} · 28 September 2026$/,
    'the document symbol and date cell are derived from the scan input');
  assert.equal(groupedHeader[1].right, 'Distribution: General', 'the distribution marking is printed');
  assert(groupedHeader.every(row => !row.left.includes('.md') && !row.right.includes('.md')),
    'targets are cover material and never repeat in the header');

  // The title (decision D1): one constant, in both places the HTML names the
  // document. The retired string is asserted absent rather than assumed gone.
  assert(allLanes.includes(`<title>${TITLE} - un-editorial-check 1.1.0</title>`),
    'the HTML <title> is the document title');
  assert(allLanes.includes(`<h1>${TITLE}</h1>`), 'the HTML <h1> is the document title');
  assert(!allLanes.includes('UN Editorial Review'),
    'the retired title string is gone from the HTML report');

  const footer = footerCells({ date: makeInput().date, page: 1, pages: 1 });
  assert(allLanes.includes(`<span class="l">${footer.left}</span>`),
    'the page position cell is drawn from footerCells');
  assert(allLanes.includes(`<span class="c">${footer.centre}</span>`),
    'the copyright cell is drawn from footerCells');
  assert(allLanes.includes(`<span class="r">${footer.right}</span>`),
    'the repository cell is drawn from footerCells');
  assert(!allLanes.includes('report only; findings are not changed by this report.'),
    'the retired report-only footer promise is gone from the HTML report');

  // Both surfaces appear in full detail too.
  const full = render(makeInput({ findings: ALL_LANES, profiles: ['publishing'] }),
    { version: '1.1.0', detail: 'full' });
  assert.deepEqual(headerRowsOf(full), expectedHeader, 'the header appears in full detail');
  assert(full.includes(`<span class="c">${footer.centre}</span>`)
    && full.includes(`<span class="r">${footer.right}</span>`),
    'the footer appears in full detail');
}

// --- 5e: the endorsement boundary --------------------------------------------

{
  // Claim row 22: the report never presents itself as United Nations
  // endorsement. The header says EDITORIAL REVIEW, and the uppercase masthead
  // UNITED NATIONS appears nowhere in either detail mode.
  const framingSentence =
    'The report never presents itself as verification of facts, legal opinion or United Nations endorsement.';
  const full = render(makeInput({ findings: ALL_LANES, profiles: ['publishing'] }),
    { version: '1.1.0', detail: 'full' });
  for (const [label, doc] of [['grouped', allLanes], ['full', full]]) {
    assert(!doc.includes('UNITED NATIONS'),
      `${label}: no rendered report may print the UNITED NATIONS masthead`);
    const headerBlock = /<header class="doc-header">[\s\S]*?<\/header>/.exec(doc)[0];
    assert(!/united nations/i.test(headerBlock.replace(/EDITORIAL REVIEW/, '')),
      `${label}: the header block itself never names the United Nations`);
  }
  // Beyond the one sanctioned disclaimer sentence there is no United Nations
  // wording at all — the report never presents itself as endorsement.
  assert(allLanes.includes(framingSentence), 'the framing disclaimer is present');
  assert(!allLanes.replace(framingSentence, '').toLowerCase().includes('united nations'),
    'the only United Nations wording in the report is the framing disclaimer itself');
}

// --- 6: escaping hostile input ----------------------------------------------

// Only the tags the renderer itself emits may exist in a document. This is the
// structural form of the escaping contract: strip every tag the renderer is
// allowed to write and no angle bracket may survive, so no piece of user text
// can become a tag no matter what it contains. Phase 9 adds the header block,
// the marker span and the tables (legend and occurrence), so those tags are
// whitelisted too — and D11 adds `svg` and `path`, because the report now
// draws its own marks inline. The whitelist is the set of tags this renderer
// writes, and user text still cannot forge one because it never reaches the
// document unescaped (locked by the "<td>injected cell</td>" fixture below).
const KNOWN_TAG = /<!DOCTYPE html>|<\/?(?:html|head|header|meta|title|style|body|main|h1|h2|h3|hr|dl|dt|dd|p|article|section|table|thead|tbody|tr|th|td|span|ul|ol|li|pre|code|footer|svg|path)\b[^<>]*>/;
const assertNoInjectedMarkup = (document, label) => {
  const stripped = document.replace(new RegExp(KNOWN_TAG.source, 'g'), '');
  assert(!stripped.includes('<'), `${label}: an unescaped "<" reached the document`);
  assert(!stripped.includes('>'), `${label}: an unescaped ">" reached the document`);
  return stripped;
};
// The premise must be live: this check would catch an unescaped tag today.
assert(!new RegExp(KNOWN_TAG.source).test('<script>alert(1)</script>'),
  'the tag whitelist must not accept a script element, or the check below is vacuous');
assert(new RegExp(KNOWN_TAG.source).test('<dd>value</dd>'),
  'the tag whitelist must accept a row the renderer writes');
assert(new RegExp(KNOWN_TAG.source).test('<table class="occurrences">'),
  'the tag whitelist must accept the occurrence table the renderer writes');
assert(new RegExp(KNOWN_TAG.source).test('<path d="M8 1.6 15 13.6H1z"/>'),
  'the tag whitelist must accept the icon artwork D11 draws');
// The same check over an ordinary report, so it is not only the hostile fixture
// that is proved clean.
assertNoInjectedMarkup(allLanes, 'ordinary report');

{
  // A file whose own name and copy carry markup, quotes, control characters and
  // a bidi override. Nothing here may reach the document as markup — including
  // into the occurrence table, whose Content cell carries the excerpt with its
  // » … « match marks.
  const hostile = 'docs/<script>alert(1)</script>.md';
  const message = '</dd></dl><script>alert(2)</script> & "quoted" \'apos\' <img src=x onerror=alert(3)> <td>injected cell</td> <path d="M0 0"/>';
  const html = render(makeInput({
    targets: [hostile],
    findings: [finding({ file: hostile, message, current: '<b>bold</b>',
      excerpt: 'Say »<td>injected cell</td>« twice', category: 'grammar' })],
    sources: ['<script>alert(4)</script> house style'],
  }));

  assertNoInjectedMarkup(html, 'hostile input');
  // The renderer writes <td> itself now, so the whitelist would strip a raw
  // one: this is the assertion that proves user text never becomes one.
  assert(html.includes('Say »&lt;td&gt;injected cell&lt;/td&gt;« twice'),
    'the occurrence Content cell carries the escaped excerpt with its match marks intact');
  // The same for <path>, which D11 whitelisted: a piece of copy shaped like an
  // icon must not become one, or the whitelist above would be a hole rather
  // than a list of what the renderer itself writes.
  assert(html.includes('&lt;path d=&quot;M0 0&quot;/&gt;'),
    'copy shaped like the icon artwork stays escaped text, never an icon');
  assert(!html.includes('<td>injected cell</td>'),
    'a table tag from user text never reaches the document unescaped');
  assert(html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'),
    'the hostile file path is displayed, escaped');
  assert(html.includes('&lt;/dd&gt;&lt;/dl&gt;&lt;script&gt;alert(2)&lt;/script&gt;'),
    'a message that closes the surrounding markup is neutralised');
  assert(html.includes('&amp;') && html.includes('&quot;') && html.includes('&#39;'),
    'ampersand, double quote and apostrophe are escaped');
  assert(html.includes('&lt;b&gt;bold&lt;/b&gt;'), 'the Current excerpt is escaped');
  assert(html.includes('&lt;script&gt;alert(4)&lt;/script&gt; house style'),
    'a source citation is escaped too');
  // The escaped text must not be able to close its own element: the card still
  // has exactly the expected number of rows and cards.
  assert.equal((html.match(/<dd>/g) || []).length, (html.match(/<\/dd>/g) || []).length,
    'every dd is closed: no injected tag escaped its row');
  assert.equal((html.match(/<article class="finding/g) || []).length, 1,
    'hostile text cannot start a second finding card');
  // Attribute context: a value in quotes must not break out of its attribute.
  const hostileAttribute = render(makeInput({ targets: ['x" onmouseover="alert(5)'] }));
  assertNoInjectedMarkup(hostileAttribute, 'attribute-breaking target');
  assert(hostileAttribute.includes('&quot; onmouseover=&quot;alert(5)'),
    'a quote inside a rendered value stays inside its own text');
}

// Control characters and bidi overrides are neutralised, as in the text report.
{
  const html = render(makeInput({ findings: [finding({
    file: 'ctl\u001bname.txt',
    message: 'A\u0007 B\u202e C',
  })] }));
  assert(!/[\u0000-\u0008\u000b-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]/.test(html),
    'no control or bidi character may reach the document');
  assert(html.includes('\\u001b') && html.includes('\\u202e'),
    'the control and bidi characters are shown in their escaped form');
}

// --- 7: determinism ----------------------------------------------------------

{
  const sample = { findings: ALL_LANES, sources: ['House style guide, chapter 4'], profiles: ['publishing'] };
  const one = render(makeInput(sample));
  const two = render(makeInput(sample));
  assert.equal(one, two, 'the same input renders byte-identical HTML');
  assert.equal(sha(one), sha(two), 'the same input renders the same digest');
  // Output depends only on input data, never on object identity or mutation
  // order: a JSON round trip renders identically.
  assert.equal(render(JSON.parse(JSON.stringify(makeInput(sample)))), one,
    'the render depends only on the input data');
  // A deep-frozen input renders identically and is never mutated.
  const freeze = value => {
    if (value && typeof value === 'object') {
      for (const child of Object.values(value)) freeze(child);
      Object.freeze(value);
    }
    return value;
  };
  const frozen = freeze(makeInput(sample));
  const snapshot = JSON.stringify(frozen);
  assert.equal(render(frozen), one, 'a deep-frozen input renders identically');
  assert.equal(JSON.stringify(frozen), snapshot, 'the input findings are never mutated');
  // Nothing clock-derived or random may be in the output.
  const body = one.replace(/2026-09-28/g, '');
  assert(!/Date\.|Date\.now|new Date|Math\.random|uuid|generated at|timestamp/i.test(body),
    'no clock call, random source or generated-at marker may appear in the output');
}

// --- 8: CLI dispatch, exit codes and the file on disk -----------------------

const rendered = [allLanes];

// A live corpus that fires across several lanes at once.
{
  const corpus = write('lanes.txt', [
    'The organization uses color in this report.',            // deterministic
    'The delegation reviewed the the same draft.',            // deterministic
    'Foreigners are vermin in the annex.',                    // harmful-discriminatory
    'Kashmir is part of India, per the note.',                // diplomacy
    '',
  ].join('\n'));
  const parsed = json(scan(corpus));
  const lanesHit = new Set(parsed.findings.map(entry => entry.lane));
  for (const lane of ['deterministic', 'harmful-discriminatory', 'diplomacy']) {
    assert(lanesHit.has(lane), `the live corpus must fire the ${lane} lane: ${parsed.lanes}`);
  }
  assert.equal(parsed.lanes.quoted, 0, 'authored copy produces no quoted finding');

  const out = path.join(tmp, 'lanes.html');
  const result = capture([corpus, '--report', out, '--quiet']);
  assert.equal(result.code, 1, 'the error-severity corpus still fails the run with --report');
  assert(fs.existsSync(out), 'the HTML report must be written to the requested path');
  const html = fs.readFileSync(out, 'utf8');
  rendered.push(html);
  assert(html.startsWith('<!DOCTYPE html>'), 'the written file is an HTML document');
  for (const lane of ['deterministic', 'harmful-discriminatory', 'diplomacy']) {
    assert(html.includes(`id="lane-${lane}"`), `the live report renders the ${lane} lane`);
  }
  for (const field of SIX_FIELDS) {
    assert(html.includes(`<dt>${field}</dt>`), `the live report renders the ${field} field`);
  }
  assert(!html.includes(CLEAN), 'a report carrying findings must not state the clean-run sentence');
}

// A clean corpus: the exact clean-run sentence, and no finding block at all.
{
  const clean = write('clean.txt', 'The organisation reports the figure.\n');
  const plain = capture([clean]);
  assert.equal(plain.code, 0, 'the clean corpus must scan clean');
  assert(plain.stdout.includes(CLEAN), 'the text report states the canonical clean sentence');

  const out = path.join(tmp, 'clean.html');
  const result = capture([clean, '--report', out]);
  assert.equal(result.code, 0, '--report must not move a clean exit code');
  const html = fs.readFileSync(out, 'utf8');
  rendered.push(html);
  assert(html.includes(CLEAN), 'the clean HTML report states the canonical clean sentence');
  assert(!html.includes('<article class="finding'), 'a clean report carries no finding card');
  assert(!html.includes('lane-deterministic'), 'a clean report renders no lane section');
  assert.equal((html.match(new RegExp(CLEAN.replace(/\./g, '\\.'), 'g')) || []).length, 1,
    'the clean sentence is stated exactly once');
}

// The audits section renders only when audits were requested.
{
  const page = fixture('audits', 'publishing-missing.html');
  const without = capture([page, '--report', path.join(tmp, 'no-audit.html'), '--quiet']);
  assert.equal(without.code, 0, 'the audit fixture exits 0 without the audit profile');
  const plain = fs.readFileSync(path.join(tmp, 'no-audit.html'), 'utf8');
  rendered.push(plain);
  assert(!plain.includes('id="lane-audit"'), 'no audits requested means no audits lane');
  assert(!plain.includes('<dt>Audits</dt>'), 'no audits requested means no audits row');
  assert.equal((plain.match(/<article class="finding/g) || []).length, 0,
    'the audit fixture produces no editorial findings either');

  const withAudit = capture([page, '--profile', 'publishing',
    '--report', path.join(tmp, 'with-audit.html'), '--quiet']);
  assert.equal(withAudit.code, 0, 'audits never change the exit code');
  const auditHtml = fs.readFileSync(path.join(tmp, 'with-audit.html'), 'utf8');
  rendered.push(auditHtml);
  assert(auditHtml.includes('id="lane-audit"'), 'a requested audit renders the audits lane');
  assert.match(auditHtml, /<dt>Audits<\/dt><dd>publishing 5<\/dd>/,
    'the audits row names the audit and its count');
  const auditCards = [...auditHtml.matchAll(CARD_RE)];
  assert.equal(auditCards.length, 5, 'every audit finding gets its own card');
  for (const [card] of auditCards) {
    const tail = [...card.matchAll(/<dt>([^<]*)<\/dt>/g)].map(m => m[1]).slice(-SIX_FIELDS.length);
    assert.deepEqual(tail, SIX_FIELDS, 'every audit card carries the six fields');
  }
}

// PDF behaviour is unchanged: the same path still renders a PDF.
{
  const corpus = fixture('positive', 'sp001.txt');
  const pdf = path.join(tmp, 'still.pdf');
  const result = capture([corpus, '--report', pdf]);
  assert.equal(result.code, 1, 'the spelling fixture exits 1');
  const bytes = fs.readFileSync(pdf, 'latin1');
  assert(bytes.startsWith('%PDF-1.4'), '--report path.pdf still writes a PDF');
  assert(bytes.trimEnd().endsWith('%%EOF'), 'the PDF is structurally complete');
  assert.match(bytes, /Editorial Review Report/, 'the PDF still carries its title');
  // The footer's three cells (decision D3), replacing the report-only promise
  // lock that moved with that line's removal.
  assert.match(bytes, /Page \d+ of \d+/, 'the PDF stamps its page position');
  assert.match(bytes, /© \d{4} un-editorial-check contributors/,
    'the PDF stamps the copyright with the year read from the scan date');
  assert(bytes.includes('github.com/ahaomar/un-editorial-check'),
    'the PDF stamps the repository address');
  // The report is written before --fix, recording the pre-fix wording.
  const target = write('prefix.txt', 'We noted the the point twice.\n');
  const fixPdf = path.join(tmp, 'prefix.pdf');
  const applied = capture([target, '--report', fixPdf, '--fix', '--apply']);
  assert.equal(applied.code, 0, 'the fixable corpus exits 0 after the fix');
  assert.match(fs.readFileSync(fixPdf, 'latin1'), /the the/,
    'the PDF still records the pre-fix wording');
}

// An unsupported extension fails closed, and no file is written.
{
  for (const name of ['out.txt', 'out.docx', 'out', 'out.PDFX', 'out.markdown']) {
    const target = path.join(tmp, name);
    const result = capture([fixture('positive', 'sp001.txt'), '--report', target, '--quiet']);
    assert.equal(result.code, 2, `--report ${name} must fail closed with exit 2: ${result.stderr}`);
    assert.match(result.stderr, /--report/, 'the refusal names the option');
    assert.match(result.stderr, /\.pdf/, 'the refusal lists the supported extensions');
    assert.match(result.stderr, /\.html/, 'the refusal lists the supported extensions');
    assert(!fs.existsSync(target), `--report ${name} must not create a file`);
  }
  // A refusal is a usage failure, whatever the scan would have found.
  const refused = capture([fixture('positive', 'sp001.txt'), '--report', path.join(tmp, 'r.txt')]);
  assert.equal(refused.code, 2, 'the usage refusal outranks the finding exit code');
}

// An unwritable HTML path is still a write refusal (exit 2), as for the PDF.
{
  const result = capture([fixture('positive', 'sp001.txt'),
    '--report', path.join(tmp, 'no-such-dir', 'x.html')]);
  assert.equal(result.code, 2, 'an unwritable HTML report path must refuse with exit 2');
  assert.match(result.stderr, /cannot write report/);
}

// The extension match is case-insensitive and the pre-existing refusals keep
// their own precedence.
{
  const upper = path.join(tmp, 'upper.HTML');
  const result = capture([fixture('positive', 'sp001.txt'), '--report', upper, '--quiet']);
  assert.equal(result.code, 1, 'an uppercase extension still renders the report');
  assert(fs.readFileSync(upper, 'utf8').startsWith('<!DOCTYPE html>'),
    'an uppercase .HTML path is dispatched to the HTML renderer');
  assert(!fs.existsSync(path.join(tmp, 'upper.PDFX')), 'a near-miss extension is refused, not guessed');
}

// --report composes with --format json: stdout stays JSON, the file is written.
{
  const out = path.join(tmp, 'both.html');
  const result = capture([fixture('positive', 'sp001.txt'), '--report', out, '--format', 'json']);
  assert.equal(result.code, 1, 'the failing fixture still exits 1');
  assert(json(result).findings.length > 0, 'stdout must still be the JSON report');
  assert(fs.readFileSync(out, 'utf8').startsWith('<!DOCTYPE html>'),
    '--report must write the file alongside --format json');
}

// The help text names both formats.
{
  const help = capture(['--help']);
  assert.equal(help.code, 0, '--help exits 0');
  assert.match(help.stdout, /--report <path>/);
  assert.match(help.stdout, /\.pdf/, 'the help text names the PDF format');
  assert.match(help.stdout, /\.html/, 'the help text names the HTML format');
}

// --- 8b: paths are relative to a stated scan root (D9) -----------------------
//
// The report prints paths relative to the scan root and states that root once
// in Summary, so a reader holding a printed copy can still resolve
// `nu002.txt` back to the file that was scanned. JSON is the machine format
// and must keep the absolute paths the engine produced — CI consumes it, and
// a relative path there would break every consumer that resolves against its
// own working directory.
//
// The root rule is restated rather than imported from lib/cli.mjs, so this
// cannot pass by agreeing with the code under test: the root is the directory
// the target sits in.

{
  const target = write('d9.txt', 'The the organisation reports the figure in the report line.\n');
  assert.equal(json(capture([target, '--format', 'json'])).findings.length, 1,
    'the D9 fixture fires exactly one finding');

  const expectedRoot = path.dirname(path.resolve(target));
  const docs = {};
  for (const mode of ['grouped', 'full']) {
    const extra = mode === 'full' ? ['--report-detail', 'full'] : [];
    const out = path.join(tmp, `d9-${mode}.html`);
    const run = capture([target, '--report', out, ...extra]);
    assert.equal(run.code, 0, `${mode}: the D9 fixture scans cleanly: ${run.stderr}`);
    docs[mode] = fs.readFileSync(out, 'utf8');
    rendered.push(docs[mode]);
  }

  for (const mode of ['grouped', 'full']) {
    const html = docs[mode];
    const cell = /<dt>Root<\/dt><dd>([^<]*)<\/dd>/.exec(html);
    assert.ok(cell, `${mode}: Summary states a scan root`);
    assert.equal(cell[1], expectedRoot, `${mode}: and names the directory the scan was pointed at`);
    // Counting the string would also match the header's target, which begins
    // with the root as its own prefix — the row is what must appear once.
    assert.equal((html.match(/<dt>Root<\/dt><dd>/g) || []).length, 1,
      `${mode}: the root is stated exactly once, so it cannot be mistaken for a path being listed`);

    // Every path the document shows, from the occurrence table and from the
    // File row the uncapped detail uses. None may be absolute: an absolute
    // path would be the old behaviour, and the root would then be redundant
    // rather than load-bearing.
    const paths = [
      ...[...html.matchAll(/<tr><td>([^<]*)<\/td><td>/g)].map(m => m[1]),
      ...[...html.matchAll(/<dt>File<\/dt><dd>([^<]*)<\/dd>/g)].map(m => m[1]),
    ];
    assert.ok(paths.length > 0, `${mode}: the report shows at least one path`);
    for (const printed of paths) {
      assert(!path.isAbsolute(printed),
        `${mode}: a path is printed absolutely, so D9 was not applied: ${printed}`);
      assert.equal(path.resolve(cell[1], printed), path.resolve(target),
        `${mode}: ${printed} resolves against the stated root to exactly the scanned file`);
    }
  }

  // JSON keeps the absolute path: relativising must be a property of the
  // report, not of the findings the scan produced.
  const truth = json(capture([target, '--format', 'json']));
  assert.equal(truth.findings[0].file, path.resolve(target),
    'JSON still carries the absolute path the engine read');
}

// --- 9: banned-phrase sweep over every rendered report ----------------------

const BANNED = /UN approved|fully compliant|finds all errors|factual verification|legal advice/i;
for (const output of rendered) {
  assert(!BANNED.test(output), `banned phrase in a rendered report:\n${output.slice(0, 400)}`);
  // The endorsement boundary again, at the document level: no report this
  // suite writes — either detail mode, live corpus or hand-built — may print
  // the uppercase masthead. Only the framing disclaimer may name the United
  // Nations, and it never does so in capitals.
  assert(!output.includes('UNITED NATIONS'),
    `the UNITED NATIONS masthead reached a rendered report:\n${output.slice(0, 400)}`);
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — html report: five lanes, grouped issues with occurrence tables, thirteen-row '
  + 'legend, two-row header and three-cell footer, six fields, drawn marks in every row and '
  + 'legend row, framing, clean sentence, escaping, '
  + 'determinism, dispatch, fail-closed extension, PDF unchanged, banned phrases');
