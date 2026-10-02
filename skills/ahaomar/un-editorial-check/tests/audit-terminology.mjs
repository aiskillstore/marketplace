// W2b audit: the terminology rework contract (rules/terminology.md).
//
//   1. UE-TE001's context gate — three offline states over a fixed evidence
//      window (120 characters before, 200 after) for `maternal mortality
//      rate`, while every other configured pair still fires unconditionally at
//      error severity.
//   2. UE-TE002 — the unsourced `women's work` / `female work` replacement
//      pairs are gone from the profile; the sourced `handicapped` pair still
//      fires and still proposes no wording the fixer can apply.
//   3. UE-TE003 — the percent sign is silent in every context, the
//      resolution-context branch is a documented limitation rather than a
//      heuristic, and the closed-up spelling is UE-SP001's on spelling-list
//      authority (and is the one part of this that --fix does rewrite).
//   4. UE-TE004 — flag-only: reported with proposed wording, never rewritten.
//   5. Catalogue wiring — every UE-TE* entry carries source ids that exist in
//      rules/sources.json, and its guard note describes the behaviour the code
//      actually has.
//   6. Doc truth — rules/sources.md cites the live manual and the running-text
//      note it actually relies on; README's --fix boundary is literally true
//      for terminology.
//
// TDD: written against the reworked engine. Standalone run:
//   node tests/audit-terminology.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CATALOGUE, run } from '../bin/check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-terminology-'));
let sequence = 0;

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
  const code = run(args, { log: line => out.push(String(line)), error: line => err.push(String(line)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const json = (result) => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const findings = (file, ...extra) => json(capture([file, '--format', 'json', ...extra])).findings;
const of = (file, ruleId) => findings(file).filter(finding => finding.ruleId === ruleId);
// A fixture written for one assertion only: nothing else may fire on it.
const sentence = (body) => write(`fixture-${sequence++}.txt`, `${body}\n`);

// --- 1. UE-TE001: the context gate -------------------------------------------

{
  // State 1: a per-100 000 live-births figure is printed inside the window.
  const file = sentence('The maternal mortality rate was 550 per 100 000 live births last year.');
  const [finding] = of(file, 'UE-TE001');
  assert(finding, 'state 1 must raise the review flag');
  assert.equal(finding.severity, 'warning', 'the gated path is never an error');
  assert.equal(finding.confidence, 'heuristic', 'the gated path is review, not proof');
  assert.match(finding.message, /per 100 000 live-births figure/,
    `the message must quote the printed figure: ${finding.message}`);
  assert(finding.proposed, 'proposed wording is review guidance');

  // State 2: a statistic is printed, but no per-100 000 live-births figure —
  // the message must admit what the offline check could not establish.
  const other = sentence('The maternal mortality rate stood at 450 in the annex table.');
  const [second] = of(other, 'UE-TE001');
  assert(second, 'state 2 must raise the review flag');
  assert.equal(second.severity, 'warning');
  assert.equal(second.confidence, 'heuristic');
  assert.match(second.message, /denominator could not be determined offline/,
    `state 2 must say the denominator is unknown offline: ${second.message}`);
  assert.match(second.message, /no defect is claimed/,
    `state 2 must claim no defect: ${second.message}`);

  // State 3: no printed statistic anywhere near the term — no finding at all.
  const silent = sentence('The maternal mortality rate is discussed in the annex.');
  assert.deepEqual(of(silent, 'UE-TE001'), [],
    'state 3 must raise nothing: a term with no statistic beside it is not flagged');

  // The window is the whole of the detection: a statistic outside it is not
  // "nearby", so the gate stays shut.
  const far = sentence('The maternal mortality rate is reported for the period'
    + ' and the annex reviews the series across every region and every demographic'
    + ' indicator covered by the wider programme reporting cycle before the final'
    + ' figure of 850 is reached at the end.');
  assert.deepEqual(of(far, 'UE-TE001'), [],
    'a statistic beyond the evidence window must not open the gate');
}

{
  // Every pair other than the gated one is still screened directly.
  const file = sentence('Maternal deaths are shown for each region.');
  const [finding] = of(file, 'UE-TE001');
  assert(finding, 'an ungated pair must still fire');
  assert.equal(finding.severity, 'error');
  assert.equal(finding.confidence, 'deterministic');
}

// --- 2. UE-TE002: the unsourced pair is gone ----------------------------------

{
  const unsourced = write('te002-unsourced.txt',
    "Women's work is shown for each region.\nWomen\u2019s work is shown for the period.\nFemale work is shown for the year.\n");
  assert.deepEqual(of(unsourced, 'UE-TE002'), [],
    'the unsourced replacement pair must no longer be proposed');

  const sourced = write('te002-sourced.txt', 'Handicapped persons may take part in the session.\n');
  const [finding] = of(sourced, 'UE-TE002');
  assert(finding, 'the sourced handicapped pair must still fire');
  assert.equal(finding.severity, 'error');
  assert.equal(finding.proposed, 'persons with disabilities');
}

// --- 3. UE-TE003: silent, with the spelling on UE-SP001 -----------------------

{
  const sign = write('te003-sign.txt', 'Progress reached 25% this year.\n');
  assert.deepEqual(of(sign, 'UE-TE003'), [], 'the sign is permitted in running prose');

  // The documented limitation: no offline resolution detector exists, so the
  // barred context is silent too — honestly, not by heuristic guess.
  const resolution = write('te003-resolution.txt',
    'The Assembly decides that programme coverage was 25% of the total.\n');
  assert.deepEqual(of(resolution, 'UE-TE003'), [],
    'resolution context has no offline detector: silence is the documented limitation');

  // The closed-up spelling is a UE-SP001 finding on spelling-list authority.
  const word = write('te003-word.txt', 'Coverage was written in percent terms for the year.\n'); // ue:ignore UE-SP001  (deliberate test data)
  const [spelling] = of(word, 'UE-SP001');
  assert(spelling, 'the closed-up spelling must be reported by UE-SP001');
  assert.equal(spelling.proposed, 'per cent');

  // And it is the one spelling finding the fixer does rewrite.
  const target = write('te003-word-fix.txt', 'Coverage was written in percent terms for the year.\n'); // ue:ignore UE-SP001  (deliberate test data)
  const applied = capture([target, '--fix', '--apply']);
  assert.equal(applied.code, 0, `spelling is fixable: ${applied.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'),
    'Coverage was written in per cent terms for the year.\n',
    'UE-SP001 carries the per cent replacement');

  // A suppression naming the silent rule is still accepted: the id, its
  // catalogue entry and its configuration switch all survive. The figure is
  // hedged so that only the suppression under test can explain a clean file.
  const suppressed = write('te003-suppressed.txt',
    'Progress reached approximately 25% this year. <!-- ue:ignore UE-TE003 -->\n');
  assert.deepEqual(findings(suppressed), []);
}

// --- 4. UE-TE004: flag-only ---------------------------------------------------

{
  const file = write('te004-flag.txt', 'Coverage was recorded in the US for the year.\n');
  const [finding] = of(file, 'UE-TE004');
  assert(finding, 'a bare country name must still be reported');
  assert.equal(finding.severity, 'error');
  assert(finding.proposed, 'proposed wording is review guidance');

  const before = fs.readFileSync(file, 'utf8');
  const applied = capture([file, '--fix', '--apply']);
  assert.equal(applied.code, 1, 'an unwritten error must still fail the run');
  assert.equal(fs.readFileSync(file, 'utf8'), before,
    '--fix must never rewrite the country name');
}

// --- 5. every UE-TE* finding stays outside the --fix set ----------------------

{
  const cases = [
    ['te001-ungated.txt', 'Maternal deaths are shown for each region.'],
    ['te001-gated.txt', 'The maternal mortality rate was 550 per 100 000 live births last year.'],
    ['te002.txt', 'Handicapped persons may take part in the session.'],
    ['te004.txt', 'Coverage was recorded in the US for the year.'],
  ];
  for (const [name, body] of cases) {
    const target = write(name, `${body}\n`);
    const before = fs.readFileSync(target, 'utf8');
    const applied = capture([target, '--fix', '--apply']);
    assert.equal(fs.readFileSync(target, 'utf8'), before,
      `${name}: terminology must never be rewritten`);
    assert.doesNotMatch(applied.stdout, /APPLIED — /, `${name}: nothing may be applied`);
    assert.notEqual(applied.code, 2, `${name}: a prose file is not refused`);
  }
}

// --- 6. catalogue wiring and guard notes --------------------------------------

{
  const registry = JSON.parse(fs.readFileSync(path.join(root, 'rules', 'sources.json'), 'utf8'));
  const known = new Set(registry.sources.map(source => source.id));
  const expectations = {
    'UE-TE001': ['120 characters', 'per-100 000 live-births figure'],
    'UE-TE002': ['unsourced'],
    'UE-TE003': ['documented limitation'],
    'UE-TE004': ['--fix never rewrites'],
  };
  for (const [id, fragments] of Object.entries(expectations)) {
    const entry = CATALOGUE.rules.find(rule => rule.id === id);
    assert(entry, `catalogue is missing ${id}`);
    assert(Array.isArray(entry.sources) && entry.sources.length,
      `${id} must cite its sources`);
    for (const source of entry.sources) {
      assert(known.has(source), `${id} cites unknown source id "${source}"`);
    }
    for (const fragment of fragments) {
      assert(entry.guardNotes.includes(fragment),
        `${id} guard note must describe "${fragment}": ${entry.guardNotes}`);
    }
  }
}

// --- 7. doc truth -------------------------------------------------------------

{
  const sources = fs.readFileSync(path.join(root, 'rules', 'sources.md'), 'utf8');
  assert(!sources.includes('editorial.un.org'),
    'rules/sources.md must not cite the dead manual URL');
  assert(sources.includes('https://www.un.org/dgacm/en/content/editorial-manual'),
    'rules/sources.md must cite the live manual');
  assert.match(sources, /may be used in running text/,
    'rules/sources.md must quote the note it relies on');
  assert.match(sources, /should not be used in resolutions/,
    'rules/sources.md must keep the one prohibition the manual actually states');

  const terminology = fs.readFileSync(path.join(root, 'rules', 'terminology.md'), 'utf8');
  assert.match(terminology, /documented limitation/,
    'rules/terminology.md must record the resolution-context limitation');
  assert.match(terminology, /120 characters before/,
    'rules/terminology.md must state the evidence window');
  assert(terminology.includes('flag-only'),
    'rules/terminology.md must say UE-TE004 is flag-only');

  const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  const fixList = readme.split('\n').find(line => line.startsWith('- It applies only deterministic replacements'));
  assert(fixList, 'README must keep its --fix list');
  assert(!fixList.includes('UE-TE003') && !fixList.includes('UE-TE004'),
    `README's fix list must not claim terminology is fixable: ${fixList}`);
  assert(fixList.includes('UE-SP001'), 'README must still name the spelling fixes');
  assert.match(readme, /It does not rewrite dates, terminology or claims\./,
    'README must still promise that terminology is never rewritten');

  const profile = JSON.parse(
    fs.readFileSync(path.join(root, 'config', 'profiles', 'un-v1.json'), 'utf8'));
  const pairs = profile.terminology.forbidden.map(entry => (Array.isArray(entry) ? entry[0] : entry.from));
  for (const removed of ["women's work", 'women\u2019s work', 'female work']) {
    assert(!pairs.includes(removed),
      `the unsourced pair "${removed}" must not be configured any more`);
  }
  assert(pairs.includes('handicapped'), 'the sourced handicapped pair must stay configured');
  assert.equal(profile.spelling.percent, 'per cent',
    'the per cent preference must live in the spelling list');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — terminology: TE001 gate, TE002 removal, TE003 silence, TE004 flag-only, '
  + 'catalogue sources, doc truth');
