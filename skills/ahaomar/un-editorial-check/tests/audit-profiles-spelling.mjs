// un-editorial-check — W2a contract tests: profile-dependent UE-SP001,
// bundled profile names, catalogue `sources` and UE-SP003 consolidation.
//
// Self-contained: its own tmpdir, its own CLI invocations through the same
// in-process `run` entry point tests/run.mjs uses. Nothing is ever written
// inside the repository (the checker self-scans the repository, and a test
// document inside it would be scanned as copy).
//
// Run standalone: node tests/audit-profiles-spelling.mjs
//
// Covered contract items (.feedbacks/REMEDIATION-PLAN.md, W2a):
//   1. the derived `-ize` conflict family, persisted as `spellingConflicts`
//   2. default run: a conflict-family key warns (exit 0), names the profile
//      choice, and is not `--fix`-able
//   3. non-conflict entries unchanged: error, fixable, exact message
//   4. `un-secretariat-document` / `un-v1` / `un-geneva-web` silence the
//      family; `generic-british-english` errors with an "-ise" reference
//      and an honest, recorded source
//   5. `spellingConflicts` schema validation and replace semantics
//   6. cli name resolution: bundled names, alias, audits, paths, and
//      unknown names → exit 2 listing the bundled names
//   7. catalogue `sources` schema plus a fail-closed registry cross-check
//   8. UE-SP003 consolidation: map-owned words never double-report
//   9. rules/spelling.md guard-note locks for items 2, 4 and 8
//
// Sections run independently so one failure still reports the status of every
// other contract item; any failure exits 1.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';
import { ProfileError, loadCatalogue, loadBaselineProfile, applyProfile } from '../lib/config.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
import { SECURITY_FIXTURE_SOURCE } from './lib/make-security-fixture.mjs';
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-profiles-'));

// Deliberate rule-violating test data. Each constant carries a same-line
// `ue:ignore` so the repository's own self-scan stays clean however the
// sentence-like-literal rule classifies this file's own source.
const CONFLICT = 'The organization reports quarterly.'; // ue:ignore UE-SP001  (deliberate test data)
const NON_CONFLICT = 'The color publishes an annual report.'; // ue:ignore UE-SP001  (deliberate test data)
const DOUBLE_IZE = 'The organization organized the report.'; // ue:ignore UE-SP001  (deliberate test data)

const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
// An explicit config keeps the suite independent of any .un-editorial.json in
// the working directory.
const config = write('config.json', '{}');

const runRaw = (argv) => {
  const out = [];
  const err = [];
  const code = run(argv, {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
// Only supply the suite's config when the caller has not chosen one.
const capture = (argv, configPath = config) =>
  runRaw(argv.includes('--config') ? argv : [...argv, '--config', configPath]);
const json = result => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const ids = result => [...new Set(json(result).findings.map(f => f.ruleId))].sort();
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);
const one = result => {
  const found = json(result).findings;
  assert.equal(found.length, 1, `expected exactly one finding:\n${result.stdout}\n${result.stderr}`);
  return found[0];
};
const readProfile = name =>
  JSON.parse(fs.readFileSync(path.join(root, 'config', 'profiles', `${name}.json`), 'utf8'));

// The family is data, derived once and persisted in un-v1.json: every key
// whose spelling is a `-ize`-family form and whose replacement is the `-ise`
// counterpart, except the entries the United Nations list itself prints in
// `-ise` form (UN-verified exceptions, kept as ordinary errors).
const UN_VERIFIED = new Set([
  'analyze', 'analyzes', 'analyzed', 'analyzing',
  'catalyze', 'catalyzes', 'catalyzed', 'catalyzing',
  'paralyze', 'paralyzes', 'paralyzed', 'paralyzing',
]);
const deriveFamily = spelling => Object.entries(spelling)
  .filter(([key, value]) =>
    /(?:ization|izations|izes|ized|izing|ize)$/.test(key)
    && /(?:isation|isations|ises|ised|ising|ise)$/.test(value)
    && !UN_VERIFIED.has(key))
  .map(([key]) => key)
  .sort();

const FAMILY = ['organization', 'organizations', 'organize', 'organized', 'organizes', 'organizing'];
const rawBaseline = JSON.parse(
  fs.readFileSync(path.join(root, 'config', 'profiles', 'un-v1.json'), 'utf8'));

const sections = [];
const section = (name, body) => sections.push([name, body]);

// --- 1. the derived conflict family ------------------------------------------

section('1. conflict family derivation and persistence', () => {
  assert.ok(Array.isArray(rawBaseline.spellingConflicts),
    'un-v1.json must persist the family as a spellingConflicts array');
  assert.deepEqual(deriveFamily(rawBaseline.spelling), FAMILY,
    'the derivation over the baseline map must yield exactly the six -ize/-ise keys');
  assert.deepEqual([...rawBaseline.spellingConflicts].sort(), FAMILY,
    'un-v1.json must persist the derived family as spellingConflicts');
  // organisational is a `-isation` replacement but not a `-ize` key: it stays
  // an ordinary error, outside the family.
  assert.ok(!FAMILY.includes('organizational'));
  assert.ok(rawBaseline.spelling.organizational, 'organizational must stay a baseline key');

  // The UN-verified exception, as data since the -yse release: the United
  // Nations list itself prints analyse, catalyse and paralyse in -ise form,
  // so the -yse keys are ordinary errors and ship in the baseline map. The
  // invariant that matters is unchanged — they must never reach the conflict
  // family, because their stance is definitive rather than a profile choice.
  for (const word of ['analyze', 'catalyze', 'paralyze']) {
    assert.ok(word in rawBaseline.spelling,
      `${word} must be a baseline key corrected to the -ise/-yse form the United Nations list prints`);
    assert.ok(UN_VERIFIED.has(word),
      `${word} must stay in the UN-verified exception set, outside the conflict family`);
    assert.match(rawBaseline.spelling[word], /yse$/,
      `${word} must correct to the -yse form printed by the United Nations list`);
  }
  const synthetic = { organize: 'organise', analyze: 'analyse', color: 'colour', organizational: 'organisational' };
  assert.deepEqual(deriveFamily(synthetic), ['organize'],
    'the derivation must keep organize and except analyze even when both are map keys');

  // The baseline file keeps its name (rules/diplomacy.md references it).
  assert.ok(fs.existsSync(path.join(root, 'config', 'profiles', 'un-v1.json')));
  // The dead editorial.un.org citation is gone; the DGACM URL stands.
  assert.ok(!rawBaseline.source.includes('editorial.un.org'),
    'un-v1.json must not cite the dead editorial.un.org source');
  assert.match(rawBaseline.source, /un\.org\/dgacm\/en\/content\/editorial-manual/,
    'un-v1.json source must point at the DGACM editorial manual');
});

// --- 2. default run: conflict keys warn, name the choice, are not fixable ----

section('2. default run: conflict warns, names the choice, not fixable', () => {
  const file = write('default-conflict.txt', `${CONFLICT}\n`);
  const result = scan(file);
  const finding = one(result);
  assert.equal(finding.ruleId, 'UE-SP001');
  assert.equal(finding.severity, 'warning',
    'without a profile the conflict family must be a warning, not an error');
  assert.equal(result.code, 0, 'a warning alone must not fail the run');
  assert.doesNotMatch(finding.message, /American spelling/,
    `the conflict message must not name a nationality, it names the profile choice: ${finding.message}`);
  assert.match(finding.message, /un-secretariat-document/,
    `the message must name the accepting profile: ${finding.message}`);
  assert.match(finding.message, /generic-british-english/,
    `the message must name the enforcing profile: ${finding.message}`);
  assert.equal(finding.suggestion, null, 'a conflict warning must not suggest a rewrite');
  assert.equal(finding.proposed, null, 'a conflict warning must carry no replacement');
  assert.equal(finding.current, 'organization');

  // Not fixable: --fix finds nothing to do and writes nothing.
  const fix = capture([file, '--fix', '--apply']);
  assert.equal(fix.code, 0);
  assert.equal(fs.readFileSync(file, 'utf8'), `${CONFLICT}\n`,
    'a conflict warning must never be rewritten');
  assert.doesNotMatch(fix.stdout, /\(proposed\)/);

  // Text output reports it as a warning section.
  const text = capture([file]);
  assert.match(text.stdout, /EDITORIAL WARNINGS/);
  assert.equal(text.code, 0);

  // Every persisted family key behaves the same way by default. The fixture
  // carries a finite verb so the UE-HR001 review heuristic stays silent and
  // this section counts the family warning alone.
  FAMILY.forEach((key, index) => {
    const target = write(`family-${index}.txt`, `The ${key} publishes an annual report.\n`);
    const scanResult = scan(target);
    const entry = one(scanResult);
    assert.equal(entry.severity, 'warning', `${key} must warn by default`);
    assert.equal(scanResult.code, 0, `${key} must not fail the default run`);
  });

  // organisational sits outside the family: an ordinary error.
  const ordinary = write('family-ordinary.txt', 'The organizational publishes an annual report.\n');
  const ordinaryResult = scan(ordinary);
  assert.equal(one(ordinaryResult).severity, 'error',
    'organizational is outside the conflict family and stays an error');
  assert.equal(ordinaryResult.code, 1);
});

// --- 3. non-conflict entries are unchanged -----------------------------------

section('3. non-conflict entries unchanged: error, fixable, exact message', () => {
  const file = write('default-ordinary.txt', `${NON_CONFLICT}\n`);
  const result = scan(file);
  const finding = one(result);
  assert.equal(finding.severity, 'error', 'a non-conflict entry is an error in every stance');
  assert.equal(finding.message, 'American spelling "color" in prose.',
    'the non-conflict message must not change');
  assert.equal(finding.suggestion, 'Use "colour".');
  assert.equal(finding.proposed, 'colour');
  assert.equal(result.code, 1);

  // … and it stays fixable.
  const fix = capture([file, '--fix', '--apply']);
  assert.equal(fix.code, 0, 'every error was written');
  assert.equal(fs.readFileSync(file, 'utf8'), 'The colour publishes an annual report.\n');
});

// --- 4. the three bundled organisation profiles ------------------------------

section('4. secretariat/alias/geneva silent; British errors with -ise', () => {
  const file = write('profiled-conflict.txt', `${CONFLICT}\n`);

  // un-secretariat-document, its un-v1 alias and un-geneva-web all accept the
  // family silently — Geneva defers, so its spelling equals the secretariat's.
  for (const name of ['un-secretariat-document', 'un-v1', 'un-geneva-web']) {
    const result = scan(file, '--profile', name);
    assert.deepEqual(ids(result), [], `${name} must silence the conflict family`);
    assert.equal(result.code, 0, `${name} must exit 0 on an accepted -ize form`);
  }

  // The silence is only for the family: settled non-conflict entries stay
  // errors under the same profiles.
  const ordinary = write('profiled-ordinary.txt', `${NON_CONFLICT}\n`);
  const enforced = scan(ordinary, '--profile', 'un-secretariat-document');
  assert.deepEqual(ids(enforced), ['UE-SP001'],
    'the secretariat profile must still enforce non-conflict spelling');
  assert.equal(one(enforced).severity, 'error');
  assert.equal(enforced.code, 1);

  // generic-british-english enforces the family as an error with an -ise
  // reference and a fixable replacement.
  const british = scan(file, '--profile', 'generic-british-english');
  const entry = one(british);
  assert.equal(entry.severity, 'error', 'the British profile must error on the -ize form');
  assert.match(entry.message, /-ise/, `the message must reference the -ise preference: ${entry.message}`);
  assert.match(entry.message, /Generic British English/,
    `the message must reference the profile: ${entry.message}`);
  assert.doesNotMatch(entry.message, /American spelling/);
  assert.equal(entry.suggestion, 'Use "organisation".');
  assert.equal(british.code, 1);
  const fix = capture([file, '--fix', '--apply', '--profile', 'generic-british-english']);
  assert.equal(fix.code, 0, 'under the British profile the family is fixable');
  assert.equal(fs.readFileSync(file, 'utf8'), 'The organisation reports quarterly.\n');

  // Honest source: a real, retrievable British style guide recorded in
  // rules/sources.json, and the profile says plainly it is not a UN rule.
  const guide = JSON.parse(fs.readFileSync(path.join(root, 'rules', 'sources.json'), 'utf8'))
    .sources.find(source => source.id === 'guardian-style-guide');
  assert(guide, 'rules/sources.json must record the British style guide');
  assert.match(guide.url, /^https:\/\//, 'the recorded guide must have a retrievable URL');
  assert.ok(guide.appliesTo.includes('profile:generic-british-english'),
    'the guide must be recorded against the British profile');
  const profile = readProfile('generic-british-english');
  assert.equal(profile.profileVersion, 1);
  assert.deepEqual(profile.spellingConflicts, [],
    'the British profile must set an empty spellingConflicts list');
  assert.match(profile.source, /Guardian/i, 'the profile source must name the style guide');
  assert.match(profile.source, /not a United Nations rule/i,
    'the profile source must say plainly it is not a UN rule');

  // Geneva: no -ise rule of its own — it inherits the baseline family and
  // defers to the Editorial Manual.
  const geneva = readProfile('un-geneva-web');
  assert.equal(geneva.spellingConflicts, undefined,
    'the Geneva profile must state no -ize/-ise rule of its own');
  assert.match(geneva.source, /ungeneva/i, 'the Geneva profile must cite its own source');
  const mergedGeneva = applyProfile(rawBaseline, geneva);
  assert.deepEqual(mergedGeneva.spelling, rawBaseline.spelling,
    'Geneva spelling must be identical to the secretariat baseline');
  assert.deepEqual([...mergedGeneva.spellingConflicts].sort(), FAMILY,
    'Geneva must inherit the baseline conflict family');
});

// --- 5. spellingConflicts: schema validation and replace semantics -----------

section('5. spellingConflicts validation and replace semantics', () => {
  // Every entry must be a baseline spelling key, or the profile fails closed.
  const typo = write('typo-conflicts.json', JSON.stringify({
    profileVersion: 1, name: 'Typo', source: 'fixture', spellingConflicts: ['typo'],
  }));
  const target = write('validate-target.txt', `${CONFLICT}\n`);
  const badEntry = scan(target, '--profile', typo);
  assert.equal(badEntry.code, 2, 'a spellingConflicts entry outside the vocabulary must fail closed');
  assert.match(badEntry.stderr, /spellingConflicts/);
  assert.match(badEntry.stderr, /vocabulary/,
    `stderr must say the entry is not in the baseline vocabulary: ${badEntry.stderr}`);

  const notArray = write('not-array-conflicts.json', JSON.stringify({
    profileVersion: 1, name: 'NotArray', source: 'fixture', spellingConflicts: 'organization',
  }));
  const badShape = scan(target, '--profile', notArray);
  assert.equal(badShape.code, 2, 'spellingConflicts must be an array');
  assert.match(badShape.stderr, /spellingConflicts/);

  // Replace semantics: the field replaces the baseline list, it never extends it.
  assert.deepEqual([...applyProfile(rawBaseline, {}).spellingConflicts].sort(), FAMILY,
    'a profile without the field must inherit the baseline family');
  assert.deepEqual(applyProfile(rawBaseline, { spellingConflicts: [] }).spellingConflicts, [],
    'a profile that sets the field must replace the baseline family');

  // Behaviourally: a custom profile without the field accepts the family …
  const inheriting = write('inherit-conflicts.json', JSON.stringify({
    profileVersion: 1, name: 'Inherit', source: 'fixture',
  }));
  const inherited = scan(write('inherit-target.txt', `${CONFLICT}\n`), '--profile', inheriting);
  assert.deepEqual(ids(inherited), [],
    'a custom profile without spellingConflicts must inherit and accept the family');

  // … and one that sets [] enforces it as a fixable error.
  const enforcing = write('enforce-conflicts.json', JSON.stringify({
    profileVersion: 1, name: 'Enforce', source: 'fixture', spellingConflicts: [],
  }));
  const enforced = scan(write('enforce-target.txt', `${CONFLICT}\n`), '--profile', enforcing);
  const entry = one(enforced);
  assert.equal(entry.severity, 'error',
    'a profile that empties spellingConflicts must enforce the family');
  assert.match(entry.message, /Enforce/,
    `the error must name the enforcing profile: ${entry.message}`);
  assert.equal(entry.suggestion, 'Use "organisation".');
  assert.equal(enforced.code, 1);
});

// --- 6. cli name resolution ---------------------------------------------------

section('6. name resolution: bundled names, alias, audits, paths, unknown', () => {
  const file = write('resolve-target.txt', `${CONFLICT}\n`);

  // An unknown bare name fails closed and lists the bundled profile names.
  const unknown = scan(file, '--profile', 'no-such-profile');
  assert.equal(unknown.code, 2, 'an unknown profile name must exit 2');
  assert.match(unknown.stderr, /profile not found/,
    `stderr must say the profile was not found: ${unknown.stderr}`);
  for (const name of ['un-secretariat-document', 'un-v1', 'un-geneva-web', 'generic-british-english']) {
    assert.ok(unknown.stderr.includes(name),
      `stderr must list the bundled profile name ${name}: ${unknown.stderr}`);
  }

  // A path-looking value keeps the plain, unprefixed refusal (run.mjs pins it).
  const missingPath = scan(file, '--profile', 'does-not-exist.json');
  assert.equal(missingPath.code, 2);
  assert.match(missingPath.stderr, /profile not found/);
  assert.doesNotMatch(missingPath.stderr, /bundled profiles/,
    'a path-like value must not be answered with the bundled-name listing');

  // Audit names still resolve and stay opt-in.
  // An existing file inside the repository (the scanner refuses the skill root
  // without --self-scan), so the audit fixture is copied out like run.mjs
  // copies its fixtures.
  // The security fixture is generated at runtime; the repository tree holds
  // no sink-shaped text (tests/lib/make-security-fixture.mjs).
  const auditFixture = write('audit-security.mjs', SECURITY_FIXTURE_SOURCE);
  const audit = scan(auditFixture, '--profile', 'security');
  assert.ok(ids(audit).includes('UE-SE001'), `the security audit must run: ${audit.stdout}`);
  assert.equal(audit.code, 0, 'audits never change the exit code');

  // An existing path wins over a bundled name of the same spelling: the local
  // file downgrades UE-SP001, so a run through it must exit 0, while the
  // bundled generic-british-english profile would exit 1.
  const local = path.join(tmp, 'generic-british-english');
  fs.writeFileSync(local, JSON.stringify({
    profileVersion: 1, name: 'Local path wins', source: 'fixture',
    spellingConflicts: [], severities: { 'UE-SP001': 'warning' },
  }));
  const target = path.join(tmp, 'path-wins-target.txt');
  fs.writeFileSync(target, `${CONFLICT}\n`);
  const viaPath = spawnSync(process.execPath,
    [cli, target, '--profile', 'generic-british-english', '--format', 'json'],
    { cwd: tmp, encoding: 'utf8' });
  assert.equal(viaPath.status, 0, `an existing path must win over the bundled name: ${viaPath.stderr}`);
  const findings = JSON.parse(viaPath.stdout).findings;
  assert.equal(findings.length, 1);
  assert.equal(findings[0].severity, 'warning');
  assert.match(findings[0].message, /Local path wins/,
    `the local profile file must have been the one loaded: ${findings[0].message}`);
});

// --- 7. catalogue `sources` ---------------------------------------------------

section('7. catalogue sources schema and registry cross-check', () => {
  const { meta } = loadCatalogue(root);
  assert.deepEqual(meta['UE-SP001'].sources, ['un-editorial-manual-spelling'],
    'UE-SP001 must cite its recorded spelling authority');

  // Fail-closed schema validation on a tampered copy of the rules directory.
  const tamperedRoot = path.join(tmp, 'tampered');
  fs.mkdirSync(path.join(tamperedRoot, 'rules'), { recursive: true });
  const catalogueText = fs.readFileSync(path.join(root, 'rules', 'catalogue.json'), 'utf8');
  const registryText = fs.readFileSync(path.join(root, 'rules', 'sources.json'), 'utf8');
  fs.writeFileSync(path.join(tamperedRoot, 'rules', 'sources.json'), registryText);
  const catalogueFile = path.join(tamperedRoot, 'rules', 'catalogue.json');
  const tamper = mutate => {
    const parsed = JSON.parse(catalogueText);
    mutate(parsed.rules.find(entry => entry.id === 'UE-SP001'));
    fs.writeFileSync(catalogueFile, JSON.stringify(parsed));
  };

  tamper(entry => { entry.sources = 'un-editorial-manual-spelling'; });
  assert.throws(() => loadCatalogue(tamperedRoot), ProfileError,
    'sources that is not an array must fail closed');

  tamper(entry => { entry.sources = ['no-such-source']; });
  assert.throws(() => loadCatalogue(tamperedRoot), ProfileError,
    'a sources id absent from rules/sources.json must fail closed');
  assert.throws(() => loadCatalogue(tamperedRoot), /no-such-source/,
    'the refusal must name the unknown source id');

  tamper(entry => { entry.sources = ['']; });
  assert.throws(() => loadCatalogue(tamperedRoot), ProfileError,
    'an empty sources entry must fail closed');

  // A missing registry behind a cited id is a refusal, never a silent pass.
  tamper(entry => { entry.sources = ['un-editorial-manual-spelling']; });
  fs.rmSync(path.join(tamperedRoot, 'rules', 'sources.json'));
  assert.throws(() => loadCatalogue(tamperedRoot), ProfileError,
    'a missing rules/sources.json behind a cited id must fail closed');
});

// --- 8. UE-SP003 consolidation ------------------------------------------------

section('8. UE-SP003 consolidation: map-owned words never double-report', () => {
  const review = write('review.json', JSON.stringify({ spellingReview: true }));

  // Map-owned words are UE-SP001's, never double-reported as -ise candidates.
  const owned = write('sp003-owned.txt', `${DOUBLE_IZE}\n`);
  const doubleReport = scan(owned, '--config', review);
  assert.deepEqual(ids(doubleReport), ['UE-SP001'],
    'a baseline-map -ize word must not double-report as UE-SP003');
  assert.equal(doubleReport.code, 0, 'the default stance keeps both as warnings');

  // Settled map keys outside the family are owned by UE-SP001 too.
  const defence = write('sp003-defence.txt', 'The defense of the report was clear.\n');
  assert.deepEqual(ids(scan(defence, '--config', review)), ['UE-SP001'],
    'a baseline-map entry must never double-report as UE-SP003');

  // Words the map does not own keep the opt-in review.
  const reviewTarget = write('sp003-review.txt', 'The report optimizes results.\n');
  assert.deepEqual(ids(scan(reviewTarget, '--config', review)), ['UE-SP003'],
    'a -ize word outside the baseline map must keep firing UE-SP003');
  assert.equal(scan(reviewTarget).code, 0, 'the review stays opt-in');

  // Under a profile that accepts the family, review mode stays silent on
  // accepted words: UE-SP001 owns them and does not fire.
  assert.deepEqual(ids(scan(owned, '--config', review, '--profile', 'un-secretariat-document')), [],
    'an accepted -ize word must stay silent even with spellingReview on');
});

// --- 9. guard-note locks (rules/spelling.md) ----------------------------------

section('9. rules/spelling.md guard-note locks', () => {
  const guard = fs.readFileSync(path.join(root, 'rules', 'spelling.md'), 'utf8');
  const sp001 = guard.split('\n').find(line => line.startsWith('- **UE-SP001**'));
  assert(sp001, 'rules/spelling.md must document UE-SP001');
  assert.match(sp001, /profile/i, 'the UE-SP001 guard note must say the profile decides');
  assert.match(sp001, /warning/, 'the guard note must state the default warning stance');
  assert.match(sp001, /un-secretariat-document/, 'the guard note must name the accepting profile');
  assert.match(sp001, /generic-british-english/, 'the guard note must name the enforcing profile');
  assert.doesNotMatch(sp001, /American spelling/,
    'the guard note must not call the conflict family American spelling');

  const sp003 = guard.split('\n').find(line => line.startsWith('- **UE-SP003**'));
  assert(sp003, 'rules/spelling.md must document UE-SP003');
  assert.match(sp003, /UE-SP001/,
    'the UE-SP003 guard note must state that UE-SP001 owns baseline-map words');
});

// --- run ----------------------------------------------------------------------

let failures = 0;
for (const [name, body] of sections) {
  try {
    body();
    console.log(`  ok — ${name}`);
  } catch (err) {
    failures += 1;
    console.error(`  FAIL — ${name}\n      ${String(err.message).split('\n').join('\n      ')}`);
  }
}
fs.rmSync(tmp, { recursive: true, force: true });
if (failures) {
  console.error(`${failures} of ${sections.length} contract sections failed`);
  process.exit(1);
}
console.log('ok — profiles, conflict family, name resolution, catalogue sources, SP003 consolidation');
