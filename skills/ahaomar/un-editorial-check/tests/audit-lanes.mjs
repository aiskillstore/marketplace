// un-editorial-check — Wave 3 lane contract suite (PHASE-6-PLAN, row B).
//
// The contract under test, verbatim from the plan: five output lanes
// (deterministic / heuristic review / harmful-discriminatory review /
// diplomatic sensitivity / audits) each carrying rule source, profile,
// confidence, limitation and recommended human action; heuristic default
// severity flip; expanded protected characteristics and "discriminatory or
// demeaning" high-severity human review, never auto-rewrite; quoted material
// reported separately; diplomacy KB variant/negation/incomplete-assertion
// coverage with the v8 web-corpus P0/P1 fixtures; PDF and --format JSON/SARIF
// reflect the lanes; and the audit lane's own contract, section 6b — an
// audit-lane finding can never decide the process exit code, whatever severity
// the reader escalates it to.
//
// Fixtures are copied out of the repository before use: the scanner never
// reads files inside its own skill root unless --self-scan is given. Every
// rendered output collected here is swept at the end for the banned phrases
// ("UN approved", "fully compliant", "finds all errors", "factual
// verification", "legal advice").

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-lanes-'));

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

const rendered = [];
const capture = (argv, configPath = config) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', configPath];
  const code = run(args, {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  const result = { code, stdout: out.join('\n'), stderr: err.join('\n') };
  rendered.push(result.stdout, result.stderr);
  return result;
};
const json = result => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);

const LANE_NAMES = ['deterministic', 'heuristic-review', 'harmful-discriminatory', 'diplomacy', 'audit'];
const METADATA = ['lane', 'context', 'source', 'profile', 'confidence', 'limitation', 'action'];

// --- 1: every finding carries its lane metadata in JSON ----------------------

for (const [label, argv] of [
  ['v8 P1 demeaning', [fixture('lanes', 'web-p1-demeaning.txt')]],
  ['v8 P1 diplomacy claims', [fixture('lanes', 'web-p1-diplomacy-claims.txt')]],
  ['dm001 discriminating copy', [fixture('positive', 'dm001-demeaning.txt')]],
  ['heuristic collective blame', [fixture('positive', 'hs002-collective-blame.txt')]],
  ['opt-in audit', [fixture('audits', 'accessibility.html'), '--profile', 'accessibility']],
]) {
  const parsed = json(scan(...argv));
  assert.ok(parsed.findings.length > 0, `${label} must produce findings`);
  assert.deepEqual(Object.keys(parsed.lanes).sort(), [...LANE_NAMES, 'quoted'].sort(),
    `${label}: the lanes summary names all five lanes plus quoted`);
  for (const finding of parsed.findings) {
    for (const field of METADATA) {
      assert.equal(typeof finding[field], 'string',
        `${label}: ${finding.ruleId} carries a string ${field}`);
      assert(finding[field].length > 0, `${label}: ${finding.ruleId} ${field} is not empty`);
    }
    assert(LANE_NAMES.includes(finding.lane),
      `${label}: ${finding.ruleId} lane "${finding.lane}" is one of the five lanes`);
  }
}

// --- 2: harmful-discriminatory lane — high-severity review, never auto-rewrite

{
  const demeaningRun = scan(fixture('lanes', 'web-p1-demeaning.txt'));
  const demeaning = json(demeaningRun);
  assert.equal(demeaningRun.code, 1, 'demeaning wording is an error: the run fails');
  assert.deepEqual(demeaning.lanes, {
    deterministic: 0, 'heuristic-review': 0, 'harmful-discriminatory': 2,
    diplomacy: 0, audit: 0, quoted: 0,
  }, 'the v8 P1 demeaning fixture lands entirely in the harmful-discriminatory lane');
  for (const finding of demeaning.findings) {
    assert.equal(finding.ruleId, 'UE-DM001');
    assert.equal(finding.lane, 'harmful-discriminatory');
    assert.equal(finding.severity, 'error');
    assert.match(finding.action, /High-severity human review/,
      'the recommended action is high-severity human review');
    assert.match(finding.limitation, /never rewritten automatically/,
      'the limitation records that the text is never rewritten automatically');
  }

  // Never auto-rewrite, proven through the full --fix pipeline: a file whose
  // only findings are discriminatory leaves the run byte-identical.
  const target = write('dm-fix.txt', fs.readFileSync(fixture('lanes', 'web-p1-demeaning.txt'), 'utf8'));
  const before = fs.readFileSync(target, 'utf8');
  const applied = capture([target, '--fix', '--apply']);
  assert.equal(fs.readFileSync(target, 'utf8'), before,
    'discriminatory wording must survive --fix --apply unchanged');
  assert.equal(applied.code, 1, 'the errors still fail the run after a refused fix');

  // The DM001 corpus fixture: three detections, all in the safety lane.
  const corpusRun = scan(fixture('positive', 'dm001-demeaning.txt'));
  const corpus = json(corpusRun);
  assert.equal(corpusRun.code, 1);
  assert.deepEqual(corpus.findings.map(f => f.ruleId), ['UE-DM001', 'UE-DM001', 'UE-DM001']);
  assert.equal(corpus.lanes['harmful-discriminatory'], 3);
}

// --- 3: diplomacy lane — advisory, attributed, never a truth verdict ----------

{
  const claimsRun = scan(fixture('lanes', 'web-p1-diplomacy-claims.txt'));
  const claims = json(claimsRun);
  assert.equal(claimsRun.code, 0, 'a diplomatic sensitivity is advisory and never fails the run');
  assert.equal(claims.lanes.diplomacy, 3, 'the v8 P1 claims fixture fires three variants');
  assert.deepEqual(claims.findings.map(f => f.line), [1, 3, 4],
    'the attributed claim on line 2 stays silent: the attribution guard holds for variants');
  for (const finding of claims.findings) {
    assert.equal(finding.ruleId, 'UE-DP001');
    assert.equal(finding.lane, 'diplomacy');
    assert.equal(finding.severity, 'warning');
    assert.match(finding.action, /Requires diplomatic review/,
      'the recommended action routes to diplomatic review');
    assert.match(finding.limitation, /never decides whose claim is correct/,
      'the limitation refuses a factual verdict');
    assert(!/\b(false|untrue|incorrect|wrong|lie)\b/i.test(finding.message),
      `the message never declares the claim false: ${finding.message}`);
  }

  // The baseline claim fixture: eight warning-severity findings, exit 0.
  const baselineRun = scan(fixture('positive', 'dp001.txt'));
  const baseline = json(baselineRun);
  assert.equal(baselineRun.code, 0, 'the contested-claims fixture is a warning corpus');
  assert.equal(baseline.lanes.diplomacy, baseline.findings.length);
  for (const finding of baseline.findings) assert.equal(finding.severity, 'warning');
}

// --- 3b: web/04 P0 — pinned detections, recorded limitation -------------------

{
  // `.feedbacks/v8/html-editor-feedback-skipped-by-skill.md` lines 30-35 raise
  // a P0 in `web/04-letter-permanent-representation.html`: the incoherent
  // heading "Dash Country is a terrioust Country" and a truncated paragraph
  // attributing a statement to a named public official. The fixture is a
  // verbatim copy of that file (QA finding F3: it had no fixture at all).
  // Two things are pinned here, and they must not be confused with each
  // other:
  //   * the seven findings the scan does produce today — five UE-SP001 -ize
  //     conflicts and two UE-RE002 ranking claims, at their exact lines —
  //     may not regress silently;
  //   * the P0 block itself (heading line 31, attributed paragraph lines
  //     33-35) produces nothing, and that gap is a documented limitation,
  //     not coverage: catching `terrioust` needs a dictionary spell-checker
  //     (forbidden by the zero npm dependencies rule), and adjudicating an
  //     attributed political statement is out of scope for the default
  //     editorial scan by the editor feedback's own classification. Row 28
  //     of docs/CLAIM-EVIDENCE-AUDIT.md records the limitation.
  const p0Run = scan(fixture('lanes', 'web-p0-incoherent-insertion.html'));
  const p0 = json(p0Run);
  assert.equal(p0Run.code, 0, 'every finding on web/04 is a warning: the run exits 0');
  // Since the acronym rule (UE-HR006) landed, the page also yields one
  // genuine unexpanded acronym at line 73 — a heuristic-review finding, so
  // the heuristic lane count rose from two to three.
  assert.deepEqual(p0.lanes, {
    deterministic: 5, 'heuristic-review': 3, 'harmful-discriminatory': 0,
    diplomacy: 0, audit: 0, quoted: 0,
  }, 'web/04 currently yields five deterministic and three heuristic findings, and nothing else');

  const sp001 = p0.findings.filter(f => f.ruleId === 'UE-SP001');
  const re002 = p0.findings.filter(f => f.ruleId === 'UE-RE002');
  assert.equal(sp001.length, 5, 'UE-SP001 x5 (the -ize conflict family) must not regress');
  assert.equal(re002.length, 2, 'UE-RE002 x2 (ranking claims) must not regress');
  assert.deepEqual(sp001.map(f => f.line), [27, 43, 51, 79, 86],
    'the -ize conflicts keep their positions');
  assert.deepEqual(re002.map(f => f.line), [78, 108],
    'the ranking claims keep their positions');
  for (const finding of p0.findings) {
    assert.equal(finding.severity, 'warning', `${finding.ruleId} stays warning severity`);
    assert.equal(finding.lane, finding.ruleId === 'UE-SP001' ? 'deterministic' : 'heuristic-review');
    assert.notEqual(finding.lane, 'diplomacy', 'the attributed statement is not adjudicated here');
    assert.notEqual(finding.lane, 'harmful-discriminatory', 'the P0 block fires no safety rule');
  }

  // The recorded gap: nothing lands on the P0 block lines. If a future rule
  // starts detecting them, this assertion fails and the limitation row must
  // be re-stated — the gap is documented, never assumed.
  const onP0Block = p0.findings.filter(f => f.line >= 31 && f.line <= 35);
  assert.deepEqual(onP0Block, [],
    'nothing on the P0 block lines is detected today — the documented limitation');
}

// --- 4: text output — lane sections, lane counts, never masquerading ---------

{
  const claimsText = capture([fixture('lanes', 'web-p1-diplomacy-claims.txt')]).stdout;
  assert.match(claimsText,
    /^lanes: deterministic 0 · heuristic-review 0 · harmful-discriminatory 0 · diplomacy 3 · audit 0 · quoted 0$/m,
    'the header names all five lanes plus quoted with their counts');
  assert.match(claimsText, /DIPLOMATIC SENSITIVITY \(3\)/);
  assert(!claimsText.includes('EDITORIAL ERRORS'),
    'a diplomatic sensitivity never masquerades as an editorial error');

  const demeaningText = capture([fixture('lanes', 'web-p1-demeaning.txt')]).stdout;
  assert.match(demeaningText, /HARMFUL-DISCRIMINATORY REVIEW \(2\)/);
  assert.match(demeaningText, /^lanes: .*harmful-discriminatory 2/m);
  assert(!demeaningText.includes('EDITORIAL ERRORS'),
    'discriminatory findings never masquerade as editorial errors');

  // An empty scan has no lane line to route: the locked empty wording stands.
  const clean = capture([write('clean.txt', 'The organisation reports the figure.\n')]).stdout;
  assert.match(clean, /No findings under the enabled, documented local rules\./);
  assert(!clean.includes('lanes:'), 'no lane line on an empty scan');
}

// --- 4b: the category marker and legend on the terminal ----------------------
//
// PHASE-9-PLAN §5 and DoD 5: the text report draws a legend of exactly the
// catalogue's thirteen categories (organisation is the custom-rule category),
// marker code together with the category's text label, so the code is never
// the only thing naming the category. Both are read from the findings in hand
// — nothing on the terminal is transcribed from a report of the same run — and
// both are gated on there being findings, so a clean run still prints the
// clean sentence and nothing else.

{
  const CATEGORIES = ['SP', 'GR', 'NU', 'TM', 'RG', 'AR', 'HS', 'DS', 'DP', 'PB', 'AC', 'SC', 'OR'];
  const target = fixture('fix', 'protected.md');

  const truth = json(capture([target, '--format', 'json']));
  const text = capture([target]).stdout;

  const legend = /^categories: (.+)$/m.exec(text);
  assert(legend, 'the terminal states the category legend');
  const shown = legend[1].split(' · ').map(entry => entry.split(' '));
  assert.deepEqual(shown.map(entry => entry[0]), CATEGORIES,
    'the legend covers exactly the thirteen categories');
  assert.match(legend[1], /SP spelling \d+/, 'a legend row carries the code, the label and a count');

  const counted = shown.reduce((sum, entry) => sum + Number(entry[2]), 0);
  assert.equal(counted, truth.findings.length,
    'the legend counts add up to the findings JSON says were reported');

  // Every finding names its category in words on the line that reports it.
  const findingLines = text.split('\n').filter(line => /^ {2}.+:\d+:\d+ {2}UE-/.test(line));
  assert.equal(findingLines.length, truth.findings.length, 'one line per finding');
  for (const line of findingLines) {
    assert.match(line, /UE-\w+  (SP|GR|NU|TM|RG|AR|HS|DS|DP|PB|AC|SC) \S+/,
      'the finding line carries the marker code and its text label together');
  }

  // A clean run carries no legend at all — it is a report of a scan that found
  // something, not a standing statement about the catalogue.
  const clean = capture([write('legend-clean.txt', 'The organisation reports the figure.\n')]).stdout;
  assert(!clean.includes('categories:'), 'no category legend on an empty scan');

  // The counts are read from the findings, so a legend that disagreed with the
  // findings it was derived from would be caught rather than believed.
  const drifted = legend[1].replace(/SP spelling \d+/, 'SP spelling 99');
  const driftedCount = drifted.split(' · ')
    .reduce((sum, entry) => sum + Number(entry.split(' ')[2]), 0);
  assert.notEqual(driftedCount, truth.findings.length,
    'the legend comparison actually rejects a count that drifted');
}

// --- 5: heuristic default severity flip --------------------------------------

{
  // A heuristic judgement never fails the run and is routed to human review:
  // UE-HS002 (heuristic confidence) is a warning in the safety lane, and
  // UE-RE002 (heuristic) lands in the heuristic-review lane.
  const blameRun = scan(fixture('positive', 'hs002-collective-blame.txt'));
  const blame = json(blameRun);
  assert.equal(blameRun.code, 0, 'a heuristic judgement never fails the run');
  assert(blame.findings.length > 0);
  for (const finding of blame.findings) {
    assert.equal(finding.confidence, 'heuristic');
    assert.equal(finding.severity, 'warning', 'heuristic checks are not error-severity by default');
    assert.equal(finding.lane, 'harmful-discriminatory',
      'the safety category wins over heuristic confidence');
  }

  const heuristicRun = scan(fixture('positive', 're002.js'));
  const heuristic = json(heuristicRun);
  assert.equal(heuristicRun.code, 0);
  for (const finding of heuristic.findings) {
    assert.equal(finding.confidence, 'heuristic');
    assert.notEqual(finding.severity, 'error', 'no heuristic check is error-severity by default');
    assert.equal(finding.lane, 'heuristic-review');
    assert.match(finding.action, /review/i, 'the action routes the reader to review');
  }
  const heuristicText = capture([fixture('positive', 're002.js')]).stdout;
  assert.match(heuristicText, /AGENT REVIEW REQUIRED \(\d+\)/,
    'heuristic findings render in their own section');
}

// --- 6: audit lane -----------------------------------------------------------

{
  const auditedRun = scan(fixture('audits', 'accessibility.html'), '--profile', 'accessibility');
  const audited = json(auditedRun);
  assert.equal(auditedRun.code, 0, 'audits never change the exit code');
  assert(audited.findings.length > 0, 'the accessibility profile produces findings');
  for (const finding of audited.findings) {
    assert.equal(finding.lane, 'audit');
    assert.equal(finding.source, 'config/profiles/accessibility.json',
      'an audit finding is sourced to its profile file');
    assert.equal(finding.profile, 'accessibility');
  }
  const text = capture([fixture('audits', 'accessibility.html'), '--profile', 'accessibility']).stdout;
  assert.match(text, /OPTIONAL AUDIT — accessibility/);
}

// --- 6b: the audit lane can never decide the exit code ------------------------

// The invariant: an audit-lane finding is reported, routed and graded like any
// other finding, and it still cannot set the process exit code. It is the
// audit lane's contract, not a glossary's, so it is locked here for the three
// bundled audit profiles and for the reader's own glossary.
//
// The lock has to escalate a rule to `error` severity, because `info` and
// `warning` cannot fail under ANY implementation of the filter — a test that
// re-grades to `info` passes whether or not the `!f.audit` guard exists, and so
// proves nothing. Each case below therefore also asserts that the finding
// really did reach error severity, so the case cannot pass by accident through
// a config key that silently did not apply.
//
// Mutation that must turn this section red:
//   lib/output.mjs  editorialErrors: drop `!f.audit` from the filter.

{
  // One glossary rule and one bundled audit rule, each driven to error severity
  // through the configuration path its own lane reads.
  const dirtyDraft = write('escalate-glossary.txt',
    'The programme reached 1,200 beneficiaries in the region.\n');
  const glossaryFile = write('escalate-glossary.json', JSON.stringify({
    glossaryVersion: 1, forbiddenTerms: ['beneficiaries'],
  }));
  const glossaryConfig = write('escalate-glossary-config.json', JSON.stringify({
    severities: { 'UE-GL001': 'error' },
  }));
  // runAudits reads severity from config.rules[id].severity, not from
  // config.severities, so an audit must be escalated through the key its own
  // code path consults. The per-profile configs are built inside the loop below
  // from whichever rules each profile raises.
  const editorialConfig = write('escalate-editorial-config.json', JSON.stringify({
    severities: { 'UE-SP001': 'error' },
  }));
  const spellings = write('escalate-editorial.txt', 'The color reports.\n');

  // The positive control first, because without it the cases below would pass
  // for the wrong reason: if severity escalation had stopped working, every
  // "still exits 0" assertion here would be trivially true.
  const control = scan(spellings, '--config', editorialConfig);
  const controlFindings = json(control).findings;
  assert.equal(controlFindings.length, 1, 'the control produces exactly one finding');
  assert.equal(controlFindings[0].severity, 'error',
    'the control is escalated to error severity, so the exit code below is decided by severity');
  assert.ok(!controlFindings[0].audit,
    'the control is an editorial finding, not an audit-lane one');
  assert.equal(control.code, 1,
    'CONTROL: an error-severity editorial finding does fail the run');

  // The glossary, escalated to error.
  const glossaryRun = scan(dirtyDraft, '--config', glossaryConfig, '--glossary', glossaryFile);
  const glossaryFindings = json(glossaryRun).findings;
  assert.equal(glossaryFindings.length, 1, 'the glossary case produces exactly one finding');
  assert.equal(glossaryFindings[0].ruleId, 'UE-GL001', 'the glossary case raises UE-GL001');
  assert.equal(glossaryFindings[0].severity, 'error',
    'audit-lane exit-code invariant: the glossary finding really is error severity — this is the only grade that exercises the exit-code filter');
  assert.equal(glossaryFindings[0].audit, 'glossary', 'the finding is audit-lane');
  assert.equal(glossaryRun.code, 0,
    'audit-lane exit-code invariant: an audit-lane glossary finding at error severity must not fail the run');

  // The bundled audits, escalated to error, one profile at a time. Each case
  // escalates whichever rule that profile actually raises, so the test does not
  // depend on a rule id that a future audit change could rename.
  for (const [profile, target, fixtureRule] of [
    ['accessibility', fixture('audits', 'accessibility.html'), 'UE-AX001'],
    ['security', fixture('audits', 'security.html'), 'UE-SE002'],
  ]) {
    // First, a plain run to learn which rules this profile raises here.
    const plain = json(scan(target, '--profile', profile)).findings;
    const present = plain.map(f => f.ruleId);
    assert.ok(present.includes(fixtureRule),
      `the ${profile} fixture still raises ${fixtureRule}, got ${present.join(', ')}`);
    // Escalate every rule the profile raises, so the case cannot pass through
    // a rule that happens to sit at warning while another one is escalated.
    const escalateAll = write(`escalate-${profile}.json`, JSON.stringify({
      rules: Object.fromEntries(present.map(id => [id, { severity: 'error' }])),
    }));
    const run = scan(target, '--profile', profile, '--config', escalateAll);
    const findings = json(run).findings;
    assert.ok(findings.length > 0, `the ${profile} case produces findings`);
    assert.ok(findings.every(f => f.severity === 'error'),
      `audit-lane exit-code invariant: every ${profile} finding is escalated to error severity, got ${JSON.stringify(findings.map(f => [f.ruleId, f.severity]))}`);
    assert.ok(findings.every(f => f.audit === profile),
      `every ${profile} finding is audit-lane`);
    assert.equal(run.code, 0,
      `audit-lane exit-code invariant: error-severity ${profile} audit findings must not fail the run`);
  }

  // Every audit profile at once, every rule it raises escalated to error: the
  // strongest form of the case, since a single dropped guard anywhere in the
  // filter is enough to fail it. The rule list is derived from a plain run, so
  // the case does not rot when an audit gains or renames a check.
  const combinedTarget = fixture('audits', 'publishing-missing.html');
  const combinedArgs = [
    '--profile', 'publishing', '--profile', 'accessibility', '--profile', 'security',
  ];
  const plainCombined = json(scan(combinedTarget, ...combinedArgs)).findings;
  const combinedIds = [...new Set(plainCombined.map(f => f.ruleId))];
  assert.ok(combinedIds.length >= 3,
    `the combined case raises findings across profiles, got ${combinedIds.join(', ')}`);
  assert.ok(plainCombined.every(f => f.audit),
    'the combined case is entirely audit-lane before escalation too');
  const allAudits = write('escalate-all-audits.json', JSON.stringify({
    rules: Object.fromEntries(combinedIds.map(id => [id, { severity: 'error' }])),
  }));
  const combined = scan(combinedTarget, ...combinedArgs, '--config', allAudits);
  const combinedFindings = json(combined).findings;
  assert.ok(combinedFindings.length > 0, 'the combined case produces audit findings');
  assert.ok(combinedFindings.every(f => f.severity === 'error'),
    `every finding in the combined case is error severity, got ${JSON.stringify(combinedFindings.map(f => [f.ruleId, f.severity]))}`);
  assert.ok(combinedFindings.every(f => f.audit),
    'every finding in the combined case is audit-lane');
  assert.equal(combined.code, 0,
    'audit-lane exit-code invariant: with every audit finding at error severity the run still exits 0');

  // The counter-case that keeps the lock honest in the other direction: the
  // same error-severity glossary finding is still reported, still graded error,
  // and still counted in the audit lane. A guard that "protects" the exit code
  // by discarding the finding would satisfy the assertions above and fail here.
  const text = capture([dirtyDraft, '--config', glossaryConfig, '--glossary', glossaryFile]).stdout;
  assert.match(text, /OPTIONAL AUDIT — glossary \(1\)/,
    'the escalated glossary finding is still reported, in its own section');
  assert.match(text, /UE-GL001/,
    'the escalated glossary finding is still reported by id');
  assert.ok(!/EDITORIAL ERRORS/.test(text),
    'an audit-lane finding never renders as an editorial error, even at error severity');

  // JSON: a consumer must not be able to conclude the run failed. The summary
  // counts audits separately from severity, so summary.errors stays 0 while the
  // finding itself carries error severity — the two facts a consumer needs to
  // tell "graded error" apart from "failed the run".
  const glossaryJson = json(glossaryRun);
  assert.equal(glossaryJson.summary.errors, 0,
    'JSON: an error-severity audit finding is not counted as an editorial error');
  assert.deepEqual(glossaryJson.summary.audits, { glossary: 1 },
    'JSON: the audit is counted in the audits summary instead');
  assert.equal(glossaryJson.lanes.audit, 1, 'JSON: the lane counts carry the audit');
  assert.equal(glossaryJson.lanes.deterministic, 0,
    'JSON: an audit finding never lands in the deterministic lane');
  assert.equal(glossaryJson.findings[0].severity, 'error',
    'JSON: the finding still reports its own escalated severity honestly');
  assert.equal(glossaryJson.findings[0].audit, 'glossary',
    'JSON: the audit tag is present, so a consumer can tell why the run passed');

  // SARIF: the level is derived from severity, so an escalated audit finding is
  // level "error" — and the properties must carry the audit tag, or a consumer
  // would have no way to tell an audit from an editorial error. SARIF has no
  // exit-code field, so `audit` is the only signal that keeps the two apart.
  const sarif = json(capture([dirtyDraft, '--config', glossaryConfig, '--glossary', glossaryFile,
    '--format', 'sarif']));
  const result = sarif.runs[0].results[0];
  assert.equal(result.ruleId, 'UE-GL001', 'SARIF: the escalated audit is reported');
  assert.equal(result.level, 'error', 'SARIF: the level follows the escalated severity');
  assert.equal(result.properties.audit, 'glossary',
    'SARIF: the audit property is what stops a consumer reading level "error" as a failed run');
  assert.equal(result.properties.lane, 'audit', 'SARIF: the lane property agrees');
}

// --- 7: SARIF carries the lanes ---------------------------------------------

{
  const sarif = json(capture([fixture('lanes', 'web-p1-demeaning.txt'), '--format', 'sarif']));
  assert.equal(sarif.version, '2.1.0');
  const run0 = sarif.runs[0];
  assert.equal(run0.results.length, 2);
  for (const rule of run0.tool.driver.rules) {
    for (const field of ['lane', 'source', 'profile', 'limitation', 'action']) {
      assert.equal(typeof rule.properties[field], 'string',
        `SARIF rule descriptor carries ${field}`);
    }
    assert(LANE_NAMES.includes(rule.properties.lane));
  }
  for (const result of run0.results) {
    for (const field of METADATA) {
      assert.equal(typeof result.properties[field], 'string',
        `SARIF result carries ${field}`);
    }
    assert.equal(result.properties.lane, 'harmful-discriminatory');
  }
}

// --- 8: the PDF reflects the lanes ------------------------------------------

const PDF_LINE_RE = /\/(F[123]) ([0-9.]+) Tf ([0-9.-]+) ([0-9.-]+) Td \(((?:\\[\s\S]|[^\\()])*)\) Tj/g;
const pdfLines = buffer => [...buffer.toString('latin1').matchAll(PDF_LINE_RE)]
  .map(m => m[5].replace(/\\([()\\])/g, '$1'));

{
  const pdfPath = path.join(tmp, 'lanes.pdf');
  const reported = capture([fixture('lanes', 'web-p1-demeaning.txt'), '--report', pdfPath]);
  assert.equal(reported.code, 1, '--report does not change the failing exit code');
  const lines = pdfLines(fs.readFileSync(pdfPath));
  assert(lines.length > 0, 'the report draws text');
  const joined = lines.join(' ');
  assert.match(joined, /harmful-discriminatory 2/,
    'the PDF carries the lane counts paragraph');
  assert.match(joined, /Lane harmful-discriminatory/,
    'the PDF finding block opens its lane rows with the lane');
  assert.match(joined, /Action High-severity human review/,
    'the PDF finding block carries the recommended human action');
  assert.match(joined, /Source rules\/hate-speech\.md/,
    'the PDF finding block carries the rule source');
  assert.match(joined, /Limitation Wording flagged for high-severity human review/,
    'the PDF finding block carries the limitation');
}

// --- 8b: both report formats carry the same framing disclaimer ---------------
//
// docs/CLAIM-EVIDENCE-AUDIT.md row 22 claims "the report" never presents
// itself as verification of facts, legal opinion or United Nations endorsement.
// There are now two report formats, so the claim only stays true while both
// carry the sentence — and it is worded once, here, so neither renderer can
// drift into its own wording.

const FRAMING = 'The report never presents itself as verification of facts, legal '
  + 'opinion or United Nations endorsement.';

{
  const pdfPath = path.join(tmp, 'framing.pdf');
  const htmlPath = path.join(tmp, 'framing.html');
  capture([fixture('lanes', 'web-p1-demeaning.txt'), '--report', pdfPath]);
  const pdfText = pdfLines(fs.readFileSync(pdfPath)).join(' ');
  assert.ok(pdfText.includes(FRAMING),
    'the PDF states the framing disclaimer named by claim row 22');
  const firstFinding = pdfText.search(/Action |Limitation /);
  assert.ok(pdfText.indexOf(FRAMING) < firstFinding,
    'the PDF leads with the framing disclaimer, before any finding');

  const framed = capture([fixture('lanes', 'web-p1-demeaning.txt'), '--report', htmlPath]);
  assert.equal(framed.code, 1);
  const html = fs.readFileSync(htmlPath, 'utf8');
  assert.ok(html.includes(FRAMING),
    'the HTML report states the same framing disclaimer');
  assert.equal(
    (html.match(new RegExp(FRAMING.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length, 1,
    'the HTML states the framing disclaimer exactly once');
}

// --- 8c: grouping is presentation, never arithmetic --------------------------
//
// PHASE-9-PLAN §2 and DoD 2: grouping must not move a single number. Seven
// occurrences still count as seven everywhere counts appear, in every format,
// and every occurrence the report claims is still listed individually.
//
// This is the one property in Phase 9 that could quietly lie — an issue that
// reads "5 occurrences" over four findings would look entirely reasonable to a
// reader and to a reviewer both — so it is checked against counts derived
// independently from JSON rather than against another report's rendering of the
// same model, and it is checked in both formats in both detail modes.
//
// The fixture is tests/fixtures/fix/protected.md: five findings that share
// rule, text, message, severity and lane, so the grouped report must collapse
// them to exactly one issue while the summary stays at five.

// Both singular and plural forms are correct output: severityCounts drops the
// trailing "s" at exactly one, so the pattern must accept either.
const COUNTS_RE = /(\d+) errors? · (\d+) warnings? · (\d+) notes?/;

const parseCounts = (text) => {
  const m = COUNTS_RE.exec(text);
  assert.ok(m, `no counts line in: ${String(text).slice(0, 200)}`);
  return { errors: Number(m[1]), warnings: Number(m[2]), notes: Number(m[3]) };
};

// Total occurrence rows in the document. The grouped layout draws a single
// table holding every place a defect appears; since D12 the uncapped layout
// draws one table per finding — the same row either way. Counting across every
// table keeps the number meaningful in both modes, where reading only the
// first table would report one row for a document listing five.
const occurrenceRows = (html) => {
  const tables = [...html.matchAll(/<table class="occurrences">([\s\S]*?)<\/table>/g)];
  // One <tr> in each <thead> is the column header, not an occurrence.
  return tables.reduce((n, table) => n + (((table[1].match(/<tr>/g) || []).length) - 1), 0);
};

{
  const target = fixture('fix', 'protected.md');

  const truth = json(capture([target, '--format', 'json']));
  const expected = truth.findings.reduce((acc, finding) => {
    if (finding.severity === 'error') acc.errors += 1;
    else if (finding.severity === 'warning') acc.warnings += 1;
    else acc.notes += 1;
    return acc;
  }, { errors: 0, warnings: 0, notes: 0 });
  assert.equal(truth.findings.length, 5, 'the fixture still fires the five findings the lock is built on');
  assert.ok(truth.findings.length > 1, 'grouping has something to group');

  // JSON is a machine format for CI: one result per finding, and the detail
  // flag is a rendering choice it never sees. Grouping must not reach it.
  const withFlag = capture([target, '--format', 'json', '--report-detail', 'grouped']);
  assert.equal(withFlag.stdout, capture([target, '--format', 'json']).stdout,
    'the grouped detail flag leaves JSON byte-identical');

  const reports = {};
  for (const mode of ['grouped', 'full']) {
    const extra = mode === 'full' ? ['--report-detail', 'full'] : [];
    const pdfPath = path.join(tmp, `counts-${mode}.pdf`);
    const htmlPath = path.join(tmp, `counts-${mode}.html`);
    const pdfRun = capture([target, '--report', pdfPath, ...extra]);
    const htmlRun = capture([target, '--report', htmlPath, ...extra]);
    assert.equal(pdfRun.code, 1, `--report in ${mode} detail keeps the failing exit code`);
    assert.equal(htmlRun.code, 1, `--report in ${mode} detail keeps the failing exit code`);
    reports[mode] = {
      pdf: pdfLines(fs.readFileSync(pdfPath)).join(' '),
      raw: fs.readFileSync(pdfPath).toString('latin1'),
      html: fs.readFileSync(htmlPath, 'utf8'),
    };
  }

  // Every format, both modes, says exactly what JSON says.
  for (const mode of ['grouped', 'full']) {
    assert.deepEqual(parseCounts(reports[mode].pdf), expected,
      `the ${mode} PDF reports the counts JSON proves`);
    const htmlCounts = COUNTS_RE.exec(reports[mode].html);
    assert.ok(htmlCounts, `the ${mode} HTML carries a counts line`);
    assert.deepEqual(
      { errors: Number(htmlCounts[1]), warnings: Number(htmlCounts[2]), notes: Number(htmlCounts[3]) },
      expected,
      `the ${mode} HTML reports the counts JSON proves`);
  }
  assert.equal(reports.grouped.pdf.match(COUNTS_RE)[0], reports.full.pdf.match(COUNTS_RE)[0],
    'grouping does not change a single number in the PDF');
  assert.equal(reports.grouped.html.match(COUNTS_RE)[0], reports.full.html.match(COUNTS_RE)[0],
    'grouping does not change a single number in HTML');

  // The lane line is a count too, and it is the one a reader routes work by.
  const lanesOf = (text) => /lanes: [^D]*/.exec(text)[0].trim();
  assert.equal(lanesOf(reports.grouped.pdf), lanesOf(reports.full.pdf),
    'grouping does not change the PDF lane counts');

  // Every occurrence is still listed: five findings, five rows, whether the
  // report draws them as one issue or as five blocks.
  assert.equal((reports.grouped.pdf.match(/\bFile\b/g) || []).length, truth.findings.length,
    'the grouped PDF lists every finding as its own occurrence row');
  assert.equal(occurrenceRows(reports.grouped.html), truth.findings.length,
    'the grouped HTML lists every finding as its own table row');
  assert.equal(occurrenceRows(reports.full.html), truth.findings.length,
    'the full detail HTML lists every finding too — D12 made it the same row');
  assert.equal((reports.full.pdf.match(/\bFile\b/g) || []).length, truth.findings.length,
    'the full detail PDF lists every finding too, one occurrence block per row');

  // D11: the marks are drawn, and both formats draw the same set. The HTML
  // carries one inline <svg> per severity and per category; the PDF carries a
  // graphics-state block per icon — `q` and `Q` on lines of their own, which
  // is the only way the renderer writes them, since every other `q` in the
  // content stream sits inline with its own operators. A renderer that stopped
  // drawing, or two renderers that disagreed about how many marks a row needs,
  // would break here rather than in a reader's viewer, where a missing icon
  // looks like a printing fault instead of a regression. Each block must also
  // contain a moveto: `pdfIcon` on an empty shape list still opens and closes
  // its graphics state, so counting pairs alone would accept an icon that
  // paints nothing at all.
  const iconBlocks = (raw) => {
    const lines = raw.split('\n');
    const blocks = [];
    let open = -1;
    for (const [index, line] of lines.entries()) {
      if (line === 'q') open = index;
      else if (line === 'Q' && open !== -1) {
        blocks.push(lines.slice(open, index + 1));
        open = -1;
      }
    }
    return blocks;
  };
  for (const mode of ['grouped', 'full']) {
    const svgs = (reports[mode].html.match(/<svg\b/g) || []).length;
    assert(svgs > 0, `the ${mode} HTML draws its marks instead of reaching for an icon font`);
    const blocks = iconBlocks(reports[mode].raw);
    assert.equal(blocks.length, svgs,
      `the ${mode} PDF draws exactly the ${svgs} marks the ${mode} HTML draws`);
    for (const block of blocks) {
      assert(block.some((line) => /^-?[\d.]+ -?[\d.]+ m$/.test(line)),
        'every mark the PDF draws carries geometry: an icon of no shapes draws nothing');
    }
  }

  // Exactly one issue, because all five findings share a key — and the count
  // is shown, because it is more than one.
  assert.equal((reports.grouped.pdf.match(/\b\d+ occurrences\b/g) || []).length, 1,
    'the five findings collapse to exactly one counted issue');
  assert.ok(reports.grouped.pdf.includes('5 occurrences'),
    'the issue states the real number of occurrences');
  assert.ok(!/\b1 occurrences?\b/.test(reports.grouped.pdf),
    'a count is never shown for a group of one');

  // The comparison above is only worth what it can fail. Feed it a report in
  // which one number drifted and prove it rejects it — otherwise this section
  // would pass on a counts line nobody was reading.
  const drifted = reports.grouped.pdf.replace('5 errors', '4 errors');
  assert.notDeepEqual(parseCounts(drifted), expected,
    'the counts comparison actually rejects a report whose count drifted');
}

// --- 8c-ii: the cap is presentation too, never arithmetic -------------------
//
// D7, D8 and D13 (REPORT-REDESIGN-PLAN §4): a capped section may withhold
// findings from the body, but it may not withhold them from the arithmetic.
// The summary counts, the lane counts and the exit code of a capped run must
// be the counts of every finding the scan produced — exactly what they are
// when nothing is withheld — and the cap block must state both the number it
// withheld and a command that lists the rest. Checked in both formats,
// because a cap that only lies in one of them would still be a lie.
//
// The fixture is thirty files carrying two distinct defects, fifteen of each.
// Two groups of fifteen: the second cannot be drawn once the body already
// holds fifteen, so the cap stops at fifteen and withholds fifteen. A single
// group of thirty would have been taken whole and withheld nothing, which is
// not this test — that case is locked in tests/report-model.mjs §11b.

{
  const dir = path.join(tmp, 'cap-corpus');
  fs.mkdirSync(dir, { recursive: true });
  for (let i = 1; i <= 15; i += 1) {
    write(path.join('cap-corpus', `a${i}.txt`),
      'The the organisation reports the figure in the report. This is a very long sentence that is written in the report.\n');
    write(path.join('cap-corpus', `b${i}.txt`),
      'is is the position of the delegation on this article set out below in full in the text of the draft resolution itself.\n');
  }

  const truth = json(capture([dir, '--format', 'json']));
  assert.equal(truth.findings.length, 30,
    'the cap fixture is exactly thirty deterministic warnings');
  const expected = truth.findings.reduce((acc, finding) => {
    if (finding.severity === 'error') acc.errors += 1;
    else if (finding.severity === 'warning') acc.warnings += 1;
    else acc.notes += 1;
    return acc;
  }, { errors: 0, warnings: 0, notes: 0 });
  assert.deepEqual(expected, { errors: 0, warnings: 30, notes: 0 },
    'JSON, which is never capped, proves the truth the reports must agree with');

  const lanesExpected = 'lanes: deterministic 30 · heuristic-review 0'
    + ' · harmful-discriminatory 0 · diplomacy 0 · audit 0 · quoted 0';
  const capLine = 'Showing 15 of 30 · 15 not listed above.';

  const built = {};
  for (const mode of ['grouped', 'full']) {
    const extra = mode === 'full' ? ['--report-detail', 'full'] : [];
    const pdfPath = path.join(tmp, `cap-${mode}.pdf`);
    const htmlPath = path.join(tmp, `cap-${mode}.html`);
    const pdfRun = capture([dir, '--report', pdfPath, ...extra]);
    const htmlRun = capture([dir, '--report', htmlPath, ...extra]);
    assert.equal(pdfRun.code, 0, `a warning-only run exits 0 in ${mode} detail`);
    assert.equal(htmlRun.code, 0, `--report does not change it in ${mode} detail`);
    const terminal = /editorial: (\d+) errors, (\d+) warnings, (\d+) notes/
      .exec(htmlRun.stdout);
    assert.ok(terminal, `${mode}: the terminal states the counts`);
    assert.deepEqual(
      { errors: Number(terminal[1]), warnings: Number(terminal[2]), notes: Number(terminal[3]) },
      expected, `${mode}: the terminal counts every finding, capped or not`);
    built[mode] = {
      pdf: pdfLines(fs.readFileSync(pdfPath)).join(' '),
      html: fs.readFileSync(htmlPath, 'utf8'),
    };
  }

  // Every format in every mode reports what JSON proves. This is the whole
  // claim: a cap reaches the body only.
  for (const mode of ['grouped', 'full']) {
    assert.deepEqual(parseCounts(built[mode].pdf), expected,
      `the capped-or-not ${mode} PDF reports the counts JSON proves`);
    assert.deepEqual(parseCounts(built[mode].html), expected,
      `the capped-or-not ${mode} HTML reports the counts JSON proves`);
    assert.ok(built[mode].pdf.includes(lanesExpected),
      `the ${mode} PDF lane line counts all thirty findings`);
    assert.ok(built[mode].html.includes(lanesExpected),
      `the ${mode} HTML lane line counts all thirty findings`);
  }

  // The header of the section that got capped claims the whole count, not the
  // drawn subset. Both detail modes of the HTML draw lane sections, so both
  // are checked; the PDF's `full` mode hangs its body off Findings by file
  // instead, and that is the header checked there.
  assert.ok(built.grouped.html.includes(
    '<span class="sec-t">Editorial Warnings</span>'
    + '<span class="sec-d">deterministic · warning only</span>'
    + '<span class="sec-c">30 findings</span>'),
    'the capped section header claims all thirty findings, not the fifteen drawn');
  assert.ok(built.full.html.includes(
    '<span class="sec-t">Editorial Warnings</span>'
    + '<span class="sec-d">deterministic · warning only</span>'
    + '<span class="sec-c">30 findings</span>'),
    'the uncapped HTML header claims the same thirty');
  assert.ok(built.full.pdf.includes(
    'Findings by file full detail · every finding 30 findings'),
    'the uncapped PDF header claims the same thirty');
  assert.ok(built.grouped.pdf.includes(
    'Editorial Warnings deterministic · warning only 30 findings'),
    'the PDF sets the same count beside the same header, on the same line');

  // The cap block itself: present in grouped in both formats, absent from
  // full, and phrased so that both the number withheld and the command that
  // lists the rest are on the page.
  assert.ok(built.grouped.html.includes(capLine),
    'the grouped HTML states how much it withheld');
  assert.ok(built.grouped.pdf.includes(capLine),
    'the grouped PDF states how much it withheld');
  assert.ok(!built.full.html.includes('Showing '), 'the full HTML never caps');
  assert.ok(!/\bShowing \d+ of \d+/.test(built.full.pdf), 'the full PDF never caps');

  const command = /un-editorial-check [^<]*--report-detail full --report \S+/
    .exec(built.grouped.html);
  assert.ok(command, 'the cap block prints a runnable re-run command');
  assert.ok(command[0].includes('--report-detail full'),
    'and that command asks for the detail level that lists everything');
  assert.ok(built.grouped.pdf.includes('--report-detail full'),
    'the PDF cap block prints the same command');

  // Grouping and capping are both presentation: the grouped body draws the one
  // group that fit, whole; the full body draws all thirty findings.
  assert.equal((built.grouped.html.match(/<article class="finding/g) || []).length, 1,
    'the capped grouped body draws only the group that fitted, whole');
  assert.equal((built.full.html.match(/<article class="finding/g) || []).length, 30,
    'the uncapped full body draws every finding');

  // Read the cap line the way a reader does: its three numbers must reconcile
  // with each other, with the truth JSON proves, and with the occurrences the
  // body actually drew. A cap saying 20 while 15 rows are listed would fail
  // the last of these — the drift this section exists to catch.
  const cap = /Showing (\d+) of (\d+) · (\d+) not listed above\./.exec(built.grouped.html);
  assert.ok(cap, 'the cap line is parseable');
  assert.equal(Number(cap[2]), truth.findings.length,
    'the cap line counts the whole scan, not the section');
  assert.equal(Number(cap[1]) + Number(cap[3]), Number(cap[2]),
    'what is drawn plus what is withheld is everything');
  assert.deepEqual(
    { shown: Number(cap[1]), withheld: Number(cap[3]) },
    { shown: 15, withheld: 15 },
    'the cap drew one whole group and withheld the other');
  assert.equal(occurrenceRows(built.grouped.html), Number(cap[1]),
    'the occurrences the body lists add up to exactly what the cap claims to have shown');
}

// --- 9: quoted material is a context, not a lane ----------------------------

// Quoted spans are masked by extraction (a quotation is never scanned as the
// author's copy), so a scan over quoted content reports only the authored
// findings — and the report layer's quoted routing for an explicit
// `finding.context` is pinned in tests/report-model.mjs. Here: the CLI always
// annotates context, and quoting never deletes authored findings.
{
  const file = write('quoted.md',
    'Coverage was 1990-2025.\n\n"Coverage was 1990-2025," she said.\n');
  const parsed = json(scan(file));
  assert.equal(parsed.lanes.quoted, 0, 'a masked quotation produces no phantom finding');
  for (const finding of parsed.findings) {
    assert.equal(typeof finding.context, 'string', 'every CLI finding carries a context');
    assert.equal(finding.context, 'authored', 'authored copy is not quoted context');
    assert.equal(finding.line, 1, 'the authored line still reports');
  }
}

// --- 10: banned-phrase sweep over every rendered output ----------------------

const BANNED = /UN approved|fully compliant|finds all errors|factual verification|legal advice/i;
for (const output of rendered) {
  assert(!BANNED.test(output), `banned phrase in rendered output:\n${output}`);
}

console.log('ok — lanes: metadata, safety lane, diplomacy lane, sections, heuristic flip, '
  + 'audit lane, audit exit-code invariant, SARIF, PDF, quoted context, framing on both formats, '
  + 'grouping is presentation: counts and occurrence rows equal JSON in every format and mode, '
  + 'the same drawn marks in both formats, '
  + 'terminal category marker and twelve-category legend, banned phrases');
