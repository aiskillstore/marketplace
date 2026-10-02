// Wave 4 (Agent C) contract: the UE-HR001..UE-HR005 review heuristics.
//
//   1. catalogue + registry contract — five entries with the exact ten-key
//      schema, review-only severity (warning, never error), heuristic
//      confidence, agent-review category, profile null, appended straight
//      after UE-GR003, honest limitation text and no invented sources;
//   2. UE-HR001 sentence-like fragment — fires on a verbless 5-8 word
//      sentence in authored prose only, on the first offending sentence of
//      a unit, and stays silent behind every documented gate (verb signal,
//      comma, parentheses, abbreviation tail, word count, repetition,
//      heading / list / nav / compact);
//   3. UE-HR002 malformed wording — tight collocations only, never the
//      idiomatic "would of course", report-only with a suggestion and no
//      replacement, silent on code-context units;
//   4. UE-HR003 duplication in two forms — a repeated 4+ word sentence inside
//      one block, and a long authored block repeated verbatim later in the same
//      file; section 4b covers the second form, its twenty-word threshold from
//      both sides, and every context where a long repeat is legitimate;
//   4b. the cross-block form — a nine-row fixture matrix, the exact shape of a
//      positive finding, eight quiet contexts, and the no-replacement,
//      exit-code, config, suppression, determinism and per-file boundaries;
//   4c. the cross-block form across a split paragraph — a duplicated paragraph
//      whose second copy inline markup broke into sub-floor units, which the
//      unit-at-a-time comparison could not see; the floor from both sides across
//      a split, the quiet surfaces still quiet across one, the suppression
//      interaction, and the block fields the reassembly reads;
//   4e. the two edge defects in the reassembly — an open block keyed on a
//      source offset alone, which made a repeat visible or not depending on what
//      else was in the scan, and a fixed-space join, which split a word an inline
//      element had broken in half; directory scans, five elements, and the seam
//      read the way a reader reads it;
//   4d. what the note promises, and only that — a standing disclaimer repeated
//      in one file is reported, navigation copy is not, the per-file key holds
//      in both directions, and the shipped wording in rules/catalogue.json and
//      rules/grammar.md is asserted so the note cannot drift from the code;
//   5. UE-HR004 incoherent heading — heading units ending in . or ; only;
//   6. UE-HR005 broken quotation — a surviving unpaired quote mark, with
//      paired quotes, apostrophes, code and compact units all silent;
//   7. fixture contract — every positive HR fixture exits 0 (review-only)
//      and fires exactly its one rule, and expected.json agrees;
//   8. fix boundary + disable — no HR id is ever in FIXABLE_RULE_IDS,
//      `--fix --apply` leaves a file containing all five findings byte
//      identical, config.rules enabled:false and ue:ignore both silence.
//
// The duplicated-insertion defect this suite now covers: the same paragraph
// inserted twice ten lines apart in .feedbacks/v8/web/01 (Omar's P0). It sat
// in two separate units, so the per-block sentence form could not see it.
//
// TDD: written before the heuristic section landed in lib/rules.mjs.
// Standalone: node tests/audit-heuristics.mjs
// Prose in this file stays single-quoted: the repository self-scan extracts
// double-quoted sentence-like literals from .mjs sources, and this suite
// must not depend on that machinery to stay clean.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run, CATALOGUE } from '../bin/check.mjs';
import { EDITORIAL_RULES } from '../lib/rules.mjs';
import { FIXABLE_RULE_IDS } from '../lib/fix.mjs';
import { extractFile } from '../lib/extract.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-heuristics-'));

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
const scan = (file) => {
  const result = capture([file, '--format', 'json']);
  assert.notEqual(result.code, 2, `scan failed for ${file}: ${result.stderr}`);
  return JSON.parse(result.stdout).findings;
};
const hrOnly = (file) => scan(file).filter(f => f.ruleId.startsWith('UE-HR'));
const hrIds = (file) => hrOnly(file).map(f => f.ruleId);
const fixture = (name) => path.join(root, 'tests', 'fixtures', 'positive', name);

const HR_IDS = ['UE-HR001', 'UE-HR002', 'UE-HR003', 'UE-HR004', 'UE-HR005', 'UE-HR006', 'UE-HR007', 'UE-HR008', 'UE-HR009'];

// --- 1. catalogue and registry contract -------------------------------------

{
  const ids = CATALOGUE.rules.map(rule => rule.id);
  const gr3 = ids.indexOf('UE-GR003');
  assert.notEqual(gr3, -1, 'UE-GR003 must exist to anchor the append point');
  // UE-GR004 extends the grammar block immediately after its siblings; the
  // five heuristic entries follow the whole grammar family, in order.
  const afterGrammar = ids.indexOf('UE-HR001');
  assert.deepEqual(ids.slice(gr3 + 1, afterGrammar), ['UE-GR004'],
    'UE-GR004 must complete the grammar block before the heuristics begin');
  assert.deepEqual(ids.slice(afterGrammar, afterGrammar + HR_IDS.length), HR_IDS,
    'the five heuristic entries must append in order after the grammar block');

  for (const id of HR_IDS) {
    const entry = CATALOGUE.rules.find(rule => rule.id === id);
    assert(entry, `${id} must exist in rules/catalogue.json`);
    assert.deepEqual(Object.keys(entry).sort(), [
      'category', 'confidence', 'extensibility', 'guardNotes', 'id',
      'profile', 'scope', 'severity', 'status', 'summary',
    ], `${id} must carry exactly the ten catalogue keys`);
    // HR007 and the gated consistency notes sit at info; the family stays review-only.
    assert.ok(['warning', 'info'].includes(entry.severity), `${id} must be review-only: warning or info`);
    assert.notEqual(entry.severity, 'error', `${id} must never be error severity`);
    assert.equal(entry.category, 'agent-review', `${id} category`);
    // The gated consistency notes prove their own inconsistency match, so
    // they register as deterministic; the rest of the family is heuristic.
    const expectedConfidence = ['UE-HR008', 'UE-HR009'].includes(id)
      ? 'deterministic' : 'heuristic';
    assert.equal(entry.confidence, expectedConfidence, `${id} confidence`);
    assert.equal(entry.scope, 'user-visible-copy', `${id} scope`);
    // The consistency notes are configuration-gated like UE-GR004.
    const expectedStatus = ['UE-HR008', 'UE-HR009'].includes(id)
      ? 'configuration-gated' : 'deterministic';
    assert.equal(entry.status, expectedStatus, `${id} status`);
    assert.equal(entry.profile, null, `${id} must be profile-independent`);
    // HR006 honours the acronym allowlist and the gated consistency notes
    // their own review switch; the rest of the family extends only through
    // severities and rule switches.
    const expectedExt = id === 'UE-HR006'
      ? 'config.allowlist.acronyms, config.severities, config.rules'
      : ['UE-HR008', 'UE-HR009'].includes(id)
        ? 'config.consistencyReview, config.severities, config.rules'
        : 'config.severities, config.rules';
    assert.equal(entry.extensibility, expectedExt, `${id} extensibility`);
    assert.equal(typeof entry.summary, 'string');
    assert.ok(entry.summary.length > 15, `${id} summary must describe the rule`);
    assert.ok(entry.guardNotes.length > 80, `${id} guardNotes must state the limitations`);
    assert.match(entry.guardNotes, /heuristic|false positive|not a complete/i,
      `${id} guardNotes must carry honest limitation language`);

    const blob = JSON.stringify(entry).toLowerCase();
    for (const banned of ['un approved', 'fully compliant', 'finds all errors',
      'factual verification', 'legal advice']) {
      assert(!blob.includes(banned), `${id} must not contain the banned phrase "${banned}"`);
    }
    assert(!/https?:\/\//.test(blob), `${id} must not invent a source URL`);

    const meta = EDITORIAL_RULES[id];
    assert(meta, `${id} must be registered in EDITORIAL_RULES`);
    // HR007 is an honesty note at info severity; every other family member
    // is a review warning.
    const expectedSeverity = ['UE-HR007', 'UE-HR008', 'UE-HR009'].includes(id) ? 'info' : 'warning';
    assert.equal(meta.severity, expectedSeverity, `${id} registry severity`);
    assert.equal(meta.category, 'agent-review', `${id} registry category`);
    const expectedMetaConfidence = ['UE-HR008', 'UE-HR009'].includes(id)
      ? 'deterministic' : 'heuristic';
    assert.equal(meta.confidence, expectedMetaConfidence, `${id} registry confidence`);
    assert.equal(meta.scope, undefined, `${id} registry entry stays minimal like its neighbours`);
  }
}

// --- 2. UE-HR001 sentence-like fragment --------------------------------------

{
  const fire = scan(write('hr001-fire.txt',
    'The annual report on the situation.\n'));
  const hits = fire.filter(f => f.ruleId === 'UE-HR001');
  assert.equal(hits.length, 1, `UE-HR001 must fire on a verbless sentence, got ${JSON.stringify(fire)}`);
  const hit = hits[0];
  assert.equal(hit.severity, 'warning', 'HR findings are review-only');
  assert.equal(hit.confidence, 'heuristic', 'HR findings are heuristic confidence');
  assert.equal(hit.context, 'authored', 'the fragment came from authored copy');
  assert.equal(typeof hit.suggestion, 'string');
  assert.ok(hit.suggestion.length > 10, 'a fired fragment needs a usable suggestion');
  assert.ok(String(hit.current).includes('annual report'), 'current carries the offending sentence');

  assert.equal(hrIds(write('hr001-fire-md.md',
    'The annual report on the situation.\n'))[0], 'UE-HR001', 'Markdown fires too');

  // First offending sentence only: the unit yields one finding even when a
  // second fireable sentence follows, and it is the first one that reports.
  const two = hrOnly(write('hr001-two.txt',
    'The annual report on the situation. Annual delegation arrival situation briefing today.\n'))
    .filter(f => f.ruleId === 'UE-HR001');
  assert.equal(two.length, 1, `only the first offending sentence may fire, got ${JSON.stringify(two)}`);
  assert.ok(String(two[0].current).startsWith('The annual report'),
    'the first offending sentence is the one that reports');

  // Verb signals suppress: inflected verb, auxiliary, curated base verb.
  for (const [name, text] of [
    ['inflected', 'The delegation meets today.\n'],
    ['auxiliary', 'The plan is ready for review.\n'],
    ['curated', 'Restart OpenCode after installation.\n'],
  ]) {
    assert.deepEqual(hrIds(write(`hr001-verb-${name}.txt`, text)).filter(id => id === 'UE-HR001'), [],
      `${name} verb signal must silence UE-HR001`);
  }

  // Structure gates: headings, list items and navigation are not fragments.
  assert.deepEqual(hrIds(write('hr001-heading.md',
    '# The annual report on the situation.\n')).filter(id => id === 'UE-HR001'), [],
  'a heading unit must never be called a fragment');
  assert.deepEqual(hrIds(write('hr001-list.md',
    '- The annual report on the situation.\n')).filter(id => id === 'UE-HR001'), [],
  'a list item must never be called a fragment');
  assert.deepEqual(hrIds(write('hr001-nav.html',
    '<nav><a href="/x">The annual report on the situation.</a></nav>\n')).filter(id => id === 'UE-HR001'), [],
  'navigation copy must never be called a fragment');

  // Sentence gates: word count, comma, parentheses, abbreviation tail.
  assert.deepEqual(hrIds(write('hr001-short.txt',
    'The annual report.\n')).filter(id => id === 'UE-HR001'), [],
  'three words is too short to judge');
  assert.deepEqual(hrIds(write('hr001-long.txt',
    'The annual report on the situation about the delegation arrival.\n')).filter(id => id === 'UE-HR001'), [],
  'ten words is too long to judge');
  assert.deepEqual(hrIds(write('hr001-comma.txt',
    'The annual report, on the situation for delegation.\n')).filter(id => id === 'UE-HR001'), [],
  'a comma means the sentence has structure the gate cannot see');
  assert.deepEqual(hrIds(write('hr001-paren.txt',
    'The annual report (draft) on the situation.\n')).filter(id => id === 'UE-HR001'), [],
  'parenthetical text suppresses the fragment call');
  assert.deepEqual(hrIds(write('hr001-abbr.txt',
    'The delegation flight route via St.\n')).filter(id => id === 'UE-HR001'), [],
  'a sentence ending in an abbreviation is a split artefact, not a fragment');
  assert.deepEqual(hrIds(write('hr001-repeat.txt',
    'The annual report inside and annual report outside.\n')).filter(id => id === 'UE-HR001'), [],
  'a repeated content word marks deliberate parallel phrasing, not a fragment');
}

// --- 3. UE-HR002 malformed wording -------------------------------------------

{
  const one = hrIds(write('hr002-of.txt',
    'The revised text could of been clearer.\n'));
  assert.deepEqual(one, ['UE-HR002'], `tight collocation must fire, got ${JSON.stringify(one)}`);

  assert.deepEqual(hrIds(write('hr002-course.txt',
    'This would of course be fine.\n')).filter(id => id === 'UE-HR002'), [],
  'the idiomatic "would of course" must never fire');

  assert.equal(hrIds(write('hr002-went.txt',
    'The delegation had went early.\n')).filter(id => id === 'UE-HR002').length, 1,
  'had went must fire');
  assert.equal(hrIds(write('hr002-better.txt',
    'This is more better than before.\n')).filter(id => id === 'UE-HR002').length, 1,
  'more better must fire');

  assert.equal(hrIds(write('hr002-two.txt',
    'The text had went further and could of been clearer.\n')).filter(id => id === 'UE-HR002').length, 2,
  'each malformed collocation gets its own finding');

  const fired = hrOnly(write('hr002-shape.txt',
    'The revised text could of been clearer.\n'))[0];
  assert.equal(typeof fired.suggestion, 'string');
  assert.ok(fired.suggestion.length > 10, 'malformed wording needs a usable suggestion');
  assert.equal(fired.proposed, null, 'guidance only — no proposed replacement');

  assert.deepEqual(hrIds(write('hr002-code.mjs',
    'const note = `The revised text could of been clearer.`;\n')).filter(id => id === 'UE-HR002'), [],
  'code-context units are never wording targets');
}

// --- 4. UE-HR003 duplicate sentence ------------------------------------------

{
  const dupLine = 'The delegation arrived early and reviewed the agenda. The delegation arrived early and reviewed the agenda.';
  const dup = hrIds(write('hr003-one-block.md', `${dupLine}\n`));
  assert.deepEqual(dup, ['UE-HR003'], `a repeated sentence must fire once, got ${JSON.stringify(dup)}`);

  // A short block repeated across two paragraphs is ordinary cross-referencing
  // and stays silent. This is the false-positive control for the cross-block
  // form and it predates that form: the sentence form's four-word threshold
  // already covered it, and the twenty-word block threshold is what keeps the
  // cross-block form silent here too.
  assert.deepEqual(hrIds(write('hr003-two-blocks.md',
    'The delegation arrived early and reviewed the agenda.\n\nThe delegation arrived early and reviewed the agenda.\n')).filter(id => id === 'UE-HR003'), [],
  'a short block repeated in two paragraphs is cross-referencing, not duplication');

  // Normalisation: case and terminal punctuation differences still match.
  assert.equal(hrIds(write('hr003-normalise.md',
    'Very good idea here. very good idea here!\n')).filter(id => id === 'UE-HR003').length, 1,
  'case and punctuation differences must not hide a duplicate');

  assert.deepEqual(hrIds(write('hr003-short.md',
    'Good work. Good work.\n')).filter(id => id === 'UE-HR003'), [],
  'a duplicate shorter than four words is too short to judge');

  // Tables are compact units: identical advice in two rows is legitimate.
  assert.deepEqual(hrIds(write('hr003-table.md',
    '| Note |\n| --- |\n| The delegation arrived early and reviewed the agenda. |\n| The delegation arrived early and reviewed the agenda. |\n')).filter(id => id === 'UE-HR003'), [],
  'identical table cells must never count as a duplicated sentence');
}

// --- 4b. UE-HR003 the cross-block form ---------------------------------------
//
// The second form: a whole authored block repeated verbatim later in the same
// file. It exists because the sentence form is per-unit, so the paragraph
// inserted twice ten lines apart in .feedbacks/v8/web/01 (Omar's P0, "duplicated
// and materially unsuitable") sat in two separate units and nothing fired. An
// exact comparison of a long authored block is the one repetition check that
// needs no language model.
//
// The threshold is REPEATED_BLOCK_MIN_WORDS = 20. Measured over this repository
// and both corpora — 223 files, 478 candidate blocks — the threshold yields
// exactly one duplicate, the web/01 insertion, and any threshold from 10 to 25
// yields the same single result; 30 and above lose it. Twenty sits inside that
// plateau with room below for a shorter genuine insertion, and above the length
// at which two paragraphs sharing a sentence is ordinary cross-referencing. The
// boundary is tested from both sides here so a later change to the number has
// to be deliberate.

{
  // A block of a known word count, so the boundary can be probed exactly.
  const words = (count) => Array.from({ length: count },
    (_, i) => ['The', 'delegation', 'arrived', 'early', 'on', 'the', 'morning',
      'of', 'the', 'session'][i % 10]).join(' ');

  // --- the matrix, one row per case -------------------------------------
  const matrix = [
    // Short block, repeated: silent. The cross-referencing case.
    { name: 'short-repeated', body: `${words(19)}.\n\n${words(19)}.\n`, fires: false,
      why: 'a nineteen-word block repeated in two paragraphs is cross-referencing' },
    // One word under the threshold: still silent, and the silence is the point.
    { name: 'boundary-below', body: `${words(19)}.\n\n${words(19)}.\n`, fires: false,
      why: 'nineteen words is one below the threshold' },
    // Exactly at the threshold: fires.
    { name: 'boundary-at', body: `${words(20)}.\n\n${words(20)}.\n`, fires: true,
      why: 'twenty words is the threshold and must fire' },
    // One word over: fires.
    { name: 'boundary-above', body: `${words(21)}.\n\n${words(21)}.\n`, fires: true,
      why: 'twenty-one words is over the threshold and must fire' },
    // A long block that is repeated nowhere: silent. Nothing to compare against.
    { name: 'long-single', body: `${words(30)}.\n\nThe chair thanked the secretariat for its support.\n`, fires: false,
      why: 'a long block appearing once is not a duplicate' },
    // Two different long blocks: silent.
    { name: 'long-distinct', body: `${words(21)}.\n\n${words(21)} differs from the first block entirely.\n`, fires: false,
      why: 'two long blocks that differ are not duplicates' },
    // A long block repeated three times: the first is never reported, each
    // repeat after it is.
    { name: 'long-thrice', body: `${words(21)}.\n\n${words(21)}.\n\n${words(21)}.\n`, fires: 2,
      why: 'every repeat after the first is reported' },
    // A long block repeated with case and punctuation differences only: still
    // the same block, because the comparison normalises both.
    { name: 'long-normalised', body: `${words(21)}.\n\n${words(21).toUpperCase()}!\n`, fires: true,
      why: 'case and terminal punctuation must not hide a repeated block' },
    // A long block with one clause added: a different block.
    { name: 'long-partial', body: `${words(21)}.\n\n${words(21)} One clause was added here.\n`, fires: false,
      why: 'a block with one clause added is not a duplicated block' },
  ];

  for (const row of matrix) {
    const file = write(`hr003-matrix-${row.name}.md`, `${row.body}\n`);
    const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
    const want = row.fires === true ? 1 : row.fires === false ? 0 : row.fires;
    assert.equal(hits.length, want,
      `${row.name}: ${row.why} — expected ${want} finding(s), got ${JSON.stringify(hits.map(f => [f.line, f.message]))}`);
  }

  // --- the shape of a positive ------------------------------------------
  const positive = hrOnly(write('hr003-block-positive.md',
    `${words(21)}.\n\n${words(21)}.\n`)).filter(f => f.ruleId === 'UE-HR003')[0];
  assert.equal(positive.line, 3, 'the later occurrence is the one reported');
  assert.equal(positive.severity, 'warning', 'still review-only, never error');
  assert.equal(positive.confidence, 'heuristic', 'still heuristic confidence');
  assert.equal(positive.category, 'agent-review', 'still the agent-review category');
  assert.equal(positive.context, 'authored', 'the repeated copy is authored narrative');
  assert.match(positive.message, /A block of 21 words is repeated verbatim in this file/,
    `the message names the length and the file: ${positive.message}`);
  assert.match(positive.message, /first seen at line 1/,
    `the message names the first occurrence: ${positive.message}`);
  assert.equal(positive.suggestion,
    'Remove the repeated block, or replace the repetition with a cross-reference.',
    'the suggestion is review guidance and names the remedy');

  // The report shows the offending copy under Current, capped like every other
  // excerpt, and never under Should be as an automatic rewrite.
  assert.equal(positive.current, `${words(21)}.`,
    'Current carries the repeated block, with its terminal full stop, so a reader can find it');
  assert.equal(positive.proposed, null,
    'proposed is null: there is no single right replacement for a duplicated block');
  assert.equal(positive._replacement, undefined,
    'no replacement is passed, so the finding can never be rewritten by --fix');

  // --- the false-positive controls --------------------------------------
  // A long string repeated in a surface where that is legitimate must be
  // silent. This is why the form is authored-only, and each of these is a real
  // document pattern rather than a synthetic one.
  const LONG = words(21);
  // A <label> is deliberately absent from this list: it is authored copy, so two
  // identical labels in one document are reported, which is the right verdict
  // rather than a false positive. Asserted here so that a later widening of the
  // authored set cannot quietly change it in either direction.
  {
    const labels = hrIds(write('hr003-block-labels.html',
      `<label>${LONG}</label><label>${LONG}</label>\n`)).filter(id => id === 'UE-HR003');
    assert.equal(labels.length, 1,
      'two identical form labels in one document are a duplicated block, not a legitimate repeat');
  }

  for (const [name, body] of [
    ['quoted.html', `<blockquote><p>${LONG}</p></blockquote><blockquote><p>${LONG}</p></blockquote>\n`],
    ['cited.html', `<cite>${LONG}</cite><cite>${LONG}</cite>\n`],
    ['nav.html', `<nav><a href="/x">${LONG}</a><a href="/y">${LONG}</a></nav>\n`],
    ['metadata.html', `<p>${LONG}</p>\n<meta name="description" content="${LONG}">\n`],
    ['code.js', `const a = "${LONG}";\nconst b = "${LONG}";\n`],
    ['heading.md', `# ${LONG}\n\n# ${LONG}\n`],
    ['table.md', `| Note |\n| --- |\n| ${LONG} |\n| ${LONG} |\n`],
  ]) {
    assert.deepEqual(hrIds(write(`hr003-block-quiet-${name}`, body)).filter(id => id === 'UE-HR003'), [],
      `${name} may legitimately repeat a long string, so UE-HR003 must stay silent`);
  }

  // A long block repeated across two different files is a shared boilerplate
  // paragraph — a standard disclaimer, a standing mandate — and never a
  // duplicated block.
  {
    const dir = path.join(tmp, 'hr003-block-boilerplate');
    fs.mkdirSync(dir, { recursive: true });
    const disclaimer = `${words(21)}. This paragraph is identical in every file of the set.`;
    fs.writeFileSync(path.join(dir, 'a.md'), `${disclaimer}\n`);
    fs.writeFileSync(path.join(dir, 'b.md'), `${disclaimer}\n`);
    assert.deepEqual(scan(dir).filter(f => f.ruleId === 'UE-HR003'), [],
      'a boilerplate paragraph shared across files is legitimate, not a duplicated block');
  }

  // --- the boundaries this form keeps -----------------------------------
  // Never error-severity, so a duplicated block can never fail a build on its
  // own; never in the fix set; silenceable by config and by ue:ignore.
  assert.equal(capture([write('hr003-block-exit.md', `${words(21)}.\n\n${words(21)}.\n`)]).code, 0,
    'a duplicated block is review-only: the run must still exit 0');
  assert(!FIXABLE_RULE_IDS.has('UE-HR003'),
    'UE-HR003 must never be --fix-able, in either form');

  {
    const file = write('hr003-block-apply.md', `${words(21)}.\n\n${words(21)}.\n`);
    const before = fs.readFileSync(file, 'utf8');
    const applied = capture([file, '--fix', '--apply']);
    assert.equal(applied.code, 0, `apply must exit 0 with a review-only finding: ${applied.stderr}`);
    assert.equal(fs.readFileSync(file, 'utf8'), before,
      '--fix --apply must never remove a duplicated block');
    assert.doesNotMatch(applied.stdout, /APPLIED/,
      '--fix must not claim a fix it did not make');
  }

  {
    const file = write('hr003-block-off.md', `${words(21)}.\n\n${words(21)}.\n`);
    const off = write('hr003-block-off.json', JSON.stringify({ rules: { 'UE-HR003': { enabled: false } } }));
    const disabled = capture([file, '--format', 'json', '--config', off]);
    assert.notEqual(disabled.code, 2, `the disable config must be accepted: ${disabled.stderr}`);
    assert.deepEqual(JSON.parse(disabled.stdout).findings.filter(f => f.ruleId === 'UE-HR003'), [],
      'config.rules enabled:false must silence the cross-block form');

    const downgraded = write('hr003-block-sev.json', JSON.stringify({ severities: { 'UE-HR003': 'error' } }));
    const escalated = capture([file, '--format', 'json', '--config', downgraded]);
    assert.equal(escalated.code, 1,
      'an organisation may still escalate the rule to error severity by configuration');
  }

  {
    const ignored = capture([write('hr003-block-ignore.md',
      `${words(21)}.\n\n${words(21)}. <!-- ue:ignore UE-HR003 -->\n`), '--format', 'json']);
    assert.deepEqual(JSON.parse(ignored.stdout).findings.filter(f => f.ruleId === 'UE-HR003'), [],
      'ue:ignore must suppress the cross-block form');
  }

  // --- determinism and isolation ----------------------------------------
  // The per-run registry hangs off the run context, so the same document
  // scanned twice in one process gives the same answer both times: a leaked
  // registry would report the first copy on the second scan.
  {
    const file = write('hr003-block-twice.md', `${words(21)}.\n\n${words(21)}.\n`);
    const first = hrOnly(file).filter(f => f.ruleId === 'UE-HR003').length;
    const second = hrOnly(file).filter(f => f.ruleId === 'UE-HR003').length;
    assert.equal(first, 1, 'the first scan reports the repeat once');
    assert.equal(second, first, 'a repeated scan in one process must give a repeated answer');
  }

  // The same block in two different files is not a duplicate: the key is
  // per-file, so a shared boilerplate string across a documentation set is
  // never reported.
  {
    const dir = path.join(tmp, 'hr003-block-files');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'a.md'), `${words(21)}.\n`);
    fs.writeFileSync(path.join(dir, 'b.md'), `${words(21)}.\n`);
    const both = scan(dir).filter(f => f.ruleId === 'UE-HR003');
    assert.deepEqual(both, [],
      'the same block in two different files is not a duplicated block');
  }

  // Three files in one directory scan, one of which duplicates: only that file
  // reports, which proves the per-file key holds in a multi-file run.
  {
    const dir = path.join(tmp, 'hr003-block-mixed');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'one.md'), `${words(21)}.\n\n${words(21)}.\n`);
    fs.writeFileSync(path.join(dir, 'two.md'), 'The chair thanked the secretariat.\n');
    const mixed = scan(dir).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(mixed.length, 1,
      `only the file that repeats reports: ${JSON.stringify(mixed.map(f => f.file))}`);
    assert.ok(mixed[0].file.endsWith('one.md'),
      `the finding must come from the repeating file: ${mixed[0].file}`);
  }
}

// --- 4c. a duplicated paragraph that inline markup split --------------------
//
// A pasted paragraph usually arrives twice, and the second copy is often the
// one somebody went over: a word bolded, a term linked. In HTML each inline
// element breaks the paragraph's text node, so the second copy reaches the
// rule as two or three units, none of which is as long as the twenty-word
// floor. Comparing units alone therefore let markup hide an exact repeat — the
// copy was identical and the rule said nothing, which is the one failure the
// cross-block form exists to prevent. A block is now the whole paragraph,
// reassembled from the units the markup split.

{
  // A paragraph of a known word count, so the floor can be probed from both
  // sides with an inline element inside the second copy.
  const words = (count) => Array.from({ length: count },
    (_, i) => ['The', 'delegation', 'reiterated', 'that', 'humanitarian', 'access',
      'remains', 'restricted', 'and', 'that'][i % 10]).join(' ');

  // The duplicated paragraph, and the one word the second copy emphasises. The
  // emphasised word is a whole word, so the two paragraphs are the same visible
  // string and only the markup differs.
  const PARA = 'The delegation reiterated that humanitarian access remains restricted and that the response is badly underfunded across the whole region today and in the coming quarter.';
  const at = PARA.indexOf('badly');
  const BOLD = (p) => `${p.slice(0, at)}<strong>badly</strong>${p.slice(at + 5)}`;

  // The split is the precondition for everything below, so it is asserted
  // rather than assumed: the second paragraph must reach the rule as more than
  // one unit, and no single unit of it may match a single unit of the other
  // paragraph — which is exactly the comparison that could not see the repeat.
  // A later change that stopped splitting the paragraph would otherwise make
  // every test below pass for the wrong reason.
  const normalise = (t) => t.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const assertSplit = (file, line) => {
    const name = path.basename(file);
    const units = extractFile(file, fs.readFileSync(file, 'utf8'), {});
    const copy = units.filter(u => u.line === line);
    const other = units.filter(u => u.line !== line);
    assert.ok(copy.length > 1,
      `${name}: the fixture must actually be split, or the case is not being tested (${copy.length} unit)`);
    for (const a of copy) {
      for (const b of other) {
        assert.notEqual(normalise(a.text), normalise(b.text),
          `${name}: a single unit of the split copy matches a single unit of the first, so the comparison these tests exercise is not the one that was blind to it`);
      }
    }
    return { copy, units };
  };

  // The real defect, in every surface it was reproduced in.
  const splitForms = [
    // Emphasis, the paste-then-emphasise case: 13, 1 and 11 words, none of them
    // the twenty the floor asks for.
    ['hr003-split-emphasis.html', (p) => `<p>${p}</p>\n\n<p>${BOLD(p)}</p>\n`, 'emphasis'],
    // A link on a term, which is how a duplicated paragraph usually gets marked
    // up in practice.
    ['hr003-split-link.html', (p) => `<p>${p}</p>\n\n<p>${p.replace('humanitarian', '<a href="/access">humanitarian</a>')}</p>\n`, 'a link'],
    // Italics, so the split is not only a single element type.
    ['hr003-split-em.html', (p) => `<p>${p}</p>\n\n<p>${p.replace('badly', '<em>badly</em>')}</p>\n`, 'italics'],
  ];

  for (const [name, build, why] of splitForms) {
    const file = write(name, build(PARA));
    const { copy } = assertSplit(file, 3);
    // The two paragraphs are the same visible copy: the markup wraps whole
    // words, so the text a reader sees is one string in both.
    assert.equal(normalise(copy.map(u => u.text).join(' ')), normalise(PARA),
      `${name}: the split copy must be the same visible text as the first, or this is not a duplicated paragraph`);
    const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(hits.length, 1,
      `${name}: a duplicated paragraph split by ${why} is the defect this form exists for and must be reported, got ${
        JSON.stringify(hits.map(f => [f.line, f.message]))} across ${JSON.stringify(copy.map(u => u.text.split(/\s+/).length))} units`);
    assert.equal(hits[0].line, 3, 'the later copy is the one reported, not the first');
    assert.equal(hits[0].message,
      'A block of 25 words is repeated verbatim in this file (first seen at line 1).',
      `the message reports the whole reassembled paragraph, not the fragment that happened to match: ${hits[0].message}`);
    assert.equal(hits[0].severity, 'warning', 'still review-only');
    assert.equal(hits[0].confidence, 'heuristic', 'still heuristic confidence');
    assert.equal(hits[0].context, 'authored', 'still authored narrative');
    assert.equal(hits[0].proposed, null, 'still no automatic rewrite');
    assert.equal(hits[0].current, BOLD(PARA).replace(/<[^>]+>/g, ''),
      'Current carries the reassembled paragraph as the reader sees it, with the markup gone');
  }

  // The floor is unchanged across a split: nineteen words is silent and twenty
  // fires, each with the second copy split by markup, so the reassembly did not
  // quietly lower the threshold.
  {
    const build = (n) => {
      const p = `${words(n)}.`;
      const cut = p.indexOf('restricted');
      return `<p>${p}</p>\n\n<p>${p.slice(0, cut)}<em>${p.slice(cut, cut + 10)}</em>${p.slice(cut + 10)}</p>\n`;
    };
    const below = write('hr003-split-below.html', build(19));
    assertSplit(below, 3);
    assert.deepEqual(hrIds(below).filter(id => id === 'UE-HR003'), [],
      'a nineteen-word paragraph split by markup is still below the floor');

    const atFloor = write('hr003-split-at.html', build(20));
    assertSplit(atFloor, 3);
    assert.equal(hrIds(atFloor).filter(id => id === 'UE-HR003').length, 1,
      'a twenty-word paragraph split by markup is still at the floor, and must fire');
  }

  // The reassembly is exact, not approximate: a clause added to the second copy
  // is still a different paragraph and stays silent, so the fix did not turn the
  // rule into a match on the longest common run.
  {
    const altered = write('hr003-split-altered.html', `<p>${PARA}</p>\n\n<p>${BOLD(PARA)} One clause was added here.</p>\n`);
    assertSplit(altered, 3);
    assert.deepEqual(hrIds(altered).filter(id => id === 'UE-HR003'), [],
      'a clause added inside the second copy makes it a different paragraph');
  }

  // Three copies, the middle one split: the first is never reported, each repeat
  // after it is, and a split repeat is counted the same as a plain one.
  {
    const three = write('hr003-split-thrice.html', `<p>${PARA}</p>\n\n<p>${BOLD(PARA)}</p>\n\n<p>${PARA}</p>\n`);
    const hits = hrOnly(three).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(hits.length, 2, `both repeats are reported, got ${JSON.stringify(hits.map(f => f.line))}`);
    assert.deepEqual(hits.map(f => f.line), [3, 5], 'the split copy at line 3 and the plain copy at line 5');
  }

  // The quiet surfaces stay quiet across a split. Each repeats a long string
  // where repetition is legitimate, with the repeat split by inline markup, so
  // the reassembly must not join it into a report.
  {
    const LONG = words(24);
    for (const [name, body] of [
      ['quoted.html', `<blockquote><p>${LONG} <em>${LONG}</em></p></blockquote><blockquote><p>${LONG} <em>${LONG}</em></p></blockquote>\n`],
      ['nav.html', `<nav><a href="/x">${LONG} <em>${LONG}</em></a><a href="/y">${LONG} <em>${LONG}</em></a></nav>\n`],
      ['heading.html', `<h2>${LONG} <em>${LONG}</em></h2><h2>${LONG} <em>${LONG}</em></h2>\n`],
      ['table.html', `<table><tr><td>${LONG} <em>${LONG}</em></td><td>x</td></tr></table>\n`],
    ]) {
      assert.deepEqual(
        hrIds(write(`hr003-split-quiet-${name}`, body)).filter(id => id === 'UE-HR003'), [],
        `${name} may legitimately repeat a long string, split by markup or not, so UE-HR003 must stay silent`);
    }
  }

  // A `ue:ignore` inside the second copy silences the whole paragraph, so the
  // split buys no way round a suppression.
  {
    const ignored = write('hr003-split-ignore.html', `<p>${PARA}</p>\n\n<p>${BOLD(PARA)}<!-- ue:ignore UE-HR003 --></p>\n`);
    assertSplit(ignored, 3);
    assert.deepEqual(hrIds(ignored).filter(id => id === 'UE-HR003'), [],
      'ue:ignore must still silence a duplicated paragraph whose second copy is split');
  }

  // A suppression that silences only part of a split paragraph withdraws the
  // block, so the surviving text is judged on its own and is never joined to
  // copy the author asked not to be read. Without that withdrawal the silenced
  // opening and the surviving remainder would reassemble into a paragraph that
  // appears nowhere on the page and match a real one.
  {
    const REST = PARA.slice(0, at + 5);
    const partial = write('hr003-split-partial-suppress.html',
      `<div>\n<!-- ue:ignore UE-HR003 -->\n<p>opening words that the author ignored entirely\n<strong>${REST}</strong></p>\n<p>opening words that the author ignored entirely ${REST}</p>\n</div>\n`);
    const units = extractFile(partial, fs.readFileSync(partial, 'utf8'), {});
    assert.ok(units.some(u => u.block === undefined && u.suppress)
      && units.some(u => u.block === undefined && !u.suppress),
      `the fixture must leave one part suppressed and one part not, or it is not testing the withdrawal: ${
        JSON.stringify(units.map(u => [u.block === undefined, u.suppress || null]))}`);
    assert.deepEqual(hrIds(partial).filter(id => id === 'UE-HR003'), [],
      'copy on the far side of a partial suppression must not be joined to the copy that was silenced');
  }

  // The fields the reassembly depends on, asserted at the extraction layer so a
  // change to their names or meaning breaks here first: the text nodes of one
  // <p> share a block, exactly one of them is the block's last, and text with
  // no enclosing block element has no block at all and is its own block.
  {
    const file = write('hr003-split-blocks.html', '<p>one two three<strong>four five</strong> six seven</p>\n');
    const units = extractFile(file, fs.readFileSync(file, 'utf8'), {});
    assert.equal(units.length, 3, `the inline element splits the paragraph into three units: ${JSON.stringify(units.map(u => u.text))}`);
    assert.equal(new Set(units.map(u => u.block)).size, 1,
      `the three text nodes of one <p> share a block id: ${JSON.stringify(units.map(u => u.block))}`);
    assert.equal(units.filter(u => u.blockLast).length, 1, 'exactly one unit of the block is its last');
    assert.equal(units[units.length - 1].blockLast, true, 'and it is the last one');

    const loose = write('hr003-split-loose.html', 'bare text<strong>more text</strong>\n');
    assert.ok(extractFile(loose, fs.readFileSync(loose, 'utf8'), {})
      .every(u => u.block === undefined),
    'text outside any block element has no block id, so each unit is its own block');
  }
  // An image inside the paragraph splits it the same way an inline element
  // does, and the alt text sits between the halves. The alt text is copy in its
  // own right, but it is not a sentence of the paragraph, so it is carried by
  // the block without joining its text: a duplicated paragraph holding a picture
  // is still a duplicated paragraph, and must be reported.
  {
    const half = (marker) => `<p>The delegation reiterated that humanitarian access remains restricted and that\n<img src="a.png" alt="${marker}"> the response is badly underfunded across the whole region today and in the coming quarter.</p>\n\n<p>${PARA}</p>\n`;
    const file = write('hr003-split-image.html', half('the delegation at the table'));
    const units = extractFile(file, fs.readFileSync(file, 'utf8'), {});
    const image = units.filter(u => u.attribute);
    assert.equal(image.length, 1, `the alt text must be a unit of its own: ${JSON.stringify(units.map(u => u.text))}`);
    assert.equal(image[0].block, units.find(u => u.line === 1).block,
      'the alt text belongs to the block it sits in, so it cannot end the block');
    assert.ok(!image[0].blockLast,
      'and it is not the block\'s last unit, because running text follows it');

    const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(hits.length, 1,
      `a duplicated paragraph holding an image must be reported, got ${JSON.stringify(hits.map(f => [f.line, f.message]))}`);
    assert.equal(hits[0].message,
      'A block of 25 words is repeated verbatim in this file (first seen at line 1).',
      `the alt text is not counted in the block: ${hits[0].message}`);
    assert.doesNotMatch(hits[0].current, /at the table/,
      'Current is the paragraph a reader reads, not the alt text of the image in it');
  }

  // An alt text that is itself a long string repeated twice is still compared
  // on its own, as it was before the reassembly: the block machinery must not
  // have swallowed the attribute surfaces into silence.
  {
    const ALT = 'a wide view of the empty assembly hall before the morning session with the delegation';
    const alt = write('hr003-alt-standalone.html', `<p>one</p><img src="a.png" alt="${ALT}"><p>one</p><img src="b.png" alt="${ALT}">\n`);
    const altUnits = extractFile(alt, fs.readFileSync(alt, 'utf8'), {});
    assert.ok(altUnits.filter(u => u.attribute).every(u => u.block === undefined),
      `an image outside any block element gives its alt text no block, so it is judged on its own: ${
        JSON.stringify(altUnits.map(u => [!!u.attribute, u.block === undefined]))}`);
    assert.deepEqual(hrIds(alt).filter(id => id === 'UE-HR003'), [],
      'a fourteen-word alt text is below the floor, as it was before the reassembly');
  }
}

// --- 4d. what the note promises, and only that -------------------------------
//
// The cross-block form documents a set of surfaces it stays silent on. That
// promise is only worth anything if it is exactly true, so each part of it is
// locked here — including the part where the honest answer is "this is
// reported", because a document with no navigation surface cannot be given the
// navigation exemption.

{
  // A standing disclaimer, repeated verbatim under each section heading. This
  // is ordinary editorial practice in a report, and in Markdown and in HTML it
  // is reported: the rule asks whether the repeat was intended, and for
  // boilerplate the answer is a suppression, not silence. What the note must
  // not do is promise a Markdown document an exemption it cannot deliver.
  const DISCLAIMER = 'The views expressed in this report are those of the authors and do not necessarily reflect the official position of the organisation, its secretariat or its governing body.';
  const sections = (md) => Array.from({ length: 3 },
    (_, i) => md ? `## Section ${i + 1}\n\n${DISCLAIMER}\n` : `<h2>Section ${i + 1}</h2>\n<p>${DISCLAIMER}</p>\n`).join('\n');

  for (const [name, body] of [
    ['hr003-disclaimer.md', sections(true)],
    ['hr003-disclaimer.html', sections(false)],
  ]) {
    const file = write(name, body);
    const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(hits.length, 2,
      `a boilerplate paragraph repeated in one file is reported in ${name}, once per repeat after the first, got ${
        JSON.stringify(hits.map(f => [f.line, f.message]))}`);
    assert.equal(hits[0].severity, 'warning',
      'a reported boilerplate repeat is a review question, never an error, so the run still exits 0');
    assert.equal(capture([file]).code, 0,
      'a standing disclaimer repeated under every heading must not fail a run');
  }

  // The exemption that does hold, and the context it is stated for. A Markdown
  // document has no navigation context at all, which is why the same long
  // string repeated there is reported rather than waved through.
  {
    const LONG = 'Select the reporting period, the reporting office and the funding window before the figures are drawn from the ledger, then confirm the totals against the source annex.';
    const navFile = write('hr003-nav-context.html',
      `<nav><a href="/a">${LONG}</a><a href="/b">${LONG}</a></nav>\n<aside><a href="/c">${LONG}</a><a href="/d">${LONG}</a></aside>\n`);
    assert.deepEqual(hrIds(navFile).filter(id => id === 'UE-HR003'), [],
      'navigation copy may repeat a long string, in nav and in aside alike');

    const mdFile = write('hr003-nav-context.md', `${LONG}\n\n${LONG}\n`);
    assert.equal(hrIds(mdFile).filter(id => id === 'UE-HR003').length, 1,
      'the same long string repeated in a Markdown document is reported, because Markdown has no navigation context');
  }

  // The per-file key, stated without the over-reach: a paragraph shared across
  // files is silent whatever it is, and a paragraph repeated inside one file is
  // reported whatever it is. Both halves are the same assertion seen from either
  // side, and the D7 false positive is the second half.
  {
    const dir = path.join(tmp, 'hr003-scope-of-key');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'one.md'), `${DISCLAIMER}\n`);
    fs.writeFileSync(path.join(dir, 'two.md'), `${DISCLAIMER}\n`);
    assert.deepEqual(scan(dir).filter(f => f.ruleId === 'UE-HR003'), [],
      'the same boilerplate paragraph in two different files is never reported');

    const inFile = path.join(tmp, 'hr003-scope-of-key-single.md');
    fs.writeFileSync(inFile, `# One\n\n${DISCLAIMER}\n\n# Two\n\n${DISCLAIMER}\n`);
    assert.equal(scan(inFile).filter(f => f.ruleId === 'UE-HR003').length, 1,
      'the same boilerplate paragraph twice in one file is reported, because the key is per file');
  }

  // The note and the code must not drift apart in either direction. These
  // assertions quote the shipped wording, so a note changed without the
  // behaviour, or the behaviour changed without the note, fails here.
  {
    const note = CATALOGUE.rules.find(r => r.id === 'UE-HR003').guardNotes;
    assert.match(note, /block is a whole paragraph/i,
      'the note must say a block is a whole paragraph, so markup splitting a copy is not out of scope');
    assert.match(note, /extraction context is navigation/i,
      'the note must scope the navigation silence to the navigation context');
    assert.match(note, /Markdown document cannot have/i,
      'the note must say a Markdown document cannot claim the navigation exemption');
    assert.match(note, /within one file it always is/i,
      'the note must state that a repeat inside one file is reported whatever its purpose');
    assert.doesNotMatch(note, /boilerplate shared across a documentation set is never reported/,
      'the note must not invite the reading that boilerplate is safe in general, which is the D7 false positive');

    const prose = fs.readFileSync(path.join(root, 'rules', 'grammar.md'), 'utf8')
      .split('\n').find(l => l.startsWith('- **UE-HR003**'));
    assert.ok(prose, 'rules/grammar.md must document UE-HR003');
    assert.match(prose, /block is a whole paragraph/i, 'the prose must agree with the note on the block');
    assert.match(prose, /Markdown document has no navigation surface/i,
      'the prose must agree with the note on the Markdown exemption');
    assert.match(prose, /Across two files the same paragraph is never reported/,
      'the prose must agree with the note on the per-file key');
  }
}

// --- 4e. the two edge defects in the reassembly -----------------------------
//
// Two things the block comparison got wrong at the edges, both of which let an
// exact repeat go unreported, and one of which also made a repeat's visibility
// depend on which other files were in the same scan.
//
//   (a) the assembler keyed its open block on a source offset alone, and a block
//       whose last unit was ineligible — a paragraph ending in an image whose
//       `title` is navigation copy — was never closed at all, so the next
//       file's copy was appended to it;
//   (b) the pieces were joined on a fixed space, so inline markup that broke a
//       word (`humanit<mark>arian</mark>`) read as two words and never matched
//       the plain copy of the paragraph.
//
// Each test below asserts the precondition of its own fixture first, because a
// fixture that does not exhibit the defect it claims to cover passes for the
// wrong reason. The word-splitting fixtures in particular would pass under the
// old fixed-space join if the fixture wrapped whole words, which is what the
// section 4c fixtures do.

{
  const normalise = (t) => t.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const unitsOf = (file) => extractFile(file, fs.readFileSync(file, 'utf8'), {});
  // The text a rule reassembles, joined the way the extractor says to join.
  const joined = (units) => {
    let out = '';
    for (const u of units) {
      if (u.attribute) continue;
      if (out) out += u.joiner === undefined ? ' ' : u.joiner;
      out += u.text;
    }
    return out;
  };

  // --- (a) an open block must not swallow the next file ---------------------
  {
    // A paragraph whose last unit carries running text is not eligible to close
    // a block: the `title` of an image is navigation copy. Before the fix that
    // unit never reached the assembler, so the block stayed open.
    const dir = path.join(tmp, 'hr003-dangling-block');
    fs.mkdirSync(dir, { recursive: true });
    const PARA = 'The delegation reiterated that humanitarian access remains restricted and that the response is badly underfunded across the whole region today and in the coming quarter.';
    const dangling = path.join(dir, 'a.html');
    fs.writeFileSync(dangling, `<p>${PARA} <img src="chart.png" title="Trend since 2019"></p>\n`);

    // The precondition, asserted: the block's last unit is ineligible copy, and
    // it is the unit that would close the block.
    const danglingUnits = unitsOf(dangling);
    const last = danglingUnits[danglingUnits.length - 1];
    assert.equal(last.context, 'nav',
      `the fixture must end in ineligible copy, or the block was never left open: ${
        JSON.stringify(danglingUnits.map(u => [u.context, !!u.blockLast]))}`);
    assert.ok(last.blockLast,
      'and that ineligible unit must be the one that closes the block');
    assert.equal(danglingUnits[0].text, PARA,
      'the paragraph itself is eligible, so only the closing unit is not');

    // The repeat that must not depend on the scan: a genuine, plain, verbatim
    // repeat in a second file, in the same directory.
    const plain = path.join(dir, 'b.html');
    fs.writeFileSync(plain, `<p>${PARA}</p>\n\n<p>${PARA}</p>\n`);

    const alone = scan(plain).filter(f => f.ruleId === 'UE-HR003');
    const together = scan(dir).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(alone.length, 1,
      `scanned on its own the plain repeat is reported, got ${JSON.stringify(alone.map(f => [f.file, f.line]))}`);
    assert.equal(together.length, 1,
      `the same repeat must be reported in a directory scan too, and it must not depend on which other files are in the run, got ${
        JSON.stringify(together.map(f => [path.basename(f.file), f.line, f.message]))}`);
    assert.ok(together[0].file.endsWith('b.html'),
      `the finding must come from the file that repeats: ${JSON.stringify(together.map(f => f.file))}`);
    assert.match(together[0].message, /first seen at line 1/,
      `and it must name the first copy in its own file: ${together[0].message}`);
  }

  // The same, in the other order and with a third file, because a scan-order
  // dependency that one arrangement does not show is still a dependency.
  {
    const dir = path.join(tmp, 'hr003-dangling-block-order');
    fs.mkdirSync(dir, { recursive: true });
    const PARA = 'The delegation reiterated that humanitarian access remains restricted and that the response is badly underfunded across the whole region today and in the coming quarter.';
    // a dangling block, then the repeat, then another dangling block
    fs.writeFileSync(path.join(dir, '1-open.html'), `<p>${PARA} <img src="c.png" title="Trend since 2019"></p>\n`);
    fs.writeFileSync(path.join(dir, '2-repeat.html'), `<p>${PARA}</p>\n\n<p>${PARA}</p>\n`);
    fs.writeFileSync(path.join(dir, '3-open.html'), `<p>${PARA} <img src="c.png" title="Trend since 2019"></p>\n`);
    const hits = scan(dir).filter(f => f.ruleId === 'UE-HR003');
    assert.equal(hits.length, 1,
      `a dangling block on either side of the repeat must not change it, got ${
        JSON.stringify(hits.map(f => [path.basename(f.file), f.line, f.message]))}`);
    assert.ok(hits[0].file.endsWith('2-repeat.html'),
      `and the finding must be the repeat, not a block that swallowed it: ${JSON.stringify(hits.map(f => f.file))}`);
  }

  // --- (b) inline markup that broke a word ---------------------------------
  {
    // A paragraph of 25 words with one word broken by an inline element. The
    // element wraps nothing: it sits inside a single word, as <mark> around a
    // highlighted span inside an otherwise ordinary sentence does.
    const HEAD = 'The delegation reiterated that humanit';
    const TAIL = 'arian access remains restricted and that the response is badly underfunded across the whole region today and in the coming quarter.';
    const PLAIN = HEAD + TAIL;
    const SPLIT = (tag) => `<p>${HEAD}<${tag}>${TAIL}</p>`;

    // The precondition, and the point of the whole case: the two copies are the
    // same visible string, but joining the split copy on a space does not
    // reproduce it, so a fixed-space reassembly cannot match. Asserted, because
    // a fixture that wrapped a whole word would pass under that join and this
    // test would prove nothing.
    for (const [name, tag, why] of [
      ['mark', 'mark', 'a highlighted span'],
      ['strong', 'strong', 'emphasis'],
      ['em', 'em', 'italics'],
      ['u', 'u', 'an underline'],
      ['span', 'span', 'a styled span'],
    ]) {
      const file = write(`hr003-wordsplit-${name}.html`, `<p>${PLAIN}</p>\n\n${SPLIT(tag)}\n`);
      const parts = unitsOf(file);
      const second = parts.filter(u => u.line === 3);
      assert.equal(second.length, 2,
        `${name}: the element must break the paragraph into two units, got ${JSON.stringify(parts.map(u => u.text.slice(0, 24)))}`);
      assert.equal(normalise(joined(second)), normalise(PLAIN),
        `${name}: the split copy is the plain copy, rejoined on the ${why}`);
      assert.notEqual(normalise(second.map(u => u.text).join(' ')), normalise(PLAIN),
        `${name}: the precondition — joining on a space must NOT reproduce the paragraph, or the fixture does not exercise the join and the test is vacuous`);
      assert.equal(second[1].joiner, '',
        `${name}: and the extractor must measure the seam as rendering nothing, not a space`);

      const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
      assert.equal(hits.length, 1,
        `${name}: a duplicated paragraph whose word ${why} split is the same defect as a whole word emphasised, got ${
          JSON.stringify(hits.map(f => [f.line, f.message]))}`);
      assert.equal(hits[0].line, 3, `${name}: the later copy is the one reported`);
      assert.equal(hits[0].message,
        'A block of 25 words is repeated verbatim in this file (first seen at line 1).',
        `${name}: the message counts the rejoined paragraph's 25 words, not the 26 the split shows: ${hits[0].message}`);
      assert.doesNotMatch(hits[0].current, /humanit arian|humanitarian <|<mark>|<strong>|<em>|<u>|<span>/,
        `${name}: Current is the copy a reader sees, with the markup gone and the word whole: ${hits[0].current}`);
    }

    // The same element in both copies, which the old fixed-space join did
    // catch. Kept, so the fix is shown to be a widening and not a change of
    // what the rule considers a repeat.
    {
      const file = write('hr003-wordsplit-both.html',
        `<p>${HEAD}<mark>${TAIL}</mark></p>\n\n<p>${HEAD}<mark>${TAIL}</mark></p>\n`);
      const hits = hrOnly(file).filter(f => f.ruleId === 'UE-HR003');
      assert.equal(hits.length, 1,
        `a split in both copies is still a verbatim repeat, got ${JSON.stringify(hits.map(f => [f.line, f.message]))}`);
    }

    // A word broken in one copy and not in the other is a different sentence,
    // and stays silent. This is the floor of the fix: it rejoins what a reader
    // would read the same, and nothing beyond that.
    {
      const file = write('hr003-wordsplit-only-one.html',
        `<p>${PLAIN}</p>\n\n<p>${HEAD} <mark>${TAIL}</mark></p>\n`);
      assert.deepEqual(hrIds(file).filter(id => id === 'UE-HR003'), [],
        'a space added inside the second copy makes it a different paragraph, and the rule must not match it');
    }
  }

  // --- the seam, read the way a reader reads it ----------------------------
  //
  // Every case below is a paragraph whose pieces an inline element separated,
  // and the exact string the reader sees. A fixed space gets the middle rows
  // wrong in both directions, so this is where the join is pinned down.
  {
    const SEAMS = [
      ['word broken, nothing at the seam', '<p>alpha<mark>beta</mark>gamma</p>', 'alphabetagamma'],
      ['word broken, a space after', '<p>alpha<mark>beta</mark> gamma</p>', 'alphabeta gamma'],
      ['a space before, none after', '<p>alpha <mark>beta</mark>gamma</p>', 'alpha betagamma'],
      ['whole words either side', '<p>alpha <mark>beta</mark> gamma</p>', 'alpha beta gamma'],
      ['a newline in the source', '<p>alpha\n<mark>beta</mark>\ngamma</p>', 'alpha beta gamma'],
      ['a break', '<p>alpha<br><mark>beta</mark>gamma</p>', 'alpha betagamma'],
      ['an image between the pieces', '<p>alpha<img src="x.png"><mark>beta</mark>gamma</p>', 'alpha betagamma'],
      ['a link wrapping a word', '<p>alpha<a href="/x">beta</a>gamma</p>', 'alpha betagamma'],
      ['two elements in a row', '<p>alpha<mark>be</mark><em>ta</em>gamma</p>', 'alphabetagamma'],
      ['a non-breaking space alone in a node', '<p>alpha<mark>&nbsp;</mark>beta</p>', 'alpha beta'],
      ['no markup at all', '<p>alpha beta gamma</p>', 'alpha beta gamma'],
    ];
    for (const [name, html, want] of SEAMS) {
      const file = write('hr003-seam.html', `${html}\n`);
      assert.equal(joined(unitsOf(file)), want,
        `${name}: the reader sees ${JSON.stringify(want)}, so the pieces must rejoin to that`);
    }
  }
}

// --- 5. UE-HR004 incoherent heading ------------------------------------------

{
  const dot = hrIds(write('hr004-dot.md', '# Programme overview of the annual report.\n'));
  assert.deepEqual(dot, ['UE-HR004'], `a heading ending in a full stop must fire, got ${JSON.stringify(dot)}`);
  assert.equal(hrIds(write('hr004-semicolon.md', '# Programme overview;\n')).filter(id => id === 'UE-HR004').length, 1,
    'a heading ending in a semicolon must fire');
  assert.deepEqual(hrIds(write('hr004-clean.md', '# Programme overview\n')).filter(id => id === 'UE-HR004'), [],
    'a heading without terminal punctuation is fine');
  assert.equal(hrIds(write('hr004-h2.html', '<h2>Programme overview.</h2>\n')).filter(id => id === 'UE-HR004').length, 1,
    'HTML heading tags fire too');
  assert.deepEqual(hrIds(write('hr004-paragraph.txt', 'Programme overview.\n')).filter(id => id === 'UE-HR004'), [],
    'a paragraph ending in a full stop is ordinary prose, not a heading');
}

// --- 6. UE-HR005 broken quotation --------------------------------------------

{
  const open = hrIds(write('hr005-open.md',
    'The delegation said "arrivals are delayed.\n'));
  assert.deepEqual(open, ['UE-HR005'], `an unpaired quote must fire, got ${JSON.stringify(open)}`);

  assert.deepEqual(hrIds(write('hr005-balanced.md',
    'The delegation said "arrivals are delayed" today.\n')).filter(id => id === 'UE-HR005'), [],
    'a balanced quotation must stay silent');
  assert.deepEqual(hrIds(write('hr005-apostrophe.md',
    'The delegation\'s arrival is confirmed.\n')).filter(id => id === 'UE-HR005'), [],
    'a straight apostrophe is not a quotation mark');
  assert.deepEqual(hrIds(write('hr005-curly-apostrophe.md',
    'Delegation’s arrival is confirmed.\n')).filter(id => id === 'UE-HR005'), [],
    'a curly apostrophe is not a quotation mark');
  assert.deepEqual(hrIds(write('hr005-curly-pair.md',
    'The delegation said “arrivals are delayed.”\n')).filter(id => id === 'UE-HR005'), [],
    'a balanced curly quotation must stay silent');
  assert.equal(hrIds(write('hr005-curly-open.md',
    'The delegation said “arrivals are delayed.\n')).filter(id => id === 'UE-HR005').length, 1,
    'an unpaired curly quote must fire');
  assert.deepEqual(hrIds(write('hr005-code.mjs',
    'const note = `He said "arrivals`;\n')).filter(id => id === 'UE-HR005'), [],
    'code-context units are never quotation targets');
  assert.deepEqual(hrIds(write('hr005-compact.html',
    '<a class="badge" href="/x">Mission said "arrivals</a>\n')).filter(id => id === 'UE-HR005'), [],
    'compact navigation units are never quotation targets');
}

// --- 7. positive fixtures: exact ids, exit 0 ---------------------------------

{
  const FIXTURES = [
    ['hr001-fragment.txt', 'UE-HR001'],
    ['hr002-malformed.txt', 'UE-HR002'],
    ['hr003-duplicate.md', 'UE-HR003'],
    ['hr004-heading.md', 'UE-HR004'],
    ['hr005-quotation.md', 'UE-HR005'],
  ];
  const manifest = JSON.parse(fs.readFileSync(fixture('expected.json'), 'utf8'));
  for (const [name, id] of FIXTURES) {
    // Fixtures are copied out of the skill root before use — the scanner
    // never reads files inside its own root unless --self-scan is given.
    const target = write(`pos-${name}`, fs.readFileSync(fixture(name), 'utf8'));
    const result = capture([target, '--format', 'json']);
    assert.equal(result.code, 0,
      `${name} must exit 0 — heuristic findings are review-only:\n${result.stdout}`);
    const findings = JSON.parse(result.stdout).findings;
    assert.deepEqual(findings.map(f => f.ruleId), [id],
      `${name} must fire exactly ${id}`);
    assert.equal(findings[0].severity, 'warning', `${name} finding severity`);
    assert.deepEqual(manifest[name], [id], `expected.json must list ${name} as [${id}]`);
  }
}

// --- 8. fix boundary, disable and suppression --------------------------------

{
  for (const id of HR_IDS) {
    assert(!FIXABLE_RULE_IDS.has(id), `${id} must never be --fix-able`);
  }

  const combo = write('hr-combo.md', [
    'The annual report on the situation.',
    '',
    'The revised text could of been clearer.',
    '',
    'The delegation arrived early and reviewed the agenda. The delegation arrived early and reviewed the agenda.',
    '',
    '# Programme overview of the annual report.',
    '',
    'The delegation said "arrivals are delayed.',
    '',
    'The field office works with UNDP on the recovery programme.',
  ].join('\n'));
  const comboFindings = scan(combo);
  // HR006 fires on its own line; HR007 needs non-English copy and is proven
  // in its own fixture below; HR008/HR009 are configuration-gated and proven
  // in their own block. The combo carries the ungated family, in source order.
  const comboExpected = HR_IDS.filter(id => !['UE-HR007', 'UE-HR008', 'UE-HR009'].includes(id));
  assert.deepEqual(comboFindings.map(f => f.ruleId), comboExpected,
    `the heuristics fire together, review-only, in source order: got ${JSON.stringify(comboFindings.map(f => f.ruleId))}`);
  assert.ok(comboFindings.every(f => f.severity === 'warning'),
    'every heuristic finding stays warning severity');

  const before = fs.readFileSync(combo, 'utf8');
  const applied = capture([combo, '--fix', '--apply']);
  assert.equal(applied.code, 0, `apply must exit 0 with only review findings: ${applied.stderr}`);
  assert.equal(fs.readFileSync(combo, 'utf8'), before,
    '--fix --apply must never rewrite a heuristic-only file');

  // The same fire text is silent once config disables the rule.
  const off = write('hr-off.json', JSON.stringify({ rules: { 'UE-HR001': { enabled: false } } }));
  const disabledRun = capture([write('hr-disabled.md', 'The annual report on the situation.\n'),
    '--format', 'json', '--config', off]);
  assert.notEqual(disabledRun.code, 2, `the disable config must be accepted: ${disabledRun.stderr}`);
  const disabled = JSON.parse(disabledRun.stdout).findings;
  assert.deepEqual(disabled.map(f => f.ruleId), [],
    'config.rules enabled:false must silence UE-HR001');

  const ignored = hrIds(write('hr-ignore.md',
    'The annual report on the situation. <!-- ue:ignore UE-HR001 -->\n'));
  assert.deepEqual(ignored, [], `ue:ignore must suppress UE-HR001, got ${JSON.stringify(ignored)}`);
}

console.log('ok — heuristic review rules: catalogue, gates, fixtures, fix boundary, disable, '
  + 'duplication in both forms');
