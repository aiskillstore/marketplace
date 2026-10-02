// The .docx and .odt contract: the ZIP reader is proven against containers
// built byte by byte, the recovered text runs the real rules, positions are
// paragraph-accurate, struck copy never reaches a rule, and every refusal is
// a refusal — never a clean run.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { run, CATALOGUE } from '../bin/check.mjs';
import { makeZip, makeDocx, makeOdt } from './lib/make-docx.mjs';
import { readZipEntries, extractDocx } from '../lib/office.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-office-'));

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
  const code = run(args, { log: l => out.push(String(l)), error: l => err.push(String(l)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const json = (result) => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const idsOf = (file, ...extra) =>
  [...new Set(json(capture([file, '--format', 'json', ...extra])).findings.map(f => f.ruleId))].sort();

// --- 1. the ZIP reader against containers built byte by byte -----------------

{
  const entries = readZipEntries(makeZip([
    { name: 'a.txt', data: 'stored content' },
    { name: 'dir/b.txt', data: 'deflated content '.repeat(64) },
  ], { comment: 'a trailing comment the EOCD scan must survive' }));
  assert.equal(entries.get('a.txt').toString(), 'stored content');
  assert.ok(entries.get('dir/b.txt').toString().startsWith('deflated content'));
  assert.equal(entries.size, 2, 'the entry count comes from the central directory');

  // Not a ZIP: every refusal path must refuse, never yield entries.
  for (const bad of [Buffer.from('not a zip at all'), Buffer.alloc(0), Buffer.alloc(10)]) {
    assert.throws(() => readZipEntries(bad), /ZIP|small|Central Directory/,
      'non-container bytes must refuse');
  }
  // A truncated container: the EOCD claims entries the file does not carry.
  const whole = makeZip([{ name: 'a.txt', data: 'x' }]);
  assert.throws(() => readZipEntries(whole.subarray(0, whole.length - 4)), /ZIP|unreadable|Central Directory/,
    'a truncated container must refuse');
  console.log('ok — office: zip reader round-trips stored and deflated entries, refuses non-containers');
}

// --- 2. a DOCX scan runs the real rules at paragraph positions ---------------

{
  const file = write('report.docx', makeDocx([
    { title: true, text: 'Quarterly Narrative Report' },
    { heading: 1, text: 'Background' },
    { text: 'The organization doubled its programme coverage in the region.' },
    { heading: 2, text: 'Figures.' },
    { text: 'Coverage reached 42 per cent of the target population, as reported.' },
  ]));
  const parsed = json(capture([file, '--format', 'json']));
  const byRule = new Map();
  for (const finding of parsed.findings) byRule.set(finding.ruleId, finding);
  assert(byRule.has('UE-SP001'), `the spelling rule must fire on recovered copy: ${parsed.findings.map(f => f.ruleId)}`);
  assert.equal(byRule.get('UE-SP001').current, 'organization');
  // A heading that ends in a full stop is the HR004 finding: the recovered
  // document carries heading structure, not just text.
  assert(byRule.has('UE-HR004'), 'a heading ending in a full stop must be reported in a DOCX');
  // Position: line 3 is the third paragraph, column 5 the word organization.
  assert.equal(byRule.get('UE-SP001').line, 3, 'line addresses the recovered paragraph');
  assert.equal(byRule.get('UE-SP001').column, 5);
  console.log('ok — office: a DOCX scan fires spelling and heading rules at paragraph positions');
}

// --- 3. struck copy, field instructions and empty paragraphs are invisible ---

{
  const file = write('tracked.docx', makeDocx([
    { text: 'The organization reports quarterly.', deleted: 'the us delegation was handicapped', instruction: ' REF Field25 ' },
  ]));
  const parsed = json(capture([file, '--format', 'json']));
  // Only the -ize family warning from "organization" may appear: the tracked
  // deletion and the field instruction carry copy that was struck or was never
  // user-visible, so neither may raise anything.
  const currents = parsed.findings.map(f => f.current);
  for (const finding of parsed.findings) {
    assert(!/us delegation|handicapped|Field25/.test(finding.current ?? ''),
      `struck or invisible copy must never reach a rule: ${finding.current}`);
  }
  assert.deepEqual([...new Set(parsed.findings.map(f => f.ruleId))].sort(), ['UE-SP001'],
    'only the live copy is judged');
  console.log('ok — office: tracked deletions and field instructions never reach a rule');
}

// --- 4. the refusal contract --------------------------------------------------

{
  // A misnamed file: bytes that are not a container refuse with a remedy.
  const notZip = write('broken.docx', Buffer.from('this is a plain text story about the organization'));
  const refused = capture([notZip]);
  assert.equal(refused.code, 2, 'non-container bytes must exit 2');
  assert.match(refused.stderr, /does not have the structure of a ZIP/, refused.stderr);
  assert.doesNotMatch(refused.stdout, /No findings under/,
    'a refusal never prints the clean sentence');

  // A ZIP container without the body part.
  const noBody = write('empty.docx', makeZip([{ name: '[Content_Types].xml', data: '<Types/>' }]));
  assert.equal(capture([noBody]).code, 2, 'a container with no document body must exit 2');

  // An encrypted package.
  const encrypted = write('locked.docx', makeZip([
    { name: 'EncryptionInfo', data: '<encryption/>' },
    { name: 'EncryptedPackage', data: Buffer.alloc(32) },
  ]));
  const locked = capture([encrypted]);
  assert.equal(locked.code, 2);
  assert.match(locked.stderr, /encrypted/, locked.stderr);

  // A body with no recoverable text: refusal, never a clean run.
  const blank = write('blank.docx', makeDocx([{ deleted: 'struck entirely' }]));
  const blankResult = capture([blank]);
  assert.equal(blankResult.code, 2, 'a text-free body must refuse, not report clean');
  assert.doesNotMatch(blankResult.stdout, /No findings under/);
  console.log('ok — office: every unreadable DOCX refuses with exit 2 and a reason');
}

// --- 5. ODT: same pipeline, OpenDocument container ----------------------------

{
  const file = write('memo.odt', makeOdt([
    { text: 'Introduction' , heading: 1 },
    'The organization met on 31/12/2025 and reviewed the program in Turkey.',
  ]));
  const byRule = new Set(json(capture([file, '--format', 'json'])).findings.map(f => f.ruleId));
  for (const id of ['UE-SP001', 'UE-NU001', 'UE-TE005']) {
    assert(byRule.has(id), `the ODT scan must fire ${id}`);
  }
  // A clean ODT is clean: the negative direction is locked too.
  const clean = write('clean.odt', makeOdt([
    { text: 'Summary', heading: 1 },
    'The delegation met in Geneva and reviewed the programme.',
  ]));
  assert.deepEqual(idsOf(clean), [], 'a clean ODT must produce no findings');
  console.log('ok — office: ODT containers run the same rules and stay silent on clean copy');
}

// --- 6. the fixer refuses a container ----------------------------------------

{
  const file = write('fixme.docx', makeDocx([{ text: 'The organization reported results in the region.' }]));
  const result = capture([file, '--fix']);
  assert.equal(result.code, 2, '--fix must refuse a DOCX');
  assert.match(result.stderr, /refusing --fix/, result.stderr);
  console.log('ok — office: the fixer refuses document containers');
}

// --- 7. collection: a directory walk picks containers up ----------------------

{
  const dir = path.join(tmp, 'docs-walk');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'one.docx'), makeDocx([{ text: 'The organization reports.' }]));
  fs.writeFileSync(path.join(dir, 'two.odt'), makeOdt(['The organization reports.']));
  fs.writeFileSync(path.join(dir, 'three.md'), 'The organization reports.\n');
  const result = capture([dir, '--format', 'json']);
  assert.equal(result.code, 0, result.stderr);
  const files = [...new Set(json(result).findings.map(f => f.file))].map(f => path.basename(f)).sort();
  assert.deepEqual(files, ['one.docx', 'three.md', 'two.odt'],
    'the walk must collect containers beside prose files');
  console.log('ok — office: directory walks collect DOCX and ODT beside prose');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — office: DOCX and ODT proven end to end: reader, rules, positions, refusals, collection');
