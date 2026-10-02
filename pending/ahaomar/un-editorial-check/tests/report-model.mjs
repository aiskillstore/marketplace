// Report model tests — plain node:assert, run with: node tests/report-model.mjs
//
// Covers the contract in .feedbacks/PHASE3-CONTRACT.md §2: the element union
// (unknown type throws), section order (D5) and the absence of section numbers
// (D6), per-finding blocks for every severity, the proposed/suggestion/message
// should-be fallback, the fixable markers, the heuristic paragraph, audits,
// sources, the empty scan, line/column sorting, file grouping, and purity
// (frozen input, deterministic output, no mutation of the findings array or
// its objects).
//
// The pre-1.5.0 "Review queue (heuristic findings)" block is gone: its whole
// job was to list every heuristic finding so a reviewer could not miss one,
// and the Agent Review Required section does that with full issue blocks
// instead of an 80-character excerpt. The locks that used to point at the
// queue point at that section now, in .feedbacks/REPORT-REDESIGN-PLAN.md §6.

import assert from 'node:assert/strict';
import { buildReport, assertElements, capLines } from '../lib/report.mjs';

// This suite describes the pre-Phase-9 layout — one block per finding — which
// `--report-detail full` restores. The grouped default has its own assertions
// at the end of the file; nothing here was rewritten to fit it, only pointed at
// the mode it has always been describing.
const buildReportFull = (input) => buildReport(input, { detail: 'full' });

// --- fixtures ---------------------------------------------------------------

const severityTag = { error: 'ERROR', warning: 'WARNING', info: 'NOTE' };

function bannerText(severity, ruleId, category, confidence, line, column) {
  return `[${severityTag[severity]}] ${ruleId} · ${category} · ${confidence} · line ${line}:${column}`;
}

const LONG_MESSAGE =
  'Each finding explains why the wording was flagged and what a reviewer should consider before any change is made in the source document.';
assert(LONG_MESSAGE.length > 80, 'fixture message long enough to prove nothing shortens it');

const MANUAL_SUFFIX = ' — manual / agent rewrite; not --fix-able';
const FIXABLE_SUFFIX = ' — --fix-able';

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
    _unit: null,
    _index: 0,
    _matched: null,
    _offset: 0,
    _replacement: null,
    ...overrides,
  };
}

function makeInput(overrides = {}) {
  return {
    version: '0.7.0',
    date: '2026-09-27',
    targets: ['docs'],
    profiles: [],
    filesCount: 4,
    findings: [finding()],
    sources: [],
    ...overrides,
  };
}

function kvValue(report, label) {
  const row = report.find(e => e.type === 'kv' && e.label === label);
  assert(row, `missing kv row: ${label}`);
  return row.value;
}

function headingIndex(report, text) {
  const i = report.findIndex(e => (e.type === 'heading' || e.type === 'issue' || e.type === 'banner') && e.text === text);
  assert(i >= 0, `missing heading: ${text}`);
  return i;
}

function paragraphTexts(report) {
  return report.filter(e => e.type === 'paragraph').map(e => e.text);
}

// D12: a finding is one `issue` element in both detail modes, so the headline
// the reader sees is that element's own `text` and `kind`. Callers want "the
// per-finding headline and its severity", which is exactly what comes back —
// and because the real element is returned, not a copy, a caller can still
// locate it by identity inside the report it was taken from.
function bannersFrom(report, index) {
  return report.slice(index).filter(e => e.type === 'issue');
}

// D12 (.feedbacks/REPORT-REDESIGN-PLAN.md §10 item 4): every row — in either
// detail mode, in every section, for every severity — closes with the same six
// provenance fields, in contract order. This list was **five** fields and had
// no `Confidence` in it: the test had been shaped around `pushFinding`'s bug
// rather than around the contract, which is how `full` printed one fewer field
// than `grouped` without anything failing.
const LANE_LABELS = ['Lane', 'Source', 'Profile', 'Confidence', 'Limitation', 'Action'];

function assertLaneBlock(report, startIndex) {
  const row = report[startIndex];
  assert.equal(row && row.type, 'issue',
    'every finding block is the one shared issue row, not a second implementation of it');
  assert.deepEqual(row.provenance.map(p => p.label), LANE_LABELS,
    `every row carries all six provenance fields in contract order: `
      + row.provenance.map(p => p.label).join(', '));
  // The lane rows close the block: nothing but the occurrence table may follow
  // them inside the row, and nothing may hang off the end of the row itself.
  const keys = Object.keys(row);
  assert.equal(keys[keys.indexOf('provenance') + 1], 'occurrences',
    'the provenance block closes the row, ahead of its occurrence table');
  const after = report[startIndex + 1];
  assert(!after || after.type === 'issue' || after.type === 'heading'
    || after.type === 'spacer',
    'a finding row is a complete block: nothing may hang off the end of it');
}

function deepFreeze(value) {
  if (value && typeof value === 'object') {
    for (const child of Object.values(value)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}

// --- element union: unknown type throws -------------------------------------

const probe = [
  { type: 'banner', kind: 'note', text: 'x' },
  { type: 'heading', level: 1, text: 'x' },
  { type: 'paragraph', text: 'x' },
  { type: 'kv', label: 'x', value: 'y' },
  { type: 'bullets', items: ['x'] },
  { type: 'spacer' },
  { type: 'rule' },
];
assert.deepEqual(assertElements(probe), probe, 'assertElements accepts every union member');
assert.throws(() => assertElements([{ type: 'widget' }]), /unknown element type: widget/);
assert.throws(
  () => assertElements([{ type: 'table', rows: [] }]),
  { name: 'Error', message: 'unknown element type: table' },
);
assert.throws(() => assertElements([{}]), /unknown element type/);
assert.throws(() => assertElements([null]), /unknown element type/);
assertElements(buildReportFull(makeInput()), 'buildReport output stays inside the union');

// --- cover block and kv rows ------------------------------------------------

const report = buildReportFull(makeInput({
  targets: ['docs', 'README.md'],
  profiles: ['publishing', 'accessibility'],
}));

assert.deepEqual(report[0], { type: 'banner', kind: 'title', text: 'Editorial Review Report' });
assert.deepEqual(
  report.slice(1, 6).map(e => e.label),
  ['Version', 'Date', 'Targets', 'Profiles', 'Files scanned'],
  'cover kv rows appear in contract order',
);
assert.equal(report[1].value, '0.7.0');
assert.equal(report[2].value, '2026-09-27');
assert.equal(report[3].value, 'docs README.md', 'targets joined with spaces');
assert.equal(report[4].value, 'publishing, accessibility');
assert.equal(report[5].value, '4', 'kv value coerced with String()');
assert.deepEqual(report[6], { type: 'rule' }, 'hairline rule closes the cover block');

const noProfiles = buildReportFull(makeInput());
assert(!noProfiles.some(e => e.type === 'kv' && e.label === 'Profiles'), 'empty profiles omits the row');
assert.deepEqual(
  noProfiles.slice(1, 5).map(e => e.label),
  ['Version', 'Date', 'Targets', 'Files scanned'],
);

// --- the full fixture: cover, counts, audits, findings, queue, sources ------

const fullFindings = [
  finding({
    line: 4,
    column: 9,
    ruleId: 'UE-RE005',
    category: 'register',
    severity: 'error',
    message: 'An exclamation mark is not used in formal copy.',
    current: 'A sentence with a misplaced mark',
  }),
  finding({ line: 12, column: 5 }),
  finding({
    line: 3,
    column: 7,
    ruleId: 'UE-HS002',
    category: 'hate-speech',
    severity: 'error',
    confidence: 'heuristic',
    message: LONG_MESSAGE,
  }),
  finding({
    file: 'index.html',
    line: 1,
    column: 1,
    ruleId: 'UE-EO001',
    category: 'publishing',
    severity: 'warning',
    audit: 'publishing',
    message: 'One first-level heading is required here.',
  }),
  finding({
    file: 'index.html',
    line: 2,
    column: 3,
    ruleId: 'UE-AX001',
    category: 'accessibility',
    severity: 'warning',
    confidence: 'heuristic',
    audit: 'accessibility',
    message: 'The image tag carries no alternative text.',
  }),
];
const fullSources = ['House style guide, chapter 4', 'United Nations editorial manual'];
const full = buildReportFull(makeInput({
  profiles: ['publishing'],
  findings: fullFindings,
  sources: fullSources,
}));

// section order (D5) and section numbering (D6)
const iSummaryHeading = headingIndex(full, 'Summary');
const iCategoriesHeading = headingIndex(full, 'Categories');
const iCounts = full.findIndex(e => e.type === 'paragraph' && e.text.endsWith(' notes'));
const iAudits = full.findIndex(e => e.type === 'kv' && e.label === 'Audits');
const iLegend1 = full.findIndex(e => e.type === 'paragraph' && e.text.includes('the wording proves the defect'));
const iLegend2 = full.findIndex(e => e.type === 'paragraph' && e.text.includes('never asserts'));
const iLegend3 = full.findIndex(e => e.type === 'paragraph' && e.text.includes('changes nothing'));
const iFindingsHeading = headingIndex(full, 'Findings by file');
const iRecsHeading = headingIndex(full, 'Priority Recommendations');
const iSourcesHeading = headingIndex(full, 'Sources');
assert.equal(full.findIndex(e => e.type === 'heading'), iSummaryHeading,
  'Summary is the first heading, straight after the cover rule');
assert.deepEqual(full.slice(iSummaryHeading - 2, iSummaryHeading).map(e => e.type),
  ['rule', 'spacer'], 'the cover rule then a spacer open the Summary section');
assert(iSummaryHeading < iCounts && iCounts < iAudits, 'counts and audit row live inside Summary');
assert(iAudits < iLegend1, 'the three promises follow the counts');
assert(iLegend1 < iLegend2 && iLegend2 < iLegend3, 'legend paragraphs keep their order');
assert(iLegend3 < iCategoriesHeading, 'Categories follows the promises');
assert(iCategoriesHeading < iFindingsHeading, 'the body follows Categories');
assert(iFindingsHeading < iRecsHeading && iRecsHeading < iSourcesHeading,
  'priority recommendations before sources');

// D6: a section heading never carries a number — no "1.", no "2)", no bare
// leading digit. The count lives on the heading's own `count` field, not in
// its text, so a reader cannot mistake a position for a heading number.
for (const element of full) {
  if (element.type !== 'heading') continue;
  assert(!/^\s*\d+[.)]/.test(element.text) && !/^\s*\d+\s/.test(element.text),
    `section heading carries a number: ${element.text}`);
}
assert(full.some(e => e.type === 'heading' && e.text === 'Summary' && e.count === '5 findings'),
  'the count rides beside the title rather than inside it');

// the three legend promises must be present
assert(full.some(e => e.type === 'paragraph' && e.text.includes('the wording proves the defect')),
  'deterministic promise');
assert(full.some(e => e.type === 'paragraph' && e.text.includes('routed to review')
  && e.text.includes('never asserts') && e.text.includes('legal threshold')),
'heuristic promise');
assert(full.some(e => e.type === 'paragraph' && e.text.includes('changes nothing')),
  'report-only promise');

// counts exclude audits; audits get their own sorted row
// The single warning is what pins the singular: before the shared pluraliser
// this line read "1 warnings", because both renderers wrote the plural no
// matter what the count was. Breaking severityCounts must make this fail.
assert.equal(full[iCounts].text, '2 errors · 1 warning · 0 notes');
assert.equal(kvValue(full, 'Audits'), 'accessibility 1, publishing 1',
  'audit rows sorted by profile name, audits excluded from severity counts');

// every level-1 heading is preceded by a spacer; level-2 headings are files
for (let i = 1; i < full.length; i++) {
  if (full[i].type === 'heading' && full[i].level === 1) {
    assert.equal(full[i - 1].type, 'spacer', 'spacer precedes each level-1 heading');
  }
}
const level2 = full.filter(e => e.type === 'heading' && e.level === 2);
assert.deepEqual(level2.map(e => e.text), ['docs/page.md', 'index.html'], 'one heading per file');

// --- per-finding blocks: severity mapping and block shape -------------------

// D12: the uncapped layout is the shared issue row with a group of one. The
// assertions below therefore read that element's own fields rather than a
// sibling run of banner/kv/paragraph elements, and the uniformity claim is
// checked directly — see the parity block at the end of this section.
const hsIdx = full.findIndex(e => e.type === 'issue' && e.text.includes('UE-HS002'));
assert.equal(full[hsIdx] && full[hsIdx].type, 'issue',
  'the uncapped finding block is the shared issue row, not a separate implementation');
const hs = full[hsIdx];
assert.equal(hs.kind, 'error', 'a hate-speech finding presents as an error');
assert.equal(hs.text, bannerText('error', 'UE-HS002', 'hate-speech', 'heuristic', 3, 7),
  'the row headline is built from the finding');
assert.equal(hs.current, '(not applicable)', 'the row quotes the current copy');
assert(!JSON.stringify(full).includes('whole line context'),
  'no developer placeholder may reach the director-facing report');
assert.equal(hs.should, LONG_MESSAGE + MANUAL_SUFFIX, 'the row carries the fixable suffix');
assert.equal(hs.message, LONG_MESSAGE, 'the row carries the reason');
assert.equal(hs.heuristic, true,
  'a heuristic finding is routed to review by its own flag, not by a stray paragraph');
assert.equal(hs.count, 1, 'an uncapped row is a group of one, so it shows no count');
assertLaneBlock(full, hsIdx);

const errIdx = full.findIndex(e => e.type === 'issue' && e.text.includes('UE-RE005'));
const err = full[errIdx];
assert.equal(err.kind, 'error');
assert.equal(err.text, bannerText('error', 'UE-RE005', 'register', 'deterministic', 4, 9),
  'the row headline is built from the finding');
assert.equal(err.current, 'A sentence with a misplaced mark');
assert.equal(err.should,
  'An exclamation mark is not used in formal copy.' + MANUAL_SUFFIX);
assert.equal(err.message, 'An exclamation mark is not used in formal copy.');
assert.equal(err.audit, null, 'editorial block carries no audit row');
assertLaneBlock(full, errIdx);

const warnIdx = full.findIndex(e => e.type === 'issue' && e.text.includes('UE-GR002'));
assert.equal(full[warnIdx].kind, 'warning');
assert.equal(full[warnIdx].text,
  bannerText('warning', 'UE-GR002', 'grammar', 'deterministic', 12, 5));

// D12, the claim itself: the same finding built as a single uncapped row and
// as a one-member group must carry every one of the row's fields identically.
// Written as a comparison rather than two independent readings, because a
// shared mistake would pass two readings but not a field-by-field diff.
{
  const one = finding({ file: 'a.md', line: 4, column: 9, ruleId: 'UE-RE005' });
  const uncapped = buildReportFull(makeInput({ findings: [one] }));
  const sole = uncapped[uncapped.findIndex(e => e.type === 'issue' && e.text.includes('UE-RE005'))];
  const groupedReport = buildReport(makeInput({ findings: [one] }));
  const twin = groupedReport[groupedReport.findIndex(e => e.type === 'issue'
    && e.text.includes('UE-RE005'))];
  assert(twin, 'the same finding also renders as a grouped row');
  assert.deepEqual(Object.keys(sole), Object.keys(twin),
    'both detail modes build the row from the same set of fields');
  for (const key of Object.keys(sole)) {
    assert.deepEqual(sole[key], twin[key],
      `field "${key}" differs between the uncapped row and the grouped row`);
  }
}

// info and unknown severities render as notes
const odd = buildReportFull(makeInput({ findings: [
  finding({ line: 1, severity: 'info' }),
  finding({ line: 2, severity: 'fatal' }),
] }));
const oddBanners = bannersFrom(odd, headingIndex(odd, 'Findings by file'));
assert.equal(oddBanners[0].kind, 'note');
assert(oddBanners[0].text.startsWith('[NOTE]'), 'info severity renders as a note');
assert.equal(oddBanners[1].kind, 'note');
assert(oddBanners[1].text.startsWith('[NOTE]'), 'unknown severity falls back to a note');

// --- should-be fallback: proposed ?? suggestion ?? message, and markers -----

const fallback = buildReportFull(makeInput({ findings: [
  finding({ line: 1, proposed: 'Propose one.', suggestion: 'Suggest one.', message: 'Message one.' }),
  finding({ line: 2, proposed: null, suggestion: 'Suggest two.', message: 'Message two.' }),
  finding({ line: 3, proposed: null, suggestion: null, message: 'Message three.' }),
  finding({ line: 4, proposed: 'Propose four.', message: 'Message four.', _replacement: 'Replace four.' }),
  finding({ line: 5, proposed: null, suggestion: 'Suggest five.', message: 'Message five.', _replacement: 'Replace five.' }),
  finding({ line: 6, proposed: null, suggestion: null, message: 'Message six.', _replacement: 'Replace six.' }),
] }));
assert.deepEqual(
  fallback.filter(e => e.type === 'issue').map(e => e.should),
  [
    'Propose one.' + MANUAL_SUFFIX,
    'Suggest two.' + MANUAL_SUFFIX,
    'Message three.' + MANUAL_SUFFIX,
    'Propose four.' + FIXABLE_SUFFIX,
    'Suggest five.' + FIXABLE_SUFFIX,
    'Message six.' + FIXABLE_SUFFIX,
  ],
  'proposed wins, then suggestion, then message; _replacement drives the marker',
);

// --- heuristic paragraph and the Agent Review Required section ---------------
//
// The block that used to sit here was "Review queue (heuristic findings)": a
// one-line-per-finding index whose only job was that a reviewer could not
// miss a heuristic finding. D5 gives that job to the Agent Review Required
// section, which prints whole issue blocks instead of an excerpt, and D6
// numbers nothing. These locks moved with it: the guarantee they hold now is
// the stronger one — every heuristic finding is present, at full length.

const det = buildReportFull(makeInput());
assert(!det.some(e => e.type === 'heading' && e.text === 'Agent Review Required'),
  'the agent review section is not drawn in the legacy per-file layout');

// Grouped, every heuristic finding that actually belongs to the
// heuristic-review lane lands in the section, whole — and a heuristic finding
// in another lane stays in that lane's section instead. (Lane choice is by
// category and audit first, so a heuristic hate-speech finding is a harmful
// finding, not an agent-review one.)
const agentFixture = makeInput({ findings: [
  finding({ ruleId: 'UE-GR002', category: 'grammar', severity: 'warning',
    confidence: 'heuristic', message: LONG_MESSAGE, line: 3, column: 7 }),
  finding({ ruleId: 'UE-SP001', category: 'spelling', severity: 'warning',
    confidence: 'heuristic', message: 'A short heuristic signal.', file: 'index.html',
    line: 9, column: 2 }),
  finding({ ruleId: 'UE-HS002', category: 'hate-speech', severity: 'error',
    confidence: 'heuristic', message: 'A harmful finding routed elsewhere.', line: 1, column: 1 }),
] });
const groupedFixture = buildReport(agentFixture);
const iAgent = headingIndex(groupedFixture, 'Agent Review Required');
const agentBlock = [];
for (const element of groupedFixture.slice(iAgent + 1)) {
  if (element.type === 'spacer') break;
  agentBlock.push(element);
}
const agentMessages = agentBlock
  .filter(element => element.type === 'issue')
  .map(element => element.message);
assert.equal(groupedFixture[iAgent].count, '2 findings',
  'the section counts the findings of its own lane only');
assert.equal(agentMessages.length, 2, 'both lane findings are in the section');
assert(agentMessages.includes(LONG_MESSAGE),
  'a heuristic finding prints its whole message here, where the old queue cut it at 80 characters');
assert(!agentMessages.includes('A harmful finding routed elsewhere.'),
  'a heuristic finding of another lane stays in that lane, not here');
assert(!det.some(e => e.type === 'issue' && e.heuristic),
  'no routed-to-review flag on deterministic findings');
assert.equal(
  full.filter(e => e.type === 'issue' && e.heuristic).length,
  2,
  'routed to review once per heuristic finding, audits included',
);

// --- audit findings live under Audits ---------------------------------------

const auditIdx = full.findIndex(e => e.type === 'issue' && e.text.includes('UE-EO001'));
const auditRow = full[auditIdx];
assert.equal(auditRow.kind, 'warning');
assert.equal(auditRow.text,
  bannerText('warning', 'UE-EO001', 'publishing', 'deterministic', 1, 1));
assert.equal(auditRow.current, '(not applicable)');
assert.equal(auditRow.audit, 'publishing', 'audit block keeps its Audit row');
assertLaneBlock(full, auditIdx);

const heuristicAuditIdx = full.findIndex(e => e.type === 'issue' && e.text.includes('UE-AX001'));
assert.equal(full[heuristicAuditIdx].audit, 'accessibility');
assert.equal(full[heuristicAuditIdx].heuristic, true,
  'a heuristic audit is routed to review by the same flag every row uses');
assertLaneBlock(full, heuristicAuditIdx);
assert(!det.some(e => e.type === 'kv' && e.label === 'Audits'), 'no audit row without audits');

// --- sources appendix -------------------------------------------------------

assert(!det.some(e => e.type === 'heading' && e.text === 'Sources'), 'no sources heading without sources');
// The only bullet list a report without sources may carry is the priority
// recommendations, and it must be the last thing in the document.
assert.equal(det[det.length - 2].type, 'heading', 'a report with no sources ends on a heading');
assert.equal(det[det.length - 2].text, 'Priority Recommendations',
  'the closing heading without sources is the recommendations');
assert.equal(det[det.length - 1].type, 'bullets', 'its recommendations are the last element');
assert.deepEqual(full[full.length - 1], { type: 'bullets', items: fullSources }, 'sources render as bullets');
assert.equal(iSourcesHeading, full.length - 2, 'sources heading directly before the bullets');
assert.notEqual(full[full.length - 1].items, fullSources, 'bullets items are a fresh array');

// --- priority recommendations derive from this scan only ---------------------

// The heading carries `derived from the findings above`, and the documentation
// makes the stronger promise: the section cannot advise a reader about
// anything the scan did not find. Both are checked against the findings
// themselves — every rule id it names must have fired, every count must be
// the count of those findings, a lane with nothing in it draws no line for
// that lane, and quoted material drives nothing at all. A template carried in
// from somewhere else would satisfy the heading and fail here.
{
  const recsOf = (report) => {
    const last = report[report.length - 1];
    assert.equal(last.type, 'bullets', 'the report closes on the recommendations');
    return last.items;
  };

  const plain = recsOf(buildReportFull(makeInput({ findings: [
    finding({ ruleId: 'UE-SP001', category: 'spelling', line: 1, column: 1 }),
    finding({ ruleId: 'UE-SP001', category: 'spelling', line: 2, column: 1 }),
    finding({ ruleId: 'UE-GR002', category: 'grammar', line: 3, column: 1 }),
  ] })));
  assert(!plain.some(t => /harmful or discriminatory/i.test(t)),
    'no harmful-discriminatory line when the scan found no harmful wording');
  assert(!plain.some(t => t.startsWith('Review the ')),
    'no diplomatic line when the scan found no diplomatic claim');
  assert.equal(plain.length, 2, 'one line per rule that fired');
  assert(plain[0].startsWith('UE-SP001 fires 2 times'),
    'the stated count is the count of the findings, ordered by that count');
  assert(plain[1].startsWith('UE-GR002 fires 1 time'), 'a rule that fired once is singular');
  for (const item of plain) {
    for (const ruleId of item.match(/UE-[A-Z]{2}\d{3}/g) ?? []) {
      assert(['UE-SP001', 'UE-GR002'].includes(ruleId),
        `the recommendations name ${ruleId}, which this scan did not fire`);
    }
  }

  const lanes = recsOf(buildReportFull(makeInput({ findings: [
    finding({ ruleId: 'UE-HS001', category: 'hate-speech', severity: 'error',
      lane: 'harmful-discriminatory', line: 1, column: 1 }),
    finding({ ruleId: 'UE-HS001', category: 'hate-speech', severity: 'error',
      lane: 'harmful-discriminatory', line: 2, column: 1 }),
    finding({ ruleId: 'UE-DP001', category: 'diplomacy', lane: 'diplomacy',
      line: 3, column: 1 }),
    finding({ ruleId: 'UE-SP001', category: 'spelling', line: 4, column: 1 }),
  ] })));
  assert(lanes.some(t => t.startsWith('Address the 2 harmful or discriminatory findings first.')),
    'the harmful line states the number of harmful findings');
  assert(lanes.some(t => t.startsWith('Review the 1 diplomatic claim.')),
    'the diplomatic line states the number of diplomatic claims');
  assert(lanes.some(t => t.startsWith('UE-HS001 fires 2 times')),
    'lane findings are counted in the ranking as well');

  // Quoted material is a context, not copy the reader wrote: it drives nothing.
  const quoted = recsOf(buildReportFull(makeInput({ findings: [
    finding({ ruleId: 'UE-DM001', category: 'discriminatory', severity: 'error',
      lane: 'harmful-discriminatory', context: 'quoted', line: 1, column: 1 }),
    finding({ ruleId: 'UE-SP001', category: 'spelling', line: 2, column: 1 }),
  ] })));
  assert(!quoted.some(t => t.includes('UE-DM001')),
    'a rule that fired only inside a quotation drives no recommendation');
  assert(!quoted.some(t => /harmful or discriminatory/i.test(t)),
    'quoted material is not counted as harmful copy');

  // A short list, not the whole catalogue: six at most, ties broken
  // deterministically so two runs over one input read the same.
  const many = recsOf(buildReportFull(makeInput({ findings:
    ['UE-SP001', 'UE-GR001', 'UE-GR002', 'UE-NU002', 'UE-TE001', 'UE-RG001', 'UE-TE003', 'UE-TE002']
      .map((ruleId, index) => finding({ ruleId, line: index + 1, column: 1 })) })));
  assert.equal(many.length, 6, 'the ranking names at most the six rules that fired most');
}

// --- empty scan -------------------------------------------------------------

const empty = buildReportFull(makeInput({ findings: [] }));
// D5's first two sections are structural, not a claim about what was found,
// so they are drawn even at zero — a clean scan reports its zero count in the
// same shape as a dirty one. No findings section is drawn: there is no lane
// to say was checked when the scan found nothing, and the clean sentence
// already states that every enabled, documented rule ran.
assert.deepEqual(
  empty.filter(e => e.type === 'heading').map(e => e.text),
  ['Summary', 'Categories'],
  'an empty scan renders Summary and Categories and no findings section',
);
const noFindingsIdx = empty.findIndex(e => e.type === 'paragraph' && e.text === 'No findings.');
assert(noFindingsIdx >= 0, 'empty scan says No findings.');
const emptyLegend3 = empty.findIndex(e => e.type === 'paragraph' && e.text.includes('changes nothing'));
assert.equal(noFindingsIdx, emptyLegend3 + 3,
  'No findings. follows the Categories heading, which follows the promises');
assert(paragraphTexts(empty).includes('0 errors · 0 warnings · 0 notes'), 'zero counts on an empty scan');
assert.deepEqual(empty[0], { type: 'banner', kind: 'title', text: 'Editorial Review Report' });

const emptyWithSources = buildReportFull(makeInput({ findings: [], sources: ['House style guide, chapter 4'] }));
const emptyNoteIdx = emptyWithSources.findIndex(e => e.type === 'paragraph' && e.text === 'No findings.');
assert(emptyNoteIdx >= 0 && emptyNoteIdx < headingIndex(emptyWithSources, 'Sources'),
  'empty note precedes the sources appendix');

// --- sorting: line then column inside a file --------------------------------

const sorted = buildReportFull(makeInput({ findings: [
  finding({ line: 10, column: 1, ruleId: 'UE-GR001' }),
  finding({ line: 3, column: 9, ruleId: 'UE-GR002' }),
  finding({ line: 3, column: 2, ruleId: 'UE-TE003' }),
] }));
const positions = bannersFrom(sorted, headingIndex(sorted, 'Findings by file'))
  .map(e => e.text.match(/line (\d+):(\d+)/))
  .map(match => [Number(match[1]), Number(match[2])]);
assert.deepEqual(positions, [[3, 2], [3, 9], [10, 1]], 'findings sorted by line then column');

// --- grouping: one heading per file, first-appearance order -----------------

const interleaved = [
  finding({ file: 'b.md', line: 2, column: 4, ruleId: 'UE-SP001' }),
  finding({ file: 'a.md', line: 5, column: 3, ruleId: 'UE-GR001' }),
  finding({ file: 'b.md', line: 1, column: 1, ruleId: 'UE-TE003' }),
  finding({ file: 'a.md', line: 1, column: 6, ruleId: 'UE-GR002' }),
];
const grouped = buildReportFull(makeInput({ findings: interleaved }));
assert.deepEqual(
  grouped.filter(e => e.type === 'heading' && e.level === 2).map(e => e.text),
  ['b.md', 'a.md'],
  'files grouped under one heading each, first appearance order',
);
const bIdx = headingIndex(grouped, 'b.md');
const aIdx = headingIndex(grouped, 'a.md');
assert(bIdx < aIdx, 'file groups never interleave');
const bGroupBanners = grouped.slice(bIdx + 1, aIdx).filter(e => e.type === 'issue');
assert.equal(bGroupBanners.length, 2, 'both b.md findings sit inside the b.md group');
assert(bGroupBanners.every(e => e.text.includes('UE-SP001') || e.text.includes('UE-TE003')),
  'the b.md group holds only b.md findings');
assert.deepEqual(
  grouped.slice(aIdx + 1).filter(e => e.type === 'issue').map(e => e.text.match(/UE-[A-Z]+\d+/)[0]),
  ['UE-GR002', 'UE-GR001'],
  'a.md findings sorted by line inside their group',
);

// --- determinism and purity -------------------------------------------------

const sample = { profiles: ['publishing'], findings: interleaved, sources: fullSources };
const one = buildReportFull(makeInput(sample));
const two = buildReportFull(makeInput(sample));
assert.deepEqual(one, two, 'same input yields deeply equal output');
const copy = buildReportFull(JSON.parse(JSON.stringify(makeInput(sample))));
assert.deepEqual(one, copy, 'output depends only on input data');

const frozen = deepFreeze(makeInput(sample));
const snapshot = JSON.parse(JSON.stringify(frozen));
const fromFrozen = buildReportFull(frozen);
assert.deepEqual(JSON.parse(JSON.stringify(frozen)), snapshot, 'input findings are never mutated');
assert.deepEqual(fromFrozen, one, 'a deep-frozen input renders identically');
assertElements(fromFrozen, 'frozen-run output stays inside the union');

// --- Wave 3 lanes: counts, lane rows, quoted material -----------------------

// The lane counts sit directly after the severity counts, and only on a
// non-empty scan. full holds two deterministic findings, one harmful-
// discriminatory (HS002), two audits and nothing quoted.
const lanesIdx = full.findIndex(e => e.type === 'paragraph' && e.text.startsWith('lanes:'));
assert.equal(lanesIdx, iCounts + 1, 'lane counts follow the severity counts');
assert.equal(full[lanesIdx].text,
  'lanes: deterministic 2 · heuristic-review 0 · harmful-discriminatory 1 · diplomacy 0 · audit 2 · quoted 0',
  'lane counts name all five lanes plus quoted');
assert(!empty.some(e => e.type === 'paragraph' && e.text.startsWith('lanes:')),
  'no lane counts on an empty scan');

// D12: a row carries its provenance inside itself, so the lane values are
// read from the row rather than by walking sibling elements — which also means
// a lane row cannot be "found" at a fixed offset into the next block.
function provenanceValue(row, label) {
  const pair = row.provenance.find(p => p.label === label);
  assert(pair, `row carries no ${label} provenance field`);
  return pair.value;
}

// HS002 sits in the harmful-discriminatory lane: high-severity human review,
// never auto-rewritten, sourced to its guard note.
assert.equal(provenanceValue(full[hsIdx], 'Lane'), 'harmful-discriminatory');
assert.equal(provenanceValue(full[hsIdx], 'Source'), 'rules/hate-speech.md');
assert.equal(provenanceValue(full[hsIdx], 'Profile'), 'editorial baseline');
assert.match(provenanceValue(full[hsIdx], 'Action'), /High-severity human review/,
  'the action routes the reader to high-severity review');

// Audit findings carry the audit lane, their profile file as source and the
// audit name as profile.
assert.equal(provenanceValue(full[auditIdx], 'Lane'), 'audit');
assert.equal(provenanceValue(full[auditIdx], 'Source'), 'config/profiles/publishing.json');
assert.equal(provenanceValue(full[auditIdx], 'Profile'), 'publishing');

// The deterministic lane keeps its rule file as source.
assert.equal(provenanceValue(full[errIdx], 'Lane'), 'deterministic');
assert.equal(provenanceValue(full[errIdx], 'Source'), 'rules/register.md');

// Quoted material: reported separately, never skipped. A quoted finding
// leaves the file groups, keeps its lane rows, counts as quoted rather than
// as its lane, and a quoted heuristic never enters the Agent Review Required
// section.
const quotedReport = buildReportFull(makeInput({ findings: [
  finding({ file: 'docs/quote.md', line: 2, column: 1, ruleId: 'UE-SP001',
    category: 'spelling', severity: 'error', context: 'quoted',
    current: '"organisation"', message: 'Spelling preference.' }),
  finding({ file: 'docs/quote.md', line: 5, column: 1, ruleId: 'UE-HS002',
    category: 'hate-speech', severity: 'error', confidence: 'heuristic',
    context: 'quoted', message: LONG_MESSAGE }),
  finding({ file: 'docs/quote.md', line: 9, column: 1, ruleId: 'UE-GR002',
    category: 'grammar', severity: 'warning', message: 'Authored copy finding.' }),
] }));
const quotedHeading = headingIndex(quotedReport, 'Quoted material');
assert.equal(quotedReport[quotedHeading].count, '2 findings',
  'the quoted section states its own count beside the title');
const quoteFileIdx = headingIndex(quotedReport, 'docs/quote.md');
assert.deepEqual(
  quotedReport.slice(quoteFileIdx + 1, quotedHeading - 1)
    .filter(e => e.type === 'issue').map(e => e.text.match(/UE-[A-Z]+\d+/)[0]),
  ['UE-GR002'],
  'quoted findings leave the file group; only authored copy stays',
);
const quotedBanners = quotedReport.slice(quotedHeading + 1).filter(e => e.type === 'issue');
assert.deepEqual(quotedBanners.map(e => e.text.match(/UE-[A-Z]+\d+/)[0]),
  ['UE-SP001', 'UE-HS002'], 'the quoted section holds both quoted findings in input order');
assertLaneBlock(quotedReport, quotedReport.indexOf(quotedBanners[0]),
  'quoted blocks carry their lane rows too');
assert.match(
  quotedReport.find(e => e.type === 'paragraph' && e.text.startsWith('lanes:')).text,
  /deterministic 1 · heuristic-review 0 · harmful-discriminatory 0 · diplomacy 0 · audit 0 · quoted 2/,
  'quoted findings count as quoted, not as their lane',
);
// Same fixture, grouped: the quoted heuristic must not be counted into the
// Agent Review Required section. The section still draws (a lane that was
// checked says so, D10), but it claims zero findings rather than borrowing
// one from a quotation.
const groupedQuoted = buildReport(makeInput({ findings: [
  finding({ file: 'docs/quote.md', line: 2, column: 1, ruleId: 'UE-SP001',
    category: 'spelling', severity: 'error', context: 'quoted',
    current: '"organisation"', message: 'Spelling preference.' }),
  finding({ file: 'docs/quote.md', line: 5, column: 1, ruleId: 'UE-HS002',
    category: 'hate-speech', severity: 'error', confidence: 'heuristic',
    context: 'quoted', message: LONG_MESSAGE }),
  finding({ file: 'docs/quote.md', line: 9, column: 1, ruleId: 'UE-GR002',
    category: 'grammar', severity: 'warning', message: 'Authored copy finding.' }),
] }));
const iGroupedAgent = headingIndex(groupedQuoted, 'Agent Review Required');
assert.equal(groupedQuoted[iGroupedAgent].count, '0 findings',
  'a quoted heuristic stays out of the Agent Review Required section');

// --- 11: the grouped default ------------------------------------------------
//
// PHASE-9-PLAN §8 asks for this section explicitly: the suite used to assert
// one block per finding, and it must now assert the grouping and that
// provenance survives summarising. The layout assertions above were pointed at
// `full`, not deleted — they still describe the report `--report-detail full`
// renders, and they still fail if that report regresses.

{
  // Three findings that are the same issue in every way but where they were
  // found, then one that differs in advice, one in its explanation, and one in
  // the text it found. Six findings, four issues.
  const same = (over) => finding({
    line: 12, column: 5, current: 'The the', message: 'Doubled word.',
    proposed: 'The', _replacement: 'The',
    excerpt: 'The »the« report was short.', ...over,
  });
  const input = makeInput({ findings: [
    same({}),
    same({ line: 48, column: 1 }),
    same({ file: 'docs/other.md', line: 3, column: 2 }),
    same({ line: 60, proposed: 'The one.', _replacement: 'The one.' }),
    same({ line: 70, message: 'A different explanation.' }),
    finding({ line: 80, current: 'is is', message: 'Doubled word.',
      proposed: 'The', _replacement: 'The' }),
  ] });

  // Captured before a single buildReport runs: everything below renders from
  // this object, and the check at the end of the block is only worth something
  // if nothing has touched it yet.
  const pristine = JSON.parse(JSON.stringify(input));

  const grouped = buildReport(input);
  const full = buildReportFull(input);
  assertElements(grouped, 'the grouped default stays inside the union');
  // D12 removed the second implementation of the finding block, so what
  // distinguishes the two layouts is no longer *what* draws a row but *how
  // many rows* there are. Both halves are asserted — six rows against four,
  // and one occurrence per row against a group of three — so "the layouts
  // still differ" cannot be satisfied by two arrays that merely are not the
  // same object.
  assert.equal(
    full.filter(e => e.type === 'issue').length, 6,
    'the uncapped layout draws one shared row per finding: six rows for six findings',
  );
  assert.equal(
    grouped.filter(e => e.type === 'issue').length, 4,
    'the grouped layout merges them: four rows for six findings',
  );
  assert.notDeepEqual(
    full.filter(e => e.type === 'issue').map(e => e.count),
    grouped.filter(e => e.type === 'issue').map(e => e.count),
    'the two layouts group differently, row by row',
  );

  const issues = grouped.filter(e => e.type === 'issue');
  assert.equal(issues.length, 4, 'six findings collapse to four issues');
  const occurrences = issues.reduce((n, issue) => n + issue.occurrences.length, 0);
  assert.equal(occurrences, 6, 'every finding is still accounted for as an occurrence');

  // `file` is not part of an issue's identity: one defect in two files is one
  // issue, and the occurrence table carries each file.
  assert.equal(issues[0].count, 3, 'the three alike findings are one issue');
  assert.deepEqual(
    issues[0].occurrences.map(o => `${o.file}:${o.line}:${o.column}`),
    ['docs/page.md:12:5', 'docs/page.md:48:1', 'docs/other.md:3:2'],
    'occurrences keep their own file, line and column, in position order',
  );

  // Differences that make two findings unlike stay separate rather than being
  // silently summarised together.
  assert.equal(issues[1].should, 'The one.' + FIXABLE_SUFFIX,
    'different advice is a different issue');
  assert.equal(issues[2].message, 'A different explanation.',
    'different explanations are different issues');
  assert.equal(issues[3].current, 'is is', 'different defective text is a different issue');

  // The six provenance fields survive summarising on every issue, whatever its
  // size — this is the property that makes summarising honest at all.
  const SIX = ['Lane', 'Source', 'Profile', 'Confidence', 'Limitation', 'Action'];
  for (const issue of issues) {
    assert.deepEqual(issue.provenance.map(p => p.label), SIX,
      `issue ${issue.ruleId} carries all six provenance fields in order`);
    for (const row of issue.provenance) {
      assert.equal(typeof row.value, 'string');
      assert.ok(row.value.length > 0 || row.label === 'Limitation',
        `provenance row ${row.label} has a value`);
    }
  }

  // A count is shown only when it is more than one.
  for (const issue of issues) {
    const located = issue.text.includes('· line ');
    assert.equal(located, issue.count === 1,
      `issue with count ${issue.count} ${located ? 'names' : 'omits'} its line`);
  }

  // Content comes from the scan-time excerpt, and falls back to the matched
  // token when a finding carries no excerpt — never to nothing.
  assert.equal(issues[0].occurrences[0].content, 'The »the« report was short.',
    'the occurrence shows the excerpt captured at scan time');
  assert.ok(issues[3].occurrences[0].content,
    'a finding with no excerpt still shows the copy it matched');

  // Grouping is presentation. Both layouts compute the counts from the
  // findings before either runs, so they cannot disagree.
  const countsOf = (report) =>
    report.find(e => e.type === 'paragraph' && /\d+ errors · \d+ warnings · \d+ notes/.test(e.text)).text;
  const lanesOf = (report) =>
    report.find(e => e.type === 'paragraph' && e.text.startsWith('lanes:')).text;
  assert.equal(countsOf(grouped), countsOf(full),
    'grouping does not change the severity counts');
  assert.equal(lanesOf(grouped), lanesOf(full),
    'grouping does not change the lane counts');

  // Purity holds for the default layout too, not only for `full`.
  const one = buildReport(input);
  const two = buildReport(input);
  assert.deepEqual(one, two, 'identical input gives identical grouped output');
  const deep = JSON.parse(JSON.stringify(input));
  assert.deepEqual(buildReport(deep), one, 'a decoded copy renders the same');
  const frozen = JSON.parse(JSON.stringify(input));
  Object.freeze(frozen);
  for (const item of frozen.findings) Object.freeze(item);
  assert.deepEqual(buildReport(frozen), one, 'a frozen input renders like a fresh one');
  assert.deepEqual(input, pristine,
    'buildReport does not mutate the findings it was given');
}

// --- 11b: the cap is presentation, never arithmetic (D7–D8, D13) ------------
//
// A capped section may withhold findings from the body. It may never withhold
// them from the arithmetic. Three properties are locked together here,
// because each one alone can look fine while the report is lying:
//
//   1. the cap stops on a whole group — the drawn occurrences must add up to
//      exactly the number the cap says it showed;
//   2. the section's own heading still states the full count, so a reader who
//      skips the cap block is not told the section has 17 findings when the
//      scan found 41;
//   3. `full`, which is never capped, reports the same findings under the
//      same severity counts and the same lane counts.
//
// The fixture is deliberately not divisible by 20: four groups of 5, 12, 18
// and 6 warnings. A group of 18 cannot be drawn once the body already holds
// 17, so the drawn total lands on 17 rather than on 20 by coincidence — if
// the cap ever split a group to hit a round number, assertion 1 fails.

{
  const CAP_COMMAND = 'un-editorial-check docs --report-detail full --report docs.pdf';
  const groups = [
    ['UE-GR001', 5], ['UE-GR002', 12], ['UE-SP001', 18], ['UE-NU001', 6],
  ];
  const findings = [];
  let line = 1;
  for (const [ruleId, size] of groups) {
    for (let n = 0; n < size; n += 1) {
      findings.push(finding({ ruleId, line, column: 1 }));
      line += 1;
    }
  }
  assert.equal(findings.length, 41, 'the cap fixture is exactly forty-one warnings');

  // The elements of one section: heading up to the spacer that opens the next.
  const sectionOf = (report, title) => {
    const at = report.findIndex(e => e.type === 'heading' && e.text === title);
    assert(at > 0, `the ${title} section is present`);
    const rest = report.slice(at + 1);
    const stop = rest.findIndex(e => e.type === 'spacer');
    return stop < 0 ? rest : rest.slice(0, stop);
  };

  const capped = buildReport(makeInput({ findings }), { command: CAP_COMMAND });
  const plain = buildReportFull(makeInput({ findings }));

  // (1) The cap element, and the arithmetic behind it.
  const caps = capped.filter(e => e.type === 'cap');
  assert.equal(caps.length, 1, 'exactly one section crosses the cap');
  assert.deepEqual(caps[0], { type: 'cap', shown: 17, total: 41, command: CAP_COMMAND },
    'the cap reports how much it drew, how much exists, and the command that lists the rest');
  assert.deepEqual(capLines(caps[0]), [
    'Showing 17 of 41 · 24 not listed above.',
    "Nothing is discarded. All 41 are in this run's JSON and SARIF output,"
      + ' and every one of them can be listed here by re-running the same scan with:',
    CAP_COMMAND,
  ], 'the cap line names both the count withheld and the exact re-run command');
  assert(!capLines(caps[0])[0].includes('20 of 41'),
    'a group is never split to reach a round number: the drawn total is 17, not 20');

  const warnings = sectionOf(capped, 'Editorial Warnings');
  const drawn = warnings.filter(e => e.type === 'issue');
  assert.equal(drawn.length, 2, 'two whole groups were drawn');
  assert.equal(drawn.reduce((n, issue) => n + issue.occurrences.length, 0), caps[0].shown,
    'the occurrences actually drawn add up to exactly the number the cap claims to have shown');
  assert.deepEqual(drawn.map(issue => issue.occurrences.length), [5, 12],
    'both groups are drawn whole, in order');

  // (2) The heading states the whole count, not the drawn count. `full` has no
  // lane sections — it hangs its body off Findings by file — so that is the
  // heading whose count is checked there.
  const heading = (report, title) => report.find(e => e.type === 'heading' && e.text === title);
  assert.equal(heading(capped, 'Editorial Warnings').count, '41 findings',
    'the capped section still claims all forty-one findings');
  assert.equal(heading(plain, 'Findings by file').count, '41 findings',
    'the uncapped layout claims the same forty-one');
  assert.equal(heading(plain, 'Editorial Warnings'), undefined,
    'the uncapped layout draws no lane sections at all');

  // (3) Nothing downstream changes: the summary and the lanes are computed
  // from the findings before either layout runs, so a cap cannot reach them.
  const countsOf = (report) =>
    report.find(e => e.type === 'paragraph' && /\d+ errors · \d+ warnings · \d+ notes/.test(e.text)).text;
  const lanesOf = (report) =>
    report.find(e => e.type === 'paragraph' && e.text.startsWith('lanes:')).text;
  assert.equal(countsOf(capped), countsOf(plain),
    'a cap never changes the severity counts');
  assert.equal(countsOf(capped), '0 errors · 41 warnings · 0 notes',
    'and those counts are every finding of the scan, not the drawn subset');
  assert.equal(lanesOf(capped), lanesOf(plain),
    'a cap never changes the lane counts');
  assert.equal(lanesOf(capped),
    'lanes: deterministic 41 · heuristic-review 0 · harmful-discriminatory 0'
      + ' · diplomacy 0 · audit 0 · quoted 0',
    'the lane line counts all forty-one findings');

  // `full` is never capped, and prints no cap block at all: every finding is
  // its own row (D12), so there is no group to cut in the first place. Both
  // halves are asserted — the row count and that each row holds exactly one
  // occurrence — because "one block per finding" fails just as loudly if the
  // rows were merged into groups as if the findings were dropped.
  assert(!plain.some(e => e.type === 'cap'),
    'the uncapped layout draws no cap block');
  assert.equal(
    plain.filter(e => e.type === 'issue').length, 41,
    'the uncapped layout is one shared row per finding, and still draws all forty-one',
  );
  assert.equal(
    plain.reduce((n, e) => n + (e.type === 'issue' ? e.occurrences.length : 0), 0),
    41, 'and each of those rows holds exactly its own single occurrence',
  );

  // A section whose one group is too large to split takes that group whole and
  // withholds nothing, so it is not capped: no cap block, and no demand for a
  // re-run command. A record announcing "0 not listed above" would state
  // nothing that a reader needs.
  const oneGroup = makeInput({
    findings: Array.from({ length: 25 }, (_, i) =>
      finding({ ruleId: 'UE-GR003', line: i + 1, column: 1 })),
  });
  const whole = buildReport(oneGroup, { command: CAP_COMMAND });
  const wholeSection = sectionOf(whole, 'Editorial Warnings');
  assert.equal(wholeSection.filter(e => e.type === 'issue').length, 1,
    'the one group too large to split is drawn whole');
  assert.equal(
    wholeSection.reduce((n, e) => n + (e.type === 'issue' ? e.occurrences.length : 0), 0),
    25, 'and nothing is withheld from it');
  assert(!whole.some(e => e.type === 'cap'),
    'a section that withheld nothing prints no cap block');
  assert.equal(heading(whole, 'Editorial Warnings').count, '25 findings',
    'it still claims its full count');
  // The same build with no command at all must also succeed: nothing is being
  // capped here, so nothing may demand a re-run command.
  assert.doesNotThrow(() => buildReport(oneGroup),
    'a section that withholds nothing needs no re-run command');

  // Refuse rather than guess: a cap with no command is a promise the report
  // cannot keep, so the body does not build. The case above builds without one
  // precisely because it caps nothing.
  assert.throws(
    () => buildReport(makeInput({ findings })),
    /capped report body needs the re-run command/,
    'a capped section without a runnable command refuses to render',
  );
}

console.log('ok — report model: union, D5 order without numbers, blocks, should-be, agent review section, audits, sources, empty, sorting, purity, lanes, quoted, grouped issues with provenance and presentation-only counts, and a cap that withholds bodies but never arithmetic');
