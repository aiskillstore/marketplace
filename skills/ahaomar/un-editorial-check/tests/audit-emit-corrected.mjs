// The --emit-corrected contract: one PDF in, a recovered working text out,
// with the deterministic corrections applied and everything else left as
// recovered — and the output honest about what it is.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { run } from '../bin/check.mjs';
import { build, PROSE } from './lib/make-pdf.mjs';
import { RECOVERED_NOTICE } from '../lib/emit-corrected.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-emit-'));
const configPath = path.join(tmp, 'config.json');
fs.writeFileSync(configPath, '{}');

const capture = async (argv) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', configPath];
  const code = run(args, { log: l => out.push(String(l)), error: l => err.push(String(l)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};

// --- 1. the corrections land in the recovered text, nothing else changes -----

{
  const pdf = path.join(tmp, 'report.pdf');
  fs.writeFileSync(pdf, build('flate'));
  const out = path.join(tmp, 'report.corrected.md');

  const result = await capture([pdf, '--emit-corrected', out]);
  // The fixture copy carries only warning-severity findings (the doubled
  // word), so the scan exits 0; the emission never changes the exit code.
  assert.equal(result.code, 0, result.stderr);
  assert.match(result.stdout, /Corrected text written/, result.stdout);

  const text = fs.readFileSync(out, 'utf8');
  assert(text.startsWith(RECOVERED_NOTICE), 'the file must say what it is');
  // The fixable defect is corrected: the doubled word collapses to one copy,
  // so both recovered lines read as the clean sentence.
  assert(!text.includes('the the'), `the doubled word must be corrected:\n${text}`);
  assert.equal(text.split(PROSE.clean).length - 1, 2,
    'both lines must be corrected to the clean copy');
  console.log('ok — emit-corrected: fixable defects corrected, the rest recovered, notice present');
}

// --- 2. the refusals ----------------------------------------------------------

{
  const txt = path.join(tmp, 'plain.txt');
  fs.writeFileSync(txt, 'The organization reports.\n');
  const noPdf = await capture([txt, '--emit-corrected', path.join(tmp, 'x.md')]);
  assert.equal(noPdf.code, 2, 'a scan without a PDF must refuse');
  assert.match(noPdf.stderr, /no PDF/, noPdf.stderr);

  const pdf = path.join(tmp, 'report.pdf');
  fs.writeFileSync(pdf, build('flate'));
  const withFix = await capture([pdf, '--fix', '--emit-corrected', path.join(tmp, 'y.md')]);
  assert.equal(withFix.code, 2, '--fix and --emit-corrected are mutually exclusive');

  const second = path.join(tmp, 'second.pdf');
  fs.writeFileSync(second, build('flate'));
  const twoPdf = await capture([pdf, second, '--emit-corrected', path.join(tmp, 'z.md')]);
  assert.equal(twoPdf.code, 2, 'two PDFs in one run must refuse');
  assert.match(twoPdf.stderr, /exactly one PDF|contains 2/, twoPdf.stderr);
  console.log('ok — emit-corrected: refusals hold for no PDF, --fix and two PDFs');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — emit-corrected: the PDF round-trip proven end to end');
