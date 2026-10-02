// un-editorial-check — behavioural test suite.
//
// The corpus under tests/fixtures is the contract:
//   * every file in fixtures/negative must produce no findings at all,
//   * every file in fixtures/positive must produce exactly the rule ids listed
//     in fixtures/positive/expected.json, and the exit code must follow from
//     the severity of those ids (errors -> 1, warnings and notes -> 0),
//   * fixtures/fix holds the --fix contract (what may be rewritten and what
//     must be refused), and fixtures/audits holds the opt-in audit contract.
//
// Fixtures are copied out of the repository before use: the scanner never
// reads files inside its own skill root unless --self-scan is given, and a
// fixture has to behave like any other project file.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { CATALOGUE, run } from '../bin/check.mjs';
import { parseJsonStrict } from '../lib/config.mjs';
import { SECURITY_FIXTURE_SOURCE } from './lib/make-security-fixture.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-'));

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
  // Only supply the suite's config when the caller has not chosen one.
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
const ids = result => [...new Set(json(result).findings.map(f => f.ruleId))].sort();
const severityOf = id => {
  const rule = CATALOGUE.rules.find(entry => entry.id === id);
  assert(rule, `catalogue is missing ${id}`);
  return rule.severity;
};
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);

// --- corpus: negatives -------------------------------------------------------

const negatives = fs.readdirSync(fixture('negative')).sort();
assert(negatives.length >= 20, 'negative corpus must stay substantial');
for (const name of negatives) {
  const result = scan(fixture('negative', name));
  assert.equal(result.code, 0, `${name}: expected exit 0\n${result.stdout}\n${result.stderr}`);
  assert.deepEqual(ids(result), [], `${name} must produce no findings`);
}

// --- corpus: positives -------------------------------------------------------

const manifest = JSON.parse(fs.readFileSync(fixture('positive', 'expected.json'), 'utf8'));
const positives = fs.readdirSync(fixture('positive')).filter(name => name !== 'expected.json').sort();
assert.deepEqual(positives, Object.keys(manifest).sort(), 'expected.json must list every positive fixture');
for (const name of positives) {
  const result = scan(fixture('positive', name));
  assert.deepEqual(ids(result), manifest[name], `${name}: ${result.stdout}`);
  const expectedExit = manifest[name].some(id => severityOf(id) === 'error') ? 1 : 0;
  assert.equal(result.code, expectedExit, `${name}: exit code must follow the severity of its findings`);
}

// Every editorial rule in the catalogue must be covered by the corpus. UE-SP003
// is gated by an opt-in config flag, so it is covered later in this file.
// UE-TE003 is covered by its own limitation: the rule is silent in every
// context (rules/terminology.md, "UE-TE003"), so no positive fixture can
// exist — its contract lives in tests/audit-terminology.mjs instead.
// UE-GR004 is configuration-gated (spacingReview) and covered in the block
// below, which scans with the review switched on.
const OPT_IN_COVERAGE = new Set(['UE-SP003', 'UE-TE003', 'UE-GL001', 'UE-GL002', 'UE-GR004', 'UE-CL002', 'UE-CL003', 'UE-HR008', 'UE-HR009']);
const covered = new Set([...Object.values(manifest).flat(), ...OPT_IN_COVERAGE]);
const uncovered = CATALOGUE.rules
  .filter(rule => rule.profile === null)
  .map(rule => rule.id)
  .filter(id => !covered.has(id));
assert.deepEqual(uncovered, [], `editorial rules with no positive fixture: ${uncovered.join(', ')}`);


// --- --stdin: one document from standard input -------------------------------

{
  // fd 0 cannot be piped in-process, so the stdin contract runs through a real
  // subprocess with the document on its standard input.
  const result = spawnSync(process.execPath, [cli, '--stdin', '--format', 'json',
    '--config', config], { input: 'The organization met on March 5, 2026 in Geneva.\n',
    encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  const parsed = JSON.parse(result.stdout);
  assert.equal(parsed.files, 1);
  const names = [...new Set(parsed.findings.map(f => f.file))];
  assert.deepEqual(names, ['<stdin>.txt'], 'stdin findings must carry the synthetic name');
  const byRule = new Set(parsed.findings.map(f => f.ruleId));
  for (const id of ['UE-SP001', 'UE-NU001']) {
    assert(byRule.has(id), `stdin must run the editorial rules, missing ${id}`);
  }
  // Error-severity findings keep their meaning on stdin: the country rule
  // fails the run exactly as it does for a named file.
  const errors = spawnSync(process.execPath, [cli, '--stdin', '--format', 'json',
    '--config', config], { input: 'The delegation from Burma arrived.\n', encoding: 'utf8' });
  assert.equal(errors.status, 1, 'an error-severity stdin finding must fail the run');
  assert(JSON.parse(errors.stdout).findings.some(f => f.ruleId === 'UE-TE005'));
  // NUL bytes refuse: the bytes are not the text they claim to be.
  const bad = spawnSync(process.execPath, [cli, '--stdin', '--config', config],
    { input: 'a\u0000b', encoding: 'utf8' });
  assert.equal(bad.status, 2, 'NUL bytes in stdin must refuse with exit 2');
  // Path plus stdin is a usage refusal.
  const both = spawnSync(process.execPath, [cli, '--stdin', 'somewhere.md', '--config', config],
    { input: 'x\n', encoding: 'utf8' });
  assert.equal(both.status, 2, '--stdin with paths must refuse');
}

// --- repeatable --report ------------------------------------------------------

{
  const pdf = write('two-report.pdf', '');
  const html = write('two-report.html', '');
  const result = capture([write('report-src.txt', 'The delegation met on 5 March 2026 in Geneva.\n'),
    '--report', pdf, '--report', html]);
  assert.equal(result.code, 0, result.stderr);
  assert.ok(fs.statSync(pdf).size > 1000, 'the PDF report must be written');
  assert.ok(fs.statSync(html).size > 1000, 'the HTML report must be written');
  const both = result.stdout.match(/Report written/g) || [];
  assert.equal(both.length, 2, 'each report path must be announced once');
}

// --- extraExtensions: project-configured formats ------------------------------

{
  const mdx = write('page.mdx', 'The organization reported results.\n');
  const map = write('ext.json', JSON.stringify({ extraExtensions: { '.mdx': 'markdown' } }));
  // Without the mapping the extension is not collected.
  assert.equal(capture([mdx, '--format', 'json']).code, 2,
    'an unmapped extra extension must stay unsupported');
  const found = json(scan(mdx, '--config', map));
  assert.deepEqual([...new Set(found.findings.map(f => f.ruleId))], ['UE-SP001'],
    'a mapped .mdx must be extracted as Markdown');
  // A bad kind fails closed.
  const bad = write('ext-bad.json', JSON.stringify({ extraExtensions: { '.mdx': 'js' } }));
  assert.equal(capture([mdx, '--config', bad]).code, 2,
    'mapping an extension to script must be refused');
}


// --- organisation profile custom rules ---------------------------------------

{
  const src = write('custom-src.txt', 'The rapporteur submitted the memorandum yesterday.\n');
  const profile = write('custom-profile.json', JSON.stringify({
    profileVersion: 1,
    name: 'House profile',
    source: 'house style board, checked 1 October 2026',
    customRules: [
      { id: 'ORG-001', pattern: 'memorandum', message: 'House style prefers "note verbale" for diplomatic correspondence.', severity: 'warning' },
      { id: 'ORG-002', pattern: 'submitted', message: 'Prefer the active form with a named office.', suggestion: 'Consider "lodged with the secretariat".', source: 'House drafting guide, section 4' },
    ],
  }));
  const result = json(scan(src, '--profile', profile));
  const custom = result.findings.filter(f => f.id && f.id.startsWith('ORG') || f.ruleId.startsWith('ORG-'));
  const byRule = new Map(result.findings.map(f => [f.ruleId, f]));
  assert(byRule.has('ORG-001'), `the custom rule must fire: ${JSON.stringify([...byRule.keys()])}`);
  assert.equal(byRule.get('ORG-001').severity, 'warning');
  assert(byRule.has('ORG-002'), 'the second custom rule must fire');
  // Provenance: the finding names the organisation profile, never a UN rule file.
  assert.match(byRule.get('ORG-002').source, /House drafting guide/);
  // The JSON finding is annotated: the lane is deterministic (deterministic
  // confidence, non-safety category) and the limitation names the lane's
  // honest boundary.
  assert.equal(byRule.get('ORG-002').lane, 'deterministic');
  assert.match(byRule.get('ORG-002').limitation, /Deterministic match/);
  // Suppression: a ue:ignore naming the custom id silences it.
  const suppressed = json(scan(write('custom-sup.txt',
    'The memorandum was circulated. <!-- ue:ignore ORG-001 -->\n'), '--profile', profile));
  assert(!suppressed.findings.some(f => f.ruleId === 'ORG-001'),
    'the custom rule must honour a span suppression');
  // The fixer never rewrites a custom rule: no finding carries a replacement.
  const fixRun = capture([src, '--fix', '--profile', profile]);
  assert.equal(fixRun.code, 0, fixRun.stderr);
  assert(!/proposed/.test(fixRun.stdout), 'a custom rule must never produce a fix diff');

  // Fail-closed validation, each a refusal with exit 2.
  const bad = (name, rule) => {
    const p = write(name, JSON.stringify({
      profileVersion: 1, name: 'x', source: 'x', customRules: [rule],
    }));
    return capture([src, '--profile', p]).code;
  };
  assert.equal(bad('c1.json', { id: 'UE-999', pattern: 'x', message: 'x' }), 2, 'UE- prefix refused');
  assert.equal(bad('c2.json', { id: 'org-1', pattern: 'x', message: 'x' }), 2, 'lowercase id refused');
  assert.equal(bad('c3.json', { id: 'UE-SP001', pattern: 'x', message: 'x' }), 2, 'catalogue id refused');
  assert.equal(bad('c4.json', { id: 'ORG-010', pattern: '(unclosed', message: 'x' }), 2, 'non-compiling pattern refused');
  assert.equal(bad('c5.json', { id: 'ORG-011', pattern: 'x' }), 2, 'missing message refused');
  assert.equal(bad('c6.json', { id: 'ORG-012', pattern: 'x', message: 'x', severity: 'fatal' }), 2, 'bad severity refused');
}


// --- the claim-evidence register ---------------------------------------------

{
  const src = write('claims-src.txt',
    'The programme reached 12,500 households. Coverage rose from 40 per cent in 2022 to 55 per cent in 2024, up from the baseline.\n');
  // The register path must not exist beforehand: --claims-out refuses to
  // replace one without --claims-overwrite, and the extraction below proves
  // the fresh-write path.
  const out = path.join(tmp, 'claims-register.json');

  // Extraction: writes the register and exits 0 whatever the copy looks like.
  const extraction = capture([src, '--claims-out', out]);
  assert.equal(extraction.code, 0, extraction.stderr);
  assert.match(extraction.stdout, /Claim register written/, extraction.stdout);
  const register = JSON.parse(fs.readFileSync(out, 'utf8'));
  assert.equal(register.registerVersion, 1);
  assert(register.entries.length >= 3, `claim-shaped findings must be recorded: ${register.entries.length}`);
  for (const entry of register.entries) {
    assert.equal(entry.source, null, 'a fresh register entry carries no source yet');
  }
  // An existing register is not replaced without --claims-overwrite.
  assert.equal(capture([src, '--claims-out', out]).code, 2, 'overwriting requires the flag');

  // An unfilled register is incomplete: every entry without a source is a finding.
  const verify1 = capture([src, '--claims', out, '--format', 'json']);
  assert.equal(verify1.code, 0, verify1.stderr);
  const v1 = json(verify1);
  assert(v1.findings.some(f => f.ruleId === 'UE-CL002'),
    'an unfilled register must raise UE-CL002');
  assert(v1.findings.some(f => f.ruleId === 'UE-CL003') === false,
    'a register freshly written from this scan has no unregistered claims');

  // Filled entries with a source and date go quiet; a detection the register
  // does not list raises UE-CL003.
  for (const entry of register.entries) { entry.source = 'Annual report'; entry.asOf = '2025-12-31'; }
  const filled = write('claims-filled.json', JSON.stringify(register, null, 2));
  const verify2 = json(capture([src, '--claims', filled, '--format', 'json']));
  assert(!verify2.findings.some(f => f.ruleId === 'UE-CL002'),
    'a filled register must not raise UE-CL002');
  const tampered = write('claims-tampered.json', JSON.stringify({ ...register, entries: [] }));
  const verify3 = json(capture([src, '--claims', tampered, '--format', 'json']));
  assert(verify3.findings.some(f => f.ruleId === 'UE-CL003'),
    'a scan with claims but an empty register must raise UE-CL003');

  // Fail-closed: a wrong version and a corrupt file refuse with exit 2.
  const badVersion = write('claims-bad.json', JSON.stringify({ registerVersion: 9, entries: [] }));
  assert.equal(capture([src, '--claims', badVersion]).code, 2, 'a future register version must refuse');
  assert.equal(capture([src, '--claims', write('claims-not.json', 'not json')]).code, 2,
    'a corrupt register must refuse');
  assert.equal(capture([src, '--claims', out, '--claims-out', out]).code, 2,
    'the two register flags are mutually exclusive');
}


// --- the configuration-gated consistency review (UE-HR008, UE-HR009) ---------

{
  const mixedQuotes = write('consistency-quotes.md',
    'The report states a "clear" position and a “measured” one in the same document.\n');
  const mixedNumbers = write('consistency-numbers.txt',
    'The office reported 1,250 households in the north and 3 500 people in the south.\n');
  const on = write('consistency.json', JSON.stringify({ consistencyReview: true }));

  // Off by default: a mixed document is the house style's own business. The
  // assertion is scoped to the consistency rules — the mixed-numbers copy
  // deliberately trips the sourcing heuristics too.
  assert(!json(scan(mixedQuotes)).findings.some(f => f.ruleId === 'UE-HR008'),
    'HR008 must be silent while consistencyReview is off');
  assert(!json(scan(mixedNumbers)).findings.some(f => f.ruleId === 'UE-HR009'),
    'HR009 must be silent while consistencyReview is off');

  const quotes = json(scan(mixedQuotes, '--config', on));
  const quoteFinding = quotes.findings.find(f => f.ruleId === 'UE-HR008');
  assert(quoteFinding, 'mixed quotation styles must be reported when the review runs');
  assert.equal(quoteFinding.severity, 'info', 'the consistency note names the inconsistency, never a winner');

  const numbers = json(scan(mixedNumbers, '--config', on));
  const numberFinding = numbers.findings.find(f => f.ruleId === 'UE-HR009');
  assert(numberFinding, 'mixed thousands separators must be reported when the review runs');
  assert.match(numberFinding.message, /1,250/, 'the message quotes the comma-grouped example');
  assert.match(numberFinding.message, /3 500/, 'the message quotes the space-grouped example');

  // A consistent document stays silent under the review.
  const consistent = write('consistency-clean.txt',
    'The office reported 1,250 households in the north and 3,500 people in the south.\n');
  const clean = json(scan(consistent, '--config', on));
  assert(!clean.findings.some(f => f.ruleId === 'UE-HR009'),
    'a consistent document must stay silent');
}

// --- exit codes --------------------------------------------------------------

assert.equal(scan(write('clean.txt', 'The organisation reports the figure.\n')).code, 0);
assert.equal(scan(fixture('positive', 'nu002.txt')).code, 0, 'warnings alone must not fail the run');
assert.equal(scan(fixture('positive', 're005.txt')).code, 1, 'error-severity findings must fail the run');
for (const argv of [['--format', 'xml'], ['--config'], ['--bogus'], ['no-such-path'], ['--apply']]) {
  assert.equal(capture(argv).code, 2, `usage error must exit 2: ${argv.join(' ')}`);
}
assert.equal(capture(['--quiet', fixture('fix', 'protected.md'), '--fix']).code, 2,
  '--quiet with a --fix preview must be refused: showing the diff is the point');

// --- positions: the offset map points at the copy, not at a masked region ----

{
  const line = 'Read https://example.test/a-very-long-path and organization here.';
  const finding = json(scan(write('position.txt', `${line}\n`))).findings[0];
  assert(finding, 'expected a finding');
  assert.equal(finding.line, 1);
  assert.equal(finding.column, line.indexOf('organization') + 1,
    'column must point at the word, not at the masked URL before it');
}

{
  const lines = ['First line is clean.', 'Second line has organization here.', ''];
  const finding = json(scan(write('position-lines.txt', lines.join('\n')))).findings[0];
  assert.equal(finding.line, 2);
  assert.equal(finding.column, lines[1].indexOf('organization') + 1);
}

{
  // HTML entities decode to one character: without an offset map the reported
  // column would drift by four for every `&amp;`.
  const line = '<p>A &amp; B organization here.</p>';
  const finding = json(scan(write('position-entity.html', `${line}\n`))).findings[0];
  assert(finding, 'expected a finding');
  assert.equal(finding.line, 1);
  assert.equal(finding.column, line.indexOf('organization') + 1,
    'entity decoding must not shift the reported position');
}

{
  // An attribute value maps back to the character inside the quotes.
  const line = '<p title="organization">Body</p>';
  const finding = json(scan(write('position-attr.html', `${line}\n`))).findings[0];
  assert(finding, 'expected a finding');
  assert.equal(finding.column, line.indexOf('organization') + 1);
}

// --- suppressions ------------------------------------------------------------

const suppressions = [
  ['The organization reports. <!-- ue:ignore UE-SP001 -->', []],
  ['The organization reports. <!-- ue:ignore UE-SP* -->', []],
  ['The organization reports. <!-- ue:ignore all -->', []],
  ['The organization reports. <!-- ue:ignore UE-TE003 -->', ['UE-SP001']],
  ['The organization reports 25%. <!-- ue:ignore UE-SP001,UE-TE003,UE-RE003 -->', []],
];
suppressions.forEach(([body, expected], index) => {
  const result = scan(write(`suppress-${index}.md`, `${body}\n`));
  assert.deepEqual(ids(result), expected, body);
});

{
  // A suppression belongs to the paragraph that contains it.
  const body = 'The organization reports. <!-- ue:ignore UE-SP001 -->\n\nThe organization reports again.\n';
  assert.deepEqual(ids(scan(write('suppress-leak.md', body))), ['UE-SP001'],
    'a suppression must not leak into the next paragraph');
}

// --- the Phase 2 families honour suppressions and configuration --------------

{
  const cases = [
    ['UE-HS001', 'Foreigners are vermin.'],
    ['UE-RE006', 'The envoy dismissed the amendment as a total sham and labelled the rapporteur a clown.'],
    ['UE-GR001', 'The delegation reviewed the the same draft of the resolution.'],
  ];
  for (const [rule, body] of cases) {
    assert.deepEqual(ids(scan(write(`suppress-${rule}.md`, `${body} <!-- ue:ignore ${rule} -->\n`))), [],
      `${rule} must accept a ue:ignore suppression`);
  }

  // Disabling a new rule through configuration silences it over its own fixture.
  const off = write('gr-off.json', JSON.stringify({ rules: { 'UE-GR001': { enabled: false } } }));
  assert.deepEqual(ids(scan(fixture('positive', 'gr001-doubled.txt'), '--config', off)), [],
    'config.rules enabled:false must silence UE-GR001');

  // Downgrading a new error rule flips the exit code of its fixture.
  const down = write('hs-downgrade.json', JSON.stringify({ severities: { 'UE-HS001': 'warning' } }));
  const file = fixture('positive', 'hs001-dehumanising.txt');
  assert.equal(scan(file).code, 1, 'the UE-HS001 fixture exits 1 at error severity');
  assert.equal(scan(file, '--config', down).code, 0,
    'config.severities must downgrade UE-HS001 to warning');
}

// --- W2 detection contract locks (guards: rules/hate-speech.md, rules/terminology.md) ---

{
  // UE-HS003 guard note: a modal outcome counts only when it ends its clause
  // or continues into an exclusion phrase — operational copy stays silent.
  const operational = [
    'Refugees should go through the registration process at the border.\n',
    'Migrants must leave their documents at the checkpoint.\n',
    'Refugees must go to the reception centre.\n',
  ];
  for (const [index, sentence] of operational.entries()) {
    assert.deepEqual(ids(scan(write(`hs003-operational-${index}.txt`, sentence))), [],
      `${sentence.trim()} must produce no findings`);
  }
  // The exclusion continuation keeps firing, and `current` spans the whole phrase.
  const exclusion = json(scan(write('hs003-continuation.txt', 'Foreigners should leave the country.\n')));
  const hs003 = exclusion.findings.find(f => f.ruleId === 'UE-HS003');
  assert(hs003, `UE-HS003 must fire on an exclusion continuation: ${exclusion.stdout}`);
  assert.equal(hs003.current, 'Foreigners should leave the country');
}

{
  // UE-TE004 guard note: a bare US at sentence final position is reported
  // like any other occurrence, and the documented exemptions stay silent.
  const finding = json(scan(write('te004-sentence-final.txt', 'Coverage was 1990-2025 in the US.\n')))
    .findings.find(f => f.ruleId === 'UE-TE004');
  assert(finding, 'a sentence-final bare US must be reported');
  assert.equal(finding.current, 'US');
  assert.deepEqual(ids(scan(fixture('negative', 'te004-exempt.txt'))), [],
    'the UE-TE004 exemptions must stay silent');
}

// --- quotations and cited titles are never checked or rewritten --------------

assert.deepEqual(ids(scan(write('quote.txt', '> The organization reports.\n'))), []);
assert.deepEqual(ids(scan(write('cite.md', 'See <cite>Organization of African Unity</cite> here.\n'))), []);

// --- the doubled-space review (UE-GR004) is configuration-gated --------------

{
  const spaced = 'The delegation met   twice in the quarter.\n';
  // Off by default: the aligned plain-text annex stays a formatting choice.
  assert.deepEqual(ids(scan(write('gr004-off.txt', spaced))), [],
    'UE-GR004 must be silent while spacingReview is off');
  // On: interior runs fire, the replacement is a single space, and the
  // position points at the run.
  const on = write('gr004-on.json', JSON.stringify({ spacingReview: true }));
  const found = json(scan(write('gr004-on.txt', spaced), '--config', on))
    .findings.filter(f => f.ruleId === 'UE-GR004');
  assert.equal(found.length, 1, `one doubled-space finding expected: ${found.length}`);
  assert.equal(found[0].line, 1);
  assert.equal(found[0].current, '   ');
  // A run a line break closes is a Markdown hard-break marker, not a defect;
  // the interior run on the last line still fires.
  const breaks = fs.readFileSync(fixture('negative', 'gr004-md-hard-break.md'), 'utf8');
  const hardBreak = write('gr004-hardbreak.md', `${breaks}The trailing run  here is interior.\n`);
  const mixed = json(scan(hardBreak, '--config', on)).findings.filter(f => f.ruleId === 'UE-GR004');
  assert.equal(mixed.length, 1, 'only the interior run may fire');
  assert.equal(mixed[0].line, 4, 'the hard-break lines must stay silent');
  // The fixer collapses the whole run through the raw span, not just one space.
  const fixResult = capture([write('gr004-fix.txt', 'Met   twice  this quarter.\n'), '--fix', '--apply', '--config', on]);
  assert.equal(fixResult.code, 0, fixResult.stderr);
  assert.equal(fs.readFileSync(path.join(tmp, 'gr004-fix.txt'), 'utf8'),
    'Met twice this quarter.\n', 'both runs collapse to a single space');
}

// --- the padded doubled word (UE-GR001) is proved against the raw span -------

{
  const found = json(scan(write('gr001-padded.txt', 'The  the report was delayed.\n')))
    .findings.filter(f => f.ruleId === 'UE-GR001');
  assert.equal(found.length, 1, 'a doubled word padded with extra spaces is still a doubled word');
  assert.equal(found[0].current, 'The the');
  // The fix deletes one copy and the whole padded span: the re-scan is clean.
  const fixResult = capture([write('gr001-padded-fix.txt', 'The  the report was delayed.\n'), '--fix', '--apply']);
  assert.equal(fixResult.code, 0, fixResult.stderr);
  assert.equal(fs.readFileSync(path.join(tmp, 'gr001-padded-fix.txt'), 'utf8'),
    'The report was delayed.\n', 'the fix removes both the word and the extra spaces');
  // A hard-wrapped join produces the same collapsed text and must stay silent:
  // the space the rules see is a line join, not a defect.
  assert.deepEqual(ids(scan(write('gr001-join.txt', 'The\nthe report was delayed.\n'))), [],
    'a hard-wrapped join must never read as a doubled word');
}

// --- the written month-first date (UE-NU001) --------------------------------

{
  const found = json(scan(write('nu001-written.txt', 'The committee met on March 5, 2026.\n')))
    .findings.filter(f => f.ruleId === 'UE-NU001');
  assert.equal(found.length, 1);
  assert.equal(found[0].current, 'March 5, 2026');
  assert.equal(found[0].proposed, '5 March 2026');
  // The correct order, a month-year reference and an abbreviated month stay
  // silent; the negative corpus fixture carries the same guarantees.
  assert.deepEqual(ids(scan(fixture('negative', 'nu001-day-first.txt'))), []);
}

// --- fenced blocks in plain text are out of reach ----------------------------

{
  // The fence must open on its marker line, not close on it: when the open
  // and close patterns are identical, the marker used to collapse its own
  // region and the body below it reached the rules and the fixer.
  const body = [
    'The US reported 45% in the intro.',
    '',
    '```text',
    'The US reported 45% inside the fence.',
    '```',
    '',
  ].join('\n');
  const result = json(scan(write('fence-body.txt', body)));
  assert(result.findings.length > 0, 'the intro line outside the fence must be checked');
  assert(result.findings.every(f => f.line === 1),
    `findings may only come from outside the fence: ${JSON.stringify(result.findings.map(f => [f.ruleId, f.line]))}`);

  assert.deepEqual(ids(scan(write('fence-open.txt', '```text\nThe US reported 45% in the open fence.\n'))), [],
    'a fence left open masks to the end of the file');

  // The reported --fix regression: a fenced body must survive --apply byte
  // for byte, because no finding may exist inside the fence for a fix to use.
  const fenced = 'Intro line.\n\n```text\nThe US delivered 45% of the supplies.\n```\n';
  const target = write('fence-fix.txt', fenced);
  const applied = capture([target, '--fix', '--apply']);
  assert.equal(applied.code, 0, `a fully fenced file has nothing to fix: ${applied.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'), fenced, 'no part of a fenced block may ever be rewritten');
}

// --- --fix -------------------------------------------------------------------

{
  const target = write('protected-copy.md', fs.readFileSync(fixture('fix', 'protected.md'), 'utf8'));
  const before = fs.readFileSync(target, 'utf8');

  const preview = capture([target, '--fix']);
  assert.equal(preview.code, 1, `preview must report the un-fixed errors: ${preview.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'), before, 'a preview must never write');
  assert.match(preview.stdout, /\(proposed\)/);
  assert.match(preview.stdout, /FIXABLE — \d+ replacement/);

  const applied = capture([target, '--fix', '--apply']);
  assert.equal(applied.code, 0, `every fixable error was applied: ${applied.stderr}`);
  assert.match(applied.stdout, /\(applied\)/);
  assert.match(applied.stdout, /^APPLIED — /m);
  assert.equal(fs.readFileSync(target, 'utf8'), [
    'The colour inside <cite>Organization</cite> and colour outside.',
    '',
    'See "Organization of African Unity" for detail, and colour in prose.',
    '',
    'Read https://example.test/organization and colour again.',
    '',
    '> organization quoted here',
    '',
    '<!-- organization in a comment -->',
    '',
    'Colour at last.',
    '',
  ].join('\n'), 'only bare prose may be rewritten');
}

// Terminology never enters the --fix set, so UE-TE004's own fixture must come
// back byte-identical and still fail the run: an error that cannot be written
// is exactly what the exit-code contract promises (README "The safe --fix
// boundary").
{
  const target = write('fix-states.txt', fs.readFileSync(fixture('fix', 'states.txt'), 'utf8'));
  const before = fs.readFileSync(target, 'utf8');
  const result = capture([target, '--fix', '--apply']);
  assert.equal(result.code, 1, `states.txt: an unfixed error must still exit 1: ${result.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'), before,
    'states.txt: --fix must never rewrite bare US');
}
{
  const target = write('fix-ranges.txt', fs.readFileSync(fixture('fix', 'ranges.txt'), 'utf8'));
  const result = capture([target, '--fix', '--apply']);
  assert.equal(result.code, 0, `ranges.txt: ${result.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'),
    'Coverage was 1990–2025 and reached 25% of the total.\n',
    'only the en-dash range may be rewritten: UE-TE003 no longer owns the sign');
}

// Non-prose files are refused with exit code 2 and left untouched.
for (const name of ['page.html', 'script.js']) {
  const target = write(`refuse-${name}`, fs.readFileSync(fixture('fix', name), 'utf8'));
  const before = fs.readFileSync(target, 'utf8');
  const result = capture([target, '--fix', '--apply']);
  assert.equal(result.code, 2, `${name} must be refused`);
  assert.match(result.stderr, /refusing --fix/);
  assert.equal(fs.readFileSync(target, 'utf8'), before, `${name} must not be rewritten`);
}

// Judgement calls are never auto-corrected: an error-severity rule without a
// deterministic replacement still exits 1 and still writes nothing.
{
  const target = write('no-auto.txt', 'Coverage reached a record level!\n');
  const before = fs.readFileSync(target, 'utf8');
  const result = capture([target, '--fix', '--apply']);
  assert.equal(result.code, 1, 'a non-fixable error must still fail the run');
  assert.doesNotMatch(result.stdout, /APPLIED/);
  assert.equal(fs.readFileSync(target, 'utf8'), before);
}

// Link safety: symlinks and hard links are refused before anything is written.
{
  const target = write('link-target.txt', 'organization\n');
  const link = path.join(tmp, 'link.txt');
  try { fs.symlinkSync(target, link); } catch { /* platforms without symlink permission */ }
  if (fs.existsSync(link)) {
    const result = capture([link, '--fix', '--apply']);
    assert.equal(result.code, 2, 'a symbolic link must be refused');
    assert.match(result.stderr, /symbolic link/i);
    assert.equal(fs.readFileSync(target, 'utf8'), 'organization\n');
  }
}
{
  const target = write('hard-target.txt', 'organization\n');
  const link = path.join(tmp, 'hard.txt');
  fs.linkSync(target, link);
  const result = capture([target, '--fix', '--apply']);
  assert.equal(result.code, 2, 'a hard-linked file must be refused');
  assert.match(result.stderr, /hard[- ]link/i);
  assert.equal(fs.readFileSync(target, 'utf8'), 'organization\n');
  assert.equal(fs.readFileSync(link, 'utf8'), 'organization\n');
}

// --- spelling review and allowlists -----------------------------------------

{
  const review = write('review.json', JSON.stringify({ spellingReview: true }));
  const file = write('ize.txt', 'The report optimizes results.\n');
  assert.deepEqual(ids(scan(file)), [], 'the -ize review is opt-in');
  assert.deepEqual(ids(scan(file, '--config', review)), ['UE-SP003']);
  assert.equal(scan(file, '--config', review).code, 0, 'notes must not fail the run');
  // Sentence-initial capitals are reviewed like any other occurrence.
  const upper = write('ize-upper.txt', 'Optimize the annexes before publication.\n');
  assert.deepEqual(ids(scan(upper, '--config', review)), ['UE-SP003'],
    'a sentence-initial -ize form must be reviewed too');
  // Words that end in -ize without being spelling variants are never flagged.
  const nonCandidate = write('ize-noncandidate.txt', 'The file size grew. She won a prize for it.\n');
  assert.deepEqual(ids(scan(nonCandidate, '--config', review)), [],
    'size and prize are not -ise candidates');
}
// A qualifier must sit in the count's own sentence: a hedge in the next
// sentence must not cover an unqualified figure.
{
  const cross = write('di001-cross.txt', 'The dashboard covers 127 countries. The total is confirmed.\n');
  assert.deepEqual(ids(scan(cross)), ['UE-DI001'],
    'a qualifier in the following sentence must not excuse the count');
  const same = write('di001-same.txt', 'The survey covered 127 countries in total.\n');
  assert.deepEqual(ids(scan(same)), [], 'a qualifier in the same sentence satisfies the rule');
}
{
  const allowed = write('allowed.json', JSON.stringify({ allowlist: { spellings: ['organization'] } }));
  assert.deepEqual(ids(scan(write('allowed.txt', 'The organization reports.\n'), '--config', allowed)), []);
}

// A single unhedged figure in one clause must not condemn a hedged figure in
// the next.
{
  const clauses = write('clauses.txt', 'Approximately 10 per cent. The other value was 20 per cent.\n');
  assert.deepEqual(ids(scan(clauses)), ['UE-RE003']);
}

// --- profiles ----------------------------------------------------------------

{
  const missing = scan(fixture('positive', 'sp001.txt'), '--profile', 'does-not-exist.json');
  assert.equal(missing.code, 2, 'a missing profile must fail loudly');
  assert.match(missing.stderr, /profile not found/);
}

// Opt-in audits: no audit rule ever runs without being asked for.
{
  const result = scan(fixture('audits', 'publishing-long.html'));
  assert.deepEqual(ids(result), [], 'audits are opt-in');
  assert.equal(result.code, 0);
}
{
  // The security fixture is generated at runtime (tests/lib/make-security-
  // fixture.mjs) so the repository tree carries no sink-shaped text for an
  // external scanner to flag; the profile still sees the full sink texts.
  const securityFixture = write('audit-security.mjs', SECURITY_FIXTURE_SOURCE);
  const result = scan(securityFixture, '--profile', 'security');
  assert.deepEqual(ids(result), ['UE-SE001', 'UE-SE004']);
  assert(result.stdout.includes('"audit": "security"'), 'audit findings must be tagged');
  assert.equal(result.code, 0, 'audits never change the exit code');
  assert.match(capture([securityFixture, '--profile', 'security']).stdout,
    /OPTIONAL AUDIT — security/);
}
// The shape of that fixture is a lock, not a style preference. It holds its
// two sinks as quoted data so that it contains no executable sink at all — a
// reader parsing it as code finds no HTML assignment and no dynamic execution,
// which is what a scanner reporting on this repository is entitled to see. The
// block above proves the profile is not weakened by that: matching happens on
// masked text, so the quoted sinks still fire both ids. Both halves are
// asserted, because either one alone would let the fixture drift into being
// either unscannable or live.
{
  // The shape lock now reads the generated file, and additionally proves the
  // generator: no contiguous sink sequence may exist in the repository source
  // either, which is the whole reason the fixture is assembled from fragments.
  const source = fs.readFileSync(
    path.join(tmp, 'audit-security.mjs'), 'utf8');
  // Strings first, then line comments: what remains is the code a parser sees.
  const live = source
    .replace(/'(?:\\[\s\S]|[^'\\])*'/g, "''")
    .replace(/\/\/[^\n]*/g, '');
  assert.doesNotMatch(live, /\.(innerHTML|outerHTML)\s*=/,
    'the security fixture must carry no live HTML sink outside a string literal');
  assert.doesNotMatch(live, /\beval\s*\(|new\s+Function\s*\(/,
    'the security fixture must carry no live dynamic-execution sink outside a string literal');
  assert.match(source, /\.(innerHTML|outerHTML)\s*=/,
    'the fixture still carries the HTML sink text the profile must find');
  assert.match(source, /\beval\s*\(/,
    'the fixture still carries the dynamic-execution sink text the profile must find');
  const generator = fs.readFileSync(
    path.join(root, 'tests', 'lib', 'make-security-fixture.mjs'), 'utf8');
  assert.doesNotMatch(generator, /\.innerHTML\s*=|\beval\s*\(/,
    'the generator itself must hold no contiguous sink sequence');
}
{
  const result = scan(fixture('audits', 'accessibility.html'), '--profile', 'accessibility');
  assert.deepEqual(ids(result), ['UE-AX001', 'UE-AX002']);
  assert.equal(result.code, 0);
}
{
  const result = scan(fixture('audits', 'publishing-missing.html'), '--profile', 'publishing');
  assert.deepEqual(ids(result), ['UE-EO001', 'UE-EO002', 'UE-EO003', 'UE-EO004', 'UE-EO005']);
  const origin = write('origin.json', JSON.stringify({ baseOrigin: 'https://example.test' }));
  const long = scan(fixture('audits', 'publishing-long.html'), '--profile', 'publishing', '--config', origin);
  assert.deepEqual(ids(long), ['UE-EO001', 'UE-EO002', 'UE-EO003', 'UE-EO004', 'UE-EO005']);
}
{
  // Every bundled audit can be requested at once, and still never fails the run.
  const result = scan(fixture('audits', 'publishing-missing.html'),
    '--profile', 'publishing', '--profile', 'accessibility', '--profile', 'security');
  assert(result.stdout.includes('"audit"'));
  assert.equal(result.code, 0);
  assert.deepEqual(ids(scan(fixture('audits', 'security.html'), '--profile', 'security')),
    ['UE-SE002', 'UE-SE003']);
}

// An organisation profile merges over the bundled United Nations baseline.
{
  const profile = write('custom-profile.json', JSON.stringify({
    profileVersion: 1,
    name: 'Custom',
    source: 'fixture',
    spelling: { organization: 'organisation-custom' },
    // Enforce the conflict family: a custom profile without the field would
    // inherit the baseline stance and accept it silently.
    spellingConflicts: [],
    terminology: { forbidden: [['old term', 'current term']] },
    register: { forbidden: ['bad phrase'] },
  }));
  const file = write('custom.txt', 'The organization, old term and bad phrase are used.\n');
  const result = capture([file, '--format', 'json', '--profile', profile]);
  assert.deepEqual(ids(result), ['UE-RE001', 'UE-SP001', 'UE-TE001']);
  const spelling = json(result).findings.find(finding => finding.ruleId === 'UE-SP001');
  assert.equal(spelling.suggestion, 'Use "organisation-custom".');
}

// A profile must not leak into the next run in the same process.
{
  const profileA = write('profile-a.json', JSON.stringify({
    profileVersion: 1, name: 'A', source: 'fixture', spelling: { color: 'colour-custom' },
  }));
  const file = write('leak.txt', 'The color reports.\n');
  assert.equal(capture([file, '--format', 'json', '--profile', profileA]).code, 1);
  const baseline = scan(file);
  assert.equal(baseline.code, 1);
  assert.equal(json(baseline).findings[0].suggestion, 'Use "colour".',
    'a profile from an earlier run leaked into the baseline');
}

{
  // Shapes the contested-claims knowledge base must reject: a claim entry is
  // all required fields (the source citation is what makes it reviewable) and
  // patterns may only use the {subject}/{claimant} placeholders with their own
  // literal claim wording between them.
  const claim = (overrides = {}) => ({
    id: 'DP-X', topic: 'Test Region', subjects: ['Test Region'], claimants: ['Testland'],
    patterns: ['{subject} is part of {claimant}'],
    neutral: 'the disputed territory of Test Region',
    unTerminology: 'the question of Test Region',
    source: 'fixture source',
    ...overrides,
  });
  const invalidShapes = [
    {},
    { profileVersion: 1, name: '', source: 'x' },
    { profileVersion: 1, name: 'x', source: 'y', extra: true },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: '' } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: ['organisation'] } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: null } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { bogus: 'x' } },
    { profileVersion: 1, name: 'x', source: 'y', terminology: { unknown: [], forbidden: [['old', '']] } },
    { profileVersion: 1, name: 'x', source: 'y', register: { unknown: [] } },
    { profileVersion: 1, name: 'x', source: 'y', rules: { 'UE-RE003': { enabled: true, extra: true } } },
    { profileVersion: 1, name: 'x', source: 'y', pageUrl: '/relative' },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: 'nope' },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { unknown: [] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: 'nope' } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [{}] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim(), claim()] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ source: '' })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ neutral: '  ' })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ subjects: [] })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ patterns: ['{subject}'] })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ patterns: ['{subject} is part of {bogus}'] })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ patterns: [' is part of {claimant}'] })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ patterns: ['{subject} is part of {claimant}'], claimants: [] })] } },
    { profileVersion: 1, name: 'x', source: 'y', diplomacy: { claims: [claim({ bogus: true })] } },
    { auditVersion: 1, name: 'security', category: 'nope', rules: ['UE-SE001'] },
    { auditVersion: 1, name: 'security', category: 'security', rules: ['UE-NOPE'] },
  ];
  const file = fixture('positive', 'sp001.txt');
  invalidShapes.forEach((shape, index) => {
    const bad = write(`invalid-profile-${index}.json`, JSON.stringify(shape));
    const result = capture([file, '--profile', bad, '--format', 'json']);
    assert.equal(result.code, 2, `expected exit 2 for ${JSON.stringify(shape)}\n${result.stderr}`);
  });
}

// --- contested claims: UE-DP001 -----------------------------------------------

{
  // Every finding carries what is currently written and what should replace
  // it: the two halves of the current-to-should-be report.
  const finding = json(scan(fixture('positive', 'dp001.txt'))).findings[0];
  assert.equal(finding.ruleId, 'UE-DP001');
  assert.equal(finding.current, 'Kashmir is part of India');
  assert.equal(finding.proposed, 'the disputed territory of Jammu and Kashmir');
  // Wave 3: contested claims are warnings that require diplomatic review;
  // the guard note rules/diplomacy.md and the catalogue carry the flip.
  assert.equal(finding.severity, 'warning');
  assert.equal(finding.lane, 'diplomacy', 'contested claims land in the diplomacy lane');
  assert.match(finding.action, /diplomatic review/i,
    `the finding must route the reader to diplomatic review: ${finding.action}`);
  assert.match(finding.suggestion, /Security Council resolution 47 \(1948\)/,
    `the finding must cite its source: ${finding.suggestion}`);
}
{
  // Deterministic replacements elsewhere report both halves too.
  const finding = json(scan(fixture('positive', 'sp001.txt'))).findings[0];
  assert.equal(finding.current, 'color');
  assert.equal(finding.proposed, 'colour');
}
{
  // A single claim can be opted out of by id without touching the others.
  const file = write('claim-opt.txt', 'Kashmir is part of India.\n');
  assert.deepEqual(ids(scan(file)), ['UE-DP001']);
  const allowed = write('claim-allow.json', JSON.stringify({ allowlist: { claims: ['DP-KASHMIR'] } }));
  assert.deepEqual(ids(scan(file, '--config', allowed)), []);
}
{
  // Escalating the rule to error makes the finding fail the run; the Wave 3
  // default (warning) keeps a status-sensitivity judgement advisory — the
  // finding requires diplomatic review, it never claims the text is false.
  const file = write('claim-severity.txt', 'Kashmir is part of India.\n');
  const advisory = scan(file);
  assert.deepEqual(ids(advisory), ['UE-DP001']);
  assert.equal(json(advisory).findings[0].severity, 'warning',
    'the default severity is a diplomatic-review warning');
  assert.equal(advisory.code, 0, 'a status-sensitivity warning alone must not fail the run');
  const escalate = write('claim-severity.json', JSON.stringify({ severities: { 'UE-DP001': 'error' } }));
  const result = scan(file, '--config', escalate);
  assert.deepEqual(ids(result), ['UE-DP001']);
  assert.equal(json(result).findings[0].severity, 'error',
    'a config severity override must reach the finding as a plain severity');
  assert.equal(result.code, 1, 'an escalated claim must fail the run');
}
{
  // ue:ignore suppresses the rule in its copy span like any other.
  const file = write('claim-ignore.md', 'Kashmir is part of India. <!-- ue:ignore UE-DP001 -->\n');
  assert.deepEqual(ids(scan(file)), []);
}
{
  // An organisation profile adds a claim the baseline does not know and
  // replaces the baseline entry it names.
  const profile = write('claims-profile.json', JSON.stringify({
    profileVersion: 1, name: 'Claims', source: 'fixture',
    diplomacy: {
      claims: [
        {
          id: 'DP-TESTREGION', topic: 'Test Region',
          subjects: ['Test Region'], claimants: ['Testland'],
          patterns: ['{subject} is part of {claimant}'],
          neutral: 'the disputed territory of Test Region',
          unTerminology: 'the question of Test Region',
          source: 'fixture source',
        },
        {
          id: 'DP-KASHMIR', topic: 'Jammu and Kashmir',
          subjects: ['Kashmir'], claimants: ['India'],
          patterns: ['{subject} is sovereign territory of {claimant}'],
          neutral: 'the disputed territory of Jammu and Kashmir',
          unTerminology: 'the question of Jammu and Kashmir',
          source: 'fixture source',
        },
      ],
    },
  }));
  const added = write('claim-added.txt', 'Test Region is part of Testland.\n');
  assert.deepEqual(ids(scan(added)), [], 'the baseline does not know this claim');
  assert.deepEqual(ids(scan(added, '--profile', profile)), ['UE-DP001']);
  const replaced = write('claim-replaced.txt', 'Kashmir is part of India.\n');
  assert.deepEqual(ids(scan(replaced, '--profile', profile)), [],
    'an organisation claim replaces the baseline entry with the same id');
}

// --- configuration validation ------------------------------------------------

const configErrors = [
  [{ baseOrigin: 'ftp://example.test' }, /baseOrigin must be an absolute http\(s\) URL/i],
  [{ baseOrigin: 'javascript:alert(1)' }, /baseOrigin must be an absolute http\(s\) URL/i],
  [{ baseOrigin: '/relative' }, /baseOrigin must be an absolute URL/i],
  [{ baseOrigin: null, spellingReview: 'false' }, /spellingReview must be a boolean/i],
  [{ allowlist: [] }, /allowlist must be an object/i],
  [{ allowlist: { spellings: 'organization' } }, /allowlist\.spellings must be an array/i],
  [{ allowlist: { claims: 'DP-KASHMIR' } }, /allowlist\.claims must be an array/i],
  [{ rules: [] }, /rules must be an object/i],
  [{ severities: 'error' }, /severities must be an object/i],
  [{ severities: { 'UE-NOPE': 'error' } }, /severities contains unknown rule/i],
  [{ unknownSetting: true }, /unknown fields: unknownSetting/],
  [{ ignoredPaths: 'dist' }, /ignoredPaths must be an array/i],
  [{ renderTargets: ['has space'] }, /must be an identifier/i],
];
for (const [settings, pattern] of configErrors) {
  const file = write(`invalid-config-${Math.random().toString(36).slice(2)}.json`, JSON.stringify(settings));
  const result = capture(['--config', file]);
  assert.equal(result.code, 2, `${JSON.stringify(settings)}: ${result.stderr}`);
  assert.match(result.stderr, pattern, `${JSON.stringify(settings)} -> ${result.stderr}`);
}
{
  const malformed = write('malformed.json', '{');
  assert.equal(capture(['--config', malformed]).code, 2);
}
{
  // JSON.parse keeps only the last duplicate value, so the parsed tree can
  // never show a duplicate — fail-closed rejection has to read the raw text.
  const dup = write('dup-keys.json', '{"spellingReview": false, "spellingReview": true}');
  const result = capture(['--config', dup]);
  assert.equal(result.code, 2, 'a duplicate-key config must fail closed');
  assert.match(result.stderr, /duplicate keys: spellingReview/);
  assert.throws(() => parseJsonStrict('{"a": {"x": 1, "x": 2}}', 'nested.json'),
    /duplicate keys: x/, 'a nested duplicate must be rejected too');
  // Strings that merely contain separators are values, not keys.
  assert.deepEqual(parseJsonStrict('{"a": "key: {value}", "b": [1, 2]}', 'ok.json'),
    { a: 'key: {value}', b: [1, 2] });
}

// --- ignored paths and directory walking -------------------------------------

{
  write('ignore/node_modules/a.txt', 'organization\n');
  write('ignore/node_modules-copy/a.txt', 'organization\n');
  write('ignore/.hidden/a.txt', 'organization\n');
  const cfg = write('ignore-config.json', JSON.stringify({ ignoredPaths: ['node_modules/**'] }));
  const result = capture([path.join(tmp, 'ignore'), '--format', 'json', '--config', cfg]);
  const parsed = JSON.parse(result.stdout);
  assert.deepEqual(parsed.findings.map(f => f.file.replace(/\\/g, '/').split('/').slice(-3).join('/')),
    ['ignore/node_modules-copy/a.txt'],
    `only the sibling directory must be scanned: ${result.stdout}`);
  assert.equal(parsed.files, 1, 'node_modules and hidden directories must be skipped');
}

// A directory scan never picks up files the extractor cannot read.
{
  const dir = path.join(tmp, 'extensions');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'style.css'), 'organization\n');
  fs.writeFileSync(path.join(dir, 'data.json'), '{"label":"organization"}\n');
  fs.writeFileSync(path.join(dir, 'page.txt'), 'organization\n');
  const parsed = JSON.parse(capture([dir, '--format', 'json']).stdout);
  assert.equal(parsed.files, 1, `only the .txt file is extractable: ${JSON.stringify(parsed)}`);
  assert.deepEqual([...new Set(parsed.findings.map(f => f.ruleId))], ['UE-SP001']);
}

// --- output ------------------------------------------------------------------

{
  const result = capture([fixture('positive', 're002.js')]);
  assert.equal(result.code, 0);
  assert.match(result.stdout, /AGENT REVIEW REQUIRED \(\d+\)/);
}
{
  const result = capture([fixture('positive', 'nu002.txt')]);
  assert.match(result.stdout, /EDITORIAL WARNINGS \(1\)/);
  assert.doesNotMatch(result.stdout, /EDITORIAL ERRORS/);
}
{
  const result = capture([fixture('positive', 'sp001.txt')]);
  assert.match(result.stdout, /EDITORIAL ERRORS \(1\)/);
  assert.match(result.stdout, /un-editorial-check \d+\.\d+\.\d+/);
}
{
  const clean = capture([write('clean-out.txt', 'The organisation reports the figure.\n')]);
  assert.match(clean.stdout, /No findings under the enabled, documented local rules\./);
}

// Internal bookkeeping never reaches a consumer.
for (const format of ['json', 'sarif']) {
  const parsed = JSON.parse(capture([fixture('positive', 'sp001.txt'), '--format', format]).stdout);
  const text = JSON.stringify(parsed);
  for (const internal of ['_unit', '_index', '_matched', '_offset', '_replacement']) {
    assert(!text.includes(`"${internal}"`), `${internal} leaked into ${format} output`);
  }
  assert.equal(format === 'json' ? 'findings' in parsed : 'runs' in parsed, true);
}

{
  const jsonReport = json(capture([fixture('positive', 'sp001.txt'), '--format', 'json']));
  const sarif = json(capture([fixture('positive', 'sp001.txt'), '--format', 'sarif']));
  assert.equal(sarif.runs[0].tool.driver.version, jsonReport.version);
  assert(sarif.runs[0].results[0].locations[0].physicalLocation.region.startLine >= 1);
  assert.equal(sarif.runs[0].results[0].properties.scope, 'user-visible-copy');
}

// Control characters in file names and content are escaped, never emitted raw.
{
  const controls = 'A\x0B B\x7F C\n';
  const file = write(`ctl ${String.fromCharCode(27)} name.txt`, `The color ${controls}\n`); // ue:ignore UE-SP001  (deliberate test data)
  const result = capture([file]);
  assert.equal(result.code, 1);
  // The report may contain line breaks, nothing else.
  assert.doesNotMatch(result.stdout, /[\x00-\x08\x0b-\x1f\x7f]/);
  assert(result.stdout.includes('\\u001b') || result.stdout.includes('\\x1b'),
    `missing escaped ESC in: ${result.stdout}`);
}
{
  const dirty = write('dirty.txt', 'The US uses boom and organization.​‮');
  for (const format of ['json', 'sarif']) {
    const result = capture([dirty, '--format', format]);
    assert.doesNotThrow(() => JSON.parse(result.stdout));
    assert.doesNotMatch(result.stdout, /[​‮]/);
  }
}

// Entity decoding must not distort a rendered-length audit.
{
  const source = '<!doctype html><html lang="en"><head><title>One &amp; two</title>'
    + `<meta name="description" content="${'A&amp;B '.repeat(40)}">`
    + '<link rel="canonical" href="https://example.test/page">'
    + '<meta property="og:title" content="Title"><meta name="twitter:card" content="summary"></head>'
    + '<body><h1>Page</h1></body></html>';
  const result = scan(write('encoded.html', source), '--profile', 'publishing');
  assert(!ids(result).includes('UE-EO002'), `decoded length must be measured: ${result.stdout}`);
}

// --- configuration discovery -------------------------------------------------

{
  // A project .un-editorial.json is picked up from the working directory.
  const project = path.join(tmp, 'project');
  fs.mkdirSync(project, { recursive: true });
  fs.writeFileSync(path.join(project, 'page.txt'), 'The organization reports.\n');
  fs.writeFileSync(path.join(project, '.un-editorial.json'),
    JSON.stringify({ allowlist: { spellings: ['organization'] } }));
  const result = spawnSync(process.execPath, [cli, 'page.txt', '--format', 'json'], {
    cwd: project, encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout).findings, [],
    '.un-editorial.json must be honoured from the working directory');
}

// --- CLI surface -------------------------------------------------------------

{
  const version = spawnSync(process.execPath, [cli, '--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr);
  assert.match(version.stdout.trim(), /^un-editorial-check \d+\.\d+\.\d+$/);
  const reported = json(capture([fixture('positive', 'sp001.txt'), '--format', 'json'])).version;
  assert.equal(version.stdout.trim(), `un-editorial-check ${reported}`,
    '--version and the report must agree');

  const help = spawnSync(process.execPath, [cli, '--help'], { encoding: 'utf8' });
  assert.equal(help.status, 0, help.stderr);
  assert.match(help.stdout, /--fix/);
  assert.match(help.stdout, /--profile/);
  assert.match(help.stdout, /--report/);
  assert.match(help.stdout, /EXIT CODES/);
}

// --- --report: the current-to-should-be PDF ----------------------------------

{
  const pdfText = file => fs.readFileSync(file, 'latin1');
  const isPdf = bytes => bytes.startsWith('%PDF-1.4') && bytes.trimEnd().endsWith('%%EOF');

  // A missing or empty value is a usage failure (exit 2), like every other flag.
  // These two run the real binary: the suite's capture() appends --config, which
  // would otherwise be swallowed as --report's value.
  const missing = spawnSync(process.execPath, [cli, '--report'], { encoding: 'utf8' });
  assert.equal(missing.status, 2, `--report without a value must refuse, got ${missing.status}`);
  assert.match(missing.stderr, /--report requires a value/);
  const empty = spawnSync(process.execPath, [cli, '--report=', fixture('negative', 'hs-clean-copy.txt')],
    { encoding: 'utf8' });
  assert.equal(empty.status, 2, '--report= must refuse');
  assert.match(empty.stderr, /--report requires a value/);

  // A clean scan writes a structurally valid PDF and does not move the exit code.
  const clean = fixture('negative', 'hs-clean-copy.txt');
  const without = capture([clean]);
  const cleanPdf = path.join(tmp, 'clean.pdf');
  const withReport = capture([clean, '--report', cleanPdf]);
  assert.equal(withReport.code, without.code, '--report must not change the exit code');
  assert(withReport.code === 0, 'the clean fixture must scan clean');
  const cleanBytes = pdfText(cleanPdf);
  assert(isPdf(cleanBytes), 'the report must be a structurally complete PDF');
  assert.match(cleanBytes, /Editorial Review Report/, 'the report must carry its title');
  // The footer's three cells (decision D3) are stamped into every report, clean
  // or not. This is the lock the report-only promise line used to hold: it
  // moved with that line's removal rather than being deleted, so the guarantee
  // "every report carries its footer" still fails if a renderer stops drawing
  // one. The year is matched as a shape rather than pinned, because a CLI scan
  // dates itself from its own input and this fixture is not a fixed date.
  assert.match(cleanBytes, /Page 1 of 1/, 'every report stamps its page position');
  assert.match(cleanBytes, /© \d{4} un-editorial-check contributors/,
    'every report stamps the copyright, its year read from the scan date');
  assert.match(cleanBytes, /github\.com\/ahaomar\/un-editorial-check/,
    'every report stamps the repository address');

  // The exit code is identical with and without --report on a failing corpus.
  const hs = fixture('positive', 'hs001-dehumanising.txt');
  const hsPlain = scan(hs);
  assert.equal(hsPlain.code, 1, 'the dehumanising fixture must exit 1');
  const hsPdf = path.join(tmp, 'hs.pdf');
  const hsReported = capture([hs, '--report', hsPdf]);
  assert.equal(hsReported.code, hsPlain.code, '--report must not change a failing exit code');
  const hsBytes = pdfText(hsPdf);
  assert(isPdf(hsBytes), 'the safety report must be a complete PDF');
  assert(hsPlain.stdout.includes('UE-HS001'), 'the fixture must fire UE-HS001');

  // A diplomatic sensitivity is a warning (Wave 3): the contested-claims
  // fixture renders and cites its source without failing the run.
  const dp = fixture('positive', 'dp001.txt');
  const dpPlain = scan(dp);
  assert.equal(dpPlain.code, 0, 'the contested-claims fixture exits 0 at warning severity');
  assert(dpPlain.stdout.includes('UE-DP001'), 'the fixture must fire UE-DP001');
  const dpPdf = path.join(tmp, 'dp.pdf');
  const dpReported = capture([dp, '--report', dpPdf]);
  assert.equal(dpReported.code, 0, '--report must not change an advisory exit code');
  const dpBytes = pdfText(dpPdf);
  assert(isPdf(dpBytes), 'the contested-claims report must be a complete PDF');
  assert.match(dpBytes, /resolution/, 'the Sources appendix must cite the claims knowledge base');

  // Unwritable paths are refusals (exit 2), named in the error.
  const bad = capture([clean, '--report', path.join(tmp, 'no-such-dir', 'x.pdf')]);
  assert.equal(bad.code, 2, 'an unwritable report path must refuse with exit 2');
  assert.match(bad.stderr, /cannot write report/);

  // --report composes with --format json: stdout stays JSON, the file is written.
  const jsonPdf = path.join(tmp, 'json.pdf');
  const both = capture([dp, '--report', jsonPdf, '--format', 'json']);
  assert.equal(both.code, 0, 'an advisory fixture composes both formats without failing');
  assert.equal(json(both).findings.length > 0, true, 'stdout must still be the JSON report');
  assert(isPdf(pdfText(jsonPdf)), '--report must write the file alongside --format json');

  // --report with --fix --apply records the PRE-fix state of the copy.
  const target = write('report-prefix.txt', 'We noted the the point twice.\n');
  const fixPdf = path.join(tmp, 'prefix.pdf');
  const applied = capture([target, '--report', fixPdf, '--fix', '--apply']);
  assert.equal(applied.code, 0, 'a fixable warning-only file must exit 0');
  assert.equal(fs.readFileSync(target, 'utf8').includes('the the'), false,
    '--fix --apply must have corrected the doubled word');
  assert.match(pdfText(fixPdf), /the the/,
    'the report must record the pre-fix wording the user asked to see');
}

// --- packaging --------------------------------------------------------------

{
  const pack = spawnSync('npm', ['pack', '--dry-run', '--json'], { cwd: root, encoding: 'utf8' });
  assert.equal(pack.status, 0, pack.stderr);
  const files = JSON.parse(pack.stdout)[0].files.map(entry => entry.path);
  for (const required of ['lib/cli.mjs', 'lib/units.mjs', 'config/default.json',
    'config/profiles/un-v1.json', 'rules/catalogue.json', 'bin/check.mjs', 'SKILL.md', 'VERSION',
    'USER-GUIDE.md',
    // Phase 10 §10.4: the embedded faces have to *ship*, not merely be
    // required on disk. A `files` entry dropped from package.json, or a
    // leading slash added to one of these paths, leaves the report rendering
    // against a font the installed package never had — and the runtime would
    // only find out when a reader saw Helvetica instead. `fonts/` is one
    // `files` string, so the four of them are named individually rather than
    // asserted as a group: a wildcard would pass on any stray file landing in
    // the directory.
    'fonts/RobotoCondensed-Regular.ttf', 'fonts/RobotoCondensed-Bold.ttf',
    'fonts/LICENSE-APACHE.txt', 'fonts/NOTICE.txt',
    'commands/un-diplomatic-agent.md']) {
    assert(files.includes(required), `npm pack must include ${required}`);
  }
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  const reported = json(capture([fixture('positive', 'sp001.txt'), '--format', 'json'])).version;
  assert.equal(pkg.version, reported, 'the report version must match package.json');
  assert.equal(fs.readFileSync(path.join(root, 'VERSION'), 'utf8').trim(), reported,
    'VERSION must match package.json');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — corpus, exit codes, positions, suppressions, fixes, profiles, config, output, report, packaging');
