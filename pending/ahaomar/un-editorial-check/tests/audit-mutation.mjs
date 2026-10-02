// un-editorial-check — variant (mutation) contract tests.
//
// Standalone: `node tests/audit-mutation.mjs`. For a representative rule in
// every deterministic family the suite proves three properties, then proves
// the rules obey configuration:
//
//   1. the rule fires on a minimal document that carries its defect;
//   2. the same document with the defect removed falls silent for that rule —
//      the detector is keyed to the defect, not to the topic;
//   3. configuration changes take effect: disabling a rule silences it, and a
//      severity flip downgrades an error to a warning and removes it from
//      the exit code.
//
// Every probe string below reaches the scanner through a call name that is
// not a render surface (scan/fires/absent/silent), so the repository
// self-scan never extracts this file's test data as user-visible copy. All
// probes and controls were verified against the shipped rules before being
// pinned here.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { run } from '../bin/check.mjs';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-mutation-'));

let configSequence = 0;
const configFor = (spec) => {
  const file = path.join(tmp, `config-${configSequence++}.json`);
  fs.writeFileSync(file, JSON.stringify(spec));
  return file;
};
const baseConfig = configFor({});
let fileSequence = 0;

/** Write one probe document outside the repository and scan it as JSON. */
const scan = (prose, { config = baseConfig, flags = [], ext = 'txt' } = {}) => {
  const file = path.join(tmp, `probe-${fileSequence++}.${ext}`);
  fs.writeFileSync(file, prose.endsWith('\n') ? prose : `${prose}\n`);
  const out = [];
  const err = [];
  const code = run([file, '--format', 'json', '--config', config, ...flags], {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  let parsed;
  try { parsed = JSON.parse(out.join('\n')); }
  catch { return assert.fail(`stdout is not JSON:\n${out.join('\n')}\n${err.join('\n')}`); }
  return { code, findings: parsed.findings, stderr: err.join('\n') };
};
const ids = result => [...new Set(result.findings.map(f => f.ruleId))].sort();
const fires = (ruleId, prose, opts) => {
  const result = scan(prose, opts);
  const finding = result.findings.find(entry => entry.ruleId === ruleId);
  assert(finding,
    `expected ${ruleId} in: ${prose} (got ${ids(result).join(', ') || 'no findings'})${result.stderr}`);
  return result;
};
const absent = (ruleId, prose, opts) => {
  const result = scan(prose, opts);
  assert(!result.findings.some(entry => entry.ruleId === ruleId),
    `expected ${ruleId} absent in: ${prose} (got ${ids(result).join(', ') || 'no findings'})${result.stderr}`);
  return result;
};
const silent = (prose, opts) => {
  const result = scan(prose, opts);
  assert.deepEqual(ids(result), [], `${prose} must produce no findings${result.stderr}`);
  return result;
};

// --- 1. spelling, grammar, numerals: fire on the defect, silent without it ---

fires('UE-SP001', 'The color of the flag was noted by the delegation.');
silent('The colour of the flag was noted by the delegation.');

fires('UE-GR001', 'The the report was clear.');
silent('The report was clear.');

fires('UE-GR002', 'The report was reviewed , and the annex follows.');
silent('The report was reviewed, and the annex follows.');

fires('UE-GR003', 'The report was clear.Annex A follows here.');
silent('The report was clear. Annex A follows here.');

fires('UE-NU001', 'The session was held on 31/12/2025 in Geneva.');
silent('The session was held on 31 December 2025 in Geneva.');

fires('UE-NU002', 'The meetings run from 5-7 March 2026.');
silent('The meetings run from 5 to 7 March 2026.');
silent('The meetings run from 5–7 March 2026.');

console.log('ok — spelling, grammar and numeral families: defect fires, repaired form is silent');

// --- 2. terminology, register: fire on the defect, silent without it --------

fires('UE-TE001', 'The maternal mortality rate was 120 per 100 000 live births.');
silent('The maternal mortality rate rose in the region.');
// UE-TE003 is documented-silent since the terminology rework: the live UN
// Numbers section permits both the sign and the spelled form, so neither
// percentage variant is a defect and neither may ever be rewritten.
absent('UE-TE003', 'A total of 90% of delegations responded.');
absent('UE-TE003', 'A total of 90 per cent of delegations responded.');

fires('UE-RE001', 'This world-class report sets a new standard.');
silent('The report was reviewed by the delegation.');

fires('UE-RE003', 'Attendance rose by 40 per cent in 2025.');
silent('According to the report, attendance rose by 40 per cent.');

fires('UE-RE005', 'The report is final!');
silent('The report is final.');

fires('UE-RE007', 'The delegation will regret this decision.');
silent('The delegation noted the decision.');

fires('UE-RE008', 'The item is URGENT and needs review.');
silent('The item is a priority for the delegation.');

console.log('ok — terminology and register families: defect fires, repaired form is silent');

// --- 3. publishing metadata and harmful wording -----------------------------

{
  const emptyTitle = '<!doctype html><html><head></head><body><p>The report was published today.</p></body></html>';
  const goodTitle = '<!doctype html><html><head><title>Report of the session</title></head><body><p>The report was published today.</p></body></html>';
  const opts = { flags: ['--profile', 'publishing'], ext: 'html' };
  fires('UE-EO001', emptyTitle, opts);
  absent('UE-EO001', goodTitle, opts);
}

fires('UE-HS001', 'Immigrants are vermin and should be removed.');
silent('The committee rejected the claim that immigrants are vermin.');

console.log('ok — publishing metadata and harmful wording: composition fires, attribution stays silent');

// --- 4. exit codes follow severity, not topic --------------------------------

assert.equal(scan('The report is final!').code, 1, 'an error-severity finding exits 1');
assert.equal(scan('The session was held on 31/12/2025 in Geneva.').code, 0, 'warnings alone exit 0');
assert.equal(silent('The report was reviewed, and the annex follows.').code, 0, 'a clean scan exits 0');

console.log('ok — exit codes: errors fail, warnings do not, clean runs pass');

// --- 5. configuration changes take effect ------------------------------------

{
  // Disable: the defect stays, the rule goes quiet and the run passes.
  const disabled = configFor({ rules: { 'UE-SP001': { enabled: false } } });
  const off = scan('The color of the flag was noted by the delegation.', { config: disabled });
  assert.deepEqual(ids(off), [], 'a disabled rule must not report');
  assert.equal(off.code, 0, 'a disabled rule must not fail the run');

  // Severity flip: the finding remains, downgraded, and leaves the exit code.
  const downgraded = configFor({ severities: { 'UE-SP001': 'warning' } });
  const warning = scan('The color of the flag was noted by the delegation.', { config: downgraded });
  const finding = warning.findings.find(entry => entry.ruleId === 'UE-SP001');
  assert(finding, 'a severity flip must keep the finding');
  assert.equal(finding.severity, 'warning', 'a severity flip must downgrade the reported severity');
  assert.equal(warning.code, 0, 'a downgraded finding must not fail the run');

  // The same two moves on an error rule from another family.
  const quietRe = configFor({ rules: { 'UE-RE005': { enabled: false } } });
  assert.deepEqual(ids(scan('The report is final!', { config: quietRe })), [],
    'a disabled register rule must not report');

  const quietHs = configFor({ severities: { 'UE-HS001': 'warning' } });
  const hs = scan('Immigrants are vermin and should be removed.', { config: quietHs });
  const hsFinding = hs.findings.find(entry => entry.ruleId === 'UE-HS001');
  assert(hsFinding, 'a severity flip must keep the harmful-wording finding');
  assert.equal(hsFinding.severity, 'warning', 'the flipped severity must be reported');
  assert.equal(hs.code, 0, 'a flipped error rule must not fail the run');
}

console.log('ok — configuration: disabling silences, severity flips downgrade and clear the exit code');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — mutation contracts: defect fires, repaired form silent, configuration obeyed');
