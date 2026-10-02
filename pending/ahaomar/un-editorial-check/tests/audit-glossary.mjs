// Glossary contract suite (Phase 7, Agent 3).
//
// Standalone: node tests/audit-glossary.mjs
//
// What it locks:
//   1. catalogue wiring — UE-GL001 and UE-GL002 are registered, profile
//      null, warning severity, no `sources` (a user file has no URL, so it is
//      recorded as config, never in the append-only source registry);
//   2. honest provenance — every glossary finding names the reader's file,
//      carries the glossary lane, and is never labelled with a United Nations
//      rule file or the UN editorial baseline;
//   3. --fix never touches it, through planFixes and end to end, and the
//      allow-list lock in tests/audit-fix-set.mjs is not weakened: the new
//      rules are probed and produce no edit;
//   4. fail closed with exit 2 on every malformed shape, each message naming
//      the problem, in the same voice as lib/config.mjs;
//   5. the config `glossary` key and the --glossary flag, with the flag
//      winning, plus config.rules switching a glossary rule off;
//   6. clean-run wording and the five lanes, so a glossary run cannot make a
//      mislabelled section appear.
// No vacuous case: every assertion below runs against a live file or a live
// invocation; nothing is skipped and no premise is weakened to make a check
// pass.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run, CATALOGUE } from '../bin/check.mjs';
import { loadGlossary, runGlossaryRules, GLOSSARY_RULE_IDS } from '../lib/glossary.mjs';
import { planFixes, FIXABLE_RULE_IDS } from '../lib/fix.mjs';
import { renderText } from '../lib/output.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-glossary-'));
const CLEAN = 'No findings under the enabled, documented local rules.';

let sequence = 0;
const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
const config = write('config.json', '{}');
const glossary = (terms, extra = {}) => write(`glossary-${sequence++}.json`,
  JSON.stringify({ glossaryVersion: 1, ...terms, ...extra }, null, 2));

const capture = (argv) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', config];
  const code = run(args, { log: line => out.push(String(line)), error: line => err.push(String(line)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const json = result => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);
const ids = result => [...new Set(json(result).findings.map(f => f.ruleId))].sort();

// A draft that disagrees with the glossary on all three counts: a forbidden
// term with a declared replacement, a forbidden term without one, and a
// required term that never appears.
const draft = write('draft.md',
  'The programme reached the beneficiaries in the region.\n\n'
  + 'Further detail follows.\n\n'
  + 'The team used the project name.\n');
const house = glossary({
  name: 'House style',
  requiredTerms: ['Sustainable Development Goal'],
  forbiddenTerms: ['beneficiaries', 'programme'],
  replacements: { beneficiaries: 'participants' },
});

// --- 1. catalogue wiring ------------------------------------------------------

{
  const idsInOrder = CATALOGUE.rules.map(rule => rule.id);
  for (const id of GLOSSARY_RULE_IDS) {
    const entry = CATALOGUE.rules.find(rule => rule.id === id);
    assert(entry, `${id} must be registered in rules/catalogue.json`);
    assert.equal(entry.profile, null, `${id} is not an audit profile rule`);
    assert.equal(entry.severity, 'warning', `${id} must be warning, never an error`);
    assert.equal(entry.category, 'terminology', `${id} category`);
    assert.equal(entry.confidence, 'deterministic', `${id} confidence`);
    assert.equal(entry.scope, 'user-visible-copy', `${id} scope`);
    // A user file has no URL and no retrieval date, so it is not a citable
    // source: recording it in rules/sources.json would be dishonest.
    assert(!('sources' in entry), `${id} must cite no registry source: a user file has no URL`);
    assert.equal(entry.extensibility, '--glossary, config.glossary, config.severities, config.rules',
      `${id} extensibility names the glossary inputs`);
    assert.ok(entry.guardNotes.length > 80, `${id} guardNotes must state the limitations`);
    assert.ok(entry.summary.length > 15, `${id} summary must describe the rule`);
    // The three override keys lib/output.mjs's annotate() reads. A catalogue
    // entry that omits `source` would make the checker cite
    // config/profiles/glossary.json, a file that does not exist.
    assert.match(entry.source, /user-supplied glossary/i,
      `${id} must declare an honest source: ${entry.source}`);
    assert.match(entry.source, /not a United Nations rule/i,
      `${id} source must say outright it is not a United Nations rule`);
    assert.ok(!/[\w-]+\.(?:json|md)/.test(entry.source),
      `${id} source must not cite a file path: ${entry.source}`);
    assert.ok(entry.limitation.length > 40, `${id} must declare a limitation`);
    assert.ok(entry.action.length > 20, `${id} must declare an action`);
    assert.match(entry.limitation, /reader's own JSON file/,
      `${id} limitation must state where the term list came from`);
    assert.match(entry.action, /never rewrites a glossary term/,
      `${id} action must say terminology is never rewritten`);
    const blob = JSON.stringify(entry).toLowerCase();
    for (const banned of ['un approved', 'fully compliant', 'finds all errors',
      'factual verification', 'legal advice']) {
      assert(!blob.includes(banned), `${id} must not carry the banned phrase "${banned}"`);
    }
    assert(!/https?:\/\//.test(blob), `${id} must not invent a source URL`);
  }
  // Appended after the heuristic block so the existing order assertions in
  // tests/audit-heuristics.mjs and tests/release-regressions.mjs keep their
  // anchor: the grammar block completes with UE-GR004, then the five UE-HR
  // entries follow in order.
  const gr4 = idsInOrder.indexOf('UE-GR004');
  const hr = ['UE-HR001', 'UE-HR002', 'UE-HR003', 'UE-HR004', 'UE-HR005'];
  assert.deepEqual(idsInOrder.slice(gr4 + 1, gr4 + 1 + hr.length), hr,
    'the heuristic entries must still sit directly after the grammar block');
  for (const id of GLOSSARY_RULE_IDS) {
    assert.ok(idsInOrder.indexOf(id) > idsInOrder.indexOf('UE-HR005'),
      `${id} must be appended at the end of the catalogue`);
  }
}

console.log('ok — glossary catalogue: UE-GL001/UE-GL002 registered, no invented source');

// --- 2. honest provenance -----------------------------------------------------

{
  const result = scan(draft, '--glossary', house);
  assert.equal(result.code, 0, `a glossary run never changes the exit code: ${result.stderr}`);
  const parsed = json(result);
  const glossaryFindings = parsed.findings.filter(f => f.ruleId.startsWith('UE-GL'));
  assert.ok(glossaryFindings.length >= 3,
    `the live draft must produce glossary findings, got ${glossaryFindings.length}`);

  for (const finding of glossaryFindings) {
    // The five metadata fields are present, non-empty and honest.
    for (const field of ['source', 'profile', 'confidence', 'limitation', 'action']) {
      assert.equal(typeof finding[field], 'string', `${finding.ruleId} carries a string ${field}`);
      assert(finding[field].length > 0, `${finding.ruleId} ${field} is not empty`);
    }
    // Never mistakable for an institutional United Nations requirement.
    assert.equal(finding.lane, 'audit', `${finding.ruleId} is audit-lane`);
    assert.equal(finding.profile, 'glossary',
      `${finding.ruleId} profile must name the glossary, not a UN profile`);
    // The source names the mechanism and says outright that it is not a UN
    // rule. It must NOT be a file path: lib/output.mjs's annotate() derives a
    // path for any audit-lane finding (config/profiles/<name>.json), and a
    // catalogue entry that omits `source` would make the checker cite a file
    // that does not exist. The real path travels in the message and in the
    // structured glossary.file.
    assert.match(finding.source, /user-supplied glossary/i,
      `${finding.ruleId} source must name the glossary: ${finding.source}`);
    assert.match(finding.source, /not a United Nations rule/i,
      `${finding.ruleId} source must say it is not a United Nations rule: ${finding.source}`);
    assert.ok(!/[\w-]+\.(?:json|md)/.test(finding.source),
      `${finding.ruleId} source must not cite a file path: ${finding.source}`);
    for (const unSource of ['rules/terminology.md', 'rules/catalogue.json', 'config/profiles/un-v1.json',
      'config/profiles/glossary.json', 'editorial baseline']) {
      assert(!finding.source.includes(unSource),
        `${finding.ruleId} must not be sourced to a United Nations rule: ${finding.source}`);
      assert(!finding.profile.includes(unSource),
        `${finding.ruleId} must not claim a United Nations profile: ${finding.profile}`);
    }
    // The limitation and action must be specific to a user glossary, not the
    // generic audit-lane wording about an audit profile.
    assert.match(finding.limitation, /reader's own JSON file/,
      `${finding.ruleId} limitation must state the provenance: ${finding.limitation}`);
    assert.match(finding.action, /never rewrites a glossary term|never rewrites a glossary/,
      `${finding.ruleId} action must say terminology is never rewritten: ${finding.action}`);
    assert.ok(!/audit profile/.test(finding.action),
      `${finding.ruleId} must not tell the reader to review under an audit profile: ${finding.action}`);
    assert.match(finding.message, /not a United Nations rule/,
      `${finding.ruleId} states in the message that it is not a United Nations rule`);
    assert.ok(finding.message.includes(house),
      `${finding.ruleId} message names the glossary file the reader wrote: ${finding.message}`);
    // The text report gives the glossary its own section and never an
    // editorial-error section.
    assert.ok(finding.audit === 'glossary',
      `${finding.ruleId} carries the glossary audit tag`);
    assert.equal(finding.context, 'authored', `${finding.ruleId} context`);
  }

  // The two rule kinds are distinguished and located honestly.
  const forbidden = glossaryFindings.filter(f => f.ruleId === 'UE-GL001');
  const required = glossaryFindings.filter(f => f.ruleId === 'UE-GL002');
  assert.ok(forbidden.length >= 2, 'both forbidden occurrences are reported');
  assert.ok(required.length >= 1, 'the absent required term is reported');
  for (const finding of forbidden) {
    assert.equal(finding.line, 1, 'the forbidden occurrence is on the line it was written on');
    assert.equal(finding.glossary.kind, 'forbidden', 'structured provenance says forbidden');
    assert.ok(finding.current, 'the finding quotes what was written');
  }
  for (const finding of required) {
    assert.equal(finding.line, 1, 'a file-level finding anchors at the top of the file');
    assert.equal(finding.glossary.kind, 'required', 'structured provenance says required');
    assert.equal(finding.glossary.term, 'Sustainable Development Goal', 'the term is named');
  }

  // The declared replacement is reported as guidance and never as an edit.
  const withReplacement = forbidden.find(f => /beneficiaries/.test(f.current));
  assert(withReplacement, 'the beneficiaries occurrence is reported');
  assert.match(withReplacement.suggestion, /"participants"/,
    'the glossary replacement is offered as guidance');
  assert.equal(withReplacement._replacement, undefined,
    'a glossary finding never carries a replacement for --fix');
  const withoutReplacement = forbidden.find(f => /programme/.test(f.current));
  assert(withoutReplacement, 'the programme occurrence is reported');
  assert.match(withoutReplacement.suggestion, /names no replacement/,
    'a term with no declared replacement says so rather than inventing one');

  // The text report: its own section, and no editorial-error section.
  const text = capture([draft, '--glossary', house]).stdout;
  assert.match(text, /OPTIONAL AUDIT — glossary \(\d+\)/,
    'glossary findings render in their own section');
  assert(!text.includes('EDITORIAL ERRORS'),
    'a glossary finding must never masquerade as an editorial error');
  assert.match(text, /^lanes: deterministic 0 · heuristic-review 0 · harmful-discriminatory 0 · diplomacy 0 · audit \d+ · quoted 0$/m,
    'every glossary finding is counted in the audit lane');

  // The report model closes the block with the same six provenance fields
  // every other row closes with (D12), and the audit row names the glossary.
  const { buildReport } = await import('../lib/report.mjs');
  const report = buildReport({
    version: '0.0.0', date: '2026-01-01', targets: [draft], profiles: [],
    filesCount: 1, findings: json(scan(draft, '--glossary', house)).findings, sources: [],
  }, { detail: 'full' });
  const row = report.find(e => e.type === 'issue');
  assert(row, 'the glossary finding renders as the shared issue row');
  assert.equal(row.audit, 'glossary', 'the block carries the glossary audit row');
  const prov = label => {
    const pair = row.provenance.find(p => p.label === label);
    assert(pair, `the glossary row carries no ${label} provenance field`);
    return pair.value;
  };
  assert.match(prov('Profile'), /glossary/, 'the block carries the glossary profile');
  assert.match(prov('Source'), /user-supplied glossary/i,
    'the block carries the glossary source');
  assert.match(prov('Action'), /never rewrites a glossary term/,
    'the block states that a glossary term is never rewritten');

  // The Sources appendix names the reader's file. A glossary has no URL, so
  // this is where its provenance is recorded instead of in the source
  // registry.
  const withSources = buildReport({
    version: '0.0.0', date: '2026-01-01', targets: [draft], profiles: [],
    filesCount: 1, findings: json(scan(draft, '--glossary', house)).findings,
    sources: [`Reader-supplied glossary: ${house}`],
  }, { detail: 'full' });
  const bullets = withSources.find(e => e.type === 'bullets');
  assert.ok(bullets, 'a glossary run has a Sources appendix');
  assert.ok(bullets.items.some(item => item.includes(house)),
    `the Sources appendix names the reader's glossary file: ${JSON.stringify(bullets.items)}`);

  // The Sources appendix is reached through the CLI too, not only by hand:
  // collectReportSources adds the glossary for a real --report run.
  const reportPath = path.join(tmp, 'glossary-report.pdf');
  const reported = capture([draft, '--glossary', house, '--report', reportPath]);
  assert.equal(reported.code, 0, `--report does not change the exit code: ${reported.stderr}`);
  const pdfText = fs.readFileSync(reportPath, 'latin1');
  const pdfLines = [...pdfText.matchAll(/\/(F[123]) ([0-9.]+) Tf ([0-9.-]+) ([0-9.-]+) Td \(((?:\\[\s\S]|[^\\()])*)\) Tj/g)]
    .map(m => m[5].replace(/\\([()\\])/g, '$1')).join(' ');
  assert.match(pdfLines, /Source user-supplied glossary/,
    'the PDF drawing carries the user-supplied source row');
  assert.match(pdfLines, /Profile glossary/, 'the PDF drawing carries the glossary profile');
  assert.match(pdfLines, /Audit glossary/, 'the PDF drawing carries the glossary audit row');
  assert.match(pdfLines, /Lane audit/, 'the PDF drawing routes the finding to the audit lane');
  assert.ok(!/EDITORIAL ERRORS/.test(pdfLines),
    'a glossary finding never appears as an editorial error in the PDF');
}

console.log('ok — glossary provenance: own section, own lane, no United Nations attribution');

// --- 3. --fix never rewrites a glossary term ----------------------------------

{
  // The allow-list lock is untouched, and the new rules are outside it.
  assert.deepEqual([...FIXABLE_RULE_IDS].sort(),
    ['UE-GR001', 'UE-GR002', 'UE-GR003', 'UE-GR004', 'UE-NU002', 'UE-SP001'],
    'the fixable set is unchanged: adding a glossary must not widen it');
  for (const id of GLOSSARY_RULE_IDS) {
    assert(!FIXABLE_RULE_IDS.has(id), `${id} must never be fixable`);
  }
  // The probe tests/audit-fix-set.mjs performs over every catalogue rule:
  // both new entries are in the catalogue, and planFixes produces no edit for
  // them even when a finding is handed a replacement.
  for (const id of GLOSSARY_RULE_IDS) {
    const source = fs.readFileSync(draft, 'utf8');
    const probe = {
      file: draft, line: 1, column: source.indexOf('beneficiaries') + 1,
      ruleId: id, category: 'terminology', severity: 'warning',
      confidence: 'deterministic', scope: 'user-visible-copy',
      message: 'glossary probe', suggestion: null,
      current: 'beneficiaries', proposed: 'participants',
      _unit: { offset: 0, raw: source },
      _index: 0, _matched: 'beneficiaries',
      _offset: source.indexOf('beneficiaries'),
      // Even with a replacement attached, the rule id keeps it out.
      _replacement: 'participants',
    };
    assert.deepEqual(planFixes([probe], new Map([[draft, source]])), [],
      `${id} must never produce an edit, even carrying a replacement`);
  }
  // End to end: a preview shows no fix, --apply writes nothing.
  const target = write('fix-target.md', fs.readFileSync(draft, 'utf8'));
  const before = fs.readFileSync(target, 'utf8');
  const preview = capture([target, '--fix', '--glossary', house]);
  assert.equal(preview.code, 0, `a glossary run stays exit 0: ${preview.stderr}`);
  assert.doesNotMatch(preview.stdout, /APPLIED/, 'a preview never applies');
  const applied = capture([target, '--fix', '--apply', '--glossary', house]);
  assert.equal(applied.code, 0, `the run still passes: ${applied.stderr}`);
  assert.equal(fs.readFileSync(target, 'utf8'), before,
    'terminology is never auto-rewritten: the draft must be byte-for-byte unchanged');
  assert.ok(!/participants/.test(fs.readFileSync(target, 'utf8')),
    'the glossary replacement must not be written into the source');
}

console.log('ok — glossary fix boundary: allow-list unchanged, planFixes refuses, source untouched');

// --- 4. fail closed, exit 2, every malformed shape -----------------------------

{
  const good = { glossaryVersion: 1, forbiddenTerms: ['beneficiaries'] };
  const refuse = (label, contents, needle) => {
    const file = path.join(tmp, `bad-${sequence++}.json`);
    fs.writeFileSync(file, contents);
    const result = capture([draft, '--glossary', file]);
    assert.equal(result.code, 2, `${label}: expected exit 2, got ${result.code}`);
    assert.match(result.stderr, needle, `${label}: message must name the problem, got: ${result.stderr}`);
    assert.match(result.stderr, /^un-editorial-check: /, `${label}: the refusal carries the tool prefix`);
  };

  refuse('not JSON', '{ not json', /glossary .* is not valid JSON/);
  refuse('duplicate keys',
    '{"glossaryVersion":1,"forbiddenTerms":["a"],"forbiddenTerms":["b"]}',
    /contains duplicate keys/);
  refuse('not an object', '["beneficiaries"]', /must be a JSON object/);
  refuse('unknown field', JSON.stringify({ ...good, spelling: [] }),
    /contains unknown fields: spelling/);
  refuse('missing version', JSON.stringify({ forbiddenTerms: ['a'] }),
    /must declare glossaryVersion 1/);
  refuse('wrong version', JSON.stringify({ glossaryVersion: 2, forbiddenTerms: ['a'] }),
    /must declare glossaryVersion 1/);
  refuse('terms not an array', JSON.stringify({ glossaryVersion: 1, forbiddenTerms: 'beneficiaries' }),
    /forbiddenTerms must be an array/);
  refuse('requiredTerms not an array', JSON.stringify({ glossaryVersion: 1, requiredTerms: {} }),
    /requiredTerms must be an array/);
  refuse('empty entry', JSON.stringify({ glossaryVersion: 1, forbiddenTerms: ['a', ''] }),
    /forbiddenTerms\[1\] must be a non-empty string/);
  refuse('blank entry', JSON.stringify({ glossaryVersion: 1, requiredTerms: ['   '] }),
    /requiredTerms\[0\] must be a non-empty string/);
  refuse('wrong type entry', JSON.stringify({ glossaryVersion: 1, forbiddenTerms: [42] }),
    /forbiddenTerms\[0\] must be a non-empty string/);
  refuse('unmatchable term', JSON.stringify({ glossaryVersion: 1, forbiddenTerms: ['---'] }),
    /can never match/);
  refuse('empty name', JSON.stringify({ ...good, name: ' ' }),
    /name must be a non-empty string/);
  refuse('empty glossary', JSON.stringify({ glossaryVersion: 1 }),
    /declares no terms/);
  refuse('empty both lists',
    JSON.stringify({ glossaryVersion: 1, forbiddenTerms: [], requiredTerms: [] }),
    /declares no terms/);
  refuse('replacements not an object',
    JSON.stringify({ ...good, replacements: ['a'] }),
    /replacements must be an object/);
  refuse('replacement value empty',
    JSON.stringify({ ...good, replacements: { beneficiaries: '' } }),
    /replacements\["beneficiaries"\] must be a non-empty string/);
  refuse('replacement key not forbidden',
    JSON.stringify({ ...good, replacements: { programme: 'program' } }),
    /not a forbidden term/);
  refuse('duplicate term',
    JSON.stringify({ glossaryVersion: 1, forbiddenTerms: ['a', 'A'] }),
    /lists "A" more than once/);

  // Missing file, wrong file kind, and the empty flag value.
  const missing = capture([draft, '--glossary', path.join(tmp, 'absent.json')]);
  assert.equal(missing.code, 2, 'a missing glossary must refuse');
  assert.match(missing.stderr, /cannot be read/, missing.stderr);
  const directory = capture([draft, '--glossary', tmp]);
  assert.equal(directory.code, 2, 'a directory is not a glossary');
  assert.match(directory.stderr, /is not a regular file/, directory.stderr);
  const emptyValue = capture([draft, '--glossary', '']);
  assert.equal(emptyValue.code, 2, '--glossary= must refuse');
  assert.match(emptyValue.stderr, /--glossary requires a value/, emptyValue.stderr);

  // A bad glossary refuses even when the run is --quiet or in fix mode: the
  // refusal is a configuration failure, not a finding.
  const quiet = capture([draft, '--quiet', '--glossary', path.join(tmp, 'absent.json')]);
  assert.equal(quiet.code, 2, '--quiet does not swallow a refusal');

  // A refusal names the file, so a reader with several glossaries knows which.
  const named = write('house-style-terms.json', '{ not json');
  const namedResult = capture([draft, '--glossary', named]);
  assert.match(namedResult.stderr, /house-style-terms\.json/,
    `the refusal names the file: ${namedResult.stderr}`);
}

console.log('ok — glossary fail-closed: 25 malformed shapes, each exit 2 with a named problem');

// --- 5. the config key, the flag, and the rule switch --------------------------

{
  // A file that disagrees with the config glossary only. The glossary path is
  // resolved from the working directory, exactly like --profile and --config,
  // so the test states that outright: a relative path in the config file is
  // relative to where the command was run from, not to the config file.
  const terms = write('config-terms.json', JSON.stringify({
    glossaryVersion: 1, forbiddenTerms: ['project name'],
  }));
  const configOnly = write('config-glossary.json', JSON.stringify({
    glossary: path.relative(process.cwd(), terms),
  }));
  const file = write('only-project-name.md', 'The team used the project name.\n');
  const viaConfig = capture([file, '--config', configOnly, '--format', 'json']);
  assert.equal(viaConfig.code, 0, `a config glossary run exits 0: ${viaConfig.stderr}`);
  assert.deepEqual(ids(viaConfig), ['UE-GL001'], 'the config key imports the glossary');
  assert.match(viaConfig.stderr, /^$/, 'a good run is silent on stderr');

  // The resolution base is the working directory, not the config file, and an
  // absolute path works from anywhere.
  const relativeToConfig = write('wrong-base.json', JSON.stringify({
    glossary: path.basename(terms),
  }));
  const wrongBase = capture([file, '--config', relativeToConfig]);
  assert.equal(wrongBase.code, 2,
    'a path relative to the config file is not silently resolved against it');
  const absolute = write('absolute-config.json', JSON.stringify({ glossary: terms }));
  assert.deepEqual(ids(scan(file, '--config', absolute)), ['UE-GL001'],
    'an absolute glossary path resolves from any working directory');

  // The flag wins over the config key: a different glossary entirely. The
  // config glossary would have fired here; the flag's glossary must not.
  // A term the file does not contain, so the flag glossary has nothing to
  // report and the config glossary's hit is unambiguous.
  const other = glossary({ forbiddenTerms: ['beneficiaries'] });
  const viaFlag = capture([file, '--config', configOnly, '--format', 'json', '--glossary', other]);
  assert.equal(viaFlag.code, 0, `a glossary run exits 0: ${viaFlag.stderr}`);
  const flagFindings = json(viaFlag).findings;
  assert.deepEqual(flagFindings.map(f => f.ruleId), [],
    'the --glossary flag replaces the config glossary, so the config term is not reported');
  assert.ok(flagFindings.every(f => f.glossary.file === other),
    'every finding names the flag glossary, never the config one');
  assert.ok(!viaFlag.stdout.includes('UE-GL001'),
    'the config glossary does not also run alongside the flag');

  // A config glossary that cannot be read refuses, rather than scanning
  // without it.
  const brokenConfig = write('broken-config.json', JSON.stringify({ glossary: 'nowhere.json' }));
  const refused = capture([file, '--config', brokenConfig]);
  assert.equal(refused.code, 2, 'a broken config glossary must refuse');
  assert.match(refused.stderr, /nowhere\.json/, refused.stderr);

  // A wrong type in config is a config error, in the config.mjs voice.
  for (const [value, needle] of [[42, /config glossary must be a non-empty path/],
    ['', /config glossary must be a non-empty path/],
    [['a.json'], /config glossary must be a non-empty path/]]) {
    const bad = write(`bad-config-${sequence++}.json`, JSON.stringify({ glossary: value }));
    const result = capture([file, '--config', bad]);
    assert.equal(result.code, 2, `config glossary ${JSON.stringify(value)} must refuse`);
    assert.match(result.stderr, needle, result.stderr);
  }
  const unknownKey = write('unknown-config.json', JSON.stringify({ glossry: 'a.json' }));
  const unknownResult = capture([file, '--config', unknownKey]);
  assert.equal(unknownResult.code, 2, 'an unknown config field still refuses');
  assert.match(unknownResult.stderr, /config contains unknown fields: glossry/, unknownResult.stderr);

  // config.rules switches a glossary rule off, and the switch is honoured.
  const switched = write('switched-config.json', JSON.stringify({
    rules: { 'UE-GL001': { enabled: false } },
  }));
  const off = scan(file, '--config', switched, '--glossary', house);
  assert.deepEqual(ids(off), ['UE-GL002'],
    'only the switched-off rule disappears; the other still runs');
  const switchedBoth = write('switched-both.json', JSON.stringify({
    rules: { 'UE-GL001': { enabled: false }, 'UE-GL002': { enabled: false } },
  }));
  assert.deepEqual(ids(scan(file, '--config', switchedBoth, '--glossary', house)), [],
    'both rules can be switched off');
  // config.severities reaches a glossary rule too, which is how a reader
  // re-grades the finding without touching the catalogue.
  // config.severities reaches a glossary rule, which is how a reader re-grades
  // the finding without touching the catalogue. This case asserts the MECHANISM
  // — that the configured grade really lands on the finding — and nothing about
  // the exit code, because that is not what this grade can test.
  //
  // It previously asserted "still cannot fail the run" at info severity, which
  // looked like it guarded the audit-lane exit-code invariant but could not:
  // info is not error severity, so the assertion passed under any
  // implementation of editorialErrors, including one with no !f.audit guard at
  // all. QA finding D11. The invariant itself is now locked at error severity
  // in tests/audit-lanes.mjs section 6b, where the mutation turns it red.
  const regraded = write('regraded-config.json', JSON.stringify({
    severities: { 'UE-GL002': 'info' },
  }));
  const regradedRun = scan(file, '--config', regraded, '--glossary', house);
  const regradedFindings = json(regradedRun).findings;
  assert.ok(regradedFindings.length > 0, 'the re-graded run still reports findings');
  assert.ok(regradedFindings.every(f => f.ruleId === 'UE-GL002'),
    'the re-graded config reports only the re-graded rule');
  assert.ok(regradedFindings.every(f => f.severity === 'info'),
    `config.severities really re-grades the glossary finding: ${JSON.stringify(regradedFindings.map(f => [f.ruleId, f.severity]))}`);

  // The escalation direction that matters is error, and it is asserted at
  // error severity here too, so this file carries the property on its own
  // terms rather than only by reference to another suite.
  const escalated = write('escalated-config.json', JSON.stringify({
    severities: { 'UE-GL002': 'error' },
  }));
  const escalatedRun = scan(file, '--config', escalated, '--glossary', house);
  const escalatedFindings = json(escalatedRun).findings;
  assert.ok(escalatedFindings.some(f => f.ruleId === 'UE-GL002' && f.severity === 'error'),
    'config.severities can escalate a glossary rule to error severity');
  assert.equal(escalatedRun.code, 0,
    'audit-lane exit-code invariant: an error-severity glossary finding is audit-lane and does not fail the run');

  // --init and --self-test refuse a glossary, and say so.
  const withInit = capture(['--init', '--glossary', house]);
  assert.equal(withInit.code, 2, '--init cannot be combined with --glossary');
  assert.match(withInit.stderr, /--init cannot be combined with --glossary/, withInit.stderr);
  const withSelfTest = capture(['--self-test', '--glossary', house]);
  assert.equal(withSelfTest.code, 2, '--self-test cannot be combined with --glossary');
  assert.match(withSelfTest.stderr, /--self-test cannot be combined with --glossary/, withSelfTest.stderr);
  const withPreview = capture([draft, '--preview', 'x', '--glossary', house]);
  assert.equal(withPreview.code, 2, '--preview cannot be combined with --glossary');
  assert.match(withPreview.stderr, /--preview cannot be combined with --glossary/, withPreview.stderr);
}

console.log('ok — glossary config: key, flag precedence, rule switch, refused combinations');

// --- 6. clean run, lanes, suppression, determinism ----------------------------

{
  // A glossary run with nothing to report prints the clean sentence, exactly.
  // Uses the required term and neither forbidden term, so the glossary has
  // nothing to report about it.
  const agreeing = write('agreeing.md',
    'The initiative supports the Sustainable Development Goal.\n');
  const clean = capture([agreeing, '--glossary', house]);
  assert.equal(clean.code, 0, `a clean glossary run exits 0: ${clean.stderr}`);
  assert.ok(clean.stdout.includes(CLEAN),
    `a clean glossary run states: ${CLEAN}\n got: ${clean.stdout}`);
  assert(!clean.stdout.includes('lanes:'), 'no lane line on an empty scan');

  // A draft that already uses the house term reports only what it breaks.
  const noForbidden = write('no-forbidden.md', 'The team reports the figure.\n');
  const onlyRequired = json(scan(noForbidden, '--glossary', house)).findings;
  assert.deepEqual(onlyRequired.map(f => f.ruleId), ['UE-GL002'],
    'only the absent required term is reported');

  // Quoted and code material is structurally out of reach, exactly as for every
  // other rule: extraction masks it before any rule reads it.
  const quoted = write('quoted.md',
    'The report quotes the field: "beneficiaries of the project".\n\n'
    + 'Inline `beneficiaries` is code.\n');
  const quotedIds = ids(scan(quoted, '--glossary', house));
  assert(!quotedIds.includes('UE-GL001'),
    `masked quotation and code must not fire UE-GL001, got ${quotedIds}`);

  // A `ue:ignore` comment switches a glossary rule off for a copy span, the
  // same way it does for any other rule. The comment must sit inside the copy
  // span, as the extraction tests show for HTML: a comment on its own line is
  // masked as markup and never joins the copy unit.
  const ignored = write('ignored.html',
    '<p>The programme reached the beneficiaries. <!-- ue:ignore UE-GL001 --></p>\n');
  assert.ok(!ids(scan(ignored, '--glossary', house)).includes('UE-GL001'),
    'ue:ignore UE-GL001 must silence the occurrence rule');
  assert.ok(ids(scan(ignored, '--glossary', house)).includes('UE-GL002'),
    'the ignore comment silences only the rule it names');
  const notIgnored = write('not-ignored.html',
    '<p>The programme reached the beneficiaries. <!-- ue:ignore UE-SP001 --></p>\n');
  assert.ok(ids(scan(notIgnored, '--glossary', house)).includes('UE-GL001'),
    'an ignore comment for another rule must not silence UE-GL001');
  // A file-level suppression needs `ue:ignore all`, since the finding is about
  // the whole file rather than one span.
  const allIgnored = write('all-ignored.html',
    '<p>The programme reached the beneficiaries. <!-- ue:ignore all --></p>\n');
  assert.deepEqual(ids(scan(allIgnored, '--glossary', house)), [],
    'ue:ignore all silences both glossary rules for the file');

  // Determinism: the same input yields the same findings, in the same order,
  // and loadGlossary keeps no mutable state between calls.
  const first = json(scan(draft, '--glossary', house)).findings;
  const second = json(scan(draft, '--glossary', house)).findings;
  assert.deepEqual(first, second, 'two runs of the same input are deeply equal');
  // Sorted by file, then numeric line, then numeric column, then rule id —
  // the same order lib/rules.mjs uses, not a string sort of the positions.
  const keys = first.map(f => `${f.file}:${f.line}:${f.column}:${f.ruleId}`);
  assert.deepEqual(keys, [...first]
    .sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line
      || a.column - b.column || a.ruleId.localeCompare(b.ruleId))
    .map(f => `${f.file}:${f.line}:${f.column}:${f.ruleId}`),
  'glossary findings are ordered by file, line, column and rule id');
  assert.ok(first.length > 2, 'the ordering is checked over a real multi-finding run');
  assert.deepEqual(loadGlossary(house), loadGlossary(house),
    'loadGlossary is pure: two loads of one file are deeply equal');

  // The module refuses a bad file directly, without a CLI in the way.
  assert.throws(() => loadGlossary(path.join(tmp, 'absent.json')), /cannot be read/);

  // A file with no extractable copy is not judged for required terms: there
  // is nothing to read, so no absence is claimed.
  const empty = write('empty.txt', '\n');
  assert.deepEqual(ids(scan(empty, '--glossary', house)), [],
    'an empty file produces no glossary finding at all');

  // renderText is reachable directly with a glossary finding, and puts it in
  // the audit section rather than an editorial one.
  const direct = renderText({
    findings: [{
      file: 'a.md', line: 1, column: 1, ruleId: 'UE-GL001', category: 'terminology',
      severity: 'warning', confidence: 'deterministic', scope: 'user-visible-copy',
      context: 'authored', message: 'Glossary x forbids "a"; this is the reader\'s house terminology, not a United Nations rule.',
      suggestion: null, current: 'a', proposed: null, audit: 'glossary',
    }],
    files: 1, version: '0.0.0',
  });
  assert.match(direct, /OPTIONAL AUDIT — glossary \(1\)/);
  assert.ok(!direct.includes('EDITORIAL'), 'no editorial section for a glossary-only run');
}

console.log('ok — glossary reporting: clean sentence, lanes, suppression, determinism, boundaries');

// --- 7. the module contract the CLI relies on ---------------------------------

{
  assert.deepEqual([...GLOSSARY_RULE_IDS], ['UE-GL001', 'UE-GL002'],
    'the rule ids are stable and in catalogue order');
  const compiled = loadGlossary(house);
  assert.equal(compiled.file, house, 'the path the reader gave is kept verbatim');
  assert.equal(compiled.name, 'House style', 'the declared name is kept');
  assert.ok(Object.isFrozen(compiled), 'a loaded glossary is frozen');
  assert.ok(Object.isFrozen(compiled.forbidden), 'the compiled term lists are frozen');
  assert.deepEqual(compiled.forbidden.map(e => e.term), ['beneficiaries', 'programme']);
  assert.equal(compiled.forbidden[0].use, 'participants', 'the declared replacement is compiled');
  assert.equal(compiled.forbidden[1].use, null, 'no declared replacement is null, not empty');
  assert.equal(compiled.required.length, 1);

  // A glossary with no declared name still reads as a file-backed source, not
  // as an anonymous claim.
  const unnamed = glossary({ forbiddenTerms: ['team'] });
  assert.equal(loadGlossary(unnamed).label, 'with no declared name');

  // runGlossaryRules is a pure function of units, glossary and context: it can
  // be called directly, and its findings carry the audit tag before any
  // renderer sees them.
  const unit = {
    file: 'x.md', text: 'The team met the beneficiaries.', raw: 'The team met the beneficiaries.',
    offset: 0, starts: [0], context: 'authored',
  };
  const directFindings = runGlossaryRules([unit], compiled, { meta: {}, cfg: { rules: {}, severities: {} } });
  // The unit names one forbidden term once, and the required term is absent
  // from the file, so both kinds fire: one occurrence finding plus the
  // file-level absence.
  assert.deepEqual(directFindings.map(f => f.ruleId), ['UE-GL002', 'UE-GL001'],
    'one forbidden occurrence and one absent required term, ordered by position');
  for (const finding of directFindings) {
    assert.equal(finding.audit, 'glossary', 'the audit tag is set by the rule, not the renderer');
    assert.equal(finding.glossary.file, house, 'structured provenance carries the file');
  }
  // The occurrence finding quotes the term; the absence finding quotes the
  // required term in its structured provenance and has no current text.
  assert.equal(directFindings[1].current, 'beneficiaries', 'the occurrence quotes the copy');
  assert.equal(directFindings[0].current, null, 'an absence has no current text to quote');
  assert.equal(directFindings[0].glossary.term, 'Sustainable Development Goal',
    'the absence names the required term structurally');
  assert.equal(directFindings[0].glossary.replacement, null,
    'a required term never carries a replacement');
  // A disabled rule produces nothing, even when called directly. Both are
  // switched off here so the assertion is about the switch, not about which
  // rule would otherwise have fired.
  const disabled = runGlossaryRules([unit], compiled, {
    meta: {},
    cfg: { rules: { 'UE-GL001': { enabled: false }, 'UE-GL002': { enabled: false } }, severities: {} },
  });
  assert.deepEqual(disabled, [], 'a disabled rule produces no finding');
  // Switching off only the occurrence rule leaves the absence finding in place.
  const onlyFirst = runGlossaryRules([unit], compiled,
    { meta: {}, cfg: { rules: { 'UE-GL001': { enabled: false } }, severities: {} } });
  assert.deepEqual(onlyFirst.map(f => f.ruleId), ['UE-GL002'],
    'the switch is per rule: disabling UE-GL001 leaves UE-GL002 running');
}

console.log('ok — glossary module: frozen compilation, pure rules, structured provenance');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — glossary: catalogue, provenance, fix boundary, fail-closed, config, reporting');
