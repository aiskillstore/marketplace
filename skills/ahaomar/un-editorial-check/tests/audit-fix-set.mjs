// Wave 4 (Agent C) contract: the --fix set is a fail-closed allow-list
// (remediation brief §8).
//
//   1. FIXABLE_RULE_IDS is exactly the spelling / numeral-range / clean
//      grammar set — and nothing from terminology, dates, claims, political
//      wording, quotations, harmful content or sourcing can ever enter it;
//   2. planFixes is fail-closed: a finding for any rule outside the list
//      never becomes an edit, no matter how deterministic its replacement
//      looks, and every catalogue rule is probed this way so a future rule
//      is auto-excluded until someone deliberately allows it;
//   3. the CLI honours the list end to end: terminology findings are still
//      reported (exit 1), but `--fix --apply` writes nothing for them, while
//      spelling and numeral-range fixes in the same file are still applied.
//
// TDD: written before the allow-list landed in lib/fix.mjs.
// Standalone: node tests/audit-fix-set.mjs
// Only node:assert, the modules under test and the in-process CLI are used;
// every fixture lives in a fresh mkdtemp directory under os.tmpdir().

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run, CATALOGUE } from '../bin/check.mjs';
import { planFixes, FIXABLE_RULE_IDS, assertProseOnly } from '../lib/fix.mjs';
import { SUPPORTED_EXTENSIONS } from '../lib/extract.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-fixset-'));

const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
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
const ids = (file) => {
  const result = capture([file, '--format', 'json']);
  assert.notEqual(result.code, 2, `scan failed for ${file}: ${result.stderr}`);
  return JSON.parse(result.stdout).findings.map(f => f.ruleId).sort();
};

// --- 1. the exact allow-list --------------------------------------------------

assert.deepEqual([...FIXABLE_RULE_IDS].sort(),
  ['UE-GR001', 'UE-GR002', 'UE-GR003', 'UE-GR004', 'UE-NU002', 'UE-SP001'],
  'the fixable set is exactly spelling, en-dash ranges and clean grammar');

for (const id of FIXABLE_RULE_IDS) {
  const rule = CATALOGUE.rules.find(entry => entry.id === id);
  assert(rule, `${id} must be a catalogue rule`);
  assert(['spelling', 'numerals', 'grammar'].includes(rule.category),
    `${id} may only be fixable inside a brief-§8 category, got ${rule.category}`);
}
// §8 names the families that must never be auto-changed. No allow-listed id
// may belong to them, and the date rule is called out explicitly because it
// sits inside the otherwise fixable "numerals" category.
const NEVER_AUTO = new Set(['terminology', 'diplomacy', 'hate-speech', 'register', 'agent-review']);
for (const id of FIXABLE_RULE_IDS) {
  const rule = CATALOGUE.rules.find(entry => entry.id === id);
  assert(!NEVER_AUTO.has(rule.category), `${id} (${rule.category}) must never be auto-fixed`);
}
assert(!FIXABLE_RULE_IDS.has('UE-NU001'), 'numeric dates are never auto-fixed');

// --- 2. planFixes is fail-closed over every catalogue rule --------------------

{
  const file = write('synthetic.txt', 'The organization covered 25% during 1990-2025 in the US.\n');
  const source = fs.readFileSync(file, 'utf8');
  const sources = new Map([[file, source]]);

  const finding = (ruleId) => ({
    file,
    line: 1,
    column: source.indexOf('organization') + 1,
    ruleId,
    category: 'synthetic',
    severity: 'error',
    confidence: 'deterministic',
    scope: 'user-visible-copy',
    message: 'synthetic probe',
    suggestion: null,
    current: 'organization',
    proposed: 'organisation',
    _unit: { offset: 0, raw: source },
    _index: 0,
    _matched: 'organization',
    _offset: source.indexOf('organization'),
    _replacement: 'organisation',
  });

  for (const rule of CATALOGUE.rules) {
    const plans = planFixes([finding(rule.id)], sources);
    if (FIXABLE_RULE_IDS.has(rule.id)) {
      assert.equal(plans.length, 1, `${rule.id} is allow-listed and must produce one plan`);
      assert.equal(plans[0].after,
        source.replace('organization', 'organisation'),
        `${rule.id}: the edit must rewrite only the matched copy`);
    } else {
      assert.deepEqual(plans, [],
        `${rule.id} is outside the fixable set and must never produce an edit`);
    }
  }

  // A mixed file: the allow-listed edit lands, the terminology edit does not,
  // and the plan never claims a write it will not perform.
  const mixed = planFixes([finding('UE-TE003'), finding('UE-SP001')], sources);
  assert.equal(mixed.length, 1, 'only the allow-listed finding may be planned');
  assert.deepEqual(mixed[0].edits.map(edit => edit.ruleId), ['UE-SP001'],
    'a terminology edit must never share a plan with a spelling edit');

  // The finding objects themselves are never mutated by the filter.
  const probe = finding('UE-TE004');
  const snapshot = JSON.parse(JSON.stringify(probe));
  planFixes([probe], sources);
  assert.deepEqual(JSON.parse(JSON.stringify(probe)), snapshot,
    'the filter must not mutate or strip the finding it skips');
}

// --- 2b. the fixable extension set --------------------------------------------
//
// The rule allow-list above is only half the gate. `--fix` also refuses any file
// that is not prose, and that set is the one PDF joins in 1.3.0: a PDF is
// readable now, so it passes the scanner and reaches the fixer, where it must
// still be refused. Both halves are locked here rather than left to the next
// reader of lib/fix.mjs to infer.
//
// The split is asserted in both directions, because a one-way assertion would
// pass if `PROSE_EXTENSIONS` grew to include `.pdf` — the exact regression this
// section exists to prevent, since a PDF is a rendered page and rewriting one
// in place is not a text edit at all.

const PROSE_FIXABLE = ['.md', '.markdown', '.txt'];

{
  for (const ext of PROSE_FIXABLE) {
    assert.doesNotThrow(() => assertProseOnly([`notes${ext}`]),
      `${ext} is prose and --fix may accept it`);
  }
  for (const ext of SUPPORTED_EXTENSIONS.filter(e => !PROSE_FIXABLE.includes(e))) {
    assert.throws(() => assertProseOnly([`copy${ext}`]),
      err => /refusing --fix/.test(err.message),
      `${ext} is supported for reading but must stay refused by --fix`);
  }
  assert.throws(() => assertProseOnly(['copy.pdf']),
    err => /refusing --fix/.test(err.message),
    'a PDF is never rewritten: --fix refuses it like every other non-prose format');
}

// --- 2c. a refused PDF is a refusal, not a clean run --------------------------
//
// The shape of QA finding F1, arrived at from the other direction: a run that
// read nothing printed the clean sentence. A PDF the tool cannot read must not
// be able to do the same thing. Locked here because the PDF refusal is the
// newest way for a run to read nothing, and this is the assertion that keeps it
// from reporting success.
//
// The engine is not stubbed. `lib/pdf-extract.mjs` refuses a buffer that is not
// a PDF at all, which is a real refusal on the real code path and needs no
// engine to be present: the adapter's own NOT_A_PDF check runs before the
// engine is consulted. The full engine refusal set is locked by P2's
// `tests/audit-pdf-extraction.mjs` against the real engine.

{
  const fake = write('not-really.pdf', 'this is plain text, not a PDF\n');
  const result = capture([fake]);
  assert.equal(result.code, 2,
    `a PDF that is not a PDF must refuse with exit 2: ${result.stdout}${result.stderr}`);
  assert.doesNotMatch(result.stdout, /No findings under the enabled/,
    'a refused PDF must never print the clean sentence (F1)');
  assert.equal(result.stdout, '',
    'a refusal writes nothing to stdout, so no consumer can read it as a result');
  assert.match(result.stderr, /cannot read/, 'the refusal names the reason');
  assert.match(result.stderr, /not a PDF document/, 'the refusal states the reason in plain words');
  assert.ok(result.stderr.includes(fake), 'the refusal names the path');

  // --fix on the same file is refused too, and the bytes are untouched. This
  // file is refused by the PDF adapter before the fixer is reached, because it
  // is not a PDF; both are exit-2 refusals naming a reason, and neither writes.
  // The `refusing --fix` message for a genuine PDF is asserted in 2b above,
  // where `assertProseOnly` is called directly.
  const before = fs.readFileSync(fake);
  const fix = capture([fake, '--fix', '--apply']);
  assert.equal(fix.code, 2, `--fix on a PDF must refuse with exit 2: ${fix.stderr}`);
  assert.doesNotMatch(fix.stdout, /No findings under the enabled/,
    '--fix on a refused PDF must never print the clean sentence (F1)');
  assert.deepEqual(fs.readFileSync(fake), before, 'a refused --fix never writes');
}

// --- 3. the CLI end to end -----------------------------------------------------

{
  // Terminology alone: reported, exit 1, byte-for-byte untouched.
  // UE-TE003 is silent after the terminology rework (locked in
  // tests/audit-terminology.mjs); UE-TE004 carries the error, flag-only.
  const file = write('terminology.txt', 'The US reported 25% in the period.\n');
  const before = fs.readFileSync(file, 'utf8');
  const preview = capture([file, '--fix']);
  assert.equal(preview.code, 1, `a terminology error must still fail the preview: ${preview.stderr}`);
  assert.doesNotMatch(preview.stdout, /APPLIED/, 'a preview never applies');
  const applied = capture([file, '--fix', '--apply']);
  assert.equal(applied.code, 1, `a terminology error must still fail the run: ${applied.stderr}`);
  assert.doesNotMatch(applied.stdout, /APPLIED/, '--fix must not claim a fix it did not make');
  assert.equal(fs.readFileSync(file, 'utf8'), before,
    'terminology findings must never be rewritten');
  assert.ok(ids(file).includes('UE-TE004') && !ids(file).includes('UE-TE003'),
    'UE-TE004 is reported; UE-TE003 no longer fires in the default run');
}

{
  // Mixed file: only the allow-listed spelling edit applies. `color` is a
  // non-conflict map entry — the organisation/organization family is
  // profile-choice, warning and not fixable by default after W2a — and
  // UE-TE003 is silent after the terminology rework, so the sign survives
  // with nothing left to fail the run.
  const file = write('mixed.txt', 'The color covered 25% of the total.\n');
  const applied = capture([file, '--fix', '--apply']);
  assert.equal(applied.code, 0, `nothing but the fixable spelling error remains: ${applied.stderr}`);
  assert.equal(fs.readFileSync(file, 'utf8'),
    'The colour covered 25% of the total.\n',
    'only the allow-listed spelling edit may be written');
  assert.ok(!ids(file).includes('UE-TE003'), 'UE-TE003 must not fire in the default run');
}

{
  // Controls: the allow-listed rules still apply and still clean the file.
  const spelling = write('spelling.txt', 'The color reports.\n');
  const spellingRun = capture([spelling, '--fix', '--apply']);
  assert.equal(spellingRun.code, 0, `a fully fixable file must exit 0: ${spellingRun.stderr}`);
  assert.equal(fs.readFileSync(spelling, 'utf8'), 'The colour reports.\n');
  assert.match(spellingRun.stdout, /APPLIED — \d+ replacement/);

  const ranges = write('ranges.txt', 'Coverage was 1990-2025.\n');
  const rangesRun = capture([ranges, '--fix', '--apply']);
  assert.equal(rangesRun.code, 0, `a numeral-range fix must exit 0: ${rangesRun.stderr}`);
  assert.equal(fs.readFileSync(ranges, 'utf8'), 'Coverage was 1990–2025.\n');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — fix set: exact allow-list, fail-closed planFixes, CLI honours §8');
console.log('ok — fix set: prose-only extension gate, a PDF never rewritten, a refused PDF is exit 2 and never a clean run');
