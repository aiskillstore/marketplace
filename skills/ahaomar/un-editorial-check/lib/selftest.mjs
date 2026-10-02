// `--self-test`: verify an installed copy against the package's own corpus.
//
// The corpus lives in lib/fixtures/self-test (the `fixtures` segment keeps it
// out of repository self-scans while `files: ["lib"]` still ships it, so the
// test runs from an npm pack tarball with no network). Every expectation
// locks only rule id, line and column — the message and severity of a rule
// may evolve with the rules themselves, but a finding appearing, moving or
// disappearing must break this test with a readable diff.
//
// Exit behaviour (wired by lib/cli.mjs): 0 verified, 1 with the diff on
// stderr even under --quiet, 2 when the corpus cannot be read.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { extractFile } from './extract.mjs';
import { runEditorialRules } from './rules.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const CORPUS_DIR = path.join(HERE, 'fixtures', 'self-test');

export class SelfTestError extends Error {}

/**
 * The built-in cases. `clean.txt` must stay at zero findings — it is the
 * guard against a rule that fires on ordinary prose — and `violations.txt`
 * carries one planted violation per line across five rules, so the success
 * line's count is meaningful rather than merely non-zero.
 */
export const CORPUS = [
  { file: 'clean.txt', expected: [] },
  {
    file: 'violations.txt',
    expected: [
      { ruleId: 'UE-SP001', line: 1, column: 5 },   // color
      { ruleId: 'UE-TE002', line: 2, column: 5 },   // handicapped
      { ruleId: 'UE-GR001', line: 3, column: 1 },   // The the
      { ruleId: 'UE-RE005', line: 4, column: 32 },  // the exclamation mark
      { ruleId: 'UE-DP001', line: 5, column: 1 },   // bare contested claim
    ],
  },
];

const markOf = (finding) => `${finding.ruleId}:${finding.line}:${finding.column}`;
const labelOf = (entry) => `${entry.ruleId}:${entry.line}:${entry.column}`;

/**
 * Run the bundled corpus through the given rule context and compare the
 * findings with the recorded expectations, both directions: an unexpected
 * finding and a missing one are both failures.
 *
 * @param {object} input
 * @param {object} input.ctx        { meta, cfg, vocab } — see lib/config.mjs
 * @param {string} [input.corpusDir] alternate corpus directory (tests only)
 * @returns {{ok: boolean, cases: number, findings: number, diff: string[]}}
 */
export function runSelfTest({ ctx, corpusDir = CORPUS_DIR }) {
  const diff = [];
  let findings = 0;

  for (const entry of CORPUS) {
    const file = path.join(corpusDir, entry.file);
    let source;
    try {
      source = fs.readFileSync(file, 'utf8');
    } catch (err) {
      throw new SelfTestError(`self-test corpus unreadable: ${file} (${err.message})`);
    }
    const units = extractFile(file, source, { renderTargets: ctx.cfg.renderTargets });
    const actual = runEditorialRules(units, ctx);

    findings += entry.expected.length;
    const wanted = new Map();
    for (const expected of entry.expected) {
      wanted.set(labelOf(expected), (wanted.get(labelOf(expected)) || 0) + 1);
    }
    for (const finding of actual) {
      const label = markOf(finding);
      if ((wanted.get(label) || 0) > 0) {
        wanted.set(label, wanted.get(label) - 1);
        continue;
      }
      diff.push(`unexpected ${finding.ruleId} at ${finding.file}:${finding.line}:${finding.column}`);
    }
    for (const [label, count] of wanted) {
      const [ruleId, line, column] = label.split(':');
      for (let i = 0; i < count; i++) {
        diff.push(`missing ${ruleId} at ${entry.file}:${line}:${column}`);
      }
    }
  }

  return { ok: diff.length === 0, cases: CORPUS.length, findings, diff };
}
