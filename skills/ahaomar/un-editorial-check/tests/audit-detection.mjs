// un-editorial-check — detection quick-win contract tests.
//
// Standalone: `node tests/audit-detection.mjs`. Each section locks one
// detection contract that the fixture corpus in tests/run.mjs does not carry:
//
//   1. the shared attribution guard (UE-DP001 + the hate-speech family):
//      full reporting-verb stem families, and a trailing attribution whose
//      joining comma is optional;
//   2. UE-HS003 modal outcomes: clause-final or exclusion-continuation only,
//      so operational copy (routes, documents) stays silent;
//   3. UE-RE002: the fixed economic term "leading indicator(s)" is exempt,
//      every other ranking claim still fires;
//   4. UE-RE004: `current` is the full question (300-character cap with
//      "..." beyond), not a 40-character prefix, and the rule is never fixable;
//   5. UE-TE004: sentence-final bare `US.` is reported, the currency,
//      acronym and URL exemptions still hold;
//   6. UE-HS002: the group must be the subject of the copula. A preposition
//      immediately before it makes the group the preposition's complement, so a
//      comparative about rights, conditions, services or data is no longer
//      reported as collective blame — and every required true positive, partitive
//      included, still fires.
//
// Every prose string below reaches the scanner through a call name that is
// not a render surface (scan/fires/silent), so the repository self-scan never
// extracts this file's test data as user-visible copy.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-detection-'));
const config = path.join(tmp, 'config.json');
fs.writeFileSync(config, '{}');

let sequence = 0;
const scan = (prose) => {
  const file = path.join(tmp, `probe-${sequence++}.txt`);
  fs.writeFileSync(file, prose.endsWith('\n') ? prose : `${prose}\n`);
  const out = [];
  const err = [];
  const code = run([file, '--format', 'json', '--config', config], {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  let parsed;
  try { parsed = JSON.parse(out.join('\n')); }
  catch { return assert.fail(`stdout is not JSON:\n${out.join('\n')}\n${err.join('\n')}`); }
  return { code, findings: parsed.findings, stderr: err.join('\n') };
};
const ids = result => [...new Set(result.findings.map(f => f.ruleId))].sort();
const silent = (prose) => {
  const result = scan(prose);
  assert.deepEqual(ids(result), [], `${prose} must produce no findings`);
};
const fires = (ruleId, prose) => {
  const result = scan(prose);
  const finding = result.findings.find(entry => entry.ruleId === ruleId);
  assert(finding,
    `expected ${ruleId} in: ${prose} (got ${ids(result).join(', ') || 'no findings'})${result.stderr}`);
  return finding;
};

// --- 1. attribution guard: full stem families, comma-optional trailing form ---

{
  // Trailing attribution without a comma: the reporting verb may follow the
  // claim directly — "Taiwan is part of China the envoy said yesterday."
  const trailingVerbs = [
    'confirmed', 'states', 'stated', 'observed', 'told', 'underlined',
    'highlighted', 'commented', 'warned', 'explained', 'clarified',
    'remarked', 'said',
  ];
  for (const verb of trailingVerbs) {
    silent(`Taiwan is part of China the envoy ${verb} yesterday.`);
  }
  // The joined form with the comma keeps working.
  silent('Taiwan is part of China, the envoy said yesterday.');

  // Leading attribution: the same stem families before the claim.
  const leadingVerbs = [
    'confirmed', 'states', 'observed', 'told', 'underlined',
    'highlighted', 'commented', 'warned', 'explained', 'clarified', 'remarked',
  ];
  for (const verb of leadingVerbs) {
    silent('The envoy ' + verb + ' that Taiwan is part of China.');
  }

  // The same guard serves the hate-speech family (lib/rules-hs.mjs).
  silent('The report states that refugees are vermin.');
  silent('The spokesperson confirmed that refugees are vermin.');
  silent('The spokesperson told reporters that refugees are vermin.');
  silent('The envoy commented that all Syrians are terrorists.');

  // The trailing window is the first six words after the claim.
  silent('Taiwan is part of China the envoy in the capital said yesterday.');
  fires('UE-DP001', 'Taiwan is part of China the envoy in the great capital said yesterday.');

  // Regression pins: naked claims must keep firing.
  fires('UE-DP001', 'Taiwan is part of China.');
  fires('UE-HS002', 'All Syrians are terrorists.');
  fires('UE-HS003', 'Foreigners must go.');
  fires('UE-HS001', 'The refugees are vermin.');

  // Attribution in a PRIOR sentence attributes nothing in this one.
  fires('UE-DP001', 'The minister spoke at length. Crimea is part of Russia.');
  fires('UE-DP001', 'The minister confirmed the report. Crimea is part of Russia.');
  fires('UE-DP001', 'The minister warned the chamber. Crimea is part of Russia.');
}

console.log('ok — attribution guard: stem families, trailing window, regression pins');

// --- 2. UE-HS003: modal outcome ends the clause or heads an exclusion phrase --

{
  // Benign operational copy: a route or an object after the outcome is
  // procedure, not a call for exclusion.
  silent('Refugees should go through the registration process at the border.');
  silent('Migrants must leave their documents at the checkpoint.');
  silent('Refugees must go to the reception centre.');

  // Exclusion demands keep firing, and `current` spans the fuller phrase
  // when an exclusion continuation follows the outcome.
  assert.equal(fires('UE-HS003', 'Foreigners must go.').current, 'Foreigners must go');
  assert.equal(fires('UE-HS003', 'Muslims must go.').current, 'Muslims must go');
  assert.equal(fires('UE-HS003', 'Foreigners should leave the country.').current,
    'Foreigners should leave the country');
  assert.equal(fires('UE-HS003', 'Migrants should leave the nation.').current,
    'Migrants should leave the nation');

  // Base-form verb template and the expelled/deported outcome forms.
  fires('UE-HS003', 'Deport all refugees.');
  fires('UE-HS003', 'Round up the Palestinians.');
  fires('UE-HS003', 'Deport all Iraqis.');
  fires('UE-HS003', 'Kill all Muslims.');
  fires('UE-HS003', 'Ban Nigerians from the scheme.');
  fires('UE-HS003', 'Refugees must be deported.');
  fires('UE-HS003', 'The refugees must be expelled.');
}

console.log('ok — UE-HS003: clause-final / exclusion continuation, operational copy silent');

// --- 3. UE-RE002: "leading indicator(s)" is a fixed economic term -------------

{
  silent('The leading indicator improved in the third quarter of 2026.');
  silent('Leading indicators point to growth.');

  // Every other ranking use of "leading", and the other superlatives, fire.
  fires('UE-RE002', 'The leading candidate won the vote.');
  fires('UE-RE002', 'The largest city grew.');
  fires('UE-RE002', 'The best result was recorded.');
  fires('UE-RE002', 'The fastest growth was recorded.');
}

console.log('ok — UE-RE002: leading-indicator exception, ranking claims unchanged');

// --- 4. UE-RE004: `current` is the full question, capped at 300 characters ----

{
  const finding = fires('UE-RE004', 'Why should Member States wait for the report?');
  assert.equal(finding.current, 'Why should Member States wait for the report?');
  // Message, suggestion and severity are unchanged by the current-field fix.
  assert.equal(finding.severity, 'warning');
  assert.equal(finding.message, 'Question phrased for effect — UN copy states findings directly.');
  assert.equal(finding.suggestion,
    'Rewrite as a declarative statement unless the question is genuinely soliciting information.');
}
{
  // The whole sentence, not a 40-character prefix.
  const question = 'Why should Member States wait for the report when the evidence is already '
    + 'before the Council and the alternative is further delay for populations in need of '
    + 'protection and assistance from every partner this body can mobilize?';
  assert(question.length > 40, 'the probe question must exceed the old 40-character cut');
  assert.equal(fires('UE-RE004', question).current, question);
}
{
  // Beyond 300 characters the field is capped with an ellipsis.
  const question = `Why should Member States wait ${'for a decision when the evidence is already before the Council and the alternative is further delay '.repeat(5)}now?`;
  assert(question.length > 300, 'the probe question must exceed the cap');
  const finding = fires('UE-RE004', question);
  assert.equal(finding.current, question.slice(0, 300) + '...',
    'the cap is 300 characters plus "..."');
  assert.equal(finding.current.length, 303);
}
{
  // UE-RE004 is not fixable: --fix never rewrites the question.
  const file = path.join(tmp, 're004-not-fixable.txt');
  const prose = 'Why should Member States wait for the report?\n';
  fs.writeFileSync(file, prose);
  const out = [];
  const code = run([file, '--fix', '--apply', '--config', config], {
    log: line => out.push(String(line)),
    error: () => {},
  });
  assert.equal(fs.readFileSync(file, 'utf8'), prose,
    'UE-RE004 must never be rewritten by --fix');
  assert.doesNotMatch(out.join('\n'), /APPLIED/, '--fix must not claim a fix it did not make');
  assert.equal(code, 0, 'a warning-only file exits 0 after --fix');
}

console.log('ok — UE-RE004: full-sentence current, 300-character cap, never fixable');

// --- 5. UE-TE004: sentence-final bare US is reported --------------------------

{
  const finding = fires('UE-TE004', 'Coverage was 1990-2025 in the US.');
  assert.equal(finding.current, 'US');

  // Mid-sentence bare US keeps firing.
  fires('UE-TE004', 'The US reported a higher value than its neighbour.');

  // The documented exemptions still hold (rules/terminology.md).
  silent('Payment in US dollars was approved for the programme.');
  silent('The US dollar is used in the report.');
  silent('The current US$ value is shown below.');
  silent('The U.S.A. position was recorded in the annex.');
  silent('See the report at https://example.test/US/100%25/report for detail.');

  // Hyphenated compound: pinned at whatever the engine does today — it
  // reports bare "US" (the hyphen ends the word), and this lock records it.
  assert.equal(fires('UE-TE004', 'The US-based supplier was selected.').current, 'US');
}

console.log('ok — UE-TE004: sentence-final US reported, exemptions intact, US-based pinned');

// --- 6. UE-HS002: the group must be the subject of the copula ----------------
//
// The false positives this removes are not marginal. "The rights of women are
// inferior to those guaranteed to men" is a statement about rights: the copula's
// subject is *rights*, and women is the object of a preposition. The rule
// matched it, and the tool then told an editor to rewrite wording it had
// misparsed. Same for data, welfare, access and outcomes.
//
// The lock moves with the change: every required true positive — the two
// guard-note templates, the bare trait form, and the partitive "All of the …"
// that .feedbacks/old/verify-hs.mjs and the dummydata corpus both depend on —
// is asserted below over the whole shared group vocabulary, and the gate is
// proved to apply to UE-HS002 alone.

{
  // --- the true positives, which must all still fire ---------------------
  const mustFire = [
    'All Syrians are criminals.',
    'All of the foreigners are criminals.',
    'Muslims are inherently violent.',
    'Kurds are dangerous by nature.',
    'Migrants are dangerous.',
    'Women are inferior to men in the published ranking.',
    'The men were dangerous because they were armed.',
    'All of the women are criminals.',
    'All of the older people are criminals.',
    'All of those refugees are criminals.',
  ];
  for (const prose of mustFire) {
    const result = scan(prose);
    const finding = result.findings.find(entry => entry.ruleId === 'UE-HS002');
    assert(finding,
      `UE-HS002 must still fire on the true positive ${JSON.stringify(prose)}`
      + ` (got ${ids(result).join(', ') || 'no findings'})`);
    // The finding is still a review-lane heuristic, not an error.
    assert.equal(finding.severity, 'warning', `${prose}: UE-HS002 stays a warning`);
    assert.match(finding.message, /routed to review/,
      `${prose}: UE-HS002 must still say it is routed to review`);
  }

  // --- the full group vocabulary through the two guard-note templates ------
  // The symmetry sweep in .feedbacks/old/verify-hs.mjs is the contract; this is
  // the same sweep as an in-repo lock, so the gate cannot be widened later
  // without a test failing here first.
  const { HS_KB } = await import('../lib/rules-hs.mjs');
  const groups = HS_KB.groups.terms;
  assert(groups.length >= 30, 'the shared group vocabulary must stay substantial');
  for (const group of groups) {
    for (const template of ['All %s are criminals.', '%s are inherently violent.',
      'All of the %s are criminals.']) {
      const prose = template.replace('%s', group);
      const result = scan(prose);
      assert(result.findings.some(entry => entry.ruleId === 'UE-HS002'),
        `symmetry: ${JSON.stringify(prose)} must fire UE-HS002`
        + ` (got ${ids(result).join(', ') || 'no findings'})`);
    }
  }

  // --- the false positives, which must now be silent --------------------
  // Each is a comparative about rights, conditions, services, data or
  // outcomes: the group is the complement of a preposition, and the trait is
  // predicated of the head noun instead.
  for (const prose of [
    'The rights of women are inferior to those guaranteed to men.',
    'The situation for women is inferior to the situation for men.',
    'Data on older people are inferior in quality to other data.',
    'The welfare of refugees is inferior to that of others.',
    'Access to justice for migrants is inferior to that for others.',
    'Outcomes for girls are inferior to those for boys.',
    'The situation with refugees is dire.',
    'Attitudes to migrants are negative in several countries.',
    'Statistics about disabled people are inferior in quality.',
    'Concern about asylum seekers is growing.',
    'The report on Roma communities is critical.',
    'Standards for wheelchair users are inferior to those for others.',
  ]) {
    const result = scan(prose);
    assert(!result.findings.some(entry => entry.ruleId === 'UE-HS002'),
      `UE-HS002 must not fire on the comparative ${JSON.stringify(prose)}`
      + ` (got ${JSON.stringify(result.findings.filter(f => f.ruleId === 'UE-HS002').map(f => f.current))})`);
  }

  // --- the gate is bounded: a comma or any other word ends the phrase ----
  // The window is a fixed 60 characters, so a prepositional phrase that is not
  // immediately adjacent to the group leaves the group as the subject and the
  // finding stands. The trait form is used because it matches without a
  // quantifier; the accusation noun needs "all", which is why the quantified
  // variants below carry one.
  fires('UE-HS002', 'In Europe, refugees are inherently violent.');
  fires('UE-HS002', 'Of all the groups, migrants are dangerous by nature.');
  fires('UE-HS002', 'Under review by the committee, all foreigners are criminals.');
  fires('UE-HS002', 'Since the report appeared, all Syrians are criminals.');  // ue:ignore UE-HS002  (deliberate test data)
  // A prepositional phrase that ends well before the group, by length alone.
  fires('UE-HS002',
    `A committee of experts on humanitarian law and procedure ${'and practice ' * 8}reported that all Syrians are criminals.`);  // ue:ignore UE-HS002  (deliberate test data)

  // --- the gate belongs to UE-HS002 alone --------------------------------
  // UE-HS001 and UE-DM001 keep matching their own compositions: a
  // dehumanising frame and a demeaning predicate still fire after the same
  // preposition, because their guard notes promise exactly that.
  {
    const hs1 = scan('The report on refugees is vermin in tone.');
    assert(hs1.findings.some(f => f.ruleId === 'UE-HS001'),
      'the subject gate must not reach UE-HS001: its guard note promises the frame fires on its own composition');
  }
  {
    const dm = scan('The report on women is a burden on the process.');
    assert(dm.findings.some(f => f.ruleId === 'UE-DM001'),
      'the subject gate must not reach UE-DM001: its guard note promises the predicate fires on its own composition');
  }
  // And the two rules that consume the same vocabulary keep their symmetry.
  fires('UE-HS001', 'Foreigners are vermin.');
  fires('UE-HS001', 'Muslims are vermin.');
  fires('UE-DM001', 'Women are a burden.');
  fires('UE-DM001', 'Men are a burden.');
}

console.log('ok — UE-HS002: subject gate on comparatives, every true positive still fires');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — detection contracts: attribution, HS003, RE002, RE004, TE004, HS002 subject gate');
