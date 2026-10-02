// Baseline snapshots (`--baseline`): a committed record of the findings a
// project has accepted, so later runs fail only on findings that are new.
//
// Key design, locked by tests/audit-adoption.mjs:
//   * a finding's key is `<cwd-relative file>|<ruleId>|<excerpt>` — no line
//     or column, so reflow or an edit above the finding cannot make it look
//     new, while a changed excerpt (fail closed) or a different rule can;
//   * the excerpt is NFC-normalised and whitespace-collapsed, so composed /
//     decomposed forms and reformatting share one key;
//   * the snapshot carries no timestamp: identical findings serialise to
//     identical bytes, which is what makes it safe to commit;
//   * an unreadable, corrupt or future-version snapshot is a refusal
//     (exit code 2 at the CLI), never a silent fall-back to a full scan;
//   * stale snapshot entries — findings that no longer fire — are reported
//     and never fail a run.

import fs from 'node:fs';
import path from 'node:path';

export const BASELINE_VERSION = 1;

export class BaselineError extends Error {}

const isPlainObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value);

/** Whitespace-collapsed, NFC-normalised excerpt: reflow must not change a key. */
function normaliseExcerpt(current) {
  return String(current ?? '').normalize('NFC').trim().split(/\s+/).join(' ');
}

/**
 * The file path as it appears in a key: working-directory relative when the
 * finding is absolute, exactly as written when it is already relative, with
 * a leading `./` removed and forward slashes throughout. With no working
 * directory given, an absolute path is made relative to its own directory —
 * the snapshot builder's default for single-directory snapshots.
 */
function relativeFile(file, cwd) {
  const raw = String(file);
  let rel = path.isAbsolute(raw) ? path.relative(cwd ?? path.dirname(raw), raw) : raw;
  rel = rel.split(path.sep).join('/');
  while (rel.startsWith('./')) rel = rel.slice(2);
  return rel;
}

/** `<file>|<ruleId>|<excerpt>` — the identity of a finding across runs. */
export function findingKey(finding, cwd) {
  return `${relativeFile(finding.file, cwd)}|${finding.ruleId}|${normaliseExcerpt(finding.current)}`;
}

/**
 * Build the snapshot object from this run's findings. Sorted by file, line,
 * column and rule id (with the key as a final tiebreak), so the serialised
 * bytes depend only on the findings themselves — not on the order they
 * arrived in.
 */
export function buildSnapshot(findings, toolVersion, cwd) {
  const entries = findings.map(finding => ({
    key: findingKey(finding, cwd),
    file: relativeFile(finding.file, cwd),
    ruleId: finding.ruleId,
    severity: finding.severity,
    line: finding.line,
    column: finding.column,
    excerpt: normaliseExcerpt(finding.current),
  }));
  entries.sort((a, b) =>
    a.file.localeCompare(b.file) || a.line - b.line || a.column - b.column ||
    a.ruleId.localeCompare(b.ruleId) || a.key.localeCompare(b.key));
  return { baselineVersion: BASELINE_VERSION, toolVersion: String(toolVersion), findings: entries };
}

/** Serialise a snapshot deterministically (two-space JSON, trailing newline). */
export function serialiseSnapshot(snapshot) {
  return `${JSON.stringify(snapshot, null, 2)}\n`;
}

/** Parse snapshot bytes, refusing anything that is not a version-1 snapshot. */
export function parseSnapshot(text, name) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (err) {
    throw new BaselineError(`baseline ${name} is not valid JSON: ${err.message}`);
  }
  if (!isPlainObject(data)) throw new BaselineError(`baseline ${name} is not a snapshot object`);
  if (data.baselineVersion !== BASELINE_VERSION) {
    throw new BaselineError(
      `baseline ${name}: unsupported baselineVersion ${String(data.baselineVersion)} (expected ${BASELINE_VERSION})`);
  }
  if (!Array.isArray(data.findings)) throw new BaselineError(`baseline ${name} findings must be an array`);
  for (const [index, entry] of data.findings.entries()) {
    if (!isPlainObject(entry) || typeof entry.key !== 'string' || !entry.key) {
      throw new BaselineError(`baseline ${name} entry ${index} must carry a key`);
    }
  }
  return {
    baselineVersion: data.baselineVersion,
    toolVersion: typeof data.toolVersion === 'string' ? data.toolVersion : '',
    findings: data.findings,
  };
}

/**
 * Read a snapshot: `null` when the file does not exist (first use), a parsed
 * snapshot otherwise, and a refusal for anything unreadable.
 */
export function readSnapshot(file) {
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw new BaselineError(`cannot read baseline ${file}: ${err.message}`);
  }
  return parseSnapshot(text, file);
}

/**
 * Split this run's findings into what the snapshot already knows and what is
 * new; snapshot entries absent from this run are stale.
 * @returns {{known: number, newFindings: object[], stale: number}}
 */
export function compareSnapshot(snapshot, findings, { cwd } = {}) {
  const knownKeys = new Set(snapshot.findings.map(entry => entry.key));
  const seen = new Set();
  const newFindings = [];
  let known = 0;
  for (const finding of findings) {
    const key = findingKey(finding, cwd);
    seen.add(key);
    if (knownKeys.has(key)) known += 1;
    else newFindings.push(finding);
  }
  const stale = snapshot.findings.filter(entry => !seen.has(entry.key)).length;
  return { known, newFindings, stale };
}

/**
 * The whole `--baseline` decision, as a pure value the CLI prints and returns.
 *
 * First use (no snapshot file): record every finding and exit 0 — by
 * definition nothing in the run is new, because the run just wrote them down.
 * Later: exit 1 only when a finding absent from the snapshot is also of
 * error severity; warnings, notes and stale entries never fail the run.
 *
 * @param {object} input
 * @param {string} input.file     the snapshot path, as the user typed it
 * @param {object[]} input.findings  every finding in this run
 * @param {object[]} input.errors    the error-severity subset that can fail
 * @param {string} input.toolVersion
 * @param {string} input.cwd      the working directory keys are relative to
 * @returns {{mode: 'written'|'compared', exitCode: number, status: string}}
 */
export function evaluateBaseline({ file, findings, errors = [], toolVersion, cwd }) {
  const target = path.resolve(cwd, file);
  const snapshot = readSnapshot(target);

  if (!snapshot) {
    const built = buildSnapshot(findings, toolVersion, cwd);
    try {
      fs.writeFileSync(target, serialiseSnapshot(built));
    } catch (err) {
      throw new BaselineError(`cannot write baseline ${file}: ${err.message}`);
    }
    const count = findings.length;
    return {
      mode: 'written',
      exitCode: 0,
      status: `Baseline written: ${file} (${count} finding${count === 1 ? '' : 's'} recorded; `
        + 'commit this file so later runs fail only on new findings)',
    };
  }

  const comparison = compareSnapshot(snapshot, findings, { cwd });
  const errorKeys = new Set(errors.map(finding => findingKey(finding, cwd)));
  const newErrors = comparison.newFindings.filter(finding => errorKeys.has(findingKey(finding, cwd)));
  const from = snapshot.toolVersion && snapshot.toolVersion !== toolVersion
    ? ` (snapshot from ${snapshot.toolVersion})`
    : '';
  const status = `Baseline ${file}${from}: ${comparison.known} known, `
    + `${comparison.newFindings.length} new, ${comparison.stale} stale, `
    + `${newErrors.length} new error-severity`;
  return { mode: 'compared', exitCode: newErrors.length ? 1 : 0, status };
}
